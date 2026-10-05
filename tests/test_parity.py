"""
Unit tests for Binary Parity and Synthetic Arbitrage Engine (core/parity.py).
"""

from core.normalizer import NormalizedMarket, OrderBook, OrderLevel
from core.parity import ParityEngine


def make_two_sided_market(platform: str, question: str, best_bid: float, best_ask: float) -> NormalizedMarket:
    book = OrderBook(
        bids=[OrderLevel(price=best_bid, size=10_000.0)],
        asks=[OrderLevel(price=best_ask, size=10_000.0)],
    )
    return NormalizedMarket(
        platform=platform,
        market_id=f"test_{platform}",
        question=question,
        category="Macro",
        book=book,
    )


class TestParityEngine:
    def setup_method(self):
        self.engine = ParityEngine(risk_free_rate=0.0480)

    def test_discount_arbitrage_detection(self):
        """When Ask_YES + Ask_NO < 1.00, discount arbitrage exists."""
        # Polymarket YES Ask is 0.40
        poly = make_two_sided_market("Polymarket", "Fed cut in July 2026", best_bid=0.38, best_ask=0.40)
        # Kalshi YES Bid is 0.65 -> Kalshi NO Ask is (1 - 0.65) = 0.35
        # Total cost to buy guaranteed $1.00 = 0.40 + 0.35 = 0.75 ($0.25 gross discount!)
        kalshi = make_two_sided_market("Kalshi", "Fed cut in July 2026", best_bid=0.65, best_ask=0.68)

        opp = self.engine.evaluate_pair(poly, kalshi, days_to_resolution=60)

        assert opp is not None
        assert opp.strategy_type == "DISCOUNT_BUY_ARB"
        assert opp.gross_spread_bps == 2500.0  # 25% discount = 2,500 bps
        assert opp.net_spread_bps > 2000.0
        assert opp.beats_sofr is True
        assert opp.capital_efficiency_grade == "INSTITUTIONAL_ALPHA"

    def test_no_arbitrage_when_spreads_wide(self):
        """When prices cross within normal bid-ask bounds, no arbitrage is reported."""
        poly = make_two_sided_market("Polymarket", "Fed cut in July 2026", best_bid=0.48, best_ask=0.52)
        kalshi = make_two_sided_market("Kalshi", "Fed cut in July 2026", best_bid=0.48, best_ask=0.52)

        opp = self.engine.evaluate_pair(poly, kalshi, days_to_resolution=60)
        assert opp is None
