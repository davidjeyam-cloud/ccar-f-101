"""
Draws the charts the synthesis agent asks for on the live MCP pages (D2.3.1 / D2.3.2) (matplotlib → PNG → st.image).

The MODEL chooses the chart type and supplies the numbers (utils/mcp_live.synthesise); this module only
draws what it was given. The drawing rules are fixed here, not left to the model:
- one y-scale per chart, starting at zero for bars;
- a single-measure bar chart uses one colour; several series use a fixed colour order and a legend;
- text is always dark ink, never the series colour;
- a value that could not be found in the tool result it cites is drawn hatched and marked "unverified".
A static image has no hover, so the page prints every plotted value in a table under the chart.
"""

from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402

SURFACE, INK, INK_2, MUTED, AXIS, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#c3c2b7", "#ecebe6"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]        # fixed order; never cycled past four
MAX_SERIES = len(SERIES)
_SCALES = ((1e12, "trillions"), (1e9, "billions"), (1e6, "millions"), (1e3, "thousands"))


def _scale(values: list) -> tuple:
    top = max((abs(v) for v in values), default=0)
    for div, word in _SCALES:
        if top >= div:
            return div, word
    return 1, ""


def _num(v: float) -> str:
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:,.1f}" if abs(v) >= 10 else f"{v:,.2f}"


def chart_png(chart: dict) -> bytes:
    series = [s for s in chart["series"] if s["points"]][:MAX_SERIES]
    labels = list(dict.fromkeys(p["label"] for s in series for p in s["points"]))
    div, word = _scale([p["value"] for s in series for p in s["points"]])
    kind = chart["chart_type"]
    if kind == "bar" and len(series) > 1:
        kind = "grouped_bar"                                   # the model sent several series: draw them side by side
    n_lab, n_ser = len(labels), len(series)

    fig, ax = plt.subplots(figsize=(max(6.5, min(11, 1.9 + n_lab * (0.75 + 0.45 * (n_ser if kind == "grouped_bar" else 1)))), 4.3))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    xs = list(range(n_lab))
    label_all = n_lab * (n_ser if kind == "grouped_bar" else 1) <= 9

    def val(s, lab):
        return next((p for p in s["points"] if p["label"] == lab), None)

    if kind == "line":
        for i, s in enumerate(series):
            pts = [(x, val(s, lab)) for x, lab in zip(xs, labels) if val(s, lab)]
            ax.plot([x for x, _ in pts], [p["value"] / div for _, p in pts], color=SERIES[i], lw=2, solid_capstyle="round",
                    marker="o", ms=8, mec=SURFACE, mew=2, label=s["name"], zorder=3)
            for x, p in pts:
                if p.get("check") != "ok":
                    ax.plot([x], [p["value"] / div], marker="o", ms=13, mfc="none", mec=INK_2, mew=1.2, zorder=4)
            if pts:
                x, p = pts[-1]
                ax.annotate(_num(p["value"] / div), (x, p["value"] / div), xytext=(8, 0), textcoords="offset points",
                            va="center", fontsize=10, color=INK)
    else:
        width = min(0.34, 0.72 / n_ser) if kind == "grouped_bar" else 0.36
        bottoms = [0.0] * n_lab
        named: set = set()
        for i, s in enumerate(series):
            for x, lab in zip(xs, labels):
                p = val(s, lab)
                if not p:
                    continue
                v = p["value"] / div
                if kind == "grouped_bar":
                    pos, base = x + (i - (n_ser - 1) / 2) * width, 0.0
                else:
                    pos, base = x, bottoms[x] if kind == "stacked_bar" else 0.0
                ax.bar(pos, v, width=width * (0.92 if kind == "grouped_bar" else 1), bottom=base, color=SERIES[i],
                       edgecolor=SURFACE, linewidth=2, hatch=None if p.get("check") == "ok" else "///", zorder=3,
                       label=None if s["name"] in named else s["name"])
                named.add(s["name"])
                if kind == "stacked_bar":
                    bottoms[x] += v
                elif label_all:
                    ax.annotate(_num(v), (pos, v), xytext=(0, 4 if v >= 0 else -12), textcoords="offset points",
                                ha="center", fontsize=10, color=INK)
        if kind == "stacked_bar":
            for x in xs:
                ax.annotate(_num(bottoms[x]), (x, bottoms[x]), xytext=(0, 4), textcoords="offset points", ha="center",
                            fontsize=10, color=INK)
        ax.axhline(0, color=AXIS, lw=1, zorder=2)

    ax.set_xticks(xs)
    wrapped = [lab if len(lab) <= 16 else lab.replace(" (", "\n(").replace(" - ", "\n") for lab in labels]
    ax.set_xticklabels(wrapped, fontsize=10.5, color=INK_2)
    ax.set_xlim(-0.6, n_lab - 0.4 + (0.5 if kind == "line" else 0))
    ax.tick_params(axis="both", length=0)
    ax.tick_params(axis="y", labelsize=10, labelcolor=MUTED)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}" if abs(v) >= 10 or v == 0 else f"{v:,.1f}"))
    ax.grid(axis="y", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    unit = " ".join(x for x in (chart.get("y_label", "").strip(), word) if x)
    ax.set_ylabel(unit, fontsize=10.5, color=INK_2)
    ax.set_title(chart["title"], loc="left", fontsize=13, fontweight="bold", color=INK, pad=14)
    if n_ser >= 2:
        handles, names = ax.get_legend_handles_labels()
        uniq = dict(zip(names, handles))
        ax.legend(uniq.values(), uniq.keys(), frameon=False, fontsize=10, labelcolor=INK_2, loc="upper center",
                  bbox_to_anchor=(0.5, -0.16 - 0.05 * max(lab.count("\n") for lab in wrapped)), ncol=min(4, n_ser))
    if any(p.get("check") != "ok" for s in series for p in s["points"]):
        fig.text(0.01, 0.005, "Hatched or ringed = value not found in the tool result it cites (unverified)",
                 fontsize=9, color=INK_2)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return buf.getvalue()
