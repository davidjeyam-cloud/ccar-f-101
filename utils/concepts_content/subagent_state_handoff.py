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
        q=("The synthesis subagent writes a fluent report, but none of its claims can be traced to a source, even though "
           "the search subagents recorded a URL and page for every finding. What's the most effective change?"),
        opts=("Tell the synthesis subagent to add citations wherever it can.",
              "Give the synthesis subagent web search so it can find sources again.",
              "Have the report subagent add a bibliography at the end.",
              "Pass findings in a structured format that keeps each claim separate from its source metadata (URL, document, page)."),
        ans=3,
        explain=("Attribution survives handoffs only when context is passed in a structured format that separates content "
                 "from metadata. Re-searching wastes work, and asking for citations without passing the metadata invites "
                 "invented ones."),
        scenarios=(3,), points=("1.3:S2",),
    ),
    Question(
        q=("The coordinator spawns the synthesis subagent with the prompt “Using the research results from the previous "
           "agents, write the report.” The report is generic and cites nothing from the research. Why?"),
        opts=("The subagent doesn't inherit anything; the research findings must be written into its prompt.",
              "The subagent needed a larger context window to hold the previous agents' results.",
              "The previous agents' results expired before synthesis started.",
              "Synthesis subagents only read results passed through a shared memory store."),
        ans=0,
        explain=("Subagents don't inherit the coordinator's history and have no shared memory. Their only input is "
                 "their prompt, so the complete findings must be put there explicitly."),
        scenarios=(3,), points=("1.3:K2", "1.3:S1"),
    ),
    Question(
        q=("While onboarding a developer to a legacy monolith, the main agent's context fills with raw search output "
           "after a handful of “where is X handled?” questions, and its overview answers get worse. What's the best "
           "pattern?"),
        opts=("Answer every question in the main agent but ask it to be brief.",
              "Restart the main session after every question.",
              "Spawn a subagent for each specific question, return only its summary, and keep the main agent coordinating.",
              "Load the whole codebase into the main agent's context up front."),
        ans=2,
        explain=("Subagents isolate verbose exploration output, so the main agent keeps the high-level picture and "
                 "receives only summaries. Restarting loses the overview, and loading everything front-loads the problem."),
        scenarios=(4,), points=("5.4:K3", "5.4:S1"),
    ),
    Question(
        q=("A research report presents a 2016 survey as current evidence and mixes up findings from a lab study and a "
           "field study. The search subagents had all of this information when they read the sources. What upstream "
           "change best fixes it?"),
        opts=("Tell the synthesis subagent to check the dates of claims.",
              "Require search subagents to return metadata with each finding: publication date, source location and method.",
              "Only allow sources published in the last two years.",
              "Have the report subagent add a disclaimer about source quality."),
        ans=1,
        explain=("Requiring subagents to include metadata (dates, source locations, methodological context) in structured "
                 "outputs lets downstream synthesis weigh and describe findings accurately. The synthesis agent can't "
                 "check what it was never given."),
        scenarios=(3,), points=("5.1:S5",),
    ),
    Question(
        q=("The report subagent runs with a tight context budget. Document-analysis subagents send it several pages "
           "each: full reasoning, quoted passages and caveats. Reports now drop findings from later analyses. What's "
           "the best fix?"),
        opts=("Increase the report subagent's max_tokens.",
              "Send the analyses one at a time and build the report incrementally.",
              "Ask the report subagent to skim the analyses.",
              "Change the analysis subagents to return structured data: key facts, citations and relevance scores."),
        ans=3,
        explain=("When downstream agents have limited context budgets, upstream agents should return structured data "
                 "rather than verbose content and reasoning chains. max_tokens limits output, not the input overload."),
        scenarios=(3,), points=("5.1:S6",),
    ),
    Question(
        q=("To “give the synthesis subagent full context”, the coordinator appends every search subagent's complete "
           "transcript, including tool calls and intermediate reasoning, to the synthesis prompt. What's the likely "
           "result?"),
        opts=("Better reports, because nothing is lost.",
              "Relevant findings get buried in noise, and the prompt may not fit the context window.",
              "An error, because transcripts can't be passed between agents.",
              "No change, because subagents ignore content they didn't produce."),
        ans=1,
        explain=("A subagent's intermediate work isn't meant for its consumer. Only the final result returns to the "
                 "parent, and whole transcripts flood the next agent's context. Pass curated, structured findings instead."),
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
