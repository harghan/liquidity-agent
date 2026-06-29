"""
Cross-platform market matching (NLP hybrid) — v2.

Markets are matched on meaning, not exact text:

1. Each market is classified into a category. Kalshi markets carry an
   authoritative ``category_hint`` from their series; Polymarket markets are
   classified from text, with a 2026 World Cup nations list so a "[A] vs [B]"
   market is recognised as World Cup even when its text omits the words.
2. Matching is gated to the same category. Within a category, confidence blends
   a rapidfuzz token-set similarity of the full questions with the rapidfuzz
   similarity of the *entity* keywords (boilerplate stripped, so the candidate
   name / rate threshold / asset / team dominates). A hard entity floor blocks
   boilerplate-only matches.
3. Thresholds are category-aware: 0.75 for person/candidate markets, 0.65 for
   everything else. Pairs are assigned greedily, highest-confidence first,
   one-to-one.
4. Every *rejected* near-miss is recorded with its confidence and the precise
   rejection reason, written to ``outputs/rejected_pairs.json`` as evidence the
   selection was algorithmic with zero cherry-picking.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from rapidfuzz import fuzz

import config
from core.normalizer import NormalizedMarket

logger = logging.getLogger("liquidity_agent.matcher")

import re

_TOKEN_RE = re.compile(r"[a-z0-9.%$]+")
# Only near-miss rejections (and above) are logged, to keep the evidence file
# meaningful rather than dumping every cross-product pair.
REJECT_LOG_MIN_CONF = 0.50


@dataclass
class MarketMatch:
    polymarket: NormalizedMarket
    kalshi: NormalizedMarket
    confidence: float
    category: str
    entity_similarity: float

    @property
    def displayed_divergence(self) -> Optional[float]:
        a, b = self.polymarket.displayed_prob, self.kalshi.displayed_prob
        if a is None or b is None:
            return None
        return abs(a - b)


def _tokens(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def _keywords(text: str) -> Set[str]:
    return {t for t in _tokens(text) if t not in config.STOPWORDS and len(t) > 1}


_MONTHS = {
    "jan": "jan", "january": "jan", "feb": "feb", "february": "feb",
    "mar": "mar", "march": "mar", "apr": "apr", "april": "apr", "may": "may",
    "jun": "jun", "june": "jun", "jul": "jul", "july": "jul", "aug": "aug",
    "august": "aug", "sep": "sep", "sept": "sep", "september": "sep",
    "oct": "oct", "october": "oct", "nov": "nov", "november": "nov",
    "dec": "dec", "december": "dec",
}
_NUM_RE = re.compile(r"(\$?)\s*(\d[\d,]*\.?\d*)\s*(k|bps|bp|%|m|million|billion|bn)?", re.I)


def _directions(token_set: Set[str]) -> Set[str]:
    """Return {'up'} / {'down'} / both / empty for a market's wording."""
    s: Set[str] = set()
    if token_set & config.DIRECTION_UP:
        s.add("up")
    if token_set & config.DIRECTION_DOWN:
        s.add("down")
    return s


def _thresholds(text: str) -> Set[float]:
    """Extract normalized numeric thresholds (strikes, bps, %), excluding years."""
    out: Set[float] = set()
    for m in _NUM_RE.finditer(text):
        dollar = m.group(1) == "$"
        try:
            val = float(m.group(2).replace(",", ""))
        except ValueError:
            continue
        unit = (m.group(3) or "").lower()
        if unit == "k":
            val *= 1_000
        elif unit in ("m", "million"):
            val *= 1_000_000
        elif unit in ("billion", "bn"):
            val *= 1_000_000_000
        # Ignore bare numbers with neither a $ sign nor a unit when they are
        # small integers — these are day-of-month, quarters, or small counts
        # ("June 30", "Q2", "11 rate cuts"), not price/rate thresholds. Also
        # drop 4-digit years.
        if not dollar and unit == "" and val == int(val):
            if 1 <= val <= 31 or 2020 <= val <= 2039:
                continue
        out.add(round(val, 4))
    return out


def _months(text: str) -> Set[str]:
    return {_MONTHS[t] for t in _tokens(text) if t in _MONTHS}


def _numeric_conflict(a: Set[float], b: Set[float]) -> bool:
    """True if both sides name thresholds but none align within tolerance."""
    if not a or not b:
        return False
    tol = config.NUMERIC_THRESHOLD_TOLERANCE
    for x in a:
        for y in b:
            hi = max(abs(x), abs(y))
            if hi == 0 or abs(x - y) / hi <= tol:
                return False
    return True


def semantic_conflict(a: NormalizedMarket, b: NormalizedMarket) -> Optional[str]:
    """Return a rejection reason if two same-category markets are not equivalent
    events (opposite direction, disjoint thresholds, or different meeting/date),
    else None."""
    at, bt = set(_tokens(a.question)), set(_tokens(b.question))
    ad, bd = _directions(at), _directions(bt)
    if ad and bd and not (ad & bd):
        return "directional_conflict"
    if _numeric_conflict(_thresholds(a.question), _thresholds(b.question)):
        return "numeric_threshold_mismatch"
    am, bm = _months(a.question), _months(b.question)
    if am and bm and not (am & bm):
        return "date_horizon_mismatch"
    return None


def classify_text(question: str) -> str:
    """Text-based category classification (used when no series hint exists)."""
    low = question.lower()
    if " vs " in low or "vs." in low or " v " in low:
        teams = [t for t in config.WORLD_CUP_TEAMS if t in low]
        if len(teams) >= 2 or "world cup" in low or "fifa" in low:
            return "World Cup"
    for category, includes, excludes in config.CATEGORY_RULES:
        if any(k in low for k in includes) and not any(e in low for e in excludes):
            return category
    return "Other"


def classify(market: NormalizedMarket) -> str:
    """Category for a market — series hint first, then text."""
    hint = market.extra.get("category_hint") if market.extra else None
    if isinstance(hint, str) and hint:
        return hint
    return classify_text(market.question)


def _entity_similarity(a: NormalizedMarket, b: NormalizedMarket) -> float:
    ka = " ".join(sorted(_keywords(a.question)))
    kb = " ".join(sorted(_keywords(b.question)))
    if not ka or not kb:
        return 0.0
    return fuzz.token_set_ratio(ka, kb) / 100.0


def score_pair(a: NormalizedMarket, b: NormalizedMarket) -> Tuple[float, float]:
    """Return ``(confidence, entity_similarity)`` in [0, 1]."""
    fuzzy = fuzz.token_set_ratio(a.question.lower(), b.question.lower()) / 100.0
    entity = _entity_similarity(a, b)
    confidence = config.MATCH_FUZZY_WEIGHT * fuzzy + config.MATCH_KEYWORD_WEIGHT * entity
    return confidence, entity


def _threshold_for(category: str) -> float:
    return (config.MATCH_THRESHOLD_PERSON if category in config.PERSON_CATEGORIES
            else config.MATCH_THRESHOLD_DEFAULT)


def match_markets(
    polymarket: List[NormalizedMarket],
    kalshi: List[NormalizedMarket],
) -> Tuple[List[MarketMatch], List[Dict[str, object]]]:
    """Return ``(matches, rejected)``.

    ``matches`` are confident one-to-one pairs; ``rejected`` is the list of
    near-miss candidate pairs with confidence and rejection reason.
    """
    poly_cat = {id(m): classify(m) for m in polymarket}
    kal_cat = {id(m): classify(m) for m in kalshi}

    # Score every same-category candidate pair.
    cands: List[Tuple[float, float, NormalizedMarket, NormalizedMarket, str, float, bool]] = []
    for pm in polymarket:
        pc = poly_cat[id(pm)]
        if pc not in config.MATCHABLE_CATEGORIES:
            continue
        for km in kalshi:
            if kal_cat[id(km)] != pc:
                continue
            conf, entity = score_pair(pm, km)
            thr = _threshold_for(pc)
            conflict = semantic_conflict(pm, km)
            passes = conf >= thr and entity >= config.MATCH_ENTITY_FLOOR and conflict is None
            cands.append((conf, entity, pm, km, pc, thr, passes, conflict))

    cands.sort(key=lambda t: t[0], reverse=True)
    used_p: Set[int] = set()
    used_k: Set[int] = set()
    matches: List[MarketMatch] = []
    rejected: List[Dict[str, object]] = []

    for conf, entity, pm, km, cat, thr, passes, conflict in cands:
        accepted = False
        reason: Optional[str] = None
        if passes and id(pm) not in used_p and id(km) not in used_k:
            used_p.add(id(pm))
            used_k.add(id(km))
            matches.append(MarketMatch(pm, km, conf, cat, entity))
            pm.category = cat
            km.category = cat
            accepted = True
        elif passes:
            reason = "lost_greedy_assignment_to_higher_confidence_pair"
        elif conflict is not None:
            reason = conflict
        elif conf < thr:
            reason = "confidence_below_category_threshold"
        else:  # conf >= thr but entity < floor
            reason = "entity_similarity_below_floor"

        if not accepted and conf >= REJECT_LOG_MIN_CONF:
            rejected.append({
                "category": cat,
                "confidence": round(conf, 3),
                "entity_similarity": round(entity, 3),
                "threshold": thr,
                "reason": reason,
                "polymarket_id": pm.market_id,
                "polymarket_question": pm.question,
                "kalshi_id": km.market_id,
                "kalshi_question": km.question,
            })

    matches.sort(key=lambda m: m.confidence, reverse=True)
    rejected.sort(key=lambda r: r["confidence"], reverse=True)

    by_cat: Dict[str, int] = {}
    for m in matches:
        by_cat[m.category] = by_cat.get(m.category, 0) + 1
    logger.info("Matched %d pairs; %d near-miss rejections logged", len(matches), len(rejected))
    logger.info("Matches by category: %s", by_cat)
    return matches, rejected
