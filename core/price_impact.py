"""
Price-impact analysis — the book walker.

For each market we simulate a market BUY of the YES outcome at three notional
sizes ($500 / $2k / $10k), walking the ask side level by level to compute the
volume-weighted execution price actually achievable. The gap between the
displayed mid-price and the $10k execution price is the headline *price impact
score*: the larger it is, the more the screen probability overstates what a
real trader could transact at.

All prices are implied probabilities in [0, 1]; impact is reported in the same
units (e.g. an impact of 0.04 means paying 4 probability "cents" above mid).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import config
from core.normalizer import NormalizedMarket, OrderBook

logger = logging.getLogger("liquidity_agent.price_impact")

_EPS = 1e-9


@dataclass
class ImpactPoint:
    """Result of walking the ask side for one notional order size."""

    size_usd: float
    filled: bool             # was the full notional absorbable by the book?
    shares: float            # contracts acquired
    notional_filled: float   # USD actually deployed
    vwap: Optional[float]    # volume-weighted execution price (probability)
    impact_abs: Optional[float]   # vwap - mid (probability points)
    impact_pct: Optional[float]   # impact_abs / mid
    slippage_vs_ask: Optional[float]  # vwap - best_ask


@dataclass
class MarketImpact:
    """Aggregated impact profile for a single market."""

    market: NormalizedMarket
    mid: Optional[float]
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    ask_depth_usd: float
    points: Dict[float, ImpactPoint] = field(default_factory=dict)

    def point(self, size_usd: float) -> Optional[ImpactPoint]:
        return self.points.get(size_usd)

    @property
    def headline_impact(self) -> Optional[float]:
        """Price impact (vs mid) at the reference size ($10k by default)."""
        pt = self.points.get(config.PRICE_IMPACT_REFERENCE_SIZE)
        return pt.impact_abs if pt else None


def simulate_buy(book: OrderBook, notional_usd: float) -> ImpactPoint:
    """Walk the ask side, spending up to ``notional_usd``.

    Returns a fully-populated :class:`ImpactPoint`. If the book cannot absorb
    the full notional, ``filled`` is False and the metrics describe the partial
    fill achievable.
    """
    mid = book.mid_price()
    best_ask = book.best_ask()

    remaining = notional_usd
    spent = 0.0
    shares = 0.0

    for level in book.asks:
        if remaining <= _EPS:
            break
        level_cost = level.notional  # price * size
        if level_cost <= remaining + _EPS:
            spent += level_cost
            shares += level.size
            remaining -= level_cost
        else:
            partial_shares = remaining / level.price
            spent += remaining
            shares += partial_shares
            remaining = 0.0
            break

    filled = spent >= notional_usd - 1e-6
    vwap = (spent / shares) if shares > _EPS else None
    impact_abs = (vwap - mid) if (vwap is not None and mid is not None) else None
    impact_pct = (impact_abs / mid) if (impact_abs is not None and mid) else None
    slippage_vs_ask = (vwap - best_ask) if (vwap is not None and best_ask is not None) else None

    return ImpactPoint(
        size_usd=notional_usd,
        filled=filled,
        shares=shares,
        notional_filled=spent,
        vwap=vwap,
        impact_abs=impact_abs,
        impact_pct=impact_pct,
        slippage_vs_ask=slippage_vs_ask,
    )


def compute_market_impact(market: NormalizedMarket) -> Optional[MarketImpact]:
    """Compute the full impact profile for ``market`` across all order sizes."""
    book = market.book
    if book is None or not book.is_two_sided():
        logger.debug("No two-sided book for %s/%s", market.platform, market.market_id)
        return None

    impact = MarketImpact(
        market=market,
        mid=book.mid_price(),
        best_bid=book.best_bid(),
        best_ask=book.best_ask(),
        spread=book.spread(),
        ask_depth_usd=book.ask_notional(),
    )
    for size in config.ORDER_SIZES_USD:
        impact.points[size] = simulate_buy(book, size)
    return impact


def compute_all(markets: List[NormalizedMarket]) -> Dict[str, MarketImpact]:
    """Compute impact for every market, keyed by ``platform:market_id``.

    Markets without a usable book are skipped and logged, never fatal.
    """
    out: Dict[str, MarketImpact] = {}
    for m in markets:
        try:
            mi = compute_market_impact(m)
            if mi is not None:
                out[f"{m.platform}:{m.market_id}"] = mi
        except Exception as exc:  # noqa: BLE001
            logger.warning("Impact computation failed for %s: %s", m.market_id, exc)
    logger.info("Computed price impact for %d markets", len(out))
    return out
