"""
D1.8 Task Decomposition Strategies — guide TS 1.6 (prompt chaining vs dynamic adaptive decomposition; per-file + cross-file
passes; map → prioritise → adapt; p.8).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-27); official docs fetched 2026-09-27 (DOC_REFS). Every
claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable
from utils.decomp_lab import expected_issues

DOCS_VERIFIED_ON = "2026-09-27"
_C = "https://code.claude.com/docs/en"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (
    DocRef("Prompting best practices — chain complex prompts, subagent orchestration, state tracking",
           f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices"),
    DocRef("Best practices for Claude Code — explore, plan, code; context; fan out", f"{_C}/best-practices"),
    DocRef("Common workflows — understand codebases, work with tests", f"{_C}/common-workflows"),
)

GROUNDING = (
    Claim("Explicit prompt chaining (a task broken into sequential calls) is useful when you need to inspect intermediate outputs "
          "or enforce a specific pipeline structure; each step is a separate call you can log, evaluate or branch on.",
          "docs", "claude-prompting-best-practices § Chain complex prompts"),
    Claim("Use subagents for parallel, isolated, independent workstreams; work directly for simple or sequential tasks.",
          "docs", "claude-prompting-best-practices § Subagent orchestration"),
    Claim("For long tasks: set up a framework first, keep a todo list, track state in structured files and make incremental progress.",
          "docs", "claude-prompting-best-practices § Long-horizon reasoning and state tracking"),
    Claim("LLM performance degrades as the context fills; scope investigations narrowly and explore → plan → implement.",
          "docs", "code.claude.com best-practices (introduction; Explore first; Avoid common failure patterns)"),
    Claim("For large migrations or analyses, distribute work across many parallel invocations (fan out across files).",
          "docs", "code.claude.com best-practices § Fan out across files"),
    Claim("Codebase exploration recipes start broad, then narrow down; test work starts by finding untested code.",
          "docs", "common-workflows § Understand new codebases; Work with tests"),
    Claim("Fixed sequential pipelines (prompt chaining) vs dynamic adaptive decomposition based on intermediate findings.",
          "guide", "TS 1.6 · Knowledge 1 · p.8"),
    Claim("Prompt chaining breaks reviews into sequential steps — each file analysed on its own, then a cross-file integration pass.",
          "guide", "TS 1.6 · Knowledge 2 · p.8"),
    Claim("Adaptive investigation plans generate subtasks from what each step discovers.", "guide", "TS 1.6 · Knowledge 3 · p.8"),
    Claim("Select the pattern: chaining for predictable multi-aspect reviews, dynamic decomposition for open-ended investigations.",
          "guide", "TS 1.6 · Skill 1 · p.8"),
    Claim("Split large reviews into per-file local passes plus a separate cross-file integration pass to avoid attention dilution.",
          "guide", "TS 1.6 · Skill 2 · p.8"),
    Claim("Decompose open-ended tasks (e.g. adding tests to a legacy codebase) by mapping structure, identifying high-impact areas, "
          "then making a prioritised plan that adapts as dependencies are discovered.", "guide", "TS 1.6 · Skill 3 · p.8"),
    Claim("The files, planted bugs, the 3-files-per-pass attention limit, module risks, the FakeClock dependency and the 6-action "
          "budget are invented to make dilution and adaptation visible.", "simulated", "utils/decomp_lab.py"),
)

CORRECT = r'''from utils.decomp_lab import (FILES, TASK, create_helper, integration_pass, map_structure, review_file, review_files,
                              submit, write_tests)   # SIMULATED reviewer / codebase

if TASK == "review":
    # A review is PREDICTABLE: the same steps every time -> a fixed chain (prompt chaining)
    if len(FILES) <= 3:
        issues = review_files(FILES, "Review these files for bugs, including cross-file mismatches.").issues
    else:
        per_file = [review_file(path) for path in FILES]           # step 1: local analysis, one file per pass
        issues = [i for r in per_file for i in r.issues]
        issues += integration_pass([r.summary for r in per_file])   # step 2: a separate cross-file integration pass
    for i in issues:
        print("ISSUE:", i)
    submit(issues)

else:
    # "Add tests to a legacy codebase" is OPEN-ENDED -> decompose dynamically
    modules = map_structure()                                                        # 1. map the structure first
    plan = [m["name"] for m in sorted(modules, key=lambda m: m["risk"] != "high")]   # 2. high-impact areas first
    tested = []
    while plan:
        name = plan.pop(0)
        result = write_tests(name)
        print(f"{name}: {result}")
        if result.startswith("OUT OF BUDGET"):
            break
        if result.startswith("BLOCKED"):                    # 3. adapt: a discovered dependency becomes a new subtask
            helper = result.split("need a ")[1].split(" helper")[0]
            print("   ", create_helper(helper))
            plan.insert(0, name)                            #    ...and the blocked module is retried next
            continue
        tested.append(name)
    submit(tested)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


_CHAIN = '''        per_file = [review_file(path) for path in FILES]           # step 1: local analysis, one file per pass
        issues = [i for r in per_file for i in r.issues]
        issues += integration_pass([r.summary for r in per_file])   # step 2: a separate cross-file integration pass'''
VARIANT_A = _swap(CORRECT, _CHAIN, '''        # WRONG: one pass over every file at once
        issues = review_files(FILES, "Review all of these files for bugs, including cross-file mismatches.").issues''')
VARIANT_B = _swap(CORRECT, _CHAIN, '''        per_file = [review_file(path) for path in FILES]           # step 1: local analysis, one file per pass
        issues = [i for r in per_file for i in r.issues]           # WRONG: no cross-file integration pass''')
VARIANT_C = _swap(CORRECT, '''    modules = map_structure()                                                        # 1. map the structure first
    plan = [m["name"] for m in sorted(modules, key=lambda m: m["risk"] != "high")]   # 2. high-impact areas first''',
                  '''    # WRONG: a fixed plan decided up front - every module in alphabetical order, no mapping
    from utils.decomp_lab import MODULE_NAMES
    plan = list(MODULE_NAMES)''')
VARIANT_C = _swap(VARIANT_C, '''        if result.startswith("BLOCKED"):                    # 3. adapt: a discovered dependency becomes a new subtask
            helper = result.split("need a ")[1].split(" helper")[0]
            print("   ", create_helper(helper))
            plan.insert(0, name)                            #    ...and the blocked module is retried next
            continue''', '''        if result.startswith("BLOCKED"):                    # the plan was fixed: skip and move on
            continue''')
VARIANT_D = _swap(CORRECT, '''        if result.startswith("BLOCKED"):                    # 3. adapt: a discovered dependency becomes a new subtask
            helper = result.split("need a ")[1].split(" helper")[0]
            print("   ", create_helper(helper))
            plan.insert(0, name)                            #    ...and the blocked module is retried next
            continue''', '''        if result.startswith("BLOCKED"):                    # WRONG: the plan never changes - skip it and carry on
            continue''')
VARIANT_E = _swap(CORRECT, _CHAIN, '''        # WRONG: an adaptive "review what looks important" plan for a predictable review
        picked = [p for p in FILES if any(w in p for w in ("pay", "pric", "order", "auth", "currency"))]
        per_file = [review_file(path) for path in picked]
        issues = [i for r in per_file for i in r.issues]
        issues += integration_pass([r.summary for r in per_file])''')

_HIGH = {"auth", "orders", "payments"}


def _facts(trace):
    ev = trace["events"]
    passes = [e for e in ev if e["kind"] == "review_pass"]
    steps = [e for e in ev if e["kind"] == "plan_step"]
    sub = next((e for e in reversed(ev) if e["kind"] == "submit"), None)
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "passes": passes, "steps": steps, "sub": sub}


def _diagnose(f):
    sc = f["scenario"]
    if f["sub"] is None:
        return False, None, f"nothing submitted ({f['raised'] or 'no result'})"
    if sc in ("large_review", "small_review"):
        from utils import decomp_lab as dl
        dl.configure(sc)
        want = expected_issues()
        got = set(f["sub"]["items"])
        missed = want - got
        multi = [p for p in f["passes"] if p["type"] == "multi"]
        integ = any(p["type"] == "integration" for p in f["passes"])
        examined = {x for p in f["passes"] for x in p["examined"]}
        txt = (f"found {len(want & got)}/{len(want)} planted issues · review passes: {len(f['passes'])} · "
               f"integration pass: {integ} · files examined: {len(examined)}/{len(dl.FILES)}"
               + (f" · missed: {sorted(missed)}" if missed else ""))
        if not missed:
            return True, None, txt
        if multi and len(multi[0]["files"]) > 3:
            return False, "ONEPASS", txt
        if len(examined) < len(dl.FILES):
            return False, "PICKY", txt
        return False, "NOINTEG", txt
    tested = set(f["sub"]["tested"])
    mapped = any(s["action"] == "map_structure" for s in f["steps"])
    helper = any(s["action"].startswith("create_helper") for s in f["steps"])
    blocked = any((s.get("result") or "").startswith("BLOCKED") for s in f["steps"])
    txt = (f"high-impact modules tested: {sorted(tested & _HIGH)} of {sorted(_HIGH)} · all tested: {sorted(tested)} · "
           f"mapped first: {mapped} · hit a hidden dependency: {blocked} · created a helper: {helper} · actions used: {f['sub']['used']}/6")
    if _HIGH <= tested:
        return True, None, txt
    return False, ("FIXEDPLAN" if not mapped else "NOADAPT"), txt


EXPECTED = {"large_review": "all 4 planted issues found (3 local + the cross-file mismatch)",
            "small_review": "both planted issues found (1 local + the cross-file mismatch)",
            "legacy_tests": "tests for all three high-impact modules (auth, orders, payments) within the 6-action budget"}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok and not trace["status"]["raised"], EXPECTED[scenario], txt


# ── Chart (top-down) ───────────────────────────────────────────────────────────

_CONCEPT = {
    "pick":   ("#EDE9FE", "#7C3AED", "choosing the pattern"),
    "chain":  ("#DBEAFE", "#0066CC", "prompt chaining (fixed steps)"),
    "dyn":    ("#FEF3C7", "#D97706", "dynamic decomposition (adapts)"),
    "done":   ("#D1FAE5", "#059669", "result"),
    "bug":    ("#FFFFFF", "#DC2626", "bug (an exam distractor)"),
}
_NODES = {
    "TASK":   ("A complex task", "box", "pick"),
    "Q":      ("⭐ Are the steps known\\nin advance?", "diamond", "pick"),
    "LOCAL":  ("⭐ Per-file passes\\n(local analysis, one file each)", "box", "chain"),
    "INTEG":  ("⭐ Cross-file integration pass\\n(over the per-file summaries)", "box", "chain"),
    "MAP":    ("⭐ Map the structure", "box", "dyn"),
    "PRIO":   ("⭐ Prioritise high-impact areas", "box", "dyn"),
    "DO":     ("Work the next subtask", "box", "dyn"),
    "ADAPT":  ("⭐ Discovered a dependency?\\n→ add a subtask, retry", "box", "dyn"),
    "DONE":   ("Complete result", "box", "done"),
    "ONEPASS": ("✗ one pass over\\nevery file", "box", "bug"),
    "NOINTEG": ("✗ no integration pass", "box", "bug"),
    "PICKY":  ("✗ adaptive plan for a\\npredictable review", "box", "bug"),
    "FIXEDPLAN": ("✗ fixed plan for an\\nopen-ended task", "box", "bug"),
    "NOADAPT": ("✗ plan never adapts", "box", "bug"),
}
_BUGS = ["ONEPASS", "NOINTEG", "PICKY", "FIXEDPLAN", "NOADAPT"]
_EXP = {"large_review": ["LOCAL", "INTEG"], "small_review": [], "legacy_tests": ["MAP", "PRIO", "DO", "ADAPT"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 1.6, p.8)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = the path that fits · '
                 '<B>red</B> = the bug your run shows · grey = not this scenario</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3"><TR><TD COLSPAN="2" '
            'BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states):
    hl = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.45; newrank=true;',
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
    lines += ['  TASK -> Q;', '  Q -> LOCAL [label="yes: predictable review"]; LOCAL -> INTEG; INTEG -> DONE;',
              '  Q -> MAP [label="no: open-ended"]; MAP -> PRIO; PRIO -> DO; DO -> ADAPT; ADAPT -> DO [label="new subtask", constraint=false];',
              '  ADAPT -> DONE;', "  { rank=same; LOCAL; MAP; }", "  { rank=same; " + "; ".join(_BUGS) + "; }",
              "  DONE -> ONEPASS [style=invis];", _key(hl), "  NOINTEG -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"TASK": ("ok", ""), "Q": ("ok", "")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "the path that fits")
    s["DONE"] = ("ok", "") if ok else ("bad", "incomplete")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("1.6", "K", 1, "When to use a fixed sequential pipeline (prompt chaining) versus dynamic decomposition that adapts to "
              "intermediate findings.", "✅ the TASK branch · flowchart · playground “Pick the pattern”"),
    ExamPoint("1.6", "K", 2, "Prompt chaining for reviews: analyse each file on its own, then run a cross-file integration pass.",
              "✅ large_review · ❌ B"),
    ExamPoint("1.6", "K", 3, "Adaptive investigation plans generate subtasks from what each step discovers.", "✅ legacy_tests · ❌ D"),
    ExamPoint("1.6", "S", 1, "Choose the pattern for the workflow: chaining for predictable multi-aspect reviews, dynamic decomposition "
              "for open-ended investigations.", "❌ C · ❌ E · playground “Pick the pattern”"),
    ExamPoint("1.6", "S", 2, "Split large reviews into per-file local passes plus a separate cross-file integration pass to avoid "
              "attention dilution.", "✅ · ❌ A · ❌ B · playground “Review strategy”"),
    ExamPoint("1.6", "S", 3, "For open-ended work (e.g. tests for a legacy codebase): map the structure, find high-impact areas, then a "
              "prioritised plan that adapts as dependencies turn up.", "✅ legacy_tests · ❌ C · ❌ D · playground “Adaptive plan”"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ Chain the review, adapt the investigation", "correct", CORRECT, "large_review",
            observe=("large_review: 14 per-file passes find the 3 local bugs, and the integration pass over the per-file summaries finds "
                     "the orders ↔ pricing mismatch — 4/4. small_review: 3 files fit in one pass, which finds both issues. legacy_tests: "
                     "map → high-risk first → payments is BLOCKED by a hidden clock dependency → FakeClock is created → payments retried; "
                     "auth, orders and payments are tested within the 6 actions."),
            why="The review's steps are known in advance, so a fixed chain fits; the test task isn't, so the plan is built from what mapping and each attempt reveal."),
    Variant("A", "⭐❌ A — one pass over all 14 files", "distractor", VARIANT_A, "large_review",
            observe=("One call gets every file. Its attention covers only the first 3 (simulated) — README.md, config.py and "
                     "logging_setup.py, none of which holds a planted bug — so it finds 0 of 4, including the cross-file mismatch. On "
                     "small_review the same single pass finds both issues: 3 files fit."),
            why="Spreading one pass across many files dilutes attention; the guide splits large reviews into per-file passes plus an integration pass.",
            fix="Per-file local passes, then a separate cross-file integration pass.", source="guide:1.6:S2"),
    Variant("B", "⭐❌ B — per-file passes, no integration pass", "distractor", VARIANT_B, "large_review",
            observe="All 3 local bugs are found — and the orders ↔ pricing mismatch is missed: no single file shows it. 3/4.",
            why="A cross-file problem only exists between files; it needs the separate integration step of the chain.",
            fix="Add a cross-file integration pass over the per-file summaries.", source="guide:1.6:K2"),
    Variant("C", "⭐❌ C — a fixed plan for an open-ended task", "distractor", VARIANT_C, "legacy_tests",
            observe=("No mapping: modules are done in alphabetical order. auth ✓, legacy_export, orders ✓, payments BLOCKED (skipped), "
                     "reports, string_utils — the budget goes on low-impact modules and payments, which moves money, has no tests."),
            why="An open-ended task has no known step list; a fixed plan can't prioritise what it hasn't mapped or react to what it finds.",
            fix="Map the structure, prioritise high-impact areas, adapt as dependencies appear.", source="guide:1.6:S3"),
    Variant("D", "⭐❌ D — mapped and prioritised, but never adapts", "distractor", VARIANT_D, "legacy_tests",
            observe=("It maps and starts with the high-risk modules — payments first — but when payments is BLOCKED by the clock "
                     "dependency it just skips it. auth and orders get tests; payments never does."),
            why="The guide's adaptive plan turns discovered dependencies into new subtasks; a plan that can't change stalls on the first surprise.",
            fix="When a step reveals a dependency, add the subtask (create the helper) and retry.", source="guide:1.6:K3"),
    Variant("E", "⭐❌ E — an adaptive “what looks important” review", "distractor", VARIANT_E, "large_review",
            observe=("The reviewer picks the files whose names look important (currency, pricing, orders, auth) and reviews those well — "
                     "finding the currency bug and the cross-file mismatch — but never opens search.py or export.py: 2/4."),
            why="A review is predictable work: every file needs the same steps. Choosing files adaptively belongs to open-ended investigations.",
            fix="Use a fixed chain over every file for reviews; keep dynamic decomposition for open-ended tasks.", source="guide:1.6:S1"),
)

TLDR = (
    "Two ways to break up big work. **Prompt chaining** — a fixed sequence of steps — fits **predictable** tasks such as a code review: "
    "analyse **each file on its own**, then run a **separate cross-file integration pass**, instead of one diluted pass over everything. "
    "**Dynamic decomposition** fits **open-ended** tasks such as “add tests to a legacy codebase”: **map** the structure, **prioritise** "
    "high-impact areas, and let the plan **adapt** as each step reveals dependencies. Using either pattern for the other kind of task is "
    "the classic mistake."
)
MENTAL_MODEL = ("A review is an assembly line — same stations, same order, every file through each — with a final inspection that looks "
                "at how the parts fit. An open-ended task is an expedition — scout the map first, head for what matters most, and re-route "
                "when the trail is blocked.")

WHAT_IT_IS = """
The exam guide's TS 1.6 (Guide §6, p.8) is about choosing and designing a decomposition. The docs support both halves: prompt chaining
is for inspecting intermediate outputs or enforcing a pipeline, long tasks need state tracking and incremental progress, and context
quality degrades as it fills.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Prompt chaining | An assembly line: fixed stations, fixed order, you can inspect the part between stations. | ⭐ TS 1.6 · Knowledge 1–2 · p.8 |
| 2 | Per-file local passes | One inspector per part, looking closely — not one glance at the whole pile. | ⭐ TS 1.6 · Skill 2 · p.8 |
| 3 | Cross-file integration pass | The final fit check: parts that pass alone can still fail to connect. | ⭐ TS 1.6 · Knowledge 2, Skill 2 · p.8 |
| 4 | Attention dilution | A torch beam: the wider you spread it, the dimmer each spot. | ⭐ TS 1.6 · Skill 2 · p.8 |
| 5 | Dynamic decomposition | An expedition: the next leg depends on what the last one found. | ⭐ TS 1.6 · Knowledge 1, 3 · p.8 |
| 6 | Map → prioritise → adapt | Scout the map, head for the summit that matters, re-route around the washed-out bridge. | ⭐ TS 1.6 · Skill 3 · p.8 |
| 7 | Choosing the pattern | A recipe for the dinner you cook every week; a plan-as-you-go for exploring a new city. | ⭐ TS 1.6 · Skill 1 · p.8 |

**Which pattern?**

| # | Task | Pattern | Why (guide) |
|---|---|---|---|
| 1 | Review a large multi-file change | Chaining: per-file passes → integration pass | Predictable steps; avoids attention dilution (TS 1.6 S2) |
| 2 | Multi-aspect review (security, style, tests) | Chaining: one fixed step per aspect | Predictable, multi-aspect (TS 1.6 S1) |
| 3 | “Add comprehensive tests to a legacy codebase” | Dynamic: map → prioritise → adapt | Open-ended; dependencies appear as you go (TS 1.6 S3) |
| 4 | Investigate an unfamiliar bug | Dynamic: subtasks from each finding | Next step depends on the last result (TS 1.6 K3) |
"""

HOW_IT_WORKS = """
**Predictable task → prompt chaining**
1. Define the fixed steps (for a review: each file on its own).
2. Run them one by one; keep each step's output (issues + a summary of the file's interface).
3. Run a separate **integration pass** over those summaries to catch problems *between* files.

**Open-ended task → dynamic decomposition**
1. **Map** the structure first.
2. **Prioritise** the high-impact areas.
3. Work the plan one subtask at a time; when a step **reveals a dependency**, add a subtask for it and re-plan.
"""

WHERE_SEEN = """
- **Scenario 5 — Claude Code for Continuous Integration** (Guide §5, p.4): automated code reviews on pull requests — chaining per-file
  passes and an integration pass.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): exploring legacy systems and generating tests — adaptive plans.
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): the coordinator's decomposition (see D1.2).
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 1.6 (p.8) and the official docs (verified 2026-09-27 — pages listed above). Section "
              "layout inspired by a community concept list (claudearchitectcertification.com — community source, unverified; no text copied).")

LAB_INTRO = """
You write the orchestration code for two kinds of task against a **simulated** reviewer and codebase: reviewing a 14-file (or 3-file)
change with planted bugs, and adding tests to a legacy codebase with a hidden dependency and a 6-action budget. All five mistakes are named
in the exam guide (⭐).
"""

DISTRACTORS = (
    ("A · One pass over all files", "One call sees everything at once.", "Attention is diluted — most bugs are missed.",
     "Per-file passes + an integration pass.", "guide:1.6:S2"),
    ("B · Per-file passes only", "Every file was reviewed carefully.", "Bugs between files are invisible file-by-file.",
     "Add a cross-file integration pass.", "guide:1.6:K2"),
    ("C · A fixed plan for an open-ended task", "A clear plan up front is disciplined.",
     "It can't prioritise what it hasn't mapped or react to discoveries.", "Map → prioritise → adapt.", "guide:1.6:S3"),
    ("D · A plan that never adapts", "It was mapped and prioritised.", "The first discovered dependency stalls it.",
     "Turn discoveries into new subtasks.", "guide:1.6:K3"),
    ("E · Adaptive picking for a predictable review", "Focus on what looks important.",
     "Files that don't look important are never opened.", "A fixed chain over every file.", "guide:1.6:S1"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Prompt chaining", "Dynamic decomposition", "One big pass")
SIDE_BY_SIDE_ROWS = (
    ("1", "Steps", "Fixed in advance", "Generated from findings", "One"),
    ("2", "Best for", "Predictable, multi-aspect reviews", "Open-ended investigations", "Small tasks that fit comfortably"),
    ("3", "Strength", "Inspectable intermediate outputs; each step focused", "Reacts to discoveries; prioritises", "Simple"),
    ("4", "Failure mode", "Can't react to surprises", "Can wander without a map and priorities", "Attention dilution"),
    ("5", "Exam reference", "TS 1.6 K1–K2, S1–S2", "TS 1.6 K1, K3, S1, S3", "TS 1.6 S2 (what it avoids)"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Are the steps known in advance?"];
  Q2 [shape=diamond, label="Does it span many files?"];
  CH [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Chain: per-file passes\\n→ cross-file integration pass"];
  ONE [shape=box, label="One pass is fine"];
  DY [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Dynamic: map → prioritise →\\nadapt as dependencies appear"];
  Q1 -> Q2 [label="yes"]; Q1 -> DY [label="no"]; Q2 -> CH [label="yes"]; Q2 -> ONE [label="no"];
}'''

EXPERIMENTS = (
    "Run ✅ on all three scenarios and read the pass list in the trace.",
    "Run ⭐❌ A on small_review (passes) and large_review (fails): same code, different size.",
    "In ✅, delete the integration_pass line and run large_review — you built ⭐❌ B.",
    "Run ⭐❌ D and find the BLOCKED line; add the create_helper step back and re-run.",
)

QUESTIONS = (
    Question(
        q=("Your CI review step sends one prompt with all 20 changed files of a pull request. It catches obvious issues "
           "in a few files, misses most others, and never notices that a changed function signature breaks a caller in "
           "another file. What's the best restructuring?"),
        opts=("Use a model with a larger context window for the same single prompt.",
              "Review only the five largest files.",
              "Ask the reviewer to be more thorough and check every file carefully.",
              "Review each file in its own pass, then run a separate cross-file integration pass."),
        ans=3,
        explain=("Chaining per-file local passes with a separate cross-file integration pass avoids attention "
                 "dilution. A bigger window doesn't fix dilution, and “be thorough” changes nothing structural."),
        scenarios=(5,), points=("1.6:K2", "1.6:S2"),
    ),
    Question(
        q=("An engineer asks the agent to “add comprehensive tests to our legacy billing codebase”. Nobody knows which "
           "modules are risky, and dependencies are tangled. Which approach fits best?"),
        opts=("Map the structure, find the high-impact areas, then follow a prioritised plan that adapts as dependencies emerge.",
              "Generate tests file by file in alphabetical order.",
              "Write a fixed ten-step pipeline up front and run it unchanged.",
              "Ask the agent to write all the tests in one response."),
        ans=0,
        explain=("Open-ended work calls for dynamic decomposition: the plan generates subtasks from what each step "
                 "discovers. A fixed pipeline can't respond to what the exploration finds."),
        scenarios=(4,), points=("1.6:K3", "1.6:S3"),
    ),
    Question(
        q=("A team has two workflows. Workflow 1: every pull request gets the same security, style and test-coverage "
           "checks. Workflow 2: finding why checkout latency spikes under load in a system nobody fully understands. "
           "Which pattern suits each?"),
        opts=("Dynamic decomposition for both, since agents should always adapt.",
              "Prompt chaining for both, since fixed steps are easier to audit.",
              "Prompt chaining for workflow 1, dynamic decomposition for workflow 2.",
              "Dynamic decomposition for workflow 1, prompt chaining for workflow 2."),
        ans=2,
        explain=("Prompt chaining suits predictable, multi-aspect work that repeats. Dynamic decomposition suits "
                 "open-ended investigations whose next steps depend on intermediate findings."),
        scenarios=(5, 4), points=("1.6:K1", "1.6:S1"),
    ),
    Question(
        q=("An agent investigating a production memory leak was given a fixed plan: profile service A, then B, then C. "
           "The profile of A shows the leak comes from a shared caching library used by D and E, which aren't in the "
           "plan. What would have handled this better?"),
        opts=("A longer fixed plan that covers every service.",
              "An adaptive plan that creates the next subtasks from what each step finds.",
              "Running A, B and C in parallel to finish sooner.",
              "Stopping the investigation and escalating after step 1."),
        ans=1,
        explain=("Adaptive investigation plans generate subtasks from what each step discovers. A fixed sequence can't "
                 "follow a lead it didn't anticipate."),
        scenarios=(4,), points=("1.6:K3",),
    ),
    Question(
        q=("A CI review runs as three separate calls: extract changes, review them, then format comments. A newer model "
           "could do it in one call. The team must log and evaluate each stage's output for audits. Should they keep "
           "the chain?"),
        opts=("No, a single call is always better with current models.",
              "Only if the context window is too small for one call.",
              "No, chaining is only for image tasks.",
              "Yes, chaining is still worth it when you need to inspect intermediate outputs or enforce a pipeline structure."),
        ans=3,
        explain=("Per the prompting docs, explicit chaining is still useful when you need to inspect intermediate "
                 "outputs or enforce a specific pipeline. Each step can be logged, evaluated or branched."),
        scenarios=(5,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Is the “3 files per pass” limit real?",
     "No — it's the simulation's stand-in for attention dilution. The guide names the effect; the exact point where it appears depends on "
     "the task and the model."),
    ("Where do subagents fit?",
     "Per-file passes can run as parallel subagents (D1.2); the docs suggest subagents for independent workstreams and direct work for "
     "sequential steps. The integration pass needs everyone's summaries, so it runs after them."),
    ("Isn't a fixed plan just good discipline?",
     "For predictable work, yes — that's chaining. For open-ended work the guide asks for a plan that adapts to what each step discovers."),
)

PLAYGROUND_INTRO = """
Type the task. Words like *review* send it to the simulated reviewer; words like *test* or *legacy* send it to the legacy codebase.
Choose the strategy and see what gets found or done.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="decomp")


PLAYGROUND = (
    _tab("review", "⭐ Review strategy", "review",
         "A torch beam: spread it over 14 files and each one gets a dim glance.", "guide:1.6:S2",
         "One pass over everything, per-file passes, or per-file passes plus an integration pass — on 3 or 14 files.",
         "guide TS 1.6 Knowledge 2, Skill 2; prompting best practices § Chain complex prompts",
         ("strategy", "n_files"), {"strategy": "chain", "n_files": 14}, ("Review this pull request for bugs.",),
         ("chain on 14: 4/4.", "per-file only: 3/4 — the cross-file mismatch is missed.", "single pass on 14: 0/4.",
          "single pass on 3: 2/2 — small work doesn't need a chain.")),
    _tab("plan", "⭐ Adaptive plan", "plan",
         "An expedition: scout, go for the summit that matters, re-route at the washed-out bridge.", "guide:1.6:S3",
         "A fixed alphabetical plan, a mapped and prioritised plan that never changes, or one that adapts to discoveries.",
         "guide TS 1.6 Knowledge 3, Skill 3",
         ("plan", "budget"), {"plan": "adaptive", "budget": 6}, ("Add comprehensive tests to our legacy codebase.",),
         ("adaptive: auth, orders, payments tested.", "mapped only: payments skipped when blocked.",
          "fixed: budget spent on low-impact modules.", "Raise the budget to 10: does the fixed plan catch up?")),
    _tab("pick", "⭐ Pick the pattern", "pick",
         "A recipe for the weekly dinner; plan-as-you-go for a new city.", "guide:1.6:S1",
         "Apply chaining or dynamic decomposition to whatever task you type — and see what happens when the pattern doesn't fit.",
         "guide TS 1.6 Knowledge 1, Skill 1",
         ("pattern",), {"pattern": "chaining"}, ("Review this pull request for bugs.", "Add comprehensive tests to our legacy codebase."),
         ("Review + chaining: 4/4.", "Review + dynamic: files that don't look important are skipped.",
          "Tests + chaining: a fixed plan, payments untested.", "Tests + dynamic: all high-impact modules tested.")),
)

DECISION_DOT = readable(DECISION_DOT)   # FLOWCHART RULE: 18pt, max 2 nodes per row

CONTENT = ConceptContent(
    slug="task-decomposition", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("subagents", "agentic-loops", "session-state"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("large_review", "small_review", "legacy_tests"), show_ledger=False,
)
