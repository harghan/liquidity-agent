"""
Chart generation (matplotlib) for the visual-first report.

Every chart is rendered to an in-memory PNG (BytesIO) at high DPI and embedded
into the PDF by the report writer. The visual language is consistent with the
PDF design system: white background, near-black (#0a0a0a) for Polymarket, gold
(#c8a951) for Kalshi, muted grey gridlines, bold sans-serif labels. No default
matplotlib styling survives.
"""

from __future__ import annotations

from io import BytesIO
from typing import List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

import config  # noqa: E402

DARK = config.COLOR_DARK
GOLD = config.COLOR_GOLD
MUTED = config.COLOR_MUTED
DANGER = config.COLOR_DANGER
SAFE = config.COLOR_SAFE
GRID = "#dddddd"

# Prefer Helvetica/Arial; fall back to the always-present DejaVu Sans. Never serif.
_available = {f.name for f in font_manager.fontManager.ttflist}
_family = next((f for f in ("Helvetica", "Arial", "Liberation Sans") if f in _available), "DejaVu Sans")
plt.rcParams.update({
    "font.family": _family,
    "font.size": 9,
    "axes.edgecolor": "#cccccc",
    "axes.linewidth": 0.8,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlecolor": DARK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "text.color": "#222222",
})

SIZE_LABELS = ["$500", "$2k", "$10k", "$50k", "$100k"]


def _png(fig, dpi: int = 170) -> BytesIO:
    # No bbox_inches="tight": keep the PNG at exactly figsize*dpi so the embedded
    # aspect ratio matches the figure and charts can fill a target box without
    # distortion. tight_layout() (called per chart) keeps labels inside the area.
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def platform_quality(pm: dict, kx: dict, figsize=(4.8, 6.0)) -> BytesIO:
    """Horizontal grouped bars: Mean LQI, Mean Spread (bps), Mean $10k Impact (bps).

    Each metric's two bars are scaled to that metric's own maximum (so differing
    units are visually comparable) while the real value is printed on the bar.
    """
    metrics = [
        ("Mean LQI", pm.get("mean_lqi") or 0, kx.get("mean_lqi") or 0, "{:.1f}"),
        ("Mean Spread (bps)", pm.get("mean_spread_bps") or 0, kx.get("mean_spread_bps") or 0, "{:.0f}"),
        ("Mean $10k Impact (bps)", (pm.get("mean_impact_bps") or {}).get("10000") or 0,
         (kx.get("mean_impact_bps") or {}).get("10000") or 0, "{:.0f}"),
    ]
    fig, axes = plt.subplots(len(metrics), 1, figsize=figsize)
    for ax, (label, pv, kv, fmt) in zip(axes, metrics):
        mx = max(pv, kv, 1e-9)
        ax.barh([1], [pv / mx], color=DARK, height=0.55, label="Polymarket")
        ax.barh([0], [kv / mx], color=GOLD, height=0.55, label="Kalshi")
        ax.text(pv / mx + 0.02, 1, fmt.format(pv), va="center", ha="left", fontsize=8.5, color=DARK, fontweight="bold")
        ax.text(kv / mx + 0.02, 0, fmt.format(kv), va="center", ha="left", fontsize=8.5, color="#7a6320", fontweight="bold")
        ax.set_xlim(0, 1.25)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title(label, fontsize=9.5, loc="left", pad=3)
        for s in ("top", "right", "bottom", "left"):
            ax.spines[s].set_visible(False)
    axes[0].legend(loc="lower right", frameon=False, fontsize=8, ncol=2, bbox_to_anchor=(1.02, 1.15))
    fig.suptitle("Platform Quality Comparison", fontsize=11.5, fontweight="bold", color=DARK, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return _png(fig)


def impact_scaling(pm_bps: Sequence[float], kx_bps: Sequence[float], figsize=(4.8, 6.0)) -> BytesIO:
    """Grouped vertical bars: mean impact (bps) at all five order sizes."""
    import numpy as np
    x = np.arange(len(SIZE_LABELS))
    w = 0.38
    fig, ax = plt.subplots(figsize=figsize)
    b1 = ax.bar(x - w / 2, pm_bps, w, color=DARK, label="Polymarket")
    b2 = ax.bar(x + w / 2, kx_bps, w, color=GOLD, label="Kalshi")
    for bars in (b1, b2):
        for r in bars:
            h = r.get_height()
            ax.text(r.get_x() + r.get_width() / 2, h, f"{h:.0f}", ha="center", va="bottom", fontsize=6.5, color="#444")
    ax.set_xticks(x)
    ax.set_xticklabels(SIZE_LABELS)
    ax.set_ylabel("Mean price impact (bps)", fontsize=9)
    ax.set_title("Price Impact Scaling by Order Size", loc="left")
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    return _png(fig)


def money_chart(pm_bps: Sequence[float], kx_bps: Sequence[float], figsize=(9.2, 4.9)) -> BytesIO:
    """The money chart: price-impact curves across the five order sizes."""
    import numpy as np
    x = np.arange(len(SIZE_LABELS))
    fig, ax = plt.subplots(figsize=figsize)
    ax.fill_between(x, pm_bps, kx_bps, color=GOLD, alpha=0.13, zorder=1)
    ax.plot(x, pm_bps, "-o", color=DARK, linewidth=2.4, markersize=7, label="Polymarket", zorder=3)
    ax.plot(x, kx_bps, "-o", color=GOLD, linewidth=2.4, markersize=7, label="Kalshi", zorder=3)

    def _crosshair(i, note):
        pv, kv = pm_bps[i], kx_bps[i]
        top = max(pv, kv)
        ax.axvline(i, color=MUTED, linestyle=":", linewidth=0.9, zorder=2)
        ax.annotate(f"{note}\nPM {pv:.0f} bps\nKX {kv:.0f} bps",
                    xy=(i, top), xytext=(0, 18), textcoords="offset points",
                    ha="center", fontsize=8, fontweight="bold", color=DARK,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=GOLD, lw=1))

    _crosshair(2, "$10k")
    _crosshair(4, "$100k")
    ax.set_xticks(x)
    ax.set_xticklabels(SIZE_LABELS, fontsize=10)
    ax.set_ylabel("Mean price impact (bps)", fontsize=10)
    ax.set_title("Price Impact Curves: Where the Orderbook Breaks", loc="left", fontsize=13)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.margins(y=0.22)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    fig.tight_layout()
    return _png(fig)


def slippage_bars(labels: Sequence[str], values: Sequence[float],
                  cheaper: Sequence[str], mean_val: float) -> BytesIO:
    """Horizontal bars of avoidable slippage, coloured by cheaper venue."""
    import numpy as np
    n = len(labels)
    fig, ax = plt.subplots(figsize=(9.2, max(2.6, 0.34 * n + 1.1)))
    y = np.arange(n)[::-1]  # largest at top
    colors = [DARK if c == "Polymarket" else GOLD for c in cheaper]
    ax.barh(y, values, color=colors, height=0.66)
    for yi, v in zip(y, values):
        ax.text(v + max(values) * 0.01, yi, f"${v:,.0f}", va="center", ha="left", fontsize=7.5, color="#333")
    if mean_val and mean_val > 0:
        ax.axvline(mean_val, color=GOLD, linestyle="--", linewidth=1.3)
        ax.text(mean_val, n - 0.3, f"  mean ${mean_val:,.0f}", color="#7a6320", fontsize=8, fontweight="bold", va="top")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Avoidable slippage on a $10,000 order (USD)", fontsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.margins(x=0.12)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return _png(fig)


def divergence_dots(labels: Sequence[str], pm_mids: Sequence[float],
                    kx_mids: Sequence[float], div_bps: Sequence[float],
                    figsize=None) -> BytesIO:
    """Dot plot: PM vs KX displayed mid per market, connector keyed to gap."""
    import numpy as np
    n = len(labels)
    if figsize is None:
        figsize = (9.2, max(2.8, 0.36 * n + 1.1))
    fig, ax = plt.subplots(figsize=figsize)
    y = np.arange(n)[::-1]
    for yi, pmv, kxv, d in zip(y, pm_mids, kx_mids, div_bps):
        wide = d >= 100
        ax.plot([pmv, kxv], [yi, yi], color=(GOLD if wide else "#cccccc"),
                linewidth=(3.0 if wide else 1.2), zorder=1, solid_capstyle="round")
        if wide:
            xm = (pmv + kxv) / 2
            ax.text(xm, yi + 0.25, f"{d:.0f} bps", color=DANGER, fontsize=7, ha="center", fontweight="bold")
    ax.scatter(pm_mids, y, color=DARK, s=42, zorder=3, label="Polymarket")
    ax.scatter(kx_mids, y, color=GOLD, s=42, zorder=3, edgecolor="#7a6320", linewidth=0.5, label="Kalshi")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("Displayed implied probability", fontsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.tight_layout()
    return _png(fig)


def prob_impact_scatter(pm_pts: Sequence[Tuple[float, float, float]],
                        kx_pts: Sequence[Tuple[float, float, float]],
                        figsize=(9.2, 5.2)) -> BytesIO:
    """Scatter of displayed probability vs $10k impact (bps), sized by volume."""
    import numpy as np

    def _sizes(vols):
        vols = [v if (v and v > 0) else 0 for v in vols]
        mx = max(vols) if any(vols) else 0
        if mx <= 0:
            return [45] * len(vols)
        return [40 + 200 * (v / mx) for v in vols]

    fig, ax = plt.subplots(figsize=figsize)
    for pts, color, lab, ec in ((pm_pts, DARK, "Polymarket", "none"),
                                (kx_pts, GOLD, "Kalshi", "#7a6320")):
        if not pts:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ss = _sizes([p[2] for p in pts])
        ax.scatter(xs, ys, s=ss, color=color, alpha=0.8, edgecolor=ec, linewidth=0.5, label=lab, zorder=3)
        # simple linear trend
        if len(xs) >= 2 and len(set(xs)) >= 2:
            m, b = np.polyfit(xs, ys, 1)
            xx = np.linspace(min(xs), max(xs), 50)
            ax.plot(xx, m * xx + b, color=color, linewidth=1.5, linestyle="--", alpha=0.8, zorder=2)

    ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("Displayed implied probability", fontsize=10)
    ax.set_ylabel("$10k price impact (bps)", fontsize=10)
    ax.grid(color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ymax = ax.get_ylim()[1]
    ax.text(0.02, ymax * 0.95, "High impact, low probability\n(illiquid tail)", fontsize=7.5,
            color=MUTED, va="top", ha="left", style="italic")
    ax.text(0.98, ymax * 0.06, "Low impact, high probability\n(deep, liquid)", fontsize=7.5,
            color=MUTED, va="bottom", ha="right", style="italic")
    ax.legend(frameon=False, fontsize=9.5, loc="upper right")
    fig.tight_layout()
    return _png(fig)
