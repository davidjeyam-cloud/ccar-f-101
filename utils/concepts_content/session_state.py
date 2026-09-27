"""
D1.4 Session State & Persistence — guide TS 1.7 (sessions: resume, fork, fresh start with a summary; pp.8–9) and the
persistence parts of TS 5.4 (context degradation, scratchpad files, crash-recovery manifests, /compact; pp.21–22).

GROUNDING (CLAUDE.md, user rules 2026-09-26): the guide decides WHAT is examinable (read from the PDF on 2026-09-27);
the official docs decide how the mechanisms actually work (fetched 2026-09-27, DOC_REFS). Every claim is in GROUNDING
with its source type; simulation choices are labelled. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-27"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Manage sessions (Claude Code CLI)", f"{_C}/sessions"),
    DocRef("Work with sessions — continue, resume, fork (Agent SDK)", f"{_C}/agent-sdk/sessions"),
    DocRef("Best practices for Claude Code — manage your session and context", f"{_C}/best-practices"),
)

GROUNDING = (
    Claim("claude --continue reopens the most recent conversation in the current directory; claude --resume <name> resumes the "
          "named session directly (an ambiguous name opens the picker); claude --resume <session-id> works too.",
          "docs", "sessions § Resume a session"),
    Claim("Name a session at start with claude -n <name> or during it with /rename <name>, so it can be resumed by name.",
          "docs", "sessions § Name your sessions"),
    Claim("A resumed session restores the full conversation history, including tool calls and their results.",
          "docs", "sessions § What a resumed session restores"),
    Claim("Branching (/branch, or --continue/--resume with --fork-session) copies the conversation into a new session with its own "
          "id and leaves the original unchanged on disk. Resuming the same session in two terminals without forking interleaves "
          "both into one transcript.", "docs", "sessions § Branch a session"),
    Claim("Agent SDK: resume=<session id> continues a specific session; fork_session=True (forkSession in TypeScript) creates a new "
          "session starting from a copy of the history; continue_conversation=True resumes the most recent session in the directory.",
          "docs", "agent-sdk/sessions § Continue, resume, and fork; Resume by ID; Fork to explore alternatives"),
    Claim("Sessions persist the conversation, not the filesystem; forking branches the conversation, not the files — edits a forked "
          "agent makes are real.", "docs", "agent-sdk/sessions § notes on file checkpointing and forking"),
    Claim("An alternative to resuming: capture the results you need as application state and pass them into a fresh session's "
          "prompt — \"often more robust than shipping transcript files around\".",
          "docs", "agent-sdk/sessions § Resume across hosts"),
    Claim("LLM performance degrades as the context fills: Claude may start forgetting earlier instructions or making more mistakes; "
          "the context window is the most important resource to manage.", "docs", "best-practices (introduction)"),
    Claim("/compact [instructions] replaces the history with a summary, optionally focused; /clear starts an empty context; "
          "compaction instructions can be put in CLAUDE.md so critical context survives.",
          "docs", "sessions § Manage context within a session; best-practices § Manage context aggressively"),
    Claim("Resuming a long, idle session can offer \"resume from summary\", which runs /compact and keeps the summary, recent "
          "exchanges and up to five recently read files.", "docs", "sessions § Resume from a summary"),
    Claim("After a spec is written, the docs suggest starting a fresh session to execute it: clean context plus a written artifact.",
          "docs", "best-practices § Let Claude interview you"),
    Claim("Named session resumption with --resume <session-name>; fork_session for independent branches from a shared baseline; "
          "telling the agent about files changed since its analysis; a new session with a structured summary is more reliable than "
          "resuming with stale tool results.", "guide", "TS 1.7 · Knowledge 1–4 · pp.8–9"),
    Claim("Skills: resume named investigation sessions; fork to compare approaches; choose resume when prior context is mostly valid "
          "and fresh-with-summary when tool results are stale; name the specific changed files for targeted re-analysis instead of "
          "full re-exploration.", "guide", "TS 1.7 · Skills 1–4 · pp.8–9"),
    Claim("Context degradation in extended sessions shows as inconsistent answers that cite \"typical patterns\" instead of the "
          "specific classes found earlier; scratchpad files persist key findings; subagents isolate verbose exploration; each agent "
          "exports state to a known location and the coordinator loads a manifest on resume.",
          "guide", "TS 5.4 · Knowledge 1–4 · pp.21–22"),
    Claim("Skills: spawn subagents for specific questions; keep and reference scratchpad files; summarise a phase's findings before "
          "the next phase and inject them; design crash recovery with state exports (manifests) injected into agent prompts; use "
          "/compact when verbose discovery output fills the context.", "guide", "TS 5.4 · Skills 1–5 · pp.21–22"),
    Claim("The guide names --resume <session-name> (a CLI flag) and fork_session (an SDK option); in the SDK, resume takes a session "
          "ID, not a name. The page teaches both and says which is which.", "guide", "TS 1.7 vs agent-sdk/sessions"),
    Claim("The lab's rule of thumb — start fresh when more than half of the analysed files changed — is this page's choice; the guide "
          "says only \"mostly valid\" vs \"stale\".", "recommendation", "guide TS 1.7 · Skill 3"),
    Claim("The fake codebase, the ~800 tokens per file read, the degradation threshold (7,000 simulated tokens), when the simulated "
          "agent re-reads a file, and the manifest's shape are invented to make each behaviour reproducible.",
          "simulated", "utils/session_lab.py; utils/session_play.py"),
)

# ── Lab code ───────────────────────────────────────────────────────────────────

CORRECT = r'''from utils.session_lab import (ANALYZED_FILES, CHANGES, QUESTION, SCRATCHPAD, TASK, load_manifest, run_agent,
                               query, submit)   # SIMULATED session layer (shaped like the Agent SDK's session options)

BASELINE = "refund-investigation"     # yesterday's analysis session - resumed BY NAME (CLI: claude --resume <name>)

if TASK == "compare":
    # two approaches from ONE shared baseline: fork it twice; the baseline itself stays untouched
    a = query("Plan approach A: raise the limit behind a feature flag.", resume=BASELINE, fork_session=True)
    b = query("Plan approach B: move the limit into the config service.", resume=BASELINE, fork_session=True)
    print(a, b, sep="\n")
    submit(a, b)

elif TASK == "recover":
    manifest = load_manifest()                   # every agent exported its state to a known location before the crash
    findings = {}
    for area, state in manifest["agents"].items():
        if state["status"] == "done":
            findings[area] = state["findings"]   # reuse finished work - don't redo it
        else:                                    # inject the saved state into the unfinished agent's prompt
            findings[area] = run_agent(area, f"Continue exploring {area}. Your saved state: {state['partial']}")
    print(findings)
    submit(findings)

elif len(CHANGES) > len(ANALYZED_FILES) / 2:     # most earlier tool results are stale -> fresh session + structured summary
    r = query(f"Key findings so far:\n{SCRATCHPAD}\nFiles changed since then (old -> new): {CHANGES}\n\n{QUESTION}",
              name="refund-investigation-v2")
    print(r)
    submit(r)

elif CHANGES:                                    # earlier context mostly valid -> resume, and say exactly what changed
    r = query(f"Since your analysis these files changed: {list(CHANGES)}. Re-read only those.\n{QUESTION}",
              resume=BASELINE)
    print(r)
    submit(r)

else:                                            # nothing changed -> resume the named session
    r = query(QUESTION, resume=BASELINE)
    print(r)
    submit(r)
'''


def _swap(code: str, old: str, new: str) -> str:
    assert old in code, f"lab code changed, cannot apply variant edit: {old[:60]!r}"
    return code.replace(old, new, 1)


_MOST = '''elif len(CHANGES) > len(ANALYZED_FILES) / 2:     # most earlier tool results are stale -> fresh session + structured summary
    r = query(f"Key findings so far:\\n{SCRATCHPAD}\\nFiles changed since then (old -> new): {CHANGES}\\n\\n{QUESTION}",
              name="refund-investigation-v2")
    print(r)
    submit(r)

'''
_ONE = '''elif CHANGES:                                    # earlier context mostly valid -> resume, and say exactly what changed
    r = query(f"Since your analysis these files changed: {list(CHANGES)}. Re-read only those.\\n{QUESTION}",
              resume=BASELINE)'''

VARIANT_A = _swap(CORRECT, _ONE, '''elif CHANGES:
    r = query(QUESTION, resume=BASELINE)   # WRONG: resumes but never says which files changed since the analysis''')
VARIANT_B = _swap(_swap(CORRECT, _MOST, ""), _ONE, '''elif CHANGES:                                    # WRONG: something changed, so throw the analysis away
    r = query(QUESTION, name="refund-investigation-v2")   # a fresh session with NO summary: full re-exploration''')
VARIANT_C = _swap(CORRECT, _MOST, "")    # always resume + name the changes, even when most results are stale
VARIANT_C = _swap(VARIANT_C, "elif CHANGES:                                    # earlier context mostly valid -> resume, and say exactly what changed",
                  "elif CHANGES:                                    # WRONG: always resume, however much of the earlier context is stale")
VARIANT_D = _swap(CORRECT, '''    a = query("Plan approach A: raise the limit behind a feature flag.", resume=BASELINE, fork_session=True)
    b = query("Plan approach B: move the limit into the config service.", resume=BASELINE, fork_session=True)''',
                  '''    # WRONG: resumes the same baseline for both approaches instead of forking it
    a = query("Plan approach A: raise the limit behind a feature flag.", resume=BASELINE)
    b = query("Plan approach B: move the limit into the config service.", resume=BASELINE)''')
VARIANT_E = _swap(CORRECT, '''    manifest = load_manifest()                   # every agent exported its state to a known location before the crash
    findings = {}
    for area, state in manifest["agents"].items():
        if state["status"] == "done":
            findings[area] = state["findings"]   # reuse finished work - don't redo it
        else:                                    # inject the saved state into the unfinished agent's prompt
            findings[area] = run_agent(area, f"Continue exploring {area}. Your saved state: {state['partial']}")''',
                  '''    # WRONG: ignores the exported state and starts every agent again from scratch
    findings = {area: run_agent(area, f"Explore {area}.") for area in ("test_files", "refund_flow", "auth_flow")}''')
VARIANT_F = _swap(_swap(CORRECT, '''              resume=BASELINE)
    print(r)''', '''              continue_conversation=True)   # WRONG: "the most recent session" - not necessarily the analysis
    print(r)'''), '''    r = query(QUESTION, resume=BASELINE)
    print(r)''', '''    r = query(QUESTION, continue_conversation=True)   # WRONG: claude --continue picks the MOST RECENT session
    print(r)''')

# ── Result check, chart ────────────────────────────────────────────────────────

_TRUTH = {"next_day_unchanged": (100, "refund_policy.py"), "one_file_changed": (50, "refund_policy.py"),
          "major_refactor": (75, "policies/refunds.py")}


def _facts(trace: dict) -> dict:
    ev = trace["events"]
    qs = [e for e in ev if e["kind"] == "session_query"]
    subs = [e for e in ev if e["kind"] == "submit"]
    runs = [e for e in ev if e["kind"] == "agent_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "qs": qs,
            "sub": subs[-1] if subs else None, "runs": runs, "manifest": any(e["kind"] == "manifest_loaded" for e in ev)}


def _diagnose(f: dict) -> tuple:
    """(ok, bug-node or None, text) for one run."""
    sc, qs, sub = f["scenario"], f["qs"], f["sub"]
    if f["raised"] or sub is None:
        return False, None, f"no result submitted ({f['raised'] or 'nothing submitted'})"
    if sc == "compare_approaches":
        forked = [q for q in qs if q["forked"] and q["base"] == "refund-investigation"]
        saw = any(q["saw_other_approach"] for q in qs)
        intact = sub["baseline_len"] == sub["baseline_len_day1"]
        ok = len(forked) == 2 and not saw and intact
        return ok, None if ok else "NOFORK", (f"forked branches: {len(forked)} · approach B carried approach A: {saw} · "
                                              f"baseline history unchanged: {intact}")
    if sc == "crash_recovery":
        n, had = len(f["runs"]), all(r["had_state"] for r in f["runs"])
        areas = next((i["areas"] for i in sub["items"] if i["type"] == "findings"), [])
        ok = f["manifest"] and n == 1 and had and len(areas) == 3
        return ok, None if ok else "RESTART", (f"manifest loaded: {f['manifest']} · agent runs: {n} · saved state injected: "
                                               f"{had} · areas in report: {len(areas)}")
    q = qs[-1] if qs else None
    value, path = _TRUTH[sc]
    if q is None:
        return False, None, "no query made"
    txt = (f"session: {q['session_name']} · file reads: {q['reads']} · context: {q['ctx']} tokens · answer: "
           f"{q['value'] if q['value'] is not None else 'vague / none'}{' in ' + q['path'] if q['path'] else ''} "
           f"(truth: {value} in {path})")
    if q["continued"] and q["session_name"] != "refund-investigation":
        return False, "CONTINUE", txt
    if q["degraded"]:
        return False, "STALE", txt
    if q["value"] is not None and (q["value"], q["path"]) != (value, path):
        return False, "SILENT", txt
    if q["reads"] > (0 if sc == "next_day_unchanged" else 2):
        return False, "REEXPLORE", txt
    return (q["value"], q["path"]) == (value, path), None, txt


def check_outcome(scenario: str, trace: dict):
    f = _facts(trace)
    ok, _bug, txt = _diagnose(f)
    expected = {
        "next_day_unchanged": "the named session resumed, with the correct answer and no re-reads",
        "one_file_changed": "the correct CURRENT limit (50) with at most 2 targeted re-reads and no degraded answer",
        "major_refactor": "the correct current limit (75 in policies/refunds.py), not degraded, at most 2 file reads",
        "compare_approaches": "two forks of the baseline, neither carrying the other, and the baseline history unchanged",
        "crash_recovery": "the manifest loaded, only the unfinished agent re-run (with its saved state), all 3 areas reported",
    }[scenario]
    return ok, expected, txt


_CONCEPT = {
    "decide":  ("#EDE9FE", "#7C3AED", "the decision — how much of the old context is still true?"),
    "resume":  ("#DBEAFE", "#0066CC", "resume (by name; tell it what changed)"),
    "fresh":   ("#FEF3C7", "#D97706", "fresh start + structured summary / scratchpad / /compact"),
    "branch":  ("#CCFBF1", "#0D9488", "branch with fork_session"),
    "recover": ("#D1FAE5", "#059669", "crash recovery from a manifest"),
    "bug":     ("#FFFFFF", "#DC2626", "bug (an exam distractor)"),
}
_NODES = {
    "START":    ("Returning to\\nearlier work", "box", "decide"),
    "Q":        ("What's still true\\nsince then?", "diamond", "decide"),
    "NAMED":    ("⭐ nothing changed\\n→ --resume <name>", "box", "resume"),
    "TELL":     ("⭐ a few files changed\\n→ resume + name the files\\n(targeted re-read)", "box", "resume"),
    "FRESH":    ("⭐ most results stale\\n→ new session +\\nstructured summary", "box", "fresh"),
    "FORK":     ("⭐ explore alternatives\\n→ fork_session per approach", "box", "branch"),
    "CRASH":    ("⭐ a run crashed\\n→ load the manifest,\\nre-run only the unfinished", "box", "recover"),
    "DONE":     ("A specific, current answer", "box", "resume"),
    "CONTINUE": ("✗ --continue: the most\\nrecent session, not the named one", "box", "bug"),
    "SILENT":   ("✗ resume without saying\\nwhat changed → stale answer", "box", "bug"),
    "REEXPLORE": ("✗ fresh with no summary\\n→ full re-exploration", "box", "bug"),
    "STALE":    ("✗ resume a mostly-stale\\nsession → degraded answer", "box", "bug"),
    "NOFORK":   ("✗ resume the same baseline\\nfor both approaches", "box", "bug"),
    "RESTART":  ("✗ restart every agent\\nafter the crash", "box", "bug"),
}
_BRANCHES = ["NAMED", "TELL", "FRESH", "FORK", "CRASH"]
_BUGS = ["CONTINUE", "SILENT", "REEXPLORE", "STALE", "NOFORK", "RESTART"]
_EXPECTED_NODE = {"next_day_unchanged": "NAMED", "one_file_changed": "TELL", "major_refactor": "FRESH",
                  "compare_approaches": "FORK", "crash_recovery": "CRASH"}


def _key(highlighted: bool) -> str:
    rows = "".join(f'<TR><TD BGCOLOR="{fill}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0">'
                   f'<FONT POINT-SIZE="10">{text}</FONT></TD></TR>' for fill, _l, text in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">'
             'named by the exam guide (TS 1.7 pp.8–9, TS 5.4 pp.21–22)</FONT></TD></TR>')
    if highlighted:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = the branch that '
                 'fits · <B>red</B> = the bug your run shows · grey = not this scenario</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3">'
            '<TR><TD COLSPAN="2" BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states: dict) -> str:
    hl = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.25; ranksep=0.5; newrank=true;',
             '  node [fontname="Helvetica", fontsize=12, style="rounded,filled", penwidth=2];',
             '  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];']
    for node, (label, shape, concept) in _NODES.items():
        fill, line, _ = _CONCEPT[concept]
        text = label
        if hl:
            state, suffix = states.get(node, (None, ""))
            fill = {"ok": "#BBF7D0", "bad": "#FECACA"}.get(state, "#F3F4F6")
            if state is None and concept != "bug":
                line = "#9CA3AF"
            if suffix:
                text = f"{label}\\n{suffix}"
        style = "rounded,filled,dashed" if concept == "bug" else "rounded,filled"
        lines.append(f'  {node} [label="{text}", shape={shape}, style="{style}", fillcolor="{fill}", color="{line}"];')
    lines.append("  START -> Q;")
    lines += [f"  Q -> {n}; {n} -> DONE;" for n in _BRANCHES]
    lines.append("  { rank=same; " + "; ".join(_BRANCHES) + "; }")
    lines.append("  { rank=same; " + "; ".join(_BUGS) + "; }")
    lines.append("  DONE -> CONTINUE [style=invis];")
    lines.append(_key(hl))
    lines.append("  RESTART -> KEY [style=invis];")
    lines.append("}")
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace) -> dict:
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, txt = _diagnose(f)
    exp = _EXPECTED_NODE.get(f["scenario"])
    s = {"START": ("ok", ""), "Q": ("ok", "")}
    if ok:
        s[exp] = ("ok", "")
        s["DONE"] = ("ok", "")
    else:
        if exp:
            s[exp] = ("ok", "the branch that fits")
        if bug:
            s[bug] = ("bad", "your run")
        s["DONE"] = ("bad", "not achieved")
    return s


# ── What the guide demands ─────────────────────────────────────────────────────

EXAM_POINTS = (
    ExamPoint("1.7", "K", 1, "Resume a specific earlier conversation by name with --resume <session-name>.", "❌ F · playground “Return by name”"),
    ExamPoint("1.7", "K", 2, "fork_session creates independent branches from a shared analysis baseline to explore different approaches.",
              "✅ compare · ❌ D · playground “fork_session”"),
    ExamPoint("1.7", "K", 3, "When resuming after code changes, tell the agent which previously analysed files changed.",
              "❌ A · playground “What changed?”"),
    ExamPoint("1.7", "K", 4, "A new session seeded with a structured summary is more reliable than resuming with stale tool results.",
              "✅ major_refactor · ❌ C"),
    ExamPoint("1.7", "S", 1, "Continue named investigation sessions across work sessions with --resume <name>.", "✅ next_day_unchanged · ❌ F"),
    ExamPoint("1.7", "S", 2, "Use fork_session for parallel exploration branches (e.g. two testing or refactoring strategies from one analysis).",
              "✅ compare_approaches"),
    ExamPoint("1.7", "S", 3, "Choose: resume when prior context is mostly valid; start fresh with an injected summary when tool results are stale.",
              "✅ · ❌ B · ❌ C · playground “What changed?”"),
    ExamPoint("1.7", "S", 4, "Tell a resumed session about the specific changed files for targeted re-analysis, not full re-exploration.",
              "❌ A · ❌ B"),
    ExamPoint("5.4", "K", 1, "Context degradation in long sessions: inconsistent answers that cite “typical patterns” instead of the specific "
              "classes found earlier.", "❌ C · playground “Degradation & /compact”"),
    ExamPoint("5.4", "K", 2, "Scratchpad files persist key findings across context boundaries.", "✅ SCRATCHPAD summary · playground “Degradation & /compact”"),
    ExamPoint("5.4", "K", 3, "Subagents isolate verbose exploration output while the main agent keeps the high-level picture.",
              "the D1.2 Subagents page (isolated context)"),
    ExamPoint("5.4", "K", 4, "Crash recovery: each agent exports its state to a known location; the coordinator loads a manifest on resume.",
              "✅ crash_recovery · ❌ E · playground “Crash recovery”"),
    ExamPoint("5.4", "S", 1, "Spawn subagents for specific questions while the main agent coordinates.", "the D1.2 Subagents page"),
    ExamPoint("5.4", "S", 2, "Keep scratchpad files of key findings and reference them for later questions to counteract degradation.",
              "playground “Degradation & /compact” (scratchpad)"),
    ExamPoint("5.4", "S", 3, "Summarise one phase's findings before starting the next, and inject the summary into the new context.",
              "✅ major_refactor (summary injected)"),
    ExamPoint("5.4", "S", 4, "Design crash recovery around structured state exports (manifests) loaded on resume and injected into prompts.",
              "✅ crash_recovery · ❌ E"),
    ExamPoint("5.4", "S", 5, "Use /compact when verbose discovery output fills the context during long exploration.",
              "playground “Degradation & /compact”"),
)

# ── Variants ───────────────────────────────────────────────────────────────────

VARIANTS = (
    Variant("correct", "✅ ⭐ Pick the right way back, every time", "correct", CORRECT, "one_file_changed",
            observe=("On one_file_changed the named session is resumed and told that refund_policy.py changed: ONE targeted re-read, "
                     "answer 50 (the current value). Walk the scenarios: next_day_unchanged resumes by name with 0 reads; "
                     "major_refactor starts fresh with the scratchpad summary and the change list (1 read, 75 in policies/refunds.py); "
                     "compare_approaches forks twice and the baseline keeps its 8 Day-1 entries; crash_recovery re-runs only auth_flow."),
            why=("Each situation gets the continuation that matches how much of the earlier context is still true — and every "
                 "continuation carries exactly the context the agent needs: a name, a list of changed files, a summary, a fork or "
                 "a manifest.")),
    Variant("A", "⭐❌ A — resume without saying what changed", "distractor", VARIANT_A, "one_file_changed",
            observe=("Resumed, no mention of the change: 0 re-reads, and the answer is 100 — the value from yesterday's Read result. "
                     "The file now says 50. (On major_refactor this variant still takes the fresh-start branch, so the bug only shows here.)"),
            why=("A resumed session restores its old tool results. Nothing tells the agent those results are out of date, so it "
                 "answers from them."),
            fix="Name the specific changed files when resuming so the agent re-reads just those.", source="guide:1.7:K3"),
    Variant("B", "⭐❌ B — any change? start over with no summary", "distractor", VARIANT_B, "one_file_changed",
            observe=("The answer is right (50) — but a fresh session with no summary had to read all 6 files again to find it, versus "
                     "1 targeted read. Same on major_refactor: 6 reads."),
            why=("Throwing the analysis away costs a full re-exploration. When most of the context is still valid, resume and name "
                 "the changes; when it isn't, start fresh WITH a summary."),
            fix="Resume + name the changed files; or, if most results are stale, a fresh session seeded with a structured summary.",
            source="guide:1.7:S4"),
    Variant("C", "⭐❌ C — always resume, however stale", "distractor", VARIANT_C, "major_refactor",
            observe=("On major_refactor it resumes and names all 5 changed files: 5 re-reads on top of the Day-1 history push the "
                     "context to ~9,300 simulated tokens, and the answer degrades to “typically defined as a constant in a policy or "
                     "config module” — no value, no file. On one_file_changed it's fine."),
            why=("When most tool results are stale, resuming drags them all along. The guide calls a fresh start with a structured "
                 "summary the more reliable choice, and names vague “typical pattern” answers as the sign of context degradation."),
            fix="When most earlier results are stale, start a new session and inject a structured summary of the findings.",
            source="guide:1.7:K4"),
    Variant("D", "⭐❌ D — resume the same baseline for both approaches", "distractor", VARIANT_D, "compare_approaches",
            observe=("Both approaches are appended to refund-investigation itself: approach B's answer shows it is ALSO CARRYING "
                     "approach A, and the baseline grows from 8 to 12 entries — it is no longer the shared starting point."),
            why="Resuming adds to a session. Only a fork copies the history into a new, independent session and leaves the original unchanged.",
            fix="Fork the baseline (fork_session / --fork-session / /branch) once per approach.", source="guide:1.7:K2"),
    Variant("E", "⭐❌ E — restart every agent after a crash", "distractor", VARIANT_E, "crash_recovery",
            observe=("The manifest is never loaded: all 3 agents run again from scratch — 3 runs instead of 1, and auth_flow starts "
                     "over instead of continuing from its saved state."),
            why="Without loading the exported state, the coordinator has no record of what finished, so finished work is redone.",
            fix="Have each agent export its state to a known location; on resume, load the manifest, reuse finished results and "
                "inject saved state into the prompts of the unfinished agents.", source="guide:5.4:S4"),
    Variant("F", "⭐❌ F — --continue instead of resuming by name", "distractor", VARIANT_F, "next_day_unchanged",
            observe=("continue_conversation picks the MOST RECENT session — the unrelated docs-typo fix — which never saw the refund "
                     "code, so it explores all 6 files again. The answer is right; the investigation's history was never used."),
            why="“Most recent” is not “the one I mean”. The guide's skill is resuming named investigation sessions.",
            fix="Name investigation sessions (claude -n / /rename) and resume them by name (claude --resume <name>).",
            source="guide:1.7:S1"),
)

# ── Prose ──────────────────────────────────────────────────────────────────────

TLDR = (
    "A **session** is the saved conversation — every prompt, tool call and tool result. Coming back to work, you choose how much "
    "of it to carry forward: **resume by name** when it's still true; **resume and name the changed files** when a few things "
    "changed; **start fresh with a structured summary** when most tool results are stale; **fork** it to try two approaches from "
    "the same baseline. In long explorations the context itself degrades, so keep key findings in a **scratchpad**, use "
    "**/compact**, and in multi-agent runs export each agent's state to a **manifest** so a crash doesn't cost the finished work."
)

MENTAL_MODEL = ("A session is a lab notebook: resume it when the notes still describe the bench, add an erratum page when a few "
                "things moved, start a new notebook with a one-page summary when the lab was rebuilt — and photocopy it before "
                "trying two experiments at once.")

WHAT_IT_IS = """
The exam guide asks for two things here: managing sessions — resuming, forking, starting fresh with a summary (Guide §6 · TS 1.7,
pp.8–9) — and keeping state reliable during long codebase exploration: context degradation, scratchpads, manifests, `/compact`
(TS 5.4, pp.21–22). The official docs describe the actual controls.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Named resumption | A labelled folder: you reopen *that* case file — “the most recent folder on the desk” may be something else. | ⭐ TS 1.7 · Knowledge 1, Skill 1 · pp.8–9 |
| 2 | Telling a resumed session what changed | An erratum slip in the notebook: without it, the old notes are read as if they were still true. | ⭐ TS 1.7 · Knowledge 3, Skill 4 · pp.8–9 |
| 3 | Fresh start with a structured summary | A new notebook whose first page is the summary — cleaner than a notebook full of crossed-out pages. | ⭐ TS 1.7 · Knowledge 4, Skill 3 · pp.8–9 |
| 4 | `fork_session` | A photocopy of the case file: each investigator works on their own copy; the original stays clean. | ⭐ TS 1.7 · Knowledge 2, Skill 2 · pp.8–9 |
| 5 | Context degradation | An overfull desk: past a point you stop citing the page you read and start saying “usually it's like…”. | ⭐ TS 5.4 · Knowledge 1 · pp.21–22 |
| 6 | Scratchpad files | Sticky notes on the monitor: the key facts stay visible however deep the pile gets. | ⭐ TS 5.4 · Knowledge 2, Skill 2 · pp.21–22 |
| 7 | `/compact` | Tidying the desk into one summary sheet — you keep the gist, lose the detail you didn't ask it to keep. | ⭐ TS 5.4 · Skill 5 · pp.21–22 |
| 8 | Crash-recovery manifest | Each worker files a status card before leaving; after the power cut the manager reads the cards, not the whole project again. | ⭐ TS 5.4 · Knowledge 4, Skill 4 · pp.21–22 |

**The controls — CLI and Agent SDK** (docs)

| # | You want to… | Claude Code CLI | Agent SDK (Python) | What happens |
|---|---|---|---|---|
| 1 | continue the most recent conversation | `claude --continue` | `continue_conversation=True` | Reopens the most recent session in this directory — whatever it was |
| 2 | continue a specific one | `claude --resume <name>` (or `<session-id>`) | `resume=<session id>` | Full history restored, including tool calls and results |
| 3 | name a session | `claude -n <name>` · `/rename <name>` | — (track the session id) | Makes it resumable by name |
| 4 | branch without touching the original | `--resume <…> --fork-session` · `/branch` | `resume=<id>, fork_session=True` | A new session with a copy of the history and its own id; the original unchanged. Files are **not** branched |
| 5 | shrink the context | `/compact [instructions]` · `/clear` | — | Summary replaces the history / empty context |

**Guide vs docs.** The guide says `--resume <session-name>` (a CLI flag) and `fork_session` (an SDK option). In the SDK, `resume`
takes a session **ID**, not a name. Neither source disagrees on behaviour.
"""

HOW_IT_WORKS = """
1. **Name investigations** so you can come back to them by name. `--continue` only means “the most recent one”.
2. **Before continuing, ask how much of the old context is still true.** A resumed session restores its old tool results —
   they don't update themselves.
3. **Mostly still true → resume, and name the changed files.** The agent re-reads just those (targeted re-analysis).
4. **Mostly stale → start a new session with a structured summary** (goal, key findings, decisions, what moved). Don't resume and
   don't re-explore from nothing.
5. **Two approaches from one analysis → fork it**, once per approach. Resuming the same session for both mixes them.
6. **During long explorations:** keep a scratchpad of key findings, `/compact` when discovery output piles up, and push verbose
   exploration into subagents (D1.2).
7. **Multi-agent runs:** every agent exports its state to a known location; after a crash the coordinator loads the manifest, reuses
   finished work and injects saved state into the prompts of the agents that hadn't finished.
"""

WHERE_SEEN = """
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): an agent that explores unfamiliar codebases over several work
  sessions — resume, fork and fresh-with-summary decisions.
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): day-to-day Claude Code sessions, `/compact`, context management.
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): coordinator + agents where crash recovery from manifests matters.
"""

GUIDE_NOTE = (
    "Grounded in the official docs (verified 2026-09-27 — pages listed above) and the exam guide §6 TS 1.7 (pp.8–9) and TS 5.4 "
    "(pp.21–22). Section layout inspired by a community concept list (claudearchitectcertification.com — community source, "
    "unverified; no text copied)."
)

LAB_INTRO = """
Yesterday you analysed the refund code in a session named **refund-investigation** (6 files read), then fixed an unrelated typo — so the
*most recent* session is not the analysis. Each scenario is a different “next day”. **You write the code that decides how to continue**
against a **simulated** session layer shaped like the Agent SDK's `resume` / `fork_session` / `continue_conversation`. The result check
wants the *current* answer with no more work than necessary. The variants are the correct design plus six mistakes, all named by the
exam guide (⭐).
"""

DISTRACTORS = (
    ("A · Resume without saying what changed", "The session has all the context — just continue.",
     "Its tool results are from before the change; it answers with the old value.", "Name the changed files so it re-reads just those.",
     "guide:1.7:K3"),
    ("B · Any change → start over with no summary", "A clean start can't be stale.",
     "Correct, but at the cost of re-exploring everything.", "Resume + targeted re-read, or fresh WITH a structured summary.",
     "guide:1.7:S4"),
    ("C · Always resume, however stale", "Resuming keeps the most context.",
     "Mostly-stale results plus the re-reads bloat the context; answers degrade.", "Start fresh with a structured summary.",
     "guide:1.7:K4"),
    ("D · Resume the same baseline for both approaches", "Both approaches need the baseline analysis.",
     "They pile into one session: B carries A, and the baseline is lost.", "Fork the baseline once per approach.", "guide:1.7:K2"),
    ("E · Restart every agent after a crash", "A clean restart is safest.",
     "Finished work is redone; unfinished agents lose their progress.", "Export state; load the manifest; re-run only what's unfinished.",
     "guide:5.4:S4"),
    ("F · --continue instead of resuming by name", "It picks up where you left off.",
     "It picks the most recent session, which may be a different task.", "Name sessions; resume by name.", "guide:1.7:S1"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Resume (by name)", "Fork", "Fresh start + structured summary")
SIDE_BY_SIDE_ROWS = (
    ("1", "Starts from", "The session's full history", "A copy of the history, as a new session", "Only the summary you inject"),
    ("2", "The original session", "Grows with the new turns", "Unchanged", "Unchanged (not used)"),
    ("3", "Old tool results", "All carried — tell it what changed", "All carried", "None — only the summary's facts"),
    ("4", "Best when", "Prior context is mostly valid (TS 1.7 S3)", "Trying alternatives from one baseline (TS 1.7 S2)",
     "Prior tool results are stale (TS 1.7 K4)"),
    ("5", "Typical failure", "Stale answers if nobody says what changed", "Forgetting that files aren't branched",
     "A thin summary that misses key decisions"),
    ("6", "Controls", "claude --resume <name> · SDK resume=<id>", "--fork-session · /branch · fork_session=True",
     "a new session + summary in the prompt (scratchpad, /compact summary)"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=11, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=10, color="#6B7280"];
  Q0 [shape=diamond, label="Do you want to try\\nmore than one direction?"];
  FORK [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Fork the baseline per direction\\n(guide TS 1.7 K2, S2)"];
  Q1 [shape=diamond, label="How much of the earlier\\ntool results is still true?"];
  RES [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="All of it: --resume <name>\\n(TS 1.7 K1, S1)"];
  TELL [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Mostly: resume + name the changed files\\n(TS 1.7 K3, S4)"];
  FRESH [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Little: new session + structured summary\\n(TS 1.7 K4, S3)"];
  Q2 [shape=diamond, label="Session getting long,\\nanswers turning vague?"];
  CMP [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Scratchpad of key findings, /compact,\\nsubagents for exploration (TS 5.4)"];
  Q0 -> FORK [label="yes"]; Q0 -> Q1 [label="no"];
  Q1 -> RES [label="all"]; Q1 -> TELL [label="mostly"]; Q1 -> FRESH [label="little"];
  RES -> Q2; TELL -> Q2; Q2 -> CMP [label="yes"];
}'''

EXPERIMENTS = (
    "Run ✅ on each scenario and watch the chart: a different branch lights up each time.",
    "Run ⭐❌ A on one_file_changed and compare its answer with the file (50). Then add the changed file list to its prompt yourself.",
    "In ✅, change the fresh-start threshold `len(ANALYZED_FILES) / 2` to `99` and run major_refactor — you just built ⭐❌ C.",
    "Run ⭐❌ D on compare_approaches: read approach B's answer for “ALSO CARRYING”.",
    "Run ⭐❌ F on next_day_unchanged and look at which session name was continued.",
)

QUESTIONS = (
    Question(
        q=("On Monday a developer ran a 3-hour Claude Code investigation of the payments service, in a session named "
           "payments-audit. Since then they have opened five unrelated sessions in the same repository. On Wednesday they "
           "want to pick up exactly that investigation, with its earlier findings intact. What should they run?"),
        opts=("claude --continue, which reopens the most recent conversation in the current directory with its history.",
              "claude --resume payments-audit, which reopens that named session with its full conversation history.",
              "A new session, pasting in Monday's final message so that the key conclusions carry into the new context.",
              "claude -p \"resume payments-audit\", which runs the named session non-interactively and prints its findings."),
        ans=1,
        explain=("--resume with the session name reopens that exact conversation. A would open the most recent of the five "
                 "unrelated sessions. C throws away the history the developer wants to keep. D misuses -p, which sends a "
                 "new prompt in print mode; it doesn't select an old session."),
        scenarios=(2, 4), points=("1.7:K1", "1.7:S1"),
    ),
    Question(
        q=("A developer resumes yesterday's analysis session of an order service. Overnight a teammate merged changes to 2 of "
           "the 11 files the session had analysed. The resumed session now recommends a fix to a function that the merge "
           "renamed. What is the most efficient way to keep the analysis accurate?"),
        opts=("Start a fresh session and have it re-analyse all 11 files, so that nothing stale can remain in its context.",
              "Keep going in the resumed session and trust it to notice the changes the next time it reads any of the files.",
              "Tell the resumed session which 2 files changed and have it re-analyse just those before it continues.",
              "Run /compact so the stale tool results are summarised away before the session continues with its work."),
        ans=2,
        explain=("When you resume, tell the session exactly what changed so it can re-analyse just those parts. Most of its "
                 "earlier work is still valid. A throws away nine files of valid analysis. B is how the stale "
                 "recommendation happened. D summarises the stale results but doesn't correct them."),
        scenarios=(4,), points=("1.7:K3", "1.7:S4"),
    ),
    Question(
        q=("Three weeks after an architecture investigation, a large refactor has rewritten about 70% of the modules that "
           "session read. The developer resumes it, and within ten minutes it cites two classes that no longer exist. What "
           "is the most reliable way to continue the investigation?"),
        opts=("Keep the resumed session, and tell it which modules were refactored so it can re-read each one on demand.",
              "Fork the old session, so the original stays untouched while the fork explores the refactored modules afresh.",
              "Run /compact in the resumed session, so the outdated file contents are condensed before it continues.",
              "Start a new session seeded with a structured summary of what still holds, and re-explore the changed code."),
        ans=3,
        explain=("When most earlier tool results are stale, a new session seeded with a structured summary is more reliable "
                 "than resuming. A works for a few changed files, but here most of the context is wrong and keeps "
                 "competing with the new reads. B copies the same stale context into the fork. C condenses the outdated "
                 "content without correcting it."),
        scenarios=(2, 4), points=("1.7:K4", "1.7:S3"),
    ),
    Question(
        q=("After a 90-minute shared analysis of a legacy billing module, the team wants to compare two refactoring "
           "strategies: strangler-fig and in-place rewrite. Neither exploration should influence the other, both results "
           "must be kept for a side-by-side review, and nobody wants to repeat the analysis. What should they use?"),
        opts=("Fork the analysis session twice, giving two independent branches from the same analysed baseline.",
              "Continue the analysis session and explore both strategies in turn, labelling each part of the conversation.",
              "Start two fresh sessions and paste the same one-paragraph summary of the analysis into each as the opener.",
              "Explore the first strategy, then /rewind to the end of the analysis and explore the second one from there."),
        ans=0,
        explain=("Forking gives divergent branches from a shared baseline: each keeps the full analysis, and neither sees the "
                 "other. B lets the first exploration colour the second. C throws away most of the 90-minute analysis. D "
                 "rewinds away the first strategy's conversation, so there is nothing left to compare side by side."),
        scenarios=(2, 4), points=("1.7:K2", "1.7:S2", "1.3:K4"),
    ),
    Question(
        q=("Two hours into a codebase exploration, the agent's answers start contradicting answers it gave earlier. It "
           "mentions “typical repository patterns” instead of the specific classes it found an hour ago. The session has "
           "already been compacted twice. What best prevents this for the rest of the task?"),
        opts=("Have the agent record key findings in a scratchpad file and consult that file when answering later questions.",
              "Switch to a model with a larger context window, so that early findings are never pushed out of its context.",
              "Instruct the agent in its system prompt to always refer to specific class names rather than general patterns.",
              "Run /compact more often, so the context stays small enough that earlier findings always remain in view."),
        ans=0,
        explain=("Context degradation in long sessions is countered by persisting key findings to a scratchpad file and "
                 "referring back to it. A larger window (B) delays the problem without fixing it. C instructs the model to "
                 "recall facts it has already lost. D compacts more often, and each compaction condenses details further."),
        scenarios=(4,), points=("5.4:K1", "5.4:S2"),
    ),
    Question(
        q=("A research coordinator runs three analysis agents over a 400-document corpus. After a crash, agents 1 and 2 had "
           "finished and agent 3 was halfway through, but the restart redid all three, which cost about 2 hours. The team "
           "wants recovery that never repeats finished work. What is the best design?"),
        opts=("Keep all three agents' full conversation histories in memory, so the coordinator can replay them after a crash.",
              "Have each agent export its state to a known location; on resume, the coordinator loads a manifest and injects it.",
              "Restart only agent 3, telling it in its prompt which documents it had processed before the crash happened.",
              "Split the corpus into many smaller batches, so that any single crash costs less work to redo when the whole run restarts."),
        ans=1,
        explain=("For crash recovery, each agent exports structured state to a known location. On resume, the coordinator loads "
                 "the manifest and injects each agent's state into its prompt. A keeps the state in memory, which the crash "
                 "wipes. C assumes the coordinator knows agent 3's progress, which it can't without an export, and still "
                 "needs agents 1 and 2's results. D reduces the loss but still repeats work."),
        scenarios=(3, 4), points=("5.4:K4", "5.4:S4"),
    ),
    Question(
        q=("A migration investigation has three phases: map dependencies, find risky call sites, then plan the changes. By "
           "phase 3, about 60% of the context is raw phase 1 search output, and the plan refers to “several modules” "
           "instead of naming them. What should the workflow do between phases?"),
        opts=("Run /clear at the start of each phase, so that every phase begins with an empty context and full attention.",
              "Keep everything in one session and ask the agent to re-read its earliest findings before it starts planning.",
              "Summarise each phase's key findings and inject that summary into the next phase's initial context.",
              "Move to a model with a larger context window for phase 3, so all the raw search output fits comfortably."),
        ans=2,
        explain=("Summarising each phase's key findings and injecting them into the next phase keeps the facts that matter "
                 "without the raw exploration. A also wipes out phase 1's results. B asks the agent to dig through the same "
                 "noise. D makes room for the noise instead of removing it."),
        scenarios=(4,), points=("5.4:S3",),
    ),
    Question(
        q=("Last night a developer ran a long refund investigation in Claude Code, then opened a quick session in the same "
           "directory to fix a typo. This morning they run claude --continue and land in the typo conversation, with none of "
           "the refund work. They assume the refund session was lost. What actually happened, and how do they get it back?"),
        opts=("--continue reopens the most recent conversation in the directory; use --resume to pick the refund session.",
              "Sessions older than 12 hours are archived; restore the refund session from the archive using /restore.",
              "The typo session overwrote the refund session's history, so it can be rebuilt only by redoing the work.",
              "--continue works only for sessions started with -p, so the refund work must be rerun under a session name."),
        ans=0,
        explain=("--continue picks the most recent conversation in the current directory, which was the typo fix. The refund "
                 "session still exists and can be chosen with --resume. B and D describe behaviour that doesn't exist, and C "
                 "assumes sessions overwrite each other, which they don't."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Is `--resume` given a name or an ID?",
     "In the Claude Code CLI, both: `claude --resume <name>` resumes a named session (an ambiguous name opens the picker), and "
     "`claude --resume <session-id>` works too. In the Agent SDK, `resume` takes a session **ID** — capture it from the result message."),
    ("Does forking copy my files too?",
     "No. The docs say forking branches the conversation, not the filesystem — edits a forked agent makes are real and visible to other "
     "sessions in the same directory. For code rollback, the docs point to checkpointing."),
    ("What's the difference between /compact and /clear?",
     "`/compact [instructions]` replaces the history with a summary (you can say what to focus on); `/clear` starts an empty context. "
     "Use `/clear` between unrelated tasks, `/compact` when a long task's context fills with discovery output."),
    ("When is ‘fresh with a summary’ better than resuming?",
     "When the earlier tool results are stale. The guide calls it more reliable than resuming with stale results. The docs make a similar "
     "point: capturing results as application state and passing them into a fresh session is often more robust than moving transcripts."),
    ("Where do the manifest and scratchpad live?",
     "Wherever your system says — the point is a known location every agent writes to and the coordinator reads on resume. The guide "
     "describes the pattern; the file names in this lab are invented."),
    ("Is the simulated agent realistic?",
     "No — it is deliberately literal: it re-reads exactly the files named, and degrades above a fixed token count. Real context "
     "degradation is gradual and less predictable; the mechanisms (restored tool results, forks, summaries) are the documented part."),
)

_Q = "What is the current auto-approve refund limit, and where is it defined?"

PLAYGROUND_INTRO = """
Ask the simulated agent about the refund code and choose **how you return to yesterday's work**: resume by name or `--continue`, tell it
what changed or not, fresh with or without a summary, fork or not, `/compact` or a scratchpad, a manifest or none. Each run shows what
happened to the sessions, the agent's answer, whether it's current and specific, and what it cost.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="session")


PLAYGROUND = (
    _tab("return", "⭐ Return by name", "return",
         "A labelled folder: reopen *that* case file — the most recent folder on the desk may be something else.", "guide:1.7:K1",
         "`claude --resume <name>` resumes the named session with its full history. `claude --continue` reopens the **most recent** "
         "conversation in the directory. Here the most recent session is an unrelated typo fix.",
         "sessions § Resume a session; guide TS 1.7 Knowledge 1, Skill 1",
         ("how",), {"how": "resume_name"}, (_Q,),
         ("By name: the analysis session, 0 file reads.",
          "--continue: the docs-typo session — it has to read all 6 files again.",
          "A brand-new session: also 6 reads — the analysis is simply not used.")),
    _tab("changes", "⭐ What changed?", "changes",
         "An erratum slip: without it, old notes are read as if still true; with too many, start a new notebook with a summary page.",
         "guide:1.7:S3",
         "A resumed session restores its old tool results. When a few files changed, resume and **name them** (targeted re-read); when "
         "most changed, start **fresh with a structured summary**. Change both knobs and compare the answer, the reads and the context size.",
         "sessions § What a resumed session restores; guide TS 1.7 Knowledge 3–4, Skills 3–4",
         ("changed", "approach"), {"changed": "one", "approach": "resume_tell"}, (_Q,),
         ("One file + resume and name it: correct (50), 1 read.",
          "One file + resume silently: stale (100).",
          "Most files + resume and name them all: 5 re-reads, ~9,300 tokens, a vague answer.",
          "Most files + fresh with summary: correct (75 in policies/refunds.py), 1 read.",
          "Fresh with no summary: correct, but 6 reads either way.")),
    _tab("fork", "⭐ fork_session", "fork",
         "A photocopy of the case file per investigator — the original stays clean for the next idea.", "guide:1.7:K2",
         "Type approach B (approach A is fixed). With forking, each approach gets its own copy of the baseline; without it, both are "
         "appended to the baseline session. The session list shows every session's prompts.",
         "sessions § Branch a session; agent-sdk/sessions § Fork to explore alternatives",
         ("fork",), {"fork": "yes"}, ("Plan approach B: move the limit into the config service.",),
         ("Fork yes: 2 new sessions; the baseline keeps 8 entries.",
          "Fork no: the baseline grows to 12 entries and B's answer says it is ALSO CARRYING approach A.")),
    _tab("degrade", "⭐ Degradation & /compact", "degrade",
         "An overfull desk: past a point you stop citing the page you read and start saying “usually it's like…” — tidy it or keep sticky notes.",
         "guide:5.4:K1",
         "As a session fills, answers degrade (the docs: more mistakes, forgotten instructions; the guide: “typical patterns” instead of "
         "specific classes). `/compact` replaces the history with a summary; a scratchpad keeps key findings to consult. The threshold here "
         "is simulated (7,000 tokens).",
         "best-practices § Manage context aggressively; sessions § Manage context; guide TS 5.4 Knowledge 1–2, Skills 2 and 5",
         ("explored", "compact", "scratchpad"), {"explored": 12, "compact": "no", "scratchpad": "no"}, (_Q,),
         ("12 files read, nothing else: ~10,000 tokens and a vague “typically…” answer.",
          "Same with /compact: ~4,500 tokens, a specific answer.",
          "Same with a scratchpad instead: still ~10,000 tokens, but the answer comes from the notes.",
          "6 files read: under the threshold, specific without any help.")),
    _tab("manifest", "⭐ Crash recovery", "manifest",
         "Each worker files a status card before leaving; after the power cut the manager reads the cards instead of redoing the project.",
         "guide:5.4:K4",
         "Before the crash, each agent exported its state to a known location. With the manifest, the coordinator reuses finished results "
         "and re-runs only the unfinished agent with its saved state in the prompt; without it, everything restarts.",
         "guide TS 5.4 Knowledge 4, Skill 4 (the docs' related advice: capture results as application state for a fresh session)",
         ("manifest",), {"manifest": "yes"}, ("Resume the codebase exploration after the crash.",),
         ("Manifest yes: 1 agent run.", "Manifest no: 3 agent runs — finished work redone.")),
)

DECISION_DOT = readable(DECISION_DOT)   # FLOWCHART RULE: 18pt, max 2 nodes per row

CONTENT = ConceptContent(
    slug="session-state",
    tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS, where_seen=WHERE_SEEN,
    guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("subagents", "subagent-state-handoff", "agentic-loops"),
    exam_points=EXAM_POINTS, playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("next_day_unchanged", "one_file_changed", "major_refactor", "compare_approaches", "crash_recovery"),
    show_ledger=False,
)
