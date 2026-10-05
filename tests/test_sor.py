"""
Unit and property tests for Smart Order Router (core/sor.py).
Validates mathematical optimality, discrete waterfilling, and alpha quantification.
"""

import math
from core.normalizer import NormalizedMarket, OrderBook, OrderLevel
from core.sor import SmartOrderRouter


def make_test_market(platform: str, market_id: str, asks, bids) -> NormalizedMarket:
    book = OrderBook(
        bids=[OrderLevel(price=p, size=s) for p, s in bids],
        asks=[OrderLevel(price=p, size=s) for p, s in asks],
    )
    return NormalizedMarket(
        platform=platform,
        market_id=market_id,
        question=f"Test Market on {platform}",
        outcome="Yes",
        category="Macro",
        book=book,
    )


class TestSmartOrderRouter:
    def setup_method(self):
        self.router = SmartOrderRouter(include_fees=False)

    def test_single_venue_cheapest_fill(self):
        """When Venue A is strictly cheaper than Venue B at all sizes, route 100% to A."""
        # Venue A has 20,000 shares @ 0.40 ($8,000 depth)
        poly = make_test_market("Polymarket", "pm1", asks=[(0.40, 20_000.0)], bids=[(0.38, 10_000.0)])
        # Venue B has 20,000 shares @ 0.50 ($10,000 depth)
        kalshi = make_test_market("Kalshi", "kx1", asks=[(0.50, 20_000.0)], bids=[(0.48, 10_000.0)])

        result = self.router.route([poly, kalshi], notional_usd=5_000.0, side="buy")

        assert result.filled is True
        assert result.venue_allocations["Polymarket"].notional_usd == 5_000.0
        assert result.venue_allocations["Kalshi"].notional_usd == 0.0
        assert math.isclose(result.blended_vwap, 0.40, rel_tol=1e-4)

    def test_multi_venue_waterfilling_split(self):
        """When Venue A depth is exhausted, order spills into Venue B at next marginal price."""
        # Venue A has 10,000 shares @ 0.40 ($4,000 depth)
        poly = make_test_market("Polymarket", "pm1", asks=[(0.40, 10_000.0)], bids=[(0.38, 5_000.0)])
        # Venue B has 50,000 shares @ 0.45 ($22,500 depth)
        kalshi = make_test_market("Kalshi", "kx1", asks=[(0.45, 50_000.0)], bids=[(0.42, 5_000.0)])

        # Request $10,000 total notional
        result = self.router.route([poly, kalshi], notional_usd=10_000.0, side="buy")

        assert result.filled is True
        # Venue A fills max capacity of $4,000 (10,000 shares @ 0.40)
        assert math.isclose(result.venue_allocations["Polymarket"].notional_usd, 4_000.0, rel_tol=1e-4)
        # Venue B fills remaining $6,000 (13,333.33 shares @ 0.45)
        assert math.isclose(result.venue_allocations["Kalshi"].notional_usd, 6_000.0, rel_tol=1e-4)

        # Total shares = 10,000 + 13,333.333 = 23,333.333
        # Blended VWAP = 10,000 / 23,333.333 = ~0.42857
        expected_vwap = 10_000.0 / (10_000.0 + (6_000.0 / 0.45))
        assert math.isclose(result.blended_vwap, expected_vwap, rel_tol=1e-4)

    def test_sor_strictly_dominates_worst_single_venue(self):
        """Blended execution must be strictly cheaper than routing 100% to the illiquid venue."""
        poly = make_test_market("Polymarket", "pm1", asks=[(0.30, 20_000.0)], bids=[(0.28, 5_000.0)])
        kalshi = make_test_market("Kalshi", "kx1", asks=[(0.60, 20_000.0)], bids=[(0.58, 5_000.0)])

        result = self.router.route([poly, kalshi], notional_usd=5_000.0, side="buy")

        # Routing $5,000 to Kalshi alone costs 0.60 per share => 8,333.33 shares
        # Routing to Polymarket costs 0.30 per share => 16,666.67 shares
        assert result.dollar_savings_vs_worst > 0
        assert result.bps_improvement_vs_worst > 2000.0  # > 2,000 bps advantage

    def test_partial_fill_handling(self):
        """When aggregate book cannot absorb notional, filled=False and max possible shares filled."""
        poly = make_test_market("Polymarket", "pm1", asks=[(0.50, 1_000.0)], bids=[(0.48, 500.0)])  # $500 max
        kalshi = make_test_market("Kalshi", "kx1", asks=[(0.55, 1_000.0)], bids=[(0.50, 500.0)])  # $550 max

        result = self.router.route([poly, kalshi], notional_usd=5_000.0, side="buy")

        assert result.filled is False
        assert math.isclose(result.total_notional_filled, 1_050.0, rel_tol=1e-3)
        assert math.isclose(result.total_shares, 2_000.0, rel_tol=1e-3)
