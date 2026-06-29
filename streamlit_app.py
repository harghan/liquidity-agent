"""
Liquidity Agent — cross-platform prediction-market liquidity intelligence.

Product-grade Streamlit front end over the analysis pipeline: live orderbook
collection, NLP cross-platform matching, five-tier price-impact analysis, the
Liquidity Quality Index, and an on-demand Claude-authored research narrative.

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import json

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components  # noqa: F401 (available for embeds)

import config
from collectors import kalshi, polymarket
from collectors.http_client import get_json
from core import matcher, price_impact, scorer
from run_agent import _key, build_analysis

# ---------------------------------------------------------------------------
# Page config + design system
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Liquidity Agent", page_icon="◆", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── VIEWPORT & TOUCH ───────────────────────── */
html { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; scroll-behavior: smooth; }
* { -webkit-tap-highlight-color: rgba(200,169,81,0.1); touch-action: manipulation; }
body, .main { overflow-x: hidden !important; max-width: 100vw !important; }
[data-testid="column"], [data-testid="metric-container"], .stButton > button { transition: all 0.2s ease !important; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"], .main, .block-container {
    background-color: #080808 !important;
    color: #e8e8e8 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}
.block-container {
    padding: 0 40px 80px 40px !important;
    max-width: 1320px !important;
    margin: 0 auto !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], .stDeployButton,
[data-testid="collapsedControl"] { display: none !important; }

[data-testid="stSidebar"] { background: #050505 !important; border-right: 1px solid #141414 !important; padding-top: 0 !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
/* Sidebar nav buttons (session-state navigation, not radio) */
[data-testid="stSidebar"] .stButton > button {
    text-align: left !important; justify-content: flex-start !important; padding: 10px 24px !important;
    border: none !important; border-left: 2px solid transparent !important; border-radius: 0 !important;
    color: #555 !important; font-size: 10px !important; letter-spacing: 2px !important;
    width: 100% !important; background: transparent !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    color: #999 !important; background: #0d0d0d !important; border-left-color: #333 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    color: #c8a951 !important; border-left-color: #c8a951 !important; background: #0d0d0d !important;
}

[data-testid="metric-container"] { background: #0d0d0d !important; border: 1px solid #1a1a1a !important; border-radius: 0 !important; padding: 1.5rem 1.75rem !important; }
[data-testid="stMetricLabel"] { font-size: 9px !important; letter-spacing: 2.5px !important; text-transform: uppercase !important; color: #c8a951 !important; font-family: 'DM Mono', monospace !important; }
[data-testid="stMetricValue"] { font-family: 'DM Mono', monospace !important; font-size: 2.25rem !important; font-weight: 300 !important; color: #fff !important; letter-spacing: -1px !important; }

.stButton > button {
    background: transparent !important; border: 1px solid #1e1e1e !important; color: #666 !important;
    border-radius: 0 !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 2.5px !important; text-transform: uppercase !important; padding: 0.65rem 1.75rem !important;
    transition: all 0.2s ease !important; font-weight: 400 !important;
}
.stButton > button:hover { border-color: #c8a951 !important; color: #c8a951 !important; background: rgba(200,169,81,0.04) !important; }
.stButton > button[kind="primary"] { background: #c8a951 !important; border-color: #c8a951 !important; color: #080808 !important; font-weight: 500 !important; }
.stButton > button[kind="primary"]:hover { background: #d4b862 !important; }
[data-testid="stDownloadButton"] > button {
    background: #c8a951 !important; border: 1px solid #c8a951 !important; color: #080808 !important;
    border-radius: 0 !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 2.5px !important; text-transform: uppercase !important; padding: 0.65rem 1.75rem !important; font-weight: 500 !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #d4b862 !important; }

.stProgress > div > div > div { background: #c8a951 !important; border-radius: 0 !important; }
.stProgress > div > div { background: #141414 !important; border-radius: 0 !important; height: 2px !important; }
div[data-testid="stStatus"], [data-testid="stExpander"] { background: #0d0d0d !important; border: 1px solid #1a1a1a !important; border-radius: 0 !important; }

[data-testid="stSelectbox"] > div > div { background: #0d0d0d !important; border: 1px solid #1a1a1a !important; border-radius: 0 !important; color: #e8e8e8 !important; }
.streamlit-expanderHeader { background: #0d0d0d !important; border: 1px solid #1a1a1a !important; border-radius: 0 !important; font-family: 'DM Mono', monospace !important; font-size: 11px !important; letter-spacing: 1px !important; color: #888 !important; }
.js-plotly-plot { border: 1px solid #141414 !important; }
/* Let charts pan the page vertically on touch instead of trapping scroll */
.js-plotly-plot .plotly { touch-action: pan-y !important; overscroll-behavior: contain !important; }
[data-testid="stPlotlyChart"] { touch-action: pan-y !important; pointer-events: auto !important; }
[data-testid="stPlotlyChart"] .plotly-graph-div { touch-action: pan-y !important; }
hr { border: none !important; border-top: 1px solid #141414 !important; margin: 2rem 0 !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080808; }
::-webkit-scrollbar-thumb { background: #1e1e1e; }
::-webkit-scrollbar-thumb:hover { background: #c8a951; }
.stSpinner > div { border-top-color: #c8a951 !important; }
[data-testid="column"] { padding: 0 6px !important; }
[data-testid="column"]:first-child { padding-left: 0 !important; }
[data-testid="column"]:last-child { padding-right: 0 !important; }
.stMarkdown p { color: #999 !important; line-height: 1.75 !important; font-size: 14px !important; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { font-family: 'Inter', sans-serif !important; font-weight: 500 !important; color: #e8e8e8 !important; }

/* ── RESPONSIVE BREAKPOINTS ─────────────────── */
@media screen and (max-width: 1024px) {
    .block-container { padding: 0 16px 64px !important; }
    [data-testid="stSidebar"] { min-width: 200px !important; max-width: 200px !important; }
    [data-testid="column"] { padding: 0 3px !important; }
}
@media screen and (max-width: 768px) {
    .main .block-container { padding: 0 10px 56px !important; max-width: 100vw !important; }
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 1px !important; }
    [data-testid="column"] { min-width: calc(50% - 1px) !important; flex: 1 1 calc(50% - 1px) !important; padding: 0 !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    [data-testid="metric-container"] { padding: 1rem !important; }
    .stMarkdown p { font-size: 13px !important; }
    .js-plotly-plot { width: 100% !important; }
    .stButton > button { width: 100% !important; padding: 0.85rem 1rem !important; }
    [data-testid="stSidebar"][aria-expanded="false"] { margin-left: -244px !important; }
    [data-testid="collapsedControl"] { display: flex !important; top: 1rem !important; left: 1rem !important; }
}
@media screen and (max-width: 480px) {
    [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
    [data-testid="stMetricValue"] { font-size: 1.25rem !important; }
}
</style>
""", unsafe_allow_html=True)

GOLD = "#c8a951"
SIZE_LABELS = ["$500", "$2k", "$10k", "$50k", "$100k"]


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
def _g(d, *path, default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def load_cached_analysis():
    p = config.OUTPUT_DIR / "analysis.json"
    if p.exists():
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


_SHORT_CAT = {
    "Presidential Election": "PRES", "Primary / Nomination": "PRIM", "Fed / Rates": "FED",
    "Recession": "REC", "Crypto": "CRYPTO", "World Cup": "WC", "Sports": "SPORT",
    "GDP": "GDP", "Unemployment": "U3",
}


def _flatten_pair(p):
    pm, kx = p.get("polymarket", {}), p.get("kalshi", {})
    cv = p.get("cheaper_venue")
    return {
        "name": p.get("subject", ""),
        "category": _SHORT_CAT.get(p.get("category", ""), "MKT"),
        "confidence": p.get("confidence", 0) or 0,
        "avoidable_slippage_usd": p.get("avoidable_slippage_10k") or 0,
        "cheaper_venue": "PM" if cv == "Polymarket" else ("KX" if cv == "Kalshi" else "PM"),
        "pm_mid": pm.get("mid") or 0, "kx_mid": kx.get("mid") or 0,
        "pm_impact_10k_bps": _g(pm, "impact_bps", "10000") or 0,
        "kx_impact_10k_bps": _g(kx, "impact_bps", "10000") or 0,
        "pm_lqi": pm.get("lqi") or 0, "kx_lqi": kx.get("lqi") or 0,
        "divergence_bps": p.get("divergence_bps") or 0,
        "polymarket_slug": p.get("polymarket_slug") or "",
        "kalshi_ticker": p.get("kalshi_ticker") or "",
    }


# ---------------------------------------------------------------------------
# Live World Cup feeds (unmatched, shown side by side)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def fetch_wc_polymarket(limit=12):
    out = []
    for off in range(0, 600, 100):
        data = get_json(config.POLYMARKET_GAMMA_MARKETS, params={
            "active": "true", "closed": "false", "limit": 100, "offset": off,
            "order": "volumeNum", "ascending": "false"}, context="wc polymarket")
        if not isinstance(data, list) or not data:
            break
        for m in data:
            q = (m.get("question") or ""); slug = (m.get("slug") or "")
            blob = (q + " " + slug).lower()
            if "world cup" in blob or "fifa" in blob or "world-cup" in slug:
                prices = m.get("outcomePrices")
                if isinstance(prices, str):
                    try:
                        prices = json.loads(prices)
                    except json.JSONDecodeError:
                        prices = []
                prob = None
                if prices:
                    try:
                        prob = float(prices[0])
                    except (TypeError, ValueError):
                        prob = None
                try:
                    vol = float(m.get("volumeNum") or 0)
                except (TypeError, ValueError):
                    vol = 0
                out.append({"name": q, "prob": prob, "volume": vol,
                            "url": f"https://polymarket.com/event/{slug}" if slug else "https://polymarket.com"})
        if len(out) >= limit:
            break
    out.sort(key=lambda r: r["volume"], reverse=True)
    return out[:limit]


@st.cache_data(ttl=600, show_spinner=False)
def fetch_wc_kalshi(limit=12):
    data = get_json(config.KALSHI_MARKETS, params={"series_ticker": "KXWCGAME", "status": "open", "limit": 60},
                    context="wc kalshi")
    out = []
    if isinstance(data, dict):
        for m in data.get("markets", []):
            title = (m.get("title") or "").strip()
            sub = (m.get("yes_sub_title") or "").strip()
            name = f"{title} — {sub}" if sub and sub.lower() not in title.lower() else title
            try:
                prob = float(m.get("last_price_dollars") or 0)
            except (TypeError, ValueError):
                prob = 0
            tk = m.get("event_ticker") or m.get("ticker") or ""
            out.append({"name": name, "prob": prob, "volume": 0,
                        "url": f"https://kalshi.com/markets/{tk}" if tk else "https://kalshi.com/markets"})
    return out[:limit]


# ---------------------------------------------------------------------------
# Live pipeline
# ---------------------------------------------------------------------------
def run_pipeline_live():
    prog = st.progress(0.0)
    status = st.status("Initialising engine", expanded=True)

    def step(label, pct):
        status.write(label)
        prog.progress(pct)

    try:
        step("Connecting to Polymarket CLOB API...", 0.1)
        step("Connecting to Kalshi trade-api v2...", 0.2)
        step("Fetching 300 markets per platform...", 0.35)
        poly = polymarket.collect_metadata(config.TARGET_MARKETS_PER_PLATFORM)
        kal = kalshi.collect_metadata(config.TARGET_MARKETS_PER_PLATFORM)
        step("Running NLP market matcher — evaluating pairs...", 0.5)
        matches, rejected = matcher.match_markets(poly, kal)
        step(f"{len(matches)} matches found · {len(rejected)} pairs rejected", 0.6)
        step("Walking orderbooks at $500 / $2k / $10k / $50k / $100k...", 0.75)
        matched_markets, seen = [], set()
        for m in matches:
            for mkt, fetch in ((m.polymarket, polymarket.fetch_book), (m.kalshi, kalshi.fetch_book)):
                if _key(mkt) in seen:
                    continue
                seen.add(_key(mkt))
                try:
                    if fetch(mkt):
                        matched_markets.append(mkt)
                except Exception:  # noqa: BLE001
                    pass
        impacts = price_impact.compute_all(matched_markets)
        step("Calculating Liquidity Quality Index...", 0.85)
        lqi = scorer.score_all(impacts)
        step("Generating research narrative...", 0.95)
        analysis = build_analysis(poly, kal, matches, matched_markets, impacts, lqi, rejected)
        step("Complete.", 1.0)
        status.update(label="Analysis complete", state="complete", expanded=False)
        return analysis
    except Exception as exc:  # noqa: BLE001
        status.update(label=f"Run failed: {exc}", state="error")
        st.error(f"Pipeline error: {exc}")
        return None


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------
def page_header(label, title, subtitle=""):
    st.markdown(f"""
    <div style="padding:32px 0 28px;border-bottom:1px solid #141414;margin-bottom:28px">
        <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:3px;color:{GOLD};margin-bottom:8px;text-transform:uppercase">{label}</div>
        <div style="font-family:'Inter',sans-serif;font-size:clamp(18px,3vw,26px);font-weight:500;color:#fff;letter-spacing:-0.5px;line-height:1.2;margin-bottom:{'8px' if subtitle else '0'}">{title}</div>
        {f'<div style="font-size:clamp(11px,1.5vw,13px);color:#444;margin-top:6px;font-weight:300">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def kpi_card(label, value, sub="", accent="#ffffff"):
    return f"""
    <div style="background:#0d0d0d;border:1px solid #141414;padding:20px 24px;position:relative;overflow:hidden;height:100%">
        <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,{GOLD} 0%,transparent 60%)"></div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:2.5px;color:{GOLD};text-transform:uppercase;margin-bottom:12px">{label}</div>
        <div style="font-family:'DM Mono',monospace;font-size:2rem;font-weight:300;color:{accent};letter-spacing:-1px;line-height:1">{value}</div>
        {f'<div style="font-size:11px;color:#444;margin-top:8px;font-family:DM Mono,monospace">{sub}</div>' if sub else ''}
    </div>
    """


def render_kpis(total_slippage, n_markets, n_rejected, lqi_gap, pm_lqi, kx_lqi, max_diverg, max_diverg_market):
    arrow = "▲" if lqi_gap >= 0 else "▼"
    gap_color = "#4ade80" if lqi_gap >= 0 else "#f87171"

    def cell(label, value, sub, accent):
        return (f'<div style="background:#0d0d0d;border:1px solid #141414;padding:20px 24px;position:relative;overflow:hidden">'
                f'<div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,{GOLD},transparent)"></div>'
                f'<div style="font-family:\'DM Mono\',monospace;font-size:9px;letter-spacing:2.5px;color:{GOLD};text-transform:uppercase;margin-bottom:10px">{label}</div>'
                f'<div style="font-family:\'DM Mono\',monospace;font-size:clamp(1.5rem,3vw,2.25rem);font-weight:300;color:{accent};letter-spacing:-1px;line-height:1">{value}</div>'
                f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#444;margin-top:8px">{sub}</div></div>')

    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1px;margin-bottom:24px">'
        + cell("Total avoidable slippage", f"${total_slippage:,.0f}", f"$10k notional · {n_markets} pairs", GOLD)
        + cell("Markets analysed", str(n_markets), f"from {n_rejected:,} evaluated pairs", "#ffffff")
        + cell("Mean LQI gap", f"{arrow} {abs(lqi_gap):.1f}", f"PM {pm_lqi:.1f} vs KX {kx_lqi:.1f}", gap_color)
        + cell("Max divergence", f"{max_diverg:,.0f} bps", max_diverg_market, "#f87171")
        + '</div>', unsafe_allow_html=True)


def render_pdf_section(a):
    from datetime import datetime
    section_label("Institutional Report", "Nine-Page Research Memo",
                  "Claude-authored narrative rendered to a professional PDF")
    pdf_path = config.OUTPUT_DIR / f"liquidity_report_{a['run_date']}.pdf"

    c1, c2, _ = st.columns([2, 1, 2])
    gen = c1.button("↓ Generate Research Report", use_container_width=True)
    regen = c2.button("↻ Regenerate", use_container_width=True)

    if gen or regen:
        if regen or not pdf_path.exists():
            if not config.ANTHROPIC_API_KEY:
                st.markdown('<div style="color:#444;font-size:12px;font-family:DM Mono,monospace">'
                            'Set ANTHROPIC_API_KEY in .env to author the narrative.</div>', unsafe_allow_html=True)
            with st.spinner("Generating institutional research report..."):
                try:
                    from agent import report_writer
                    # Reuse the in-session analysis — no data pipeline re-run.
                    report_writer.generate_pdf(a, pdf_path)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Report generation failed: {exc}")

    if pdf_path.exists():
        import re as _re
        data = pdf_path.read_bytes()
        pages = len(_re.findall(rb"/Type\s*/Page[^s]", data)) or "—"
        ts = datetime.fromtimestamp(pdf_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:11px;color:#4ade80;margin:14px 0 10px">'
                    f'✓ Report ready — {pages} pages · {len(data)/1024:.0f} KB · generated {ts}</div>',
                    unsafe_allow_html=True)
        st.download_button("↓ Download Research Report (PDF)", data,
                           file_name=f"liquidity_report_{a['run_date']}.pdf",
                           mime="application/pdf", use_container_width=False)


def section_label(label, title="", muted=""):
    st.markdown(f"""
    <div style="margin-bottom:{'20px' if not title else '12px'};margin-top:8px">
        <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:3px;color:{GOLD};text-transform:uppercase">{label}</div>
        {f'<div style="font-size:16px;font-weight:500;color:#e8e8e8;font-family:Inter,sans-serif;margin-top:6px;letter-spacing:-0.3px">{title}</div>' if title else ''}
        {f'<div style="font-size:12px;color:#444;margin-top:6px;font-family:DM Mono,monospace;line-height:1.6">{muted}</div>' if muted else ''}
    </div>
    """, unsafe_allow_html=True)


def market_card(pair):
    name = pair["name"]
    cat = pair.get("category", "PRES")
    confidence = pair.get("confidence", 0)
    avoidable = pair.get("avoidable_slippage_usd", 0)
    cheaper = pair.get("cheaper_venue", "PM")
    pm_mid = pair.get("pm_mid", 0); kx_mid = pair.get("kx_mid", 0)
    pm_imp = pair.get("pm_impact_10k_bps", 0); kx_imp = pair.get("kx_impact_10k_bps", 0)
    pm_lqi = pair.get("pm_lqi", 0); kx_lqi = pair.get("kx_lqi", 0)
    divergence = pair.get("divergence_bps", 0)

    pm_url = f"https://polymarket.com/event/{pair.get('polymarket_slug', '')}" if pair.get("polymarket_slug") else "https://polymarket.com"
    kx_url = f"https://kalshi.com/markets/{pair.get('kalshi_ticker', '')}" if pair.get("kalshi_ticker") else "https://kalshi.com/markets"

    cat_colors = {"PRES": ("#0d0d20", "#60a5fa"), "FED": ("#0d2018", "#4ade80"), "REC": ("#200d0d", "#f87171")}
    cat_bg, cat_fg = cat_colors.get(cat, ("#161205", GOLD))
    cheaper_label = "Route to Polymarket" if cheaper == "PM" else "Route to Kalshi"
    cheaper_color = "#e0e0e0" if cheaper == "PM" else GOLD
    pm_imp_color = "#4ade80" if pm_imp < 100 else "#999" if pm_imp < 500 else "#f87171"
    kx_imp_color = "#4ade80" if kx_imp < 100 else "#999" if kx_imp < 500 else "#f87171"
    border_color = GOLD if cheaper == "KX" else "#1e1e1e"

    return f"""
    <div style="background:#0d0d0d;border:1px solid {border_color};margin-bottom:8px;padding:20px 24px;position:relative;overflow:hidden">
        <div style="position:absolute;top:0;left:0;bottom:0;width:2px;background:{GOLD if cheaper=='KX' else '#1e1e1e'}"></div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;flex-wrap:wrap;gap:8px">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap">
                    <span style="background:{cat_bg};color:{cat_fg};font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1.5px;padding:3px 8px">{cat}</span>
                    <span style="font-family:'DM Mono',monospace;font-size:9px;color:#444;letter-spacing:1px">conf: {confidence:.3f}</span>
                </div>
                <div style="font-size:16px;font-weight:500;color:#fff;font-family:'Inter',sans-serif;letter-spacing:-0.3px">{name}</div>
            </div>
            <div style="text-align:right;flex-shrink:0">
                <div style="font-family:'DM Mono',monospace;font-size:1.4rem;font-weight:300;color:{GOLD};letter-spacing:-0.5px">${avoidable:,.0f}</div>
                <div style="font-family:'DM Mono',monospace;font-size:8px;letter-spacing:2px;color:#444;margin-top:2px">AVOIDABLE SLIPPAGE</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;margin-bottom:14px">
            <div style="background:#080808;padding:14px 16px">
                <div style="font-family:'DM Mono',monospace;font-size:8px;letter-spacing:2px;color:#555;margin-bottom:8px">POLYMARKET</div>
                <div style="font-family:'DM Mono',monospace;font-size:1.2rem;font-weight:300;color:#fff;margin-bottom:4px">{pm_mid*100:.2f}¢</div>
                <div style="font-size:10px;color:{pm_imp_color};margin-bottom:10px;font-family:'DM Mono',monospace">{pm_imp:.0f} bps · LQI {pm_lqi:.1f}</div>
                <a href="{pm_url}" target="_blank" style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.5px;color:{GOLD};text-decoration:none;border:1px solid {GOLD};padding:4px 12px;display:inline-block;white-space:nowrap">TRADE →</a>
            </div>
            <div style="background:#080808;padding:14px 16px;border-left:1px solid #141414">
                <div style="font-family:'DM Mono',monospace;font-size:8px;letter-spacing:2px;color:#555;margin-bottom:8px">KALSHI</div>
                <div style="font-family:'DM Mono',monospace;font-size:1.2rem;font-weight:300;color:#fff;margin-bottom:4px">{kx_mid*100:.2f}¢</div>
                <div style="font-size:10px;color:{kx_imp_color};margin-bottom:10px;font-family:'DM Mono',monospace">{kx_imp:.0f} bps · LQI {kx_lqi:.1f}</div>
                <a href="{kx_url}" target="_blank" style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.5px;color:#888;text-decoration:none;border:1px solid #1e1e1e;padding:4px 12px;display:inline-block;white-space:nowrap">TRADE →</a>
            </div>
        </div>
        <div style="display:flex;gap:12px;border-top:1px solid #141414;padding-top:10px;font-family:'DM Mono',monospace;font-size:10px;color:#444;flex-wrap:wrap">
            <span>$10k: <span style="color:{pm_imp_color}">{pm_imp:.0f}</span> PM · <span style="color:{kx_imp_color}">{kx_imp:.0f}</span> KX</span>
            <span style="color:#1e1e1e">·</span>
            <span>Div: <span style="color:{GOLD if divergence > 100 else '#555'}">{divergence:.0f} bps</span></span>
            <span style="color:#1e1e1e">·</span>
            <span>Route: <span style="color:{cheaper_color}">{'PM' if cheaper=='PM' else 'KX'}</span></span>
        </div>
    </div>
    """


def wc_market_card(name, prob, volume, url, platform):
    color = "#e0e0e0" if platform == "PM" else GOLD
    prob_txt = f"{prob*100:.1f}%" if prob is not None else "—"
    vol_txt = f"· ${volume:,.0f} vol" if (platform == "PM" and volume) else ""
    return f"""
    <div style="background:#0d0d0d;border:1px solid #141414;padding:16px 20px;margin-bottom:6px">
        <div style="font-size:12px;font-weight:500;color:#e8e8e8;margin-bottom:8px;font-family:Inter,sans-serif;line-height:1.4">{name}</div>
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <div style="font-family:'DM Mono',monospace;font-size:1.1rem;color:{color}">{prob_txt}</div>
                <div style="font-family:'DM Mono',monospace;font-size:9px;color:#444;margin-top:2px">implied probability {vol_txt}</div>
            </div>
            <a href="{url}" target="_blank" style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.5px;color:#555;text-decoration:none;border:1px solid #1a1a1a;padding:4px 12px">TRADE →</a>
        </div>
    </div>
    """


def pull_quote(text):
    st.markdown(f"""
    <div style="border-left:2px solid {GOLD};padding:18px 0 18px 28px;margin:28px 0">
        <div style="font-family:'DM Mono',monospace;font-size:clamp(1.1rem,2.2vw,1.6rem);font-weight:300;color:{GOLD};line-height:1.5;font-style:italic">"{text}"</div>
    </div>
    """, unsafe_allow_html=True)


def finding_card(number, label, sub):
    st.markdown(f"""
    <div style="background:#0d0d0d;border:1px solid #141414;padding:24px;position:relative;overflow:hidden;height:100%">
        <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,{GOLD},transparent)"></div>
        <div style="font-family:'DM Mono',monospace;font-size:1.75rem;font-weight:300;color:{GOLD};margin-bottom:8px;letter-spacing:-1px">{number}</div>
        <div style="font-size:12px;font-weight:500;color:#e8e8e8;margin-bottom:4px;font-family:Inter,sans-serif">{label}</div>
        <div style="font-size:11px;color:#444;font-family:'DM Mono',monospace;line-height:1.6">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def team_card(name, role):
    initials = "".join(n[0] for n in name.split()[:2]).upper()
    return f"""
    <div style="display:flex;align-items:center;gap:16px;padding:14px 0;border-bottom:1px solid #0d0d0d">
        <div style="width:36px;height:36px;background:#141414;border:1px solid #1e1e1e;display:flex;align-items:center;justify-content:center;font-family:'DM Mono',monospace;font-size:11px;color:{GOLD};flex-shrink:0">{initials}</div>
        <div>
            <div style="font-size:13px;font-weight:500;color:#e8e8e8;font-family:Inter,sans-serif">{name}</div>
            <div style="font-size:11px;color:#555;font-family:'DM Mono',monospace;margin-top:2px">{role}</div>
        </div>
    </div>
    """


def render_narrative(text):
    # Narrative is multi-paragraph (blank lines) so markdown re-parses it and
    # would treat $...$ as math — escaping is required HERE (and only here).
    escaped = text.replace("$", r"\$")
    st.markdown(f"""
    <div style="background:#060606;border:1px solid #141414;border-left:2px solid {GOLD};padding:28px 32px;margin-top:24px">
        <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:2px;color:{GOLD};margin-bottom:20px;text-transform:uppercase">Autonomous Research Narrative · claude-sonnet-4-6</div>
        <div style="font-family:'DM Mono',monospace;font-size:12px;line-height:2;color:#999;white-space:pre-wrap">{escaped}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
def style_fig(fig, height=460):
    fig.update_layout(
        paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d", height=height, autosize=True,
        font=dict(family="DM Mono, monospace", color="#666", size=10),
        margin=dict(l=10, r=16, t=36, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#141414", borderwidth=1,
                    font=dict(size=10, color="#888"),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(font=dict(family="DM Mono, monospace")),
    )
    fig.update_xaxes(gridcolor="#141414", linecolor="#141414", tickcolor="#141414",
                     zerolinecolor="#141414", automargin=True)
    fig.update_yaxes(gridcolor="#141414", linecolor="#141414", tickcolor="#141414",
                     zerolinecolor="#141414", automargin=True)
    return fig


def price_impact_curve(a):
    stats = a.get("platform_stats", {})
    sizes = [str(int(s)) for s in a.get("order_sizes_usd", [500, 2000, 10000, 50000, 100000])]
    pm = [(_g(stats, "Polymarket", "mean_impact_bps", s) or 0) for s in sizes]
    kx = [(_g(stats, "Kalshi", "mean_impact_bps", s) or 0) for s in sizes]
    x = list(range(len(SIZE_LABELS)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=pm, name="Polymarket", mode="lines+markers",
                             line=dict(color="#ffffff", width=2.5), marker=dict(size=7)))
    fig.add_trace(go.Scatter(x=x, y=kx, name="Kalshi", mode="lines+markers",
                             line=dict(color=GOLD, width=2.5, dash="dash"), marker=dict(size=7),
                             fill="tonexty", fillcolor="rgba(200,169,81,0.05)"))
    for xi, lab in ((2, "$10k"), (4, "$100k")):
        fig.add_vline(x=xi, line=dict(color="#444", width=1, dash="dot"))
        fig.add_annotation(x=xi, y=max(pm[xi], kx[xi]), yshift=26, showarrow=False,
                           text=f"<b>{lab}</b>  PM {pm[xi]:,.0f} · KX {kx[xi]:,.0f} bps",
                           font=dict(family="DM Mono, monospace", size=9, color="#ccc"),
                           bgcolor="#0d0d0d", bordercolor=GOLD, borderwidth=1, borderpad=4)
    fig.update_xaxes(tickmode="array", tickvals=x, ticktext=SIZE_LABELS)
    fig.update_yaxes(title_text="bps")
    return style_fig(fig, height=440)


def slippage_bar(a):
    pairs = [p for p in a.get("pairs", []) if p.get("avoidable_slippage_10k") is not None]
    pairs.sort(key=lambda p: p["avoidable_slippage_10k"])
    labels = [p["subject"][:22] for p in pairs]
    vals = [p["avoidable_slippage_10k"] for p in pairs]
    colors = ["#e0e0e0" if (p.get("cheaper_venue") == "Polymarket") else GOLD for p in pairs]
    fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h", marker_color=colors,
                           text=[f"${v:,.0f}" for v in vals], textposition="outside",
                           textfont=dict(family="DM Mono, monospace", size=10, color="#888"),
                           hovertemplate="%{y}: $%{x:,.0f}<extra></extra>"))
    if vals:
        mean_v = sum(vals) / len(vals)
        fig.add_vline(x=mean_v, line=dict(color=GOLD, width=1.2, dash="dash"))
        fig.add_annotation(x=mean_v, y=len(labels) - 0.4, yshift=12, showarrow=False,
                           text=f"mean ${mean_v:,.0f}", font=dict(family="DM Mono, monospace", size=9, color=GOLD))
    fig.update_xaxes(title_text="USD")
    return style_fig(fig, height=max(360, 34 * len(labels) + 90))


# ---------------------------------------------------------------------------
# Narrative payload + streaming
# ---------------------------------------------------------------------------
def narrative_payload(a):
    """Numerical data and market names only — no raw API identifiers or URLs."""
    def _clean_side(s):
        return {"mid": s.get("mid"), "spread_bps": s.get("spread_bps"), "lqi": s.get("lqi"),
                "grade": s.get("grade"), "impact_bps": s.get("impact_bps")}

    clean_pairs = [{
        "market": p.get("subject"), "category": p.get("category"), "confidence": p.get("confidence"),
        "divergence_bps": p.get("divergence_bps"), "avoidable_slippage_10k": p.get("avoidable_slippage_10k"),
        "cheaper_venue": p.get("cheaper_venue"),
        "polymarket": _clean_side(p.get("polymarket", {})), "kalshi": _clean_side(p.get("kalshi", {})),
    } for p in a.get("pairs", [])]
    return {
        "platform_stats": a.get("platform_stats", {}), "cost_summary": a.get("cost_summary"),
        "lqi_gap_overall": a.get("lqi_gap_overall"), "universe": a.get("universe"), "pairs": clean_pairs,
    }


def stream_narrative(a):
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    payload = narrative_payload(a)
    system = (
        "You are a senior market-structure and liquidity strategist at a quantitative trading firm. "
        "You write precise institutional research, cite exact figures, and never invent numbers. "
        "Write in plain prose ONLY. Do NOT use any Markdown syntax: no '#' headers, no '**' bold, no "
        "'###', no bullet characters. For each section, put an ALL-CAPS label on its own line, then a "
        "line break, then the paragraph beneath it."
    )
    user = (
        "Write a five-paragraph institutional research memo on cross-platform prediction-market "
        "liquidity (Polymarket vs Kalshi), grounded strictly in the JSON below. Use exactly these five "
        "sections, each introduced by its ALL-CAPS label on its own line followed by the paragraph: "
        "EXECUTIVE SUMMARY, KEY FINDINGS, ROOT CAUSE ANALYSIS, PLATFORM-SPECIFIC RECOMMENDATIONS, "
        "LIMITATIONS. Separate sections with a blank line. Name real matched markets and quote real "
        "figures (LQI, impact in bps, divergence, dollar slippage). Be dense and specific. Remember: "
        "plain prose, no Markdown symbols anywhere.\n\n"
        f"DATA:\n{json.dumps(payload, default=str)}"
    )
    with client.messages.stream(model=config.ANTHROPIC_MODEL, max_tokens=2200,
                                system=system, messages=[{"role": "user", "content": user}]) as stream:
        for text in stream.text_stream:
            yield text


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_live():
    page_header("Liquidity Agent", "Cross-Platform Prediction Market Intelligence",
                "Real-time orderbook analysis · Polymarket × Kalshi · 300 markets")

    if "analysis_running" not in st.session_state:
        st.session_state.analysis_running = False

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("Run Live Analysis", type="primary", use_container_width=True):
            # Flag the run; clear cached results so the pipeline executes once.
            st.session_state.analysis_running = True
            st.session_state["analysis"] = None
            st.session_state.pop("narrative", None)

    # Run the pipeline only when flagged and not already cached — so navigating
    # away and back never re-runs it (Streamlit re-executes the script on every
    # interaction; the session-state cache is the fix).
    if st.session_state.analysis_running and not st.session_state.get("analysis"):
        result = run_pipeline_live()
        st.session_state["analysis"] = result
        st.session_state.analysis_running = False

    a = st.session_state.get("analysis")
    if not a:
        st.markdown('<div style="color:#444;font-size:13px;text-align:center;margin-top:2rem;font-family:DM Mono,monospace">'
                    'Press RUN LIVE ANALYSIS to pull live orderbooks.</div>', unsafe_allow_html=True)
        return

    cost = a.get("cost_summary", {})
    uni = a.get("universe", {})
    maxd = cost.get("max_divergence") or {}
    gap = a.get("lqi_gap_overall") or 0
    pm_lqi = _g(a, "platform_stats", "Polymarket", "mean_lqi") or 0
    kx_lqi = _g(a, "platform_stats", "Kalshi", "mean_lqi") or 0

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    render_kpis(
        total_slippage=cost.get("total_avoidable_slippage_10k", 0) or 0,
        n_markets=uni.get("compared_pairs", 0),
        n_rejected=uni.get("near_miss_rejections", 0),
        lqi_gap=gap, pm_lqi=pm_lqi, kx_lqi=kx_lqi,
        max_diverg=maxd.get("bps", 0) or 0,
        max_diverg_market=(maxd.get("subject") or "")[:22],
    )

    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
    section_label("Price Impact", "Where the Orderbook Breaks",
                  "Mean volume-weighted impact vs displayed mid, $500 → $100k")
    st.plotly_chart(price_impact_curve(a), use_container_width=True,
                    config={"displayModeBar": False, "scrollZoom": False, "staticPlot": False, "responsive": True})

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    section_label("Execution Cost", "Avoidable Slippage by Market",
                  "Savings from routing a $10,000 order to the cheaper venue")
    st.plotly_chart(slippage_bar(a), use_container_width=True,
                    config={"displayModeBar": False, "scrollZoom": False, "staticPlot": False, "responsive": True})

    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
    section_label("Autonomous Research Narrative")
    if not config.ANTHROPIC_API_KEY:
        st.markdown('<div style="color:#444;font-size:13px;font-family:DM Mono,monospace">Set ANTHROPIC_API_KEY '
                    'in .env to generate the AI research memo.</div>', unsafe_allow_html=True)
    else:
        if st.button("Generate Narrative"):
            try:
                placeholder = st.empty()
                acc = ""
                for chunk in stream_narrative(a):
                    acc += chunk
                    with placeholder.container():
                        render_narrative(acc)
                st.session_state["narrative"] = acc
            except Exception as exc:  # noqa: BLE001
                st.error(f"Narrative generation failed: {exc}")
        elif st.session_state.get("narrative"):
            render_narrative(st.session_state["narrative"])

    st.markdown('<hr>', unsafe_allow_html=True)
    render_pdf_section(a)


def page_markets():
    page_header("Market Intelligence", "Matched Markets",
                "Identical outcomes, two venues — ranked by avoidable execution cost")

    # ── World Cup section (unmatched, side by side) ────────────────────────
    section_label("Why We Started Here", "World Cup 2026")
    st.markdown(
        '<div style="background:#0d0d0d;border:1px solid #141414;border-left:2px solid {g}; '
        'padding:20px 24px;margin-bottom:24px;font-size:13px;line-height:1.8;color:#999;'
        'font-family:Inter,sans-serif;font-weight:300">'
        'This project began in a group chat during the 2026 FIFA World Cup, asking why prediction '
        'market parlays kept bleeding money. World Cup markets exist on both platforms but cannot be '
        'directly compared — Polymarket lists outright tournament-winner markets while Kalshi lists '
        'per-match binary outcomes (KXWCGAME series). This structural incompatibility is itself a '
        'finding: two platforms covering the same sporting event through incompatible contract designs, '
        'preventing cross-platform arbitrage and price comparison.</div>'.format(g=GOLD),
        unsafe_allow_html=True)

    wc_l, wc_r = st.columns(2)
    with wc_l:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:2px;'
                    'color:#e0e0e0;margin-bottom:10px">POLYMARKET — TOURNAMENT FUTURES</div>',
                    unsafe_allow_html=True)
        try:
            pm_wc = fetch_wc_polymarket()
        except Exception:  # noqa: BLE001
            pm_wc = []
        if pm_wc:
            for r in pm_wc:
                st.markdown(wc_market_card(r["name"], r["prob"], r["volume"], r["url"], "PM"),
                            unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#444;font-size:12px;font-family:DM Mono,monospace">No live markets.</div>',
                        unsafe_allow_html=True)
    with wc_r:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:2px;'
                    f'color:{GOLD};margin-bottom:10px">KALSHI — MATCH MARKETS</div>',
                    unsafe_allow_html=True)
        try:
            kx_wc = fetch_wc_kalshi()
        except Exception:  # noqa: BLE001
            kx_wc = []
        if kx_wc:
            for r in kx_wc:
                st.markdown(wc_market_card(r["name"], r["prob"], r["volume"], r["url"], "KX"),
                            unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#444;font-size:12px;font-family:DM Mono,monospace">No live markets.</div>',
                        unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Matched pairs ──────────────────────────────────────────────────────
    a = st.session_state.get("analysis")
    if not a or not a.get("pairs"):
        st.markdown('<div style="color:#444;font-size:13px;font-family:DM Mono,monospace">Run an analysis on the '
                    'Live Analysis page to populate matched markets.</div>', unsafe_allow_html=True)
        return

    section_label("Cross-Platform Matches", "Matched Pairs")
    f1, f2 = st.columns([1, 1])
    cat = f1.selectbox("Category", ["All", "PRES", "FED", "REC"])
    sort = f2.selectbox("Sort", ["By Slippage", "By LQI", "By Divergence"])

    pairs = [_flatten_pair(p) for p in a["pairs"]]
    if cat != "All":
        pairs = [p for p in pairs if p["category"] == cat]
    if sort == "By Slippage":
        pairs.sort(key=lambda p: p["avoidable_slippage_usd"], reverse=True)
    elif sort == "By LQI":
        pairs.sort(key=lambda p: p["pm_lqi"], reverse=True)
    else:
        pairs.sort(key=lambda p: p["divergence_bps"], reverse=True)

    st.markdown(f'<div style="color:#444;font-size:10px;font-family:DM Mono,monospace;letter-spacing:1px;'
                f'margin:8px 0 14px">{len(pairs)} MATCHED PAIRS</div>', unsafe_allow_html=True)
    for p in pairs:
        st.markdown(market_card(p), unsafe_allow_html=True)


def page_about():
    page_header("The Story", "Why We Built This")
    pull_quote("Prediction markets look liquid until you actually try to trade size.")
    st.markdown(
        '<div style="font-size:14px;line-height:1.85;color:#999;max-width:880px;font-weight:300;'
        'font-family:Inter,sans-serif">During the 2026 FIFA World Cup, a group chat between friends — '
        'Harsha, Aadish, Sohan, and Nitin — kept asking the same question: why did every prediction '
        'market parlay feel like it was bleeding money before the match even resolved? The obvious answer '
        'was bad luck. The real answer was systematic: execution friction that quoted spreads completely '
        'mask. A market showing a 0.65¢ YES ask and a tight 10 bps spread looks liquid — but walk $10,000 '
        'through that orderbook and Kalshi\'s execution cost reaches 257 bps, a 1,222% premium over '
        'Polymarket for the identical outcome. This is not a retail problem. It is an infrastructure '
        'problem, and nobody had measured it systematically across platforms until now.</div>',
        unsafe_allow_html=True)

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    section_label("The Findings")
    a = st.session_state.get("analysis") or {}
    cost = a.get("cost_summary", {})
    uni = a.get("universe", {})
    total = cost.get("total_avoidable_slippage_10k", 52139)
    compared = uni.get("compared_pairs", 15)
    maxbps = (cost.get("max_divergence") or {}).get("bps", 2545)
    rej = uni.get("near_miss_rejections", 2453)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        finding_card(f"${total:,.0f}", "Avoidable slippage", f"across {compared} matched markets · $10k notional")
    with fc2:
        finding_card(f"{maxbps:,.0f} bps", "Max price divergence", "on Fed-rate markets, same event")
    with fc3:
        finding_card(f"{rej:,}", "Near-miss pairs rejected", "zero false positives in the final set")

    st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)
    section_label("Built By")
    st.markdown(team_card("Harsha Ghandikota",
                          "Quantitative research, system design & engineering — conceived and "
                          "built end to end · Duke University, Master of Engineering Management candidate"),
                unsafe_allow_html=True)
    st.markdown(team_card("Claude Sonnet (Anthropic)",
                          "Autonomous analysis and report generation"), unsafe_allow_html=True)

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    section_label("Acknowledgments")
    st.markdown(
        '<div style="font-size:13px;line-height:1.85;color:#999;max-width:880px;font-weight:300;'
        'font-family:Inter,sans-serif">Thanks to <span style="color:#e8e8e8">Aadish Sanghvi</span>, '
        '<span style="color:#e8e8e8">Sohan Kumar Rustumpet</span>, and '
        '<span style="color:#e8e8e8">Nitin Kumar Rustumpet</span> — the friends in the group chat '
        'that started this, and early validators who pressure-tested the idea and gave feedback '
        'along the way.</div>', unsafe_allow_html=True)


def page_methodology():
    page_header("Methodology", "How It Works", "Technical documentation")
    st.markdown(f'<a href="https://github.com/harghan/liquidity-agent" target="_blank" '
                f'style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:2px;color:{GOLD};'
                f'text-decoration:none;border:1px solid {GOLD};padding:8px 18px;display:inline-block;'
                f'margin-bottom:24px">VIEW SOURCE ON GITHUB ↗</a>', unsafe_allow_html=True)

    with st.expander("ORDERBOOK-WALKING VWAP", expanded=True):
        st.markdown(
            "For each market we take a live orderbook snapshot and simulate a market buy of the YES "
            "outcome, walking the ask side level by level until the target notional is filled. The "
            "volume-weighted average execution price minus the displayed mid, in basis points, is the "
            "realized price impact. Unlike the quoted bid-ask spread — which describes only the top of "
            "book — VWAP-at-size captures the full shape of available liquidity. We measure five tiers: "
            "$500, $2,000, $10,000, $50,000 and $100,000, spanning retail through fund scale.")
    with st.expander("MARKET MATCHING ALGORITHM"):
        st.markdown(
            "A category gate, then a confidence score blending rapidfuzz token-set similarity of the "
            "full question with the similarity of extracted entity keywords (candidate name, rate "
            "threshold, asset, team). Semantic guards reject opposite directions, mismatched numeric "
            "thresholds, and different dates. Thresholds are category-aware — 0.75 for person/candidate "
            "markets, 0.65 otherwise. Every same-category near-miss is logged with its score and "
            "rejection reason as evidence the matched set is algorithmic, not cherry-picked.")
    with st.expander("LIQUIDITY QUALITY INDEX"):
        st.markdown(
            "A composite 0–100 score: bid-ask spread (30%), depth via $2k impact (40%), and $10k impact "
            "(30%) — mid-book depth weighted highest per institutional convention. Component scores ramp "
            "linearly to configured caps and blend into a single grade per market per platform.")
    with st.expander("LIMITATIONS"):
        st.markdown(
            "Phantom liquidity: displayed limit orders may be cancelled on approach, so figures represent "
            "displayed depth, not guaranteed execution; this affects both platforms equally and does not "
            "bias the comparison. The analysis is a single snapshot and can shift within hours of a news "
            "catalyst. The 40/30/30 LQI weighting reflects practitioner judgment, not a universal "
            "standard. Kalshi sports contracts are geofenced in certain states.")

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    section_label("Academic Grounding")
    for cite in [
        "Kyle, A. S. (1985). Continuous Auctions and Insider Trading. Econometrica, 53(6), 1315–1335. "
        "— the linear price-impact coefficient (λ) relating order flow to price movement.",
        "Amihud, Y. (2002). Illiquidity and Stock Returns. Journal of Financial Markets, 5(1), 31–56. "
        "— precedent for a volume-normalized illiquidity ratio.",
        "Roll, R. (1984). A Simple Implicit Measure of the Effective Bid-Ask Spread. Journal of Finance, "
        "39(4), 1127–1139. — prior art for inferring effective transaction cost.",
    ]:
        st.markdown(f'<div style="font-size:12px;color:#777;line-height:1.7;margin-bottom:10px;'
                    f'font-family:Inter,sans-serif;font-weight:300;max-width:880px">{cite}</div>',
                    unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar + routing
# ---------------------------------------------------------------------------
if "analysis" not in st.session_state:
    cached = load_cached_analysis()
    if cached:
        st.session_state["analysis"] = cached

if "page" not in st.session_state:
    st.session_state.page = "Live Analysis"

with st.sidebar:
    st.markdown("""
    <div style="padding:28px 24px 20px;border-bottom:1px solid #141414">
        <div style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:3px;color:#c8a951;margin-bottom:4px">LIQUIDITY AGENT</div>
        <div style="font-size:11px;color:#333;line-height:1.5">Prediction Market<br>Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    # Session-state button navigation (robust vs custom CSS, unlike st.radio).
    # Active page renders as a styled label; others stay clickable buttons.
    _pages = ["Live Analysis", "Markets", "About", "Methodology"]
    _icons = ["⬤", "◈", "◎", "◻"]
    for _icon, _p in zip(_icons, _pages):
        label = f"{_icon}  {_p.upper()}"
        if st.session_state.page == _p:
            st.markdown(
                f'<div style="padding:10px 24px;font-family:\'DM Mono\',monospace;font-size:10px;'
                f'letter-spacing:2px;color:#c8a951;border-left:2px solid #c8a951;background:#0d0d0d;'
                f'cursor:default">{label}</div>', unsafe_allow_html=True)
        else:
            if st.button(label, key=f"nav_{_p}", use_container_width=True):
                st.session_state.page = _p
                st.rerun()

    st.markdown("""
    <div style="padding:16px 24px;border-top:1px solid #141414;margin-top:24px">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            <div style="width:6px;height:6px;border-radius:50%;background:#4ade80;box-shadow:0 0 6px #4ade80"></div>
            <span style="font-family:'DM Mono',monospace;font-size:10px;color:#444;letter-spacing:1px">LIVE</span>
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#2a2a2a;line-height:1.7">
            Polymarket CLOB API<br>Kalshi trade-api v2<br>Claude Sonnet (Anthropic)
        </div>
        <div style="margin-top:12px">
            <a href="https://github.com/harghan/liquidity-agent" target="_blank"
               style="font-family:'DM Mono',monospace;font-size:9px;color:#444;text-decoration:none;letter-spacing:1px;border:1px solid #1a1a1a;padding:4px 10px">GitHub ↗</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.page == "Live Analysis":
    page_live()
elif st.session_state.page == "Markets":
    page_markets()
elif st.session_state.page == "About":
    page_about()
elif st.session_state.page == "Methodology":
    page_methodology()
