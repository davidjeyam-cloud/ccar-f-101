"""
Sequence diagrams for the live MCP pages (D2.3.1 hosted, D2.3.2 local) (matplotlib → PNG → st.image).

sequence_png(events) draws whatever utils/mcp_live.Log recorded, so the diagram under an answer
is the run that actually happened — not a stock picture. canonical_events() is the textbook flow
shown before the first run.

A sequence diagram reads top to bottom in time; the five lanes stay fixed. Text is kept large and
the figure grows downwards with the number of messages (same idea as the FLOWCHART RULE: scrolling
is fine, shrinking text is not).
"""

from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

LANES = [("you", "You"), ("agent", "Agent\n+ MCP client"), ("model", "Model\n(Gemini)"),
         ("server", "MCP servers\n(on this PC)"), ("sec", "The web")]
_X = {key: i * 2.6 + 1.3 for i, (key, _) in enumerate(LANES)}
_COLOR = {"user": "#1C2833", "answer": "#059669", "model": "#6B46C1", "model_reply": "#6B46C1",
          "mcp": "#0066CC", "mcp_reply": "#0066CC", "mcp_error": "#DC2626", "inferred": "#8A94A0",
          "sec": "#D97706"}
_DASHED = {"model_reply", "mcp_reply", "mcp_error", "inferred"}
ROW = 0.62


LANE_LABELS = {
    "hosted": {"server": "MCP server\n(separate service, URL)", "sec": "sec.gov"},
    "local": {"server": "MCP server\n(child process)", "sec": "This PC / the web"},
}


def canonical_events(mode: str = "hosted") -> list[dict]:
    """The textbook flow for each setup. Only the first and last steps and the transport differ."""
    if mode == "hosted":
        first = [("agent", "server", "HTTP POST initialize → the server's URL", "mcp")]
        call, back = "HTTP POST tools/call X", ("server", "sec", "HTTPS to sec.gov", "sec")
        last = [("agent", "server", "close the HTTP session (the server keeps running)", "mcp")]
    else:
        first = [("agent", "server", "START the server process (the client launches it)", "mcp"),
                 ("agent", "server", "initialize  (over stdin / stdout)", "mcp")]
        call, back = "tools/call X  (over stdin / stdout)", ("server", "sec", "read this PC  (or search the web)", "sec")
        last = [("agent", "server", "close the pipes → the server process exits", "mcp")]
    rows = [("you", "agent", "question", "user"), *first,
            ("server", "agent", "protocol version, capabilities", "mcp_reply"),
            ("agent", "server", "tools/list", "mcp"),
            ("server", "agent", "tools (name, description, inputSchema)", "mcp_reply"),
            ("agent", "model", "question + ALL tool descriptions", "model"),
            ("model", "agent", "function_call X  (Claude: tool_use)", "model_reply"),
            ("agent", "server", call, "mcp"), back,
            ("server", "agent", "result (content, isError)", "mcp_reply"),
            ("agent", "model", "history + tool result", "model"),
            ("model", "agent", "text, no function_call  (Claude: end_turn)", "model_reply"),
            *last,
            ("agent", "you", "answer", "answer")]
    return [{"n": i + 1, "src": s, "dst": d, "label": lab, "kind": k} for i, (s, d, lab, k) in enumerate(rows)]


def sequence_png(events: list[dict], title: str = "", mode: str = "") -> bytes:
    names = {**dict(LANES), **LANE_LABELS.get(mode, {})}
    n = len(events)
    top = n * ROW + 0.55
    fig, ax = plt.subplots(figsize=(12, max(3.2, top * 0.62 + 1.3)))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0.15, top + 1.75)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    if title:
        ax.text(0.1, top + 1.62, title, fontsize=13, fontweight="bold", color="#1C2833", va="top")
    for key, _ in LANES:
        x, label = _X[key], names[key]
        ax.plot([x, x], [0.2, top], color="#C9D1D9", lw=1.2, zorder=1)
        ax.text(x, top + 0.38, label, ha="center", va="center", fontsize=11.5, fontweight="bold", color="#1C2833",
                bbox=dict(boxstyle="round,pad=0.35", fc="#EEF4FB", ec="#9DB7D5", lw=1))
    for i, ev in enumerate(events):
        y = top - 0.55 - i * ROW
        x1, x2 = _X[ev["src"]], _X[ev["dst"]]
        color = _COLOR.get(ev["kind"], "#1C2833")
        ax.annotate("", xy=(x2, y), xytext=(x1, y), zorder=3,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.7,
                                    linestyle="--" if ev["kind"] in _DASHED else "-"))
        label = f'{ev["n"]}. {ev["label"]}'
        if ev.get("ms") is not None:
            label += f'  · {ev["ms"]} ms'
        ax.text((x1 + x2) / 2, y + 0.09, label, ha="center", va="bottom", fontsize=10.5, color=color, zorder=4,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return buf.getvalue()
