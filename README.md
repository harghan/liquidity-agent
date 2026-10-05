# PRISM // Institutional Prediction Market Liquidity & Smart Order Router (SOR)

[![Tests](https://img.shields.io/badge/tests-14%2F14%20passing-brightgreen)](#test-suite)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](#architecture)
[![License](https://img.shields.io/badge/license-Proprietary-red)](#commercial-model)

An enterprise-grade quantitative execution engine, autonomous AI order refraction agent, and liquidity intelligence terminal designed for macro hedge funds, quantitative proprietary trading desks, and institutional brokers trading event derivatives across fragmented prediction venues (**Polymarket** and **Kalshi**).

---

## ⚡ The Blue Ocean Value Proposition

Retail traders and unsophisticated screen-watchers look at displayed mid-prices. **Serious capital looks at executable depth, marginal liquidity consumption, and book exhaustion.**

* **The Problem:** In fragmented prediction markets, executing an institutional clip (\$25k to \$100k+) on a single venue can cause an **84x price inflation** due to shallow orderbook depth.
* **The Solution:** PRISM provides a **non-custodial Smart Order Router (SOR)** and **Autonomous AI Execution Agent** that continuously streams orderbooks across decentralized CLOBs (Polymarket) and CFTC-regulated exchanges (Kalshi), solving the discrete marginal cost waterfilling problem in sub-milliseconds to minimize implementation shortfall.

```
                                 PRISM SYSTEM ARCHITECTURE
   
  [ Ingestion Layer ]                 [ Quantitative & AI Core ]        [ Enterprise Delivery ]
  
  +----------------------+            +-----------------------+         +-----------------------+
  | Polymarket CLOB      |            | Autonomous AI Agent   |         | PRISM Web Terminal    |
  | (Polygon Off-Chain)  |---+        | (NLP Intent Parser &  |         | (Vercel Production &  |
  +----------------------+   |        |  Microstructure Pred) |         |  Apple Pro UI)        |
                             +------->+-----------------------+-------->| - Real-Time SOR Sim   |
  +----------------------+   |        | Smart Order Router    |         | - Spotlight ⌘K Bar    |
  | Kalshi CFTC DCM      |---+        | (Discrete Waterfill   |         | - Depth Waterfall     |
  | (Secaucus Engine)    |            |  Marginal Cost Opt)   |         | - Parity Radar        |
  +----------------------+            +-----------------------+         +-----------------------+
                                      | Parity & Basis Engine |         | High-Throughput       |
                                      | (Binary Parity &      |-------->| B2B Execution API     |
                                      |  SOFR Hurdle Rate)    |         | (JSON / Serverless)   |
                                      +-----------------------+         +-----------------------+
```

---

## 🚀 Key Features

### 1. Multi-Venue Smart Order Router (`core/sor.py`)
* **Equal-Marginal-Price Discrete Waterfilling:** Solves $\min \sum \text{Cost}_i(q_i)$ subject to $\sum q_i = Q_{\text{target}}$ across heterogeneous orderbooks.
* **Fee-Adjusted Marginal Cost:** Ingests Kalshi's CFTC variable fee curve $3.5\% \times p(1-p)$ and Polymarket's gas/relayer dynamics.
* **Implementation Shortfall & Alpha Quantification:** Automatically calculates exact dollar savings vs. worst-case single venue and slippage basis point improvements.
* **Legging Risk Index:** Measures cross-venue execution and partial fill risk (0 to 100).

### 2. Microstructure & Parity Engine (`core/parity.py` & `core/normalizer.py`)
* **Two-Sided Parity:** Full support for `BUY YES`, `BUY NO`, `SELL YES`, and `SELL NO` via binary complement orderbook mapping ($P_{\text{YES}} + P_{\text{NO}} = 1.00$).
* **Order Book Imbalance (OBI) & Microprice:** Real-time adverse selection predictors at the top of the book.
* **Capital Efficiency & SOFR Hurdle Evaluation:** Benchmarks synthetic arbitrage against the 4.80% risk-free rate, warning desks when the 200% margin lockup makes a trade capital-destructive.

### 3. Institutional Resolution & Temporal Matcher (`core/matcher.py`)
* **Zero False-Positive Calendar Matching:** Strict `_years()` extraction guarantees that cross-year contracts (e.g., 2026 vs. 2027 Fed cuts) trigger immediate `year_horizon_mismatch` rejections.
* **Semantic Conflict Guards:** Deterministic rejection of opposing directions (`hike` vs. `cut`) and disjoint numeric strike thresholds.

### 4. Interactive Web Terminal (`app.py`)
* High-frequency dark-theme interactive interface powered by Streamlit and Plotly.
* Live SOR Execution Simulator with real-time allocation sliders and execution waterfall charts.
* Side-by-side cumulative depth waterfall comparison and synthetic arbitrage monitor.

---

## 🛠️ Quickstart

### 1. Launch the Institutional Web Terminal
```bash
streamlit run app.py
```
Access the interactive terminal at `http://localhost:8501`.

### 2. Run the Quantitative Test Suite
```bash
python3 test_all.py
```

---

## 🧪 Test Suite

The quantitative core is backed by 14 comprehensive unit, microstructure, and AI agent property tests verifying mathematical optimality and autonomous execution:

| Test Name | Component | Verified Property |
| :--- | :--- | :--- |
| `test_single_venue_cheapest_fill` | `core/sor.py` | 100% allocation to single venue when strictly dominant |
| `test_multi_venue_waterfilling_split` | `core/sor.py` | Optimal spillover allocation at exact marginal cost threshold |
| `test_sor_strictly_dominates_worst` | `core/sor.py` | Proven reduction in implementation shortfall vs single venue |
| `test_partial_fill_handling` | `core/sor.py` | Graceful degradation and capacity reporting on book exhaustion |
| `test_year_horizon_mismatch` | `core/matcher.py` | Deterministic rejection of disjoint resolution years (2026 vs 2027) |
| `test_directional_conflict` | `core/matcher.py` | Immediate rejection of opposing bets (hike vs cut) |
| `test_month_horizon_mismatch` | `core/matcher.py` | Calendar mismatch detection within fiscal year |
| `test_identical_events_pass` | `core/matcher.py` | High-confidence matching of economically identical events |
| `test_discount_arbitrage_detection` | `core/parity.py` | Detection of $Ask_{\text{YES}} + Ask_{\text{NO}} < 1.00$ discounts |
| `test_no_arbitrage_when_spreads_wide` | `core/parity.py` | No false arbitrage alarms during normal bid/ask spreads |
| `test_intent_parsing` | `core/ai_agent.py` | Natural language parameter extraction (size, side, slippage, urgency) |
| `test_short_intent_parsing` | `core/ai_agent.py` | Directional classification for synthetic shorts and hedges |
| `test_microstructure_predictor_cadence`| `core/ai_agent.py` | OBI, microprice drift, and iceberg vs sweep queue classification |
| `test_autonomous_sor_planning` | `core/ai_agent.py` | End-to-end plan generation, PM rationale, and cryptographic ticket |

---

## 📁 Project Layout

```
liquidity-agent/
├── public/                 # Enterprise Apple Pro Web Terminal (Jony Ive Design System)
│   └── index.html          # PRISM Web Terminal with Spotlight ⌘K AI Mandate Engine
├── api/                    # Vercel Serverless Python Backend
│   └── index.py            # Endpoints: /api/route, /api/markets, /api/parity, /api/ai/plan
├── core/
│   ├── ai_agent.py         # Autonomous Execution Agent & Predictive Microstructure
│   ├── sor.py              # Enterprise Smart Order Router (Discrete Waterfilling)
│   ├── parity.py           # Synthetic binary parity & SOFR hurdle rate engine
│   ├── normalizer.py       # Normalized schemas, microprice, fees, OrderBook
│   ├── matcher.py          # Temporal horizon & semantic conflict matcher
│   ├── price_impact.py     # Multi-size book walker ($500 to $100k)
│   └── scorer.py           # Liquidity Quality Index (LQI)
├── app.py                  # Streamlit TCA & Macro Execution Terminal
├── test_all.py             # Standalone test runner (14/14 tests)
├── collectors/             # Polymarket & Kalshi REST / CLOB fetchers
├── tests/                  # Test suite (test_sor, test_matcher, test_parity, test_ai_agent)
└── outputs/                # Historical datasets, raw impacts, summary JSON
```

---

## 💼 Commercial Model & Ideal Customer Profile (ICP)

1. **Macro Hedge Funds & Quantitative Prop Desks:** Pre-trade market impact simulator and non-custodial Smart Order Routing API to deploy 6-figure positions with minimal slippage.
2. **Neo-Brokers & Web3 Frontends:** White-label routing SDK enabling retail frontends to tap unified cross-venue liquidity.
3. **Market Makers:** Real-time cross-venue basis alerts and oracle resolution divergence monitoring.
