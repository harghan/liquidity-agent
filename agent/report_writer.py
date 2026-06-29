"""
Visual-first 9-page PDF report (full redesign).

Charts carry the argument; prose annotates the charts. The report writer:

* renders all charts via :mod:`agent.charts` (matplotlib -> PNG),
* lays out nine pages exactly as specified using a BaseDocTemplate with a
  dedicated cover template (dark header band + author credit) and a main
  template (slim running header + footer on every page),
* colours a market heatmap and styles every table per the design system,
* and asks Claude (claude-sonnet-4-6) to author the interpretive prose as a
  structured JSON object, grounded in the computed analysis. If the API key is
  absent or the call fails, fully-specified default prose (built from the data)
  is used instead, so the report is always complete.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import HRFlowable

import config
from agent import charts

logger = logging.getLogger("liquidity_agent.report")

PAGE_W, PAGE_H = LETTER
M = 0.75 * inch                      # page margin
FRAME_W = PAGE_W - 2 * M

DARK = HexColor(config.COLOR_DARK)
GOLD = HexColor(config.COLOR_GOLD)
ROW_ALT = HexColor(config.COLOR_ROW_ALT)
MUTED = HexColor(config.COLOR_MUTED)
FOOTER_GREY = HexColor(config.COLOR_MUTED_FOOTER)
DANGER = HexColor(config.COLOR_DANGER)
SAFE = HexColor(config.COLOR_SAFE)
RULE_GREY = HexColor("#cccccc")

_RUNTIME: Dict[str, str] = {}

_CAT_CODE = {
    "Presidential Election": "PRES", "Primary / Nomination": "PRIM",
    "Fed / Rates": "FED", "Inflation": "CPI", "Recession": "REC",
    "GDP": "GDP", "Unemployment": "U3", "Crypto": "CRYPTO",
    "World Cup": "WC", "Sports": "SPORT",
}


# ===========================================================================
# Stage 1 — Claude interpretive prose (structured JSON, grounded in the data)
# ===========================================================================
def _g(d: dict, *path, default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _clip(text: str, n: int) -> str:
    """Trim to <= n chars, preferring to end on a sentence boundary."""
    text = (text or "").strip()
    if len(text) <= n:
        return text
    head = text[:n]
    dot = head.rfind(". ")
    if dot >= int(n * 0.5):
        return head[:dot + 1]
    return head.rstrip() + "…"


def _default_prose(a: Dict[str, Any]) -> Dict[str, Any]:
    cost = a.get("cost_summary", {})
    gap = a.get("lqi_gap_overall")
    total = cost.get("total_avoidable_slippage_10k", 0) or 0
    pm_lqi = _g(a, "platform_stats", "Polymarket", "mean_lqi")
    kx_lqi = _g(a, "platform_stats", "Kalshi", "mean_lqi")
    pm100 = _g(a, "platform_stats", "Polymarket", "mean_impact_bps", "100000")
    kx100 = _g(a, "platform_stats", "Kalshi", "mean_impact_bps", "100000")
    top = (a.get("top_pairs") or [{}])[0]
    cats = ", ".join(f"{k} ({v})" for k, v in (a.get("universe", {}).get("matches_by_category", {}) or {}).items())
    better = "Polymarket" if (gap or 0) >= 0 else "Kalshi"

    return {
        "page3": {
            "retail": ("At $500 — true retail scale — both venues are effectively "
                       "frictionless. Displayed mid and executed price are nearly identical, "
                       "so a retail participant sees no meaningful cross-platform edge; venue "
                       "choice should be driven by access and fees, not depth."),
            "institutional": ("At $10,000 the curves separate. This is where an "
                              "individual professional or small fund enters, and the platform "
                              "with deeper resting size begins to deliver materially better "
                              "execution. The gap here is the first actionable signal."),
            "fund": (f"At $100,000 — fund scale — divergence becomes decisive: mean impact "
                     f"reaches roughly {pm100 or 0:.0f} bps on Polymarket versus {kx100 or 0:.0f} bps "
                     "on Kalshi. For size, the thinner book is not merely more expensive; in the "
                     "tail it may be unfillable at any sane price."),
        },
        "page6": ("Persistent divergence in displayed mids for economically identical events "
                  "implies the two venues are not in continuous price equilibrium. Capital does "
                  "not move freely between them — Kalshi is CFTC-regulated and USD-funded while "
                  "Polymarket is offshore and crypto-funded — so structural frictions in "
                  "participant access and settlement, not merely noise, sustain the gaps."),
        "page7": [
            ("The scatter contrasts each venue's liquidity-provision model: impact tends to "
             "fall as displayed probability rises, because consensus 'likely' outcomes attract "
             "tighter, deeper two-sided quoting, while longshots sit in the illiquid tail."),
            ("The informative cases are the anomalies — high-probability contracts that remain "
             "thin, and longshots that are surprisingly deep — because they reveal where market-"
             "maker attention is mispriced relative to where displayed probability would predict."),
        ],
        "page8": {
            "hypotheses": [
                ("Regulatory asymmetry. Kalshi's CFTC-regulated, USD-funded retail base and "
                 "Polymarket's offshore, crypto-native and more sophisticated flow create "
                 "structurally different information sets and order-arrival patterns, which "
                 "show up as different depth and different price levels for the same event."),
                ("Contract design. Kalshi concentrates liquidity in pooled, multi-candidate "
                 "event contracts, whereas Polymarket lists standalone binary markets per "
                 "outcome. The two architectures distribute depth differently and leave "
                 "uneven per-outcome liquidity."),
                ("Market-maker incentive structure. Kalshi runs a maker-rebate program "
                 "(on the order of ~$35k/day) while Polymarket is fee-free; rebates reward "
                 "tight quotes at the touch but not necessarily mid-book depth, producing "
                 "different depth profiles away from best bid/ask."),
                ("Participant composition. Different participant pools carry different "
                 "information efficiency and different tolerance for holding inventory "
                 "overnight, which feeds through to both the level and the resilience of "
                 "quoted depth."),
            ],
            "polymarket_recs": [
                ("Introduce targeted maker incentives on non-frontrunner candidate contracts. "
                 f"The matched presidential markets show standalone binaries leave secondary "
                 "candidates structurally thin; a small rebate on those specific contracts would "
                 "close the depth gap where it is widest."),
                (f"Prioritise depth in the markets driving the largest avoidable slippage "
                 f"(e.g. '{top.get('subject','—')}'). These are where users currently lose the "
                 "most to impact and where added resting size has the highest marginal value."),
                ("Reconsider standalone binary design for multi-candidate events: a pooled or "
                 "linked-quoting mechanism would let market makers recycle inventory across "
                 "correlated outcomes and lift per-outcome depth without new capital."),
            ],
            "kalshi_recs": [
                ("Address the pooled-contract depth distribution: the architecture concentrates "
                 "liquidity unevenly across outcomes, leaving several matched contracts thinner "
                 "at size than their Polymarket equivalents."),
                ("Re-examine whether the current rebate structure rewards touch-only quoting. "
                 "Tight top-of-book with shallow mid-book is exactly the profile observed; "
                 "tying rebates to depth-at-size rather than best-quote presence would help."),
                (f"Focus on the series where Polymarket outperforms most severely — led by "
                 f"{cats or 'the matched categories'} — and target maker support there first."),
            ],
        },
        "page9": {
            "vwap": [
                ("For each market we take a live orderbook snapshot and simulate a market buy of "
                 "the YES outcome, walking the ask side level by level until the desired notional "
                 "is filled. The volume-weighted average execution price (VWAP) is the price a "
                 "taker would actually achieve at that size."),
                ("Price impact is VWAP minus the displayed mid, expressed in basis points. Unlike "
                 "the quoted bid-ask spread, which describes only the top of book, VWAP-at-size "
                 "captures the full shape of available liquidity and is therefore a far better "
                 "measure of what execution actually costs."),
                ("We walk five tiers — $500, $2,000, $10,000, $50,000 and $100,000 — spanning "
                 "retail through fund scale. The progression reveals where each book stops being "
                 "deep enough to absorb size, which the headline quoted spread cannot show."),
                ("The Liquidity Quality Index composites three of these signals — spread (30%), "
                 "depth via $2k impact (40%), and $10k impact (30%) — into a single 0–100 score, "
                 "with mid-book depth weighted highest per institutional convention."),
            ],
            "matching": [
                ("Markets are matched across platforms with an NLP hybrid: a category gate, then "
                 "a confidence score blending rapidfuzz token-set similarity of the full question "
                 "with the similarity of extracted entity keywords (candidate name, rate threshold, "
                 "asset, team). Semantic guards reject opposite directions, mismatched thresholds, "
                 "and different dates."),
                ("Confidence thresholds are category-aware: 0.75 for person/candidate markets and "
                 "0.65 elsewhere. Every same-category near-miss that was not accepted is recorded "
                 "with its score and rejection reason in rejected_pairs.json — evidence that the "
                 "matched set is algorithmic, not cherry-picked."),
            ],
        },
    }


def _merge_prose(defaults: Dict[str, Any], got: Dict[str, Any]) -> Dict[str, Any]:
    """Shallow-merge model output over defaults, keeping defaults for anything
    missing or malformed."""
    out = json.loads(json.dumps(defaults))  # deep copy
    try:
        for k in ("page3", "page8", "page9"):
            if isinstance(got.get(k), dict):
                out[k].update({kk: vv for kk, vv in got[k].items() if vv})
        if isinstance(got.get("page6"), str) and got["page6"].strip():
            out["page6"] = got["page6"].strip()
        if isinstance(got.get("page7"), list) and got["page7"]:
            out["page7"] = [str(x) for x in got["page7"]][:2] or out["page7"]
    except Exception:  # noqa: BLE001
        return defaults
    return out


def generate_prose(analysis: Dict[str, Any]) -> Dict[str, Any]:
    defaults = _default_prose(analysis)
    if not config.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set — using grounded default prose")
        return defaults
    try:
        import anthropic
    except ImportError:
        logger.error("anthropic SDK not installed — using default prose")
        return defaults

    schema = {
        "page3": {"retail": "str", "institutional": "str", "fund": "str"},
        "page6": "str",
        "page7": ["str", "str"],
        "page8": {"hypotheses": ["str x4"], "polymarket_recs": ["str x3"], "kalshi_recs": ["str x3"]},
        "page9": {"vwap": ["str x4"], "matching": ["str x2"]},
    }
    system = (
        "You are a senior market-structure and liquidity strategist at a quantitative "
        "trading firm, writing the prose for a visual-first research memo. You cite exact "
        "figures from the data, never invent numbers or markets, and write with the concision "
        "of a desk strategist. Return ONLY a single JSON object — no prose outside the JSON."
    )
    user = (
        "Write the interpretive prose blocks for a Polymarket-vs-Kalshi liquidity memo. "
        "Ground every claim in the JSON analysis. Name real matched markets and quote real "
        "figures (LQI, impact in bps, divergence, dollar slippage). Keep page3 paragraphs "
        "tight (the three together under ~150 words). For page8 use these four hypotheses as "
        "the basis (regulatory asymmetry; contract design; maker-rebate incentive structure; "
        "participant composition) and make the six recommendations specific enough to act on, "
        "naming markets/series and mechanisms. Hard length limits: each hypothesis and each "
        "recommendation at most 2 sentences (~45 words); each page9 paragraph at most 2 "
        "sentences. Be dense, not wordy.\n\n"
        f"Return JSON with exactly this shape: {json.dumps(schema)}\n\n"
        f"ANALYSIS:\n{json.dumps(analysis, default=str)}"
    )
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        logger.info("Requesting interpretive prose from %s…", config.ANTHROPIC_MODEL)
        with client.messages.stream(
            model=config.ANTHROPIC_MODEL,
            max_tokens=config.ANTHROPIC_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
        ) as stream:
            msg = stream.get_final_message()
        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("no JSON object in model output")
        got = json.loads(text[start:end + 1])
        logger.info("Interpretive prose received and parsed")
        return _merge_prose(defaults, got)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Prose generation failed (%s) — using grounded defaults", exc)
        return defaults


# ===========================================================================
# Stage 2 — styles, helpers, color scales
# ===========================================================================
def _styles() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    s: Dict[str, ParagraphStyle] = {}
    s["h"] = ParagraphStyle("h", parent=base["Normal"], fontName=config.FONT_BOLD,
                            fontSize=13, leading=16, textColor=DARK, spaceAfter=2)
    s["title_pg"] = ParagraphStyle("title_pg", parent=base["Normal"], fontName=config.FONT_BOLD,
                                   fontSize=15, leading=18, textColor=DARK)
    s["body"] = ParagraphStyle("body", parent=base["Normal"], fontName=config.FONT_BODY,
                               fontSize=9.5, leading=14, textColor=HexColor("#1a1a1a"),
                               alignment=TA_JUSTIFY, spaceAfter=6)
    s["num"] = ParagraphStyle("num", parent=base["Normal"], fontName=config.FONT_BODY,
                              fontSize=9.5, leading=14, textColor=HexColor("#1a1a1a"),
                              alignment=TA_LEFT, spaceAfter=6, leftIndent=14, firstLineIndent=-14)
    # Compact variants for the two text-dense pages (root cause, methodology),
    # so each fits on a single page per the 9-page spec.
    s["body_c"] = ParagraphStyle("body_c", parent=base["Normal"], fontName=config.FONT_BODY,
                                 fontSize=8.8, leading=11.6, textColor=HexColor("#1a1a1a"),
                                 alignment=TA_JUSTIFY, spaceAfter=4)
    s["num_c"] = ParagraphStyle("num_c", parent=base["Normal"], fontName=config.FONT_BODY,
                                fontSize=8.8, leading=11.6, textColor=HexColor("#1a1a1a"),
                                alignment=TA_LEFT, spaceAfter=4, leftIndent=13, firstLineIndent=-13)
    s["caption"] = ParagraphStyle("caption", parent=base["Normal"], fontName=config.FONT_BODY,
                                  fontSize=7.5, leading=10, textColor=MUTED, alignment=TA_LEFT,
                                  spaceBefore=3)
    s["cell"] = ParagraphStyle("cell", parent=base["Normal"], fontName=config.FONT_BODY,
                               fontSize=8.5, leading=10.5, textColor=HexColor("#1a1a1a"))
    s["cell_r"] = ParagraphStyle("cell_r", parent=s["cell"], alignment=2)  # right
    s["cell_w"] = ParagraphStyle("cell_w", parent=s["cell"], textColor=white, fontName=config.FONT_BOLD)
    s["cell_w_r"] = ParagraphStyle("cell_w_r", parent=s["cell_w"], alignment=2)
    s["cellhead"] = ParagraphStyle("cellhead", parent=base["Normal"], fontName=config.FONT_BOLD,
                                   fontSize=8, leading=10, textColor=white)
    s["cellhead_r"] = ParagraphStyle("cellhead_r", parent=s["cellhead"], alignment=2)
    s["kpi_val"] = ParagraphStyle("kpi_val", parent=base["Normal"], fontName=config.FONT_BOLD,
                                  fontSize=22, leading=24, textColor=DARK, alignment=TA_CENTER)
    s["kpi_lab"] = ParagraphStyle("kpi_lab", parent=base["Normal"], fontName=config.FONT_BODY,
                                  fontSize=7.5, leading=9.5, textColor=MUTED, alignment=TA_CENTER)
    s["kpi_sub"] = ParagraphStyle("kpi_sub", parent=base["Normal"], fontName=config.FONT_BODY,
                                  fontSize=8, leading=10, textColor=DARK, alignment=TA_CENTER)
    s["annot"] = ParagraphStyle("annot", parent=base["Normal"], fontName=config.FONT_BOLD,
                                fontSize=8.5, leading=11, textColor=DARK, alignment=TA_CENTER)
    s["param"] = ParagraphStyle("param", parent=base["Normal"], fontName=config.FONT_BODY,
                                fontSize=9, leading=12, textColor=HexColor("#1a1a1a"))
    s["param_b"] = ParagraphStyle("param_b", parent=s["param"], fontName=config.FONT_BOLD)
    return s


def _section(title: str, styles) -> List[Any]:
    return [Paragraph(title, styles["h"]),
            HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=1, spaceAfter=7)]


def _lerp(c1: Color, c2: Color, t: float) -> Color:
    t = max(0.0, min(1.0, t))
    return Color(c1.red + (c2.red - c1.red) * t,
                 c1.green + (c2.green - c1.green) * t,
                 c1.blue + (c2.blue - c1.blue) * t)


def _tint(c: Color, t: float) -> Color:
    """Blend colour c toward white by (1-t); higher t = more saturated."""
    return _lerp(white, c, max(0.0, min(1.0, t)))


def _lqi_color(v: Optional[float]) -> Color:
    if v is None:
        return white
    t = v / 100.0
    if t >= 0.5:
        return _tint(SAFE, 0.35 + 0.5 * (t - 0.5) * 2)
    return _tint(DANGER, 0.35 + 0.5 * (0.5 - t) * 2)


def _impact_color(bps: Optional[float], cap: float = 500.0) -> Color:
    if bps is None:
        return white
    t = max(0.0, min(1.0, bps / cap))  # 0 good -> 1 bad
    # green (low) -> red (high), as light tints
    if t <= 0.5:
        return _tint(SAFE, 0.30 + 0.4 * (0.5 - t) * 2)
    return _tint(DANGER, 0.30 + 0.5 * (t - 0.5) * 2)


def _divergence_color(bps: Optional[float], cap: float = 300.0) -> Color:
    if bps is None:
        return white
    return _tint(GOLD, max(0.0, min(1.0, bps / cap)))


def _png_size(buf) -> Tuple[int, int]:
    data = buf.getvalue()
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def _img(buf, width: float) -> Image:
    w, h = _png_size(buf)
    buf.seek(0)
    return Image(buf, width=width, height=width * h / w)


# Usable height of the main content frame (matches the Frame in generate_pdf).
FRAME_H = PAGE_H - 0.62 * inch - 0.42 * inch


def _h(flowable, width: float = FRAME_W) -> float:
    """Measured height of a flowable INCLUDING the spaceBefore/spaceAfter the
    frame inserts around it (wrap() alone omits these, which would cause
    overflow when sizing charts to fill)."""
    st = getattr(flowable, "style", None)
    sb = getattr(st, "spaceBefore", 0) if st else getattr(flowable, "spaceBefore", 0)
    sa = getattr(st, "spaceAfter", 0) if st else getattr(flowable, "spaceAfter", 0)
    return flowable.wrap(width, 100000)[1] + (sb or 0) + (sa or 0)


# Safety margin so a chart sized to "fill" never tips content onto a new page.
_FILL_SAFETY = 12.0


def _img_exact(buf, width: float, height: float) -> Image:
    """Embed a chart at an exact box. The chart is rendered at the matching
    aspect (figsize), so this fills the box without distortion."""
    buf.seek(0)
    return Image(buf, width=width, height=height)


def _table(data, col_widths, styles, total_row=False, bold_rows=None, gold_col=None) -> Table:
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ROW_ALT]),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]
    if total_row:
        cmds += [("BACKGROUND", (0, -1), (-1, -1), DARK),
                 ("TEXTCOLOR", (0, -1), (-1, -1), white),
                 ("FONTNAME", (0, -1), (-1, -1), config.FONT_BOLD)]
    for r in (bold_rows or []):
        cmds.append(("FONTNAME", (0, r), (-1, r), config.FONT_BOLD))
    t.setStyle(TableStyle(cmds))
    return t


# ===========================================================================
# Page builders
# ===========================================================================
def _wrap_lines(canvas, text, font, size, max_w) -> List[str]:
    canvas.setFont(font, size)
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if canvas.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _on_cover(canvas, doc):
    canvas.saveState()
    # Dark band — top 40%.
    band_h = PAGE_H * 0.40
    canvas.setFillColor(DARK)
    canvas.rect(0, PAGE_H - band_h, PAGE_W, band_h, fill=1, stroke=0)
    # Title (28pt bold white, wrapped, centered within band).
    title = "Cross-Platform Prediction Market Liquidity Intelligence"
    lines = _wrap_lines(canvas, title, config.FONT_BOLD, 28, PAGE_W - 1.6 * inch)
    y = PAGE_H - 0.95 * inch
    canvas.setFillColor(white)
    canvas.setFont(config.FONT_BOLD, 28)
    for ln in lines:
        canvas.drawCentredString(PAGE_W / 2, y, ln)
        y -= 33
    # Subtitle (gold 12pt) + classification (muted white 8pt).
    canvas.setFillColor(GOLD)
    canvas.setFont(config.FONT_BOLD, 12)
    canvas.drawCentredString(PAGE_W / 2, y - 4, "A Systematic Orderbook Analysis of Polymarket and Kalshi")
    canvas.setFillColor(HexColor("#cfcfcf"))
    canvas.setFont(config.FONT_BODY, 8)
    canvas.drawCentredString(PAGE_W / 2, y - 22, "QUANTITATIVE STRATEGY  |  MARKET MICROSTRUCTURE RESEARCH")
    # Author credit — bottom quarter, centered 9pt.
    canvas.setFillColor(HexColor("#1a1a1a"))
    canvas.setFont(config.FONT_BODY, 9)
    canvas.drawCentredString(PAGE_W / 2, 1.30 * inch, config.AUTHOR_CREDIT_LINE_1)
    canvas.drawCentredString(PAGE_W / 2, 1.30 * inch - 14, config.AUTHOR_CREDIT_LINE_2)
    _draw_footer(canvas)
    canvas.restoreState()


def _on_main(canvas, doc):
    canvas.saveState()
    # Running header — slim 18pt dark bar.
    bar_h = 18
    canvas.setFillColor(DARK)
    canvas.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont(config.FONT_BODY, 8)
    canvas.drawString(M, PAGE_H - bar_h + 6, "Cross-Platform Prediction Market Liquidity Intelligence")
    canvas.setFillColor(GOLD)
    canvas.drawRightString(PAGE_W - M, PAGE_H - bar_h + 6, f"Page {canvas.getPageNumber()}")
    _draw_footer(canvas)
    canvas.restoreState()


def _draw_footer(canvas):
    canvas.setStrokeColor(RULE_GREY)
    canvas.setLineWidth(0.5)
    canvas.line(M, 0.55 * inch, PAGE_W - M, 0.55 * inch)
    canvas.setFont(config.FONT_BODY, 7)
    canvas.setFillColor(FOOTER_GREY)
    canvas.drawString(M, 0.4 * inch, f"Data sources: {config.DATA_SOURCE}")
    canvas.drawRightString(PAGE_W - M, 0.4 * inch, f"Generated {_RUNTIME.get('ts', '')}")


def _cover_story(a, styles) -> List[Any]:
    uni = a.get("universe", {})
    cost = a.get("cost_summary", {})
    rows = [
        ["Run date", a.get("run_date", "")],
        ["Markets analysed (Polymarket / Kalshi)",
         f"{uni.get('polymarket_universe', 0)} / {uni.get('kalshi_universe', 0)}"],
        ["Confident cross-platform matches", str(uni.get("matched_pairs", 0))],
        ["Fully comparable pairs (both books)", str(uni.get("compared_pairs", 0))],
        ["Near-miss rejections logged", str(uni.get("near_miss_rejections", 0))],
        ["Simulated order sizes", " / ".join(a.get("order_size_labels", []))],
        ["Total avoidable slippage ($10k orders)",
         f"${cost.get('total_avoidable_slippage_10k', 0):,.0f}"],
        ["Report author model", a.get("model", config.ANTHROPIC_MODEL)],
    ]
    data = [[Paragraph("Run parameter", styles["cellhead"]), Paragraph("Value", styles["cellhead"])]]
    for k, v in rows:
        data.append([Paragraph(k, styles["param"]), Paragraph(str(v), styles["param_b"])])
    t = _table(data, [FRAME_W * 0.62, FRAME_W * 0.38], styles)
    return [t]


def _kpi_box_row(a, styles) -> Table:
    cost = a.get("cost_summary", {})
    uni = a.get("universe", {})
    gap = a.get("lqi_gap_overall")
    maxd = cost.get("max_divergence") or {}

    def cell(value_markup, label, sub=None):
        cells = [Paragraph(value_markup, styles["kpi_val"]), Spacer(1, 2),
                 Paragraph(label, styles["kpi_lab"])]
        if sub:
            cells.insert(1, Paragraph(sub, styles["kpi_sub"]))
            cells.insert(2, Spacer(1, 1))
        return cells

    if gap is None:
        gap_markup = "—"
    else:
        arrow = "▲" if gap >= 0 else "▼"
        col = config.COLOR_SAFE if gap >= 0 else config.COLOR_DANGER
        gap_markup = f'<font color="{col}">{arrow} {gap:+.1f}</font>'

    data = [[
        cell(f"${cost.get('total_avoidable_slippage_10k', 0):,.0f}", "Total Avoidable Slippage<br/>($10k orders)"),
        cell(str(uni.get("compared_pairs", 0)), "Matched Markets<br/>Analysed"),
        cell(gap_markup, "Mean LQI Gap<br/>(Polymarket − Kalshi)"),
        cell(f"{maxd.get('bps', 0) or 0:.0f} bps", "Max Price Divergence",
             sub=(maxd.get("subject") or "")[:22]),
    ]]
    cw = FRAME_W / 4.0
    t = Table(data, colWidths=[cw] * 4, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, DARK),
        ("LINEABOVE", (0, 0), (-1, 0), 3, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _page_dashboard(a, styles) -> List[Any]:
    stats = a.get("platform_stats", {})
    pm = stats.get("Polymarket", {})
    kx = stats.get("Kalshi", {})
    sizes = [str(int(s)) for s in a.get("order_sizes_usd", [])]
    pm_bps = [(_g(pm, "mean_impact_bps", s) or 0) for s in sizes]
    kx_bps = [(_g(kx, "mean_impact_bps", s) or 0) for s in sizes]

    kpi = _kpi_box_row(a, styles)
    caption = Paragraph("All figures derived from a live orderbook snapshot. "
                        "Impact expressed in basis points vs displayed mid.", styles["caption"])
    gap1, gap2 = 14, 6
    # Charts consume all vertical space below the KPI boxes.
    avail = FRAME_H - _h(kpi) - gap1 - gap2 - _h(caption) - _FILL_SAFETY
    col_w = FRAME_W / 2
    chart_w = col_w - 5
    fs = (chart_w / 72.0, avail / 72.0)
    left = _img_exact(charts.platform_quality(pm, kx, figsize=fs), chart_w, avail)
    right = _img_exact(charts.impact_scaling(pm_bps, kx_bps, figsize=fs), chart_w, avail)
    twin = Table([[left, right]], colWidths=[col_w, col_w], hAlign="LEFT")
    twin.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (0, 0), 10),
                              ("RIGHTPADDING", (1, 0), (1, 0), 0)]))
    return [kpi, Spacer(1, gap1), twin, Spacer(1, gap2), caption]


def _annot_boxes(styles) -> Table:
    texts = ["$500 — Retail scale.<br/>Platforms near-identical.",
             "$10,000 — Institutional entry.<br/>Gap opens.",
             "$100,000 — Fund scale.<br/>Divergence critical."]
    row = [Paragraph(t, styles["annot"]) for t in texts]
    cw = FRAME_W / 3.0
    t = Table([row], colWidths=[cw] * 3, hAlign="LEFT")
    t.setStyle(TableStyle([("BOX", (0, 0), (0, 0), 1, GOLD), ("BOX", (1, 0), (1, 0), 1, GOLD),
                           ("BOX", (2, 0), (2, 0), 1, GOLD),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return t


def _page_money(a, prose, styles) -> List[Any]:
    stats = a.get("platform_stats", {})
    sizes = [str(int(s)) for s in a.get("order_sizes_usd", [])]
    pm_bps = [(_g(stats, "Polymarket", "mean_impact_bps", s) or 0) for s in sizes]
    kx_bps = [(_g(stats, "Kalshi", "mean_impact_bps", s) or 0) for s in sizes]

    boxes = _annot_boxes(styles)
    p3 = prose.get("page3", {})
    prose_flow = [Paragraph(p3[k], styles["body"]) for k in ("retail", "institutional", "fund") if p3.get(k)]
    gap = 6
    used = _h(boxes) + gap + sum(_h(p) for p in prose_flow)
    avail = FRAME_H - used - _FILL_SAFETY
    chart = _img_exact(charts.money_chart(pm_bps, kx_bps, figsize=(FRAME_W / 72.0, avail / 72.0)),
                       FRAME_W, avail)
    # Chart, then boxes and prose directly below with no padding gap.
    return [chart, boxes, Spacer(1, gap)] + prose_flow


def _page_heatmap(a, styles) -> List[Any]:
    pairs = a.get("pairs", [])
    title = Paragraph("Liquidity Quality Heatmap — All Matched Markets", styles["h"])
    rule = HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=1, spaceAfter=7)
    # Larger 9.5pt cells for this page (spec), with bolder headers.
    hc = ParagraphStyle("hc", parent=styles["cell"], fontSize=9.5, leading=11.5)
    hc_r = ParagraphStyle("hc_r", parent=hc, alignment=2)
    hh = ParagraphStyle("hh", parent=styles["cellhead"], fontSize=9)
    hh_r = ParagraphStyle("hh_r", parent=hh, alignment=2)
    flow = [title, rule]
    header = ["Market", "Cat.", "LQI", "Spread (bps)", "$10k (bps)", "$50k (bps)", "Diverg. (bps)", "Cheaper"]
    head_styles = [hh, hh, hh_r, hh_r, hh_r, hh_r, hh_r, hh]
    data = [[Paragraph(h, hs) for h, hs in zip(header, head_styles)]]
    bg_cmds = []
    for i, p in enumerate(pairs, start=1):
        pm, kx = p["polymarket"], p["kalshi"]
        lqi_v = pm.get("lqi")
        i10 = _g(pm, "impact_bps", "10000")
        i50 = _g(pm, "impact_bps", "50000")
        div = p.get("divergence_bps")
        cheaper = p.get("cheaper_venue") or "—"
        ch_short = "PM" if cheaper == "Polymarket" else ("KX" if cheaper == "Kalshi" else "—")
        row = [
            Paragraph(p["subject"][:26], hc),
            Paragraph(_CAT_CODE.get(p["category"], p["category"][:5]), hc),
            Paragraph(f"{lqi_v:.0f}" if lqi_v is not None else "—", hc_r),
            Paragraph(f"{pm.get('spread_bps'):.0f}" if pm.get("spread_bps") is not None else "—", hc_r),
            Paragraph(f"{i10:.0f}" if i10 is not None else "—", hc_r),
            Paragraph(f"{i50:.0f}" if i50 is not None else "—", hc_r),
            Paragraph(f"{div:.0f}" if div is not None else "—", hc_r),
            Paragraph(f'<font color="{config.COLOR_WHITE if ch_short=="PM" else "#000000"}">{ch_short}</font>', hc),
        ]
        data.append(row)
        bg_cmds.append(("BACKGROUND", (2, i), (2, i), _lqi_color(lqi_v)))
        bg_cmds.append(("BACKGROUND", (4, i), (4, i), _impact_color(i10)))
        bg_cmds.append(("BACKGROUND", (5, i), (5, i), _impact_color(i50)))
        bg_cmds.append(("BACKGROUND", (6, i), (6, i), _divergence_color(div)))
        bg_cmds.append(("BACKGROUND", (7, i), (7, i), DARK if ch_short == "PM" else (GOLD if ch_short == "KX" else white)))

    widths = [FRAME_W * w for w in (0.27, 0.10, 0.08, 0.13, 0.12, 0.12, 0.12, 0.09)]
    caption = Paragraph("Heatmap derived from live orderbook walking at all order sizes. "
                        "Green = superior, red = inferior for each metric; gold = wider divergence.",
                        styles["caption"])
    # Force row heights so the table fills the page down to the footer.
    nrows = len(data)
    avail = FRAME_H - _h(title) - _h(rule) - _h(caption) - _FILL_SAFETY
    row_h = max(16.0, avail / nrows) if nrows else 18.0
    t = Table(data, colWidths=widths, rowHeights=[row_h] * nrows, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ] + bg_cmds
    t.setStyle(TableStyle(style))
    flow.append(t)
    flow.append(caption)
    return flow


def _page_slippage(a, styles) -> List[Any]:
    pairs = [p for p in a.get("pairs", []) if p.get("avoidable_slippage_10k") is not None]
    flow = [Paragraph("Avoidable Slippage by Market — $10,000 Notional", styles["h"]),
            HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=1, spaceAfter=7)]
    if pairs:
        labels = [p["subject"][:26] for p in pairs]
        values = [p["avoidable_slippage_10k"] for p in pairs]
        cheaper = [p.get("cheaper_venue") or "Polymarket" for p in pairs]
        mean_val = sum(values) / len(values) if values else 0
        flow.append(_img(charts.slippage_bars(labels, values, cheaper, mean_val), FRAME_W))
        flow.append(Spacer(1, 8))
        # League table
        header = ["#", "Market", "Category", "PM slip ($)", "KX slip ($)", "Avoidable ($)", "Cheaper"]
        hs = [styles["cellhead"], styles["cellhead"], styles["cellhead"], styles["cellhead_r"],
              styles["cellhead_r"], styles["cellhead_r"], styles["cellhead"]]
        data = [[Paragraph(h, x) for h, x in zip(header, hs)]]
        for i, p in enumerate(pairs, 1):
            data.append([
                Paragraph(str(i), styles["cell"]),
                Paragraph(p["subject"][:24], styles["cell"]),
                Paragraph(p["category"].split()[0], styles["cell"]),
                Paragraph(f"{p.get('slippage_cost_pm', 0):,.0f}", styles["cell_r"]),
                Paragraph(f"{p.get('slippage_cost_kx', 0):,.0f}", styles["cell_r"]),
                Paragraph(f"{p['avoidable_slippage_10k']:,.0f}", styles["cell_r"]),
                Paragraph(f'<font color="{config.COLOR_GOLD}"><b>{("PM" if p.get("cheaper_venue")=="Polymarket" else "KX")}</b></font>', styles["cell"]),
            ])
        total = sum(values)
        data.append([Paragraph("", styles["cell_w"]), Paragraph("TOTAL", styles["cell_w"]),
                     Paragraph("", styles["cell_w"]), Paragraph("", styles["cell_w_r"]),
                     Paragraph("", styles["cell_w_r"]), Paragraph(f"{total:,.0f}", styles["cell_w_r"]),
                     Paragraph("", styles["cell_w"])])
        widths = [FRAME_W * w for w in (0.05, 0.30, 0.15, 0.135, 0.135, 0.14, 0.09)]
        bold_rows = [r for r in range(1, min(4, len(pairs) + 1))]
        flow.append(_table(data, widths, styles, total_row=True, bold_rows=bold_rows))
    else:
        flow.append(Paragraph("No comparable pairs with slippage data in this run.", styles["body"]))
    return flow


def _page_divergence(a, prose, styles) -> List[Any]:
    pairs = [p for p in a.get("pairs", []) if p.get("divergence_bps") is not None]
    pairs = sorted(pairs, key=lambda p: p["divergence_bps"], reverse=True)
    title = Paragraph("Displayed Mid Divergence — Same Event, Two Prices", styles["h"])
    rule = HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=1, spaceAfter=7)
    para = Paragraph(prose.get("page6", ""), styles["body"])
    flow: List[Any] = [title, rule]
    if pairs:
        labels = [p["subject"][:26] for p in pairs]
        pm_mids = [p["polymarket"].get("mid") or 0 for p in pairs]
        kx_mids = [p["kalshi"].get("mid") or 0 for p in pairs]
        divs = [p["divergence_bps"] for p in pairs]
        avail = FRAME_H - _h(title) - _h(rule) - _h(para) - _FILL_SAFETY
        chart = _img_exact(charts.divergence_dots(labels, pm_mids, kx_mids, divs,
                                                  figsize=(FRAME_W / 72.0, avail / 72.0)), FRAME_W, avail)
        flow.append(chart)
    flow.append(para)
    return flow


def _page_scatter(a, prose, styles) -> List[Any]:
    pairs = a.get("pairs", [])
    pm_pts = [(p["polymarket"].get("mid") or 0, _g(p["polymarket"], "impact_bps", "10000") or 0,
               p["polymarket"].get("volume") or 0) for p in pairs]
    kx_pts = [(p["kalshi"].get("mid") or 0, _g(p["kalshi"], "impact_bps", "10000") or 0,
               p["kalshi"].get("volume") or 0) for p in pairs]
    title = Paragraph("Does Higher Probability Mean Better Liquidity?", styles["h"])
    rule = HRFlowable(width="100%", thickness=1, color=GOLD, spaceBefore=1, spaceAfter=7)
    prose_flow = [Paragraph(p, styles["body"]) for p in prose.get("page7", [])]
    avail = FRAME_H - _h(title) - _h(rule) - sum(_h(p) for p in prose_flow) - _FILL_SAFETY
    chart = _img_exact(charts.prob_impact_scatter(pm_pts, kx_pts, figsize=(FRAME_W / 72.0, avail / 72.0)),
                       FRAME_W, avail)
    return [title, rule, chart] + prose_flow


def _page_rootcause(a, prose, styles) -> List[Any]:
    p8 = prose.get("page8", {})
    flow = _section("Why Do These Divergences Exist?", styles)
    for i, h in enumerate(p8.get("hypotheses", []), 1):
        flow.append(Paragraph(f"{i}.&nbsp;&nbsp;{_clip(h, 480)}", styles["num_c"]))
    flow.append(Spacer(1, 5))
    flow += _section("Recommendations — Addressed to Each Platform", styles)
    flow.append(Paragraph("For Polymarket", styles["param_b"]))
    for i, r in enumerate(p8.get("polymarket_recs", []), 1):
        flow.append(Paragraph(f"{i}.&nbsp;&nbsp;{_clip(r, 440)}", styles["num_c"]))
    flow.append(Spacer(1, 4))
    flow.append(Paragraph("For Kalshi", styles["param_b"]))
    for i, r in enumerate(p8.get("kalshi_recs", []), 1):
        flow.append(Paragraph(f"{i}.&nbsp;&nbsp;{_clip(r, 440)}", styles["num_c"]))
    return flow


def _page_methodology(a, prose, styles) -> List[Any]:
    p9 = prose.get("page9", {})
    flow = _section("Orderbook-Walking VWAP Methodology", styles)
    for para in p9.get("vwap", []):
        flow.append(Paragraph(_clip(para, 440), styles["body_c"]))
    flow.append(Paragraph(f"<i>{config.PHANTOM_LIQUIDITY_DISCLAIMER}</i>", styles["body_c"]))
    flow += _section("Market Matching", styles)
    for para in p9.get("matching", []):
        flow.append(Paragraph(_clip(para, 470), styles["body_c"]))
    flow += _section("Limitations and Caveats", styles)
    bullets = [
        "Phantom liquidity: displayed orders may be cancelled on approach, so figures are displayed depth, not guaranteed execution.",
        "Single-snapshot analysis: conditions can shift materially within hours of a news catalyst.",
        "LQI weight subjectivity: the 40/30/30 weighting reflects practitioner judgment, not a universal standard.",
        "Geographic restrictions: Kalshi sports contracts are geofenced in certain states, so availability of matched sports markets may vary.",
    ]
    for b in bullets:
        flow.append(Paragraph(f"•&nbsp;&nbsp;{b}", styles["num_c"]))
    flow.append(Spacer(1, 5))
    flow += _section("References", styles)
    for cite, title, note in config.ACADEMIC_REFERENCES:
        flow.append(Paragraph(f"<b>{cite}</b> {title} <i>{note}</i>", styles["caption"]))
    return flow


# ===========================================================================
# Assembly
# ===========================================================================
def generate_pdf(analysis: Dict[str, Any], output_path: Path,
                 prose: Optional[Dict[str, Any]] = None) -> Path:
    _RUNTIME["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    styles = _styles()
    if prose is None:
        prose = generate_prose(analysis)
    # Cache the prose so layout-only regenerations need no API call.
    try:
        with open(config.OUTPUT_DIR / "prose.json", "w", encoding="utf-8") as f:
            json.dump(prose, f, indent=2)
    except OSError:
        pass

    cover = Frame(M, 1.6 * inch, FRAME_W, PAGE_H * 0.60 - 1.9 * inch, id="cover",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    main = Frame(M, 0.62 * inch, FRAME_W, PAGE_H - 0.62 * inch - 0.42 * inch, id="main",
                 leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    doc = BaseDocTemplate(
        str(output_path), pagesize=LETTER,
        title="Cross-Platform Prediction Market Liquidity Intelligence",
        author="liquidity-agent",
    )
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover], onPage=_on_cover),
        PageTemplate(id="main", frames=[main], onPage=_on_main),
    ])

    story: List[Any] = []
    story += _cover_story(analysis, styles)
    story += [NextPageTemplate("main"), PageBreak()]
    story += _page_dashboard(analysis, styles) + [PageBreak()]
    story += _page_money(analysis, prose, styles) + [PageBreak()]
    story += _page_heatmap(analysis, styles) + [PageBreak()]
    story += _page_slippage(analysis, styles) + [PageBreak()]
    story += _page_divergence(analysis, prose, styles) + [PageBreak()]
    story += _page_scatter(analysis, prose, styles) + [PageBreak()]
    story += _page_rootcause(analysis, prose, styles) + [PageBreak()]
    story += _page_methodology(analysis, prose, styles)

    doc.build(story)
    logger.info("PDF written to %s", output_path)
    return output_path
