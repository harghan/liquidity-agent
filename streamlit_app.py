"""
Liquidity Agent — cross-platform prediction-market liquidity intelligence.

A product-grade Streamlit front end over the same pipeline that powers the PDF
report: live orderbook collection, NLP cross-platform matching, five-tier
price-impact analysis, the Liquidity Quality Index, and an on-demand
Claude-authored research narrative.

    streamlit run streamlit_app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import config
from collectors import kalshi, polymarket
from core import matcher, price_impact, scorer
from run_agent import _key, build_analysis

# ---------------------------------------------------------------------------
# Page config + design system
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Liquidity Agent", page_icon="◆", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap');

#root > div, .main, .block-container {
    background: #0a0a0a !important;
    color: #ffffff !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    max-width: 1200px !important;
    padding: 0 2rem !important;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.stSidebar { background: #050505 !important; border-right: 1px solid #1a1a1a !important; }
h1, h2, h3 { font-family: 'Inter', sans-serif !important; font-weight: 500 !important; letter-spacing: -0.5px !important; }

[data-testid="metric-container"] {
    background: #111 !important; border: 1px solid #1e1e1e !important;
    border-radius: 0 !important; padding: 1.5rem !important;
}
[data-testid="metric-container"] label {
    font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important;
    color: #c8a951 !important; font-family: 'DM Mono', monospace !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important; font-size: 2rem !important;
    font-weight: 300 !important; color: #ffffff !important;
}

.stButton > button {
    background: transparent !important; border: 1px solid #c8a951 !important; color: #c8a951 !important;
    border-radius: 0 !important; font-family: 'DM Mono', monospace !important; font-size: 11px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important; padding: 0.75rem 2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { background: #c8a951 !important; color: #0a0a0a !important; }
.stButton > button[kind="primary"] { background: #c8a951 !important; color: #0a0a0a !important; font-weight: 500 !important; }

.stDataFrame { background: #111 !important; border: 1px solid #1e1e1e !important; }
iframe { background: #0a0a0a !important; }
.stProgress > div > div { background: #c8a951 !important; }
hr { border-color: #1e1e1e !important; }

.stRadio > label { color: #666 !important; font-size: 11px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; }
.stRadio [data-baseweb="radio"] { gap: 0.75rem !important; }
.stRadio div[role="radiogroup"] label { color: #aaa !important; font-family: 'DM Mono', monospace !important; font-size: 12px !important; letter-spacing: 1px !important; }

.stTextInput > div > div, .stSelectbox > div > div { background: #111 !important; border: 1px solid #1e1e1e !important; border-radius: 0 !important; color: #fff !important; }
.streamlit-expanderHeader { background: #111 !important; border: 1px solid #1e1e1e !important; color: #fff !important; border-radius: 0 !important; }
.streamlit-expanderContent { background: #0d0d0d !important; border: 1px solid #1e1e1e !important; }
.stSpinner > div { border-top-color: #c8a951 !important; }
[data-testid="stStatusWidget"], div[data-testid="stStatus"] { background: #111 !important; border: 1px solid #1e1e1e !important; border-radius: 0 !important; }

.gold-rule { height: 1px; background: #c8a951; margin: 2rem 0; opacity: 0.4; }
.section-label { font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: #c8a951; font-family: 'DM Mono', monospace; margin-bottom: 0.5rem; }
.hero-number { font-family: 'DM Mono', monospace; font-size: 4rem; font-weight: 300; line-height: 1; }
.market-card { background: #111; border: 1px solid #1e1e1e; padding: 1.25rem; margin-bottom: 0.5rem; }
.market-card:hover { border-color: #c8a951; }
.badge { font-size: 9px; letter-spacing: 1.5px; padding: 2px 8px; font-family: 'DM Mono', monospace; }
.badge-pres { background: #0d0d20; color: #60a5fa; }
.badge-fed { background: #0d2018; color: #4ade80; }
.badge-rec { background: #200d0d; color: #f87171; }
.badge-other { background: #1a160a; color: #c8a951; }
.editorial { font-size: 15px; line-height: 1.85; color: #cfcfcf; font-weight: 300; max-width: 720px; }
.callout { background: #111; border-left: 2px solid #c8a951; padding: 1rem 1.25rem; margin-bottom: 0.75rem; }
.callout .n { font-family: 'DM Mono', monospace; font-size: 1.4rem; color: #fff; font-weight: 300; }
.callout .d { font-size: 12px; color: #888; margin-top: 4px; }
.narrative-box { background: #0d0d0d; border: 1px solid #1e1e1e; padding: 1.75rem 2rem;
    font-family: 'DM Mono', monospace; font-size: 13px; line-height: 1.9; color: #d8d8d8; white-space: pre-wrap; }
.team-row { font-size: 14px; color: #ddd; padding: 6px 0; border-bottom: 1px solid #141414; font-weight: 300; }
.team-row b { color: #fff; font-weight: 500; }
.cite { font-size: 13px; color: #aaa; line-height: 1.7; margin-bottom: 10px; font-weight: 300; }
</style>
""", unsafe_allow_html=True)

DARK = "#0a0a0a"
GOLD = "#c8a951"
SIZE_LABELS = ["$500", "$2k", "$10k", "$50k", "$100k"]
GITHUB_URL = "https://github.com/"  # set to the repo URL when published


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


def esc(s) -> str:
    """Escape '$' so Streamlit's markdown/KaTeX never renders dollar amounts as
    LaTeX math. Applied to anything containing dollar figures before st.markdown."""
    return str(s).replace("$", "\\$")


# Styled container for the AI narrative.
NARRATIVE_BOX = (
    "<div style=\"font-family:'DM Mono',monospace;font-size:13px;line-height:1.9;color:#ccc;"
    "background:#0d0d0d;border:1px solid #1e1e1e;padding:1.5rem;border-left:3px solid #c8a951;\">"
    "{text}</div>"
)


def load_cached_analysis():
    p = config.OUTPUT_DIR / "analysis.json"
    if p.exists():
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def run_pipeline_live():
    """Run the full pipeline with on-screen progress; return the analysis dict."""
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
# Charts
# ---------------------------------------------------------------------------
def _dark_layout(fig, height=460, title=None):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=DARK, plot_bgcolor=DARK,
        font=dict(family="Inter, sans-serif", color="#cccccc", size=12),
        height=height, margin=dict(l=20, r=20, t=50 if title else 20, b=30),
        title=dict(text=title, font=dict(size=15, color="#ffffff")) if title else None,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(family="DM Mono, monospace", size=11)),
        hoverlabel=dict(font=dict(family="DM Mono, monospace")),
    )
    fig.update_xaxes(gridcolor="#1a1a1a", zeroline=False, showline=False)
    fig.update_yaxes(gridcolor="#1a1a1a", zeroline=False, showline=False)
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
        fig.add_vline(x=xi, line=dict(color="#555", width=1, dash="dot"))
        top = max(pm[xi], kx[xi])
        fig.add_annotation(x=xi, y=top, yshift=24, showarrow=False,
                           text=f"<b>{lab}</b><br>PM {pm[xi]:,.0f} bps<br>KX {kx[xi]:,.0f} bps",
                           font=dict(family="DM Mono, monospace", size=10, color="#fff"),
                           bgcolor="#111", bordercolor=GOLD, borderwidth=1, borderpad=5, align="left")
    fig.update_xaxes(tickmode="array", tickvals=x, ticktext=SIZE_LABELS)
    fig.update_yaxes(title_text="Mean price impact (bps)")
    return _dark_layout(fig, height=480, title="Price Impact Curves — Where the Orderbook Breaks")


def slippage_bar(a):
    pairs = [p for p in a.get("pairs", []) if p.get("avoidable_slippage_10k") is not None]
    pairs.sort(key=lambda p: p["avoidable_slippage_10k"])  # ascending → largest on top
    labels = [p["subject"][:24] for p in pairs]
    vals = [p["avoidable_slippage_10k"] for p in pairs]
    colors = ["#e0e0e0" if (p.get("cheaper_venue") == "Polymarket") else GOLD for p in pairs]
    fig = go.Figure(go.Bar(
        x=vals, y=labels, orientation="h", marker_color=colors,
        text=[f"${v:,.0f}" for v in vals], textposition="outside",
        textfont=dict(family="DM Mono, monospace", size=11, color="#bbb"),
        hovertemplate="%{y}: $%{x:,.0f}<extra></extra>",
    ))
    if vals:
        mean_v = sum(vals) / len(vals)
        fig.add_vline(x=mean_v, line=dict(color=GOLD, width=1.2, dash="dash"))
        fig.add_annotation(x=mean_v, y=len(labels) - 0.4, yshift=10, showarrow=False,
                           text=f"mean ${mean_v:,.0f}", font=dict(family="DM Mono, monospace", size=10, color=GOLD))
    fig.update_xaxes(title_text="Avoidable slippage on a $10,000 order (USD)")
    height = max(360, 36 * len(labels) + 90)
    return _dark_layout(fig, height=height, title="Avoidable Slippage by Market — $10,000 Notional")


# ---------------------------------------------------------------------------
# Narrative (streaming)
# ---------------------------------------------------------------------------
def narrative_payload(a):
    """Build the sanitized data payload for the narrative prompt: numerical data
    and human-readable market names only — no raw API identifiers or URLs."""
    def _clean_side(s):
        return {
            "mid": s.get("mid"),
            "spread_bps": s.get("spread_bps"),
            "lqi": s.get("lqi"),
            "grade": s.get("grade"),
            "impact_bps": s.get("impact_bps"),
        }

    clean_pairs = [{
        "market": p.get("subject"),          # human-readable name only
        "category": p.get("category"),
        "confidence": p.get("confidence"),
        "divergence_bps": p.get("divergence_bps"),
        "avoidable_slippage_10k": p.get("avoidable_slippage_10k"),
        "cheaper_venue": p.get("cheaper_venue"),
        "polymarket": _clean_side(p.get("polymarket", {})),
        "kalshi": _clean_side(p.get("kalshi", {})),
    } for p in a.get("pairs", [])]

    return {
        "platform_stats": a.get("platform_stats", {}),  # mean LQI, spreads, impact bps
        "cost_summary": a.get("cost_summary"),
        "lqi_gap_overall": a.get("lqi_gap_overall"),
        "universe": a.get("universe"),                  # match counts
        "pairs": clean_pairs,
    }


def stream_narrative(a):
    import anthropic
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    payload = narrative_payload(a)
    system = (
        "You are a senior market-structure and liquidity strategist at a quantitative trading "
        "firm. You write precise institutional research, cite exact figures, and never invent "
        "numbers. Write in plain prose ONLY. Do NOT use any Markdown syntax: no '#' headers, no "
        "'**' bold, no '###', no bullet characters. For each section, put an ALL-CAPS label on its "
        "own line, then a line break, then the paragraph beneath it."
    )
    user = (
        "Write a five-paragraph institutional research memo on cross-platform prediction-market "
        "liquidity (Polymarket vs Kalshi), grounded strictly in the JSON below. Use exactly these "
        "five sections, each introduced by its ALL-CAPS label on its own line followed by the "
        "paragraph: EXECUTIVE SUMMARY, KEY FINDINGS, ROOT CAUSE ANALYSIS, "
        "PLATFORM-SPECIFIC RECOMMENDATIONS, LIMITATIONS. Separate sections with a blank line. "
        "Name real matched markets and quote real figures (LQI, impact in bps, divergence, dollar "
        "slippage). Be dense and specific. Remember: plain prose, no Markdown symbols anywhere.\n\n"
        f"DATA:\n{json.dumps(payload, default=str)}"
    )
    with client.messages.stream(model=config.ANTHROPIC_MODEL, max_tokens=2200,
                                system=system, messages=[{"role": "user", "content": user}]) as stream:
        for text in stream.text_stream:
            yield text


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def hero(label, headline, subtitle):
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 style="font-size:2.4rem;margin:0.2rem 0 0.4rem 0">{headline}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#888;font-size:14px;font-weight:300">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)


def page_live():
    hero("Liquidity Agent", "Cross-Platform Prediction Market Intelligence",
         "Real-time orderbook analysis · Polymarket × Kalshi · 300 markets")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        run = st.button("Run Live Analysis", type="primary", use_container_width=True)
    if run:
        a = run_pipeline_live()
        if a:
            st.session_state["analysis"] = a
            st.session_state.pop("narrative", None)

    a = st.session_state.get("analysis")
    if not a:
        st.markdown('<div style="color:#666;font-size:13px;text-align:center;margin-top:2rem">'
                    'Press <span style="color:#c8a951">Run Live Analysis</span> to pull live orderbooks, '
                    'or load the most recent cached run from the sidebar.</div>', unsafe_allow_html=True)
        return

    cost = a.get("cost_summary", {})
    uni = a.get("universe", {})
    maxd = cost.get("max_divergence") or {}
    gap = a.get("lqi_gap_overall")
    pm_lqi = _g(a, "platform_stats", "Polymarket", "mean_lqi")
    kx_lqi = _g(a, "platform_stats", "Kalshi", "mean_lqi")

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Avoidable Slippage", f"${cost.get('total_avoidable_slippage_10k', 0):,.0f}",
              "per $10k notional", delta_color="off")
    k2.metric("Markets Analysed", f"{uni.get('compared_pairs', 0)}",
              f"from {uni.get('near_miss_rejections', 0):,} evaluated pairs", delta_color="off")
    lead = f"+{gap:.1f} pts" if (gap is not None and gap >= 0) else (f"{gap:.1f} pts" if gap is not None else "—")
    k3.metric("Polymarket LQI Lead", lead,
              f"{pm_lqi} vs {kx_lqi}" if pm_lqi is not None else "—", delta_color="off")
    k4.metric("Max Price Divergence", f"{maxd.get('bps', 0) or 0:,.0f} bps",
              (maxd.get("subject") or "")[:24], delta_color="off")

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
    st.plotly_chart(price_impact_curve(a), use_container_width=True, config={"displayModeBar": False})
    st.plotly_chart(slippage_bar(a), use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Autonomous Research Narrative</div>', unsafe_allow_html=True)
    if not config.ANTHROPIC_API_KEY:
        st.markdown('<div style="color:#888;font-size:13px">Set <span style="color:#c8a951">ANTHROPIC_API_KEY</span> '
                    'in <code>.env</code> to generate the AI research memo.</div>', unsafe_allow_html=True)
    else:
        if st.button("Generate Narrative"):
            try:
                placeholder = st.empty()
                acc = ""
                for chunk in stream_narrative(a):
                    acc += chunk
                    # Escape $ so amounts never render as LaTeX, stream into the box.
                    placeholder.markdown(NARRATIVE_BOX.format(text=esc(acc)), unsafe_allow_html=True)
                st.session_state["narrative"] = acc
            except Exception as exc:  # noqa: BLE001
                st.error(f"Narrative generation failed: {exc}")
        elif st.session_state.get("narrative"):
            st.markdown(NARRATIVE_BOX.format(text=esc(st.session_state["narrative"])),
                        unsafe_allow_html=True)


_BADGE = {
    "Presidential Election": ("badge-pres", "PRESIDENTIAL"),
    "Primary / Nomination": ("badge-pres", "PRIMARY"),
    "Fed / Rates": ("badge-fed", "FED RATES"),
    "Recession": ("badge-rec", "RECESSION"),
    "Crypto": ("badge-other", "CRYPTO"),
    "World Cup": ("badge-other", "WORLD CUP"),
    "Sports": ("badge-other", "SPORTS"),
}


def _cents(mid):
    return f"{(mid or 0) * 100:.2f}¢"


def _lqi_color(v):
    if v is None:
        return "#888"
    return "#4ade80" if v >= 75 else ("#facc15" if v >= 50 else "#f87171")


def market_card(p):
    pm, kx = p.get("polymarket", {}), p.get("kalshi", {})
    badge_cls, badge_txt = _BADGE.get(p.get("category", ""), ("badge-other", "MARKET"))
    pm_i10 = _g(pm, "impact_bps", "10000") or 0
    kx_i10 = _g(kx, "impact_bps", "10000") or 0
    pm_url = p.get("polymarket_url") or pm.get("url") or "#"
    kx_url = p.get("kalshi_url") or kx.get("url") or "#"
    route = p.get("cheaper_venue") or "—"
    route_disp = "POLYMARKET" if route == "Polymarket" else ("KALSHI" if route == "Kalshi" else "—")
    avoid = p.get("avoidable_slippage_10k") or 0
    div = p.get("divergence_bps") or 0
    pm_lqi, kx_lqi = pm.get("lqi"), kx.get("lqi")
    html = f"""
<div class="market-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">
    <div>
      <span class="badge {badge_cls}">{badge_txt}</span>
      <div style="font-size:16px;font-weight:500;color:#fff;margin-top:6px">{p.get('subject','')}</div>
      <div style="font-size:11px;color:#666;margin-top:2px">Match confidence: {p.get('confidence',0):.3f}</div>
    </div>
    <div style="text-align:right">
      <div style="font-family:'DM Mono',monospace;font-size:22px;color:#c8a951">${avoid:,.0f}</div>
      <div style="font-size:10px;color:#666;letter-spacing:1px">AVOIDABLE SLIPPAGE</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:12px">
    <div style="background:#0a0a0a;padding:12px;border-left:2px solid #e0e0e0">
      <div style="font-size:10px;letter-spacing:1px;color:#888;margin-bottom:4px">POLYMARKET</div>
      <div style="font-family:'DM Mono',monospace;font-size:18px;color:#fff">{_cents(pm.get('mid'))}</div>
      <div style="font-size:11px;color:{_lqi_color(pm_lqi)};margin-top:2px">{pm_i10:,.0f} bps · LQI {pm_lqi if pm_lqi is not None else '—'}</div>
      <a href="{pm_url}" target="_blank" style="display:inline-block;margin-top:8px;font-size:10px;letter-spacing:1px;color:#c8a951;text-decoration:none;border:1px solid #c8a951;padding:3px 10px">TRADE →</a>
    </div>
    <div style="background:#0a0a0a;padding:12px;border-left:2px solid #c8a951">
      <div style="font-size:10px;letter-spacing:1px;color:#888;margin-bottom:4px">KALSHI</div>
      <div style="font-family:'DM Mono',monospace;font-size:18px;color:#fff">{_cents(kx.get('mid'))}</div>
      <div style="font-size:11px;color:{_lqi_color(kx_lqi)};margin-top:2px">{kx_i10:,.0f} bps · LQI {kx_lqi if kx_lqi is not None else '—'}</div>
      <a href="{kx_url}" target="_blank" style="display:inline-block;margin-top:8px;font-size:10px;letter-spacing:1px;color:#666;text-decoration:none;border:1px solid #333;padding:3px 10px">TRADE →</a>
    </div>
  </div>
  <div style="display:flex;gap:1rem;font-size:11px;color:#666;flex-wrap:wrap">
    <span>$10k impact: <span style="color:#fff;font-family:'DM Mono',monospace">{pm_i10:,.0f} bps PM · {kx_i10:,.0f} bps KX</span></span>
    <span>·</span>
    <span>Divergence: <span style="color:#c8a951;font-family:'DM Mono',monospace">{div:,.0f} bps</span></span>
    <span>·</span>
    <span>Route: <span style="color:#4ade80;font-family:'DM Mono',monospace">{route_disp}</span></span>
  </div>
</div>
"""
    st.markdown(esc(html), unsafe_allow_html=True)


def page_markets():
    hero("Market Intelligence", "Matched Markets",
         "Identical outcomes, two venues — ranked by avoidable execution cost")
    a = st.session_state.get("analysis")
    if not a or not a.get("pairs"):
        st.markdown('<div style="color:#666;font-size:13px">Run an analysis on the Live Analysis page first.</div>',
                    unsafe_allow_html=True)
        return
    pairs = list(a["pairs"])
    f1, f2 = st.columns([1, 1])
    cat = f1.selectbox("Category", ["All", "PRES", "FED", "REC"])
    sort = f2.selectbox("Sort", ["By Slippage", "By LQI", "By Divergence"])
    cat_map = {"PRES": "Presidential Election", "FED": "Fed / Rates", "REC": "Recession"}
    if cat != "All":
        pairs = [p for p in pairs if p.get("category") == cat_map[cat]]
    if sort == "By Slippage":
        pairs.sort(key=lambda p: p.get("avoidable_slippage_10k") or 0, reverse=True)
    elif sort == "By LQI":
        pairs.sort(key=lambda p: _g(p, "polymarket", "lqi") or 0, reverse=True)
    else:
        pairs.sort(key=lambda p: p.get("divergence_bps") or 0, reverse=True)

    st.markdown(f'<div style="color:#666;font-size:11px;font-family:DM Mono,monospace;letter-spacing:1px;'
                f'margin-bottom:1rem">{len(pairs)} MATCHED PAIRS</div>', unsafe_allow_html=True)
    for p in pairs:
        market_card(p)


def page_about():
    hero("The Story", "Why We Built This", "")
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:1.6rem;color:#c8a951;font-weight:300;'
                'line-height:1.4;margin-bottom:1.5rem;max-width:760px">'
                '"Prediction markets look liquid until you actually try to trade size."</div>',
                unsafe_allow_html=True)
    st.markdown(esc(
        '<div class="editorial">During the 2026 FIFA World Cup, a group chat between friends — '
        'Harsha, Aadish, Sohan, and Nitin — kept asking the same question: why did every prediction '
        'market parlay feel like it was bleeding money before the match even resolved?<br><br>'
        'The obvious answer was bad luck. The real answer was something more systematic: execution '
        'friction that quoted spreads completely mask. A market showing a 0.65¢ YES ask and a tight '
        '10 basis point spread looks liquid. But walk $10,000 through that same orderbook and Kalshi\'s '
        'execution cost reaches 257 basis points — a 1,222% cost premium over Polymarket for the '
        'identical outcome contract.<br><br>'
        'This is not a retail problem. It\'s an infrastructure problem. And nobody had measured it '
        'systematically across platforms until now.</div>'), unsafe_allow_html=True)

    st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">What We Built</div>', unsafe_allow_html=True)
    st.markdown(esc(
        '<div class="editorial">Liquidity Agent is an autonomous pipeline. It pulls ~300 live markets '
        'from each of Polymarket and Kalshi, matches economically identical contracts across venues with '
        'an NLP hybrid matcher, walks every orderbook at five notional sizes ($500 → $100k) to measure '
        'real volume-weighted price impact, scores a composite Liquidity Quality Index, and commissions '
        'Claude to write the research narrative. Output is a nine-page institutional PDF and this live '
        'dashboard.</div>'), unsafe_allow_html=True)

    st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">The Findings</div>', unsafe_allow_html=True)
    a = st.session_state.get("analysis") or {}
    cost = a.get("cost_summary", {})
    uni = a.get("universe", {})
    total = cost.get("total_avoidable_slippage_10k", 52139)
    compared = uni.get("compared_pairs", 15)
    maxbps = (cost.get("max_divergence") or {}).get("bps", 2545)
    rej = uni.get("near_miss_rejections", 2453)
    for n, d in [
        (f"${total:,.0f}", f"avoidable slippage across {compared} matched markets at $10k notional"),
        (f"{maxbps:,.0f} bps", "maximum cross-platform price divergence on Fed rate markets"),
        (f"{rej:,}", "near-miss pairs rejected — zero false positives in the final dataset"),
    ]:
        st.markdown(esc(f'<div class="callout"><span class="n">{n}</span><div class="d">{d}</div></div>'),
                    unsafe_allow_html=True)

    st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">The Team</div>', unsafe_allow_html=True)
    for line in [
        "<b>Harsha Ghandikota</b> — Research concept, system design, Duke University MEM 2026",
        "<b>Aadish Sanghvi</b> — Critical review and commentary",
        "<b>Sohan Kumar Rustumpet</b> — Critical review and commentary",
        "<b>Nitin Kumar Rustumpet</b> — Critical review and commentary",
        "<b>Claude Sonnet (Anthropic)</b> — Autonomous analysis and report generation",
    ]:
        st.markdown(f'<div class="team-row">{line}</div>', unsafe_allow_html=True)


def page_methodology():
    hero("Methodology", "How It Works", "Technical documentation")

    def section(label, body):
        st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)
        st.markdown(esc(f'<div class="editorial">{body}</div>'), unsafe_allow_html=True)
        st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)

    section("Orderbook-Walking VWAP",
            "For each market we take a live orderbook snapshot and simulate a market buy of the YES "
            "outcome, walking the ask side level by level until the target notional is filled. The "
            "volume-weighted average execution price (VWAP) minus the displayed mid, in basis points, "
            "is the realized price impact. Unlike the quoted bid-ask spread — which describes only the "
            "top of book — VWAP-at-size captures the full shape of available liquidity. We measure five "
            "tiers: $500, $2,000, $10,000, $50,000 and $100,000, spanning retail through fund scale.")
    section("Market Matching Algorithm",
            "Markets are matched with a category gate followed by a confidence score blending rapidfuzz "
            "token-set similarity of the full question with the similarity of extracted entity keywords "
            "(candidate name, rate threshold, asset, team). Semantic guards reject opposite directions, "
            "mismatched numeric thresholds, and different dates. Thresholds are category-aware — 0.75 for "
            "person/candidate markets, 0.65 otherwise. Every same-category near-miss is logged with its "
            "score and rejection reason, evidence the matched set is algorithmic, not cherry-picked.")
    section("Liquidity Quality Index",
            "The LQI is a composite 0–100 score combining three components: bid-ask spread (30%), depth "
            "via $2k impact (40%), and $10k impact (30%) — mid-book depth weighted highest per "
            "institutional convention. Component scores ramp linearly to configured caps and are blended "
            "into a single grade per market per platform.")
    section("Limitations",
            "Phantom liquidity: displayed limit orders may be cancelled on approach, so all figures "
            "represent displayed depth, not guaranteed execution; this affects both platforms equally and "
            "does not bias the cross-platform comparison. The analysis is a single snapshot and can shift "
            "within hours of a news catalyst. The 40/30/30 LQI weighting reflects practitioner judgment, "
            "not a universal standard. Kalshi sports contracts are geofenced in certain states.")

    st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Academic Grounding</div>', unsafe_allow_html=True)
    for cite in [
        "<b>Kyle, A. S. (1985).</b> Continuous Auctions and Insider Trading. <i>Econometrica, 53(6)</i>, "
        "1315–1335. — the linear price-impact coefficient (λ) relating order flow to price movement.",
        "<b>Amihud, Y. (2002).</b> Illiquidity and Stock Returns. <i>Journal of Financial Markets, 5(1)</i>, "
        "31–56. — precedent for a volume-normalized illiquidity ratio.",
        "<b>Roll, R. (1984).</b> A Simple Implicit Measure of the Effective Bid-Ask Spread. <i>Journal of "
        "Finance, 39(4)</i>, 1127–1139. — prior art for inferring effective transaction cost.",
    ]:
        st.markdown(f'<div class="cite">{cite}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="margin-top:1.5rem"><a href="{GITHUB_URL}" target="_blank" '
                'style="color:#c8a951;font-family:DM Mono,monospace;font-size:12px;letter-spacing:1px;'
                'text-decoration:none;border:1px solid #c8a951;padding:6px 16px">VIEW SOURCE ON GITHUB →</a></div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
# Load cached analysis once so pages have data before the first live run.
if "analysis" not in st.session_state:
    cached = load_cached_analysis()
    if cached:
        st.session_state["analysis"] = cached

with st.sidebar:
    st.markdown('<div style="font-family:DM Mono,monospace;color:#c8a951;font-size:13px;letter-spacing:3px;'
                'padding:1rem 0 1.5rem 0">◆ LIQUIDITY<br>&nbsp;&nbsp;AGENT</div>', unsafe_allow_html=True)
    page = st.radio("Navigation", ["Live Analysis", "Markets", "About", "Methodology"],
                    label_visibility="collapsed")
    st.markdown('<div style="position:fixed;bottom:1.5rem;font-size:10px;color:#444;'
                'font-family:DM Mono,monospace;letter-spacing:1px">POLYMARKET × KALSHI</div>',
                unsafe_allow_html=True)

if page == "Live Analysis":
    page_live()
elif page == "Markets":
    page_markets()
elif page == "About":
    page_about()
elif page == "Methodology":
    page_methodology()
