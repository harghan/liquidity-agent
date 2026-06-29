#!/usr/bin/env python3
"""
liquidity-agent — single entry point (v2 full rebuild).

Pipeline:
    1. Collect ~300 in-scope markets per platform (metadata only).
    2. Match overlapping markets across platforms with the NLP hybrid matcher;
       log every near-miss rejection to outputs/rejected_pairs.json.
    3. Fetch live orderbooks for matched markets only.
    4. Walk each book at five sizes ($500/$2k/$10k/$50k/$100k) for real impact.
    5. Score the Liquidity Quality Index (0-100) per market per platform.
    6. Assemble the cross-platform analysis (divergence + dollar-cost figures);
       emit raw_impacts.json and summary.json.
    7. Have Claude reason over the analysis and render a 9-page visual-first PDF.

Usage:  python run_agent.py   ->   outputs/liquidity_report_{YYYY-MM-DD}.pdf
"""

from __future__ import annotations

import json
import logging
import statistics
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import config
from agent import report_writer
from collectors import kalshi, polymarket
from core import matcher, price_impact, scorer
from core.matcher import MarketMatch
from core.normalizer import NormalizedMarket
from core.price_impact import MarketImpact
from core.scorer import LQIResult

logger = config.configure_logging()

NOTIONAL = config.PRICE_IMPACT_REFERENCE_SIZE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _key(m: NormalizedMarket) -> str:
    return f"{m.platform}:{m.market_id}"


def _round(x: Optional[float], nd: int = 5) -> Optional[float]:
    return None if x is None else round(float(x), nd)


def _bps(x: Optional[float], nd: int = 1) -> Optional[float]:
    """Probability units -> basis points (1.0 prob = 10,000 bps)."""
    return None if x is None else round(float(x) * 10_000.0, nd)


def _impact_display(mi: MarketImpact, size: float) -> Tuple[Optional[float], bool]:
    """Impact (probability) for a size. If the book is exhausted, report the
    cost to sweep the entire book as a lower bound on the true (unfillable)
    cost — this is what makes the 'where the book breaks' curve meaningful."""
    pt = mi.points.get(size)
    if pt is None or pt.impact_abs is None:
        return None, False
    if pt.filled:
        return pt.impact_abs, True
    worst = mi.market.book.asks[-1].price if (mi.market.book and mi.market.book.asks) else None
    if worst is not None and mi.mid is not None:
        return max(pt.impact_abs, worst - mi.mid), False
    return pt.impact_abs, False


def _side(market: NormalizedMarket, impacts: Dict[str, MarketImpact],
          lqi: Dict[str, LQIResult]) -> Optional[Dict[str, Any]]:
    mi = impacts.get(_key(market))
    if mi is None:
        return None
    l = lqi.get(_key(market))
    impact_bps: Dict[str, Optional[float]] = {}
    impact_abs: Dict[str, Optional[float]] = {}
    filled: Dict[str, bool] = {}
    for size in config.ORDER_SIZES_USD:
        ia, ok = _impact_display(mi, size)
        impact_bps[str(int(size))] = _bps(ia)
        impact_abs[str(int(size))] = _round(ia)
        filled[str(int(size))] = ok
    return {
        "market_id": market.market_id,
        "question": market.question,
        "url": market.url,
        "mid": _round(mi.mid),
        "displayed": _round(market.displayed_prob),
        "best_bid": _round(mi.best_bid),
        "best_ask": _round(mi.best_ask),
        "spread": _round(mi.spread),
        "spread_bps": _bps(mi.spread),
        "ask_depth_usd": round(mi.ask_depth_usd, 0),
        "volume": round(market.volume or 0.0, 0),
        "impact_bps": impact_bps,
        "impact_abs": impact_abs,
        "filled": filled,
        "vwap_10k": _round(mi.points[NOTIONAL].vwap) if mi.points.get(NOTIONAL) else None,
        "lqi": l.total if l else None,
        "grade": l.grade if l else None,
        "lqi_components": ({"spread": l.spread_score, "depth": l.depth_score,
                            "impact": l.impact_score} if l else None),
    }


def _slippage_cost(side: Dict[str, Any]) -> Optional[float]:
    imp = side["impact_abs"].get(str(int(NOTIONAL)))
    vwap = side.get("vwap_10k")
    if imp is None or not vwap:
        return None
    return NOTIONAL * imp / vwap


def _subject(match: MarketMatch) -> str:
    out = (match.kalshi.outcome or "").strip()
    if out and out.lower() not in ("yes", "no"):
        return out
    q = match.polymarket.question
    return q[:46] + ("…" if len(q) > 46 else "")


def _platform_stats(markets: List[NormalizedMarket], impacts: Dict[str, MarketImpact],
                    lqi: Dict[str, LQIResult]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for platform in ("Polymarket", "Kalshi"):
        keys = [_key(m) for m in markets if m.platform == platform and _key(m) in impacts]
        if not keys:
            continue
        lqis = [lqi[k].total for k in keys if k in lqi and lqi[k].total is not None]
        spreads_bps = [_bps(impacts[k].spread) for k in keys if impacts[k].spread is not None]
        mean_impact_bps: Dict[str, Optional[float]] = {}
        for size in config.ORDER_SIZES_USD:
            vals = []
            for k in keys:
                ia, _ = _impact_display(impacts[k], size)
                if ia is not None:
                    vals.append(ia * 10_000.0)
            mean_impact_bps[str(int(size))] = round(statistics.mean(vals), 1) if vals else None
        out[platform] = {
            "markets_scored": len(keys),
            "mean_lqi": round(statistics.mean(lqis), 1) if lqis else None,
            "median_lqi": round(statistics.median(lqis), 1) if lqis else None,
            "mean_spread_bps": round(statistics.mean(spreads_bps), 1) if spreads_bps else None,
            "mean_impact_bps": mean_impact_bps,
        }
    return out


def build_analysis(poly_universe, kal_universe, matches, matched_markets,
                   impacts, lqi, rejected) -> Dict[str, Any]:
    pairs: List[Dict[str, Any]] = []
    for m in matches:
        pm = _side(m.polymarket, impacts, lqi)
        kx = _side(m.kalshi, impacts, lqi)
        if pm is None or kx is None:
            continue
        mid_div = (abs(pm["mid"] - kx["mid"]) if pm["mid"] is not None and kx["mid"] is not None else None)
        cost_pm, cost_kx = _slippage_cost(pm), _slippage_cost(kx)
        avoidable = cheaper = None
        if cost_pm is not None and cost_kx is not None:
            avoidable = abs(cost_pm - cost_kx)
            cheaper = "Polymarket" if cost_pm <= cost_kx else "Kalshi"
        lqi_gap = (round(pm["lqi"] - kx["lqi"], 1) if pm["lqi"] is not None and kx["lqi"] is not None else None)
        pairs.append({
            "subject": _subject(m),
            "category": m.category,
            "confidence": round(m.confidence, 3),
            "entity_similarity": round(m.entity_similarity, 3),
            "polymarket": pm,
            "kalshi": kx,
            "mid_divergence": _round(mid_div),
            "divergence_bps": _bps(mid_div),
            "lqi_gap_pm_minus_kx": lqi_gap,
            "cheaper_venue": cheaper,
            "slippage_cost_pm": round(cost_pm, 0) if cost_pm is not None else None,
            "slippage_cost_kx": round(cost_kx, 0) if cost_kx is not None else None,
            "avoidable_slippage_10k": round(avoidable, 0) if avoidable is not None else None,
        })

    pairs.sort(key=lambda p: (p["avoidable_slippage_10k"] or 0), reverse=True)

    divs = [p["divergence_bps"] for p in pairs if p["divergence_bps"] is not None]
    avoid = [p["avoidable_slippage_10k"] for p in pairs if p["avoidable_slippage_10k"] is not None]
    max_div_pair = max(pairs, key=lambda p: (p["divergence_bps"] or 0)) if divs else None

    stats = _platform_stats(matched_markets, impacts, lqi)
    matches_by_cat: Dict[str, int] = {}
    for m in matches:
        matches_by_cat[m.category] = matches_by_cat.get(m.category, 0) + 1

    lqi_gap_overall = None
    if "Polymarket" in stats and "Kalshi" in stats:
        a, b = stats["Polymarket"].get("mean_lqi"), stats["Kalshi"].get("mean_lqi")
        if a is not None and b is not None:
            lqi_gap_overall = round(a - b, 1)

    return {
        "run_date": date.today().isoformat(),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "model": config.ANTHROPIC_MODEL,
        "order_sizes_usd": config.ORDER_SIZES_USD,
        "order_size_labels": ["$500", "$2k", "$10k", "$50k", "$100k"],
        "notional_per_trade_usd": NOTIONAL,
        "methodology": {
            "match_threshold_person": config.MATCH_THRESHOLD_PERSON,
            "match_threshold_default": config.MATCH_THRESHOLD_DEFAULT,
            "match_fuzzy_weight": config.MATCH_FUZZY_WEIGHT,
            "match_keyword_weight": config.MATCH_KEYWORD_WEIGHT,
            "lqi_weights": config.LQI_WEIGHTS,
            "lqi_caps": {"spread": config.LQI_SPREAD_CAP,
                         "depth_impact": config.LQI_DEPTH_IMPACT_CAP,
                         "impact": config.LQI_IMPACT_CAP},
        },
        "disclaimers": {"phantom_liquidity": config.PHANTOM_LIQUIDITY_DISCLAIMER},
        "universe": {
            "polymarket_universe": len(poly_universe),
            "kalshi_universe": len(kal_universe),
            "matched_pairs": len(matches),
            "compared_pairs": len(pairs),
            "near_miss_rejections": len(rejected),
            "matches_by_category": matches_by_cat,
        },
        "platform_stats": stats,
        "lqi_gap_overall": lqi_gap_overall,
        "cost_summary": {
            "notional_per_trade": NOTIONAL,
            "total_avoidable_slippage_10k": round(sum(avoid), 0) if avoid else 0.0,
            "mean_avoidable_slippage_10k": round(statistics.mean(avoid), 0) if avoid else 0.0,
            "mean_divergence_bps": round(statistics.mean(divs), 1) if divs else None,
            "max_divergence": ({"subject": max_div_pair["subject"],
                                "bps": max_div_pair["divergence_bps"]} if max_div_pair else None),
        },
        "pairs": pairs,
        "top_pairs": pairs[:3],
    }


def _write_json(path: Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    logger.info("Wrote %s", path)


def _export_raw_impacts(impacts: Dict[str, MarketImpact], lqi: Dict[str, LQIResult]) -> List[dict]:
    rows = []
    for key, mi in impacts.items():
        m = mi.market
        sizes = {}
        for size in config.ORDER_SIZES_USD:
            pt = mi.points.get(size)
            ia, ok = _impact_display(mi, size)
            sizes[str(int(size))] = {
                "impact_abs": _round(ia), "impact_bps": _bps(ia), "filled": ok,
                "vwap": _round(pt.vwap) if pt else None,
                "shares": round(pt.shares, 2) if pt else None,
                "notional_filled": round(pt.notional_filled, 2) if pt else None,
            }
        l = lqi.get(key)
        rows.append({
            "key": key, "platform": m.platform, "market_id": m.market_id,
            "question": m.question, "category": m.category,
            "mid": _round(mi.mid), "spread_bps": _bps(mi.spread),
            "ask_depth_usd": round(mi.ask_depth_usd, 0),
            "lqi": l.total if l else None, "grade": l.grade if l else None,
            "impact_by_size": sizes,
        })
    return rows


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def run() -> Optional[str]:
    logger.info("=" * 72)
    logger.info("liquidity-agent v2 run starting")
    logger.info("=" * 72)

    try:
        poly_universe = polymarket.collect_metadata(config.TARGET_MARKETS_PER_PLATFORM)
    except Exception as exc:  # noqa: BLE001
        logger.error("Polymarket collection failed: %s", exc)
        poly_universe = []
    try:
        kal_universe = kalshi.collect_metadata(config.TARGET_MARKETS_PER_PLATFORM)
    except Exception as exc:  # noqa: BLE001
        logger.error("Kalshi collection failed: %s", exc)
        kal_universe = []
    if not poly_universe and not kal_universe:
        logger.error("Both platforms returned no markets — aborting.")
        return None

    matches, rejected = matcher.match_markets(poly_universe, kal_universe)
    _write_json(config.OUTPUT_DIR / "rejected_pairs.json", {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "note": ("Every same-category candidate pair scoring >= 0.50 that was NOT "
                 "accepted, with its confidence and rejection reason. Evidence that "
                 "matching is algorithmic with zero cherry-picking."),
        "count": len(rejected),
        "rejected_pairs": rejected,
    })

    # Fetch orderbooks for matched markets only.
    matched_markets: List[NormalizedMarket] = []
    seen = set()
    for m in matches:
        for mkt, fetch in ((m.polymarket, polymarket.fetch_book), (m.kalshi, kalshi.fetch_book)):
            if _key(mkt) in seen:
                continue
            seen.add(_key(mkt))
            try:
                if fetch(mkt):
                    matched_markets.append(mkt)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Book fetch failed for %s: %s", _key(mkt), exc)
    logger.info("Fetched live books for %d/%d matched markets", len(matched_markets), len(seen))

    impacts = price_impact.compute_all(matched_markets)
    lqi = scorer.score_all(impacts)

    analysis = build_analysis(poly_universe, kal_universe, matches, matched_markets,
                              impacts, lqi, rejected)
    # Persist the full analysis so the PDF can be regenerated (layout-only) with
    # no data fetch and no API call via `python run_agent.py --pdf-only`.
    _write_json(config.OUTPUT_DIR / "analysis.json", analysis)

    _write_json(config.OUTPUT_DIR / "raw_impacts.json", {
        "generated_at": analysis["generated_at"],
        "order_sizes_usd": config.ORDER_SIZES_USD,
        "markets": _export_raw_impacts(impacts, lqi),
    })
    _write_json(config.OUTPUT_DIR / "summary.json", {
        "generated_at": analysis["generated_at"],
        "run_date": analysis["run_date"],
        "platform_lqi": {p: s.get("mean_lqi") for p, s in analysis["platform_stats"].items()},
        "lqi_gap_pm_minus_kx": analysis["lqi_gap_overall"],
        "total_avoidable_slippage_10k": analysis["cost_summary"]["total_avoidable_slippage_10k"],
        "matched_pairs": analysis["universe"]["matched_pairs"],
        "compared_pairs": analysis["universe"]["compared_pairs"],
        "matches_by_category": analysis["universe"]["matches_by_category"],
        "mean_divergence_bps": analysis["cost_summary"]["mean_divergence_bps"],
        "top_3_pairs": [{
            "subject": p["subject"], "category": p["category"],
            "avoidable_slippage_10k": p["avoidable_slippage_10k"],
            "divergence_bps": p["divergence_bps"], "cheaper_venue": p["cheaper_venue"],
        } for p in analysis["top_pairs"]],
    })

    logger.info("Analysis: %d matched / %d comparable; avoidable slippage $%s; by-cat %s",
                analysis["universe"]["matched_pairs"], analysis["universe"]["compared_pairs"],
                f"{analysis['cost_summary']['total_avoidable_slippage_10k']:,.0f}",
                analysis["universe"]["matches_by_category"])

    output_path = config.OUTPUT_DIR / f"liquidity_report_{analysis['run_date']}.pdf"
    try:
        report_writer.generate_pdf(analysis, output_path)
    except Exception as exc:  # noqa: BLE001
        logger.error("PDF generation failed: %s", exc, exc_info=True)
        return None

    logger.info("=" * 72)
    logger.info("Done. Report: %s", output_path)
    logger.info("=" * 72)
    return str(output_path)


def regenerate_pdf_only() -> Optional[str]:
    """Rebuild the PDF from cached analysis.json (+ prose.json if present) with
    no data collection and no API call. Used for layout/credit tweaks."""
    analysis_path = config.OUTPUT_DIR / "analysis.json"
    if not analysis_path.exists():
        logger.error("--pdf-only requires outputs/analysis.json (run a full pass first).")
        return None
    with open(analysis_path, encoding="utf-8") as f:
        analysis = json.load(f)
    prose = None
    prose_path = config.OUTPUT_DIR / "prose.json"
    if prose_path.exists():
        with open(prose_path, encoding="utf-8") as f:
            prose = json.load(f)
        logger.info("Loaded cached prose.json (no API call)")
    output_path = config.OUTPUT_DIR / f"liquidity_report_{analysis['run_date']}.pdf"
    report_writer.generate_pdf(analysis, output_path, prose=prose)
    logger.info("Regenerated (pdf-only): %s", output_path)
    return str(output_path)


if __name__ == "__main__":
    import sys
    if "--pdf-only" in sys.argv:
        path = regenerate_pdf_only()
    else:
        path = run()
    if path:
        print(f"\n✓ Report generated: {path}\n")
    else:
        print("\n✗ Run did not produce a report — see logs above.\n")
        raise SystemExit(1)
