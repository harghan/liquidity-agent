"""
Unit tests for Autonomous AI & Predictive Microstructure Agent (core/ai_agent.py).
"""

from core.ai_agent import AutonomousSORAgent, ExecutionIntentParser, MicrostructurePredictor
from core.normalizer import NormalizedMarket, OrderBook, OrderLevel


def make_test_market(platform: str, question: str, ask_depth: float) -> NormalizedMarket:
    book = OrderBook(
        bids=[OrderLevel(price=0.48, size=ask_depth * 0.8)],
        asks=[OrderLevel(price=0.50, size=ask_depth)],
    )
    return NormalizedMarket(
        platform=platform,
        market_id=f"test_{platform}",
        question=question,
        category="Fed / Rates",
        book=book,
    )


class TestAIAgent:
    def test_intent_parsing(self):
        prompt = "Hedge $50,000 on Fed rate cuts with max 15 bps slippage immediately"
        intent = ExecutionIntentParser.parse(prompt)

        assert intent.target_size_usd == 50000.0
        assert "fed" in intent.target_event_keywords or "rate" in intent.target_event_keywords
        assert intent.max_slippage_bps == 15.0
        assert intent.urgency == "HIGH"
        assert intent.side == "buy"

    def test_short_intent_parsing(self):
        prompt = "Short $100k of Vivek Ramaswamy 2028 election slowly with iceberg"
        intent = ExecutionIntentParser.parse(prompt)

        assert intent.target_size_usd == 100000.0
        assert "vivek" in intent.target_event_keywords
        assert intent.side == "sell"
        assert intent.urgency == "LOW"
        assert intent.execution_style == "PASSIVE_PEG"

    def test_microstructure_predictor_cadence(self):
        # Small order relative to depth -> immediate sweep
        market = make_test_market("Polymarket", "Fed decision July 2026", ask_depth=500_000.0)
        signals = MicrostructurePredictor.evaluate(market, target_notional=10_000.0)
        assert signals.recommended_cadence == "IMMEDIATE_SWEEP"

        # Large order relative to depth -> staggered iceberg
        signals_large = MicrostructurePredictor.evaluate(market, target_notional=450_000.0)
        assert signals_large.recommended_cadence == "STAGGERED_ICEBERG"

    def test_autonomous_sor_planning(self):
        agent = AutonomousSORAgent()
        p1 = make_test_market("Polymarket", "Fed interest rate decision in 2026", ask_depth=100_000.0)
        k1 = make_test_market("Kalshi", "Fed interest rate decision in 2026", ask_depth=50_000.0)

        plan = agent.plan_execution(
            prompt="Deploy $25,000 across Fed interest rate markets with minimal slippage",
            available_markets=[p1, k1],
        )

        assert plan.intent.target_size_usd == 25000.0
        assert plan.sor_result is not None
        assert plan.sor_result.filled is True
        assert len(plan.pre_signed_hash) > 10
        assert "Autonomous Agent identified optimal liquidity split" in plan.ai_rationale
