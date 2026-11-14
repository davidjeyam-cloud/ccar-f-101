"""
SIMULATED tool_choice / structured-extraction / tool-distribution lab for D2.2 Tool Choice.

Documented behaviour it enforces (platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools, strict-tool-use,
build-with-claude/structured-outputs — fetched 2026-09-27):
- tool_choice: {"type":"auto"} (default with tools: may answer in text), {"type":"any"} (must call one of the tools),
  {"type":"tool","name":…} (must call that tool), {"type":"none"} (no tools);
- with any/tool the API prefills the assistant turn, so there is NO text before the tool_use block;
- forced tool use (any/tool) is rejected with a 400 on some models (the docs list Claude Opus 5.5, Fable 5.1, Mythos 5.1) and
  with manual extended thinking; use auto + strict tools / structured outputs there;
- strict: true guarantees the tool input matches the schema (types, required fields) — not that the values are right.
INVENTED (simulation): the documents, the "chatty document → auto answers in text" behaviour, the fabricated value when a
required field is missing, the $-string type slip without strict, the 18-tool confusion and the synthesis agent's misuse of a
web-search tool. The model id "mock-opus-5.5" stands for a model that rejects forced tool use.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from utils import lab_trace

SCENARIO_IDS = ("must_extract", "unknown_type", "missing_fields", "metadata_first", "scoped_tools", "model_rejects_forcing")
NO_FORCE_MODELS = {"mock-opus-5.5"}

DOCS = {
    "invoice_acme": {"type": "invoice", "text": ("Hi team! Great working with you this quarter :) Attached is invoice INV-77 from "
                                                 "Acme Parts Ltd dated 2026-09-01. Total due: $1,240.00 for replacement server fans "
                                                 "(hardware). Tax ID: GB123456789."),
                     "facts": {"vendor": "Acme Parts Ltd", "total": "$1,240.00", "invoice_date": "2026-09-01",
                               "tax_id": "GB123456789", "category": "hardware"}},
    "invoice_northwind": {"type": "invoice", "text": ("Hello! Here's our invoice from Northwind Repairs dated 2026-09-12 for the "
                                                      "quarterly lift maintenance visit. Total: $310.50. Thanks!"),
                          "facts": {"vendor": "Northwind Repairs", "total": "$310.50", "invoice_date": "2026-09-12",
                                    "tax_id": None, "category": "maintenance"}},
    "contract_brightline": {"type": "contract", "text": ("Hello! Please find the signed services agreement between Example Corp "
                                                         "and Brightline Consulting, effective 2026-10-01, for 12 months at a "
                                                         "monthly fee of $4,000.00."),
                            "facts": {"party_a": "Example Corp", "party_b": "Brightline Consulting",
                                      "effective_date": "2026-10-01", "term_months": 12, "monthly_fee": "$4,000.00"}},
}

TASK = "extract"
DOCUMENT = ""
MODEL = "mock-claude"
FORCED_TOOL_CHOICE_SUPPORTED = True
_DOC_KEY = "invoice_acme"
_SEQ = [0]

# 18 tools a careless setup hands to every agent
ALL_TOOLS = ["web_search", "search_internal_wiki", "search_tickets", "fetch_url", "load_document", "verify_fact",
             "summarize_text", "translate_text", "extract_invoice", "extract_contract", "send_email", "create_ticket",
             "update_crm", "query_database", "run_sql", "list_files", "read_file", "post_to_slack"]
_URLS = ["https://example.com/reports/ev-market-2026.pdf", "https://example.com/login",
         "https://example.com/reports/battery-costs.pdf"]


class APIError(Exception):
    """A SIMULATED HTTP 400 from the Messages API."""


def configure(scenario_id: str) -> None:
    global TASK, DOCUMENT, MODEL, FORCED_TOOL_CHOICE_SUPPORTED, _DOC_KEY
    TASK = {"metadata_first": "pipeline", "scoped_tools": "distribute"}.get(scenario_id, "extract")
    _DOC_KEY = {"unknown_type": "contract_brightline", "missing_fields": "invoice_northwind"}.get(scenario_id, "invoice_acme")
    DOCUMENT = DOCS[_DOC_KEY]["text"]
    MODEL = "mock-opus-5.5" if scenario_id == "model_rejects_forcing" else "mock-claude"
    FORCED_TOOL_CHOICE_SUPPORTED = MODEL not in NO_FORCE_MODELS
    _SEQ[0] = 0


# ── response objects ──────────────────────────────────────────────────────────

@dataclass
class Block:
    type: str
    text: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)
    id: str = ""


@dataclass
class Response:
    stop_reason: str
    content: list


def _money(v):
    return float(str(v).replace("$", "").replace(",", "")) if isinstance(v, str) and v.startswith("$") else v


def _fill(tool: dict, facts: dict) -> tuple:
    """Fill a tool's input from the document's facts. Returns (input, fabricated fields, miscategorised fields)."""
    schema = tool.get("input_schema", {}) or {}
    props, required = schema.get("properties", {}) or {}, set(schema.get("required", []) or [])
    strict = bool(tool.get("strict"))
    out, fabricated, miscat = {}, [], []
    for name, spec in props.items():
        if name.endswith("_detail"):
            continue
        types = spec.get("type") if isinstance(spec.get("type"), list) else [spec.get("type")]
        nullable = "null" in types
        val = facts.get(name)
        if val is None:
            if name in required and not nullable:
                out[name] = 0 if "number" in types or "integer" in types else f"(guessed {name})"
                fabricated.append(name)
            elif name in required or nullable:
                out[name] = None
            continue
        if "enum" in spec:
            enum = spec["enum"]
            if val in enum:
                out[name] = val
            elif "other" in enum:
                out[name] = "other"
                if f"{name}_detail" in props:
                    out[f"{name}_detail"] = str(val)
            else:
                out[name] = enum[0]
                miscat.append(f"{name}: '{val}' forced into '{enum[0]}'")
            continue
        if ("number" in types or "integer" in types) and isinstance(val, str) and val.startswith("$"):
            out[name] = _money(val) if strict else val          # without strict the $-string slips through
            continue
        out[name] = val
    for name in props:
        if name.endswith("_detail") and name not in out:
            out[name] = None
    return out, fabricated, miscat


def _instructed(messages) -> bool:
    text = " ".join(str(m.get("content")) for m in messages if m.get("role") == "user").lower()
    return bool(re.search(r"\b(use|call)\b[^.]*\btool\b", text))


def _metadata_done(messages) -> bool:
    return any('"vendor_id"' in str(m.get("content")) for m in messages if m.get("role") == "user")


def _enrich_done(messages) -> bool:
    return any('"enriched"' in str(m.get("content")) for m in messages if m.get("role") == "user")


def create(model: str, tools: list, messages: list, tool_choice: dict | None = None, thinking: dict | None = None,
           max_tokens: int = 1024) -> Response:
    """SIMULATED messages.create for this lab."""
    choice = tool_choice or {"type": "auto"}
    ctype = choice.get("type")
    names = [t.get("name") for t in tools]
    if ctype in ("any", "tool") and model in NO_FORCE_MODELS:
        raise APIError(f"400 invalid_request_error (SIMULATED): forced tool use (tool_choice {ctype}) is not supported on "
                       f"{model} - use tool_choice auto with strict tools, or structured outputs")
    if ctype in ("any", "tool") and (thinking or {}).get("type") == "enabled":
        raise APIError("400 invalid_request_error (SIMULATED): tool_choice any/tool is not supported with manual extended thinking")
    if ctype == "tool" and choice.get("name") not in names:
        raise APIError(f"400 invalid_request_error (SIMULATED): tool_choice names {choice.get('name')!r}, which is not in tools")
    doc = DOCS[_DOC_KEY]
    chosen = None
    if ctype == "none" or not tools:
        chosen = None
    elif ctype == "tool":
        chosen = next(t for t in tools if t.get("name") == choice["name"])
    elif TASK == "pipeline":
        by = {t.get("name"): t for t in tools}
        if _enrich_done(messages):
            chosen = None if ctype == "auto" else (by.get("enrich_vendor") or tools[0])
        elif "enrich_vendor" in by:
            chosen = by["enrich_vendor"]           # the user asked to enrich; with auto/any the model goes straight there
        else:
            chosen = tools[0]
    else:
        match = [t for t in tools if doc["type"] in (t.get("name") or "")]
        best = match[0] if match else tools[0]
        chatty = doc["text"].lower().startswith(("hi", "hello"))
        chosen = None if (ctype == "auto" and chatty and not _instructed(messages)) else best
    _SEQ[0] += 1
    rec = {"kind": "tc_call", "call": _SEQ[0], "model": model, "tool_choice": ctype, "forced_name": choice.get("name"),
           "n_tools": len(tools), "tools": names, "strict": {t.get("name"): bool(t.get("strict")) for t in tools}}
    if chosen is None:
        text = (f"Thanks for sharing! This looks like a {doc['type']} from {doc['facts'].get('vendor') or doc['facts'].get('party_b')}."
                if not _enrich_done(messages) else "Done: metadata extracted and the vendor record enriched.")
        rec.update({"stop_reason": "end_turn", "tool": None, "text": text})
        lab_trace.record(rec)
        return Response("end_turn", [Block("text", text=text)])
    if chosen.get("name") == "extract_metadata":
        inp = {"vendor": doc["facts"].get("vendor"), "document_type": doc["type"]}
        fab, mis = [], []
    elif chosen.get("name") == "enrich_vendor":
        vid = None
        for m in messages:
            mm = re.search(r'"vendor_id":\s*"([^"]+)"', str(m.get("content")))
            if mm:
                vid = mm.group(1)
        inp = {"vendor_id": vid or "V-0000"}
        fab = [] if vid else ["vendor_id"]
        mis = []
    else:
        inp, fab, mis = _fill(chosen, doc["facts"])
    blocks = ([] if ctype in ("any", "tool") else [Block("text", text="I'll pull that out with the extraction tool.")])
    blocks.append(Block("tool_use", name=chosen["name"], input=inp, id=f"toolu_sim_{_SEQ[0]:03d}"))
    rec.update({"stop_reason": "tool_use", "tool": chosen["name"], "input": inp, "fabricated": fab, "miscategorized": mis,
                "text_before_tool": ctype not in ("any", "tool")})
    lab_trace.record(rec)
    return Response("tool_use", blocks)


def run_tool(name: str, tool_input: dict) -> str:
    if name == "extract_metadata":
        return json.dumps({"vendor": tool_input.get("vendor"), "vendor_id": "V-4471", "document_type": tool_input.get("document_type")})
    if name == "enrich_vendor":
        if tool_input.get("vendor_id") == "V-4471":
            return json.dumps({"vendor_id": "V-4471", "enriched": True, "credit_terms": "net 30"})
        return "ERROR: unknown vendor id"
    return json.dumps({"stored": True})


def submit_extraction(response: Response) -> None:
    uses = [b for b in response.content if b.type == "tool_use"]
    lab_trace.record({"kind": "tc_submit", "tool": uses[0].name if uses else None,
                      "input": uses[0].input if uses else None, "text": " ".join(b.text for b in response.content if b.type == "text")})
    print("SUBMITTED:", uses[0].name if uses else "(no tool call — text only)", uses[0].input if uses else "")


# ── tool distribution across agents ───────────────────────────────────────────

def run_agent(role: str, tools: list) -> str:
    """Run a research agent with the given tool NAMES. SIMULATED."""
    tools = list(tools)
    calls = []
    if role == "searcher":
        if len(tools) > 8:                      # too many options: a similarly named tool gets picked
            wrong = next((t for t in tools if "search" in t and t != "web_search"), None)
            calls.append(wrong or "web_search")
        elif "web_search" in tools:
            calls.append("web_search")
        for url in _URLS:
            if "load_document" in tools:
                calls.append(f"load_document({url})" + (" → REJECTED: not a document URL" if not url.endswith(".pdf") else ""))
            elif "fetch_url" in tools:
                calls.append(f"fetch_url({url})" + (" → fetched a login page" if not url.endswith(".pdf") else ""))
        out = "findings from 2 reports"
    elif role == "synthesizer":
        if "web_search" in tools:
            calls.append("web_search(battery cost 2026)")   # doing the searcher's job
        if "verify_fact" in tools:
            calls.append("verify_fact(battery pack costs fell 12%)")
        out = "cited report" + ("" if "verify_fact" in tools else " (one disputed figure left unchecked)")
    else:
        out = "unknown role"
    lab_trace.record({"kind": "tc_agent", "role": role, "tools": tools, "calls": calls})
    print(f"{role} ({len(tools)} tools): {calls}")
    return out
