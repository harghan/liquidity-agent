"""
Cross-Venue Parity, Basis, & Synthetic Arbitrage Engine.

In prediction markets, binary payoff conditions dictate:
    Price(YES) + Price(NO) = 1.00

This engine calculates:
1. Synthetic Cross-Venue Cash-Out Arbitrage (Bid_YES_A + Bid_NO_B - 1.00).
2. Synthetic Cross-Venue Discount Arbitrage (1.00 - [Ask_YES_A + Ask_NO_B]).
3. All-in Fee-Adjusted Net Basis and Annualized Return on Invested Capital (RoIC).
4. SOFR Benchmark Hurdle Rate comparison (identifying whether an arb is real or capital-destructive).
5. Oracle Resolution Risk Scoring (CFTC legal rulebook vs UMA optimistic oracle).

Author: 30-yr Quant Market Microstructure & HFT Architecture Team
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from core.normalizer import NormalizedMarket, calculate_venue_fee

logger = logging.getLogger("liquidity_agent.parity")

# Benchmark risk-free rate for capital opportunity cost comparison (SOFR / 3M T-Bill)
RISK_FREE_RATE_BENCHMARK = 0.0480  # 4.80% annualized


@dataclass
class ArbitrageOpportunity:
    """A cross-venue synthetic arbitrage opportunity with capital efficiency metrics."""

    pair_name: str
    event_category: str
    venue_a: str
    venue_b: str
    strategy_type: str  # "CASH_OUT_ARB" (sell both) or "DISCOUNT_BUY_ARB" (buy both)
    gross_spread_bps: float
    net_spread_bps: float
    net_profit_per_10k: float
    annualized_roic: Optional[float]
    days_to_resolution: Optional[int]
    beats_sofr: bool
    capital_efficiency_grade: str  # "INSTITUTIONAL_ALPHA", "MARGINAL", "CAPITAL_DESTRUCTIVE"
    oracle_dispute_risk: str  # "LOW", "MODERATE", "ELEVATED"
    execution_notes: str


class ParityEngine:
    """Evaluates synthetic binary parity and capital efficiency across venues."""

    def __init__(self, risk_free_rate: float = RISK_FREE_RATE_BENCHMARK):
        self.risk_free_rate = risk_free_rate

    def evaluate_pair(
        self,
        poly_market: NormalizedMarket,
        kalshi_market: NormalizedMarket,
        days_to_resolution: Optional[int] = None,
    ) -> Optional[ArbitrageOpportunity]:
        """Evaluate synthetic arbitrage and basis between Polymarket and Kalshi books."""
        p_book = poly_market.book
        k_book = kalshi_market.book
        if not p_book or not k_book or not p_book.is_two_sided() or not k_book.is_two_sided():
            return None

        # Top of book quotes
        p_bb, p_ba = p_book.best_bid(), p_book.best_ask()
        k_bb, k_ba = k_book.best_bid(), k_book.best_ask()

        if p_bb is None or p_ba is None or k_bb is None or k_ba is None:
            return None

        # Economic parity:
        # Kalshi NO Ask = 1 - Kalshi YES Bid
        # Kalshi NO Bid = 1 - Kalshi YES Ask
        k_no_bid = 1.0 - k_ba
        k_no_ask = 1.0 - k_bb

        # Strategy 1: Buy Polymarket YES + Buy Kalshi NO (Discount Buy Arb)
        # Cost to buy both sides = p_ba + k_no_ask = p_ba + (1 - k_bb)
        # Payoff at resolution is guaranteed $1.00
        cost_buy_both = p_ba + k_no_ask
        discount_spread = 1.0 - cost_buy_both

        # Strategy 2: Sell Polymarket YES + Sell Kalshi NO (Cash-Out Arb)
        # Proceeds from selling both = p_bb + k_no_bid = p_bb + (1 - k_ba)
        # Liability at resolution is guaranteed $1.00
        proceeds_sell_both = p_bb + k_no_bid
        cashout_spread = proceeds_sell_both - 1.0

        # Pick the best viable synthetic path
        if discount_spread >= cashout_spread and discount_spread > 0.0010:  # > 10 bps
            gross_spread = discount_spread
            strat = "DISCOUNT_BUY_ARB"
            # Fee estimation on 10,000 contracts
            fee_p = calculate_venue_fee("Polymarket", p_ba, 10_000)
            fee_k = calculate_venue_fee("Kalshi", k_no_ask, 10_000)
            net_spread = gross_spread - ((fee_p + fee_k) / 10_000.0)
            capital_required = cost_buy_both  # per contract
        elif cashout_spread > 0.0010:
            gross_spread = cashout_spread
            strat = "CASH_OUT_ARB"
            fee_p = calculate_venue_fee("Polymarket", p_bb, 10_000)
            fee_k = calculate_venue_fee("Kalshi", k_no_bid, 10_000)
            net_spread = gross_spread - ((fee_p + fee_k) / 10_000.0)
            capital_required = 1.00  # full collateral lock
        else:
            # No actionable cross-venue arbitrage (market is within arbitrage bounds)
            return None

        gross_bps = round(gross_spread * 10_000.0, 1)
        net_bps = round(net_spread * 10_000.0, 1)
        net_profit_10k = round(net_spread * 10_000.0, 2)

        # Annualization calculation
        days = days_to_resolution or 120  # default assumption: 4 months
        annualized_roic = None
        beats_sofr = False
        if days > 0 and capital_required > 0:
            annualized_roic = round((net_spread / capital_required) * (365.0 / days), 4)
            beats_sofr = annualized_roic > self.risk_free_rate

        # Quality Grade
        if net_bps > 200 and beats_sofr:
            grade = "INSTITUTIONAL_ALPHA"
        elif net_bps > 50 and beats_sofr:
            grade = "MARGINAL_ATTRACTIVE"
        else:
            grade = "CAPITAL_DESTRUCTIVE"  # Spread exists, but 200% margin & duration yield < SOFR

        # Oracle dispute risk heuristic
        cat = poly_market.category
        if cat in ("Presidential Election", "Primary / Nomination"):
            oracle_risk = "MODERATE"
            notes = "CFTC election litigation vs. UMA token vote creates resolution basis."
        elif cat in ("Fed / Rates", "Inflation", "GDP"):
            oracle_risk = "LOW"
            notes = "Both platforms resolve against identical official government prints."
        else:
            oracle_risk = "ELEVATED"
            notes = "Subjective resolution wording may cause conflicting venue determinations."

        return ArbitrageOpportunity(
            pair_name=poly_market.question[:50],
            event_category=poly_market.category,
            venue_a=poly_market.platform,
            venue_b=kalshi_market.platform,
            strategy_type=strat,
            gross_spread_bps=gross_bps,
            net_spread_bps=net_bps,
            net_profit_per_10k=net_profit_10k,
            annualized_roic=annualized_roic,
            days_to_resolution=days,
            beats_sofr=beats_sofr,
            capital_efficiency_grade=grade,
            oracle_dispute_risk=oracle_risk,
            execution_notes=notes,
        )

    def scan_all_pairs(
        self,
        matched_pairs: List[Tuple[NormalizedMarket, NormalizedMarket]],
    ) -> List[ArbitrageOpportunity]:
        """Scan all verified matched pairs for active synthetic arbitrage dislocations."""
        opportunities: List[ArbitrageOpportunity] = []
        for poly, kalshi in matched_pairs:
            opp = self.evaluate_pair(poly, kalshi)
            if opp:
                opportunities.append(opp)
        opportunities.sort(key=lambda o: o.net_spread_bps, reverse=True)
        return opportunities
