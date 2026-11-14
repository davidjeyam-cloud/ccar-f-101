"""
D3.2 Plan Mode — when to plan (large, multi-file, several valid approaches, architectural) and when to execute directly
(simple, well-scoped), keeping verbose discovery in the Explore subagent, and planning first then executing. Guide TS 3.4
(p.14).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); Claude Code docs fetched 2026-09-28 (DOC_REFS).
Every claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Choose a permission mode — Analyze before you edit with plan mode", f"{_C}/permission-modes"),
    DocRef("Subagents — built-in Explore and Plan subagents", f"{_C}/sub-agents"),
    DocRef("Common workflows — Plan before editing", f"{_C}/common-workflows"),
)

GROUNDING = (
    Claim("Plan mode: Claude researches and proposes changes without making them — it reads files, runs shell commands to "
          "explore and writes a plan, but doesn't edit source until you approve.", "docs", "permission-modes § plan mode"),
    Claim("Enter plan mode with Shift+Tab, by prefixing a prompt with /plan, or start with claude --permission-mode plan.",
          "docs", "permission-modes § plan mode"),
    Claim("When the plan is ready you can approve and start in auto mode (or auto-accept edits), approve and review each edit "
          "manually, or keep planning; approving exits plan mode. Ctrl+G opens the plan in your editor to change it.",
          "docs", "permission-modes § Review and approve a plan"),
    Claim("Explore is a fast, read-only built-in subagent for file discovery and code search; Claude delegates to it to keep "
          "exploration results out of the main conversation's context. Thoroughness: quick, medium, very thorough.",
          "docs", "sub-agents § Built-in subagents"),
    Claim("In plan mode, Claude delegates codebase research to the read-only Plan subagent so that output stays in a separate "
          "context window.", "docs", "sub-agents § Built-in subagents (Plan)"),
    Claim("Plan mode suits complex tasks: large-scale changes, several valid approaches, architectural decisions, multi-file "
          "modifications; direct execution suits simple, well-scoped changes (adding one validation check to one function); plan "
          "mode allows safe exploration and design before committing to changes, preventing costly rework; the Explore subagent "
          "isolates verbose discovery output and returns summaries.", "guide", "TS 3.4 · Knowledge 1–4 · p.14"),
    Claim("Skills: plan mode for architectural tasks (microservice restructuring, a library migration touching 45+ files, choosing "
          "between integration approaches with different infrastructure); direct execution for clear-scope changes (a single-file "
          "bug fix with a clear stack trace, a date-validation conditional); Explore for verbose discovery to avoid context "
          "exhaustion; plan for investigation then execute directly.", "guide", "TS 3.4 · Skills 1–4 · p.14"),
    Claim("The minutes, token counts, context window and the 'first approach turns out wrong' behaviour are invented to make the "
          "trade-offs visible.", "simulated", "utils/plan_lab.py"),
)

CORRECT = r'''from utils.plan_lab import run_session   # SIMULATED Claude Code session


def choose_mode(task):
    """Plan when the task is big, has several valid approaches, or is architectural; otherwise just do it."""
    needs_design = task["files"] > 3 or task["approaches"] > 1 or task["architectural"]
    return "plan" if needs_design else "direct"


def use_explore(task):
    """Verbose discovery goes to the Explore subagent - only its summary enters the main context."""
    return task["discovery_files"] > 50


def after_approval(task):
    """Plan for investigation, then EXECUTE: approving the plan switches to an editing mode."""
    return "acceptEdits"


run_session(choose_mode, use_explore, after_approval)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


_CHOOSE = '''    needs_design = task["files"] > 3 or task["approaches"] > 1 or task["architectural"]
    return "plan" if needs_design else "direct"'''
# ⭐ TS 3.4 · Skill 1 — direct execution for an architectural, multi-approach task
VARIANT_A = _swap(CORRECT, _CHOOSE, '''    return "direct"   # WRONG: never plans''')
# ⭐ TS 3.4 · Skill 2 / Knowledge 2 — plan mode for a one-line, clear-scope fix
VARIANT_B = _swap(CORRECT, _CHOOSE, '''    return "plan"   # WRONG: plans everything, even a one-line fix''')
# ⭐ TS 3.4 · Skill 3 / Knowledge 4 — verbose discovery in the main conversation
VARIANT_C = _swap(CORRECT, '''    return task["discovery_files"] > 50''', '''    return False   # WRONG: all discovery output lands in the main context''')
# ⭐ TS 3.4 · Skill 4 — the plan is approved but never executed
VARIANT_D = _swap(CORRECT, '''    return "acceptEdits"''', '''    return "keep_planning"   # WRONG: never leaves plan mode''')
# ⭐ TS 3.4 · Knowledge 1 — deciding by file count alone
VARIANT_E = _swap(CORRECT, _CHOOSE, '''    return "plan" if task["files"] > 10 else "direct"   # WRONG: only size counts''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "plan_session"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


_RIGHT_MODE = {"library_migration": "plan", "single_bug": "direct", "choose_integration": "plan", "big_discovery": "plan"}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "run_session() was never called"
    txt = (f"mode: {r['mode']} · Explore: {'yes' if r['explore'] else 'no'} · {r['minutes']} min · reworked files: "
           f"{r['rework_files']} · main context {r['context']:,} · {'DONE' if r['done'] else 'NOT DONE'}")
    if r["exhausted"]:
        return False, "NOEXPLORE", txt
    if not r["done"]:
        return False, "NEVEREXEC", txt
    if r["mode"] == "direct" and _RIGHT_MODE[sc] == "plan":
        return False, "DIRECT", txt
    if r["mode"] == "plan" and _RIGHT_MODE[sc] == "direct":
        return False, "OVERPLAN", txt
    return True, None, txt


EXPECTED = {
    "library_migration": "plan first (45 files, 2 approaches), then execute — no rework",
    "single_bug": "direct execution — a one-file fix with a clear stack trace needs no plan",
    "choose_integration": "plan first — only 2 files, but two approaches with different infrastructure",
    "big_discovery": "300 files of discovery go to Explore; the main context stays under the window and the task finishes",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":    ("#EDE9FE", "#7C3AED", "the decision"),
    "plan": ("#DBEAFE", "#0066CC", "plan mode"),
    "dir":  ("#D1FAE5", "#059669", "direct execution"),
    "exp":  ("#CCFBF1", "#0D9488", "Explore subagent"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "Q":     ("Large, several valid approaches,\\narchitectural or multi-file?", "diamond", "q"),
    "PLAN":  ("⭐ Plan mode: explore read-only,\\ncompare approaches, write a plan", "box", "plan"),
    "DIRECT": ("⭐ Direct execution\\n(clear, small scope)", "box", "dir"),
    "EXPL":  ("⭐ Verbose discovery →\\nExplore subagent (summary back)", "box", "exp"),
    "APPROVE": ("Approve the plan", "diamond", "plan"),
    "EXEC":  ("⭐ Execute the planned approach\\n(plan → direct)", "box", "dir"),
    "DONE":  ("Done without rework", "box", "q"),
    "DIRECTBUG": ("✗ direct on an\\narchitectural task", "box", "bug"),
    "OVERPLAN":  ("✗ plan mode for a\\none-line fix", "box", "bug"),
    "NOEXPLORE": ("✗ discovery floods the\\nmain context", "box", "bug"),
    "NEVEREXEC": ("✗ plan approved,\\nnever executed", "box", "bug"),
}
_BUGS = ["DIRECTBUG", "OVERPLAN", "NOEXPLORE", "NEVEREXEC"]
_BUGMAP = {"DIRECT": "DIRECTBUG"}
_EXP = {"library_migration": ["PLAN", "APPROVE", "EXEC", "DONE"], "single_bug": ["DIRECT", "DONE"],
        "choose_integration": ["PLAN", "APPROVE", "EXEC", "DONE"], "big_discovery": ["EXPL", "PLAN", "APPROVE", "EXEC", "DONE"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 3.4 p.14)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = the right path · '
                 '<B>red</B> = the bug your run shows</FONT></TD></TR>')
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
    lines += ["  EXPL -> Q [label=\"lots to discover first\", style=dashed];",
              '  Q -> PLAN [label="yes"]; Q -> DIRECT [label="no"]; { rank=same; PLAN; DIRECT; }',
              "  PLAN -> APPROVE; APPROVE -> EXEC [label=\"approve\"]; APPROVE -> PLAN [label=\"keep planning\", style=dashed];",
              "  EXEC -> DONE; DIRECT -> DONE;",
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  DONE -> DIRECTBUG [style=invis];", _key(hl),
              f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"Q": ("ok", "")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this task needs")
    if bug:
        s[_BUGMAP.get(bug, bug)] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("3.4", "K", 1, "Plan mode fits complex tasks: large-scale changes, several valid approaches, architectural decisions, multi-file changes.",
              "✅ library_migration, choose_integration · ❌ A · ❌ E"),
    ExamPoint("3.4", "K", 2, "Direct execution fits simple, well-scoped changes (one validation check in one function).", "✅ single_bug · ❌ B"),
    ExamPoint("3.4", "K", 3, "Plan mode allows safe exploration and design before committing to changes, preventing costly rework.",
              "❌ A (rework) · playground “Plan or direct?”"),
    ExamPoint("3.4", "K", 4, "The Explore subagent isolates verbose discovery output and returns summaries, preserving the main context.",
              "✅ big_discovery · ❌ C"),
    ExamPoint("3.4", "S", 1, "Choose plan mode for architectural tasks (microservice restructuring, a 45+-file library migration, choosing between integrations with different infrastructure).",
              "✅ library_migration, choose_integration"),
    ExamPoint("3.4", "S", 2, "Choose direct execution for well-understood changes (a single-file bug with a clear stack trace, a date-validation conditional).",
              "✅ single_bug · ❌ B"),
    ExamPoint("3.4", "S", 3, "Use the Explore subagent for verbose discovery phases to avoid exhausting the context window.", "✅ big_discovery · ❌ C"),
    ExamPoint("3.4", "S", 4, "Combine plan mode for investigation with direct execution for implementation.", "✅ after_approval · ❌ D"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ plan when design is needed · direct when it's clear · Explore for big discovery · plan → execute", "correct", CORRECT, "library_migration",
            observe=("library_migration: plan mode compares the 2 approaches, the plan is approved (→ acceptEdits) and executed across "
                     "45 files — 55 simulated min, 0 reworked. single_bug: direct — 3 min. choose_integration: only 2 files, but 2 "
                     "approaches → plan, 11 min, no rework. big_discovery: Explore reads 300 files in its own context and returns a "
                     "2,500-token summary; the main context stays at 22,500."),
            why="The mode follows the task's shape. The context stays for the work, and the plan turns into edits once approved."),
    Variant("A", "⭐❌ A — always direct execution", "distractor", VARIANT_A, "library_migration",
            observe=("library_migration: started on the first approach; after 30 files it turned out wrong → 30 files reverted, 107 min "
                     "instead of 55. choose_integration: 1 file of rework."),
            why="Tasks with several valid approaches or architectural choices need the design done before edits start — that's what plan mode prevents.",
            fix="Plan mode for large, multi-approach, architectural work.", source="guide:3.4:S1"),
    Variant("B", "⭐❌ B — plan mode for everything", "distractor", VARIANT_B, "single_bug",
            observe="The one-line null-check fix takes 10 simulated min through plan → approve → execute, instead of 3 min direct.",
            why="Direct execution fits simple, well-scoped changes such as a single-file bug with a clear stack trace.",
            fix="Direct execution for clear, small changes.", source="guide:3.4:S2"),
    Variant("C", "⭐❌ C — verbose discovery in the main conversation", "distractor", VARIANT_C, "big_discovery",
            observe="300 files of discovery add 270,000 tokens: main context 290,000 > the 200,000 window → exhausted, NOT DONE.",
            why="The Explore subagent does verbose discovery in its own context and returns only a summary.",
            fix="Send discovery to Explore.", source="guide:3.4:S3"),
    Variant("D", "⭐❌ D — the plan is never executed", "distractor", VARIANT_D, "library_migration",
            observe="At the approval prompt the policy chooses “keep planning”: edits stay blocked, nothing changes — NOT DONE.",
            why="Plan for investigation, then execute: approving switches to an editing mode.",
            fix="Approve and execute (auto / accept edits / manual approval).", source="guide:3.4:S4"),
    Variant("E", "⭐❌ E — decide by file count alone", "distractor", VARIANT_E, "choose_integration",
            observe="Only 2 files, so it goes direct — the first integration approach turns out wrong for the infrastructure; 1 file of rework.",
            why="The guide's triggers include several valid approaches and architectural decisions, not just size.",
            fix="Plan when there are several approaches or architectural choices, whatever the size.", source="guide:3.4:K1"),
)

TLDR = (
    "**Plan mode** is for tasks that need design: large or multi-file changes, **several valid approaches**, architectural "
    "choices (a 45-file library migration; hosted vs embedded payments). **Direct execution** is for small, clear changes "
    "(a one-file fix with a stack trace; adding one date check).\n\n"
    "- **Explore:** send verbose discovery to the Explore subagent, so only a summary enters your context.\n"
    "- **Then execute:** plan to investigate, then approve and execute.\n"
    "- **Docs:** in plan mode Claude reads and proposes but **doesn't edit** until you approve. Enter it with `Shift+Tab`, "
    "`/plan` or `--permission-mode plan`."
)
MENTAL_MODEL = ("Plan mode is the architect's drawing before the builders arrive. You don't draw plans to change a light bulb "
                "(direct execution), but you do before moving a wall. The Explore subagent is the surveyor who walks the whole "
                "site and hands you one page. Once the drawing is approved, somebody still has to build it.")

WHAT_IT_IS = """
The exam guide covers when to use plan mode vs direct execution (Guide §6 · TS 3.4, p.14). The Claude Code docs define plan
mode's behaviour and the built-in Explore and Plan subagents.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Plan mode | The architect's drawing before the builders arrive. | ⭐ TS 3.4 · Knowledge 1, 3 |
| 2 | Direct execution | Changing a light bulb — no drawing needed. | ⭐ TS 3.4 · Knowledge 2, Skill 2 |
| 3 | Several valid approaches | Two floor plans that both fit — choose before you pour concrete. | ⭐ TS 3.4 · Knowledge 1, Skill 1 |
| 4 | Explore subagent | The surveyor who walks the whole site and hands you one page. | ⭐ TS 3.4 · Knowledge 4, Skill 3 |
| 5 | Plan, then execute | An approved drawing still needs builders. | ⭐ TS 3.4 · Skill 4 |
| 6 | Approval options | Approve and build automatically, approve and check each brick, or send the drawing back. | 📘 docs |
| 7 | Plan subagent | Plan mode's own researcher, working in a separate room. | 📘 docs |

**Plan mode vs direct execution** (the comparison CLAUDE.md requires)

| # | Aspect | Plan mode | Direct execution |
|---|---|---|---|
| 1 | Edits | Blocked until you approve the plan | Made as Claude goes |
| 2 | What Claude does first | Reads, explores, compares approaches, writes a plan | Makes the change |
| 3 | Best for | ⭐ Large, multi-file, several approaches, architectural | ⭐ Small, clear scope |
| 4 | Guide examples | Microservice restructuring; a library migration touching 45+ files; hosted vs embedded integration | A single-file bug with a clear stack trace; a date-validation conditional |
| 5 | Risk it prevents | Costly rework after the wrong approach | Overhead on trivial changes |
| 6 | How to enter | `Shift+Tab`, `/plan <prompt>`, `claude --permission-mode plan` | The default flow |
| 7 | After | Approve → auto / accept edits / manual approval; or keep planning | — |

**Built-in subagents for discovery** (docs)

| # | Subagent | Tools | Used for |
|---|---|---|---|
| 1 | ⭐ Explore | Read-only (Write and Edit denied) | File discovery and code search; keeps results out of the main context; thoroughness quick / medium / very thorough |
| 2 | Plan | Read-only | Research while in plan mode, in a separate context |
| 3 | general-purpose | All tools available to subagents | Tasks that need exploration **and** changes |
"""

HOW_IT_WORKS = """
1. **Size up the task.** Is it large or multi-file? Are there several valid approaches, or architectural choices? If yes →
   plan mode. If it's small and clear → direct.
2. **Lots to discover first?** Send it to the **Explore** subagent. Only its summary comes back to your context.
3. **In plan mode** Claude reads, compares approaches and writes a plan — without editing. Adjust it, or open it with `Ctrl+G`.
4. **Approve and execute:** pick auto mode, accept edits, or manual approval. "Keep planning" stays read-only.
"""

WHERE_SEEN = """
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): library migrations, bug fixes, refactors.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): exploring unfamiliar codebases without flooding context.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 3.4 (p.14) and the Claude Code docs (verified 2026-09-28 — pages listed above). "
              "Section layout inspired by a community concept list (claudearchitectcertification.com — community source, "
              "unverified; no text copied).")

LAB_INTRO = """
You write the policy a developer follows in Claude Code:

- `choose_mode(task)` — plan or direct.
- `use_explore(task)` — whether discovery goes to the Explore subagent.
- `after_approval(task)` — what to pick at the plan-approval prompt.

The **simulated** session runs tasks taken from the guide's own examples and reports the simulated time, the files that had to
be reworked, and how full the main context got (window: 200,000 simulated tokens).
"""

DISTRACTORS = (
    ("A · Always direct", "It's faster to just start.", "30 files of rework on the migration.", "Plan for multi-approach, architectural work.", "guide:3.4:S1"),
    ("B · Always plan", "Planning is always safer.", "A one-line fix takes 3× as long.", "Direct for small, clear changes.", "guide:3.4:S2"),
    ("C · Discovery in the main conversation", "Claude should see everything.", "290k tokens → context exhausted.", "Explore subagent.", "guide:3.4:S3"),
    ("D · Keep planning forever", "The plan was the hard part.", "Nothing is ever changed.", "Approve and execute.", "guide:3.4:S4"),
    ("E · Decide by file count", "Only big changes need a plan.", "2 files, 2 approaches → rework.", "Plan for several approaches too.", "guide:3.4:K1"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Task (guide examples)", "Mode", "Why")
SIDE_BY_SIDE_ROWS = (
    ("1", "Restructure a monolith into microservices", "Plan", "Architectural"),
    ("2", "Library migration touching 45+ files", "Plan → execute", "Large, multi-file, approach to choose"),
    ("3", "Choose between two integrations with different infrastructure", "Plan", "Several valid approaches"),
    ("4", "Single-file bug with a clear stack trace", "Direct", "Clear, small scope"),
    ("5", "Add a date-validation conditional", "Direct", "Well understood"),
    ("6", "Discovery across hundreds of files", "Explore subagent (then plan)", "Keeps the main context free"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q0 [shape=diamond, label="Lots to discover first?"];
  EXP [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Explore subagent\\n(summary back)"];
  Q1 [shape=diamond, label="Large / multi-file / several\\napproaches / architectural?"];
  PLAN [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Plan mode"];
  DIRECT [shape=box, fillcolor="#D1FAE5", color="#059669", label="Direct execution"];
  EXEC [shape=box, fillcolor="#D1FAE5", color="#059669", label="Approve → execute"];
  Q0 -> EXP [label="yes"]; EXP -> Q1; Q0 -> Q1 [label="no"]; Q1 -> PLAN [label="yes"]; Q1 -> DIRECT [label="no"]; PLAN -> EXEC;
}''')

EXPERIMENTS = (
    "Run ✅ on all four scenarios and compare the simulated minutes and reworked files.",
    "In ✅, lower the threshold to files > 50 and run library_migration — what happens?",
    "Run ⭐❌ C on big_discovery and find the line where the context overflows.",
    "In the playground's “Plan or direct?” tab, type your own task (e.g. “two ways to add caching: Redis vs in-memory”) and try both modes.",
)

QUESTIONS = (
    Question(
        q=("A developer asks Claude Code to move a service from one ORM to another. About 60 files are affected, and there "
           "are two reasonable approaches: an incremental adapter layer or a one-shot rewrite. The developer has one sprint "
           "and cannot afford to redo the work. How should they start?"),
        opts=("Ask Claude to implement both approaches on separate branches, then keep whichever passes more tests.",
              "Plan mode: explore the codebase, compare both approaches and agree a plan before any file changes.",
              "Direct execution, but ask Claude to explain each change in detail before it makes that change.",
              "Direct execution with a git commit after every file, so any wrong turn can be undone cheaply."),
        ans=1,
        explain=("A large change with several valid approaches and architectural consequences is what plan mode is for: explore, "
                 "compare, decide, then edit. A builds the migration twice. C and D make edits before the approach has been "
                 "chosen. Explaining or committing each step doesn't make the choice any better."),
        scenarios=(2,), points=("3.4:K1", "3.4:S1", "3.4:K3"),
    ),
    Question(
        q=("A stack trace points to a missing null check on one line of one function, and the fix is obvious. The team's new "
           "guideline says “use plan mode for all production changes”, and the developer is about to spend 10 minutes "
           "producing a plan for it. Which approach fits best?"),
        opts=("Plan mode, as the guideline says, since every production change needs an explored and approved plan.",
              "Plan mode, but only to search the codebase for other null checks that might be missing elsewhere.",
              "Delegate the fix to an Explore subagent, so that the main session stays clear for other work.",
              "Direct execution: make the one-line change and run the tests."),
        ans=3,
        explain=("A well-understood, single-location change with a clear scope suits direct execution. A spends planning effort "
                 "on a decision that has already been made. B widens the task. C: Explore is a read-only discovery helper, "
                 "not a way to make edits."),
        scenarios=(2,), points=("3.4:K2", "3.4:S2"),
    ),
    Question(
        q=("During a multi-phase task, the main session's context fills with search output from about 400 files before any "
           "design work starts. By the design phase, Claude's reasoning refers to “the relevant modules” instead of naming "
           "them. What should change?"),
        opts=("Run /clear after discovery, then ask Claude to design from what it remembers about the modules.",
              "Ask Claude to read fewer files during discovery, so that the context has room for the design work.",
              "Run discovery in the Explore subagent, which returns a summary and keeps verbose output out.",
              "Switch to a model with a larger context window, so the discovery output and the design both fit."),
        ans=2,
        explain=("The Explore subagent isolates verbose discovery output and returns a summary, so the main context keeps room "
                 "for design. A leaves nothing to design from. B trades completeness for space. D makes room for the noise "
                 "instead of removing it."),
        scenarios=(2, 4), points=("3.4:K4", "3.4:S3"),
    ),
    Question(
        q=("A team must add payments using either a hosted checkout page or an embedded card form. Each option needs "
           "different infrastructure, compliance work and front-end changes, and the team has three days to choose. A "
           "developer proposes letting Claude implement the embedded form directly, since “we can always switch later”. How "
           "should you evaluate this?"),
        opts=("Use plan mode instead, to investigate both options against the codebase and decide before implementing.",
              "Reasonable, because direct execution will expose the real constraints faster than any analysis could.",
              "Reasonable, as long as the developer gives Claude very detailed instructions describing the embedded form.",
              "Ask Claude for a generic pros-and-cons list of both options without looking at the codebase at all."),
        ans=0,
        explain=("Two approaches with different infrastructure and compliance consequences call for plan mode's investigation "
                 "before any commitment. B commits first and learns late. C assumes the answer is already known. D compares "
                 "the options without the codebase that decides between them."),
        scenarios=(2,), points=("3.4:S1",),
    ),
    Question(
        q=("A team used plan mode to design a 45-file library migration and approved the plan. They are now reviewing every "
           "small, mechanical edit in plan mode as well, and after two days only 9 files are done. What is the better "
           "workflow?"),
        opts=("Re-plan the migration in smaller chunks, so that each plan-mode review covers fewer files at a time.",
              "Hand each remaining file to a separate subagent in plan mode, so that the reviews happen in parallel.",
              "Keep the approved plan, and switch to direct execution to implement its well-defined steps.",
              "Abandon the plan and let Claude convert all of the remaining files in one pass without it."),
        ans=2,
        explain=("Plan for the uncertain part, then execute directly once the steps are clear. A and B keep paying for planning "
                 "that was already done. D throws away the agreed design."),
        scenarios=(2,), points=("3.4:S4", "3.4:K3"),
    ),
    Question(
        q=("A developer puts Claude Code into plan mode and asks it to rename a function across 30 files. Claude describes "
           "the change in detail, but no file is modified. The developer files a bug report saying “Edit is broken in plan "
           "mode”. What actually happened?"),
        opts=("The rename touched too many files, so Claude Code refused it until the edit limit is raised.",
              "Edits made in plan mode go to a staging area and need a separate command to apply them to disk.",
              "Plan mode supports renames only through the IDE, so the edit has to be made from the editor instead.",
              "Plan mode is read-only: Claude researches and proposes, and edits happen only after approval."),
        ans=3,
        explain=("Plan mode is for research and proposals. Files change only after you approve the plan and leave plan mode. "
                 "A, B and C describe limits and mechanisms that don't exist."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("How do I get into plan mode?",
     "Press Shift+Tab until the indicator shows plan mode, prefix a single prompt with /plan, or start with claude "
     "--permission-mode plan. Shift+Tab again leaves plan mode without approving."),
    ("What are the approval choices?",
     "Approve and use auto mode (or auto-accept edits), approve and review each edit manually, or keep planning. You can also "
     "edit the plan in your editor with Ctrl+G first."),
    ("Explore or Plan subagent?",
     "Both are read-only built-ins. Claude delegates discovery to Explore to keep search results out of the main context. In "
     "plan mode it uses the Plan subagent for the same kind of research. The guide names Explore."),
    ("Is plan mode ever wrong?",
     "Not wrong, but wasteful for small, clear changes. The guide expects direct execution for a single-file fix with a clear "
     "stack trace."),
)

PLAYGROUND_INTRO = """
Pick a task (or type your own — the engine reads simple cues such as a file count, “two ways” or “vs”, “migration” or
“architecture”, and “stack trace”) and a mode, then compare the simulated time, rework and context.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="plan")


PLAYGROUND = (
    _tab("decide", "⭐ Plan or direct?", "decide", "Draw plans before moving a wall, not to change a bulb.", "guide:3.4:K1",
         "Run a task in plan mode or directly.", "permission-modes § plan mode; guide TS 3.4",
         ("task_pick", "mode_pick"), {"task_pick": "library_migration", "mode_pick": "plan"},
         ("use the task selected below", "Two ways to add caching: Redis vs in-memory", "Fix the crash in cart.py, stack trace points to line 12", "Rename a field in 30 files"),
         ("migration direct: 30 files of rework.", "one-line bug in plan mode: 10 min instead of 3.", "“Two ways … vs …” direct: rework.")),
    _tab("explore", "⭐ Explore subagent", "explore", "The surveyor hands you one page.", "guide:3.4:S3",
         "Discovery across many files, with or without the Explore subagent.", "sub-agents § Built-in subagents",
         ("discovery", "use_explore"), {"discovery": "300", "use_explore": "yes"}, ("Find every place the old auth token is read, then replace it",),
         ("300 files without Explore: context exhausted.", "50 files without Explore: fits.", "300 with Explore: 22,500 tokens.")),
    _tab("approve", "⭐ Plan, then execute", "approve", "An approved drawing still needs builders.", "guide:3.4:S4",
         "What you pick at the approval prompt.", "permission-modes § Review and approve a plan",
         ("approval",), {"approval": "acceptEdits"}, ("Migrate from the old HTTP library to the new one",), ("keep planning: nothing changes.", "any approve option: done.")),
)

CONTENT = ConceptContent(
    slug="plan-mode", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("subagents", "task-decomposition", "checkpoints"), exam_points=EXAM_POINTS, playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO, scenarios=("library_migration", "single_bug", "choose_integration", "big_discovery"),
    show_ledger=False,
)
