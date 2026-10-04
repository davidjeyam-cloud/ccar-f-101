"""
LIVE MCP client + agents for the live MCP pages D2.3.1 / D2.3.2 (utils/mcp_page.py).

Unlike utils/mcp_lab.py (SIMULATED), everything here is real:
- real MCP servers spoken to with the official `mcp` Python SDK — ONE client session per server —
  in the two ways a server can be reached:
    "laptop"  LOCAL, stdio: mcp_servers/laptop_server.py, the workbench's own server (hardware, storage,
              web search). The client starts it as a child process and talks over its stdin/stdout.
    "sec"     HOSTED SEPARATELY, Streamable HTTP: the community `sec-edgar-mcp` package (not
              SEC-affiliated; the SEC hosts no MCP server). It runs as its own service and the client
              only knows its URL. Here the service runs on this PC (bound to 127.0.0.1) to stand in for
              a provider's hosting — start_service() / stop_service() play the provider's role;
- real models — Gemini (utils/llm.MODEL). A research agent chooses tools from the descriptions the
  servers returned in tools/list (all servers' tools are offered together); a synthesis agent with no
  tools then writes the answer and chooses the charts. The Claude term is recorded beside each
  Gemini one.

It is an ➕ extra: building a client or a server is not on the CCAR-F exam. What the exam does test,
and what a run makes visible: the model picks a tool from its description (TS 2.1); a failure must be
flagged as one (TS 2.2); tools from every configured server are available together (TS 2.4); a
subagent gets its context passed in, not inherited (TS 1.3); figures keep their source (TS 5.6).

Optional dependencies (requirements-mcp.txt). Nothing here is imported at app start, so the app runs
without them.

One set of sessions per question: connect → initialize → tools/list → agent loop → close. Slower
than keeping servers alive, but each run shows the whole lifecycle and nothing is left running
between Streamlit reruns.
"""

from __future__ import annotations

import asyncio
import contextlib
import importlib.util
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MAX_TURNS = 12                # guard only — hitting it is reported as a failure, never as success
RESULT_CAP = 6000             # characters of a tool result passed to the model (the full text stays in the trace)
CALL_TIMEOUT_S = 60
MODEL_TIMEOUT_MS = 45_000     # a model request that has not answered by then is abandoned and reported
SYNTH_MAX_TOKENS = 4000       # caps the synthesis reply, so a runaway reply ends instead of running on
EMPTY_RETRIES = 2             # an empty model reply is retried this many times, then reported as a failure
UA_ENV = "SEC_EDGAR_USER_AGENT"
LAPTOP_SERVER = Path(__file__).resolve().parent.parent / "mcp_servers" / "laptop_server.py"
EDGAR_SERVER = LAPTOP_SERVER.with_name("edgar_hosted_server.py")
RESOURCE_CAP = 6000           # characters of an attached resource passed to the model
_SECRET_NAME = re.compile(r"API_KEY|TOKEN|SECRET|PASSWORD", re.I)

# Each server is started through a one-liner that turns on urllib3's connection log first, so web
# requests made with the `requests` library are logged too. The servers' own code is not changed.
_LOG_ON = "import logging; logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG); "
SEC_HOST, SEC_PORT = "127.0.0.1", 9870        # loopback only: the stand-in service is never exposed to the network
SEC_URL = f"http://{SEC_HOST}:{SEC_PORT}/mcp"
SVC_LOG = Path(tempfile.gettempdir()) / "ccarf_sec_edgar_service.log"
SVC_PID = Path(tempfile.gettempdir()) / "ccarf_sec_edgar_service.pid"
SERVERS = {
    "laptop": {
        "label": "my-laptop", "transport": "stdio",
        "about": "my own server: this computer's hardware and storage, and web search",
        "launch": _LOG_ON + f"import runpy; runpy.run_path(r'{LAPTOP_SERVER}', run_name='__main__')",
    },
    "sec": {
        "label": "sec-edgar", "transport": "http", "url": SEC_URL,
        "about": "community tools for US company filings (sec.gov), plus this workbench's resources and prompts",
        "launch": _LOG_ON + f"import sys, runpy; sys.argv = ['edgar_hosted_server', '--host', '{SEC_HOST}', "
                            f"'--port', '{SEC_PORT}']; runpy.run_path(r'{EDGAR_SERVER}', run_name='__main__')",
    },
}

SYSTEM_PROMPT = (
    "You are the research agent. You gather facts using ONLY the tools provided. The tools come from one or more\n"
    "MCP servers: tools about this computer (hardware, storage, folders), a web search tool, and SEC EDGAR tools\n"
    "about US-listed companies. Not every server is connected every time.\n"
    "- Choose the tool whose description fits the question. Use the computer tools for questions about this\n"
    "  computer, the SEC tools for company filings, and web search only for facts those tools cannot give.\n"
    "- A question can need more than one tool, e.g. read the hardware, then search the web about that part.\n"
    "- For SEC tools, resolve a company name to a ticker or CIK with a tool before using other tools. For a\n"
    "  comparison, gather the same data for EVERY company named, with the same tool and settings for each.\n"
    "- If a tool returns an error or no data, say so plainly. Never fill a gap from memory.\n"
    "- When you have the data, reply in one or two sentences saying what you gathered. A separate synthesis agent\n"
    "  writes the final answer from the tool results, so do not write a long answer yourself.\n"
    "- Attached resources, when present, are reference data the application chose to give you (a ticker list, a\n"
    "  folder catalogue, a policy). Use them instead of guessing or searching for the same facts.\n"
    "- Only call a tool that saves or changes something when the user asked for that.\n"
    "- If these tools cannot answer the question, say that in one sentence."
)

SYNTHESIS_PROMPT = (
    "You are the synthesis agent. You receive a user's question and the results of tool calls that a research\n"
    "agent gathered (about this computer, from web search, or from SEC EDGAR filings). You did not see that\n"
    "agent's conversation: everything you know is in this message.\n"
    "Rules:\n"
    "- Use ONLY the tool results and any attached resources. Never add a fact or figure from memory. If something needed is missing or a\n"
    "  tool failed, say so in caveats.\n"
    "- headline: one sentence that answers the question.\n"
    "- summary: 2 to 5 short sentences in plain words. Give each figure with its unit, and with its period and\n"
    "  form type when it comes from a filing.\n"
    "- key_points: 2 to 5 bullets. Each is one fact with its figure, ending with its call number like [call 2].\n"
    "- caveats: data gaps, failed tools, partial results, and mismatches. If companies' figures cover different\n"
    "  periods or form types (a 10-K year against a 10-Q quarter), say so: they are not like-for-like. If a fact\n"
    "  comes from a web search snippet, say it is unverified web text.\n"
    "- charts: add a chart only when two or more comparable numbers exist. At most 3 charts. Choose\n"
    "  chart_type by the job the chart does:\n"
    "    bar          = compare ONE measure across companies or items. One series named after the measure;\n"
    "                   one point per item.\n"
    "    grouped_bar  = compare 2 to 4 measures across items. One series per measure; one point per item.\n"
    "    line         = one measure over 3 or more time periods. One series per item; one point per period,\n"
    "                   oldest first.\n"
    "    stacked_bar  = parts that add up to a whole (used and free space, for example). One series per part;\n"
    "                   one point per item.\n"
    "  One scale per chart: never put values of very different size or unit in one chart (revenue and earnings\n"
    "  per share, for example). Make a second chart instead. No chart for a single number or for text.\n"
    "- Chart values: copy each value exactly as the number in the tool result (78678000000, not 78.7), and set\n"
    "  source_call to the call number it came from. y_label names the unit, e.g. USD or GB.\n"
    "- why_this_chart: one sentence saying why this chart type fits this data."
)


# ── setup checks ─────────────────────────────────────────────────────────────
def setup_status() -> dict:
    """What is installed / configured. Only checks presence — never returns a secret value."""
    return {
        "mcp_sdk": importlib.util.find_spec("mcp") is not None,
        "gemini_key": bool(os.getenv("GEMINI_API_KEY")),
        "server_pkg": importlib.util.find_spec("sec_edgar_mcp") is not None,
        "sec_contact": bool(os.getenv(UA_ENV)),
        "search_pkg": importlib.util.find_spec("ddgs") is not None,
        "laptop_server": LAPTOP_SERVER.exists(),
    }


def server_ready(key: str) -> tuple:
    """(ready, reason it is not) for one server."""
    s = setup_status()
    if key == "laptop":
        return (True, "") if s["laptop_server"] else (False, f"{LAPTOP_SERVER.name} is missing")
    if not s["server_pkg"]:
        return False, "the sec-edgar-mcp package is not installed"
    if not s["sec_contact"]:
        return False, f"{UA_ENV} is not set in .env"
    return True, ""


# ── the hosted stand-in: a separate service the client does NOT start ────────
def service_running() -> bool:
    try:
        socket.create_connection((SEC_HOST, SEC_PORT), timeout=0.4).close()
        return True
    except OSError:
        return False


def start_service(wait_s: int = 40) -> None:
    """Play the provider: run sec-edgar-mcp as its own HTTP service. The MCP client never calls this."""
    if service_running():
        return
    logf = open(SVC_LOG, "a", encoding="utf-8", errors="replace")
    proc = subprocess.Popen([sys.executable, "-c", SERVERS["sec"]["launch"]], env=_server_env(), stdout=logf,
                            stderr=logf, stdin=subprocess.DEVNULL,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    SVC_PID.write_text(str(proc.pid))
    deadline = time.time() + wait_s
    while time.time() < deadline:
        if service_running():
            return
        if proc.poll() is not None:
            raise RuntimeError("The SEC EDGAR service stopped while starting. Last log lines: "
                               + SVC_LOG.read_text(encoding="utf-8", errors="replace")[-400:])
        time.sleep(0.4)
    raise RuntimeError(f"The SEC EDGAR service did not open port {SEC_PORT} within {wait_s} seconds.")


def stop_service() -> None:
    try:
        pid = int(SVC_PID.read_text().strip())
    except (OSError, ValueError):
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
    else:
        with contextlib.suppress(OSError):
            os.kill(pid, 15)
    with contextlib.suppress(OSError):
        SVC_PID.unlink()


def _server_env() -> dict:
    """The subprocess gets the normal environment minus anything that looks like a credential."""
    env = {k: v for k, v in os.environ.items() if not _SECRET_NAME.search(k)}
    env["COLUMNS"] = "1000"                             # keep each log record on one line (no wrapping)
    return env


# ── event log (drives the sequence diagram and the trace) ────────────────────
class Log:
    def __init__(self) -> None:
        self.events: list[dict] = []
        self._t0 = time.time()

    def add(self, src: str, dst: str, label: str, kind: str = "call", **detail) -> dict:
        ev = {"n": len(self.events) + 1, "src": src, "dst": dst, "label": label, "kind": kind,
              "at_ms": int((time.time() - self._t0) * 1000), **detail}
        self.events.append(ev)
        return ev


# ── server log → web requests ────────────────────────────────────────────────
_HTTP_LINE = re.compile(r'HTTP Request:\s+(GET|POST)\s+(https?://\S+)\s+"HTTP/[\d.]+\s+(\d{3})')          # httpx
_URLLIB3_LINE = re.compile(r'(https?://[\w.-]+):\d+\s+"(GET|POST)\s+(\S+)\s+HTTP/[\d.]+"\s+(\d{3})')      # requests
_NET_LINE = re.compile(r"NET\s+(\w+)\s+(\S+)\s+->\s+(.+?)\s{2,}", re.M)                                   # laptop_server


class ServerLog:
    """One server's stderr, written to a temp file and read back through a second handle.

    A server logs a line for each outgoing web request, so the lines that appear while a tools/call is in
    flight say what that call fetched. It is the server's own record, not a guess: an MCP client never
    sees a server's network traffic."""

    def __init__(self, existing: Path | None = None) -> None:
        self.owned = existing is None
        if self.owned:                                  # a child process's stderr: we create the file
            fd, self.path = tempfile.mkstemp(suffix=".log", prefix="mcp_server_")
            self.writer = os.fdopen(fd, "w", encoding="utf-8", errors="replace")
            self._reader = open(self.path, "r", encoding="utf-8", errors="replace")
        else:                                           # a separate service's log: read new lines only
            self.path, self.writer = str(existing), None
            self._reader = open(self.path, "r", encoding="utf-8", errors="replace")
            self._reader.seek(0, os.SEEK_END)
        self.full = ""

    def new_text(self) -> str:
        text = self._reader.read()                      # everything written since the last read
        self.full += text
        return text

    def close(self) -> None:
        self.new_text()
        for f in (self._reader, self.writer):
            if f is not None:
                with contextlib.suppress(OSError):
                    f.close()
        if self.owned:
            with contextlib.suppress(OSError):
                os.remove(self.path)


def http_hits(log_text: str) -> list[dict]:
    """Outgoing requests found in a stretch of server log, in order. `status` is an HTTP code, or a short
    text for requests the server describes itself (the laptop server's web search)."""
    hits = [(m.start(), m.group(1), m.group(2), int(m.group(3))) for m in _HTTP_LINE.finditer(log_text)]
    hits += [(m.start(), m.group(2), m.group(1) + m.group(3), int(m.group(4))) for m in _URLLIB3_LINE.finditer(log_text)]
    hits += [(m.start(), m.group(1), m.group(2), m.group(3).strip()) for m in _NET_LINE.finditer(log_text + "  ")]
    return [{"method": method, "url": url, "status": status} for _, method, url, status in sorted(hits, key=lambda h: h[0])]


# ── the MCP sessions: one client per server ──────────────────────────────────
def _annotations(tool) -> dict:
    a = tool.annotations
    return {"read_only": bool(a.readOnlyHint) if a and a.readOnlyHint is not None else None,
            "open_world": bool(a.openWorldHint) if a and a.openWorldHint is not None else None}


async def _with_sessions(keys: list, work, log: Log, confirm: str = "decline") -> dict:
    """For each server: start it → initialize → tools/list. Then work(sessions, tools). Then close them all.

    `confirm` is how this client answers when a server asks the user a question mid-call (elicitation):
    "accept" or "decline". A web form cannot pause for a pop-up, so the user chooses the answer beforehand."""
    from mcp import ClientSession, StdioServerParameters, types
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamablehttp_client

    log.notes = []                                      # log messages and questions the servers sent us

    async def on_log(params) -> None:                   # notifications/message
        log.notes.append({"kind": "log", "level": str(params.level), "text": str(params.data)[:200]})

    async def on_elicit(context, params):               # elicitation/create — the server asks the user
        log.notes.append({"kind": "elicitation", "text": params.message[:300], "answer": confirm})
        log.add("server", "agent", "elicitation: the server asks the user to confirm", "mcp_reply")
        log.add("agent", "server", f"user's answer: {confirm}", "mcp")
        if confirm == "accept":
            fields = list((params.requestedSchema or {}).get("properties", {}))
            return types.ElicitResult(action="accept", content={f: True for f in fields})
        return types.ElicitResult(action="decline")

    out: dict = {"servers": {}, "tools": []}
    logs: dict = {}
    log.server_logs = logs
    sessions: dict = {}
    try:
        async with contextlib.AsyncExitStack() as stack:
            for key in keys:
                spec = SERVERS[key]
                t = time.time()
                if spec["transport"] == "http":
                    # Hosted separately: the server is already running. The client only opens a URL.
                    logs[key] = ServerLog(SVC_LOG)
                    log.add("agent", "server", f"HTTP POST initialize → {spec['url']}", "mcp")
                    read, write, _ = await stack.enter_async_context(streamablehttp_client(spec["url"]))
                else:
                    # Local: the client starts the server as a child process and talks over its stdin/stdout.
                    logs[key] = ServerLog()
                    params = StdioServerParameters(command=sys.executable, args=["-c", spec["launch"]], env=_server_env())
                    log.add("agent", "server", f"START the {spec['label']} process, then initialize (stdio)", "mcp")
                    read, write = await stack.enter_async_context(stdio_client(params, errlog=logs[key].writer))
                session = await stack.enter_async_context(
                    ClientSession(read, write, logging_callback=on_log, elicitation_callback=on_elicit))
                init = await session.initialize()
                connect_ms = int((time.time() - t) * 1000)
                log.add("server", "agent", f"{spec['label']}: protocol {init.protocolVersion}", "mcp_reply", ms=connect_ms)
                log.add("agent", "server", f"tools/list → {spec['label']}", "mcp")
                t = time.time()
                tools = (await session.list_tools()).tools
                log.add("server", "agent", f"{spec['label']}: {len(tools)} tools", "mcp_reply", ms=int((time.time() - t) * 1000))
                sessions[key] = session
                out["servers"][key] = {"label": spec["label"], "about": spec["about"], "name": init.serverInfo.name,
                                       "transport": spec["transport"], "url": spec.get("url", ""),
                                       "protocol": str(init.protocolVersion), "connect_ms": connect_ms, "tools": len(tools)}
                out["tools"] += [{"name": x.name, "description": (x.description or "").strip(),
                                  "inputSchema": x.inputSchema, "server": key, **_annotations(x)} for x in tools]
                logs[key].new_text()
            out.update(await work(sessions, out["tools"]) or {})
            for key in keys:
                log.add("agent", "server", "close the HTTP session (the service keeps running)"
                        if SERVERS[key]["transport"] == "http" else "close the pipes → the server process exits", "mcp")
    finally:
        for slog in logs.values():
            slog.close()
        out["server_log"] = {key: slog.full[-6000:] for key, slog in logs.items()}
    return out


async def _call_tool(session, server: str, name: str, args: dict, log: Log) -> dict:
    """tools/call, normalised. Three outcomes the page keeps apart:
    ok · isError=true (the protocol's own flag) · success:false in the body while isError=false."""
    slog = log.server_logs[server]
    log.add("agent", "server", f"tools/call {name} → {SERVERS[server]['label']}", "mcp", args=args)
    slog.new_text()                                     # drop anything logged before this call
    t = time.time()
    progress: list = []
    notes_before = len(getattr(log, "notes", []))

    async def on_progress(done, total, message) -> None:      # notifications/progress
        progress.append((done, total, message))

    try:
        res = await asyncio.wait_for(session.call_tool(name, args, progress_callback=on_progress), CALL_TIMEOUT_S)
        text = "".join(getattr(c, "text", "") or "" for c in res.content)
        is_error = bool(res.isError)
        protocol_error = ""
    except Exception as exc:                                    # JSON-RPC error, timeout, dropped connection
        text, is_error, protocol_error = f"{type(exc).__name__}: {exc}", True, type(exc).__name__
    ms = int((time.time() - t) * 1000)
    hits = http_hits(slog.new_text())
    if hits:
        log.add("server", "sec", f"{len(hits)} web request{'s' if len(hits) != 1 else ''}", "sec")
    body = text[text.index("{"):] if is_error and "{" in text else text    # "Error executing tool x: {json}"
    try:
        parsed = json.loads(body)
    except ValueError:
        parsed = None
    soft = not is_error and isinstance(parsed, dict) and parsed.get("success") is False
    status = ("protocol error" if protocol_error else "isError=true" if is_error
              else "soft error (success:false, isError=false)" if soft else "ok")
    log.add("server", "agent", f"result: {status}", "mcp_error" if status != "ok" else "mcp_reply", ms=ms)
    return {"tool": name, "server": server, "args": args, "text": text, "parsed": parsed, "is_error": is_error,
            "soft_error": soft, "status": status, "ms": ms, "chars": len(text), "http": hits,
            "progress": len(progress), "progress_last": progress[-1][2] if progress else "",
            "notes": list(getattr(log, "notes", [])[notes_before:])}


# ── what a server offers: tools, resources, resource templates, prompts ──────
def catalog(key: str) -> dict:
    """Connect, ask the server for everything it offers, disconnect."""
    log = Log()

    async def work(sessions, tools):
        s = sessions[key]
        res = (await s.list_resources()).resources
        tpl = (await s.list_resource_templates()).resourceTemplates
        prm = (await s.list_prompts()).prompts
        return {
            "resources": [{"uri": str(r.uri), "name": r.title or r.name, "mime": r.mimeType or "", "description": r.description or ""} for r in res],
            "templates": [{"uri": t.uriTemplate, "name": t.title or t.name, "mime": t.mimeType or "", "description": t.description or ""} for t in tpl],
            "prompts": [{"name": q.name, "title": q.title or q.name, "description": q.description or "",
                         "arguments": [{"name": a.name, "required": bool(a.required)} for a in (q.arguments or [])]} for q in prm],
        }
    out = asyncio.run(_with_sessions([key], work, log))
    out["capabilities"] = out["servers"][key]
    return out


def read_resource(key: str, uri: str) -> dict:
    """resources/read for one URI. The APPLICATION calls this — the model does not."""
    log = Log()

    async def work(sessions, tools):
        t = time.time()
        res = await sessions[key].read_resource(uri)
        c = res.contents[0]
        return {"uri": uri, "mime": c.mimeType or "", "text": getattr(c, "text", "") or "", "ms": int((time.time() - t) * 1000)}
    return asyncio.run(_with_sessions([key], work, log))


def get_prompt(key: str, name: str, arguments: dict) -> dict:
    """prompts/get: the server fills its template with the user's arguments and returns the message text."""
    log = Log()

    async def work(sessions, tools):
        res = await sessions[key].get_prompt(name, arguments)
        return {"text": "\n".join(getattr(m.content, "text", "") for m in res.messages), "description": res.description or ""}
    return asyncio.run(_with_sessions([key], work, log))


# ── synthesis agent ──────────────────────────────────────────────────────────
def _find_value(value: float, text: str) -> bool:
    """Is this number in the tool result text? Whole numbers are matched as whole numbers (not inside a longer one)."""
    flat = re.sub(r"(?<=\d),(?=\d)", "", text)
    cands = {f"{value:g}", repr(value)}
    if float(value).is_integer():
        cands |= {str(int(value)), f"{int(value)}.0"}
    return any(re.search(r"(?<![\d.])" + re.escape(c) + r"(?!\d)", flat) for c in cands)


def synthesise(question: str, calls: list, client, log: Log, attached: list | None = None) -> dict:
    """A second agent with its own prompt and NO tools. Its only input is the question and the tool results —
    it does not inherit the research agent's conversation. It returns a curated answer and chart specs as JSON
    (schema-constrained), and every chart value is then checked against the tool result it cites."""
    from typing import Literal

    from google.genai import types
    from pydantic import BaseModel

    from utils import llm

    class Point(BaseModel):
        label: str
        value: float
        source_call: int

    class Series(BaseModel):
        name: str
        points: list[Point]

    class Chart(BaseModel):
        chart_type: Literal["bar", "grouped_bar", "line", "stacked_bar"]
        title: str
        why_this_chart: str
        y_label: str
        series: list[Series]

    class Synthesis(BaseModel):
        headline: str
        summary: str
        key_points: list[str]
        charts: list[Chart]
        caveats: list[str]

    blocks = []
    for i, c in enumerate(calls, 1):
        blocks.append(f"[call {i}] {c['tool']}({json.dumps(c['args'])}) — {c['status']}\n{c['text'][:RESULT_CAP]}")
    extra = "".join(f"\n\n[attached resource {a['uri']}]\n{a['text'][:RESOURCE_CAP]}" for a in attached or [])
    user_msg = f"Question: {question}\n\nTool results:\n\n" + "\n\n".join(blocks) + extra
    config = types.GenerateContentConfig(
        system_instruction=SYNTHESIS_PROMPT, temperature=0, response_mime_type="application/json",
        response_schema=Synthesis, thinking_config=types.ThinkingConfig(thinking_budget=0),
        max_output_tokens=SYNTH_MAX_TOKENS,
        # Without a timeout a stalled request blocks the page for good (seen live on 2026-10-04).
        http_options=types.HttpOptions(timeout=MODEL_TIMEOUT_MS))
    log.add("agent", "model", f"SYNTHESIS agent: question + {len(calls)} tool results (no tools)", "model")
    t = time.time()
    resp = llm._call(client.models.generate_content, model=llm.MODEL, contents=user_msg, config=config)
    ms = int((time.time() - t) * 1000)
    usage = resp.usage_metadata
    finish = str(getattr(resp.candidates[0], "finish_reason", "")) if resp.candidates else ""
    out = {"ms": ms, "prompt": SYNTHESIS_PROMPT, "user_chars": len(user_msg), "raw": resp.text or "", "finish": finish,
           "in_tokens": getattr(usage, "prompt_token_count", None),
           "out_tokens": getattr(usage, "candidates_token_count", None)}
    try:
        data = Synthesis.model_validate_json(resp.text or "").model_dump()
    except Exception as exc:                                  # schema-valid JSON is expected; if not, say so
        why = (f"it was cut off at the {SYNTH_MAX_TOKENS}-token limit" if "MAX_TOKENS" in finish
               else f"it did not match the schema ({type(exc).__name__})")
        out["error"] = f"The synthesis agent's reply could not be used: {why}."
        log.add("model", "agent", "synthesis reply did not match the schema", "mcp_error", ms=ms)
        return out
    for chart in data["charts"]:
        for series in chart["series"]:
            for pt in series["points"]:
                k = pt["source_call"]
                cited = calls[k - 1]["text"] if 1 <= k <= len(calls) else ""
                if cited and _find_value(pt["value"], cited):
                    pt["check"] = "ok"
                else:
                    other = next((j for j, c in enumerate(calls, 1) if _find_value(pt["value"], c["text"])), None)
                    pt["check"] = f"in call {other}, not call {k}" if other else "not found"
                    if other:
                        pt["source_call"] = other
    # A chart needs at least two numbers to compare; anything less is a sentence, not a chart.
    data["charts"] = [c for c in data["charts"] if sum(len(sr["points"]) for sr in c["series"]) >= 2]
    out.update(data)
    kinds = ", ".join(c["chart_type"] for c in data["charts"]) or "no chart"
    log.add("model", "agent", f"summary + charts chosen: {kinds}", "model_reply", ms=ms)
    return out


# ── research agent: the model chooses the tools ──────────────────────────────
def ask(question: str, servers: list | None = None, attach: list | None = None, confirm: str = "decline",
        prompt_used: dict | None = None) -> dict:
    """Run one question: connect to the servers, let the research agent call tools, then let the synthesis
    agent write the answer. `servers` are keys of SERVERS (default: every server that is ready).
    `attach` is [(server key, resource URI), …]: the application reads those resources and puts them in the
    model's context. `confirm` answers a server's mid-call question ("accept" / "decline")."""
    from google.genai import types
    from utils import llm

    keys = [k for k in (servers or list(SERVERS)) if server_ready(k)[0]]
    if not keys:
        raise RuntimeError("No MCP server is ready to connect.")
    if "sec" in keys and not service_running():
        raise RuntimeError(f"Nothing is listening at {SEC_URL}. The hosted server is not running — start the service "
                           "first. (An MCP client cannot start a server that someone else hosts.)")
    client = llm._client()                    # raises a clear error when GEMINI_API_KEY is missing
    log = Log()
    log.add("you", "agent", "question", "user")

    async def work(sessions, tools):
        owner = {t["name"]: t["server"] for t in tools}
        decls = [types.FunctionDeclaration(name=t["name"], description=t["description"],
                                           parameters_json_schema=t["inputSchema"]) for t in tools]
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT, temperature=0,
            tools=[types.Tool(function_declarations=decls)],
            tool_config=types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode="AUTO")),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            # Thinking off: with it on, this model returned an empty reply (thinking tokens, no text, no
            # function_call) in about half of my runs of one question on 2026-10-04.
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            http_options=types.HttpOptions(timeout=MODEL_TIMEOUT_MS),
        )
        attached = []
        for key, uri in attach or []:                 # resources/read — the APPLICATION's choice, not the model's
            if key not in sessions:
                continue
            log.add("agent", "server", f"resources/read {uri}", "mcp")
            t = time.time()
            res = await sessions[key].read_resource(uri)
            text = getattr(res.contents[0], "text", "") or ""
            ms = int((time.time() - t) * 1000)
            log.add("server", "agent", f"resource: {len(text):,} characters", "mcp_reply", ms=ms)
            attached.append({"server": key, "uri": uri, "mime": res.contents[0].mimeType or "", "text": text, "ms": ms})
        context = "".join(f"[attached resource {a['uri']}]\n{a['text'][:RESOURCE_CAP]}\n\n" for a in attached)
        contents = [types.Content(role="user", parts=[types.Part(text=context + question)])]

        model_calls, calls, answer, stopped, empties = [], [], "", "max_turns", 0
        for turn in range(1, MAX_TURNS + 1):
            log.add("agent", "model", f"question + {len(decls)} tool descriptions" if turn == 1
                    else "history + tool result", "model")
            t = time.time()
            resp = llm._call(client.models.generate_content, model=llm.MODEL, contents=contents, config=config)
            ms = int((time.time() - t) * 1000)
            cand = resp.candidates[0] if resp.candidates else None
            parts = (cand.content.parts if cand and cand.content and cand.content.parts else [])
            text = "".join(p.text for p in parts if getattr(p, "text", None) and not getattr(p, "thought", False))
            fcalls = [p.function_call for p in parts if getattr(p, "function_call", None)]
            usage = resp.usage_metadata
            model_calls.append({
                "turn": turn, "ms": ms, "finish_reason": str(getattr(cand, "finish_reason", "")),
                "function_calls": [{"name": f.name, "args": dict(f.args or {})} for f in fcalls],
                "text": text,
                "claude_term": "stop_reason = tool_use" if fcalls else "stop_reason = end_turn",
                "in_tokens": getattr(usage, "prompt_token_count", None),
                "out_tokens": getattr(usage, "candidates_token_count", None),
                "thought_tokens": getattr(usage, "thoughts_token_count", None),
            })
            if not fcalls and not text.strip():
                # An empty reply is not an answer (seen live on 2026-10-04). Ask again, then fail loudly.
                model_calls[-1]["claude_term"] = "stop_reason = end_turn, but EMPTY"
                log.add("model", "agent", "EMPTY reply (no text, no function_call)", "mcp_error", ms=ms)
                empties += 1
                if empties > EMPTY_RETRIES:
                    stopped = "empty_reply"
                    break
                continue
            if not fcalls:
                log.add("model", "agent", "text, no function_call  (Claude: end_turn)", "model_reply", ms=ms)
                answer, stopped = text, "end_turn"
                break
            log.add("model", "agent", "function_call " + ", ".join(f.name for f in fcalls) + "  (Claude: tool_use)",
                    "model_reply", ms=ms)
            contents.append(cand.content)
            reply_parts = []
            for f in fcalls:
                server = owner.get(f.name)
                if server is None:                    # the model named a tool no server offers
                    call = {"tool": f.name, "server": "", "args": dict(f.args or {}), "text": f"Unknown tool: {f.name}",
                            "parsed": None, "is_error": True, "soft_error": False, "status": "unknown tool", "ms": 0,
                            "chars": 0, "http": []}
                else:
                    call = await _call_tool(sessions[server], server, f.name, dict(f.args or {}), log)
                call["turn"] = turn
                call["sent_chars"] = min(call["chars"], RESULT_CAP)
                calls.append(call)
                body = call["text"][:RESULT_CAP]
                payload = {"result": body} if call["status"] == "ok" else {"error": body}
                reply_parts.append(types.Part.from_function_response(name=f.name, response=payload))
            contents.append(types.Content(role="user", parts=reply_parts))
        return {"model_calls": model_calls, "calls": calls, "answer": answer, "stopped": stopped, "attached": attached}

    try:
        out = asyncio.run(_with_sessions(keys, work, log, confirm))
    except BaseExceptionGroup as group:           # anyio wraps a failure inside the session in a group
        leaf = group
        while isinstance(leaf, BaseExceptionGroup) and leaf.exceptions:
            leaf = leaf.exceptions[0]
        if "Timeout" in type(leaf).__name__:
            raise RuntimeError(f"The model did not answer within {MODEL_TIMEOUT_MS // 1000} seconds "
                               f"({type(leaf).__name__}). Nothing is wrong with the MCP server. Ask again.") from leaf
        raise leaf
    # The servers are closed. If the research agent gathered anything, hand it to the synthesis agent.
    if out["stopped"] == "end_turn" and any(c["status"] == "ok" for c in out["calls"]):
        t = time.time()
        try:
            out["synthesis"] = synthesise(question, out["calls"], client, log, out["attached"])
        except Exception as exc:                  # a timeout or API error must not lose the tool results
            ms = int((time.time() - t) * 1000)
            log.add("model", "agent", f"synthesis failed: {type(exc).__name__}", "mcp_error", ms=ms)
            out["synthesis"] = {"ms": ms, "prompt": SYNTHESIS_PROMPT, "raw": "", "in_tokens": None, "out_tokens": None,
                                "error": f"The synthesis agent did not answer ({type(exc).__name__}: {str(exc)[:160]})."}
    if out["stopped"] == "end_turn":
        log.add("agent", "you", "answer", "answer")
    elif out["stopped"] == "empty_reply":
        log.add("agent", "you", "stopped: the model kept returning an empty reply", "mcp_error")
    else:
        log.add("agent", "you", f"stopped: {MAX_TURNS}-turn guard hit (not an answer)", "mcp_error")
    out.update(question=question, events=log.events, model=llm.MODEL, system_prompt=SYSTEM_PROMPT,
               prompt_used=prompt_used, confirm=confirm)
    return out
