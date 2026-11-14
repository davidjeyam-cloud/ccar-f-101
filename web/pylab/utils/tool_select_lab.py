"""
SIMULATED tool-selection lab for D2.1 Tool Calling: you write the tool definitions (names, descriptions, input schemas) and
the system prompt; a simulated model routes a set of test requests to tools, and the lab scores how many it routed right.

How the simulated model chooses (deterministic, INVENTED — a stand-in for how much a description helps, which the docs call
"by far the most important factor in tool performance"):
- each request word that appears in a tool's name or in a normal sentence of its description scores +1;
- a request word that appears only in a "do not use … / instead …" sentence of a tool's description scores -2 for that tool
  (boundaries steer requests away);
- if the best scores tie, the model can't tell the tools apart and takes the FIRST tied tool in the list (a misroute risk);
- a system-prompt rule of the form "whenever the user mentions X, use tool_y" overrides the descriptions for any request
  containing X (the guide's keyword-sensitive instructions);
- when a tool's description says ids look like ORD-#### and to prefix a bare number, the model formats "1001" as "ORD-1001";
  otherwise it passes the number through unchanged.
Grounding: platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools (best practices, fetched 2026-09-27); guide TS 2.1.
"""

from __future__ import annotations

import json
import re

from utils import lab_trace

SCENARIO_IDS = ("similar_tools", "generic_tool", "keyword_prompt", "edge_cases")

_STOP = set("a an the of to for in on at by and or is are be it its this that these those what which who how does do me my i "
            "you your we our from with about into out up it's there their them please any all can could should would give "
            "tell just than then so as if when whenever use used using not don't only s".split())

# which job each tool NAME actually does in the fake backend
KIND = {"analyze_content": "web", "extract_web_results": "web", "analyze_document": "doc",
        "extract_data_points": "extract", "summarize_content": "summarize", "verify_claim_against_source": "verify",
        "lookup_order": "order", "get_customer": "customer"}
_DOC_ANY = {"doc", "extract", "summarize", "verify"}

REQUESTS = {
    "similar_tools": [
        ("Pull the key facts out of these web search results about solar panel prices.", "web", None),
        ("Here are the top results from a web search on electric car sales - what do they say?", "web", None),
        ("Go through this uploaded PDF contract and pull out the payment terms.", "doc_any", None),
        ("What does the attached annual report document say about revenue?", "doc_any", None),
    ],
    "generic_tool": [
        ("Extract every price and date from the uploaded contract PDF.", "extract", None),
        ("Give me a short summary of the attached quarterly report.", "summarize", None),
        ("Does the attached report actually support the claim that sales rose 20%?", "verify", None),
    ],
    "keyword_prompt": [
        ("Turn these web search results into a short document for the team.", "web", None),
        ("Pull the key facts out of these web search results about heat pumps.", "web", None),
    ],
    "edge_cases": [
        ("What's the status of order 1001?", "order", {"order_id": "ORD-1001"}),
        ("Where is the order for alice@example.com?", "customer", None),
    ],
}
SCENARIO = "similar_tools"


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id


def _stem(w: str) -> str:
    w = w.lower()
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w


def _words(text: str) -> list:
    out = []
    for raw in re.findall(r"[a-z0-9@.\-]+", text.lower()):
        w = "email" if "@" in raw else raw.strip(".-")
        if not re.search(r"[a-z0-9]", w) or w in _STOP:
            continue
        w = _stem(w)
        if w not in _STOP:
            out.append(w)
    return out


def _tool_vocab(tool: dict):
    desc = tool.get("description", "") or ""
    props = (tool.get("input_schema") or {}).get("properties", {}) or {}
    desc_all = desc + " " + " ".join(str(p.get("description", "")) for p in props.values())
    pos, neg = set(_words(tool.get("name", "").replace("_", " "))), set()
    for sentence in re.split(r"(?<=[.;!?])\s+", desc_all):
        low = sentence.lower()
        target = neg if re.search(r"\bdo not\b|\bdon't\b|\bnot for\b|\binstead\b|\bnever\b", low) else pos
        target.update(_words(sentence))
    return pos, neg - pos


def _keyword_rules(system: str) -> list:
    rules = []
    for m in re.finditer(r"(?:if|when|whenever)[^.]*?\bmentions?\s+(?:an?\s+|the\s+)?['\"]?([a-z]+)['\"]?[^.]*?\b(?:use|call)\s+([a-z_]+)",
                         (system or "").lower()):
        rules.append((_stem(m.group(1)), m.group(2)))
    return rules


def _format_input(tool: dict, request: str):
    if tool.get("name") not in ("lookup_order", "get_customer"):
        return None
    text = json.dumps(tool).lower()
    email = re.search(r"[\w.]+@example\.com", request)
    if tool["name"] == "get_customer":
        return {"email": email.group(0)} if email else {}
    num = re.search(r"\b(?:ord-)?(\d{4})\b", request.lower())
    if not num:
        return {"order_id": None}
    formatted = "ord-" in text and ("prefix" in text or "form" in text or "format" in text)
    return {"order_id": f"ORD-{num.group(1)}" if formatted else num.group(1)}


def route(request: str, tools: list, system: str = "") -> dict:
    """Which tool the SIMULATED model picks for one request, and why."""
    words = _words(request)
    for word, tool_name in _keyword_rules(system):
        if word in words and any(t.get("name") == tool_name for t in tools):
            tool = next(t for t in tools if t.get("name") == tool_name)
            return {"tool": tool_name, "why": f"system prompt rule: “mentions {word}” → {tool_name}", "scores": {},
                    "ambiguous": False, "keyword_override": True, "input": _format_input(tool, request)}
    scores, detail = {}, {}
    for t in tools:
        pos, neg = _tool_vocab(t)
        hits = [w for w in words if w in pos]
        bad = [w for w in words if w in neg]
        scores[t["name"]] = len(hits) - 2 * len(bad)
        detail[t["name"]] = {"+": hits, "-": bad}
    best = max(scores.values()) if scores else 0
    tied = [n for n, s in scores.items() if s == best]
    pick = tied[0]
    tool = next(t for t in tools if t["name"] == pick)
    why = (f"highest score {best} (matched {detail[pick]['+'] or 'nothing'})" if len(tied) == 1 else
           f"TIE at {best} between {tied} — the tools can't be told apart, so the first one listed wins")
    return {"tool": pick, "why": why, "scores": scores, "detail": detail, "ambiguous": len(tied) > 1,
            "keyword_override": False, "input": _format_input(tool, request)}


def _correct(kind_needed: str, tool_name: str) -> bool:
    kind = KIND.get(tool_name, "unknown")
    return kind in _DOC_ANY if kind_needed == "doc_any" else kind == kind_needed


def evaluate(tools: list, system: str = "") -> None:
    """Route this scenario's test requests with your tool definitions and system prompt; record the score."""
    names = [t.get("name", "") for t in tools]
    bad_names = [n for n in names if not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", n or "")]
    rows = []
    for text, needed, want_input in REQUESTS[SCENARIO]:
        r = route(text, tools, system)
        ok = _correct(needed, r["tool"])
        if ok and want_input:
            ok = r["input"] == want_input
        if ok and needed == "order" and r["input"] and r["input"].get("order_id") != "ORD-1001":
            ok = False
        rows.append({"request": text, "needed": needed, "picked": r["tool"], "input": r["input"], "ok": ok,
                     "why": r["why"], "ambiguous": r["ambiguous"], "keyword_override": r["keyword_override"]})
        mark = "✓" if ok else "✗"
        print(f"{mark} {text}\n    → {r['tool']}({r['input'] or ''})  [{r['why']}]")
    score = sum(r["ok"] for r in rows)
    print(f"ROUTED CORRECTLY: {score}/{len(rows)}" + (f" · invalid tool names: {bad_names}" if bad_names else ""))
    lab_trace.record({"kind": "tool_eval", "scenario": SCENARIO, "rows": rows, "score": score, "total": len(rows),
                      "n_tools": len(tools), "bad_names": bad_names,
                      "short_descriptions": [t.get("name") for t in tools if len(re.split(r"(?<=[.!?])\s+", (t.get("description") or "").strip())) < 3]})
