"""
D1.6 Subagent State Handoff — what travels between agents, and in what shape. Guide TS 1.3 (context passing: complete
findings in the prompt, structured content + metadata, no shared memory; pp.6–7), TS 5.4 (phase summaries injected into the
next phase, state exports injected on resume; pp.21–22) and TS 1.4 (structured handoff to humans — covered in depth on the
D1.5 Escalation page; p.7).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-27); official docs fetched 2026-09-26/27 (DOC_REFS). Every
claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

import json

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-27"
_C = "https://code.claude.com/docs/en"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (
    DocRef("Subagents in the SDK — What subagents inherit", f"{_C}/agent-sdk/subagents"),
    DocRef("Create custom subagents (Claude Code) — context received, best practices", f"{_C}/sub-agents"),
    DocRef("Work with sessions — resume across hosts (Agent SDK)", f"{_C}/agent-sdk/sessions"),
    DocRef("Prompting best practices — state management, multi-context-window work", f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices"),
)

GROUNDING = (
    Claim("A non-fork subagent starts with a fresh context; the ONLY content passed from the parent is the spawn tool's prompt "
          "string, so file paths, errors and decisions it needs must be in that prompt.", "docs", "agent-sdk/subagents § What subagents inherit"),
    Claim("Only the subagent's final message returns to the parent; its intermediate tool calls and results stay inside it.",
          "docs", "agent-sdk/subagents § Benefits (Context isolation)"),
    Claim("Spawning many subagents that each return detailed results risks context explosion in the coordinator.",
          "docs", "sub-agents § Best practices (Don't)"),
    Claim("Chaining subagents: each returns its results to Claude, which passes context to the next.", "docs", "sub-agents § Common patterns — Chain subagents"),
    Claim("Use structured formats (e.g. JSON) for structured state such as test results or task status; free text for progress notes.",
          "docs", "claude-prompting-best-practices § State management best practices"),
    Claim("Instead of relying on session resume, capture the results you need as application state and pass them into a fresh "
          "session's prompt.", "docs", "agent-sdk/sessions § Resume across hosts"),
    Claim("Subagent context must be provided explicitly in the prompt: subagents don't inherit parent context or share memory "
          "between invocations.", "guide", "TS 1.3 · Knowledge 2 · pp.6–7"),
    Claim("Include complete findings from earlier agents directly in the subagent's prompt (e.g. search results and document "
          "analyses passed to the synthesis subagent).", "guide", "TS 1.3 · Skill 1 · pp.6–7"),
    Claim("Use structured data formats that separate content from metadata (source URLs, document names, page numbers) when "
          "passing context, to preserve attribution.", "guide", "TS 1.3 · Skill 2 · pp.6–7"),
    Claim("Summarise one exploration phase's key findings before spawning agents for the next phase and inject the summary into "
          "their initial context.", "guide", "TS 5.4 · Skill 3 · pp.21–22"),
    Claim("Crash recovery: agents export structured state to a known location; the coordinator loads a manifest on resume and "
          "injects it into agent prompts.", "guide", "TS 5.4 · Knowledge 4, Skill 4 · pp.21–22"),
    Claim("Handoffs to humans use a structured summary (customer id, root cause, refund amount, recommended action) because the "
          "human lacks the transcript.", "guide", "TS 1.4 · Knowledge 3, Skill 3 · p.7 (D1.5 page)"),
    Claim("The page's 'what goes in a handoff' checklist (goal, complete findings with metadata, decisions, what's left) is this "
          "workbench's synthesis of the guide and docs points above.", "recommendation", "TS 1.3 S1–S2, TS 5.4 S3–S4"),
    Claim("The findings (example.com), token sizes, the 3,000-token context budget and what an over-budget agent does are invented.",
          "simulated", "utils/handoff_lab.py"),
)

CORRECT = r'''import json

from utils.handoff_lab import FINDINGS, PHASE1_SUMMARY, SAVED_STATE, TASK, run_agent, submit   # SIMULATED agents


def as_payload(findings):
    # structured: the content kept separate from its metadata, so attribution survives the hop
    return json.dumps([{"claim": f["claim"],
                        "source": {"url": f["source_url"], "document": f["document"], "page": f["page"]}}
                       for f in findings], indent=0)


if TASK == "synthesize":
    # the synthesizer sees ONLY this prompt: give it ALL the findings, each with its source
    result = run_agent("synthesizer", "Write a cited report on AI in the creative industries from ALL of these "
                                      "findings (JSON; cite each claim's source):\n" + as_payload(FINDINGS))
elif TASK == "next_phase":
    # summarise what the last phase established and inject it into the next phase's first prompt
    result = run_agent("explorer", "Phase 2: trace the dependencies of ledger.post_refund.\n"
                                   "What phase 1 already established:\n" + PHASE1_SUMMARY)
else:   # resume_agent
    # the agent exported its state before the crash; inject it so the agent continues instead of restarting
    result = run_agent("explorer", "Continue the refund-flow exploration from your saved state - do not start over:\n"
                                   + json.dumps(SAVED_STATE))
print(result[:400])
submit(result)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


_SYN = '''"findings (JSON; cite each claim's source):\\n" + as_payload(FINDINGS))'''
VARIANT_A = _swap(CORRECT, _SYN, '''"findings the search agents gathered.")   # WRONG: a pointer, not the content''')
VARIANT_B = _swap(CORRECT, _SYN, '''"findings:\\n" + " ".join(f["claim"] for f in FINDINGS))   # WRONG: prose - metadata dropped''')
VARIANT_C = _swap(CORRECT, _SYN, '''"findings:\\n" + RAW_TRANSCRIPTS)   # WRONG: the agents' whole transcripts''')
VARIANT_C = _swap(VARIANT_C, "from utils.handoff_lab import FINDINGS, PHASE1_SUMMARY, SAVED_STATE, TASK, run_agent, submit",
                  "from utils.handoff_lab import FINDINGS, PHASE1_SUMMARY, RAW_TRANSCRIPTS, SAVED_STATE, TASK, run_agent, submit")
VARIANT_D = _swap(CORRECT, _SYN, '''"findings (JSON):\\n" + as_payload(FINDINGS[:2]))   # WRONG: "keep it short" - only the top 2''')
VARIANT_E = _swap(CORRECT, '''"Phase 2: trace the dependencies of ledger.post_refund.\\n"
                                   "What phase 1 already established:\\n" + PHASE1_SUMMARY)''',
                  '''"Phase 2: trace the dependencies of ledger.post_refund.")   # WRONG: phase-1 findings not passed on''')
VARIANT_F = _swap(CORRECT, '''"Continue the refund-flow exploration from your saved state - do not start over:\\n"
                                   + json.dumps(SAVED_STATE))''',
                  '''"Continue the refund-flow exploration.")   # WRONG: assumes it remembers - the saved state isn't passed''')

# ── Check, chart ───────────────────────────────────────────────────────────────

_N = {"cited_report": 6, "long_research": 24}


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "handoff_agent"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "ev": ev[-1] if ev else None}


def _diagnose(f):
    e, sc = f["ev"], f["scenario"]
    if e is None:
        return False, None, f"no agent was run ({f['raised'] or 'nothing happened'})"
    if sc in _N:
        n = _N[sc]
        txt = (f"prompt {e['prompt_tokens']} tokens (budget {3000}) · claims received {e['claims_received']}/{n} · "
               f"used {e['claims_used']} · cited {e['cited']}")
        if e["over_budget"]:
            return False, "TRANSCRIPT", txt
        if e["claims_received"] == 0:
            return False, "POINTER", txt
        if e["claims_received"] < n:
            return False, "LOSSY", txt
        if e["cited"] < n:
            return False, "PROSE", txt
        return True, None, txt
    txt = f"file reads {e['reads']} · phase-1 summary in prompt: {e['had_summary']} · saved state in prompt: {e['had_state']}"
    if sc == "next_phase":
        return (e["reads"] <= 2, None if e["reads"] <= 2 else "NOSUMMARY", txt)
    return (e["reads"] <= 1, None if e["reads"] <= 1 else "NOSTATE", txt)


EXPECTED = {"cited_report": "all 6 findings received and cited, within the context budget",
            "long_research": "all 24 findings received and cited, within the context budget",
            "next_phase": "the phase-2 agent builds on phase 1 (≤ 2 file reads), no re-exploration",
            "crash_resume": "the agent continues from its saved state (1 step), not from scratch"}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok and not trace["status"]["raised"], EXPECTED[scenario], txt


_CONCEPT = {
    "src":    ("#EDE9FE", "#7C3AED", "upstream agent's results"),
    "pack":   ("#FEF3C7", "#D97706", "packing the handoff (what + shape)"),
    "hop":    ("#DBEAFE", "#0066CC", "the only channel: the prompt"),
    "use":    ("#D1FAE5", "#059669", "downstream agent can act"),
    "bug":    ("#FFFFFF", "#DC2626", "bug (an exam distractor)"),
}
_NODES = {
    "UP":     ("Upstream agent finishes\\n(only its final message\\ncomes back)", "box", "src"),
    "Q":      ("What does the next\\nagent need?", "diamond", "pack"),
    "ALL":    ("⭐ the COMPLETE findings", "box", "pack"),
    "META":   ("⭐ structured: content +\\nmetadata (url, doc, page)", "box", "pack"),
    "SUM":    ("⭐ a phase summary\\nfor the next phase", "box", "pack"),
    "STATE":  ("⭐ exported state\\nfor a resumed agent", "box", "pack"),
    "PROMPT": ("⭐ all of it IN the prompt\\n(no shared memory)", "box", "hop"),
    "DOWN":   ("Downstream agent: cites,\\nbuilds on, continues", "box", "use"),
    "POINTER": ("✗ a pointer (“the findings\\nfrom earlier”)", "box", "bug"),
    "PROSE":  ("✗ prose — sources dropped", "box", "bug"),
    "LOSSY":  ("✗ “keep it short” — only\\nsome findings", "box", "bug"),
    "TRANSCRIPT": ("✗ whole transcripts —\\ncontext blown", "box", "bug"),
    "NOSUMMARY": ("✗ next phase starts blind\\n→ re-exploration", "box", "bug"),
    "NOSTATE": ("✗ resumed without its\\nstate → restart", "box", "bug"),
}
_PACK = ["ALL", "META", "SUM", "STATE"]
_BUGS = ["POINTER", "PROSE", "LOSSY", "TRANSCRIPT", "NOSUMMARY", "NOSTATE"]
_EXP = {"cited_report": ["ALL", "META"], "long_research": ["ALL", "META"], "next_phase": ["SUM"], "crash_resume": ["STATE"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 1.3 pp.6–7, TS 5.4 pp.21–22)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = what this handoff '
                 'needed · <B>red</B> = the bug your run shows · grey = not this scenario</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3"><TR><TD COLSPAN="2" '
            'BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states):
    hl = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.25; ranksep=0.5; newrank=true;',
             '  node [fontname="Helvetica", fontsize=12, style="rounded,filled", penwidth=2];',
             '  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];']
    for node, (label, shape, concept) in _NODES.items():
        fill, line, _ = _CONCEPT[concept]
        text = label
        if hl:
            st_, suf = states.get(node, (None, ""))
            fill = {"ok": "#BBF7D0", "bad": "#FECACA"}.get(st_, "#F3F4F6")
            if st_ is None and concept != "bug":
                line = "#9CA3AF"
            if suf:
                text = f"{label}\\n{suf}"
        style = "rounded,filled,dashed" if concept == "bug" else "rounded,filled"
        lines.append(f'  {node} [label="{text}", shape={shape}, style="{style}", fillcolor="{fill}", color="{line}"];')
    lines.append("  UP -> Q;")
    lines += [f"  Q -> {n}; {n} -> PROMPT;" for n in _PACK]
    lines.append("  PROMPT -> DOWN;")
    lines.append("  { rank=same; " + "; ".join(_PACK) + "; }")
    lines.append("  { rank=same; " + "; ".join(_BUGS) + "; }")
    lines.append("  DOWN -> POINTER [style=invis];")
    lines.append(_key(hl))
    lines.append("  NOSTATE -> KEY [style=invis];")
    lines.append("}")
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"UP": ("ok", ""), "Q": ("ok", "")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "needed here")
    s["PROMPT"] = ("ok", "") if ok else ("bad", "missing or wrong content")
    s["DOWN"] = ("ok", "") if ok else ("bad", "couldn't do the job")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("1.3", "K", 2, "Subagent context must be provided explicitly in the prompt — no inherited parent context, no memory "
              "shared between invocations.", "❌ A · ❌ F · playground “Complete findings”, “Resume with state”"),
    ExamPoint("1.3", "S", 1, "Put the complete findings from earlier agents directly into the subagent's prompt.",
              "✅ · ❌ A · ❌ D"),
    ExamPoint("1.3", "S", 2, "Pass context in structured formats that separate content from metadata (source URL, document, page) "
              "so attribution survives.", "✅ as_payload() · ❌ B · playground “Structure & metadata”"),
    ExamPoint("5.4", "S", 3, "Summarise one phase's key findings before spawning the next phase's agents, and inject the summary "
              "into their initial context.", "✅ next_phase · ❌ E · playground “Phase summary”"),
    ExamPoint("5.4", "K", 4, "Crash recovery: each agent exports its state to a known location; the coordinator loads a manifest on resume.",
              "✅ crash_resume · ❌ F (the manifest side is on the D1.4 page)"),
    ExamPoint("5.4", "S", 4, "Inject the exported state into the resumed agent's prompt.", "✅ crash_resume · ❌ F"),
    ExamPoint("1.4", "S", 3, "Structured handoff summaries for humans who can't see the transcript (customer id, root cause, amount, "
              "recommended action).", "the D1.5 Escalation page (❌ F there)"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ Complete, structured, in the prompt", "correct", CORRECT, "cited_report",
            observe=("The synthesizer receives all 6 findings as JSON — each claim with its url, document and page — in a ~300-token "
                     "prompt, and cites all 6. long_research: all 24 cited in ~1,200 tokens. next_phase: the phase-2 agent reads 2 "
                     "files because the phase-1 summary tells it where to look. crash_resume: 1 step, continuing from the saved state."),
            why="Every downstream agent gets exactly what it needs, in a shape that keeps attribution — and nothing it doesn't."),
    Variant("A", "⭐❌ A — pass a pointer, not the findings", "distractor", VARIANT_A, "cited_report",
            observe="The prompt says “the findings the search agents gathered” — and contains none. The synthesizer answers NO_FINDINGS: 0 of 6.",
            why="A subagent sees only its prompt: nothing is inherited and there's no shared memory, so a reference to earlier results points at nothing.",
            fix="Paste the complete findings into the prompt.", source="guide:1.3:K2"),
    Variant("B", "⭐❌ B — flatten the findings into prose", "distractor", VARIANT_B, "cited_report",
            observe="All 6 claims arrive as one paragraph with no urls, documents or pages. The report uses all 6 — and every one ends in “[no source]”.",
            why="The content survived the hop; the metadata didn't. Without it the synthesizer can't attribute anything.",
            fix="Send structured records: the claim, and its source url, document and page as separate fields.", source="guide:1.3:S2"),
    Variant("C", "❌ C — hand over the whole transcripts", "distractor", VARIANT_C, "long_research",
            observe=("The prompt carries every call and raw page the search agents saw — tens of thousands of simulated tokens, far over "
                     "the 3,000-token budget. The overloaded synthesizer uses only the first third of the claims. It also fails on "
                     "cited_report."),
            why=("The docs design subagents so that only the final message returns, and warn that many detailed results explode the "
                 "context. Passing transcripts undoes that isolation."),
            fix="Pass the findings (content + metadata), not the transcript that produced them.", source="docs"),
    Variant("D", "⭐❌ D — “keep it short”: only the top findings", "distractor", VARIANT_D, "long_research",
            observe="Only 2 of 24 findings are passed, well structured and fully cited — and the report is missing 22 claims.",
            why="The guide asks for the COMPLETE findings in the subagent's prompt; trimming for brevity silently drops coverage.",
            fix="Pass all findings; if size is a problem, drop transcript noise, not findings.", source="guide:1.3:S1"),
    Variant("E", "⭐❌ E — start the next phase without a summary", "distractor", VARIANT_E, "next_phase",
            observe="The phase-2 agent gets only its task. It re-explores the whole repository: 12 file reads instead of 2.",
            why="A new agent starts blank. Summarising phase 1 and injecting it into phase 2's first prompt is how the work carries over.",
            fix="Summarise phase 1's key findings and put them in the next phase's initial prompt.", source="guide:5.4:S3"),
    Variant("F", "⭐❌ F — resume an agent without its saved state", "distractor", VARIANT_F, "crash_resume",
            observe="“Continue the exploration” — but the saved state isn't in the prompt, so the agent starts over: 12 file reads instead of 1 step.",
            why="An agent doesn't remember a previous run. The state it exported only helps if it's loaded and injected into the prompt.",
            fix="Load the exported state and inject it into the resumed agent's prompt.", source="guide:5.4:S4"),
)

TLDR = (
    "Agents don't share a brain. The **only** thing that crosses from one agent to the next is the **prompt** you write — and only "
    "the **final message** comes back. So a handoff must carry the **complete findings**, in a **structured** shape that keeps each "
    "claim's **source metadata**, plus a **summary of the previous phase** or the **saved state** of an interrupted agent — and not "
    "the raw transcripts that produced them."
)
MENTAL_MODEL = ("A relay baton with a sealed envelope: the next runner knows only what's in the envelope. Put the whole result in, "
                "label every item with where it came from — and don't stuff in your running diary.")

WHAT_IT_IS = """
D1.2 showed that subagents have isolated context. This page is about the **payload**: what you put into the prompt that crosses the gap,
and in what shape. The exam guide asks for complete findings and structured content-plus-metadata (Guide §6 · TS 1.3, pp.6–7), phase
summaries and state injection (TS 5.4, pp.21–22), and structured handoffs to humans (TS 1.4, p.7 — see D1.5).

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | No shared memory | A new contractor gets only the envelope — “as discussed” means nothing to them. | ⭐ TS 1.3 · Knowledge 2 · pp.6–7 |
| 2 | Complete findings in the prompt | Hand over the whole file, not a sticky note saying where the file is. | ⭐ TS 1.3 · Skill 1 · pp.6–7 |
| 3 | Structured content + metadata | Every fact wears its name tag (url · document · page); strip the tags and nobody can cite it. | ⭐ TS 1.3 · Skill 2 · pp.6–7 |
| 4 | Final message, not the transcript | Send the minutes, not the recording of the whole meeting. | 📘 docs (subagents: only the final message returns; context explosion) |
| 5 | Phase summary | The handover note at shift change: what's done, where things are, what's left. | ⭐ TS 5.4 · Skill 3 · pp.21–22 |
| 6 | State injection on resume | A bookmark only works if you hand it back with the book. | ⭐ TS 5.4 · Knowledge 4, Skill 4 · pp.21–22 |
| 7 | Handoff to a human | The same envelope rule for people: the human wasn't in the chat either. | ⭐ TS 1.4 · Skill 3 · p.7 (D1.5) |

**What goes in a handoff?** (this page's checklist, built from the guide and docs)

| # | Put in | Leave out | Why |
|---|---|---|---|
| 1 | The goal and the quality bar | — | The agent can't see the coordinator's instructions (D1.2) |
| 2 | ALL relevant findings | — | Complete findings (TS 1.3 S1) |
| 3 | Each finding's source url, document, page — as separate fields | Findings flattened into prose | Attribution (TS 1.3 S2) |
| 4 | A summary of what earlier phases established | The earlier phases' raw exploration | Phase summaries (TS 5.4 S3) |
| 5 | Saved state, for a resumed agent | “You remember where you were” | State injection (TS 5.4 S4) |
| 6 | — | Whole transcripts of other agents | Only final messages return; context explosion (docs) |
"""

HOW_IT_WORKS = """
1. The upstream agent finishes; **only its final message** comes back to the coordinator.
2. The coordinator decides what the next agent needs: the **complete** findings, a **phase summary**, or **saved state**.
3. It packs them in a **structured** form — content in one field, metadata (source url, document, page) in others.
4. It puts all of it **in the next agent's prompt**. There is no other channel.
5. The downstream agent can now cite, build on the earlier phase, or continue where it stopped.
"""

WHERE_SEEN = """
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): search → analysis → synthesis, with a cited report at the end.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): multi-phase codebase exploration, summaries between phases.
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): the handoff to a human agent (D1.5).
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 1.3 (pp.6–7), TS 5.4 (pp.21–22) and TS 1.4 (p.7), and the official docs (verified "
              "2026-09-27 — pages listed above). Section layout inspired by a community concept list (claudearchitectcertification.com "
              "— community source, unverified; no text copied).")

LAB_INTRO = """
You write the **coordinator's handoff code**: what goes into the prompt of the next agent. The downstream agents are **simulated** — they can
use only what their prompt contains. Four situations: a cited report from 6 findings, a long research run with 24 findings (and bulky
transcripts available), phase 2 of a codebase exploration, and resuming a crashed agent. Five mistakes come from the exam guide (⭐), one
from the docs.
"""

DISTRACTORS = (
    ("A · Pass a pointer", "The findings were just produced — the next agent can use them.",
     "Nothing is inherited or shared; the prompt contains no findings.", "Put the complete findings in the prompt.", "guide:1.3:K2"),
    ("B · Flatten into prose", "The claims are all there, in readable form.",
     "The source urls, documents and pages are gone — nothing can be cited.", "Structured records: content + metadata fields.", "guide:1.3:S2"),
    ("C · Pass whole transcripts", "More context can't hurt.",
     "It swamps the agent's context; quality drops.", "Pass findings, not transcripts.", "docs"),
    ("D · Only the top findings", "Shorter prompts are better.",
     "Coverage is silently lost.", "Pass all findings; cut noise, not content.", "guide:1.3:S1"),
    ("E · Next phase without a summary", "The new agent can look for itself.",
     "It re-explores everything the last phase found.", "Summarise phase 1 into phase 2's prompt.", "guide:5.4:S3"),
    ("F · Resume without the saved state", "It's the same agent, it'll pick up.",
     "A fresh run has no memory: it starts over.", "Inject the exported state into the prompt.", "guide:5.4:S4"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Handoff content", "Complete findings, structured", "Prose summary", "Pointer only", "Full transcripts")
SIDE_BY_SIDE_ROWS = (
    ("1", "Claims reach the next agent", "All", "All", "None", "All (buried)"),
    ("2", "Sources survive", "Yes — separate fields", "No", "—", "Somewhere in the noise"),
    ("3", "Context cost", "Small", "Small", "Tiny", "Huge"),
    ("4", "Typical failure", "—", "Uncited report", "“No findings provided”", "Degraded, partial output"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=11, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=10, color="#6B7280"];
  Q1 [shape=diamond, label="Is the next agent continuing\\nan interrupted run?"];
  ST [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Inject its exported state\\n(TS 5.4 S4)"];
  Q2 [shape=diamond, label="Is it starting a new phase?"];
  SU [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Inject a summary of the last phase\\n(TS 5.4 S3)"];
  Q3 [shape=diamond, label="Does it work on\\nearlier findings?"];
  FI [shape=box, fillcolor="#FEF3C7", color="#D97706", label="ALL findings, structured with source metadata\\n(TS 1.3 S1–S2)"];
  P [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Everything goes IN the prompt — never\\n“as discussed”, never whole transcripts"];
  Q1 -> ST [label="yes"]; Q1 -> Q2 [label="no"]; Q2 -> SU [label="yes"]; Q2 -> Q3 [label="no"]; Q3 -> FI [label="yes"];
  ST -> P; SU -> P; FI -> P;
}'''

EXPERIMENTS = (
    "Run ✅ on each scenario and read the prompt size and the cited count in the output.",
    "Run ⭐❌ B, then change it to pass `as_payload(FINDINGS)` — the same claims, now cited.",
    "Run ❌ C on long_research: how many of the 24 claims survived the overloaded context?",
    "In ✅, delete `+ PHASE1_SUMMARY` and run next_phase: count the file reads.",
)

QUESTIONS = (
    Question(
        q=("Reviewers flag that 70% of the research system's final reports contain only generic statements, with no reference "
           "to anything the search subagents retrieved. The coordinator's logs show both search subagents returned 8–12 "
           "findings each, and the synthesis subagent completed without errors. The coordinator spawns synthesis with the "
           "prompt: “Write the final report using the research gathered in the previous steps, following our citation "
           "standards.” What is the most likely root cause?"),
        opts=("The synthesis subagent's system prompt does not tell it to prefer retrieved evidence over its general knowledge.",
              "The combined search findings exceeded the synthesis subagent's context window and were silently truncated on the way into it.",
              "The synthesis prompt refers to the earlier research but does not contain it, and subagents inherit no parent context.",
              "The search subagents returned their findings in a format the synthesis subagent could not parse reliably."),
        ans=2,
        explain=("The prompt quoted in the logs is one sentence long: it points at the research instead of carrying it. A subagent "
                 "does not inherit the coordinator's history and shares no memory with other agents, so its prompt is its only "
                 "input. A blames the downstream agent's instructions, but it cannot prefer evidence it never received. B needs "
                 "the findings to be in the prompt before anything can be truncated. D would hurt attribution, but these reports "
                 "contain none of the research at all, which points to absence, not format."),
        scenarios=(3,), points=("1.3:K2", "1.3:S1"),
    ),
    Question(
        q=("The synthesis subagent now receives all 40 findings, and the reports read well. However, an audit finds that 35% of "
           "citations point to the wrong source, usually another source retrieved in the same search batch. The coordinator "
           "builds the synthesis prompt by joining each search subagent's findings into paragraphs, with a “Sources:” list of "
           "URLs at the end of each paragraph. What change most effectively fixes the misattribution?"),
        opts=("Instruct the synthesis subagent to check each citation against the paragraph's Sources list before using it.",
              "Pass each finding as a structured record, with the claim in one field and its URL, document and page in others.",
              "Give the synthesis subagent a fetch tool so it can reopen each source and confirm every claim before it cites it.",
              "Limit each paragraph to five findings so that the synthesis subagent has fewer sources to choose between per claim."),
        ans=1,
        explain=("Pooling several claims over one shared source list destroys the claim-to-source mapping before synthesis starts. "
                 "Structured records that keep content and metadata in separate fields carry that mapping across the handoff. "
                 "A asks the model to recover a mapping its input no longer contains. C repeats upstream work for every citation "
                 "and gives synthesis tools it should not need. D shrinks the ambiguity, but any paragraph with more than one "
                 "source is still ambiguous."),
        scenarios=(3,), points=("1.3:S2", "5.6:K1"),
    ),
    Question(
        q=("To cut cost, a teammate proposes that the coordinator pass only the 5 highest-relevance findings (out of about 25) "
           "to the synthesis subagent. The synthesis prompt would shrink from 4,000 to 900 tokens, but the subagent's input "
           "budget already fits 4,000 tokens comfortably. Over the last two weeks, the most common reader complaint has been "
           "that reports miss perspectives covered in the research. How should you evaluate the proposal?"),
        opts=("Adopt it, because shorter prompts reduce attention dilution and will lift report quality overall.",
              "Adopt it, and have the synthesis subagent note in each report that further findings were available.",
              "Reject it, and append each search subagent's full transcript instead, so that no perspective can be lost at all.",
              "Reject it, and keep passing the complete findings: they fit the budget, and trimming worsens the complaint."),
        ans=3,
        explain=("The synthesis subagent can only use what its prompt contains, so it needs the complete findings from the earlier "
                 "agents. They fit the budget here, and the readers' complaint is about coverage, which trimming makes worse. "
                 "A cites a real effect of very long inputs, but it does not apply at 4,000 tokens. B admits the gap without "
                 "closing it. C overcorrects: transcripts add tool calls and intermediate reasoning, which bury the findings."),
        scenarios=(3,), points=("1.3:S1",),
    ),
    Question(
        q=("A coordinator agent migrates a legacy billing module in two phases. Phase 1 subagents mapped where refund logic "
           "lives and, after 40 minutes, identified the 6 relevant files and their call paths. Phase 2 subagents are spawned "
           "with only their modification tasks. Logs show each phase 2 subagent spends most of its turns re-running Grep and "
           "Read across the whole repository before editing anything. What is the most effective change?"),
        opts=("Summarise phase 1's key findings (files, entry points, dependencies) and inject them into each phase 2 prompt.",
              "Raise the phase 2 subagents' max_turns so they have room to finish both the exploration and the edits.",
              "Resume the phase 1 subagent sessions for phase 2 so that the edits run in the context that already holds the exploration.",
              "Tell phase 2 subagents in their system prompt to avoid re-exploring code that phase 1 has already analysed."),
        ans=0,
        explain=("A new subagent starts blank. Summarising one phase's key findings and injecting that summary into the next phase's "
                 "initial context is how the exploration carries over. B pays for the waste instead of removing it. C drags each "
                 "phase 1 session's verbose search output into the edit work, and each session holds only its own slice of the "
                 "map. D asks the agent to avoid work it cannot identify, because it does not know what phase 1 found."),
        scenarios=(4,), points=("5.4:S3",),
    ),
    Question(
        q=("A nightly job runs four exploration subagents over a large monorepo, and each takes about 90 minutes. When the host "
           "restarts mid-run, the coordinator re-spawns every subagent from the beginning, and 3 of the last 10 runs missed "
           "their morning deadline as a result. Which recovery design best addresses this?"),
        opts=("Re-spawn each interrupted subagent with a prompt telling it to continue from where it stopped and skip done work.",
              "Add retries with exponential backoff around every subagent invocation and lengthen the host's restart grace period too.",
              "Have each agent export its state to a known location, then load a manifest on resume and inject each agent's state.",
              "Replace the four subagents with a single long-running agent so only one session needs recovering after a restart."),
        ans=2,
        explain=("A re-spawned agent has no memory of the earlier run. Recovery works only if each agent exports structured state "
                 "(files covered, findings, next steps) to a known location, and the coordinator loads the manifest and injects "
                 "that state into the new prompts. A points at state the new agent does not have. B makes restarts rarer, but "
                 "every retry still starts from zero. D concentrates 6 hours of exploration into one degrading context and still "
                 "recovers nothing."),
        scenarios=(4,), points=("5.4:K4", "5.4:S4"),
    ),
    Question(
        q=("Your support agent escalates policy-exception refunds by calling escalate_to_human with the note “Customer needs "
           "help with a refund; see conversation.” Human agents work in a separate ticketing tool with no access to the chat "
           "transcript. Their average handling time on escalated tickets is 11 minutes, most of it spent asking customers to "
           "repeat details the agent had already collected. What change most effectively reduces handling time?"),
        opts=("Before escalating, ask the customer to summarise the issue in one message and forward it with the ticket.",
              "Route each escalation to the human agent the customer spoke to most recently, who is likely to recall the case.",
              "Give human agents read access to the full chat transcript so they can review the whole case before contacting the customer.",
              "Have the agent compile a structured handoff: customer ID, order, amount, root cause, steps tried, recommended action."),
        ans=3,
        explain=("The human receiving the ticket was not in the conversation. A structured handoff hands over what the agent already "
                 "verified and decided, so the human can act immediately. A puts the burden back on the customer and loses the "
                 "verified tool data (customer ID, amount). B solves a different problem, and most escalations have no earlier "
                 "human contact. C changes tooling and still leaves the human reading a long transcript to extract the same "
                 "five facts."),
        scenarios=(1,), points=("1.4:S3", "1.4:K3"),
    ),
    Question(
        q=("The synthesis subagent has a 6,000-token input budget. Four document-analysis subagents each return 3,000–4,000 "
           "tokens: their full reasoning, long quoted passages and caveats. Coordinator logs show the synthesis input is "
           "truncated on every run, and findings from the third and fourth analyses are missing from 80% of reports. What is "
           "the most effective fix?"),
        opts=("Increase the synthesis subagent's max_tokens so that it can take in all four full analyses within one single synthesis call.",
              "Have the analysis subagents return structured findings, each with its source and a short excerpt, not full reasoning.",
              "Run synthesis once per analysis and then add a final pass that concatenates the four partial reports into one.",
              "Shuffle the order of the analyses on each run so that no single subagent's findings are always the ones cut."),
        ans=1,
        explain=("When a downstream agent has a limited budget, the fix belongs upstream: return compact structured data (findings, "
                 "sources, excerpts) instead of reasoning chains. A misreads max_tokens, which caps the output, not the input. "
                 "C multiplies calls and loses cross-document synthesis. D spreads the loss around without reducing it."),
        scenarios=(3,), points=("5.1:S6", "1.3:S2"),
    ),
    Question(
        q=("A report on remote-work productivity says “studies disagree sharply”, presenting a 38% gain and a 12% gain as a "
           "contradiction. The analysis subagents extracted both figures correctly, but each structured finding records only "
           "the claim and its URL. The 38% figure comes from a 2019 survey and the 12% figure from a 2024 study. What upstream "
           "change best prevents this class of error?"),
        opts=("Require analysis subagents to include publication or data-collection dates and method in every structured finding.",
              "Instruct the synthesis subagent to label every apparent contradiction as unresolved instead of interpreting it.",
              "Have the synthesis subagent keep only the most recent source whenever two statistics on one topic disagree.",
              "Add a verification subagent that re-fetches both sources of any conflict to determine which of the two figures is correct."),
        ans=0,
        explain=("Both figures are right. What is missing is the date that would show the difference is a change over time, not a "
                 "disagreement, and synthesis cannot reason about metadata it was never passed. B still misreports the difference "
                 "as a conflict. C arbitrarily discards a credible source instead of attributing both. D spends a round trip "
                 "per conflict to re-check figures that were already correct."),
        scenarios=(3,), points=("5.6:S4", "5.1:S5"),
    ),
    Question(
        q=("An engineer notices the synthesis subagent ignores about half the findings and proposes “giving it the full "
           "picture”: appending each search subagent's complete transcript (tool calls, raw pages, intermediate reasoning) to "
           "the synthesis prompt. The prompt would grow from 3,000 to 45,000 tokens. What outcome should you expect?"),
        opts=("Better coverage, because every finding and the reasoning behind it are now available to the synthesis agent.",
              "A request error, because one agent's transcript cannot be passed into another agent's prompt by design.",
              "No change, because a subagent gives low weight to content that another agent produced before it ran.",
              "Worse output, because the findings are buried among raw tool output and the prompt may exceed its budget."),
        ans=3,
        explain=("By design, only a subagent's final message returns to its parent; its intermediate work stays in its own context. "
                 "Pasting whole transcripts into the next agent's prompt undoes that isolation and floods the context. Pass "
                 "curated, structured findings instead. A assumes more context is always better. B is false: a transcript is "
                 "just text in a prompt. C invents a weighting rule that no documentation describes."),
        scenarios=(3,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("How is this different from D1.2?",
     "D1.2 covered the architecture (coordinator, spawning, isolation). This page is about the payload: what goes into the prompt that "
     "crosses from one agent to the next, and in what shape."),
    ("Isn't JSON overkill?",
     "Any structured format works; the point (TS 1.3 S2) is that content and metadata are separate fields so attribution survives. The docs "
     "also recommend structured formats for structured state."),
    ("How big can a handoff be?",
     "As big as the complete findings need — cut noise (transcripts, raw pages), not findings. The 3,000-token budget in this lab is invented."),
    ("Where does the human handoff fit?",
     "Same rule, different recipient: the human can't see the transcript, so the handoff carries customer id, root cause, amount and next "
     "action — see D1.5."),
)

_Q = "Write a cited report on AI in the creative industries from these findings."
PLAYGROUND_INTRO = """
Type the instruction for the **downstream agent**, choose what your handoff carries, and see the **exact prompt** it received and what it could
do with it. Every tab changes one thing about the envelope.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="handoff")


PLAYGROUND = (
    _tab("complete", "⭐ Complete findings", "payload",
         "Hand over the whole file, not a sticky note saying where the file is.", "guide:1.3:S1",
         "The synthesizer sees only its prompt. Pass all the findings, just the first two, or only a pointer to them.",
         "agent-sdk/subagents § What subagents inherit; guide TS 1.3 Knowledge 2, Skill 1",
         ("payload", "n_findings"), {"payload": "all", "n_findings": 6}, (_Q,),
         ("All: every claim cited.", "First two: 2 claims — the rest is gone.", "Pointer: NO_FINDINGS.",
          "Set 24 findings: the full set still fits the budget as structured data.")),
    _tab("meta", "⭐ Structure & metadata", "format",
         "Every fact wears its name tag; strip the tags and nobody can cite it.", "guide:1.3:S2",
         "The same findings, sent as structured records (claim + url, document, page) or flattened into prose.",
         "guide TS 1.3 Skill 2; prompting best practices § State management (structured formats)",
         ("fmt",), {"fmt": "structured"}, (_Q,),
         ("Structured: [Document, p.N] after every claim.", "Prose: every claim ends in [no source].")),
    _tab("transcript", "Final message vs transcript", "transcript",
         "Send the minutes, not the recording of the whole meeting.", "",
         "Pass the findings, or the search agents' whole transcripts. Only the final message is meant to cross back (docs).",
         "agent-sdk/subagents § Benefits; sub-agents § Best practices",
         ("crossing", "n_findings"), {"crossing": "final", "n_findings": 24}, (_Q,),
         ("Final: ~1,200 tokens, 24/24 cited.", "Raw transcripts: tens of thousands of tokens — over budget, most claims lost.")),
    _tab("phase", "⭐ Phase summary", "phase",
         "The handover note at shift change: what's done, where things are, what's left.", "guide:5.4:S3",
         "Phase 2 traces ledger.post_refund's dependencies. With the phase-1 summary in its prompt it goes straight to the right files.",
         "guide TS 5.4 Skill 3",
         ("summary",), {"summary": "yes"}, ("Phase 2: trace the dependencies of ledger.post_refund.",),
         ("Summary yes: 2 file reads.", "Summary no: 12 — the whole repository again.")),
    _tab("resume", "⭐ Resume with state", "crash",
         "A bookmark only works if you hand it back with the book.", "guide:5.4:S4",
         "The crashed agent exported its state. Inject it into the resumed agent's prompt, or just say “continue”.",
         "guide TS 5.4 Knowledge 4, Skill 4; agent-sdk/sessions § Resume across hosts",
         ("state",), {"state": "yes"}, ("Continue the refund-flow exploration.",),
         ("State yes: 1 step, continuing.", "State no: 12 reads — a restart.")),
)

DECISION_DOT = readable(DECISION_DOT)   # FLOWCHART RULE: 18pt, max 2 nodes per row

CONTENT = ConceptContent(
    slug="subagent-state-handoff", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("subagents", "session-state", "escalation"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("cited_report", "long_research", "next_phase", "crash_resume"), show_ledger=False,
)
