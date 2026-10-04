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


# ── schematic: where each part runs ─────────────────────────────────────────
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

_GREEN, _BLUE, _AMBER, _GREY = "#059669", "#0066CC", "#D97706", "#64748B"


def _zone(ax, x0, y0, x1, y1, title, color, fill, dashed=False, lw=2.6, size=12.5):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=1.6", fc=fill, ec=color,
                                lw=lw, ls="--" if dashed else "-", zorder=1))
    ax.text(x0 + 1.2, y1 - 1.0, title, ha="left", va="top", fontsize=size, fontweight="bold", color=color, zorder=2,
            linespacing=1.25)


def _box(ax, cx, cy, w, h, text, color, fill="#FFFFFF", size=12):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc=fill, ec=color,
                                lw=2, zorder=3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=size, color="#1C2833", zorder=4, linespacing=1.3)


def _arrow(ax, p0, p1, label, color, lw=2.2, both=False, dashed=False, label_at=0.5, dy=2.2, size=11.5, dx=0.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<|-|>" if both else "-|>", mutation_scale=16, color=color, lw=lw,
                                 ls="--" if dashed else "-", zorder=5, shrinkA=0, shrinkB=0))
    x = p0[0] + (p1[0] - p0[0]) * label_at + dx
    y = p0[1] + (p1[1] - p0[1]) * label_at + dy
    ax.text(x, y, label, ha="center", va="bottom", fontsize=size, color=color, zorder=6, linespacing=1.25,
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.92))


def schematic_png(kind: str, on_windows: bool = True) -> bytes:
    """Where each part runs: this machine / localhost / somewhere else (the internet) / the SEC's servers.

    kind: "hosted" (the server is a separate service reached by a URL) or "local" (a child process, stdio).
    on_windows: whether the app is running on a Windows computer (the user's laptop). The zone's name says so
    plainly; on any other system it says the app is on some other machine (for the hosted copy: Streamlit's server)."""
    fig, ax = plt.subplots(figsize=(12, 9.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 91 if on_windows else 100)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    laptop = ("YOUR LAPTOP — it is running this app right now" if on_windows else
              "THE MACHINE RUNNING THIS APP\n(on the hosted copy: Streamlit's server)")
    _zone(ax, 1.5, 2, 61, 88, laptop, _GREEN, "#F2FAF5")
    _zone(ax, 66, 2, 99, 88, "SOMEWHERE ELSE\nacross the internet,\non other people's computers", _AMBER, "#FFF8E8")
    if on_windows:
        _box(ax, 31, 77.5, 36, 8, "Your browser tab\n(this web page)", _GREY, "#F1F5F9")
    else:
        _box(ax, 46, 95, 36, 7, "Your browser tab\n(on your own laptop)", _GREY, "#F1F5F9")
        ax.add_patch(FancyArrowPatch((46, 91.5), (46, 68.2), arrowstyle="<|-|>", mutation_scale=16, color=_GREY, lw=2,
                                     zorder=5))
    _box(ax, 31, 62, 42, 12, "Streamlit app  (a Python process)\nthe agent  +  the MCP client", _BLUE, "#EEF4FB")
    if on_windows:
        ax.add_patch(FancyArrowPatch((31, 73.4), (31, 68.2), arrowstyle="<|-|>", mutation_scale=16, color=_GREY, lw=2, zorder=5))

    _box(ax, 82.5, 62, 29, 13, "Google — the Gemini model\ngenerativelanguage\n.googleapis.com", _AMBER, "#FFFFFF", 11.5)
    _arrow(ax, (52, 62), (68, 62), "HTTPS\nleaves this machine", _AMBER, both=True, dy=1.6, dx=-2.5)

    if kind == "hosted":
        _zone(ax, 5, 6, 57, 45, "localhost = 127.0.0.1\nonly this machine can connect (loopback)", _BLUE,
              "#EAF3FF", dashed=True, lw=2.2, size=11.5)
        _box(ax, 31, 21, 44, 15,
             "MCP server process — the sec-edgar tools\nlistens on port 9870\nstarted by the “Start the service” button", _GREEN,
             "#FFFFFF", 11.5)
        _arrow(ax, (31, 55.8), (31, 28.7), "HTTP POST  http://127.0.0.1:9870/mcp\nstays inside this machine", _BLUE, lw=2.8,
               both=True, label_at=0.25, dy=-2.7, dx=0)
        _zone(ax, 68, 6, 97.5, 50, "THE SEC's SERVERS", _AMBER, "#FFFFFF", lw=2.2, size=11.5)
        _box(ax, 82.7, 36, 25, 11, "data.sec.gov\nREST API  →  JSON", _AMBER, "#FFF8E8", 11.5)
        _box(ax, 82.7, 17, 25, 12, "www.sec.gov\nfiles: filing text,\nthe ticker list", _AMBER, "#FFF8E8", 11.5)
        _arrow(ax, (53.2, 25), (70.2, 36), "HTTPS GET", _AMBER, label_at=0.45, dy=1.0, dx=-0.5)
        _arrow(ax, (53.2, 17), (70.2, 17), "HTTPS GET", _AMBER, dy=0.9)
    else:
        _box(ax, 31, 36, 42, 12, "MCP server process  (a child process)\nlaptop_server.py\nstarted by the app for each question", _GREEN,
             "#FFFFFF", 11.5)
        _arrow(ax, (31, 55.8), (31, 42.2), "stdio: stdin / stdout pipes\nno network port at all", _BLUE, lw=2.8, both=True,
               label_at=0.55, dy=-1.1)
        _box(ax, 31, 12, 42, 11, "This computer's own data\nhardware · disks · folders · notes file", _GREY, "#F1F5F9", 11.5)
        _arrow(ax, (31, 29.8), (31, 17.7), "reads directly\n(no request)", _GREEN, dy=-0.5, label_at=0.5)
        _box(ax, 82.7, 30, 27, 12, "A public search engine\nand three well-known websites\n(web_search · check_internet)", _AMBER,
             "#FFF8E8", 11)
        _arrow(ax, (52, 35), (69, 30), "HTTPS\n2 tools only", _AMBER, dy=1.0, label_at=0.5)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=125, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return buf.getvalue()
