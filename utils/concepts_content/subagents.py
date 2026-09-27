"""
D1.2 Subagents — coordinator-subagent orchestration (guide TS 1.2) and subagent invocation, context passing and
spawning (guide TS 1.3).

GROUNDING (CLAUDE.md, user rule 2026-09-26): written from the OFFICIAL docs fetched and read on 2026-09-26 (DOC_REFS)
plus the exam guide's TS 1.2 (pp.5-6) and TS 1.3 (pp.6-7). Every substantive claim is in GROUNDING with its source type.
Where the guide and the docs differ — the guide calls the spawn tool "Task", the current docs call it "Agent"; the
guide's hub-and-spoke coordinator vs the docs' allowance for nested subagents — the page says so.

Everything is paraphrased. No guide/docs passages are copied at length and no real exam question is reproduced.
"""

import json
import re

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.research_backend import SUBTOPICS

DOCS_VERIFIED_ON = "2026-09-26"
_C = "https://code.claude.com/docs/en"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (
    DocRef("Subagents in the SDK (Agent SDK)", f"{_C}/agent-sdk/subagents"),
    DocRef("Create custom subagents (Claude Code)", f"{_C}/sub-agents"),
    DocRef("Work with sessions — continue, resume, fork (Agent SDK)", f"{_C}/agent-sdk/sessions"),
    DocRef("Handle tool calls — parallel tool results", f"{_P}/agents-and-tools/tool-use/handle-tool-calls"),
)

GROUNDING = (
    Claim("A subagent is a separate agent instance the main agent spawns for a focused subtask. Documented benefits: context "
          "isolation, parallelisation, specialised instructions, tool restrictions.",
          "docs", "agent-sdk/subagents § Overview, Benefits of using subagents"),
    Claim("A non-fork subagent's context starts fresh: it does NOT receive the parent's conversation history or tool results. "
          "The only content passed from parent to subagent is the spawn tool's prompt string, so file paths, errors and decisions "
          "it needs must be in that prompt.",
          "docs", "agent-sdk/subagents § What subagents inherit"),
    Claim("Only the subagent's FINAL message returns to the parent as the tool result; its intermediate tool calls and results "
          "stay inside it. The parent may summarise it in its own reply.",
          "docs", "agent-sdk/subagents § Benefits (Context isolation); What subagents inherit"),
    Claim("Subagents are spawned through the \"Agent\" tool; it appears as \"Agent\" in tool_use blocks but as \"Task\" in the "
          "system:init tools list, and before Claude Code v2.1.63 tool_use blocks named it \"Task\" — match both. The docs' "
          "examples put \"Agent\" in allowed_tools.",
          "docs", "agent-sdk/subagents § Detect subagent invocation; sub-agents § Tool Name: Task vs Agent"),
    Claim("AgentDefinition: description and prompt are required; tools, disallowedTools, model, skills, memory, mcpServers, "
          "maxTurns, background and others are optional. Omitting tools means the subagent inherits every tool available to "
          "subagents; listing tools restricts it, and a tool left out is simply absent from its session.",
          "docs", "agent-sdk/subagents § AgentDefinition configuration; Tool restrictions"),
    Claim("Claude chooses a subagent from each one's description; naming a subagent in the prompt forces that choice.",
          "docs", "agent-sdk/subagents § Automatic invocation, Explicit invocation"),
    Claim("Subagents can spawn subagents (default depth 3 layers below the main agent; 1 turns nesting off). At most 20 subagents "
          "run at once by default; past the limit the spawn is REFUSED with the text \"Concurrent subagent limit reached\" until the "
          "count drops. A spend cap refuses further spawns with \"Budget limit reached\" and ends the query with error_max_budget_usd.",
          "docs", "agent-sdk/subagents § Cap subagent depth, concurrency, and spend"),
    Claim("Several tool_use blocks in one assistant response are answered together: all their tool_result blocks go back in a "
          "single user message.",
          "docs", "tool-use/handle-tool-calls § parallel tool use (as read for D1.1)"),
    Claim("A fork subagent inherits the parent conversation instead of starting fresh (an exception to isolation).",
          "docs", "agent-sdk/subagents § Benefits; sub-agents § Forks"),
    Claim("Session fork: a NEW session starts with a copy of the original's history; the original stays unchanged; the fork has "
          "its own session id and both can be resumed separately. Forking branches the conversation, not the filesystem — file "
          "edits a forked agent makes are real.",
          "docs", "agent-sdk/sessions § Fork to explore alternatives"),
    Claim("Docs best practices: don't spawn many subagents that each return detailed results (context explosion); don't use "
          "subagents for frequent back-and-forth refinement; subagent results still go through permission checks.",
          "docs", "sub-agents § Best Practices; Restrictions & Limitations"),
    Claim("A resumed subagent keeps its full history; a subagent that hits maxTurns has its output marked partial and can be "
          "resumed.", "docs", "agent-sdk/subagents § Resume subagents"),
    Claim("Hub-and-spoke: the coordinator manages ALL inter-subagent communication, error handling and information routing.",
          "guide", "TS 1.2 · Knowledge 1 · pp.5–6"),
    Claim("Subagents have isolated context — they do not inherit the coordinator's conversation history automatically.",
          "guide", "TS 1.2 · Knowledge 2 · pp.5–6; TS 1.3 · Knowledge 2 · pp.6–7"),
    Claim("The coordinator's role: task decomposition, delegation, result aggregation, and choosing which subagents to invoke by "
          "query complexity.", "guide", "TS 1.2 · Knowledge 3 · pp.5–6"),
    Claim("Risk: overly narrow decomposition by the coordinator leaves broad topics incompletely covered.",
          "guide", "TS 1.2 · Knowledge 4 · pp.5–6"),
    Claim("Coordinator skills: select subagents dynamically instead of always running the full pipeline; partition scope to "
          "minimise duplication; run iterative refinement (evaluate synthesis for gaps, re-delegate targeted searches, re-synthesise); "
          "route all subagent communication through the coordinator.",
          "guide", "TS 1.2 · Skills 1–4 · pp.5–6"),
    Claim("The spawn mechanism is the \"Task\" tool and allowedTools must include \"Task\" for the coordinator to invoke subagents.",
          "guide", "TS 1.3 · Knowledge 1 · pp.6–7"),
    Claim("Subagent context must be given explicitly in the prompt; subagents do not inherit parent context or share memory "
          "between invocations.", "guide", "TS 1.3 · Knowledge 2 · pp.6–7"),
    Claim("AgentDefinition config covers descriptions, system prompts and tool restrictions per subagent type; fork-based session "
          "management explores divergent approaches from a shared baseline.",
          "guide", "TS 1.3 · Knowledge 3 and 4 · pp.6–7"),
    Claim("Invocation skills: put complete findings in the subagent prompt; use structured formats that separate content from "
          "metadata (source URL, document, page) to keep attribution; emit multiple Task calls in ONE coordinator response for "
          "parallel subagents; write coordinator prompts as goals and quality criteria, not step-by-step procedures.",
          "guide", "TS 1.3 · Skills 1–4 · pp.6–7"),
    Claim("The guide says \"Task\"; the current docs say \"Agent\" (\"Task\" is a legacy alias). The page teaches both and the exam "
          "term first.", "guide", "TS 1.3 · Knowledge 1 · pp.6–7, vs the docs' Tool Name note"),
    Claim("The lab's \"Task\" tool name and the three subagent types (searcher, analyst, synthesizer) are this workbench's "
          "choices, modelled on guide Scenario 3 (Multi-Agent Research System).",
          "recommendation", "guide §5 · Scenario 3 · p.4"),
    Claim("The simulated coordinator follows its system prompt by KEYWORD (\"parallel\", \"gaps\", \"single most\", \"step 1\"…); the "
          "subagents' replies, the fake findings (example.com), the simulated seconds per run and the token sizes are scripted. "
          "Real models interpret instructions far less literally.",
          "simulated", "utils/mock_claude.py; utils/research_backend.py; utils/research_playground.py"),
)

# ── Lab code ───────────────────────────────────────────────────────────────────

_IMPORTS = r'''from utils.mock_claude import MockClaude   # SIMULATED stand-in. In the real SDK the Task/Agent tool spawns subagents for you
from utils.research_backend import QUERY, TASK_TOOL, WEB_SEARCH_TOOL, run_research_tool

client = MockClaude()
MODEL = "mock-claude"

'''

_PROMPT = r'''# Goal + quality criteria (not a step-by-step recipe). It also says: delegate in parallel, give each
# subagent complete context, and review the draft for gaps.
COORDINATOR_PROMPT = """ROLE: coordinator.
Goal: a cited report that covers ALL major areas of the topic; every claim needs a source.
Quality bar: no major area missing, no duplicated research - give each subagent a distinct area.
Choose only the subagents the question actually needs.
Delegate independent areas in parallel (all Task calls in ONE response).
Subagents cannot see this conversation: put the complete context they need in each prompt.
When a draft comes back, review it for gaps and re-delegate targeted searches for anything missing."""

'''

_AGENTS = r'''AGENTS = {   # AgentDefinition-style: a description, a system prompt, and TOOL RESTRICTIONS per subagent type
    "searcher":    {"description": "Finds sources for ONE area", "tools": [WEB_SEARCH_TOOL],
                    "prompt": "ROLE: searcher. Search for the area you are given; return findings as JSON with source metadata."},
    "analyst":     {"description": "Verifies findings", "tools": [],
                    "prompt": "ROLE: analyst. Verify the findings you are given; keep every source."},
    "synthesizer": {"description": "Writes the cited report", "tools": [],
                    "prompt": "ROLE: synthesizer. Write a cited report ONLY from the findings you are given."},
}
'''

_ALLOWED = r'''ALLOWED_TOOLS = [TASK_TOOL]   # the coordinator's allowedTools must include the spawn tool ("Task" on the exam; "Agent" in current docs)
'''

_RUN_SUB = r'''

def run_subagent(subagent_type, prompt):
    agent = AGENTS[subagent_type]
    messages = [{"role": "user", "content": prompt}]       # the prompt string is the ONLY thing a subagent receives
    for _ in range(6):
        r = client.messages.create(model=MODEL, max_tokens=512, system=agent["prompt"],
                                   tools=agent["tools"], messages=messages)
        if r.stop_reason != "tool_use":
            return "".join(b.text for b in r.content if b.type == "text")   # only the FINAL message goes back
        messages.append({"role": "assistant", "content": r.content})
        results = [{"type": "tool_result", "tool_use_id": b.id, "content": run_research_tool(b.name, b.input)}
                   for b in r.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    raise RuntimeError("subagent did not finish")


'''

_LOOP = r'''messages = [{"role": "user", "content": QUERY}]
for turn in range(1, 11):
    r = client.messages.create(model=MODEL, max_tokens=1024, system=COORDINATOR_PROMPT,
                               tools=ALLOWED_TOOLS, messages=messages)
    calls = [b for b in r.content if b.type == "tool_use"]
    print(f"coordinator turn {turn}: stop_reason = {r.stop_reason}, Task calls in this response: {len(calls)}")
    if r.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": r.content})
        results = []
        for b in calls:                                     # every Task call in the response gets a result...
            out = run_subagent(b.input["subagent_type"], b.input["prompt"])
            print(f"   {b.input['subagent_type']:11s} -> {out[:70]!r}")
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": results})   # ...all in ONE user message
        continue
    if r.stop_reason == "end_turn":
        print("FINAL REPORT:\n" + "".join(b.text for b in r.content if b.type == "text"))
        break
    raise RuntimeError(f"unhandled stop_reason: {r.stop_reason}")
else:
    raise RuntimeError("coordinator did not finish within 10 turns")
'''

CORRECT = _IMPORTS + _PROMPT + _AGENTS + _ALLOWED + _RUN_SUB + _LOOP


def _swap(code: str, old: str, new: str) -> str:
    assert old in code, f"lab code changed, cannot apply variant edit: {old[:60]!r}"
    return code.replace(old, new, 1)


VARIANT_A = _swap(CORRECT, _ALLOWED.strip("\n"),
                  'ALLOWED_TOOLS = []   # WRONG: "Task" is missing from allowedTools, so the coordinator cannot spawn any subagent')

VARIANT_B = _swap(CORRECT, '    messages = [{"role": "user", "content": prompt}]       # the prompt string is the ONLY thing a subagent receives',
                  r'''    # WRONG: assumes the subagent already knows what the coordinator knows (inherited context / shared memory).
    # It does not: it starts fresh and sees ONLY what is in this message.
    LABELS = {"searcher": prompt,
              "analyst": "Verify the findings gathered so far.",
              "synthesizer": "Write the final report from the findings gathered so far."}
    messages = [{"role": "user", "content": LABELS[subagent_type]}]''')

VARIANT_C = (_IMPORTS + _AGENTS + _RUN_SUB + r'''# WRONG: the developer hard-codes the pipeline. No coordinator decides which subagents THIS question needs,
# so a one-fact question gets the same three subagents as a broad research topic.
findings = run_subagent("searcher", "Research: " + QUERY + " Return findings as JSON with source url, document and page.")
verified = run_subagent("analyst", "Verify and annotate these findings. Keep every source.\n" + findings)
report = run_subagent("synthesizer", "Write a cited report, using ONLY these verified findings:\n" + verified)
print("FINAL REPORT:\n" + report)
''')

VARIANT_D = _swap(CORRECT, "# Goal + quality criteria (not a step-by-step recipe). It also says: delegate in parallel, give each\n# subagent complete context, and review the draft for gaps.\n",
                  "# WRONG: the goal is too narrow - it tells the coordinator to cover only ONE area of a broad topic.\n")
VARIANT_D = _swap(VARIANT_D, "Goal: a cited report that covers ALL major areas of the topic; every claim needs a source.",
                  "Goal: a cited report on the single most prominent area of the topic; every claim needs a source.")

VARIANT_E = _swap(CORRECT, "# Goal + quality criteria (not a step-by-step recipe). It also says: delegate in parallel, give each\n# subagent complete context, and review the draft for gaps.\n",
                  "# WRONG: the coordinator is told to delegate ONE area per turn instead of emitting all Task calls in one response.\n")
VARIANT_E = _swap(VARIANT_E, "Delegate independent areas in parallel (all Task calls in ONE response).",
                  "Delegate one area at a time, waiting for each result.")

VARIANT_F = _swap(CORRECT, "def run_subagent(subagent_type, prompt):\n    agent = AGENTS[subagent_type]\n",
                  'PIPE = []   # WRONG: subagents hand results to each other directly, around the coordinator\n\n\n'
                  'def run_subagent(subagent_type, prompt):\n    agent = AGENTS[subagent_type]\n'
                  '    if subagent_type != "searcher":\n        prompt = "\\n".join(PIPE)   # the next subagent reads the pipe, not what the coordinator wrote\n')
VARIANT_F = _swap(VARIANT_F, '            return "".join(b.text for b in r.content if b.type == "text")   # only the FINAL message goes back',
                  '            text = "".join(b.text for b in r.content if b.type == "text")\n'
                  '            if subagent_type == "searcher":\n'
                  '                PIPE.append(text)      # findings (and errors) never reach the coordinator\n'
                  '                return "ok - forwarded directly to the analyst"\n'
                  '            return text')

VARIANT_G = _swap(CORRECT, "# Goal + quality criteria (not a step-by-step recipe). It also says: delegate in parallel, give each\n# subagent complete context, and review the draft for gaps.\n",
                  "# WRONG: nothing asks the coordinator to review the draft for gaps, so nothing re-delegates.\n")
VARIANT_G = _swap(VARIANT_G, "\nWhen a draft comes back, review it for gaps and re-delegate targeted searches for anything missing.", "")

VARIANT_H = _swap(CORRECT, "from utils.research_backend import QUERY, TASK_TOOL, WEB_SEARCH_TOOL, run_research_tool\n",
                  "from utils.research_backend import QUERY, TASK_TOOL, WEB_SEARCH_TOOL, run_research_tool\nimport json\n")
VARIANT_H = _swap(VARIANT_H, '            return "".join(b.text for b in r.content if b.type == "text")   # only the FINAL message goes back',
                  '            text = "".join(b.text for b in r.content if b.type == "text")\n'
                  '            # WRONG: sends the subagent\'s whole transcript back, not just its final message\n'
                  '            return text + "\\n--- full subagent transcript ---\\n" + json.dumps(messages, default=lambda o: o.to_dict())')

# ── Metrics, chart colours and the result check ────────────────────────────────

_SEC = {"searcher": 4, "analyst": 3, "synthesizer": 5}   # simulated seconds per subagent run
BLOAT_LIMIT_TOKENS = 3200                                  # a coordinator whose input passes this is drowning in subagent transcripts


def _metrics(trace: dict) -> dict:
    ev = [e for e in trace["events"] if e["kind"] == "api_call"]
    coord = [e for e in ev if e.get("role") in (None, "coordinator")]
    runs = [e for e in ev if e.get("role") in _SEC and e["n_messages"] == 1]
    final = coord[-1] if coord else (ev[-1] if ev else None)
    text = ""
    if final and final["stop_reason"] == "end_turn":
        text = "".join(b["text"] for b in final["blocks"] if b["type"] == "text")
    low = text.lower()
    elapsed, group = 0, None
    for e in ev:
        if e.get("role") in (None, "coordinator"):
            elapsed += max(group.values()) if group else 0
            group = {}
        elif e["n_messages"] == 1 and group is not None:
            group[len(group)] = _SEC[e["role"]]
        elif e["n_messages"] == 1:            # no coordinator at all (hard-coded pipeline): runs are sequential
            elapsed += _SEC[e["role"]]
    elapsed += max(group.values()) if group else 0
    return {
        "scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"],
        "coord": coord, "runs": runs, "text": text,
        "covered": [t for t in SUBTOPICS if f"## {t}" in low],
        "cited": len(re.findall(r"\[[^\]]+, p\.\d+\]", text)),
        "max_par": max([e["n_task_calls"] for e in coord] or [0]),
        "saw_chars": (coord[-1]["seen_chars"] if coord else None),
        "blind": (coord[-1]["blind_results"] if coord else None),
        "peak_in": max([e["input_tokens"] for e in coord] or [0]),
        "targeted": any("TARGETED" in e["prompt_head"] for e in runs),
        "searchers": [e for e in runs if e["role"] == "searcher" and "TARGETED" not in e["prompt_head"]],
        "seconds": elapsed,
    }


def check_outcome(scenario: str, trace: dict):
    m = _metrics(trace)
    saw, blind = m["saw_chars"], m["blind"]
    if scenario == "simple_question":
        expected = ("a cited answer using exactly ONE subagent run (the coordinator picked only what the question needs) "
                    "and the coordinator saw that subagent's real result")
        conds = [m["cited"] >= 1, len(m["runs"]) == 1, blind == 0]
    else:
        expected = ("all 3 areas covered with citations, delegated in parallel (≥3 Task calls in ONE response), the coordinator "
                    "received every subagent's real result (none was an empty acknowledgement), no context bloat"
                    + (", and the failed film search re-delegated" if scenario == "source_fails" else ""))
        conds = [len(m["covered"]) == 3, m["cited"] >= 3, m["max_par"] >= 3, blind == 0,
                 m["peak_in"] < BLOAT_LIMIT_TOKENS]
    observed = (f"areas covered {len(m['covered'])}/3 · citations {m['cited']} · max Task calls in one response {m['max_par']} · "
                f"subagent runs {len(m['runs'])} · simulated time {m['seconds']} s · coordinator blind to "
                f"{'n/a (no coordinator)' if blind is None else str(blind) + ' result(s)'} · coordinator peak input {m['peak_in']} tokens · "
                f"raised: {m['raised'] or 'no'}")
    return all(conds) and not m["raised"], expected, observed


# ── Flowchart: one left-to-right line; colour = concept, ⭐ = named by the exam guide ──

_CONCEPT = {
    "coord":   ("#DBEAFE", "#0066CC", "coordinator (hub)"),
    "spawn":   ("#EDE9FE", "#7C3AED", "spawning — Task tool / Task calls"),
    "context": ("#FEF3C7", "#D97706", "context passing (prompt in, final message out)"),
    "sub":     ("#D1FAE5", "#059669", "subagent work (isolated context)"),
    "review":  ("#CCFBF1", "#0D9488", "coverage review & re-delegation"),
    "bug":     ("#FFFFFF", "#DC2626", "bug (an exam distractor)"),
}

_NODES = {
    "Q":       ("User question", "box", "coord"),
    "COORD":   ("⭐ Coordinator\\ndecompose · pick subagents", "box", "coord"),
    "GATE":    ("⭐ Task tool in\\nallowedTools?", "diamond", "spawn"),
    "FAN":     ("⭐ Task calls\\n(parallel: ONE response)", "box", "spawn"),
    "CTX":     ("⭐ Complete context in\\nthe PROMPT (+ sources)", "box", "context"),
    "SEARCH":  ("Search subagents\\n(isolated context)", "box", "sub"),
    "ANALYZE": ("Analysis subagent", "box", "sub"),
    "SYNTH":   ("Synthesis subagent", "box", "sub"),
    "BACK":    ("Only the final message\\nreturns to the coordinator", "box", "context"),
    "REVIEW":  ("⭐ Coordinator reviews\\ncoverage & gaps", "box", "review"),
    "DONE":    ("Cited report", "box", "coord"),
    "NOTASK":  ("✗ Task not in\\nallowedTools", "box", "bug"),
    "INHERIT": ("✗ assumes inherited /\\nshared context", "box", "bug"),
    "FIXED":   ("✗ hard-coded pipeline\\nfor every question", "box", "bug"),
    "NARROW":  ("✗ too-narrow\\ndecomposition", "box", "bug"),
    "SEQ":     ("✗ one Task call\\nper turn", "box", "bug"),
    "PEER":    ("✗ results routed around\\nthe coordinator", "box", "bug"),
    "NOREVIEW": ("✗ no gap review,\\nno re-delegation", "box", "bug"),
    "BLOAT":   ("✗ whole transcripts\\nreturned", "box", "bug"),
}
_BUGS = ["NOTASK", "INHERIT", "FIXED", "NARROW", "SEQ", "PEER", "NOREVIEW", "BLOAT"]
_CHAIN = ["Q", "COORD", "GATE", "FAN", "CTX", "SEARCH", "ANALYZE", "SYNTH", "BACK", "REVIEW", "DONE"]
_NOT_REACHED = ("#F3F4F6", "#9CA3AF")
_OK, _BAD = "#BBF7D0", "#FECACA"


def _key(highlighted: bool) -> str:
    rows = "".join(
        f'<TR><TD BGCOLOR="{fill}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD>'
        f'<TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">{text}</FONT></TD></TR>'
        for fill, _line, text in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0">'
             '<FONT POINT-SIZE="10">named by the exam guide (TS 1.2 pp.5–6, TS 1.3 pp.6–7)</FONT></TD></TR>')
    if highlighted:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = handled '
                 'correctly · <B>red</B> = went wrong · grey = not reached</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3">'
            '<TR><TD COLSPAN="2" BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states: dict) -> str:
    highlighted = bool(states)
    lines = ["digraph G {",
             '  rankdir=TB; bgcolor="transparent"; nodesep=0.28; ranksep=0.45; newrank=true;',
             '  node [fontname="Helvetica", fontsize=12, style="rounded,filled", penwidth=2];',
             '  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];']
    for node, (label, shape, concept) in _NODES.items():
        fill, line, _ = _CONCEPT[concept]
        text, style = label, "rounded,filled"
        if highlighted:
            state, suffix = states.get(node, (None, ""))
            fill = {"ok": _OK, "bad": _BAD}.get(state, _NOT_REACHED[0])
            if state is None and concept != "bug":
                line = _NOT_REACHED[1]
            if suffix:
                text = f"{label}\\n{suffix}"
        if concept == "bug":
            style = "rounded,filled,dashed"
        lines.append(f'  {node} [label="{text}", shape={shape}, style="{style}", fillcolor="{fill}", color="{line}"];')
    lines.append("  " + " -> ".join(_CHAIN) + ";")
    lines.append('  REVIEW -> FAN [constraint=false, label="re-delegate", color="#0D9488", fontcolor="#0D9488"];')
    lines.append("  { rank=same; " + "; ".join(_BUGS) + "; }")
    lines.append("  DONE -> NOTASK [style=invis];")
    lines.append(_key(highlighted))
    lines.append("  BLOAT -> KEY [style=invis];")
    lines.append("}")
    return "\n".join(lines)


def node_states(trace) -> dict:
    if not trace:
        return {}
    m = _metrics(trace)
    ev = [e for e in trace["events"] if e["kind"] == "api_call"]
    roles = {e.get("role") for e in ev}
    simple = m["scenario"] == "simple_question"
    s = {"Q": ("ok", "")}
    coord = m["coord"] if any(e.get("role") == "coordinator" for e in ev) else []
    if coord:
        s["COORD"] = ("ok", f"×{len(coord)} turns")
        has_task = any(("Task" in e["tool_names"] or "Agent" in e["tool_names"]) for e in coord)
        s["GATE"] = ("ok", "") if has_task else ("bad", "not allowed")
        if m["max_par"]:
            seq = len(m["searchers"]) >= 2 and m["max_par"] < 2 and not simple
            s["FAN"] = ("bad", f"only {m['max_par']} per response") if seq else ("ok", f"max {m['max_par']} per response")
    if "searcher" in roles:
        s["SEARCH"] = ("ok", f"×{sum(1 for r in m['runs'] if r['role'] == 'searcher')}")
    if "analyst" in roles:
        s["ANALYZE"] = ("ok", "")
    if "synthesizer" in roles:
        s["SYNTH"] = ("ok", "")
    sub_runs = [r for r in m["runs"] if r["role"] in ("analyst", "synthesizer")]
    if m["runs"]:
        s["CTX"] = ("bad", "findings missing") if any(not r["prompt_has_findings"] for r in sub_runs) else ("ok", "")
        s["BACK"] = ("bad", f"{m['blind']} blind result(s)") if (coord and m["blind"]) else ("ok", "")
    if "synthesizer" in roles:
        s["REVIEW"] = ("ok", "re-delegated" if m["targeted"] else "")
    if m["text"]:
        s["DONE"] = ("ok", "") if m["cited"] >= 1 else ("bad", "no citations")
    elif coord or m["runs"]:
        s["DONE"] = ("bad", "no report")

    # the bug nodes light up red only when THIS run shows that bug
    if coord and not any(("Task" in e["tool_names"] or "Agent" in e["tool_names"]) for e in coord):
        s["NOTASK"] = ("bad", "no subagents could be spawned")
    if coord and any(not r["prompt_has_findings"] for r in sub_runs):
        s["INHERIT"] = ("bad", "subagent got no findings")
    if simple and len(m["runs"]) > 1:
        s["FIXED"] = ("bad", f"{len(m['runs'])} runs for a one-fact question")
    elif not coord and m["runs"]:
        s["FIXED"] = ("bad", "no coordinator: one search for the whole topic")
    if coord and not simple and 0 < len({t for t in SUBTOPICS if any(t in r["prompt_head"].lower() for r in m["searchers"])}) < 3:
        s["NARROW"] = ("bad", f"only {len(m['searchers'])} area(s) searched")
    if coord and not simple and len(m["searchers"]) >= 2 and m["max_par"] < 2:
        s["SEQ"] = ("bad", f"{len(m['coord'])} coordinator turns")
    if coord and m["runs"] and m["blind"]:
        s["PEER"] = ("bad", "coordinator blind")
    if m["scenario"] == "source_fails" and "film" not in " ".join(m["covered"]) and not m["targeted"]:
        s["NOREVIEW"] = ("bad", "film silently missing")
    if coord and m["peak_in"] >= BLOAT_LIMIT_TOKENS:
        s["BLOAT"] = ("bad", f"{m['peak_in']} input tokens")
    return s


# ── What the guide demands: TS 1.2 (pp.5–6) and TS 1.3 (pp.6–7) — paraphrased; bullet numbers = order under each heading ──

EXAM_POINTS = (
    ExamPoint("1.2", "K", 1, "Hub-and-spoke: one coordinator manages ALL communication between subagents, error handling and "
              "information routing.", "❌ F (routes around the coordinator) · flowchart"),
    ExamPoint("1.2", "K", 2, "Subagents have isolated context — they don't inherit the coordinator's conversation history.",
              "❌ B · playground “Isolated context”"),
    ExamPoint("1.2", "K", 3, "The coordinator decomposes the task, delegates, aggregates results, and picks which subagents to "
              "invoke based on how complex the query is.", "✅ · playground “Dynamic selection”"),
    ExamPoint("1.2", "K", 4, "Risk: decomposing too narrowly leaves a broad topic only partly covered.",
              "❌ D · playground “Decomposition”"),
    ExamPoint("1.2", "S", 1, "Design coordinators that analyse the query and select subagents dynamically rather than always "
              "running the full pipeline.", "❌ C · playground “Dynamic selection”"),
    ExamPoint("1.2", "S", 2, "Partition the research scope across subagents (distinct subtopics or source types) to minimise "
              "duplication.", "playground “Decomposition” (overlapping)"),
    ExamPoint("1.2", "S", 3, "Iterative refinement: the coordinator evaluates the synthesis for gaps, re-delegates targeted "
              "queries, and re-invokes synthesis until coverage is sufficient.", "❌ G · playground “Review & refinement”"),
    ExamPoint("1.2", "S", 4, "Route all subagent communication through the coordinator — for observability, consistent error "
              "handling and controlled information flow.", "❌ F"),
    ExamPoint("1.3", "K", 1, "The Task tool spawns subagents, and the coordinator's allowedTools must include \"Task\".",
              "❌ A · playground “Spawn tool”"),
    ExamPoint("1.3", "K", 2, "Subagent context must be given explicitly in the prompt — no automatic inheritance and no shared "
              "memory between invocations.", "❌ B · playground “Isolated context”"),
    ExamPoint("1.3", "K", 3, "AgentDefinition: a description, a system prompt and tool restrictions for each subagent type.",
              "✅ AGENTS dict · playground “AgentDefinition tools”"),
    ExamPoint("1.3", "K", 4, "Fork-based session management to explore divergent approaches from a shared analysis baseline.",
              "playground “Session fork”"),
    ExamPoint("1.3", "S", 1, "Put the complete findings from earlier agents directly in the subagent's prompt.",
              "✅ · ❌ B · ❌ H's opposite"),
    ExamPoint("1.3", "S", 2, "Use structured formats that separate content from metadata (source URL, document, page) when "
              "passing context, to preserve attribution.", "playground “Structured findings”"),
    ExamPoint("1.3", "S", 3, "Spawn parallel subagents by emitting several Task calls in ONE coordinator response, not across "
              "separate turns.", "❌ E · playground “Parallel spawning”"),
    ExamPoint("1.3", "S", 4, "Write coordinator prompts as goals and quality criteria, not step-by-step procedures, so subagents "
              "can adapt.", "✅ prompt · playground “Goals, not procedures”"),
)

# ── Lab variants ───────────────────────────────────────────────────────────────

VARIANTS = (
    Variant(
        "correct", "✅ ⭐ Coordinator + subagents, done right", "correct", CORRECT, "broad_topic",
        observe=("Coordinator turn 1 emits THREE Task calls in one response (visual arts, music, film); each searcher runs with only "
                 "its prompt and returns its final message; the coordinator then delegates verification and synthesis, passing the "
                 "complete findings (with source metadata) in each prompt. Result: 3/3 areas, 6 citations, 5 subagent runs, "
                 "simulated 12 s. Switch scenario: simple_question uses ONE subagent; source_fails shows the coordinator reviewing the "
                 "draft, spotting the missing film section and re-delegating a targeted search before re-synthesising."),
        why=("Each part of the design is doing a job: the spawn tool is allowed, the work is split into distinct areas, every prompt "
             "carries everything the subagent needs, independent calls go out together, all results flow back through the "
             "coordinator, and a review step catches gaps."),
    ),
    Variant(
        "A", "⭐❌ A — the Task tool isn't in allowedTools", "distractor", VARIANT_A, "broad_topic",
        observe=("The coordinator has no spawn tool, so it never delegates: zero subagent runs, and it answers from “general "
                 "knowledge with no sources” — 0 citations, 0/3 areas. Nothing crashes, which is the trap: it looks like an answer."),
        why=("Without the spawn tool in the coordinator's tool list there is nothing to call. Defining subagents is not enough — the "
             "coordinator has to be allowed to use the tool that spawns them."),
        fix=("Include the spawn tool in the coordinator's allowed tools: \"Task\" in the exam's wording; the current docs' examples "
             "use \"Agent\" (\"Task\" is a legacy alias). Match both when detecting spawns."),
        source="guide:1.3:K1",
    ),
    Variant(
        "B", "⭐❌ B — assume subagents inherit context", "distractor", VARIANT_B, "broad_topic",
        observe=("The searchers work (their prompts name the area). But the analyst is told only “verify the findings gathered so far” "
                 "and the synthesizer “write the final report from the findings gathered so far” — neither can see the coordinator's "
                 "findings. The analyst answers NO_FINDINGS_PROVIDED, the synthesizer says it has no findings: 0/3 areas, 0 citations. "
                 "The coordinator's gap review notices and retries, spending 9 subagent runs to reach the same wall. On "
                 "simple_question it passes — there is no downstream stage to starve."),
        why=("A subagent starts with a fresh context: the only channel from coordinator to subagent is the prompt string. "
             "Nothing is inherited and nothing is shared between invocations, so “the findings so far” means nothing to it."),
        fix="Put the complete findings — with their source metadata — directly in each subagent's prompt.",
        source="guide:1.3:K2",
    ),
    Variant(
        "C", "⭐❌ C — always run the full pipeline", "distractor", VARIANT_C, "simple_question",
        observe=("The answer is correct and cited, but it took THREE subagent runs (search → verify → synthesise) for a one-fact "
                 "question, versus one in the correct run. On broad_topic it is worse: one search for the whole topic, no "
                 "decomposition — 0/3 areas covered."),
        why=("A hard-coded pipeline ignores how complex the question is: it wastes work on simple queries and cannot decompose a "
             "broad one. The coordinator's job includes choosing which subagents to invoke for this query."),
        fix=("Let the coordinator analyse the query and select subagents dynamically; enforce must-hold rules around it in code "
             "only where a step truly must run every time."),
        source="guide:1.2:S1",
    ),
    Variant(
        "D", "⭐❌ D — decompose too narrowly", "distractor", VARIANT_D, "broad_topic",
        observe=("The coordinator searches only ONE area (visual arts). Every subagent succeeds, the report reads well — and it covers "
                 "1/3 areas with 2 citations. Nothing flags the missing music and film sections."),
        why=("The subagents did exactly what they were told; the hole is in the coordinator's decomposition. Too narrow a split "
             "leaves a broad topic incompletely covered while every individual result looks fine."),
        fix="Fix it at the coordinator: partition the topic into all its major areas and state coverage as a quality criterion.",
        source="guide:1.2:K4",
    ),
    Variant(
        "E", "⭐❌ E — spawn one subagent per turn", "distractor", VARIANT_E, "broad_topic",
        observe=("The result is complete (3/3 areas, 6 citations) but the coordinator takes 6 turns instead of 4 and the simulated "
                 "time is 20 s instead of 12 s: the searches ran one after another. The chart shows the Task calls at one per "
                 "response. On source_fails it is 29 s vs 21 s."),
        why=("Independent subagents only run concurrently when their Task calls arrive in the SAME coordinator response; one call "
             "per turn serialises them and adds a model round trip each time."),
        fix="Emit all independent Task calls together in one response.",
        source="guide:1.3:S3",
    ),
    Variant(
        "F", "⭐❌ F — route results around the coordinator", "distractor", VARIANT_F, "simple_question",
        observe=("The searcher's findings go straight into a pipe; the coordinator only gets “ok - forwarded directly to the "
                 "analyst”. On simple_question it then cannot answer — “I could not confirm the answer”, 0 citations. On broad_topic "
                 "and source_fails the run can still finish, and even repair the film gap, but the coordinator was BLIND to 3 of 5 "
                 "results (4 of 7 on source_fails): it never saw the findings or the film error, so its error handling is guesswork."),
        why=("In hub-and-spoke the coordinator is the single point for communication, error handling and information routing. "
             "Bypassing it costs observability and consistent error handling, even on runs that happen to succeed."),
        fix="Return every subagent result to the coordinator; let it decide what to pass on, and to whom.",
        source="guide:1.2:S4",
    ),
    Variant(
        "G", "⭐❌ G — no gap review or re-delegation", "distractor", VARIANT_G, "source_fails",
        observe=("The film search times out. Without a review step the coordinator accepts the first draft: 2/3 areas, 4 "
                 "citations, 5 runs — the film section is silently missing. On broad_topic (no failure) the same code passes, "
                 "which is why this bug hides until a source fails."),
        why=("Nothing makes the coordinator evaluate the synthesis for gaps, so it can't re-delegate targeted searches or "
             "re-invoke synthesis. Iterative refinement is what turns a partial draft into sufficient coverage."),
        fix=("Have the coordinator evaluate the draft against the coverage criteria, re-delegate targeted queries for what's "
             "missing, and re-invoke synthesis until coverage is sufficient."),
        source="guide:1.2:S3",
    ),
    Variant(
        "H", "❌ H — return the whole subagent transcript", "distractor", VARIANT_H, "broad_topic",
        observe=("The report is still right (3/3, 6 citations), but the coordinator's input balloons to about 8,500 simulated "
                 "tokens, versus about 2,000 in the correct run — each subagent's whole transcript was appended to what the "
                 "coordinator must carry. On source_fails it exceeds 10,000."),
        why=("Only the subagent's FINAL message is supposed to return; keeping its intermediate calls out of the parent is the "
             "point of context isolation. The docs' own warning: many subagents each returning detailed results explodes the "
             "coordinator's context."),
        fix="Return the final message only — a concise, structured summary with its sources.",
        source="docs",
    ),
)

# ── Prose ──────────────────────────────────────────────────────────────────────

TLDR = (
    "A **coordinator** agent splits a big task into distinct parts and hands each to a **subagent** through the spawn tool — "
    "**`Task`** on the exam, **`Agent`** in the current docs. A subagent starts with a **fresh context**: the *only* thing it "
    "receives is the prompt the coordinator writes, and only its **final message** comes back. So a well-built coordinator "
    "(1) is allowed to spawn, (2) decomposes broadly enough, (3) puts the complete findings and their sources in every prompt, "
    "(4) emits independent calls together in one response, (5) keeps every result flowing through itself, and (6) reviews the "
    "draft for gaps and re-delegates."
)

MENTAL_MODEL = ("The coordinator is a project manager who can only send **emails** to contractors: a contractor sees just the "
                "email — never the manager's inbox — and sends back only a final report. Leave the facts out of the email and the "
                "work is wrong; brief only one contractor and the project has a hole.")

WHAT_IT_IS = """
The docs describe subagents as separate agent instances your main agent spawns for focused subtasks, with four benefits:
**context isolation**, **parallelisation**, **specialised instructions** and **tool restrictions**. The exam guide turns that
into an architecture: a **hub-and-spoke** system where a coordinator decomposes the work, delegates, aggregates, and manages
*all* communication and error handling (Guide §6 · TS 1.2, pp.5–6), plus the mechanics of spawning and passing context
(TS 1.3, pp.6–7).

**Sub-concepts — each with its picture to remember and where the exam names it**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Hub-and-spoke coordinator | A switchboard: every call goes through the operator, so the operator knows what is happening and can react to a failure. | ⭐ TS 1.2 · Knowledge 1, Skill 4 · pp.5–6 |
| 2 | Isolated context | Each subagent is a new hire on day one: it knows only what the briefing says. | ⭐ TS 1.2 · Knowledge 2 · pp.5–6; TS 1.3 · Knowledge 2 · pp.6–7 |
| 3 | Decomposition & selection | A manager splits the job by workstream, skips workstreams this job doesn't need — and a plan that covers one workstream has a hole. | ⭐ TS 1.2 · Knowledge 3–4, Skills 1–2 · pp.5–6 |
| 4 | The spawn tool | The coordinator's badge: without `Task` on the allowed list, the door doesn't open. | ⭐ TS 1.3 · Knowledge 1 · pp.6–7 |
| 5 | AgentDefinition | A job description: the role, its instructions, its toolbox. | ⭐ TS 1.3 · Knowledge 3 · pp.6–7 |
| 6 | Explicit context & structured findings | Hand over a labelled file (claim · source · page), not a summary in your own words. | ⭐ TS 1.3 · Skills 1–2 · pp.6–7 |
| 7 | Parallel spawning | Send all the briefing emails at once, not one after another. | ⭐ TS 1.3 · Skill 3 · pp.6–7 |
| 8 | Iterative refinement | Proofread the draft, then send the missing chapter back to be written. | ⭐ TS 1.2 · Skill 3 · pp.5–6 |
| 9 | Goals, not procedures | Give the contractor the goal and the quality bar — a rigid checklist breaks the moment the situation differs. | ⭐ TS 1.3 · Skill 4 · pp.6–7 |
| 10 | Session fork | Photocopy the case file: two investigators, one shared starting point, the original untouched. | ⭐ TS 1.3 · Knowledge 4 · pp.6–7 |

**What a subagent receives — and doesn't** (docs, non-fork subagent)

| # | Receives | Does NOT receive |
|---|---|---|
| 1 | Its own system prompt (`AgentDefinition.prompt`) and the spawn tool's **prompt string** | The parent's conversation history or tool results |
| 2 | Project CLAUDE.md files (unless the definition sets `omitClaudeMd`) | Preloaded skill content, unless listed in `skills` |
| 3 | Its tool definitions (all available to subagents, or only the ones in `tools`) | The parent's system prompt |

**AgentDefinition fields** (docs — the exam names *description*, *system prompt* and *tool restrictions*)

| # | Field | Required? | What it does |
|---|---|---|---|
| 1 | `description` | yes | When Claude should use this subagent — how it chooses |
| 2 | `prompt` | yes | The subagent's system prompt: its role and behaviour |
| 3 | `tools` | no | Allowed tool names; **omitted = inherits every tool available to subagents**; a tool left out isn't in its session at all |
| 4 | `disallowedTools` · `model` · `skills` · `memory` · `mcpServers` · `maxTurns` · `background` … | no | Further optional controls (beyond what the exam names) |

**`Task` or `Agent`?** The guide says the spawn tool is **`Task`** and that `allowedTools` must include it. The current docs say
the tool is **`Agent`** — it shows up as `"Agent"` in `tool_use` blocks and as `"Task"` in the init tool list, `"Task"` was the
name before Claude Code v2.1.63, and the docs advise matching both. For the exam: **Task**. In real code today: know both.

**Hub-and-spoke vs nesting.** The guide's model has the coordinator route everything. The docs *also* let subagents spawn their
own subagents (default: 3 layers deep) and cap that with depth, concurrency (default 20 at once) and spend limits. Designing
for observability and error handling means keeping the coordinator in the middle, as the exam expects.
"""

HOW_IT_WORKS = """
1. **Allow spawning.** The coordinator's tool list includes the spawn tool (`Task`), and each subagent type has a definition:
   description, system prompt, tool restrictions.
2. **Decompose and select.** The coordinator reads the question, splits a broad one into *distinct* areas, and picks only the
   subagents this query needs — a simple question may need just one.
3. **Spawn — in one response.** Independent subagents are requested together, as several `Task` calls in a single coordinator
   response. All their `tool_result` blocks go back in one user message (the same rule you met in D1.1).
4. **Give complete context in the prompt.** Each subagent sees only its prompt. Put the goal, the quality criteria, and any earlier
   findings — as structured data with source URL, document and page — directly in it.
5. **Only the final message returns.** The subagent's own tool calls stay inside it; the coordinator receives its final message
   as the tool result.
6. **Aggregate, review, refine.** The coordinator combines results, checks coverage against the quality criteria, re-delegates
   targeted searches for gaps, and re-invokes synthesis until coverage is sufficient — then answers.
7. **Fork, don't overwrite, to explore.** To try a different approach from a shared analysis baseline, fork the session: the fork
   is a new session with a copy of the history; the original is unchanged.
"""

WHERE_SEEN = """
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): the scenario this page's lab is modelled on — a coordinator
  delegating search, analysis and synthesis to subagents and returning a cited report.
- **Claude Code itself:** built-in subagents such as Explore and Plan, and your own in `.claude/agents/` (docs: create custom
  subagents). Their descriptions decide when Claude delegates.
- **The Agent SDK:** the `agents` option on `query()` defines subagents programmatically; messages from inside a subagent carry a
  `parent_tool_use_id`, which is how you tell it apart from the coordinator.
"""

GUIDE_NOTE = (
    "Grounded in the official docs (verified 2026-09-26 — pages listed above) and the exam guide §6 TS 1.2 (pp.5–6) and TS 1.3 "
    "(pp.6–7), Domain 1 — Agentic Architecture & Orchestration (27%). Section layout inspired by a community concept list "
    "(claudearchitectcertification.com — community source, unverified; no text copied)."
)

LAB_INTRO = """
Pick a starting point and a scenario, **edit the code if you like, and press Run.** You write the *coordinator* — its prompt, the tool
list, and how each subagent is run and what comes back — against a **simulated** research model and a fake search backend. The variants
are the correct design plus eight ways to get it wrong: seven from the exam guide (⭐, exact bullets in the table below) and one from the
docs' own warnings. Some only break on the right scenario — that's what makes them distractors.
"""

DISTRACTORS = (
    ("A · No spawn tool in allowedTools",
     "The subagents are defined and described, so delegation should just happen.",
     "Nothing is callable: the coordinator answers alone, unsourced — and nothing errors.",
     "Put the spawn tool (`Task` on the exam, `Agent` in current docs) in the coordinator's allowed tools.", "guide:1.3:K1"),
    ("B · Assume subagents inherit context",
     "The coordinator obviously has the findings, so “write the report from what we have” should work.",
     "A subagent starts fresh: only its prompt reaches it, and nothing is shared between invocations — it has no findings.",
     "Put the complete findings, with source metadata, in the subagent's prompt.", "guide:1.3:K2"),
    ("C · Always run the full pipeline",
     "A fixed search → verify → write sequence is predictable and easy to reason about.",
     "One-fact questions pay for three subagents; broad ones never get decomposed.",
     "Let the coordinator select subagents by query complexity.", "guide:1.2:S1"),
    ("D · Decompose too narrowly",
     "Every subagent succeeds and the report reads fluently — it must be complete.",
     "The coordinator only assigned one area, so the report silently covers a third of the topic.",
     "Partition the topic into all its major areas; make coverage a stated quality criterion.", "guide:1.2:K4"),
    ("E · One Task call per turn",
     "Waiting for each result is simple, and the final report is identical.",
     "Independent work is serialised: more coordinator turns and more wall-clock time.",
     "Emit all independent Task calls in a single response.", "guide:1.3:S3"),
    ("F · Route results around the coordinator",
     "Handing findings straight to the next subagent saves a hop.",
     "The coordinator is blind: it can't see failures, handle errors consistently or answer from what it never received.",
     "All subagent communication goes through the coordinator.", "guide:1.2:S4"),
    ("G · No gap review or re-delegation",
     "The first draft came back, so the coordinator can just return it.",
     "A failed or missing area is never noticed; the report is silently incomplete.",
     "Evaluate the draft for gaps, re-delegate targeted searches, re-invoke synthesis.", "guide:1.2:S3"),
    ("H · Return the whole subagent transcript",
     "More information can't hurt — the coordinator can see everything the subagent did.",
     "The coordinator's context balloons with intermediate calls, defeating context isolation.",
     "Return only the subagent's final message, as a concise structured summary with sources.", "docs"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Single agent", "Coordinator + subagents (hub-and-spoke)", "Peer-to-peer / shared memory",
                        "Fixed pipeline")
SIDE_BY_SIDE_ROWS = (
    ("1", "Who decides what runs", "The one agent, in one context", "The coordinator, per query (TS 1.2)",
     "Each agent, ad hoc", "The developer, in advance (TS 1.6)"),
    ("2", "Context", "One growing conversation", "Isolated per subagent; only the prompt goes in (TS 1.3)",
     "Assumed shared — it isn't", "Whatever the code passes"),
    ("3", "Communication path", "—", "Everything through the coordinator", "Directly between agents", "Code hands results along"),
    ("4", "Errors", "Handled inline", "Seen and handled centrally by the coordinator", "Invisible to anyone above",
     "Whatever the code handles"),
    ("5", "Best for", "Small or tightly coupled tasks", "Broad tasks that split into independent parts", "— (an anti-pattern here)",
     "Predictable multi-step work"),
    ("6", "Typical failure", "Context fills up with noise", "Narrow decomposition; missing context in prompts", "No observability",
     "Can't adapt to the query"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.4; ranksep=0.45;
  node [fontname="Helvetica", fontsize=11, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=10, color="#6B7280"];
  Q1 [shape=diamond, label="Does the task split into\\nindependent parts?"];
  ONE [shape=box, label="One agent\\n(or one subagent to keep noisy\\nwork out of the main context)"];
  Q2 [shape=diamond, label="Do the parts need each\\nother's results?"];
  PAR [shape=box, fillcolor="#EDE9FE", color="#7C3AED", label="Spawn them together:\\nseveral Task calls in ONE response\\n(guide TS 1.3, Skill 3)"];
  SEQ [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Chain them THROUGH the coordinator:\\nresult -> coordinator -> next prompt\\n(guide TS 1.2, Skill 4)"];
  Q3 [shape=diamond, label="Does each subagent's prompt\\ncarry everything it needs?"];
  CTX [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Add the complete findings + sources\\nto the prompt (guide TS 1.3, Skills 1-2)"];
  Q4 [shape=diamond, label="Can coverage be checked\\nagainst criteria?"];
  REV [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Coordinator reviews the draft, re-delegates\\ntargeted searches, re-synthesises\\n(guide TS 1.2, Skill 3)"];
  Q1 -> ONE [label="no"]; Q1 -> Q2 [label="yes"];
  Q2 -> PAR [label="no"]; Q2 -> SEQ [label="yes"];
  PAR -> Q3; SEQ -> Q3;
  Q3 -> CTX [label="no"]; Q3 -> Q4 [label="yes"]; CTX -> Q4;
  Q4 -> REV [label="yes"];
}'''

EXPERIMENTS = (
    "Run ✅ on broad_topic and read the first coordinator turn in the output: THREE Task calls in one response. Then run ❌ E and "
    "count the coordinator turns and the simulated time.",
    "Run ✅ on simple_question: one subagent. Run ❌ C on it: same answer, three runs. Who chose the pipeline in each?",
    "Run ❌ B on broad_topic and read what the analyst and synthesizer were sent. Then edit the `LABELS` dict so each one gets the "
    "real `prompt` — and watch the report come back.",
    "Run ✅ on source_fails and follow the film area: failed search → gap noticed → targeted retry → second synthesis. Then delete the "
    "last line of the coordinator prompt (the gap review) and run again.",
    "In ✅, change `ALLOWED_TOOLS` to `[]` and run: no subagents, no sources, no error.",
    "In ❌ H, count the tokens in the trace's “in tokens” column for the coordinator's calls, then compare with ✅.",
)

QUESTIONS = (
    Question(
        q=("A research coordinator gets good results from three search subagents, then calls a synthesis subagent with the prompt "
           "\"Combine the findings above into a final report.\" The synthesis subagent replies that it has no findings to work with. "
           "What is the most likely root cause?"),
        opts=("The synthesis subagent's tool list is too restrictive.",
              "The findings were never included in the synthesis subagent's prompt, and subagents don't inherit the coordinator's "
              "conversation.",
              "The search subagents returned too few tokens.",
              "The coordinator's max_tokens is set too low."),
        ans=1,
        explain=("A subagent starts with a fresh context; the only channel from the coordinator is the prompt string. “The findings "
                 "above” refers to a conversation the subagent cannot see. Tool restrictions, result size and the coordinator's "
                 "max_tokens would not make a subagent report that it received nothing."),
        scenarios=(3,), ts="1.3",
    ),
    Question(
        q=("A research system answers “AI in the creative industries” with a polished report about digital art only; music and film are "
           "absent. Logs show every subagent completed its assigned task without error. What is the best first fix?"),
        opts=("Give each search subagent more turns.",
              "Change the coordinator's decomposition so the topic is partitioned into all its major areas.",
              "Strengthen the synthesis subagent's system prompt.",
              "Switch the synthesis subagent to a larger model."),
        ans=1,
        explain=("Every subagent did what it was assigned — the gap is in what the coordinator assigned. Too-narrow decomposition "
                 "leaves a broad topic incompletely covered; more turns, a better synthesis prompt or a bigger model can't add "
                 "areas nobody was asked to research."),
        scenarios=(3,), ts="1.2",
    ),
    Question(
        q=("A coordinator needs three independent searches. It requests one subagent per turn, and total latency is roughly the sum of "
           "the three searches. Which change most directly reduces it?"),
        opts=("Shorten each subagent's system prompt.",
              "Have the coordinator emit all three Task calls in a single response.",
              "Cache the search results between runs.",
              "Run the synthesis subagent before the searches."),
        ans=1,
        explain=("Independent subagents run concurrently when their spawn calls arrive in the same coordinator response; one per turn "
                 "serialises them. Shorter prompts and caching don't change the ordering, and synthesis needs the findings first."),
        scenarios=(3,), ts="1.3",
    ),
    Question(
        q=("A coordinator configured with three well-described subagents keeps answering from its own knowledge. It never delegates and "
           "no errors appear. Which cause is most likely?"),
        opts=("The subagent descriptions are too long.",
              "The coordinator's allowedTools does not include the spawn tool (\"Task\").",
              "The subagents are sharing memory with the coordinator.",
              "The coordinator has no CLAUDE.md."),
        ans=1,
        explain=("Defining subagents isn't enough: the coordinator must be allowed to use the tool that spawns them. Without it there is "
                 "nothing to call, so it falls back to answering alone — silently."),
        scenarios=(3,), ts="1.3",
    ),
    Question(
        q=("After upgrading the Agent SDK, your code that detects subagent spawns by matching tool_use blocks named \"Task\" finds "
           "nothing, although delegation still happens. What do the docs suggest?"),
        opts=("Subagents were disabled by the upgrade.",
              "Match both \"Task\" and \"Agent\" — the tool is now named \"Agent\" and \"Task\" is a legacy alias.",
              "Only the init tool list can be used to detect spawns.",
              "Re-define the subagents with a new AgentDefinition."),
        ans=1,
        explain=("The docs say the tool appears as \"Agent\" in tool_use blocks (before v2.1.63 it was \"Task\") and advise matching both "
                 "values to stay compatible across versions."),
        basis="docs", in_bank=False,
    ),
    Question(
        q=("A subagent reads forty files and runs a dozen searches while investigating. What does the parent agent receive?"),
        opts=("All forty files, so it can double-check.",
              "The subagent's final message as the tool result — its intermediate calls and results stay inside the subagent.",
              "A live stream of every call the subagent makes.",
              "Nothing until the parent resumes the subagent."),
        ans=1,
        explain=("Per the docs, only the subagent's final message returns to the parent; intermediate tool calls and results stay "
                 "in the subagent, which is why delegating noisy work keeps the main context small."),
        basis="docs", in_bank=False,
    ),
)

FAQ = (
    ("Is it called Task or Agent?",
     "The exam guide says **Task** and says `allowedTools` must include it. The current docs call the tool **Agent** (renamed in Claude "
     "Code v2.1.63; `Task` remains as a legacy alias) and use `\"Agent\"` in their `allowed_tools` examples. Answer with Task on the exam; "
     "in real code match both."),
    ("Can subagents spawn subagents?",
     "The docs say yes — by default up to 3 layers deep, adjustable, with concurrency (default 20) and spend limits. The exam's "
     "hub-and-spoke model keeps the coordinator in the middle for observability and error handling, so design that way."),
    ("What actually comes back from a subagent?",
     "Its final message, as the spawn tool's result. Its own tool calls and results stay inside it. The parent may summarise the message "
     "in its own reply."),
    ("Subagent or fork?",
     "A subagent starts fresh (it gets only the prompt). A **fork** subagent inherits the parent conversation instead. Separately, a "
     "**session fork** copies a session's history into a new session so you can try another direction — the original is unchanged, but "
     "files are not branched."),
    ("What happens past the concurrent-subagent limit?",
     "Per the docs, the spawn is refused with the text “Concurrent subagent limit reached” until the running count drops — it isn't "
     "queued. The playground's “Parallel spawning” tab lets you set the limit and watch the coordinator recover."),
    ("Does the simulated coordinator behave like real Claude?",
     "No. It follows its system prompt by keyword (“parallel”, “gaps”, “step 1”…) so failures are reproducible. Real models interpret "
     "prompts far less literally — the mechanics (context isolation, the spawn tool, only the final message returning) are the "
     "documented part."),
)

# ── Agent playground: one message box per sub-concept ──────────────────────────

_BROAD = "How is AI changing the creative industries? Give me a cited report."
_SIMPLE = "In what year did the Eiffel Tower open to the public?"

PLAYGROUND_INTRO = """
Ask a research question and watch a **coordinator delegate to subagents** while you change the developer-side settings: is the spawn
tool allowed, what context each subagent receives, parallel or one-at-a-time, how many may run at once, how the coordinator is
prompted, whether a source fails, whether the coordinator reviews the draft. The exact coordinator prompt built from your settings is
shown on every run, and each subagent shows **precisely what it received** — the docs' rule that the prompt is the only channel.
The hub-and-spoke rule (Guide TS 1.2 Skill 4) is exercised in the code lab (❌ F).
"""

PLAYGROUND = (
    PlayTab(
        "task_tool", "⭐ Spawn tool", "none",
        "The spawn tool is the coordinator's badge: without `Task` on the allowed list the door never opens — and nothing tells you.",
        "guide:1.3:K1",
        "For the coordinator to invoke subagents, the spawn tool has to be in its allowed tools — `Task` in the exam guide, `Agent` in the "
        "current docs' examples (the docs say to match both). Defining subagents alone does nothing. With the tool removed, the simulated "
        "coordinator falls back to answering alone, with no sources.",
        "agent-sdk/subagents § Detect subagent invocation; guide TS 1.3 Knowledge 1",
        ("allow_task",), {"allow_task": "yes"}, (_BROAD, _SIMPLE),
        ("“yes”: three parallel searches, verify, synthesise — a cited report.",
         "“no”: zero subagent runs and a report with “[no sources]” — no error anywhere.",
         "Try the simple question with the tool off: same silent fallback."),
        engine="research"),
    PlayTab(
        "context", "⭐ Isolated context", "none",
        "A subagent is a new hire on day one: it knows only what the briefing says — never the manager's inbox.",
        "guide:1.3:K2",
        "A non-fork subagent starts with a fresh context. The only content the parent passes is the spawn tool's prompt string, so the "
        "findings it needs must be IN that prompt; there is no inheritance and no shared memory between invocations (docs: “What "
        "subagents inherit”). “Just a short label” shows what goes wrong when you assume otherwise.",
        "agent-sdk/subagents § What subagents inherit; guide TS 1.3 Knowledge 2, Skill 1",
        ("context_mode",), {"context_mode": "full_prompt"}, (_BROAD,),
        ("“complete findings in the prompt”: a full report.",
         "“just a short label”: the analyst and synthesizer received no findings — open their “received” lines. 0/3 areas, no citations; the "
         "coordinator's gap review retries but each retry hits the same wall (9 runs)."),
        engine="research"),
    PlayTab(
        "agentdef", "⭐ AgentDefinition tools", "none",
        "An AgentDefinition is a job description: the role, its instructions — and the toolbox it is given.",
        "guide:1.3:K3",
        "Each subagent type has a description, a system prompt and tool restrictions (`tools`). Omitting `tools` inherits every tool "
        "available to subagents; listing tools restricts it, and a tool you leave out simply isn't in the subagent's session — no "
        "prompt, no error. Here you can remove the searcher's `web_search`.",
        "agent-sdk/subagents § AgentDefinition configuration; Tool restrictions",
        ("searcher_has_search",), {"searcher_has_search": "yes"}, (_BROAD,),
        ("“includes web_search”: normal run.",
         "“left out”: every searcher answers SEARCH_FAILED (“no search tool”) — open a searcher run to see its tools list is empty.",
         "Notice the restriction was silent: least privilege is helpful, but the coordinator has to read the result."),
        engine="research"),
    PlayTab(
        "structured", "⭐ Structured findings", "none",
        "Hand over a labelled file (claim · source · page), not a summary in your own words — or nobody can tell where a claim came from.",
        "guide:1.3:S2",
        "When context passes between agents, use a structured format that keeps content separate from metadata — source URL, document "
        "name, page — so the final report can cite. Flatten it to bare claims and the attribution is gone; the synthesizer can only mark "
        "claims “[no source]”.",
        "guide TS 1.3 Skill 2 (a design rule; the docs describe the prompt as the only channel)",
        ("findings_format",), {"findings_format": "structured"}, (_BROAD,),
        ("“structured”: every claim ends with [document, p.N].",
         "“claims only”: the report still has all three areas but 0 citations and six “[no source]” claims."),
        engine="research"),
    PlayTab(
        "parallel", "⭐ Parallel spawning", "none",
        "Send all the briefing emails at once, not one after another — and know the mailbox has a size limit.",
        "guide:1.3:S3",
        "Independent subagents run concurrently when their Task calls arrive in ONE coordinator response; one per turn serialises them. "
        "The docs add a cap: by default at most 20 subagents run at once, and past it the spawn is **refused** with “Concurrent subagent "
        "limit reached” — not queued. Lower the limit to 2 and watch the coordinator recover (if it reviews gaps).",
        "guide TS 1.3 Skill 3; agent-sdk/subagents § Cap subagent depth, concurrency, and spend",
        ("parallel", "max_concurrent", "review_gaps"), {"parallel": "yes", "max_concurrent": 20, "review_gaps": "yes"}, (_BROAD,),
        ("Parallel with limit 20: 4 coordinator turns and 12 simulated seconds.",
         "“one subagent per turn”: 6 turns and 20 s for the same report.",
         "Parallel with limit 2 and gap review “yes”: the third search is refused, the coordinator notices film is missing and retries — 21 s, complete.",
         "Same limit with review “no”: the refused search is never retried — 2/3 areas."),
        engine="research"),
    PlayTab(
        "select", "⭐ Dynamic selection", "none",
        "A good manager staffs the job, not the org chart: a one-line question doesn't need a three-team project.",
        "guide:1.2:S1",
        "The coordinator analyses the query and chooses which subagents to invoke instead of always running the full pipeline. Ask a "
        "one-fact question and an adaptive coordinator uses one subagent; a fixed step-by-step prompt runs search → verify → synthesise anyway.",
        "guide TS 1.2 Knowledge 3, Skill 1",
        ("prompt_style",), {"prompt_style": "goal"}, (_SIMPLE, _BROAD),
        ("Simple question with “goals + quality criteria”: 1 subagent run, 4 s.",
         "Same question with “fixed step-by-step”: 3 runs, 12 s — the same answer, three times the work."),
        engine="research"),
    PlayTab(
        "goals", "⭐ Goals, not procedures", "none",
        "Give the contractor the goal and the quality bar — a rigid checklist breaks the moment the situation differs.",
        "guide:1.3:S4",
        "Coordinator prompts should state research goals and quality criteria, not a step-by-step procedure, so subagents (and the "
        "coordinator) can adapt. In this simulation a procedural prompt has no delegation-in-parallel or gap-review wording, so a failed "
        "source goes unnoticed. (Real Claude's behaviour with such a prompt is less literal — this is a stand-in.)",
        "guide TS 1.3 Skill 4",
        ("prompt_style", "fail_source"), {"prompt_style": "goal", "fail_source": "yes"}, (_BROAD,),
        ("Goal-based with the film source failing: the coordinator re-delegates and finishes with 3/3 areas.",
         "Procedural with the same failure: sequential turns (20 s) and 2/3 areas — the fixed steps had no place for “notice the gap”."),
        engine="research"),
    PlayTab(
        "decompose", "⭐ Decomposition", "none",
        "A manager who staffs only one workstream has a plan with a hole; two staffing the same one are paying twice.",
        "guide:1.2:K4",
        "The coordinator partitions the research scope across subagents: distinct areas minimise duplication. Too narrow a split leaves a "
        "broad topic incompletely covered even though every subagent succeeds; overlapping areas research the same sources twice.",
        "guide TS 1.2 Knowledge 4, Skill 2",
        ("decomposition",), {"decomposition": "distinct"}, (_BROAD,),
        ("“distinct”: 3/3 areas, 6 citations.",
         "“only the single most prominent area”: 1/3 — and the report reads fine.",
         "“overlapping”: music is researched twice — the note counts 2 duplicated findings and the run costs more tokens."),
        engine="research"),
    PlayTab(
        "refine", "⭐ Review & refinement", "none",
        "Proofread the draft, then send the missing chapter back — a draft is not a deliverable.",
        "guide:1.2:S3",
        "Iterative refinement: the coordinator evaluates the synthesis for gaps, re-delegates targeted searches, and re-invokes synthesis "
        "until coverage is sufficient. Make the film source fail and switch the review on and off.",
        "guide TS 1.2 Skill 3",
        ("review_gaps", "fail_source"), {"review_gaps": "yes", "fail_source": "yes"}, (_BROAD,),
        ("Review “yes” with the failure: gap noticed, targeted film search, second synthesis — 7 runs, 21 s, 3/3 areas.",
         "Review “no”: 5 runs, 12 s, 2/3 areas — faster and silently incomplete.",
         "Failure “no” and review “yes”: no gap, so no extra work — refinement only costs when it is needed."),
        engine="research"),
    PlayTab(
        "fork", "⭐ Session fork", "none",
        "A session fork is a photocopy of the case file: two investigators, one shared starting point, the original untouched.",
        "guide:1.3:K4",
        "To explore divergent approaches from a shared analysis baseline, fork the session: the fork is a NEW session that starts with a "
        "copy of the original's history and gets its own session id; the original stays unchanged and both can be resumed separately. "
        "Forking branches the conversation, **not the filesystem** — file edits a forked agent makes are real.",
        "agent-sdk/sessions § Fork to explore alternatives",
        (), {}, ("Instead of JWT, outline how OAuth2 would work",),
        ("Fork S1, add a message to the fork only, and compare the two histories.",
         "Fork the fork (S3 from S2): each keeps its own history.",
         "Read the caption: what does a fork not protect you from?"),
        engine="fork"),
)

CONTENT = ConceptContent(
    slug="subagents",
    tldr=TLDR,
    mental_model=MENTAL_MODEL,
    what_it_is=WHAT_IT_IS,
    how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN,
    guide_note=GUIDE_NOTE,
    docs_refs=DOC_REFS,
    docs_verified_on=DOCS_VERIFIED_ON,
    grounding=GROUNDING,
    flow_dot=flow_dot,
    node_states=node_states,
    lab_intro=LAB_INTRO,
    variants=VARIANTS,
    check_outcome=check_outcome,
    distractors=DISTRACTORS,
    side_by_side_headers=SIDE_BY_SIDE_HEADERS,
    side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT,
    experiments=EXPERIMENTS,
    questions=QUESTIONS,
    faq=FAQ,
    related=("agentic-loops", "subagent-state-handoff", "task-decomposition", "session-state"),
    exam_points=EXAM_POINTS,
    playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO,
    scenarios=("broad_topic", "simple_question", "source_fails"),
    show_ledger=False,
)
