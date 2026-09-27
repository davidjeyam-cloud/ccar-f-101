"""
Playground engine for D2.2 Tool Choice, on the SIMULATED API in utils/toolchoice_lab.py (see its docstring for what is
documented vs invented). Tool definitions come from the page's correct lab code, modified by the tab's knobs.
"""

from __future__ import annotations

import contextlib
import copy
import io
from dataclasses import dataclass

from utils import lab_trace
from utils import toolchoice_lab as tl


@dataclass
class ToolChoiceConfig:
    mode: str = "modes"
    choice: str = "any"             # auto | any | tool:extract_invoice | tool:extract_contract | none
    doc: str = "invoice"            # invoice | contract
    first: str = "forced"           # pipeline: forced | any | auto
    release: str = "yes"            # pipeline
    nullable: str = "yes"
    other: str = "yes"
    strict: str = "yes"
    validate: str = "yes"
    searcher_tools: str = "scoped"  # scoped | fetch_url | all
    synth_tools: str = "verify_fact"  # verify_fact | web_search | none | all
    model: str = "mock-opus-5.5"
    thinking: str = "off"


def _defs():
    from utils.concepts_content import tool_choice as tc
    ns: dict = {}
    code = tc.CORRECT.split("\ndef first_choice")[0]
    exec(compile(code, "<tool defs>", "exec"), ns)
    return ns


def _choice(c: str) -> dict:
    if c.startswith("tool:"):
        return {"type": "tool", "name": c.split(":", 1)[1]}
    return {"type": c}


def _resp_summary(r) -> dict:
    blocks = [{"type": b.type, "text": b.text} if b.type == "text" else {"type": b.type, "name": b.name, "input": b.input} for b in r.content]
    return {"stop_reason": r.stop_reason, "content": blocks}


def run_toolchoice(message: str, cfg: ToolChoiceConfig) -> dict:
    lab_trace.reset()
    d = _defs()
    out = {"lines": [], "request": None, "response": None, "error": None, "notes": [], "ok": True}
    msg = message.strip()
    try:
        if cfg.mode in ("modes", "support", "schema", "semantic"):
            if cfg.mode == "modes":
                tl.configure("unknown_type" if cfg.doc == "contract" else "must_extract")
                model, thinking, choice = "mock-claude", None, _choice(cfg.choice)
                tools = [d["INVOICE"], d["CONTRACT"]]
            elif cfg.mode == "support":
                tl.configure("model_rejects_forcing" if cfg.model == "mock-opus-5.5" else "must_extract")
                tl.MODEL = cfg.model
                model, choice = cfg.model, _choice(cfg.choice)
                thinking = {"type": "enabled", "budget_tokens": 2000} if cfg.thinking == "enabled" else None
                tools = [d["INVOICE"], d["CONTRACT"]]
            else:
                tl.configure("missing_fields" if cfg.mode == "schema" else "must_extract")
                model, thinking, choice = "mock-claude", None, {"type": "any"}
                inv = copy.deepcopy(d["INVOICE"])
                props = inv["input_schema"]["properties"]
                if cfg.mode == "schema":
                    if cfg.nullable == "no":
                        props["tax_id"] = {"type": "string"}
                    if cfg.other == "no":
                        props["category"] = {"type": "string", "enum": ["hardware", "software", "services"]}
                        props.pop("category_detail", None)
                        inv["input_schema"]["required"] = [r for r in inv["input_schema"]["required"] if r != "category_detail"]
                    if cfg.strict == "no":
                        inv.pop("strict", None)
                tools = [inv]
            content = tl.DOCUMENT + (" " + msg if msg else "")
            out["request"] = {"model": model, "tool_choice": choice, "thinking": thinking,
                              "tools": [{"name": t["name"], "strict": bool(t.get("strict"))} for t in tools]}
            r = tl.create(model=model, tools=tools, tool_choice=choice, thinking=thinking,
                          messages=[{"role": "user", "content": content}])
            out["response"] = _resp_summary(r)
            ev = lab_trace.EVENTS[-1]
            if ev.get("fabricated"):
                out["notes"].append(f"Invented values for required fields the document lacks: {ev['fabricated']}")
            if ev.get("miscategorized"):
                out["notes"].append(f"Forced into a category: {ev['miscategorized']}")
            inp = ev.get("input") or {}
            if isinstance(inp.get("total"), str) or isinstance(inp.get("monthly_fee"), str):
                out["notes"].append("A “$…” string landed in a number field (no strict: true).")
            if r.stop_reason != "tool_use":
                out["notes"].append("No tool call — a text reply. Nothing structured to store.")
            if cfg.mode == "semantic":
                line_items = [700.0, 500.0]
                total = 1240.0
                out["lines"].append(f"Extraction (schema-valid): total {inp.get('total')} · line items {line_items} (sum {sum(line_items)})")
                if cfg.validate == "yes":
                    out["lines"].append(f"Your semantic check: line items sum to {sum(line_items)} ≠ total {total} → flagged for review / retry.")
                else:
                    out["notes"].append(f"Schema-valid but wrong: line items sum to {sum(line_items)}, total says {total} — stored unchecked.")
        elif cfg.mode == "pipeline":
            tl.configure("metadata_first")
            tools = [d["METADATA"], d["ENRICH"]]
            messages = [{"role": "user", "content": tl.DOCUMENT + " " + (msg or "Extract the metadata, then enrich the vendor record.")}]
            choice = {"forced": {"type": "tool", "name": "extract_metadata"}, "any": {"type": "any"}, "auto": {"type": "auto"}}[cfg.first]
            seq = []
            for turn in range(1, 6):
                r = tl.create(model="mock-claude", tools=tools, tool_choice=choice, messages=messages)
                names = [b.name for b in r.content if b.type == "tool_use"]
                ev = lab_trace.EVENTS[-1]
                out["lines"].append(f"turn {turn}: tool_choice {choice['type']}{' ' + choice.get('name', '') if choice.get('name') else ''} → "
                                    f"{names or 'text: ' + ''.join(b.text for b in r.content)}"
                                    + (f" {ev['input']}" if names else ""))
                seq += names
                if r.stop_reason != "tool_use":
                    break
                messages.append({"role": "assistant", "content": r.content})
                messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": b.id,
                                                              "content": tl.run_tool(b.name, b.input)} for b in r.content if b.type == "tool_use"]})
                if cfg.release == "yes":
                    choice = {"type": "auto"}
            if not seq or seq[0] != "extract_metadata":
                out["notes"].append("Enrichment ran before metadata extraction (with an invented vendor id).")
            elif "enrich_vendor" not in seq:
                out["notes"].append("The forced tool was never released: enrichment never ran.")
        else:
            tl.configure("scoped_tools")
            s_tools = {"scoped": ["web_search", "load_document"], "fetch_url": ["web_search", "fetch_url"], "all": tl.ALL_TOOLS}[cfg.searcher_tools]
            y_tools = {"verify_fact": ["verify_fact"], "web_search": ["web_search"], "none": [], "all": tl.ALL_TOOLS}[cfg.synth_tools]
            with contextlib.redirect_stdout(io.StringIO()):     # the lab prints for the code lab; the playground renders events
                tl.run_agent("searcher", s_tools)
                tl.run_agent("synthesizer", y_tools)
            for e in lab_trace.EVENTS:
                if e["kind"] == "tc_agent":
                    out["lines"].append(f"{e['role']} ({len(e['tools'])} tools) → {e['calls'] or 'no tool calls'}")
                    if e["role"] == "searcher" and "web_search" not in e["calls"]:
                        out["notes"].append("The searcher picked the wrong search tool among 18.")
                    if e["role"] == "searcher" and any("fetched a login page" in c for c in e["calls"]):
                        out["notes"].append("fetch_url fetched a login page — a constrained load_document would have rejected it.")
                    if e["role"] == "synthesizer" and any(c.startswith("web_search") for c in e["calls"]):
                        out["notes"].append("The synthesis agent ran a web search itself — outside its role.")
                    if e["role"] == "synthesizer" and not any(c.startswith("verify_fact") for c in e["calls"]):
                        out["notes"].append("The disputed figure was never fact-checked.")
    except tl.APIError as e:
        out["error"] = str(e)
        out["notes"].append("The request was rejected — nothing was extracted.")
    out["ok"] = not out["notes"]
    return out
