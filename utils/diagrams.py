"""
Diagrams for ccar-f-101. Each function returns PNG bytes ready for st.image().
Style mirrors agents101's utils/diagrams.py (matplotlib -> PNG, same palette
family) so the two apps look related, adapted to this project's three-key
architecture (Claude Code subscription / Gemini demos / Claude API 🔑 pages).
"""

import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── Colour palette ──────────────────────────────────────────────────────────
C = {
    "bg":       "#F5F7FA",   # matches .streamlit/config.toml backgroundColor
    "claude":   "#D97706",   # amber  — Claude Code / Claude API (exam ground truth)
    "gemini":   "#0066CC",   # blue   — Gemini (this app's demo engine)
    "app":      "#1A202C",   # dark navy — the Streamlit app itself
    "active":   "#059669",   # green  — active now, no purchase needed
    "future":   "#DC2626",   # red    — needs a purchase before it works
    "arrow":    "#5D6D7E",
    "dim":      "#AAB7B8",
}
W, H = 7.0, 4.4


def _fig():
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.set_facecolor(C["bg"])
    fig.patch.set_facecolor(C["bg"])
    return fig, ax


def _box(ax, cx, cy, text, color, w=1.9, h=0.72, fontsize=9):
    patch = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.12",
        facecolor=color, edgecolor="white", linewidth=2.0, zorder=3,
    )
    ax.add_patch(patch)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4,
            multialignment="center", linespacing=1.4)


def _arrow(ax, x1, y1, x2, y2, label="", color=None, dashed=False):
    color = color or C["arrow"]
    ls = (0, (4, 3)) if dashed else "solid"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                                mutation_scale=14, linestyle=ls), zorder=5)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.1, label, ha="center", va="bottom",
                fontsize=7, color=color, style="italic", zorder=6)


def _badge(ax, cx, cy, text, color, fontsize=7.5):
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=6,
            bbox=dict(boxstyle="round,pad=0.28", facecolor=color,
                      edgecolor="white", linewidth=1, zorder=5))


def _to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════
# Diagram 00 — Hello Claude: the three-key architecture
# ══════════════════════════════════════════════════════════════════════════

def diagram_00_hello() -> bytes:
    fig, ax = _fig()

    ax.text(W / 2, 4.22, "Three keys, three jobs — CCAR-F study workbench",
            ha="center", fontsize=11.5, fontweight="bold", color="#1C2833")
    ax.text(W / 2, 3.98, "You learn Claude Code and the Claude API; this app's own demos run on Gemini",
            ha="center", fontsize=8, color="#566573", style="italic")

    # Top row: the learner and VS Code / Claude Code
    _box(ax, 1.0, 3.55, "You\n(learner)", C["app"], w=1.5, h=0.5, fontsize=8.5)
    _box(ax, 3.5, 3.55, "Claude Code\n(VS Code panel)", C["claude"], w=2.1, h=0.5, fontsize=8.5)
    _arrow(ax, 1.75, 3.55, 2.45, 3.55, label="your subscription\n— no key")

    _badge(ax, 3.5, 3.08, "builds this repo + sandbox_project/", C["dim"], fontsize=6.8)

    # Middle: the Streamlit app itself
    _box(ax, 3.5, 2.60, "This Streamlit app\n(app.py -> pages/)", C["app"], w=2.6, h=0.55, fontsize=8.5)
    _arrow(ax, 3.5, 3.35, 3.5, 2.875)

    # Bottom row: two demo engines. Fan-out arrows START at 2.15 (comfortably
    # below the app box's true bottom edge, ~2.325 once FancyBboxPatch's own
    # corner padding is accounted for) and END at 1.20 (above the demo boxes'
    # top). Labels are placed manually at the gap's midpoint (~1.68), not via
    # _arrow's auto-midpoint, so they can never collide with either box.
    _box(ax, 1.7, 0.85, "Gemini 2.5 Flash\nGEMINI_API_KEY", C["gemini"], w=2.1, h=0.6, fontsize=8)
    _box(ax, 5.3, 0.85, "Claude API\nANTHROPIC_API_KEY", C["claude"], w=2.1, h=0.6, fontsize=8)

    # NOTE: matplotlib + DejaVu Sans (the default font) has no emoji glyphs —
    # keep diagram text to plain ASCII/Unicode punctuation, same lesson the
    # arch-diagram skill already learned for wkhtmltoimage.
    _arrow(ax, 3.05, 2.15, 2.15, 1.20)
    _arrow(ax, 3.95, 2.15, 4.85, 1.20, dashed=True)
    # Opaque background patch (matching the page background) behind each
    # label so the arrow line never visually crosses through the text.
    _label_bg = dict(boxstyle="round,pad=0.15", facecolor=C["bg"], edgecolor="none")
    ax.text(2.35, 1.68, "pattern demos\nevery page", ha="center", va="center",
            fontsize=7, color=C["gemini"], style="italic", linespacing=1.3, zorder=6,
            bbox=_label_bg)
    ax.text(4.65, 1.68, "KEY pages only\nexact exam mechanics", ha="center", va="center",
            fontsize=7, color=C["claude"], style="italic", linespacing=1.3, zorder=6,
            bbox=_label_bg)

    _badge(ax, 1.7, 0.30, "ACTIVE NOW — free tier, cheap", C["active"], fontsize=7)
    _badge(ax, 5.3, 0.30, "BUY BEFORE DAY 1 — see KEY pages", C["future"], fontsize=7)

    return _to_bytes(fig)
