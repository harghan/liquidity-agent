"""
Smart Order Router (SOR) — Multi-Venue Optimal Liquidity Allocation Engine.

Solves the multi-venue convex optimization problem for discrete orderbooks:
    min sum(Cost_i(q_i)) subject to sum(q_i) = Q_target, 0 <= q_i <= Depth_i

Uses Equal-Marginal-Price Discrete Waterfilling across heterogeneous venues
(e.g., Polymarket off-chain CLOB vs. Kalshi CFTC matching engine), factoring in
venue fee structures, marginal price impact, and book exhaustion.

Author: 30-yr Quant Market Microstructure & HFT Architecture Team
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.normalizer import (
    NormalizedMarket,
    OrderBook,
    OrderLevel,
    calculate_net_marginal_price,
    calculate_venue_fee,
)

logger = logging.getLogger("liquidity_agent.sor")

_EPS = 1e-9


@dataclass(frozen=True)
class FillStep:
    """A discrete execution tranche in the optimal routing schedule."""

    step_index: int
    platform: str
    market_id: str
    price: float
    effective_price: float  # fee-adjusted marginal price
    size_shares: float
    notional_usd: float
    cumulative_notional: float
    cumulative_shares: float
    cumulative_vwap: float


@dataclass
class VenueAllocation:
    """Allocation summary for a single venue under the SOR schedule."""

    platform: str
    market_id: str
    notional_usd: float
    shares: float
    vwap: Optional[float]
    effective_vwap: Optional[float]  # including fees
    total_fee_usd: float
    pct_of_total_order: float
    is_fully_filled: bool
    fill_ratio: float  # notional filled / requested venue capacity


@dataclass
class SORResult:
    """Complete institutional routing plan with benchmarks and savings metrics."""

    target_notional_usd: float
    side: str  # "buy" or "sell"
    filled: bool
    total_notional_filled: float
    total_shares: float
    blended_vwap: Optional[float]
    blended_effective_vwap: Optional[float]  # all-in with venue fees
    total_fees_usd: float
    venue_allocations: Dict[str, VenueAllocation]
    execution_steps: List[FillStep] = field(default_factory=list)

    # Benchmark comparisons vs single-venue execution
    single_venue_results: Dict[str, Dict[str, Optional[float]]] = field(default_factory=dict)
    dollar_savings_vs_worst: float = 0.0
    dollar_savings_vs_best: float = 0.0
    bps_improvement_vs_worst: float = 0.0
    bps_improvement_vs_best: float = 0.0
    legging_risk_index: float = 0.0  # 0 to 100 risk score (cross-chain/latency mismatch)


class SmartOrderRouter:
    """Enterprise multi-venue smart order routing engine."""

    def __init__(self, include_fees: bool = True):
        self.include_fees = include_fees

    def route(
        self,
        markets: List[NormalizedMarket],
        notional_usd: float,
        side: str = "buy",
        use_synthetic_no: bool = False,
    ) -> SORResult:
        """Calculate the globally optimal liquidity allocation across all participating markets.

        Args:
            markets: List of NormalizedMarket instances (same economic event across venues).
            notional_usd: Desired execution size in USD.
            side: "buy" (sweeps asks) or "sell" (sweeps bids).
            use_synthetic_no: If True, evaluates synthetic NO book parity for additional liquidity.

        Returns:
            A fully populated SORResult with optimal venue allocations and alpha metrics.
        """
        side = side.lower().strip()
        if side not in ("buy", "sell"):
            raise ValueError(f"Invalid side '{side}'. Must be 'buy' or 'sell'.")
        if notional_usd <= _EPS:
            raise ValueError(f"Notional USD must be positive, got {notional_usd}.")

        # 1. Build list of candidate tranches across all venues
        # Tranche tuple: (effective_price, raw_price, available_notional, available_shares, market)
        tranches: List[Tuple[float, float, float, float, NormalizedMarket]] = []

        active_markets: List[NormalizedMarket] = []
        for m in markets:
            if not m.has_book:
                continue
            book = m.book
            if use_synthetic_no and m.outcome.lower() == "no":
                book = book.synthetic_no_book()

            active_markets.append(m)
            levels = book.asks if side == "buy" else book.bids

            for lvl in levels:
                if lvl.size <= _EPS or lvl.price <= _EPS:
                    continue
                eff_price = (
                    calculate_net_marginal_price(m.platform, lvl.price, lvl.size, is_taker=True)
                    if self.include_fees
                    else lvl.price
                )
                level_cost = lvl.price * lvl.size
                tranches.append((eff_price, lvl.price, level_cost, lvl.size, m))

        if not tranches:
            logger.warning("No usable liquidity tranches found across %d markets", len(markets))
            return SORResult(
                target_notional_usd=notional_usd,
                side=side,
                filled=False,
                total_notional_filled=0.0,
                total_shares=0.0,
                blended_vwap=None,
                blended_effective_vwap=None,
                total_fees_usd=0.0,
                venue_allocations={},
            )

        # 2. Sort tranches by effective marginal price:
        # If BUY: ascending (cheapest effective price first)
        # If SELL: descending (highest effective bid first)
        tranches.sort(key=lambda t: t[0], reverse=(side == "sell"))

        # 3. Discrete Waterfilling sweep across the aggregated virtual orderbook
        remaining_usd = notional_usd
        total_spent = 0.0
        total_shares = 0.0
        steps: List[FillStep] = []
        venue_accum: Dict[str, Dict[str, float]] = {
            m.platform: {"notional": 0.0, "shares": 0.0, "gross_cost": 0.0, "fee": 0.0}
            for m in active_markets
        }

        step_idx = 1
        for eff_p, raw_p, tranche_notional, tranche_shares, m in tranches:
            if remaining_usd <= _EPS:
                break

            fill_usd = min(remaining_usd, tranche_notional)
            fill_shares = fill_usd / raw_p
            remaining_usd -= fill_usd
            total_spent += fill_usd
            total_shares += fill_shares

            # Calculate venue fee for this slice
            slice_fee = (
                calculate_venue_fee(m.platform, raw_p, fill_shares, is_taker=True)
                if self.include_fees
                else 0.0
            )

            # Accumulate per-venue metrics
            va = venue_accum[m.platform]
            va["notional"] += fill_usd
            va["shares"] += fill_shares
            va["gross_cost"] += fill_usd
            va["fee"] += slice_fee

            cur_vwap = total_spent / total_shares if total_shares > _EPS else None

            steps.append(
                FillStep(
                    step_index=step_idx,
                    platform=m.platform,
                    market_id=m.market_id,
                    price=raw_p,
                    effective_price=eff_p,
                    size_shares=round(fill_shares, 2),
                    notional_usd=round(fill_usd, 2),
                    cumulative_notional=round(total_spent, 2),
                    cumulative_shares=round(total_shares, 2),
                    cumulative_vwap=round(cur_vwap, 5) if cur_vwap else 0.0,
                )
            )
            step_idx += 1

        filled = total_spent >= (notional_usd - 1e-4)
        blended_vwap = (total_spent / total_shares) if total_shares > _EPS else None
        total_fees = sum(v["fee"] for v in venue_accum.values())
        blended_effective_vwap = (
            ((total_spent + total_fees) / total_shares) if total_shares > _EPS else None
        )

        # 4. Finalize venue allocations
        allocations: Dict[str, VenueAllocation] = {}
        for m in active_markets:
            v = venue_accum[m.platform]
            v_shares = v["shares"]
            v_notional = v["notional"]
            v_vwap = (v_notional / v_shares) if v_shares > _EPS else None
            v_eff_vwap = (
                ((v_notional + v["fee"]) / v_shares) if v_shares > _EPS else None
            )
            allocations[m.platform] = VenueAllocation(
                platform=m.platform,
                market_id=m.market_id,
                notional_usd=round(v_notional, 2),
                shares=round(v_shares, 2),
                vwap=round(v_vwap, 5) if v_vwap else None,
                effective_vwap=round(v_eff_vwap, 5) if v_eff_vwap else None,
                total_fee_usd=round(v["fee"], 2),
                pct_of_total_order=round((v_notional / total_spent) * 100.0, 1)
                if total_spent > _EPS
                else 0.0,
                is_fully_filled=filled,
                fill_ratio=round((v_notional / notional_usd), 4),
            )

        # 5. Compute Single-Venue Benchmarks (What if client sent 100% to Venue X?)
        single_benchmarks: Dict[str, Dict[str, Optional[float]]] = {}
        single_costs: List[float] = []

        for m in active_markets:
            s_fill_usd, s_shares, s_vwap, s_fees = self._simulate_single_venue(
                m, notional_usd, side
            )
            single_benchmarks[m.platform] = {
                "notional_filled": round(s_fill_usd, 2),
                "shares_filled": round(s_shares, 2),
                "vwap": round(s_vwap, 5) if s_vwap else None,
                "fees_usd": round(s_fees, 2),
                "total_cost": round(s_fill_usd + s_fees, 2),
                "fully_filled": (s_fill_usd >= notional_usd - 1e-4),
            }
            if s_fill_usd >= notional_usd - 1e-4 and s_vwap:
                single_costs.append(s_fill_usd + s_fees)

        # 6. Quantify Alpha & Value Creation ($ Savings and BPS improvement)
        # Using standard institutional Implementation Shortfall & TCA metrics
        dollar_savings_worst = 0.0
        dollar_savings_best = 0.0
        bps_savings_worst = 0.0
        bps_savings_best = 0.0

        valid_vwaps = [
            s["vwap"] for s in single_benchmarks.values() if s["vwap"] is not None and s.get("fully_filled")
        ]

        if valid_vwaps and blended_vwap and total_shares > _EPS:
            if side == "buy":
                # For buyers, lower VWAP is better. Worst single venue has highest VWAP.
                worst_vwap = max(valid_vwaps)
                best_vwap = min(valid_vwaps)
                bps_savings_worst = max(0.0, (worst_vwap - blended_vwap) * 10_000.0)
                bps_savings_best = max(0.0, (best_vwap - blended_vwap) * 10_000.0)
                dollar_savings_worst = max(0.0, (worst_vwap - blended_vwap) * total_shares)
                dollar_savings_best = max(0.0, (best_vwap - blended_vwap) * total_shares)
            else:
                # For sellers, higher VWAP is better. Worst single venue has lowest VWAP.
                worst_vwap = min(valid_vwaps)
                best_vwap = max(valid_vwaps)
                bps_savings_worst = max(0.0, (blended_vwap - worst_vwap) * 10_000.0)
                bps_savings_best = max(0.0, (blended_vwap - best_vwap) * 10_000.0)
                dollar_savings_worst = max(0.0, (blended_vwap - worst_vwap) * total_shares)
                dollar_savings_best = max(0.0, (blended_vwap - best_vwap) * total_shares)

        # 7. Legging Risk Index: Measures execution risk across heterogeneous venues
        # Based on number of active venues and fill imbalance
        active_venues_count = sum(1 for a in allocations.values() if a.notional_usd > _EPS)
        if active_venues_count <= 1:
            legging_risk = 0.0  # single venue execution has zero multi-leg mismatch
        else:
            # Imbalance factor: higher risk if one leg is 90% and other is 10%
            shares_list = [a.shares for a in allocations.values() if a.shares > _EPS]
            ratio = min(shares_list) / max(shares_list) if shares_list else 1.0
            legging_risk = round(15.0 + (1.0 - ratio) * 35.0, 1)

        return SORResult(
            target_notional_usd=round(notional_usd, 2),
            side=side,
            filled=filled,
            total_notional_filled=round(total_spent, 2),
            total_shares=round(total_shares, 2),
            blended_vwap=round(blended_vwap, 5) if blended_vwap else None,
            blended_effective_vwap=round(blended_effective_vwap, 5) if blended_effective_vwap else None,
            total_fees_usd=round(total_fees, 2),
            venue_allocations=allocations,
            execution_steps=steps,
            single_venue_results=single_benchmarks,
            dollar_savings_vs_worst=round(dollar_savings_worst, 2),
            dollar_savings_vs_best=round(dollar_savings_best, 2),
            bps_improvement_vs_worst=round(bps_savings_worst, 1),
            bps_improvement_vs_best=round(bps_savings_best, 1),
            legging_risk_index=legging_risk,
        )

    def _simulate_single_venue(
        self, market: NormalizedMarket, notional_usd: float, side: str
    ) -> Tuple[float, float, Optional[float], float]:
        """Simulate sending 100% of the order to a single venue."""
        book = market.book
        if not book:
            return 0.0, 0.0, None, 0.0

        levels = book.asks if side == "buy" else book.bids
        remaining = notional_usd
        spent = 0.0
        shares = 0.0

        for lvl in levels:
            if remaining <= _EPS:
                break
            level_cost = lvl.price * lvl.size
            if level_cost <= remaining + _EPS:
                spent += level_cost
                shares += lvl.size
                remaining -= level_cost
            else:
                partial_shares = remaining / lvl.price
                spent += remaining
                shares += partial_shares
                remaining = 0.0
                break

        fees = calculate_venue_fee(market.platform, spent / shares if shares > 0 else 0.5, shares)
        vwap = (spent / shares) if shares > _EPS else None
        return spent, shares, vwap, fees
