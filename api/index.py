"""
PRISM // Vercel Serverless API Endpoint.
Exposes Autonomous AI Smart Order Router (SOR), Microstructure Predictor, and Synthetic Parity.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.ai_agent import AutonomousSORAgent, ExecutionIntentParser, MicrostructurePredictor
from core.normalizer import NormalizedMarket, build_orderbook
from core.parity import ParityEngine
from core.sor import SmartOrderRouter


def get_demo_markets(event_name: str = "Vivek Ramaswamy 2028"):
    """Generate realistic live L2 books for SOR calculation."""
    if "Vivek" in event_name:
        mid_p, mid_k = 0.0065, 0.0025
    elif "FOMC" in event_name or "Fed" in event_name:
        mid_p, mid_k = 0.6200, 0.5900
    elif "Recession" in event_name:
        mid_p, mid_k = 0.2400, 0.2150
    else:
        mid_p, mid_k = 0.0450, 0.0380

    poly_asks = [
        (round(mid_p + 0.005, 4), 15_000.0),
        (round(mid_p + 0.015, 4), 35_000.0),
        (round(mid_p + 0.030, 4), 80_000.0),
        (round(mid_p + 0.060, 4), 150_000.0),
    ]
    poly_bids = [
        (round(mid_p - 0.005, 4), 12_000.0),
        (round(mid_p - 0.015, 4), 30_000.0),
        (round(mid_p - 0.025, 4), 70_000.0),
    ]

    kalshi_asks = [
        (round(mid_k + 0.002, 4), 5_000.0),
        (round(mid_k + 0.010, 4), 12_000.0),
        (round(mid_k + 0.040, 4), 25_000.0),
        (round(mid_k + 0.120, 4), 40_000.0),  # Steep liquidity cliff
    ]
    kalshi_bids = [
        (round(mid_k - 0.002, 4), 4_000.0),
        (round(mid_k - 0.010, 4), 10_000.0),
        (round(mid_k - 0.030, 4), 20_000.0),
    ]

    pm = NormalizedMarket(
        platform="Polymarket",
        market_id="pm_live_01",
        question=event_name,
        category="Presidential Election",
        book=build_orderbook(poly_bids, poly_asks),
    )
    km = NormalizedMarket(
        platform="Kalshi",
        market_id="kx_live_01",
        question=event_name,
        category="Presidential Election",
        book=build_orderbook(kalshi_bids, kalshi_asks),
    )
    return pm, km


class handler(BaseHTTPRequestHandler):
    """Vercel serverless request handler."""

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json({"status": "ok"})

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        req_path = self.headers.get("x-matched-path") or self.headers.get("x-forwarded-uri") or parsed.path
        route_param = query.get("__route", [""])[0]
        check_str = f"{req_path} {route_param} {parsed.path}".lower()

        if "health" in check_str:
            return self._send_json({
                "status": "healthy",
                "service": "PRISM Liquidity Refraction Engine",
                "version": "2.1.0",
                "venues": ["Polymarket", "Kalshi"],
            })

        if "ai" in check_str or "prompt" in query:
            prompt = query.get("prompt", ["Deploy $50k on Vivek Ramaswamy with < 20 bps slippage"])[0]
            return self._send_json(self._generate_ai_plan(prompt))

        if "markets" in check_str:
            events = [
                {
                    "id": "vivek_2028",
                    "title": "Will Vivek Ramaswamy win the 2028 US Presidential Election?",
                    "category": "Presidential Election",
                    "poly_mid": 0.0065,
                    "kalshi_mid": 0.0025,
                    "spread_bps": 40.0,
                    "liquidity_usd": 21461179.0,
                },
                {
                    "id": "fomc_july_2026",
                    "title": "Federal Reserve Interest Rate Decision (FOMC July 2026)",
                    "category": "Fed / Rates",
                    "poly_mid": 0.6200,
                    "kalshi_mid": 0.5900,
                    "spread_bps": 300.0,
                    "liquidity_usd": 12850000.0,
                },
                {
                    "id": "tim_walz_2028",
                    "title": "Will Tim Walz win the 2028 US Presidential Election?",
                    "category": "Presidential Election",
                    "poly_mid": 0.0550,
                    "kalshi_mid": 0.0500,
                    "spread_bps": 50.0,
                    "liquidity_usd": 8940000.0,
                },
                {
                    "id": "recession_2026",
                    "title": "Will the US enter an NBER Recession before 2027?",
                    "category": "Recession",
                    "poly_mid": 0.2400,
                    "kalshi_mid": 0.2150,
                    "spread_bps": 250.0,
                    "liquidity_usd": 4200000.0,
                },
            ]
            return self._send_json({"events": events})

        if "parity" in check_str:
            parity_engine = ParityEngine(risk_free_rate=0.0480)
            opportunities = [
                {
                    "pair": "Federal Reserve Rate Decision (Dec 2026)",
                    "strategy": "DISCOUNT_BUY_ARB",
                    "gross_bps": 320.0,
                    "net_bps": 284.5,
                    "profit_10k": 284.50,
                    "annualized_roic": "14.4%",
                    "beats_sofr": True,
                    "grade": "INSTITUTIONAL_ALPHA",
                },
                {
                    "pair": "Vivek Ramaswamy 2028 Presidential",
                    "strategy": "CASH_OUT_ARB",
                    "gross_bps": 40.0,
                    "net_bps": 18.2,
                    "profit_10k": 18.20,
                    "annualized_roic": "0.7%",
                    "beats_sofr": False,
                    "grade": "CAPITAL_DESTRUCTIVE",
                },
            ]
            return self._send_json({"opportunities": opportunities, "sofr_benchmark": 0.0480})

        # Default fallback: Route order via GET query parameters
        event_name = query.get("event", ["Vivek Ramaswamy 2028"])[0]
        size_usd = float(query.get("size", [25000.0])[0])
        side = query.get("side", ["buy"])[0]

        pm, km = get_demo_markets(event_name)
        router = SmartOrderRouter(include_fees=True)
        res = router.route([pm, km], notional_usd=size_usd, side=side)

        return self._send_json(self._serialize_sor(res))

    def do_POST(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        req_path = self.headers.get("x-matched-path") or self.headers.get("x-forwarded-uri") or parsed.path
        route_param = query.get("__route", [""])[0]
        check_str = f"{req_path} {route_param} {parsed.path}".lower()

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            body = json.loads(post_body.decode("utf-8"))
        except Exception:
            body = {}

        if "prompt" in body or "ai" in check_str:
            prompt = body.get("prompt", "Deploy $50k on Vivek Ramaswamy with < 20 bps slippage")
            return self._send_json(self._generate_ai_plan(prompt))

        event_name = body.get("event", "Vivek Ramaswamy 2028")
        size_usd = float(body.get("size_usd", 25000.0))
        side = body.get("side", "buy")

        pm, km = get_demo_markets(event_name)
        router = SmartOrderRouter(include_fees=True)
        res = router.route([pm, km], notional_usd=size_usd, side=side)

        return self._send_json(self._serialize_sor(res))

    def _generate_ai_plan(self, prompt: str):
        markets = []
        for ev in ["Vivek Ramaswamy 2028", "Federal Reserve FOMC July 2026", "Recession 2026"]:
            pm, km = get_demo_markets(ev)
            markets.extend([pm, km])

        ai_agent = AutonomousSORAgent()
        plan = ai_agent.plan_execution(prompt, markets)

        return {
            "status": "success",
            "prompt": plan.intent.raw_prompt,
            "intent": {
                "target_size_usd": plan.intent.target_size_usd,
                "side": plan.intent.side,
                "outcome_target": plan.intent.outcome_target,
                "max_slippage_bps": plan.intent.max_slippage_bps,
                "urgency": plan.intent.urgency,
                "execution_style": plan.intent.execution_style,
                "keywords": plan.intent.target_event_keywords,
            },
            "signals": {
                "order_book_imbalance": plan.signals.order_book_imbalance,
                "microprice_drift_bps": plan.signals.microprice_drift_bps,
                "predicted_impact_bps": plan.signals.predicted_impact_bps,
                "recommended_cadence": plan.signals.recommended_cadence,
                "confidence_score": plan.signals.confidence_score,
            },
            "matched_event": plan.matched_market.question if plan.matched_market else "Vivek Ramaswamy 2028",
            "ai_rationale": plan.ai_rationale,
            "pre_signed_hash": plan.pre_signed_hash,
            "sor_result": self._serialize_sor(plan.sor_result) if plan.sor_result else None,
        }

    def _serialize_sor(self, res):
        allocs = {}
        for plat, a in res.venue_allocations.items():
            allocs[plat] = {
                "notional_usd": a.notional_usd,
                "shares": a.shares,
                "vwap": a.vwap,
                "effective_vwap": a.effective_vwap,
                "total_fee_usd": a.total_fee_usd,
                "pct_of_total_order": a.pct_of_total_order,
            }

        steps = [
            {
                "step": s.step_index,
                "platform": s.platform,
                "raw_price": s.price,
                "effective_price": s.effective_price,
                "shares": s.size_shares,
                "notional_usd": s.notional_usd,
                "cumulative_notional": s.cumulative_notional,
                "cumulative_vwap": s.cumulative_vwap,
            }
            for s in res.execution_steps
        ]

        return {
            "target_notional_usd": res.target_notional_usd,
            "side": res.side,
            "filled": res.filled,
            "total_notional_filled": res.total_notional_filled,
            "total_shares": res.total_shares,
            "blended_vwap": res.blended_vwap,
            "blended_effective_vwap": res.blended_effective_vwap,
            "total_fees_usd": res.total_fees_usd,
            "dollar_savings_vs_worst": res.dollar_savings_vs_worst,
            "bps_improvement_vs_worst": res.bps_improvement_vs_worst,
            "legging_risk_index": res.legging_risk_index,
            "venue_allocations": allocs,
            "execution_steps": steps,
        }
