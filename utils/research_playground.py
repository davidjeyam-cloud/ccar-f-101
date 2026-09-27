"""
The multi-agent PLAYGROUND engine (D1.2 Subagents): type a research question and watch a coordinator delegate to
subagents while you change the developer-side settings — is the spawn tool allowed, what context each subagent
receives, parallel or one-at-a-time, how many may run at once, how the coordinator is told to behave, whether a
source fails and whether the coordinator reviews the draft for gaps.

Trusted workbench code in the Streamlit process (learner *code* still runs in the subprocess lab). The model is the
SIMULATED one from utils/mock_claude.py: the coordinator follows its system prompt by KEYWORD, which is a stand-in
for real instruction-following. Every subagent call is made with only the prompt string the coordinator wrote —
that is the documented rule (code.claude.com/docs/en/agent-sdk/subagents § What subagents inherit).

Grounding: subagents start with a fresh context and receive only the Agent/Task tool's prompt; only the final
message returns; the concurrent-subagent limit REFUSES further spawns with "Concurrent subagent limit reached"
(default 20) — all from the subagents doc fetched 2026-09-26. Simulation choices (not docs): the scripted replies,
the simulated seconds per subagent, the keyword-driven coordinator.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from utils import lab_trace, mock_claude as mc, research_backend as rb
from utils.research_backend import SUBTOPICS, TASK_TOOL, WEB_SEARCH_TOOL

SIM_SECONDS = {"searcher": 4, "analyst": 3, "synthesizer": 5}   # simulated, per subagent run
MAX_COORDINATOR_TURNS = 12

AGENT_PROMPTS = {
    "searcher": "ROLE: searcher. Search for the area you are given; return findings as JSON with source metadata.",
    "analyst": "ROLE: analyst. Verify the findings you are given; keep every source.",
    "synthesizer": "ROLE: synthesizer. Write a cited report ONLY from the findings you are given.",
}


@dataclass
class ResearchConfig:
    allow_task: str = "yes"               # is the spawn tool in the coordinator's allowedTools?
    context_mode: str = "full_prompt"     # "full_prompt" | "assume_inherited"
    parallel: str = "yes"                 # all Task calls in ONE response, or one per turn
    max_concurrent: int = 20              # docs default: 20 running subagents at once
    decomposition: str = "distinct"       # "distinct" | "overlapping" | "narrow"
    review_gaps: str = "yes"              # does the coordinator review the draft and re-delegate?
    fail_source: str = "no"               # does the first film search time out?
    findings_format: str = "structured"   # "structured" (source metadata kept) | "claims_only"
    prompt_style: str = "goal"            # "goal" (goals + quality criteria) | "procedural" (fixed steps)
    searcher_has_search: str = "yes"      # AgentDefinition.tools for the searcher includes web_search?


def compose_prompt(cfg: ResearchConfig) -> str:
    """The coordinator's system prompt, built from the knobs — shown on screen so the learner sees the cause."""
    if cfg.prompt_style == "procedural":
        lines = ["ROLE: coordinator.",
                 "Follow these steps exactly. Step 1: search each area. Step 2: verify the findings. "
                 "Step 3: write the report.",
                 "Subagents cannot see this conversation: put the complete context they need in each prompt."]
        return "\n".join(lines)
    goal = ("Goal: a cited report on the single most prominent area of the topic; every claim needs a source."
            if cfg.decomposition == "narrow" else
            "Goal: a cited report that covers ALL major areas of the topic; every claim needs a source.")
    quality = ("Quality bar: several subagents may research the same area - allow overlapping work."
               if cfg.decomposition == "overlapping" else
               "Quality bar: no major area missing, no duplicated research - give each subagent a distinct area.")
    lines = ["ROLE: coordinator.", goal, quality, "Choose only the subagents the question actually needs.",
             ("Delegate independent areas in parallel (all Task calls in ONE response)."
              if cfg.parallel == "yes" else "Delegate one area at a time, waiting for each result."),
             "Subagents cannot see this conversation: put the complete context they need in each prompt."]
    if cfg.review_gaps == "yes":
        lines.append("When a draft comes back, review it for gaps and re-delegate targeted searches for anything missing.")
    return "\n".join(lines)


def _claims_only(text: str) -> str:
    """Flatten structured findings to bare claims (attribution dropped) — the failure this knob demonstrates."""
    blocks = mc._extract_findings(text)
    if not blocks:
        return text
    return "\n".join(json.dumps({"topic": b["topic"], "findings": [{"claim": f["claim"]} for f in b["findings"]]})
                     for b in blocks)


def _run_subagent(client, cfg: ResearchConfig, kind: str, prompt: str) -> dict:
    """One subagent run. It receives ONLY `content` (its whole world) — never the coordinator's messages."""
    content = prompt
    if cfg.context_mode == "assume_inherited" and kind != "searcher":
        content = {"analyst": "Verify the findings gathered so far.",
                   "synthesizer": "Write the final report from the findings gathered so far."}[kind]
    tools = [WEB_SEARCH_TOOL] if (kind == "searcher" and cfg.searcher_has_search == "yes") else []
    messages = [{"role": "user", "content": content}]
    tool_log = []
    for _ in range(6):
        r = client.messages.create(model=mc.PRIMARY_MODEL, max_tokens=512, system=AGENT_PROMPTS[kind],
                                   tools=tools, messages=messages)
        if r.stop_reason != "tool_use":
            text = "".join(b.text for b in r.content if b.type == "text")
            if kind == "searcher" and cfg.findings_format == "claims_only":
                text = _claims_only(text)
            return {"type": "subagent", "kind": kind, "received": content, "tools": [t["name"] for t in tools],
                    "tool_log": tool_log, "result": text, "seconds": SIM_SECONDS[kind]}
        messages.append({"role": "assistant", "content": r.content})
        results = []
        for b in r.content:
            if b.type == "tool_use":
                out = rb.run_research_tool(b.name, b.input)
                tool_log.append(f"{b.name}({b.input}) → {out[:90]}")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": results})
    return {"type": "subagent", "kind": kind, "received": content, "tools": [t["name"] for t in tools],
            "tool_log": tool_log, "result": "SUBAGENT_DID_NOT_FINISH", "seconds": SIM_SECONDS[kind]}


def run_research(user_text: str, cfg: ResearchConfig) -> dict:
    lab_trace.reset()
    mc.reset()
    rb.configure(fail_topic="film" if cfg.fail_source == "yes" else None)
    system = compose_prompt(cfg)
    client = mc.MockClaude("broad_topic")   # any research scenario: the behaviour is the role-dispatching one
    tools = [TASK_TOOL] if cfg.allow_task == "yes" else []
    messages = [{"role": "user", "content": user_text}]
    events: list[dict] = [{"type": "setup", "system": system, "tools": [t["name"] for t in tools]}]
    elapsed = runs = 0
    report, turns = "", 0
    peak_in = 0

    for turn in range(1, MAX_COORDINATOR_TURNS + 1):
        try:
            r = client.messages.create(model=mc.PRIMARY_MODEL, max_tokens=1024, system=system, tools=tools,
                                       messages=messages)
        except (mc.MockAPIError, mc.RunawayGuard) as e:
            events.append({"type": "error", "text": f"{type(e).__name__}: {e}"})
            break
        turns += 1
        api = lab_trace.EVENTS[-1]
        peak_in = max(peak_in, api["input_tokens"])
        calls = [b for b in r.content if b.type == "tool_use"]
        text = "".join(b.text for b in r.content if b.type == "text")
        events.append({"type": "coord", "turn": turn, "stop_reason": r.stop_reason, "text": text,
                       "calls": [{"kind": b.input.get("subagent_type"), "desc": b.input.get("description"),
                                  "prompt": b.input.get("prompt")} for b in calls],
                       "in": api["input_tokens"], "seen_chars": api["seen_chars"]})
        if r.stop_reason != "tool_use":
            report = text
            break
        messages.append({"role": "assistant", "content": r.content})
        results, seconds = [], []
        for i, b in enumerate(calls):
            if i >= cfg.max_concurrent:
                out = "Concurrent subagent limit reached"
                events.append({"type": "limit", "text": f"{out} — the spawn was refused, not queued "
                                                       f"(limit {cfg.max_concurrent}); the coordinator gets this text as the result."})
            else:
                run = _run_subagent(client, cfg, b.input["subagent_type"], b.input["prompt"])
                events.append(run)
                runs += 1
                seconds.append(run["seconds"])
                out = run["result"]
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        elapsed += max(seconds or [0])
        messages.append({"role": "user", "content": results})

    low = report.lower()
    covered = [t for t in SUBTOPICS if f"## {t}" in low]
    cited = len(re.findall(r"\[[^\]]+, p\.\d+\]", report))
    no_source = report.count("[no source]")
    coord = [e for e in events if e["type"] == "coord"]
    max_par = max([len(e["calls"]) for e in coord] or [0])
    simple = "eiffel" in user_text.lower()
    notes = []
    if cfg.allow_task != "yes":
        notes.append("The spawn tool was not in allowedTools, so the coordinator answered alone, without sources.")
    if not simple and report and len(covered) < 3 and cfg.allow_task == "yes":
        notes.append(f"Coverage: {len(covered)}/3 areas ({', '.join(covered) or 'none'}).")
    if not simple and report and cited == 0 and cfg.allow_task == "yes":
        notes.append("The report has no citations.")
    if no_source:
        notes.append(f"{no_source} claim(s) have no source — attribution was lost between agents.")
    first_wave = sum(1 for e in events if e["type"] == "subagent" and e["kind"] == "searcher"
                     and not e["received"].startswith("TARGETED"))
    if not simple and max_par == 1 and first_wave >= 2 and cfg.allow_task == "yes":
        notes.append("One Task call per response — the searches ran one after another.")
    if simple and runs > 1:
        notes.append(f"A one-fact question used {runs} subagent runs.")
    dup = _duplicate_sources(events)
    if dup:
        notes.append(f"{dup} duplicated finding(s): overlapping scopes researched the same sources twice.")
    ok = bool(report) and not notes
    return {"events": events, "result": {
        "report": report, "runs": runs, "turns": turns, "seconds": elapsed, "covered": covered, "cited": cited,
        "peak_in": peak_in, "notes": notes, "ok": ok, "system": system}}


def _duplicate_sources(events) -> int:
    seen, dup = set(), 0
    for e in events:
        if e["type"] == "subagent" and e["kind"] == "searcher" and not e["received"].startswith("TARGETED"):
            for b in mc._extract_findings(e["result"]):
                for f in b["findings"]:
                    key = f.get("source_url") or f["claim"]
                    dup += key in seen
                    seen.add(key)
    return dup
