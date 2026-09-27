"""
Playground engine for D2.1 Tool Calling: builds the tool set from the page's correct definitions plus the chosen mistakes
(the same transformations the lab's variants use), then routes the typed request with the SIMULATED router in
utils/tool_select_lab.py and shows every tool's score.
"""

from __future__ import annotations

from dataclasses import dataclass

from utils import tool_select_lab as tsl


@dataclass
class ToolSelConfig:
    mode: str = "desc"
    quality: str = "detailed"      # detailed | minimal
    web_tool: str = "renamed"      # renamed | overlapping
    doc_tools: str = "split"       # split | generic
    keyword_rule: str = "off"      # off | on
    formats: str = "with"          # with | without


def build(cfg: ToolSelConfig):
    from utils.concepts_content import tool_calling as tc
    code = tc.CORRECT
    if cfg.quality == "minimal":
        code = tc.make_minimal(code)
    if cfg.web_tool == "overlapping":
        code = tc.make_overlapping(code)
    if cfg.doc_tools == "generic":
        code = tc.make_generic(code)
    if cfg.keyword_rule == "on":
        code = tc.add_keyword_rule(code)
    if cfg.formats == "without" and cfg.quality != "minimal":
        code = tc.strip_formats(code)
    ns: dict = {}
    exec(compile(code.replace("evaluate(TOOLS, SYSTEM)", ""), "<playground tools>", "exec"), ns)
    return ns["TOOLS"], ns["SYSTEM"]


def run_toolsel(message: str, cfg: ToolSelConfig) -> dict:
    tools, system = build(cfg)
    r = tsl.route(message.strip() or "Pull the key facts out of these web search results.", tools, system)
    expected = next((need for sc in tsl.REQUESTS.values() for text, need, _ in sc if text == message.strip()), None)
    ok = None if expected is None else tsl._correct(expected, r["tool"]) and (expected != "order" or (r["input"] or {}).get("order_id") == "ORD-1001")
    rows = []
    for t in tools:
        d = (r.get("detail") or {}).get(t["name"], {"+": [], "-": []})
        rows.append({"tool": t["name"], "score": (r.get("scores") or {}).get(t["name"], "—"),
                     "matched (+1 each)": ", ".join(d["+"]) or "—", "“do not use” words (−2 each)": ", ".join(d["-"]) or "—",
                     "description": (t.get("description") or "")[:140]})
    return {"tool": r["tool"], "input": r["input"], "why": r["why"], "rows": rows, "system": system, "expected": expected,
            "ok": ok, "kind": tsl.KIND.get(r["tool"], "?")}
