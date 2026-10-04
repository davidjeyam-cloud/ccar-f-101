"""
Shared renderer for the two live MCP pages (➕ extras — not on the CCAR-F exam):

    pages/c231_mcp_hosted.py  D2.3.1  MCP client → a server hosted SEPARATELY (SEC EDGAR, Streamable HTTP)
    pages/c232_mcp_local.py   D2.3.2  My OWN MCP server, hosted LOCALLY (my-laptop, stdio)

Each page connects to ONE server so the two setups can be told apart. Both open with a schematic and a
sequence diagram of their setup and the same numbered comparison table; then a question box, the answer
(written by the synthesis agent, with any charts it chose), one steps table, and the tool results printed as
readable tables. The engine is utils/mcp_live.py.

Kept simple at the user's request (2026-10-04, "too much info"): tokens, the run's own sequence diagram and
the raw JSON sit in one collapsed Details expander. Pressing Ask clears the previous result.
"""

import csv
import io
import json
import platform
import re

import streamlit as st

from utils import mcp_charts, mcp_live, mcp_seq

MAX_ROWS = 25
# Plumbing fields that add nothing for a reader (still visible in Details → Raw JSON).
HIDE = {"success", "context_ref", "scale", "raw_value", "source", "suggestion", "disclaimer", "verification_note",
        "data_source"}

_NODE = 'shape=box, style="rounded,filled", fontname="Helvetica", fontsize=18, margin="0.25,0.14"'
_EDGE = 'fontname="Helvetica", fontsize=15'
SCHEMATIC = {
    "hosted": f"""digraph G {{ rankdir=TB; nodesep=0.7; ranksep=0.75; node [{_NODE}]; edge [{_EDGE}];
  you [label="You\\n(this web page)", fillcolor="#F1F5F9", color="#64748B"];
  subgraph cluster_app {{ label="THIS APP — on your PC"; fontname="Helvetica"; fontsize=16; color="#0066CC"; style="rounded";
    agent [label="Agent + MCP client", fillcolor="#EEF4FB", color="#0066CC"]; }}
  model [label="Model (Gemini)\\nchooses the tool", fillcolor="#F3EEFB", color="#6B46C1"];
  subgraph cluster_srv {{ label="SEPARATE SERVICE — reached by a URL\\n(already running; the client did not start it)";
    fontname="Helvetica"; fontsize=16; color="#059669"; style="rounded";
    server [label="MCP server: sec-edgar\\nthe 21 tools live HERE", fillcolor="#ECFDF5", color="#059669"]; }}
  data [label="sec.gov\\n(the filings)", fillcolor="#FFFBEB", color="#D97706"];
  you -> agent [label=" question / answer", dir=both];
  agent -> model [label=" question + tool list ", dir=both];
  agent -> server [label=" Streamable HTTP\\n each message is an HTTP POST", dir=both, color="#0066CC", penwidth=2];
  server -> data [label=" HTTPS", color="#D97706"];
  {{ rank=same; agent; model }} }}""",
    "local": f"""digraph G {{ rankdir=TB; nodesep=0.7; ranksep=0.75; node [{_NODE}]; edge [{_EDGE}];
  you [label="You\\n(this web page)", fillcolor="#F1F5F9", color="#64748B"];
  subgraph cluster_app {{ label="THIS APP — on your PC"; fontname="Helvetica"; fontsize=16; color="#0066CC"; style="rounded";
    agent [label="Agent + MCP client", fillcolor="#EEF4FB", color="#0066CC"];
    server [label="MCP server: my-laptop\\nYOUR 4 tools live HERE\\n(child process the client starts)", fillcolor="#ECFDF5", color="#059669"]; }}
  model [label="Model (Gemini)\\nchooses the tool", fillcolor="#F3EEFB", color="#6B46C1"];
  pc [label="This PC\\nhardware · disks · folders", fillcolor="#FFFBEB", color="#D97706"];
  web [label="Public web\\n(web_search only)", fillcolor="#FFFBEB", color="#D97706"];
  you -> agent [label=" question / answer", dir=both];
  agent -> model [label=" question + tool list ", dir=both];
  agent -> server [label=" stdio\\n stdin / stdout pipes", dir=both, color="#0066CC", penwidth=2];
  server -> pc [label=" reads", color="#D97706"];
  server -> web [label=" searches", color="#D97706", style=dashed];
  {{ rank=same; agent; model }} {{ rank=same; pc; web }} }}""",
}

COMPARE = (
    ("Who starts the server", "Its owner. It is already running; the client never starts it",
     "The client. It launches the server as a child process and the server exits when the client closes"),
    ("How the client finds it", "A URL (`http://…/mcp`)", "A command line (which program and file to run)"),
    ("Transport", "Streamable HTTP — each message is an HTTP POST", "stdio — messages go over the process's stdin / stdout"),
    ("Where the tools run", "Inside the separate service, outside this app", "Inside the child process, on this PC"),
    ("Who wrote the tools", "Someone else (the community `sec-edgar-mcp`). You cannot change them",
     "You (`mcp_servers/laptop_server.py`). You write the descriptions and the errors"),
    ("What the client can see", "Requests and results only — not what the server does behind its URL*",
     "The same protocol view, plus you can read the server's code and log"),
    ("Who it can serve", "Many clients at once", "One client (the one that started it)"),
    ("The same in both", "`initialize` → `tools/list` → `tools/call`; the model chooses the tool from its description",
     "`initialize` → `tools/list` → `tools/call`; the model chooses the tool from its description"),
)

PAGES = {
    "hosted": {
        "num": "D2.3.1", "icon": "🌐", "server": "sec", "other": "local",
        "title": "MCP client → a server hosted separately (SEC EDGAR)",
        "caption": "This app is only the CLIENT. The MCP server runs as its own service and is reached by a URL; "
                   "its tools fetch from sec.gov.",
        "seq_title": "Hosted separately: the server is already running; the client only knows its URL",
        "examples": ("What was Apple's revenue and net income in its latest filing?",
                     "Compare the revenue and net income of Apple, Microsoft and Alphabet in their latest filings.",
                     "List the two most recent 10-K filings for Microsoft.",
                     "Company facts for ticker AAPL"),
        "placeholder": "e.g. What was Apple's net income in its latest filing?",
    },
    "local": {
        "num": "D2.3.2", "icon": "🏠", "server": "laptop", "other": "hosted",
        "title": "My own MCP server, hosted on this PC (my-laptop)",
        "caption": "This app is the CLIENT and also STARTS the server: your own tools, in a child process on this PC.",
        "seq_title": "Local: the client starts the server and talks to it over stdin / stdout",
        "examples": ("What laptop is this, and how much memory is free?",
                     "How full are my drives?",
                     "What processor does this computer have, and when was it released? Search the web.",
                     "Which folders in my Downloads folder are the biggest?"),
        "placeholder": "e.g. How full are my drives?",
    },
}


# ── readable results ─────────────────────────────────────────────────────────
def _label(key: str) -> str:
    words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(key)).replace("_", " ").strip()
    words = " ".join(w.upper() if w.lower() in ("cik", "sic", "url", "sec", "eps", "id", "ram", "gb", "cpu") else w for w in words.split(" "))
    return words[:1].upper() + words[1:]


def _fmt(value, key: str = "") -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)) and re.search(r"cik|sic|year|number|_id$|^id$", str(key).lower()):
        return str(value)                                # identifiers: no thousands separators
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            return f"{value:,.2f}"
        return f"{int(value):,}" if abs(value) >= 10000 else str(int(value))
    text = str(value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?", text):
        return text[:10]
    if text.startswith("http"):
        return f"[open link]({text})"
    return text.replace("|", "\\|").replace("$", "\\$").replace("\n", " ")


def _scalar(v) -> bool:
    return not isinstance(v, (dict, list))


def _table(headers: list, rows: list, limit: int = MAX_ROWS) -> None:
    shown = rows[:limit]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(r) + " |" for r in shown]
    st.markdown("\n".join(lines))
    if len(rows) > limit:
        st.caption(f"Showing the first {limit} of {len(rows)} rows.")


def _show(obj, title: str = "", depth: int = 0) -> None:
    """Print a tool result as headings and tables. Nothing is added or summarised: every value shown is
    in the result; only the plumbing fields in HIDE are left out."""
    if title:
        st.markdown(f"{'#' * min(5 + depth, 6)} {_label(title)}" if depth else f"**{_label(title)}**")
    if isinstance(obj, list):
        if not obj:
            st.markdown("*Nothing returned (an empty list).*")
        elif all(isinstance(x, dict) for x in obj):
            cols = [k for k in dict.fromkeys(k for x in obj for k in x) if k not in HIDE
                    and any(_scalar(x.get(k)) and x.get(k) not in (None, "") for x in obj)]
            _table(["#"] + [_label(c) for c in cols],
                   [[str(i)] + [_fmt(x.get(c), c) if _scalar(x.get(c)) else "…" for c in cols] for i, x in enumerate(obj, 1)])
        else:
            st.markdown(", ".join(_fmt(x) for x in obj[:60]))
        return
    if not isinstance(obj, dict):
        st.markdown(_fmt(obj))
        return
    items = {k: v for k, v in obj.items() if k not in HIDE}
    scalars = [(k, v) for k, v in items.items() if _scalar(v)]
    if scalars:
        _table(["Field", "Value"], [[_label(k), _fmt(v, k)] for k, v in scalars])
    for k, v in items.items():
        if _scalar(v):
            continue
        # {"statements": {"income_statement": {"data": {...}}}} → one heading "Statements › Income statement › Data"
        while isinstance(v, dict):
            inner = {a: b for a, b in v.items() if a not in HIDE}
            if len(inner) != 1 or _scalar(next(iter(inner.values()))):
                break
            sub, v = next(iter(inner.items()))
            k = f"{_label(k)} › {_label(sub)}"
        # {"NetIncomeLoss": {"value": …, "period": …}, …} reads best as one table, a row per item
        if isinstance(v, dict) and v and all(isinstance(x, dict) and all(_scalar(y) for y in x.values()) for x in v.values()):
            cols = [c for c in dict.fromkeys(c for x in v.values() for c in x) if c not in HIDE]
            st.markdown(f"**{_label(k)}**")
            _table(["Item"] + [_label(c) for c in cols],
                   [[_label(name)] + [_fmt(x.get(c), c) for c in cols] for name, x in v.items()])
        elif isinstance(v, dict) and not v:
            st.markdown(f"**{_label(k)}:** *nothing returned*")
        elif depth < 4:
            _show(v, k, depth + 1)


def _result(call: dict) -> None:
    parsed = call["parsed"]
    if call["status"] != "ok":
        if isinstance(parsed, dict) and "errorCategory" in parsed:        # the laptop server's structured error
            st.error(f"The tool refused or failed — **{parsed['errorCategory']}** error, "
                     f"{'worth retrying' if parsed.get('isRetryable') else 'retrying will not help'}: "
                     f"{parsed.get('message', '')}")
        else:
            reason = parsed.get("error") if isinstance(parsed, dict) else call["text"]
            st.error(f"The tool failed: {str(reason)[:500]}")
    elif parsed is None:
        st.text(call["text"][:3000] or "(the tool returned nothing)")
    else:
        _show(parsed)


def _money(text) -> str:
    return str(text).replace("$", "\\$")


def _cell(text) -> str:
    return str(text).replace("|", "\\|").replace("$", "\\$").replace("\n", " ")


def _web_cell(call: dict) -> tuple:
    """(request type, what, outcome) for the web row of one tool call — taken from the server's own log."""
    counts: dict = {}
    for h in call.get("http", []):
        counts[(h["method"], h["url"], h["status"])] = counts.get((h["method"], h["url"], h["status"]), 0) + 1
    whats, outcomes, kinds = [], [], []
    for (method, url, status), n in counts.items():
        times = f" ×{n}" if n > 1 else ""
        if str(url).startswith("http"):
            host = url.split("//", 1)[-1].split("/", 1)[0]
            whats.append(f"[{host}/…/{url.rsplit('/', 1)[-1]}]({url}){times}")
            outcomes.append(f"HTTP {status}")
            kinds.append(f"HTTP {method}")
        else:
            whats.append("Public web search engine" + times)
            outcomes.append(str(status))
            kinds.append("Web search")
    total = len(call.get("http", []))
    kind = " + ".join(dict.fromkeys(kinds)) + (f" ×{total}" if total > 1 else "")
    good = all(o in ("HTTP 200",) or "results" in o for o in outcomes)
    return kind, " · ".join(whats), ("✅ " if good else "⚠️ ") + ", ".join(dict.fromkeys(outcomes))


def _flow(run: dict) -> None:
    """One table, in the order things happened: every model call, tool call and sec.gov request."""
    calls, rows = run["calls"], []

    def add(step, kind, what, outcome, ms=None):
        rows.append([str(len(rows) + 1), step, kind, what, outcome, f"{ms / 1000:.1f} s" if ms is not None else "—"])

    add("🙋 You asked", "—", _cell(run["question"]), "—")
    for srv in run["servers"].values():
        if srv["transport"] == "http":
            add(f'🔌 Connect to `{srv["label"]}`', "MCP over **HTTP** · `initialize` + `tools/list`",
                f'Open {srv["url"]} — the server was already running; this app did not start it',
                f'{srv["tools"]} tools offered', srv["connect_ms"])
        else:
            add(f'🔌 Start `{srv["label"]}`', "MCP over **stdio** · `initialize` + `tools/list`",
                "Launch the server as a child process of this app and talk over its stdin / stdout",
                f'{srv["tools"]} tools offered', srv["connect_ms"])
    if run.get("prompt_used"):
        pu = run["prompt_used"]
        add(f'📝 Prompt `{pu["name"]}`', "MCP · `prompts/get`  (YOU chose it)",
            "Blanks filled: " + (", ".join(f"{k} = {_cell(v)}" for k, v in pu["arguments"].items()) or "none"),
            "The server returned the question text", pu.get("ms"))
    for a in run.get("attached", []):
        add("📎 Resource", "MCP · `resources/read`  (the APP chose it)", f'`{a["uri"]}`',
            f'{len(a["text"]):,} characters added to the model\'s context', a["ms"])
    for m in run["model_calls"]:
        asked = ", ".join(f'`{f["name"]}`' for f in m["function_calls"])
        add(f'🧠 Model call {m["turn"]}', "Model request (Gemini)",
f'Question + all {len(run["tools"])} tools from {len(run["servers"])} server{"s" if len(run["servers"]) != 1 else ""}'
            if m["turn"] == 1 else "Everything so far + the tool result",
            f"Chose tool {asked}" if asked else ("Finished gathering" if m["text"].strip() else "⚠️ Empty reply"), m["ms"])
        for c in (c for c in calls if c.get("turn") == m["turn"]):
            sent = ", ".join(f"{_label(k)} = {_cell(v)}" for k, v in c["args"].items()) or "nothing"
            via = "HTTP POST" if run["servers"].get(c["server"], {}).get("transport") == "http" else "stdio"
            add(f'🛠️ Tool `{c["tool"]}`', f"MCP · `tools/call` ({via})", f"Sent: {sent}",
                "✅ Result returned" if c["status"] == "ok" else f'⚠️ {c["status"]}', c["ms"])
            for note in (n for n in c.get("notes", []) if n["kind"] == "elicitation"):
                add("❓ The server asked you", "MCP · `elicitation/create`  (server → client)", _cell(note["text"]),
                    "You answered: **" + ("approve" if note["answer"] == "accept" else "decline") + "**")
            logs = [n for n in c.get("notes", []) if n["kind"] == "log"]
            if c.get("progress") or logs:
                add("📣 Notifications", "MCP · `notifications/progress` + `message`  (server → client)",
                    f'{c.get("progress", 0)} progress update{"s" if c.get("progress", 0) != 1 else ""}'
                    + (f' (last: {_cell(c["progress_last"])})' if c.get("progress_last") else "")
                    + (" · log: " + " / ".join(_cell(n["text"]) for n in logs[:2]) if logs else ""),
                    "Shown to you, never sent to the model")
            if c.get("http"):
                kind, what, outcome = _web_cell(c)
                add("🌐 Web", kind, what, outcome)
            else:
                add("🌐 Web", "none", "Not contacted (no web request in the server's log)", "—")
    syn = run.get("synthesis")
    if syn:
        kinds = ", ".join(c["chart_type"].replace("_", " ") for c in syn.get("charts", []))
        add("🧪 Synthesis agent", "Model request (Gemini, no tools)",
            f"The question + all {len(calls)} tool result{'s' if len(calls) != 1 else ''}",
            "⚠️ Reply did not match the schema" if syn.get("error")
            else "Wrote the curated answer; " + (f"chose chart type: {kinds}" if kinds else "chose no chart"), syn["ms"])
    _table(["#", "Step", "Request type", "What", "Outcome", "Time"], rows, limit=200)
    total_s = run["events"][-1]["at_ms"] / 1000 if run["events"] else 0
    st.caption(f'Totals: {len(calls)} tool call{"s" if len(calls) != 1 else ""} · '
               f'{sum(len(c.get("http", [])) for c in calls)} web requests · {len(run["model_calls"]) + (1 if syn else 0)} model calls · '
               f"{total_s:.1f} s. The web rows sit inside the tool call above them, so they have no separate time.")

    if calls:
        st.markdown("#### What each tool returned")
    for i, c in enumerate(calls, 1):
        with st.container(border=True):
            st.markdown(f'**{i}. `{c["tool"]}`** · from `{run["servers"].get(c["server"], {}).get("label", "?")}`')
            _result(c)


def _details(run: dict) -> None:
    with st.expander("🔬 Details — sequence diagram, tokens, raw JSON"):
        t1, t2, t3, t4 = st.tabs(["Sequence diagram", "Model calls and tokens", "Raw JSON from the server",
                                  "Synthesis agent"])
        with t4:
            syn = run.get("synthesis")
            if not syn:
                st.markdown("The synthesis agent did not run (no tool returned data).")
            else:
                st.caption(f'A second model call with its own prompt and no tools · {syn["in_tokens"]} tokens in · '
                           f'{syn["out_tokens"]} out · {syn["ms"]} ms. It sees only the question and the tool results.')
                st.markdown("**Its system prompt (exact)**")
                st.code(syn["prompt"], language="text")
                st.markdown("**Its reply (JSON, constrained by a schema)**")
                st.code(syn["raw"][:8000], language="json")
                st.markdown("**What the research agent said before handing over**")
                st.code(run["answer"] or "(nothing)", language="text")
        with t1:
            st.image(run["seq_png"], width="stretch")
            st.caption("Drawn from this run's own event log.")
        with t2:
            st.caption(f'Model `{run["model"]}` · function-calling mode AUTO (Claude: `tool_choice: "auto"`)')
            rows = [[str(m["turn"]), m["finish_reason"], f'`{m["claude_term"]}`',
                     ", ".join(f["name"] for f in m["function_calls"]) or "— (text)",
                     str(m["in_tokens"]), str(m["out_tokens"]), str(m["ms"])] for m in run["model_calls"]]
            _table(["Turn", "Finish reason", "Claude term", "Tool asked for", "In tokens", "Out tokens", "ms"], rows)
            st.markdown("**System prompt (exact)**")
            st.code(run["system_prompt"], language="text")
        with t3:
            if not run["calls"]:
                st.markdown("No tool was called.")
            for i, c in enumerate(run["calls"], 1):
                st.markdown(f'**{i}. `{c["tool"]}` — {c["status"]} · isError={c["is_error"]}**')
                st.code(c["text"][:8000] or "(empty)", language="json")


def _answer(run: dict) -> None:
    syn = run.get("synthesis")
    if not syn or syn.get("error"):
        if syn:
            st.warning(syn["error"] + " Showing the research agent's own words instead.")
        with st.container(border=True):
            st.markdown("ℹ️ **Reply from the research agent** — no tool returned data, so there was nothing to "
                        "summarise or chart." if not syn else "**Reply from the research agent**")
            st.markdown(_money(run["answer"]))
        return
    with st.container(border=True):
        st.markdown("✅ **Answer** — written by the synthesis agent from the tool results")
        st.markdown(f"#### {_money(syn['headline'])}")
        st.markdown(_money(syn["summary"]))
        if syn["key_points"]:
            st.markdown("**Key points**")
            st.markdown("\n".join(f"- {_money(k)}" for k in syn["key_points"]))
        if syn["caveats"]:
            st.markdown("**⚠️ Read before comparing**")
            st.markdown("\n".join(f"- {_money(k)}" for k in syn["caveats"]))
    for n, chart in enumerate(syn["charts"], 1):
        with st.container(border=True):
            left, right = st.columns([3, 2])
            with left:
                st.image(mcp_charts.chart_png(chart))
            with right:
                st.markdown(f"**Chart {n} — the model chose: {chart['chart_type'].replace('_', ' ')}**")
                st.markdown(f"*Why:* {_money(chart['why_this_chart'])}")
                rows = [[_cell(s["name"]), _cell(pt["label"]), f"{pt['value']:,.2f}".rstrip("0").rstrip("."),
                         f"call {pt['source_call']} · `{run['calls'][pt['source_call'] - 1]['tool']}`"
                         if 1 <= pt["source_call"] <= len(run["calls"]) else "—",
                         "✅" if pt["check"] == "ok" else f"⚠️ {pt['check']}"]
                        for s in chart["series"] for pt in s["points"]]
                _table(["Series", "Label", "Value", "From", "In the tool result?"], rows)
                if len(chart["series"]) > mcp_charts.MAX_SERIES:
                    st.caption(f"The chart draws the first {mcp_charts.MAX_SERIES} series; the table lists all of them.")
    if syn["charts"]:
        st.caption("The model chose each chart type and supplied the numbers. The page then looks for every number in "
                   "the tool result it cites: ✅ found, ⚠️ not found (drawn hatched).")


def _render(run: dict) -> None:
    if run.get("error"):
        st.error(run["error"])
        return
    if run["stopped"] == "end_turn":
        _answer(run)
    elif run["stopped"] == "empty_reply":
        st.error("The model kept returning an empty reply, so there is no answer. Ask again.")
    else:
        st.error(f"Stopped after {mcp_live.MAX_TURNS} model calls without an answer. This is a failure, not a result.")
    st.markdown("#### What happened, step by step")
    _flow(run)
    _details(run)


FEATURES = (
    # feature, who controls it, protocol calls, local server, hosted server
    ("Tools", "The MODEL — it decides when to call one", "`tools/list`, `tools/call`",
     "9 tools", "21 tools (the community package's)"),
    ("Resources", "The APPLICATION — it decides what to read and attach", "`resources/list`, `resources/read`",
     "3: folder catalogue, clean-up policy, notes", "2: ticker list, form types"),
    ("Resource templates", "The APPLICATION — one definition, many URIs", "`resources/templates/list`, `resources/read`",
     "`laptop://drive/{letter}`", "`edgar://company/{ticker}`"),
    ("Prompts", "The USER — you pick one and fill its blanks", "`prompts/list`, `prompts/get`",
     "3: health check, clean-up plan, can it run", "3: compare companies, latest filing, insider activity"),
    ("Progress and log notifications", "The SERVER sends them while a slow tool runs", "`notifications/progress`, `notifications/message`",
     "`get_folder_sizes`, `summarize_file_types`", "— not used"),
    ("Elicitation", "The SERVER asks the user a question mid-call", "`elicitation/create`",
     "`save_note` asks before it writes", "— not used"),
    ("Tool annotations", "The SERVER hints: read-only? touches the outside world?", "a field in `tools/list`",
     "On every tool", "— the package sets none"),
    ("Sampling, roots, subscriptions, list-changed, completion", "—", "—",
     "Not built", "Not built"),
)


def _first_sentence(text: str) -> str:
    line = " ".join(text.split("\n\n")[0].split())
    return (line.split(". ")[0].rstrip(".") + ".") if line else "—"


def _show_resource(res: dict) -> None:
    text, mime = res["text"], res["mime"]
    st.caption(f'`resources/read {res["uri"]}` → {mime or "text"} · {len(text):,} characters · {res["ms"]} ms')
    if "csv" in mime:
        rows = list(csv.reader(io.StringIO(text)))
        if rows:
            _table(["#"] + [_label(h) for h in rows[0]], [[str(i)] + [_fmt(v) for v in r] for i, r in enumerate(rows[1:], 1)], limit=60)
    elif "json" in mime:
        try:
            _show(json.loads(text))
        except ValueError:
            st.text(text[:3000])
    elif "markdown" in mime:
        st.markdown(_money(text))
    else:
        st.text(text[:3000])


def _offers(kind: str) -> dict | None:
    """'What this server offers': everything the server lists, tabulated. Returns the catalogue (or None)."""
    cfg = PAGES[kind]
    key = f"mcp_catalog_{kind}"
    top = st.columns([5, 1])
    top[0].subheader("What this server offers")
    if top[1].button("Refresh", key=f"mcp_refresh_{kind}"):
        st.session_state.pop(key, None)
    if key not in st.session_state:
        try:
            with st.spinner("Asking the server what it offers (tools, resources, prompts)…"):
                st.session_state[key] = mcp_live.catalog(cfg["server"])
        except Exception as exc:                                   # show it — never hide a failure
            st.error(f"Could not list what the server offers: {type(exc).__name__}: {exc}")
            return None
    cat = st.session_state[key]
    tools, resources, templates, prompts = cat["tools"], cat["resources"], cat["templates"], cat["prompts"]
    t1, t2, t3, t4 = st.tabs([f"🛠️ Tools ({len(tools)})", f"📚 Resources ({len(resources) + len(templates)})",
                              f"📝 Prompts ({len(prompts)})", "🧩 All MCP features"])
    with t1:
        st.caption("**The model decides** when to call a tool. All it reads is the name and description below.")
        yes_no = {True: "No, read-only", False: "**Yes**", None: "not stated"}
        web = {True: "Yes", False: "No", None: "not stated"}
        _table(["#", "Tool", "What it does", "Inputs", "Changes anything?", "Reaches outside this PC?"],
               [[str(i), f'`{t["name"]}`', _cell(_first_sentence(t["description"])),
                 ", ".join(f"`{a}`" for a in t["inputSchema"].get("properties", {})) or "none",
                 yes_no[t.get("read_only")], web[t.get("open_world")]] for i, t in enumerate(tools, 1)], limit=60)
        if kind == "hosted":
            st.caption("\"Not stated\": the community package sets no annotations, so a client cannot tell from the "
                       "tool list which tools are safe. On the local page every tool states both.")
    with t2:
        st.caption("**The application decides** which resources to read and hand to the model. A resource is data to "
                   "read — it never acts. Attach one in the question form below.")
        _table(["#", "URI", "Name", "Type", "What it holds"],
               [[str(i), f'`{r["uri"]}`', _cell(r["name"]), r["mime"] or "—", _cell(r["description"])]
                for i, r in enumerate(resources, 1)]
               + [[str(len(resources) + i), f'`{t["uri"]}`', _cell(t["name"]) + " *(template)*", t["mime"] or "—",
                   _cell(t["description"])] for i, t in enumerate(templates, 1)])
        example = "laptop://drive/C" if kind == "local" else "edgar://company/AAPL"
        with st.form(f"mcp_read_{kind}"):
            uri = st.selectbox("Read a resource now", [r["uri"] for r in resources] + [example], key=f"mcp_read_uri_{kind}")
            custom = st.text_input("…or type a URI that fits the template", placeholder=example)
            go = st.form_submit_button("Read it  (resources/read)")
        if go:
            try:
                st.session_state[f"mcp_res_{kind}"] = mcp_live.read_resource(cfg["server"], custom.strip() or uri)
            except Exception as exc:
                st.session_state.pop(f"mcp_res_{kind}", None)
                st.error(f"{type(exc).__name__}: {exc}")
        if st.session_state.get(f"mcp_res_{kind}"):
            _show_resource(st.session_state[f"mcp_res_{kind}"])
    with t3:
        st.caption("**You decide** to use a prompt. It is a ready-made question written by the server's author; you "
                   "fill in the blanks. Choose one in the question form below.")
        _table(["#", "Prompt", "What it asks for", "Blanks to fill"],
               [[str(i), f'`{q["name"]}`', _cell(q["description"]),
                 ", ".join(f'`{a["name"]}`' + ("" if a["required"] else " (optional)") for a in q["arguments"]) or "none"]
                for i, q in enumerate(prompts, 1)])
    with t4:
        mine, theirs = ("On this server (local)", "On the hosted server") if kind == "local" else \
                       ("On this server (hosted)", "On the local server")
        cols = (3, 4) if kind == "local" else (4, 3)
        _table(["#", "MCP feature", "Who controls it", "Protocol calls", mine, theirs],
               [[str(i), f"**{f[0]}**", f[1], f[2], f[cols[0]], f[cols[1]]] for i, f in enumerate(FEATURES, 1)])
        st.caption("The first three rows are the server features in the MCP docs, with the docs' own answer to \"who "
                   "controls it\". The current MCP docs mark sampling and logging as deprecated; this workbench's SDK "
                   "still supports logging, and the local server uses it.")
    return cat


def _parse_blanks(text: str) -> dict:
    """'folder=Downloads; days=30' → {'folder': 'Downloads', 'days': '30'}"""
    out = {}
    for part in re.split(r"[;\n]", text or ""):
        if "=" in part:
            k, v = part.split("=", 1)
            if k.strip():
                out[k.strip()] = v.strip()
    return out


def _setup(kind: str) -> bool:
    """Show only what is missing. Returns False when the page cannot run."""
    status = mcp_live.setup_status()
    problems = []
    if not status["mcp_sdk"]:
        problems.append("**The MCP package is not installed.** Run `uv pip install -r requirements.txt`, then restart "
                        "the app.")
    if not status["gemini_key"]:
        problems.append("**`GEMINI_API_KEY` is not set.** The model that chooses the tool needs it. On your PC put it "
                        "in `.env`; on the hosted copy add it under the app's Settings → Secrets.")
    ready, why = mcp_live.server_ready(PAGES[kind]["server"])
    if not ready:
        problems.append(f"**This page's server is not available:** {why}."
                        + (" Run `uv pip install -r requirements-mcp.txt`." if "installed" in why else ""))
    for p in problems:
        st.error(p)
    if problems:
        st.info("The rest of the app works without these.")
        return False
    if kind == "local" and not status["search_pkg"]:
        st.warning("The `ddgs` package is not installed, so the `web_search` tool will report a failure. "
                   "Run `uv pip install -r requirements-mcp.txt`.")
    return True


def _service_box() -> bool:
    """The hosted page only: the separate service must be running. Starting it here plays the provider's part."""
    running = mcp_live.service_running()
    with st.container(border=True):
        left, right = st.columns([4, 1])
        with left:
            if running:
                st.markdown(f"🟢 **The hosted server is running** at `{mcp_live.SEC_URL}`.")
            else:
                st.markdown(f"🔴 **Nothing is running** at `{mcp_live.SEC_URL}`. A client cannot start a server that "
                            "someone else hosts — start the service first.")
            st.caption("The SEC does not host an MCP server. This is the community `sec-edgar-mcp` program, run as "
                       "its own service on this PC (reachable only from this PC) to stand in for a provider's "
                       "hosting. The client code is the same as for a real remote URL.")
        with right:
            if running:
                if st.button("Stop the service"):
                    st.session_state.pop("mcp_catalog_hosted", None)
                    mcp_live.stop_service()
                    st.rerun()
            elif st.button("Start the service", type="primary"):
                try:
                    with st.spinner("Starting the service…"):
                        mcp_live.start_service()
                except Exception as exc:                           # show it — never hide a failure
                    st.error(f"{type(exc).__name__}: {exc}")
                    return False
                st.rerun()
    return running


def render(kind: str) -> None:
    cfg = PAGES[kind]
    other = PAGES[cfg["other"]]
    st.set_page_config(page_title=f'{cfg["num"]} — {cfg["title"]}', page_icon=cfg["icon"], layout="wide")
    st.markdown("<style>table { font-size:0.95rem; }</style>", unsafe_allow_html=True)
    st.title(f'{cfg["icon"]} {cfg["title"]}')
    st.caption(cfg["caption"] + "  ·  ➕ Extra: not on the CCAR-F exam  ·  Live data, not investment advice")
    if not _setup(kind):
        return
    if kind == "local" and platform.system() != "Windows":
        st.warning("**You are on the hosted copy of this app.** The server below is started on the machine the app "
                   "runs on, so \"this computer\" means that hosted Linux machine — not your laptop. To see your own "
                   "laptop's details, run the app on your PC (http://localhost:8501).")

    # ── the setup: schematic + sequence diagram + the difference ──
    st.subheader("How this setup works")
    left, right = st.columns([2, 3])
    with left:
        st.markdown("**Schematic — where each part runs**")
        st.graphviz_chart(SCHEMATIC[kind])
    with right:
        st.markdown("**Sequence — who talks to whom, in order**")
        st.image(mcp_seq.sequence_png(mcp_seq.canonical_events(kind), cfg["seq_title"], kind), width="stretch")
    mine, theirs = ("Hosted separately — this page", "Local, my own — the other page") if kind == "hosted" else \
                   ("Local, my own — this page", "Hosted separately — the other page")
    order = (1, 2) if kind == "hosted" else (2, 1)
    with st.expander(f'What is different from {other["num"]} ({other["title"]})', expanded=True):
        _table(["#", "", mine, theirs],
               [[str(n), f"**{row[0]}**", row[order[0]], row[order[1]]] for n, row in enumerate(COMPARE, 1)])
        st.caption("*On the hosted page the stand-in service runs on your PC, so the page can read its log to show the "
                   "sec.gov requests. With a server hosted by someone else you would not see those.")
        pages = st.session_state.get("_mcp_pages", {})
        if cfg["other"] in pages:
            st.page_link(pages[cfg["other"]], label=f'Open {other["num"]} — {other["title"]}', icon=other["icon"])

    st.markdown("---")
    if kind == "hosted" and not _service_box():
        return
    cat = _offers(kind)
    if cat is None:
        return

    st.markdown("---")
    st.subheader("Try it")
    # One question at a time: pressing Ask wipes the previous result, and nothing is remembered between questions.
    state_key = f"mcp_run_{kind}"
    prompts = {q["name"]: q for q in cat["prompts"]}
    with st.form(f"mcp_ask_{kind}", clear_on_submit=True):
        typed = st.text_input("Your question", placeholder=cfg["placeholder"])
        picked = st.selectbox("…or pick an example", ("",) + cfg["examples"], key=f"mcp_example_{kind}")
        left, right = st.columns(2)
        with left:
            prompt_name = st.selectbox("…or use one of the server's prompts (you choose)", [""] + list(prompts),
                                       key=f"mcp_prompt_{kind}",
                                       format_func=lambda n: "—" if not n else f'{n}  (blanks: '
                                       + (", ".join(a["name"] for a in prompts[n]["arguments"]) or "none") + ")")
            blanks = st.text_input("Fill the prompt's blanks", placeholder="name=value; name=value",
                                   key=f"mcp_blanks_{kind}")
        with right:
            attach = st.multiselect("Attach resources (the app adds them to the model's context)",
                                    [r["uri"] for r in cat["resources"]], key=f"mcp_attach_{kind}")
            confirm = "decline"
            if kind == "local":
                confirm = "accept" if st.radio("If the server asks me to confirm (save_note does)",
                                               ("Decline", "Approve"), horizontal=True,
                                               key="mcp_confirm_local") == "Approve" else "decline"
        submitted = st.form_submit_button("Ask", type="primary")
    question, prompt_used = ((typed.strip() or picked) if submitted else ""), None
    if submitted and prompt_name:
        args = _parse_blanks(blanks)
        missing = [a["name"] for a in prompts[prompt_name]["arguments"] if a["required"] and a["name"] not in args]
        if missing:
            st.warning(f"The prompt `{prompt_name}` needs: " + ", ".join(f"`{m}=…`" for m in missing))
            question = ""
        else:
            try:
                got = mcp_live.get_prompt(cfg["server"], prompt_name, args)
                question, prompt_used = got["text"], {"name": prompt_name, "arguments": args}
            except Exception as exc:
                st.error(f"prompts/get failed: {type(exc).__name__}: {exc}")
                question = ""
    elif submitted and not question:
        st.warning("Type a question, pick an example, or choose a prompt first.")

    slot = st.empty()                                  # the previous result lives here; emptied on a new Ask
    if question:
        st.session_state.pop(state_key, None)
        with slot.container():
            try:
                with st.spinner("The model is choosing a tool · gathering data · writing the answer… (10 to 20 seconds)"):
                    run = mcp_live.ask(question, servers=[cfg["server"]], confirm=confirm, prompt_used=prompt_used,
                                       attach=[(cfg["server"], u) for u in attach])
                    run["seq_png"] = mcp_seq.sequence_png(run["events"], "What actually happened", kind)
            except Exception as exc:                               # show the real error — no silent fallback
                run = {"question": question, "error": f"{type(exc).__name__}: {exc}"}
        st.session_state[state_key] = run

    run = st.session_state.get(state_key)
    with slot.container():
        if run:
            st.markdown(f"### {_cell(run['question'])}")
            _render(run)

    with st.expander("ℹ️ About this page"):
        common = """
- **Who chooses the tool?** The model. It reads each tool's description and picks one; the MCP client only carries
  the request and the result. *(On the exam: tool descriptions drive tool selection — TS 2.1.)*
- **Two agents.** A *research agent* chooses and calls the tools. A *synthesis agent* with no tools then writes the
  answer and chooses any chart from the question and the tool results alone. *(On the exam: a subagent's context
  is passed in, not inherited — TS 1.3.)*
- **Is the result changed?** No. The tables print the values the tool returned; the untouched JSON is under Details.
- **The model** is Gemini here; the Claude terms are shown beside it under Details. No API key is passed to a server.
"""
        if kind == "hosted":
            st.markdown("""
- **Is this server hosted by the SEC?** No. The SEC publishes data, not an MCP server. `sec-edgar-mcp` is a
  community program; here it runs as a separate service on this PC, listening only on `127.0.0.1`.
- **How do you know when sec.gov was contacted?** The page reads the stand-in service's log. That is only possible
  because the service runs on your PC.""" + common)
        else:
            st.markdown("""
- **The server is yours:** `mcp_servers/laptop_server.py`. Change a tool's description there and ask the same
  question again to see the choice change.
- **Privacy.** Whatever a tool returns is sent to the model (Google's Gemini). The server never returns the
  computer name, user name, serial numbers, network addresses or file contents, and it only looks inside your home
  folder — but hardware details and folder names it does return leave this PC that way.
- **Web search results are unverified** text from third-party sites; the answer says so.""" + common)
