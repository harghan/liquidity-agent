"""
Unit tests for NLP Matcher & Semantic Conflict Detection (core/matcher.py).
Ensures zero false-positives across temporal horizons and contract terms.
"""

from core.matcher import semantic_conflict, score_pair
from core.normalizer import NormalizedMarket


def make_market(platform: str, question: str, category: str = "Fed / Rates") -> NormalizedMarket:
    return NormalizedMarket(
        platform=platform,
        market_id=f"test_{platform}",
        question=question,
        category=category,
    )


class TestMatcherSafety:
    def test_year_horizon_mismatch_strictly_rejected(self):
        """A 2026 contract must NEVER match a 2027 contract."""
        m_2026 = make_market("Polymarket", "Fed rate hike in 2026?")
        m_2027 = make_market(
            "Kalshi",
            "Will the Federal Reserve Hike rates by 0bps at their December 2027 meeting? — Fed maintains rate",
        )

        reason = semantic_conflict(m_2026, m_2027)
        assert reason == "year_horizon_mismatch", f"Expected year_horizon_mismatch, got: {reason}"

    def test_directional_conflict_rejected(self):
        """Hike vs Cut must be rejected as opposite economic bets."""
        m_hike = make_market("Polymarket", "Federal Reserve interest rate hike in July 2026?")
        m_cut = make_market("Kalshi", "Federal Reserve interest rate cut in July 2026?")

        reason = semantic_conflict(m_hike, m_cut)
        assert reason == "directional_conflict", f"Expected directional_conflict, got: {reason}"

    def test_month_horizon_mismatch_rejected(self):
        """July 2026 vs December 2026 must be rejected."""
        m_jul = make_market("Polymarket", "Fed rate cut in July 2026?")
        m_dec = make_market("Kalshi", "Fed rate cut in December 2026?")

        reason = semantic_conflict(m_jul, m_dec)
        assert reason == "date_horizon_mismatch", f"Expected date_horizon_mismatch, got: {reason}"

    def test_identical_events_pass(self):
        """Identical candidate / horizon pairs should have zero conflict."""
        m_poly = make_market(
            "Polymarket",
            "Will Vivek Ramaswamy win the 2028 US Presidential Election?",
            category="Presidential Election",
        )
        m_kalshi = make_market(
            "Kalshi",
            "Who will win the next presidential election? — Vivek Ramaswamy",
            category="Presidential Election",
        )

        reason = semantic_conflict(m_poly, m_kalshi)
        assert reason is None, f"Expected no conflict for equivalent events, got: {reason}"
