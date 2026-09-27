"""
SIMULATED agent-to-agent handoff lab for D1.6 Subagent State Handoff: what a downstream agent can do depends ONLY on what
the handoff (its prompt) carries. The downstream "agents" are scripted functions, not model calls.

Grounding (fetched 2026-09-26/27): a subagent receives only the spawn tool's prompt string and returns only its final
message (code.claude.com/docs/en/agent-sdk/subagents § What subagents inherit); many subagents returning detailed
results explode the coordinator's context (code.claude.com/docs/en/sub-agents § Best practices); structured formats suit
state data (platform.claude.com prompting best practices § State management). Guide: TS 1.3 Skills 1–2 (complete
findings in the prompt; structured content + metadata), TS 5.4 Skills 3–4 (phase summaries; state exports injected into
prompts), TS 1.3 Knowledge 2 (no shared memory between invocations).
INVENTED (simulation): the findings (example.com), token sizes, the context budget and what an agent does over it.
"""

from __future__ import annotations

import json
import re

from utils import lab_trace

SCENARIO_IDS = ("cited_report", "long_research", "next_phase", "crash_resume")
CONTEXT_BUDGET = 3000        # simulated tokens a downstream agent can use well

_BASE = [
    ("visual arts", "Most surveyed studios use generative tools for concept art.", "https://example.com/arts-survey", "Arts Survey 2025", 12),
    ("visual arts", "Galleries report disputes over training data and consent.", "https://example.com/gallery-report", "Gallery Report", 4),
    ("music", "Streaming services label AI-assisted tracks separately.", "https://example.com/music-labels", "Music Labels Brief", 7),
    ("music", "Session musicians report fewer demo commissions.", "https://example.com/musicians-poll", "Musicians Poll", 3),
    ("film", "Studios use AI for previsualisation and dubbing.", "https://example.com/film-tech", "Film Tech Review", 9),
    ("film", "Guild contracts now include rules on digital replicas.", "https://example.com/guild-terms", "Guild Terms Summary", 2),
]
PHASE1_SUMMARY = """Phase 1 findings (structured summary):
- Entry point: orders.refund() in orders.py
- Policy check: refund_policy.AUTO_APPROVE_LIMIT (refund_policy.py)
- Money movement: ledger.post_refund() in ledger.py
- Not relevant to refunds: reports/, exports/, ui/ (checked)"""
_REPO_FILES = 12
SAVED_STATE = {"agent": "refund-flow explorer", "done": ["orders.py", "refund_policy.py"],
               "next": "trace ledger.post_refund callers", "notes": "refund() calls policy check before ledger"}

TASK = "synthesize"
FINDINGS: list = []
RAW_TRANSCRIPTS = ""


def _mk(n: int) -> list:
    out = []
    for i in range(n):
        area, claim, url, doc, page = _BASE[i % len(_BASE)]
        tag = f" (item {i + 1})" if n > len(_BASE) else ""
        out.append({"area": area, "claim": claim.rstrip(".") + tag + " (fake data).", "source_url": url + (f"#{i + 1}" if tag else ""),
                    "document": doc, "page": page + (i // len(_BASE)) * 10})
    return out


def configure(scenario_id: str) -> None:
    global TASK, FINDINGS, RAW_TRANSCRIPTS
    TASK = {"cited_report": "synthesize", "long_research": "synthesize", "next_phase": "next_phase",
            "crash_resume": "resume_agent"}.get(scenario_id, "synthesize")
    FINDINGS = _mk(24 if scenario_id == "long_research" else 6)
    # what the search agents' full transcripts would look like: every call, every raw result, the reasoning
    RAW_TRANSCRIPTS = "\n".join(
        f"[searcher transcript {i}] tool_use web_search(...) -> raw page text " + ("lorem ipsum " * 380)
        + f" ... final: {json.dumps(f)}" for i, f in enumerate(FINDINGS, 1))


def _tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _claims_in(prompt: str) -> list:
    return [f for f in FINDINGS if f["claim"] in prompt]


def _has_meta(prompt: str, f: dict) -> bool:
    # attribution survives only if the claim's own source travels with it (url or document + page)
    i = prompt.find(f["claim"])
    window = prompt[max(0, i - 40): i + len(f["claim"]) + 260]
    return f["source_url"] in window or (f["document"] in window and str(f["page"]) in window)


def run_agent(role: str, prompt: str) -> str:
    """Run a downstream agent that sees ONLY `prompt`. SIMULATED."""
    tokens = _tokens(prompt)
    over = tokens > CONTEXT_BUDGET
    ev = {"kind": "handoff_agent", "role": role, "prompt_tokens": tokens, "over_budget": over, "prompt_head": prompt[:180]}
    if role == "synthesizer":
        found = _claims_in(prompt)
        if over:   # drowning in transcript noise: keeps only the first part of what it was given
            found = found[: max(1, len(found) // 3)]
        lines = [f"{f['claim']} [{f['document']}, p.{f['page']}]" if _has_meta(prompt, f) else f"{f['claim']} [no source]"
                 for f in found]
        out = "\n".join(lines) if lines else "NO_FINDINGS: I was given no findings to write the report from."
        ev.update({"claims_received": len(_claims_in(prompt)), "claims_used": len(found),
                   "cited": sum(1 for f in found if _has_meta(prompt, f))})
    elif role == "explorer":
        knows_phase1 = "entry point" in prompt.lower() and "ledger" in prompt.lower()
        has_state = SAVED_STATE["next"] in prompt
        if has_state:
            reads, out = 1, "Continued from saved state: ledger.post_refund is called only from orders.refund()."
        elif knows_phase1:
            reads, out = 2, "ledger.post_refund depends on orders.refund() and refund_policy.AUTO_APPROVE_LIMIT."
        else:
            reads, out = _REPO_FILES, "Explored the whole repository again: ledger.post_refund depends on orders.refund() and refund_policy."
        ev.update({"reads": reads, "had_state": has_state, "had_summary": knows_phase1})
    else:
        out = f"unknown role {role!r}"
    lab_trace.record(ev)
    return out


def submit(result: str) -> None:
    lab_trace.record({"kind": "submit", "text": str(result)[:4000]})
    print("SUBMITTED:\n" + str(result)[:1200])
