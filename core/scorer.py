"""
Liquidity Quality Index (LQI).

A composite 0..100 score per market per platform, combining three components
that each capture a distinct dimension of executable liquidity:

* spread (30%)  — tightness of the top-of-book bid/ask
* depth  (40%)  — slippage absorbing a $2k order (deeper book ⇒ less slippage)
* impact (30%)  — slippage on a $10k order (resilience to size)

Each raw metric (all in probability units) is mapped to a 0..100 sub-score via
a linear ramp to a configured cap, where the cap is the value at which the
component is considered fully degraded. Higher LQI = more trustworthy, more
executable liquidity behind the displayed price.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import config
from core.price_impact import MarketImpact

logger = logging.getLogger("liquidity_agent.scorer")


@dataclass
class LQIResult:
    """LQI total plus its components and the raw metrics behind them."""

    total: float
    spread_score: float
    depth_score: float
    impact_score: float
    spread: Optional[float]
    impact_2k: Optional[float]
    impact_10k: Optional[float]
    grade: str


def _ramp(value: float, cap: float) -> float:
    """Linear 100→0 score as ``value`` rises from 0 to ``cap`` (clamped)."""
    if cap <= 0:
        return 0.0
    score = 100.0 * (1.0 - (max(value, 0.0) / cap))
    return max(0.0, min(100.0, score))


def _grade(total: float) -> str:
    if total >= 80:
        return "A — institutional"
    if total >= 65:
        return "B — healthy"
    if total >= 50:
        return "C — usable"
    if total >= 35:
        return "D — thin"
    return "F — illiquid"


def _degraded_impact(impact: MarketImpact, size: float, cap: float) -> float:
    """Return the impact metric for ``size``, treating an unfillable book as
    maximally degraded (the cap)."""
    pt = impact.points.get(size)
    if pt is None or pt.impact_abs is None or not pt.filled:
        return cap
    return pt.impact_abs


def score_market(impact: MarketImpact) -> LQIResult:
    """Compute the LQI for a single market's impact profile."""
    spread = impact.spread if impact.spread is not None else config.LQI_SPREAD_CAP
    impact_2k = _degraded_impact(impact, config.DEPTH_REFERENCE_SIZE, config.LQI_DEPTH_IMPACT_CAP)
    impact_10k = _degraded_impact(impact, config.PRICE_IMPACT_REFERENCE_SIZE, config.LQI_IMPACT_CAP)

    spread_score = _ramp(spread, config.LQI_SPREAD_CAP)
    depth_score = _ramp(impact_2k, config.LQI_DEPTH_IMPACT_CAP)
    impact_score = _ramp(impact_10k, config.LQI_IMPACT_CAP)

    total = (
        config.LQI_WEIGHTS["spread"] * spread_score
        + config.LQI_WEIGHTS["depth"] * depth_score
        + config.LQI_WEIGHTS["impact"] * impact_score
    )

    # Preserve the actual (possibly None) measured impacts for reporting.
    pt2 = impact.points.get(config.DEPTH_REFERENCE_SIZE)
    pt10 = impact.points.get(config.PRICE_IMPACT_REFERENCE_SIZE)
    return LQIResult(
        total=round(total, 1),
        spread_score=round(spread_score, 1),
        depth_score=round(depth_score, 1),
        impact_score=round(impact_score, 1),
        spread=impact.spread,
        impact_2k=pt2.impact_abs if pt2 else None,
        impact_10k=pt10.impact_abs if pt10 else None,
        grade=_grade(total),
    )


def score_all(impacts: Dict[str, MarketImpact]) -> Dict[str, LQIResult]:
    """Score every market, keyed identically to ``impacts``."""
    out: Dict[str, LQIResult] = {}
    for key, mi in impacts.items():
        try:
            out[key] = score_market(mi)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LQI scoring failed for %s: %s", key, exc)
    logger.info("Scored LQI for %d markets", len(out))
    return out
