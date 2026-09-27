"""
Fake research backend for the multi-agent labs (D1.2 Subagents). Deterministic, no network, obviously fake
data (example.com). Like utils/tools.py it is configured per scenario by the lab harness.

    web_search(query)  ->  JSON {"topic", "findings": [{claim, source_url, document, page}]}
                           or "ERROR: ..." when the scenario makes a source fail

The findings carry SOURCE METADATA (url, document, page) next to each claim on purpose: the guide asks for
structured formats that keep content separate from attribution when context is passed between agents.
"""

from __future__ import annotations

import json

from utils import lab_trace

SUBTOPICS = ("visual arts", "music", "film")

QUERY_BROAD = "How is AI changing the creative industries? Give me a cited report."
QUERY_SIMPLE = "In what year did the Eiffel Tower open to the public?"

STATE: dict = {"fail_topic": None}
QUERY: str = QUERY_BROAD   # read by lab code via `from utils.research_backend import QUERY`

_FINDINGS = {
    "visual arts": [
        ("Generative tools are now used for concept art by most surveyed studios (fake data).",
         "https://example.com/arts-survey", "Arts Survey 2025", 12),
        ("Galleries report new disputes about training data and artist consent (fake data).",
         "https://example.com/gallery-report", "Gallery Report", 4),
    ],
    "music": [
        ("Streaming services label AI-assisted tracks separately (fake data).",
         "https://example.com/music-labels", "Music Labels Brief", 7),
        ("Session musicians report fewer demo commissions (fake data).",
         "https://example.com/musicians-poll", "Musicians Poll", 3),
    ],
    "film": [
        ("Studios use AI for previsualisation and dubbing (fake data).",
         "https://example.com/film-tech", "Film Tech Review", 9),
        ("Guild contracts now include rules on digital replicas (fake data).",
         "https://example.com/guild-terms", "Guild Terms Summary", 2),
    ],
}
_EIFFEL = [("The Eiffel Tower opened to the public in 1889 (fake data).",
            "https://example.com/eiffel-history", "Tower History", 3)]


def configure(query_kind: str = "broad", fail_topic: str | None = None) -> None:
    global QUERY
    QUERY = QUERY_SIMPLE if query_kind == "simple" else QUERY_BROAD
    STATE["fail_topic"] = fail_topic


def _pack(topic: str, rows) -> str:
    return json.dumps({"topic": topic, "findings": [
        {"claim": c, "source_url": u, "document": d, "page": p} for c, u, d, p in rows]})


def web_search(query: str) -> str:
    q = query.lower()
    if STATE["fail_topic"] and STATE["fail_topic"] in q and "targeted" not in q:
        return "ERROR: source timeout (simulated)"
    for topic in SUBTOPICS:
        if topic in q:
            return _pack(topic, _FINDINGS[topic])
    if "eiffel" in q:
        return _pack("eiffel tower", _EIFFEL)
    return json.dumps({"topic": "unknown", "findings": []})


WEB_SEARCH_TOOL = {
    "name": "web_search",
    "description": "Search the (fake) web for one topic. Returns findings with source url, document and page.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
}

# The spawn tool. The exam guide calls it "Task" (TS 1.3); current Claude Code / Agent SDK docs call it "Agent"
# (renamed in v2.1.63; "Task" is kept as a legacy alias). The simulated coordinator accepts either name.
TASK_TOOL = {
    "name": "Task",
    "description": ("Launch a subagent to do one focused piece of work. The subagent starts with a fresh context: "
                    "it sees ONLY the prompt you write here."),
    "input_schema": {"type": "object", "properties": {
        "subagent_type": {"type": "string", "enum": ["searcher", "analyst", "synthesizer"]},
        "description": {"type": "string", "description": "3-5 word label"},
        "prompt": {"type": "string", "description": "Everything the subagent needs to know"}},
        "required": ["subagent_type", "description", "prompt"]},
}

_DISPATCH = {"web_search": web_search}


def run_research_tool(name: str, args: dict) -> str:
    fn = _DISPATCH.get(name)
    result = f"ERROR: unknown tool {name!r}" if fn is None else fn(**args)
    lab_trace.record({"kind": "tool_exec", "name": name, "args": args, "result": result})
    return result
