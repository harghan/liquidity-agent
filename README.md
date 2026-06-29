# liquidity-agent

A cross-platform prediction-market **liquidity intelligence agent**. It pulls
~300 live markets each from **Polymarket** and **Kalshi**, matches overlapping
markets across venues with an NLP hybrid matcher, walks each orderbook at five
order sizes to measure *real* volume-weighted price impact, scores a **Liquidity
Quality Index (LQI)** per market per platform, and uses the **Anthropic Claude
API** to author the interpretive prose for a **9-page, visual-first PDF research
report**.

```bash
python run_agent.py        # -> outputs/liquidity_report_YYYY-MM-DD.pdf  (+ JSON artifacts)
python run_scheduled.py    # same pipeline, appends a record to outputs/timeseries.json
```

## Pipeline

1. **Collect** ~300 in-scope markets per platform (macro, crypto, politics,
   sports/World Cup) — metadata only, cheap and paged.
2. **Match** equivalent markets across venues. A category gate, then a
   confidence score blending rapidfuzz question similarity with entity-keyword
   similarity (candidate name / rate threshold / asset / team). **Semantic
   guards** reject opposite directions (hike vs cut), mismatched numeric
   thresholds (BTC $150k vs $69k), and different dates. Thresholds are
   category-aware: **0.75** for person/candidate markets, **0.65** otherwise.
   Every near-miss is logged to `rejected_pairs.json`.
3. **Fetch orderbooks** for matched markets only.
4. **Walk each book** at **$500 / $2k / $10k / $50k / $100k**. Impact is the
   volume-weighted execution price minus displayed mid (in bps); where a book is
   exhausted the cost to sweep it is reported as a lower bound — that is where
   the orderbook "breaks".
5. **Score the LQI** (0–100): spread (30%), depth via $2k impact (40%), and
   $10k impact (30%) — mid-book depth weighted highest per practitioner
   convention (cf. Kyle 1985, Amihud 2002, Roll 1984).
6. **Reason + render**: Claude (`claude-sonnet-4-6`) writes the interpretive
   prose as structured JSON grounded in the computed analysis; the report writer
   renders nine pages of charts and styled tables. If the API key is missing or
   the call fails, grounded default prose is used and the report still builds.

## The report (9 pages, visual-first)

1. Title page — dark header band, gold subtitle, run parameters, author credit.
2. Analytics dashboard — four KPI boxes + platform-quality and impact-scaling charts.
3. The money chart — price-impact curves across all five sizes with crosshairs.
4. Liquidity-quality heatmap — every matched market, diverging colour scales.
5. Slippage league table — avoidable-slippage bar chart + ranked table.
6. Cross-platform divergence dot plot — same event, two displayed prices.
7. Probability-vs-impact scatter — liquidity-provision model per platform.
8. Root-cause analysis + platform-specific recommendations.
9. Methodology, limitations, and academic references.

## Output artifacts (`outputs/`)

| File | Contents |
|------|----------|
| `liquidity_report_{date}.pdf` | the 9-page report |
| `rejected_pairs.json` | every near-miss candidate pair with confidence + rejection reason (proof matching is algorithmic) |
| `raw_impacts.json` | full impact dataset at all five order sizes for every market |
| `summary.json` | machine-readable summary: platform LQI, total avoidable slippage, match count, top-3 pairs, timestamp |
| `timeseries.json` | appended per `run_scheduled.py` run, for longitudinal deployment |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env          # add your ANTHROPIC_API_KEY
python run_agent.py
```

Only `ANTHROPIC_API_KEY` is required (for the report prose). All market-data
APIs are free and keyless. Each collector is independently runnable for
smoke-testing: `python -m collectors.polymarket` / `python -m collectors.kalshi`.

## A note on matched-pair counts

The matched set reflects genuine live cross-platform overlap. Presidential
(candidate) markets overlap richly; recession, Fed-rate, and crypto produce a
handful of true equivalents; inflation and World Cup currently have essentially
no economically-identical contracts across the two venues (e.g. Polymarket lists
no CPI markets, and its World Cup contracts are outright-winner while Kalshi's
are per-match). Rather than force category quotas, the agent reports exactly what
the algorithm finds and logs all rejections — by design, with zero
cherry-picking.

## Project structure

```
liquidity-agent/
├── run_agent.py            # single entry point
├── run_scheduled.py        # scheduled runner -> timeseries.json
├── config.py               # all tunable parameters + design system
├── collectors/             # polymarket.py, kalshi.py, http_client.py
├── core/                   # normalizer, matcher, price_impact, scorer
├── agent/                  # report_writer.py (PDF), charts.py (matplotlib)
├── outputs/                # PDF + JSON artifacts
└── logs/                   # timestamped run logs
```

All parameters — order sizes, LQI weights, matching thresholds, Kalshi series,
the model, and the full colour/typography design system — live in `config.py`.
