"""
D5.3 Error Propagation — what a subagent's failure looks like when it reaches the coordinator. Guide TS 5.3 (Knowledge 1–4,
Skills 1–4, p.21): structured error context instead of a generic status, access failures kept apart from valid empty results,
local recovery for transient failures with only the unresolved ones propagated, no silent suppression and no workflow-wide
termination, and coverage annotations in the synthesis. D1.5 (escalation) and D2.3 (MCP structured errors) are the neighbours.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-11-14); official docs fetched 2026-11-14 (DOC_REFS). Every claim
is in GROUNDING with its source type. The guide distinction between an access failure and a valid empty result is NOT stated in
the docs; the page says so. Paraphrased; no real exam question.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-11-14"
_P = "https://platform.claude.com/docs/en"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Handle tool calls — Handling errors with is_error", f"{_P}/agents-and-tools/tool-use/handle-tool-calls"),
    DocRef("Agent SDK subagents — context isolation; what subagents inherit; resume (partial output)", f"{_C}/agent-sdk/subagents"),
    DocRef("Agent SDK agent loop — handle the result (result subtypes)", f"{_C}/agent-sdk/agent-loop"),
    DocRef("MCP specification — Tools, Error Handling (protocol errors vs tool execution errors)",
           "https://modelcontextprotocol.io/specification/2025-11-25/server/tools"),
)

GROUNDING = (
    Claim("A subagent's useful failure information must be structured: failure type, what was attempted, partial results and "
          "alternative approaches let the coordinator make a recovery decision.", "guide", "TS 5.3 · Knowledge 1, Skill 1 · p.21"),
    Claim("An access failure (a timeout that needs a retry decision) is a different thing from a valid empty result (a query that "
          "worked and matched nothing); error reporting must tell them apart.", "guide", "TS 5.3 · Knowledge 2, Skill 2 · p.21"),
    Claim("The docs do not define “valid empty result” as a term. The tool_result docs show an empty-content example without saying "
          "whether it means “nothing found” or a failure, so this distinction comes from the guide alone.", "docs",
          "handle-tool-calls § Example of empty tool result"),
    Claim("A generic status such as “search unavailable” hides context from the coordinator; silently returning an empty result as "
          "success and terminating the whole workflow on one failure are both anti-patterns.", "guide", "TS 5.3 · Knowledge 3–4 · p.21"),
    Claim("Subagents recover locally from transient failures and propagate only what they cannot resolve, including what was "
          "attempted and the partial results.", "guide", "TS 5.3 · Skill 3 · p.21"),
    Claim("Synthesis output carries coverage annotations: which findings are well supported and which topics have gaps because a "
          "source was unavailable.", "guide", "TS 5.3 · Skill 4 · p.21"),
    Claim("A client tool that fails returns its error in the tool_result content with is_error set to true, and Claude then "
          "incorporates the error into its response.", "docs", "handle-tool-calls § Handling errors with is_error"),
    Claim("The docs advise instructive error messages: say what went wrong and what Claude should try next, not just a generic "
          "“failed”, so Claude can recover or adapt without guessing.", "docs", "handle-tool-calls § Handling errors with is_error (tip)"),
    Claim("Intermediate tool calls and results stay inside a subagent; only its final message returns to the parent. So whatever "
          "the coordinator needs about a failure has to be in that final message.", "docs", "agent-sdk/subagents § Benefits of using subagents"),
    Claim("An API error that ends a subagent early, such as a rate limit, is never delivered as its result.", "docs",
          "agent-sdk/subagents § What subagents inherit"),
    Claim("When a subagent stops at its maxTurns limit, Claude Code marks the output in the Agent tool result as partial, so Claude "
          "knows the run is unfinished.", "docs", "agent-sdk/subagents § Resume subagents"),
    Claim("The Agent SDK ends a run with a typed result subtype (success, error_max_turns, error_max_budget_usd, "
          "error_during_execution); the result text is present only on success, so check the subtype before reading it.",
          "docs", "agent-sdk/agent-loop § Handle the result"),
    Claim("MCP separates protocol errors (malformed requests) from tool execution errors reported in the result with isError: "
          "true, which carry actionable feedback a model can use to self-correct; clients should give execution errors to the model.",
          "docs", "MCP specification, tools § Error Handling"),
    Claim("The topics, findings, failures, the deterministic coordinator policy and the report are invented to make each effect "
          "repeatable; the coordinator is code, not a model.", "simulated", "utils/errprop_lab.py"),
    Claim("Retrying once locally and offering a news-archive alternative are this page's choices for a small, readable example; the "
          "guide names local recovery and alternatives but no retry count.", "recommendation", "TS 5.3 · Skill 3"),
)

CORRECT = r'''from utils.errprop_lab import SearchError, run_research, web_search   # SIMULATED research system


def search_subagent(topic):
    attempted = []
    for attempt in range(2):                          # local recovery: one retry for a transient failure
        attempted.append(f"web search: {topic} (attempt {attempt + 1})")
        try:
            hits = web_search(topic)
        except SearchError as err:
            failure, partial = err.failure_type, err.partial
            continue
        if not hits:                                  # a VALID empty result: the search worked, nothing matched
            return {"status": "empty", "topic": topic, "query": topic}
        return {"status": "ok", "topic": topic, "findings": hits}
    return {"status": "error", "topic": topic,        # only what could not be resolved locally is propagated
            "failure_type": failure, "attempted": attempted, "partial": partial,
            "alternatives": ["news_archive"]}


def synthesize(findings, coverage):
    claims = [f"{f['claim']} ({f['source']}, {f['date']})" for hits in findings.values() for f in hits]
    return {"claims": claims, "coverage": coverage}   # which topics are well supported, which have gaps


run_research(search_subagent, synthesize)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


_TAIL = '''    return {"status": "error", "topic": topic,        # only what could not be resolved locally is propagated
            "failure_type": failure, "attempted": attempted, "partial": partial,
            "alternatives": ["news_archive"]}'''
# ⭐ TS 5.3 · Knowledge 3 — a generic status
VARIANT_A = _swap(CORRECT, _TAIL, '''    return {"status": "error", "message": "search unavailable"}   # WRONG: a generic status hides what the coordinator needs''')
# ⭐ TS 5.3 · Knowledge 4 — the failure suppressed as an empty success
VARIANT_B = _swap(CORRECT, _TAIL, '''    return {"status": "empty", "topic": topic, "query": topic}   # WRONG: a failure reported as "no results", looks like success''')
# ⭐ TS 5.3 · Knowledge 4 — let the exception end the whole workflow
VARIANT_C = _swap(CORRECT, '''            failure, partial = err.failure_type, err.partial
            continue''', '''            raise                                     # WRONG: one failed search ends the whole workflow''')
# ⭐ TS 5.3 · Knowledge 2 / Skill 2 — a valid empty result reported as a failure
VARIANT_D = _swap(CORRECT, '''            return {"status": "empty", "topic": topic, "query": topic}''',
                  '''            return {"status": "error", "topic": topic, "failure_type": "no_results", "attempted": attempted,
                    "partial": [], "alternatives": ["news_archive"]}   # WRONG: nothing matched is not a failure''')
# ⭐ TS 5.3 · Skill 3 — no local recovery
VARIANT_E = _swap(CORRECT, "for attempt in range(2):                          # local recovery: one retry for a transient failure",
                  "for attempt in range(1):                          # WRONG: no local retry - even a one-off blip is propagated")
# ⭐ TS 5.3 · Skill 4 — a report with no coverage annotations
VARIANT_F = _swap(CORRECT, '''    return {"claims": claims, "coverage": coverage}   # which topics are well supported, which have gaps''',
                  '''    return {"claims": claims}                         # WRONG: the report reads as complete''')

# ── Check and chart ────────────────────────────────────────────────────────────

from utils import errprop_lab as _lab


def _event(trace):
    ev = [e for e in trace["events"] if e["kind"] == "errprop_run"]
    return trace["status"]["raised"], trace["status"].get("scenario"), (ev[-1] if ev else None)


def _diagnose(trace):
    raised, _sc, rec = _event(trace)
    if raised:
        return False, None, f"raised: {raised[:160]}"
    return _lab.diagnose(rec)


EXPECTED_TEXT = {
    "timeout_alt": "all three topics supported: music recovered through the news-archive alternative (1 coordinator round trip)",
    "empty_valid": "film reported as “none found” (a valid empty result), no error, no round trip",
    "transient": "all three supported, and no error ever reached the coordinator",
    "partial_gap": "music marked partial (the two findings kept, the gap shown), 1 round trip, nothing else lost",
}


def check_outcome(scenario, trace):
    ok, _bug, txt = _diagnose(trace)
    return ok, EXPECTED_TEXT[scenario], txt


_CONCEPT = {
    "local": ("#FEF3C7", "#D97706", "what the subagent does first"),
    "ctx": ("#DBEAFE", "#0066CC", "what it propagates"),
    "coord": ("#CCFBF1", "#0D9488", "what the coordinator does"),
    "out": ("#EDE9FE", "#7C3AED", "result"),
    "bug": ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "FAIL": ("A subagent's search\\nfails or finds nothing", "box", "local"),
    "LOCAL": ("⭐ Recover locally\\n(transient failures)", "box", "local"),
    "KIND": ("⭐ Access failure\\nvs valid empty result", "box", "local"),
    "CTX": ("⭐ Structured context: type,\\nattempted, partial, alternatives", "box", "ctx"),
    "COORD": ("Coordinator decides: retry,\\nalternative, or partial", "box", "coord"),
    "COV": ("⭐ Synthesis with coverage\\nannotations", "box", "coord"),
    "OUT": ("A report that shows\\nits own gaps", "box", "out"),
    "GENERIC": ("✗ generic status\\n“search unavailable”", "box", "bug"),
    "SUPPRESS": ("✗ failure returned as\\nan empty success", "box", "bug"),
    "TERMINATE": ("✗ one failure ends\\nthe whole workflow", "box", "bug"),
    "EMPTYERR": ("✗ nothing found\\nreported as a failure", "box", "bug"),
    "NOLOCAL": ("✗ transient blip\\npropagated", "box", "bug"),
    "NOCOVER": ("✗ report with no\\ncoverage annotations", "box", "bug"),
}
_BUGS = ["GENERIC", "SUPPRESS", "TERMINATE", "EMPTYERR", "NOLOCAL", "NOCOVER"]
_EXP = {"timeout_alt": ["CTX", "COORD"], "empty_valid": ["KIND"], "transient": ["LOCAL"], "partial_gap": ["CTX", "COV"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 5.3 p.21)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = what this scenario '
                 'relies on · <B>red</B> = the bug your run shows</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3"><TR><TD COLSPAN="2" '
            'BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states):
    hl = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.3; ranksep=0.45; newrank=true;',
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
    lines += ["  FAIL -> LOCAL -> KIND -> CTX -> COORD -> COV -> OUT;"]
    for a, b in (("GENERIC", "SUPPRESS"), ("TERMINATE", "EMPTYERR"), ("NOLOCAL", "NOCOVER")):
        lines.append(f"  {{ rank=same; {a}; {b}; }}")
    lines += ["  OUT -> GENERIC [style=invis];", "  GENERIC -> TERMINATE [style=invis];", "  TERMINATE -> NOLOCAL [style=invis];",
              "  SUPPRESS -> EMPTYERR [style=invis];", "  EMPTYERR -> NOCOVER [style=invis];", _key(hl),
              "  NOLOCAL -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    raised, sc, _rec = _event(trace)
    ok, bug, _ = _diagnose(trace)
    s = {"OUT": ("ok", "") if ok else ("bad", "not achieved")}
    for n in _EXP.get(sc, []):
        s[n] = ("ok", "" if ok else "what this scenario needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("5.3", "K", 1, "Structured error context (failure type, attempted query, partial results, alternative approaches) "
              "is what lets the coordinator make an intelligent recovery decision.", "✅ the error dict · ❌ A"),
    ExamPoint("5.3", "K", 2, "An access failure (a timeout that needs a retry decision) is not the same as a valid empty result (a "
              "query that worked and matched nothing).", "✅ empty_valid · ❌ D"),
    ExamPoint("5.3", "K", 3, "A generic status such as “search unavailable” hides the context the coordinator needs.",
              "✅ timeout_alt · ❌ A"),
    ExamPoint("5.3", "K", 4, "Silently suppressing an error (an empty result marked as success) and terminating the whole workflow "
              "on one failure are both anti-patterns.", "✅ partial_gap · ❌ B, C"),
    ExamPoint("5.3", "S", 1, "Return failure type, what was attempted, partial results and potential alternatives so the "
              "coordinator can recover.", "✅ the error dict · ❌ A"),
    ExamPoint("5.3", "S", 2, "Tell access failures and valid empty results apart in error reporting.", "✅ empty_valid · ❌ D"),
    ExamPoint("5.3", "S", 3, "Recover locally from transient failures and propagate only what cannot be resolved, with what was "
              "attempted and the partial results.", "✅ transient · ❌ E"),
    ExamPoint("5.3", "S", 4, "Structure the synthesis with coverage annotations: which findings are well supported, which topics "
              "have gaps because sources were unavailable.", "✅ synthesize · ❌ F"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ structured context · empty ≠ failure · local retry · coverage annotations", "correct", CORRECT,
            "timeout_alt",
            observe=("timeout_alt: music recovered through the news archive; every topic supported. empty_valid: film “none_found”, "
                     "no error. transient: nothing reaches the coordinator. partial_gap: music “partial” with its two findings, the "
                     "gap shown. Every scenario ends with a report that says what it covers."),
            why=("The subagent absorbs what it can, tells a failure from an empty result, and sends the coordinator enough to choose "
                 "a recovery. The synthesis then says where the evidence is thin.")),
    Variant("A", "⭐❌ A — a generic “search unavailable” status", "distractor", VARIANT_A, "timeout_alt",
            observe=("music is a “gap” with the reason “search unavailable”, although the news archive would have worked. The "
                     "coordinator made 0 round trips: it had nothing to base a decision on."),
            why="A generic status hides what was attempted and what else could be tried, so the coordinator cannot recover.",
            fix="Return failure type, attempted query, partial results and alternatives.", source="guide:5.3:K3"),
    Variant("B", "⭐❌ B — the failure returned as an empty success", "distractor", VARIANT_B, "partial_gap",
            observe=("music is reported “none_found”: the two findings that were retrieved are gone, and the report says nobody found "
                     "anything on music. It looks like a success."),
            why=("An error dressed as an empty result prevents any recovery and makes the report claim something false."),
            fix="Propagate the failure with its context and partial results.", source="guide:5.3:K4"),
    Variant("C", "⭐❌ C — let the exception end the whole workflow", "distractor", VARIANT_C, "partial_gap",
            observe=("“WORKFLOW TERMINATED”: no report. visual arts had been searched fine and its findings are lost; film was "
                     "never even reached, because the run stopped at music."),
            why="One failed source should not discard the rest; the coordinator can proceed with partial results.",
            fix="Catch locally; propagate structured context; let the coordinator decide.", source="guide:5.3:K4"),
    Variant("D", "⭐❌ D — nothing found reported as a failure", "distractor", VARIANT_D, "empty_valid",
            observe=("film becomes a “gap” and the coordinator spends a round trip on an alternative. In truth the search worked "
                     "and the topic simply has no matches."),
            why="A valid empty result is an answer. Treating it as an error sends the coordinator after a problem that doesn't exist.",
            fix="Return a distinct empty status for a query that succeeded with no matches.", source="guide:5.3:K2"),
    Variant("E", "⭐❌ E — no local recovery: every blip is propagated", "distractor", VARIANT_E, "transient",
            observe=("The one-off failure reaches the coordinator (1 error, 1 round trip) although a single retry would have "
                     "worked. The correct run shows 0 and 0."),
            why="Transient failures are the subagent's to handle; propagating them costs the coordinator extra work for nothing.",
            fix="Retry locally; propagate only what the subagent cannot resolve.", source="guide:5.3:S3"),
    Variant("F", "⭐❌ F — a report with no coverage annotations", "distractor", VARIANT_F, "partial_gap",
            observe="The report lists claims and nothing else: a reader cannot tell that music rests on two partial findings.",
            why="Without coverage annotations a report with gaps reads as complete.",
            fix="Annotate which topics are well supported and which have gaps and why.", source="guide:5.3:S4"),
)

TLDR = (
    "A multi-agent system fails in pieces: one subagent's source times out while the others finish. What the **coordinator** "
    "learns about that failure decides whether the run recovers, or quietly produces a wrong report (guide TS 5.3).\n\n"
    "- **Send structured context**: failure type, what was attempted, partial results, alternatives. Not “search unavailable”.\n"
    "- **An empty result is not a failure.** A query that worked and found nothing is an answer; a timeout is not.\n"
    "- **Recover locally first.** Retry transient failures inside the subagent; propagate only what it could not resolve.\n"
    "- **Never hide it, never blow up.** Don't return an error as an empty success, and don't end the whole workflow on one failure.\n"
    "- **Say what you covered.** The synthesis annotates which topics are well supported and which have gaps."
)
MENTAL_MODEL = ("A subagent is a field researcher phoning the editor. “It didn't work” is useless; “the archive timed out after two "
                "tries, I have two of five sources, the newspaper morgue might have the rest” lets the editor decide. And “I found "
                "nothing” must never be the cover story for “I couldn't get in”.")

WHAT_IT_IS = """
**In the guide.** TS 5.3 (p.21): four Knowledge bullets and four Skills — structured context, empty vs failure, generic statuses,
the two anti-patterns, local recovery, and coverage annotations.

**What the docs add.** A failing tool goes back to the model as a `tool_result` with `is_error: true`, and the docs say to write
*instructive* messages (what went wrong, what to try next) rather than a bare “failed”. Only a subagent's **final message**
returns to its parent, so whatever the coordinator needs about a failure has to be in it. The Agent SDK ends a run with a typed
result subtype that must be checked before the result is read. The access-failure-versus-empty-result distinction is the guide's
own: the docs do not define it.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | Reference |
|---|---|---|---|
| 1 | Structured error context | A field report, not a shrug: what failed, what I tried, what I have, what else to try. | ⭐ TS 5.3 · Knowledge 1, Skill 1 |
| 2 | Access failure vs valid empty result | “Couldn't get in” and “nothing there” are different sentences. | ⭐ TS 5.3 · Knowledge 2, Skill 2 |
| 3 | Generic statuses hide context | “Unavailable” tells the editor nothing to decide with. | ⭐ TS 5.3 · Knowledge 3 |
| 4 | Silent suppression | Reporting a failed visit as “no one home” is lying with a straight face. | ⭐ TS 5.3 · Knowledge 4 |
| 5 | Terminating on one failure | One locked door shouldn't send the whole team home. | ⭐ TS 5.3 · Knowledge 4 |
| 6 | Local recovery | Jiggle the handle once before you phone the editor. | ⭐ TS 5.3 · Skill 3 |
| 7 | Coverage annotations | Mark the map: where we looked, and where we couldn't. | ⭐ TS 5.3 · Skill 4 |
| 8 | Instructive tool errors | An error message is the next instruction for the model. | 📘 docs (handle-tool-calls) |

**Failure shapes the coordinator can receive**

| # | What the subagent returns | What the coordinator can do | Verdict |
|---|---|---|---|
| 1 | `ok` with findings | Use them | ✅ |
| 2 | `empty` (query worked, no matches) | Record “searched, nothing found” | ✅ a valid result |
| 3 | `error` with type, attempted, partial, alternatives | Try an alternative, or continue with partial results and annotate | ✅ recoverable |
| 4 | `error`: “search unavailable” | Nothing but skip | ❌ context hidden |
| 5 | `empty` that was really a timeout | Believe a falsehood | ❌ suppressed |
| 6 | An exception that kills the run | Nothing: the coordinator never gets control | ❌ workflow terminated |
"""

HOW_IT_WORKS = """
1. The subagent runs its search. On a **transient** failure it retries once or twice itself.
2. If the search **worked** but matched nothing, it returns a distinct *empty* result. If it could **not** be completed, it
   returns an *error* carrying the failure type, what was attempted, any partial results, and alternatives.
3. The coordinator reads the status and decides: use it, try an alternative, or continue with what it has.
4. The synthesis writes the report **with coverage annotations**, so a gap is visible rather than silent.
"""

WHERE_SEEN = """
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.3–4): the web-search subagent times out; the coordinator must recover or
  proceed with partial results.
- The guide's own exercise for this task statement: simulate a subagent timeout, check the coordinator receives structured context,
  and check the final output annotates the coverage gap.
"""

GUIDE_NOTE = ("Grounded in the exam guide TS 5.3 (p.21) and the official docs fetched 2026-11-14 (handle-tool-calls, Agent SDK subagents "
              "and agent loop, MCP tools specification). The guide's access-failure-vs-empty-result distinction is not stated in the docs. "
              "Section layout inspired by a community concept list (claudearchitectcertification.com — unverified; no text copied). "
              "Note: TS 5.3 has no concept in that community list; this page was added because the guide has the task statement.")

LAB_INTRO = """
A **simulated** research run over three topics. You write `search_subagent(topic)` (what it sends the coordinator) and
`synthesize(findings, coverage)` (the report). The **coordinator is deterministic code**: it uses the status, tries one
alternative if you offered one, or proceeds with partial results. Four scenarios:

- a search that times out for good, with a news-archive alternative;
- a search that works and finds nothing;
- a one-off failure that a retry fixes;
- a search that dies half-way, with partial results.
"""

DISTRACTORS = (
    ("A · Generic status", "Simple, and it's honest that it failed.", "The coordinator can't choose a recovery.",
     "Failure type, attempted query, partial results, alternatives.", "guide:5.3:K3"),
    ("B · Empty success", "The run keeps going.", "A false “no results”; partial findings lost.",
     "Propagate the failure with its context.", "guide:5.3:K4"),
    ("C · Terminate everything", "Fail fast.", "Good findings from other topics are thrown away.",
     "Catch locally; let the coordinator proceed with partial results.", "guide:5.3:K4"),
    ("D · Empty as failure", "Better safe than sorry.", "A phantom problem and a wasted round trip.",
     "A distinct empty status for a query that worked.", "guide:5.3:K2"),
    ("E · No local recovery", "Let the coordinator decide everything.", "It is troubled by blips a retry would fix.",
     "Retry transient failures locally; propagate the rest.", "guide:5.3:S3"),
    ("F · No coverage annotations", "The report is cleaner.", "A report with gaps reads as complete.",
     "Annotate well-supported topics and gaps.", "guide:5.3:S4"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Situation", "Weak design", "Good design")
SIDE_BY_SIDE_ROWS = (
    ("1", "Search times out for good", "“search unavailable”: the topic is dropped", "Type, attempt, alternative: the coordinator tries the archive"),
    ("2", "Search works, no matches", "An error, and a wasted retry", "A distinct empty result: “searched, nothing found”"),
    ("3", "One-off failure", "The coordinator is told, and must act", "The subagent retries; nobody else hears of it"),
    ("4", "Dies half-way with 2 findings", "Empty success, or the whole run ends", "Partial results kept; the gap annotated"),
    ("5", "The final report", "Reads as complete", "States which topics are well supported and which have gaps"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Did the search\\ncomplete?"];
  Q2 [shape=diamond, label="Any matches?"];
  OK [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Return the findings"];
  EMPTY [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Return a distinct\\nempty result"];
  Q3 [shape=diamond, label="Transient and\\nrecoverable here?"];
  RETRY [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Retry locally"];
  ERR [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Propagate: type, attempted,\\npartial, alternatives"];
  Q1 -> Q2 [label="yes"]; Q1 -> Q3 [label="no (access failure)"];
  Q2 -> OK [label="yes"]; Q2 -> EMPTY [label="no"];
  Q3 -> RETRY [label="yes"]; Q3 -> ERR [label="no / retries used up"];
}''')

EXPERIMENTS = (
    "Run ✅ on all four scenarios and read each coverage line.",
    "Run ⭐❌ B on partial_gap: where did the two findings go?",
    "Run ⭐❌ C on empty_valid: it passes. Then on partial_gap: why does it fail there?",
    "In ✅, change `range(2)` to `range(5)`: does anything change for timeout_alt? What does that say about retrying a permanent failure?",
    "In the playground's empty-vs-failure tab, switch to “as an error” and watch the round trip appear.",
)

QUESTIONS = (
    Question(
        q=("A research coordinator delegates five topics to web-search subagents. When a source times out, the subagent retries "
           "twice and then returns `{\"status\": \"error\", \"message\": \"search unavailable\"}`. In 62% of these cases the "
           "coordinator drops the topic, although logs show an archive source answered the same query when tried by hand. "
           "What change would most effectively raise the recovery rate?"),
        opts=("Add a longer backoff to the subagent's retries so that a source has more time to come back.",
              "Return the failure type, attempted query, partial results and alternatives to the coordinator.",
              "Have the coordinator re-run every failed search itself, using its own tools, before it gives up on a topic.",
              "Replace the message with a more descriptive sentence, such as “search timed out after 30 seconds”."),
        ans=1,
        explain=("Structured context (type, attempted query, partial results, alternatives) lets the coordinator pick a recovery, such "
                 "as the archive. A retries a permanent failure for longer. C moves the work to the wrong agent and still hides what "
                 "failed. D is better wording but still unstructured, with no partial results or alternatives."),
        scenarios=(3,), points=("5.3:K1", "5.3:K3", "5.3:S1"),
    ),
    Question(
        q=("A final research report shows “film: source unavailable” in 18% of runs. Engineers find the film search returned HTTP 200 "
           "with zero results in every one of those runs, and the subagent maps zero results to an error status. The coordinator "
           "wastes a round trip on each. What is the most effective fix?"),
        opts=("Report a successful search with no matches as a distinct empty result, and keep errors for searches that fail.",
              "Retry any search that returns zero results, in case the source simply returned too few matches the first time.",
              "Broaden the query automatically whenever a search returns nothing, so that an empty result becomes much less likely.",
              "Drop topics with empty results from the report, so that readers never see a source flagged as unavailable."),
        ans=0,
        explain=("A query that worked and matched nothing is a valid result, and error reporting has to tell it apart from an access "
                 "failure. B and C treat a legitimate answer as a problem to be worked around. D hides real coverage information."),
        scenarios=(3,), points=("5.3:K2", "5.3:S2"),
    ),
    Question(
        q=("To keep runs from failing, a team makes each subagent catch every exception and return an empty list marked as "
           "successful. Last week a report said “no recent coverage of music”, but the music search had actually timed out. "
           "What is wrong with this design?"),
        opts=("It should log the exception and rethrow it, so that the whole workflow stops and an engineer reviews it.",
              "It should wait longer before catching, so a slow source has time to finish before the subagent reports.",
              "It should return an empty list only when the exception is a timeout, and rethrow every other exception type.",
              "It hides the failure as success; the subagent should propagate structured context for the coordinator."),
        ans=3,
        explain=("Returning an empty result as success is silent suppression: no recovery happens and the report says something false. "
                 "A swaps one anti-pattern for the other, ending the workflow on one failure. B and C keep the suppression."),
        scenarios=(3,), points=("5.3:K4",),
    ),
    Question(
        q=("Logs show the coordinator receives an error from 34% of searches, and about 80% of those succeed when simply retried "
           "once. Each error costs a coordinator round trip, adding about 40% latency to research runs. What is the most effective "
           "change?"),
        opts=("Let the coordinator retry every failed search itself, as it can then apply a consistent policy to all of them.",
              "Raise the subagents' timeout limit so that fewer searches fail in the first place, before any errors are propagated.",
              "Have subagents retry transient failures locally and propagate only what they cannot resolve, with context.",
              "Cache the results of every successful search for a day, so that repeated topics don't need to be searched again."),
        ans=2,
        explain=("Subagents should recover locally from transient failures and send up only what they cannot resolve, including what "
                 "was attempted and partial results. A keeps the round trips. B only reduces failures, and some will remain. D does "
                 "nothing for the failures that do happen."),
        scenarios=(3,), points=("5.3:S3",),
    ),
    Question(
        q=("A research report combines findings on five topics. Two topics rest on one source each, and one topic's only source was "
           "unavailable, so it was left out without a word. Readers treat the report as a complete survey. Which change to the "
           "synthesis step best prevents this?"),
        opts=("Add a closing line saying that the report is based on the sources that were available on the day it was written.",
              "Drop the thinly supported topics, so that the report contains only findings that rest on at least two sources.",
              "Rerun the whole research task until every source answers, and publish the report only when all five topics are covered.",
              "Annotate coverage: mark which findings are well supported and which topics have gaps because a source was unavailable."),
        ans=3,
        explain=("Coverage annotations show where the evidence is strong and where a source was missing, so gaps are visible. A is "
                 "vague boilerplate. B removes real findings. C may never finish when a source stays down, and hides nothing."),
        scenarios=(3,), points=("5.3:S4",),
    ),
    Question(
        q=("A client tool that queries an order system fails with a network error. The code returns the string “failed” as a normal "
           "tool result with no error flag, and the assistant keeps repeating the same call. What do the tool-use docs suggest?"),
        opts=("Raise an exception in the client so that the request ends, instead of returning anything to the model.",
              "Return the error with is_error set to true and an instructive message about what to try next.",
              "Return an empty tool result, so that the model infers for itself that the order system returned no data.",
              "Add a retry count to the system prompt, so that the model stops after three failed attempts at the call."),
        ans=1,
        explain=("The docs say to return the error in the tool result content with is_error true, and to write instructive messages "
                 "(what went wrong, what to try next) instead of a generic “failed”. A ends the run. C is the suppression anti-pattern. "
                 "D is a prompt instruction where the tool result should carry the information."),
        scenarios=(3,), basis="docs", in_bank=False,
    ),
    Question(
        q=("An orchestration script runs an Agent SDK task capped at 10 turns and reads the result text from the final message. On "
           "complex tasks it gets nothing and no error is logged. What do the docs say to do?"),
        opts=("Raise the cap to 100 turns, since a result is always produced when the cap is high enough.",
              "Read the result text from the last assistant message instead of from the final result message.",
              "Check the result subtype first: the text is present only on success, and hitting the cap is an error subtype.",
              "Wrap the call in a retry loop, since a missing result is a transient condition that goes away on a second run."),
        ans=2,
        explain=("The docs say the result field is present only on the success variant, so check the subtype before reading it, and a "
                 "run that hits max_turns ends with an error subtype and no final response. A only moves the cap. B reads a partial "
                 "message as if it were the result. D retries a deterministic outcome."),
        scenarios=(3,), basis="docs", in_bank=False,
    ),
)

FAQ = (
    ("How is this different from D2.3's structured errors?",
     "D2.3 is about one tool's error: `isError`, an error category, retryable or not. D5.3 is about what crosses an agent boundary: "
     "a subagent's failure reaching a coordinator, partial results, local recovery, and the coverage annotations in the final report."),
    ("Does the coordinator see a subagent's tool errors?",
     "Not directly. The docs say intermediate tool calls and results stay inside the subagent; only its final message returns. So "
     "whatever the coordinator needs about a failure must be in that final message."),
    ("Why does the docs' empty-result example not settle empty vs failure?",
     "It shows a tool_result with no content and doesn't say what it means. The valid-empty-versus-access-failure distinction is "
     "stated in the exam guide, not the docs, and this page labels it that way."),
    ("Is one local retry the right number?",
     "The guide names local recovery but not a count. One retry keeps the example small; real systems choose by the failure type."),
)

PLAYGROUND_INTRO = """
Each tab plays one sub-concept on the **simulated** research run. The message box holds the research question (the simulation
ignores its wording; what changes the result is how the subagent reports). Change the knobs and read the coverage lines.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="errprop")


_Q = "Research the impact of AI on creative industries: visual arts, music and film."

PLAYGROUND = (
    _tab("context", "⭐ Structured context", "context", "A field report, not a shrug.", "guide:5.3:K1",
         "The music search times out for good; a news-archive alternative exists.", "guide TS 5.3 K1, K3, S1; docs § is_error",
         ("ep_context",), {"ep_context": "full"}, (_Q,),
         ("generic: music becomes a gap, though the archive would have worked.",)),
    _tab("partial", "⭐ Partial results", "partial", "Hand over what you have.", "guide:5.3:K1",
         "The music search returns two findings, then times out.", "guide TS 5.3 K1, S1", ("ep_partial",), {"ep_partial": "keep"},
         (_Q,), ("drop: the two findings are lost; music becomes a bare gap.",)),
    _tab("empty", "⭐ Empty ≠ failure", "empty", "“Couldn't get in” vs “nothing there”.", "guide:5.3:K2",
         "The film search works and finds nothing.", "guide TS 5.3 K2, S2", ("ep_empty",), {"ep_empty": "valid"}, (_Q,),
         ("as an error: film becomes a gap and costs a round trip.",)),
    _tab("local", "⭐ Local recovery", "local", "Jiggle the handle first.", "guide:5.3:S3",
         "The music search fails once, then works.", "guide TS 5.3 S3", ("ep_local",), {"ep_local": "retry"}, (_Q,),
         ("none: the blip reaches the coordinator and costs a round trip.",)),
    _tab("anti", "⭐ The two anti-patterns", "anti", "Don't lie, and don't walk out.", "guide:5.3:K4",
         "The music search dies half-way.", "guide TS 5.3 K4", ("ep_failure",), {"ep_failure": "structured"}, (_Q,),
         ("suppress: “none found”, findings lost.", "terminate: no report at all.")),
    _tab("coverage", "⭐ Coverage annotations", "coverage", "Mark the map.", "guide:5.3:S4",
         "The music search dies half-way; two findings survive.", "guide TS 5.3 S4", ("ep_coverage",), {"ep_coverage": "annotate"}, (_Q,),
         ("none: the report reads as complete.",)),
)

CONTENT = ConceptContent(
    slug="error-propagation", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("escalation", "mcp", "subagents", "subagent-state-handoff"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("timeout_alt", "empty_valid", "transient", "partial_gap"), show_ledger=False,
)
