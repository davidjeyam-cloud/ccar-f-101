"""
D2.6 Built-In Tools vs Custom Tools vs Skills vs MCP — picking the right built-in tool for each job (guide TS 2.5: Grep for
content, Glob for paths, Read/Write for whole files, Edit for unique anchors, Read + Write when Edit can't anchor, incremental
exploration, tracing through wrapper modules), and picking the right extension surface (CLAUDE.md, skill, hook, MCP, subagent)
for each need (TS 3.2 Skill 5, TS 2.4 Skill 3–4). Guide pp.11–13.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); Claude Code docs fetched 2026-09-28 (DOC_REFS).
Every claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Tools reference — Read, Write, Edit, Grep, Glob, Bash", f"{_C}/tools-reference"),
    DocRef("Extend Claude Code — CLAUDE.md, skills, subagents, hooks, MCP, plugins", f"{_C}/features-overview"),
)

GROUNDING = (
    Claim("Grep searches file contents for a pattern (ripgrep regex syntax; respects .gitignore); output modes: files, content "
          "lines, counts.", "docs", "tools-reference § Grep"),
    Claim("Glob finds files by path pattern; ** matches any depth (e.g. **/*.js); results sorted by modification time, capped "
          "at 100.", "docs", "tools-reference § Glob"),
    Claim("Read returns a file's contents with line numbers; Write creates or overwrites a file; Edit replaces an exact "
          "old_string that must appear exactly once — otherwise give more surrounding context or set replace_all: true. Claude "
          "reads a file in the conversation before editing it.", "docs", "tools-reference § Read, Write, Edit"),
    Claim("On macOS, Linux and WSL the Grep and Glob tools are absent by default; Claude searches with grep and find through "
          "Bash instead.", "docs", "tools-reference § Grep, Glob"),
    Claim("Built-in tools cover most coding tasks; the extension layer adds CLAUDE.md (always loaded), skills (on demand), "
          "MCP (external services), subagents (isolated context) and hooks (run on events).", "docs", "features-overview § Overview"),
    Claim("CLAUDE.md loads every session; a skill's description loads each session and its full content when used; MCP tool "
          "names load at start with schemas deferred; subagents get isolated context; hooks cost no context unless they return "
          "output.", "docs", "features-overview § Context cost by feature"),
    Claim("An instruction such as 'never edit .env' in CLAUDE.md or a skill is a request, not a guarantee; if a rule must hold "
          "every time, make it a hook.", "docs", "features-overview § Hook vs Skill"),
    Claim("MCP connects Claude to external services (tools and data); skills carry knowledge and workflows, including how to "
          "use those tools well.", "docs", "features-overview § MCP vs Skill"),
    Claim("Grep for content search; Glob for path patterns; Read/Write for whole files and Edit for targeted changes by unique "
          "text; Read + Write when Edit can't find a unique anchor.", "guide", "TS 2.5 · Knowledge 1–4 · pp.11–12"),
    Claim("Skills: Grep to find callers or error messages; Glob for naming patterns like **/*.test.tsx; Read then Write when Edit "
          "can't anchor; build understanding incrementally (Grep for entry points, then Read following imports) instead of "
          "reading everything upfront; trace usage through wrapper modules by listing exported names, then searching for each.",
          "guide", "TS 2.5 · Skills 1–5 · p.12"),
    Claim("Choose skills for on-demand, task-specific workflows and CLAUDE.md for always-loaded universal standards.", "guide",
          "TS 3.2 · Skill 5 · p.13"),
    Claim("Enhance MCP tool descriptions so the agent doesn't prefer built-ins like Grep over more capable MCP tools; prefer "
          "community MCP servers for standard integrations.", "guide", "TS 2.4 · Skills 3–4 · p.11"),
    Claim("The guide assumes Grep and Glob tools; the docs say they are absent by default on macOS/Linux/WSL, where the same "
          "searches run through Bash. The choice (content vs path search) is the same either way.", "guide", "TS 2.5 vs tools-reference"),
    Claim("The repository, the tasks, the read budget and the tool error texts are invented.", "simulated", "utils/builtin_lab.py"),
)

CORRECT = r'''import re
from utils.builtin_lab import TASK, EditError, glob, grep, read, submit, write, edit   # SIMULATED repo + tools

if TASK == "find_callers":
    # CONTENT search: which files CALL process_refund? -> Grep (not a file-name search)
    hits = grep(r"process_refund\(")
    submit(sorted({path for path, n, line in hits if not line.lstrip().startswith("def ")}))

elif TASK == "find_tests":
    # PATH pattern: which files are .test.tsx files? -> Glob
    submit(glob("**/*.test.tsx"))

elif TASK == "edit_nonunique":
    # change the PAYMENTS timeout to 60 - "timeout = 30" appears twice
    path = "config/app.toml"
    read(path)
    try:
        edit(path, "timeout = 30", "timeout = 60")
    except EditError:
        # Edit can't anchor uniquely -> Read the whole file, change the right occurrence, Write it back
        text = read(path)
        head, tail = text.split("[payments]")
        write(path, head + "[payments]" + tail.replace("timeout = 30", "timeout = 60", 1))
    submit("done")

elif TASK == "trace_flow":
    # how does a refund get approved? Start at the entry point, then follow the imports - don't read everything
    entry = grep(r"def process_refund\(")[0][0]
    seen, queue = [], [entry]
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.append(path)
        for mod in re.findall(r"from (billing\.\w+) import", read(path)):
            queue.append(mod.replace(".", "/") + ".py")
    submit(sorted(seen))

elif TASK == "wrapper_usage":
    # which files call the functions the payments wrapper EXPORTS? First list the exported names...
    names = re.findall(r"'(\w+)'", read("payments/__init__.py").split("__all__")[1])
    # ...then search for each name
    users = {path for name in names for path, n, line in grep(rf"\b{name}\(") if not path.startswith("payments/")}
    submit(sorted(users))
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ TS 2.5 · Skill 1 / Knowledge 1 — a file-name search for a content question
VARIANT_A = _swap(CORRECT, '''    hits = grep(r"process_refund\\(")
    submit(sorted({path for path, n, line in hits if not line.lstrip().startswith("def ")}))''',
                  '''    submit(glob("**/*refund*"))   # WRONG: searches file NAMES, not the code that calls the function''')
# ⭐ TS 2.5 · Skill 2 / Knowledge 2 — a content search for a path question
VARIANT_B = _swap(CORRECT, '''    submit(glob("**/*.test.tsx"))''',
                  '''    submit(sorted({path for path, n, line in grep("test")}))   # WRONG: searches CONTENTS for "test"''')
# 📘 docs — replace_all when only one occurrence should change
VARIANT_C = _swap(CORRECT, '''        edit(path, "timeout = 30", "timeout = 60")''',
                  '''        edit(path, "timeout = 30", "timeout = 60", replace_all=True)   # WRONG: changes EVERY timeout''')
# ⭐ TS 2.5 · Skill 3 / Knowledge 4 — no Read + Write fallback when Edit can't anchor
VARIANT_D = _swap(CORRECT, '''        # Edit can't anchor uniquely -> Read the whole file, change the right occurrence, Write it back
        text = read(path)
        head, tail = text.split("[payments]")
        write(path, head + "[payments]" + tail.replace("timeout = 30", "timeout = 60", 1))''',
                  '''        pass   # WRONG: Edit failed and nothing else is tried''')
# ⭐ TS 2.5 · Skill 4 — read everything upfront
VARIANT_E = _swap(CORRECT, '''    entry = grep(r"def process_refund\\(")[0][0]''', '''    from utils.builtin_lab import all_paths
    everything = {p: read(p) for p in all_paths()}   # WRONG: reads the whole repo upfront
    entry = next(p for p, t in everything.items() if "def process_refund(" in t)''')
# ⭐ TS 2.5 · Skill 5 — search for the original names, not the wrapper's exported names
VARIANT_F = _swap(CORRECT, '''    names = re.findall(r"'(\\w+)'", read("payments/__init__.py").split("__all__")[1])''',
                  '''    names = ["charge", "refund"]   # WRONG: the functions' ORIGINAL names - the wrapper exports them under other names''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "builtin_task"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "submit() was never called"
    calls = " · ".join(r["calls"])
    if sc == "edit_nonunique":
        txt = f"calls: {calls} · config/app.toml now: {r['toml']!r}"
        if r["correct"]:
            return True, None, txt
        return False, ("REPLACEALL" if r["toml"].count("timeout = 60") == 2 else "NOFALLBACK"), txt
    txt = f"calls: {calls} · answer: {r['answer']} · chars read: {r['chars_read']}"
    over = sc == "trace_flow" and r["chars_read"] > r["budget"]
    if r["correct"] and not over:
        return True, None, txt
    bug = {"find_callers": "WRONGSEARCH", "find_tests": "WRONGSEARCH", "trace_flow": "READALL", "wrapper_usage": "ORIGNAMES"}[sc]
    return False, bug, txt + (f" (over the {r['budget']}-char budget)" if over else "")


EXPECTED = {
    "find_callers": "support/bot.py and web/checkout.py — the files that CALL process_refund (a content search)",
    "find_tests": "ui/Button.test.tsx and ui/forms/Field.test.tsx — files named *.test.tsx (a path search)",
    "edit_nonunique": "only the [payments] timeout becomes 60; [orders] stays 30",
    "trace_flow": "refunds.py → approvals.py → limits.py, reading under 1,600 chars",
    "wrapper_usage": "shop/cart.py, shop/returns.py and shop/admin.py — callers of charge_card / issue_refund",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":    ("#EDE9FE", "#7C3AED", "the question"),
    "find": ("#DBEAFE", "#0066CC", "finding (Grep / Glob)"),
    "file": ("#FEF3C7", "#D97706", "changing files (Read / Edit / Write)"),
    "flow": ("#CCFBF1", "#0D9488", "understanding code incrementally"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "Q":     ("What do you need?", "diamond", "q"),
    "GREP":  ("⭐ Text INSIDE files\\n(callers, errors, imports)\\n→ Grep", "box", "find"),
    "GLOB":  ("⭐ Files by NAME / path\\n(**/*.test.tsx) → Glob", "box", "find"),
    "EDIT":  ("⭐ Targeted change with a\\nunique anchor → Edit", "box", "file"),
    "RW":    ("⭐ Edit can't anchor →\\nRead the file + Write it", "box", "file"),
    "INC":   ("⭐ Understand a flow: Grep the\\nentry point, Read along imports", "box", "flow"),
    "WRAP":  ("⭐ Through a wrapper: list the\\nexported names, Grep each", "box", "flow"),
    "WRONGSEARCH": ("✗ path search for content\\n(or content for paths)", "box", "bug"),
    "REPLACEALL":  ("✗ replace_all when one\\noccurrence should change", "box", "bug"),
    "NOFALLBACK":  ("✗ Edit fails,\\nno Read + Write", "box", "bug"),
    "READALL":     ("✗ read every file\\nupfront", "box", "bug"),
    "ORIGNAMES":   ("✗ searched the original\\nnames, not the exports", "box", "bug"),
}
_BUGS = ["WRONGSEARCH", "REPLACEALL", "NOFALLBACK", "READALL", "ORIGNAMES"]
_EXP = {"find_callers": ["GREP"], "find_tests": ["GLOB"], "edit_nonunique": ["EDIT", "RW"], "trace_flow": ["GREP", "INC"],
        "wrapper_usage": ["WRAP", "GREP"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 2.5 pp.11–12)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = the right tool · '
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
    lines += ['  Q -> GREP [label="find text"]; Q -> GLOB [label="find files"]; Q -> EDIT [label="change a file"];',
              '  Q -> INC [label="understand code"]; EDIT -> RW [label="not unique / not found"]; INC -> WRAP [label="through a wrapper"];',
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  WRAP -> WRONGSEARCH [style=invis]; RW -> WRONGSEARCH [style=invis];",
              _key(hl), f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
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
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("2.5", "K", 1, "Grep searches file contents for patterns (function names, error messages, imports).", "✅ find_callers · ❌ A"),
    ExamPoint("2.5", "K", 2, "Glob matches file paths by pattern (names, extensions).", "✅ find_tests · ❌ B"),
    ExamPoint("2.5", "K", 3, "Read/Write handle whole files; Edit makes targeted changes by unique text matching.", "✅ edit_nonunique"),
    ExamPoint("2.5", "K", 4, "When Edit fails on non-unique text, fall back to Read + Write.", "✅ edit_nonunique · ❌ D"),
    ExamPoint("2.5", "S", 1, "Choose Grep to search code content across a codebase (all callers of a function, an error message).", "✅ find_callers"),
    ExamPoint("2.5", "S", 2, "Choose Glob to find files matching naming patterns (**/*.test.tsx).", "✅ find_tests"),
    ExamPoint("2.5", "S", 3, "Read the full file, then Write, when Edit can't find a unique anchor.", "✅ edit_nonunique · ❌ D"),
    ExamPoint("2.5", "S", 4, "Build understanding incrementally — Grep for entry points, then Read along imports — instead of reading everything upfront.",
              "✅ trace_flow · ❌ E"),
    ExamPoint("2.5", "S", 5, "Trace usage across wrapper modules: list the exported names first, then search for each.", "✅ wrapper_usage · ❌ F"),
    ExamPoint("3.2", "S", 5, "Choose skills for on-demand, task-specific workflows and CLAUDE.md for always-loaded universal standards.",
              "Grids below · playground “Which surface?”"),
    ExamPoint("2.4", "S", 3, "Describe MCP tools well enough that the agent doesn't prefer built-ins like Grep over a more capable MCP tool.",
              "Grid below (see also D2.3)"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ Grep for content · Glob for paths · Read + Write fallback · incremental · exported names", "correct", CORRECT, "find_callers",
            observe=("find_callers: Grep 'process_refund\\(' → 3 lines; dropping the definition leaves support/bot.py and "
                     "web/checkout.py. find_tests: Glob '**/*.test.tsx' → the 2 test files. edit_nonunique: Edit fails (“appears 2 "
                     "times”), so Read + Write changes only [payments]. trace_flow: Grep the entry point, then Read along imports — 3 "
                     "files, 403 chars. wrapper_usage: Read payments/__init__.py → exports charge_card, issue_refund → Grep each → the 3 shop files."),
            why="Each job gets the tool built for it, and understanding grows from an entry point instead of from reading everything."),
    Variant("A", "⭐❌ A — Glob for a content question", "distractor", VARIANT_A, "find_callers",
            observe="Glob '**/*refund*' → billing/refunds.py, docs/refund_policy.md, scripts/refund_report.py — none of which is a caller; both real callers are missed.",
            why="Callers are text inside files. Glob only matches file names and paths.", fix="Grep for the call pattern.", source="guide:2.5:S1"),
    Variant("B", "⭐❌ B — Grep for a path question", "distractor", VARIANT_B, "find_tests",
            observe="Grep 'test' → the 2 test files plus ui/README.md and ui/testing-utils.tsx, which only mention the word.",
            why="“Which files are test files?” is a naming pattern. Content search also returns files that merely mention the word.",
            fix="Glob '**/*.test.tsx'.", source="guide:2.5:S2"),
    Variant("C", "❌ C — replace_all when one occurrence should change", "distractor", VARIANT_C, "edit_nonunique",
            observe="Edit replaced 2 occurrences: [orders] timeout is now 60 as well as [payments].",
            why="replace_all changes every match. The docs offer it for when all of them should change.",
            fix="A longer, unique anchor — or Read + Write.", source="docs"),
    Variant("D", "⭐❌ D — Edit fails and nothing else is tried", "distractor", VARIANT_D, "edit_nonunique",
            observe="Edit raised “old_string appears 2 times”; the code swallowed it — the payments timeout is still 30.",
            why="When Edit can't find a unique anchor, the guide's fallback is to Read the whole file and Write it back.",
            fix="Read + Write (or a longer anchor).", source="guide:2.5:S3"),
    Variant("E", "⭐❌ E — read the whole repository upfront", "distractor", VARIANT_E, "trace_flow",
            observe="33 files read, 7,895 chars — to find the same 3 files the incremental version found with 403 chars (budget 1,600).",
            why="Reading everything fills the context with unrelated code. Grep finds the entry point; Read follows only what it imports.",
            fix="Grep the entry point, then Read along imports.", source="guide:2.5:S4"),
    Variant("F", "⭐❌ F — search the original names, not the wrapper's exports", "distractor", VARIANT_F, "wrapper_usage",
            observe="Grep charge( / refund( finds only legacy/old_pay.py; the 3 shop files call charge_card / issue_refund and are all missed.",
            why="A wrapper can re-export functions under new names. List the exported names first, then search for each.",
            fix="Read the wrapper's exports, then Grep each name.", source="guide:2.5:S5"),
)

TLDR = (
    "**Built-in tools first.** The docs say they cover most coding tasks:\n\n"
    "- **Grep:** text *inside* files (callers, error messages, imports).\n"
    "- **Glob:** files by *name or path* (`**/*.test.tsx`).\n"
    "- **Edit:** a small change anchored on text that appears **once**.\n"
    "- **Read + Write:** when Edit can't anchor.\n\n"
    "**Explore incrementally.** Grep for the entry point, then Read along the imports. **Through a wrapper**, list the exported "
    "names, then search for each.\n\n"
    "**Extensions** are for needs built-ins don't meet:\n\n"
    "- **CLAUDE.md:** always-on rules.\n"
    "- **Skill:** on-demand workflows.\n"
    "- **Hook:** rules that must hold every time.\n"
    "- **MCP:** external systems.\n"
    "- **Subagent:** noisy work in isolation."
)
MENTAL_MODEL = ("Grep is a search inside the pages; Glob reads the spines on the shelf. Edit is a precise sticker — it needs one "
                "exact spot. If the spot appears twice, rewrite the page (Read + Write). Don't read the whole library to answer "
                "one question: find the index entry and follow the references.")

WHAT_IT_IS = """
The exam guide covers choosing and applying built-in tools (Guide §6 · TS 2.5, pp.11–12). It also covers choosing skills vs
CLAUDE.md (TS 3.2 · Skill 5, p.13) and MCP tools vs built-ins (TS 2.4 · Skill 3, p.11). The docs' tools reference and
*Extend Claude Code* page give the exact behaviour and context costs.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Grep | A search inside the pages — finds where text is used. | ⭐ TS 2.5 · Knowledge 1, Skill 1 |
| 2 | Glob | Reading the book spines — finds files by name or path. | ⭐ TS 2.5 · Knowledge 2, Skill 2 |
| 3 | Edit | A precise sticker on one exact spot; if the spot appears twice, it won't stick. | ⭐ TS 2.5 · Knowledge 3 |
| 4 | Read + Write fallback | When the sticker won't stick, rewrite the page. | ⭐ TS 2.5 · Knowledge 4, Skill 3 |
| 5 | Incremental exploration | Find the index entry, follow the references — don't read the library. | ⭐ TS 2.5 · Skill 4 |
| 6 | Wrapper modules | A shop sign can rename the product; search for the name on the sign. | ⭐ TS 2.5 · Skill 5 |
| 7 | Skill vs CLAUDE.md | A manual on the shelf (fetched when needed) vs the rules on the wall (always seen). | ⭐ TS 3.2 · Skill 5 |
| 8 | MCP tool vs built-in | A specialist tool only gets used if its label says why it beats the familiar one. | ⭐ TS 2.4 · Skill 3 |
| 9 | Grep/Glob absent by default on macOS/Linux/WSL | Same two questions, asked through Bash (`grep`, `find`). | 📘 docs only |

**Grid 1 — which built-in tool?** (docs + guide)

| # | Question | Tool | Not this | Why |
|---|---|---|---|---|
| 1 | Where is `process_refund(` called? | ⭐ **Grep** | Glob | The answer is text inside files |
| 2 | Which files are `*.test.tsx`? | ⭐ **Glob** | Grep | The answer is a naming pattern |
| 3 | Change one line whose text is unique | ⭐ **Edit** | Write | Targeted, small, safe |
| 4 | Change one of two identical lines | ⭐ **Read + Write** (or a longer unique anchor) | Edit with `replace_all` | Edit needs exactly one match |
| 5 | Understand how a refund is approved | ⭐ **Grep** entry point → **Read** along imports | Read everything | Context goes on what matters |
| 6 | Who calls a wrapper's functions? | ⭐ **Read** the exports → **Grep** each name | Grep the original names | Re-exports can rename them |

**Grid 2 — built-in vs extension surface** (docs: *Extend Claude Code*)

| # | Surface | What it's for | Loads | Context cost | Enforced? |
|---|---|---|---|---|---|
| 1 | Built-in tools | Files, search, shell, web — most coding tasks | Always there | Tool definitions | — |
| 2 | CLAUDE.md | ⭐ Always-on conventions (“use pnpm”) | Every session, full content | Every request | No — an instruction |
| 3 | Skill | ⭐ On-demand workflows and reference (`/deploy`) | Description each session; content when used | Low until used | No — an instruction |
| 4 | Hook | Rules that must hold every time; automation on events | On its event, outside the conversation | Zero unless it returns output | **Yes** |
| 5 | MCP server | ⭐ External systems' tools and data | Tool names at start; schemas on demand | Low until used | — |
| 6 | Subagent | Noisy work in isolation; only a summary returns | When spawned | Isolated | — |
"""

HOW_IT_WORKS = """
1. **Name the question.** Text inside files → Grep. Files by name → Glob. A change → Edit.
2. **Edit needs one exact match.** If the text appears twice, give a longer unique anchor, or Read the file and Write it back.
   Use `replace_all` only when **every** match should change.
3. **Explore from an entry point:** Grep for it, Read it, follow its imports. Stop when the question is answered.
4. **Through a wrapper:** read what it exports (it may rename things), then Grep for each exported name.
5. **When built-ins aren't enough**, pick the extension by the need. Always-on rule → CLAUDE.md. Occasional workflow →
   skill. Must-hold rule → hook. External system → MCP. Noisy side task → subagent.
"""

WHERE_SEEN = """
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): finding code, editing safely, exploring incrementally.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): built-ins vs MCP tools, skills vs CLAUDE.md.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 2.5 (pp.11–12), TS 3.2 Skill 5 (p.13) and TS 2.4 Skill 3 (p.11), and the Claude "
              "Code docs (verified 2026-09-28 — pages listed above). Section layout inspired by a community concept list "
              "(claudearchitectcertification.com — community source, unverified; no text copied).")

LAB_INTRO = """
A small **simulated** repository and five jobs. You call `grep`, `glob`, `read`, `edit` and `write`, shaped like Claude Code's
built-in tools, and `submit()` the answer. The lab checks the answer and counts how many characters you read, as a stand-in for
context. Edit follows the docs' rule: the text must appear **exactly once**, and you must read a file before editing it.
"""

DISTRACTORS = (
    ("A · Glob for a content question", "“refund” is in the file names.", "Returns files named like it, not the callers.", "Grep.", "guide:2.5:S1"),
    ("B · Grep for a path question", "“test” finds the tests.", "Also returns files that mention “test”.", "Glob **/*.test.tsx.", "guide:2.5:S2"),
    ("C · replace_all for one occurrence", "Edit said it's ambiguous — make it change them all.", "Changes the other section too.",
     "A longer anchor, or Read + Write.", "docs"),
    ("D · Give up when Edit fails", "The tool refused.", "The change never happens.", "Read + Write.", "guide:2.5:S3"),
    ("E · Read everything upfront", "Then nothing is missed.", "7,895 chars to find 3 files.", "Grep the entry, Read along imports.", "guide:2.5:S4"),
    ("F · Search the original names", "Those are the functions.", "The wrapper renamed them; every caller is missed.",
     "Read the exports, Grep each.", "guide:2.5:S5"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Grep", "Glob")
SIDE_BY_SIDE_ROWS = (
    ("1", "Searches", "File contents (ripgrep regex)", "File paths (glob patterns, ** = any depth)"),
    ("2", "Answers", "“Where is this text?”", "“Which files are named like this?”"),
    ("3", "Returns", "Files, matching lines, or counts", "File paths, newest first, up to 100"),
    ("4", ".gitignore", "Respected", "Not respected by default"),
    ("5", "Exam example", "All callers of a function; an error message", "**/*.test.tsx"),
    ("6", "On macOS/Linux/WSL by default", "Absent — grep via Bash", "Absent — find via Bash"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Can a built-in tool\\ndo it?"];
  Q2 [shape=diamond, label="Looking for text\\nINSIDE files?"];
  GREP [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Grep"];
  GLOB [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Glob (by name/path)"];
  Q3 [shape=diamond, label="What's missing?"];
  CMD [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Always-on rule → CLAUDE.md"];
  SKILL [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Occasional workflow → skill"];
  HOOK [shape=box, fillcolor="#D1FAE5", color="#059669", label="Must hold every time → hook"];
  MCP [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="External system → MCP"];
  Q1 -> Q2 [label="yes: search"]; Q2 -> GREP [label="yes"]; Q2 -> GLOB [label="no"];
  Q1 -> Q3 [label="no"]; Q3 -> CMD; Q3 -> SKILL; Q3 -> HOOK; Q3 -> MCP;
}''')

EXPERIMENTS = (
    "Run ✅ on all five tasks and read the tool calls for each.",
    "In ✅'s edit branch, replace the fallback with edit(path, \"[payments]\\ntimeout = 30\", \"[payments]\\ntimeout = 60\") — a longer unique anchor also works.",
    "Run ⭐❌ E on trace_flow and compare the chars read with ✅'s 403.",
    "In the playground's search tab, type an error message and try both Grep and Glob.",
    "In “Which surface?”, pick the guardrail need and choose CLAUDE.md, then Hook.",
)

QUESTIONS = (
    Question(
        q=("Before removing the deprecated function legacy_price(), a developer asks the agent to find every place it is "
           "called across a 4,000-file repository. A first attempt opened files one by one with Read and, after 25 minutes, "
           "had covered about 10% of the code. Which built-in tool fits this step?"),
        opts=("Glob for **/*price*, then Read each matching file to look for the calls.",
              "Grep for legacy_price( across the codebase.",
              "Read the files that import pricing modules, one directory at a time.",
              "Bash with a find command listing every file changed in the last year."),
        ans=1,
        explain=("Grep searches file contents, which is exactly what finding callers needs. A matches file names, not calls, "
                 "and misses callers in files named differently. C is the slow file-by-file approach again. D lists files "
                 "by date, which says nothing about calls."),
        scenarios=(4,), points=("2.5:K1", "2.5:S1"),
    ),
    Question(
        q=("Before a testing-framework migration, the agent must list every React test file. They follow the "
           "Component.test.tsx naming and are scattered across 60 folders. The agent's first attempt, a Grep for “describe(”, "
           "returned 1,400 matches, including 300 from files that are not tests. Which tool is right?"),
        opts=("Grep for “test.tsx” in file contents across the whole repository.",
              "Read the package.json test configuration to find where the test files are.",
              "Glob with **/*.test.tsx.",
              "Grep for “import { render }” to find files that render React components."),
        ans=2,
        explain=("Glob matches file paths by pattern, which is what a naming convention needs. A and D search contents for a "
                 "proxy, which is imprecise. B describes the configuration, not the files."),
        scenarios=(4,), points=("2.5:K2", "2.5:S2"),
    ),
    Question(
        q=("The agent must change timeout = 30 to timeout = 60 only in the [payments] section of a config file. Edit fails "
           "because that exact line appears in four sections. On its next attempt the agent edits the first match instead, "
           "changing the wrong section. What is the right fallback?"),
        opts=("Retry Edit with replace-all enabled, so that every occurrence is changed at once in a single step.",
              "Ask the developer to make the change by hand, since Edit can never target a line that repeats.",
              "Use Grep to count the matches, then Edit whichever one appears closest to the start of the file.",
              "Read the whole file, then Write it back with only the intended section changed."),
        ans=3,
        explain=("When Edit can't find unique anchor text, the fallback is Read plus Write, changing only the intended "
                 "section. A changes all four sections. B gives up on a task the tools can do. C is the “first match” "
                 "guess that already went wrong."),
        scenarios=(2, 4), points=("2.5:K3", "2.5:K4", "2.5:S3"),
    ),
    Question(
        q=("A new engineer asks how an order moves from checkout to fulfilment in an unfamiliar 3,000-file codebase. The "
           "agent's first plan is to Read every file under src/ before answering, which would use up most of its context. "
           "What is the most effective exploration strategy?"),
        opts=("Glob for every file under src/, then Read them in alphabetical order until the flow becomes clear.",
              "Answer from general knowledge of e-commerce systems, then check a few files to confirm the answer.",
              "Grep for the checkout entry point, then Read along the imports it leads to, step by step.",
              "Read the README and the top-level folder names, then describe the whole flow from those alone."),
        ans=2,
        explain=("Build understanding incrementally: find the entry point with Grep, then follow imports with Read. A reads "
                 "everything and fills the context. B starts from assumptions, not the code. D guesses the flow from "
                 "folder names."),
        scenarios=(4,), points=("2.5:S4",),
    ),
    Question(
        q=("A utils/index.ts file re-exports helpers from five internal modules. To find usages of one module, the agent "
           "grepped for that module's file name and found 3 matches, although the helpers are used in over 200 files. What "
           "should it do instead?"),
        opts=("List the names that index.ts exports, then Grep for each of those names across the codebase.",
              "Grep for “utils/index” to find every file that imports the barrel file, and count each as a usage.",
              "Read every file in the repository with “utils” in its path, looking for calls to the helpers.",
              "Conclude that the module is barely used, and report the 3 matches as the complete usage list."),
        ans=0,
        explain=("Callers import the re-exported names, not the module's file, so you trace usage by first finding the exported "
                 "names and then searching for each one. B counts every importer, whether or not it uses this module's "
                 "helpers. C is slow and too narrow. D reports a false result."),
        scenarios=(4,), points=("2.5:S5",),
    ),
    Question(
        q=("A team wants Claude to always use their package manager's commands (pnpm, never npm) in every session. "
           "Separately, they have a ten-step release-notes workflow that is needed only on release days, about twice a "
           "month. Both currently sit in a 600-line CLAUDE.md. Where should each live?"),
        opts=("Both in CLAUDE.md, since everything Claude needs should be loaded at the start of every session.",
              "Both as skills, so neither takes up context until a developer or Claude decides to invoke it.",
              "The release workflow in CLAUDE.md, and the package-manager rule as a skill run before installs.",
              "The package-manager rule in CLAUDE.md, and the release workflow as a skill."),
        ans=3,
        explain=("CLAUDE.md is for rules that apply all the time. Skills are for on-demand, task-specific workflows. A loads a "
                 "twice-a-month workflow into every session. B makes an always-on rule depend on someone invoking it. C gets "
                 "the two the wrong way round."),
        scenarios=(2, 4), points=("3.2:S5",),
    ),
    Question(
        q=("A team wrote “never edit .env files” in CLAUDE.md, yet in the last month Claude edited a .env file twice while "
           "fixing configuration bugs. The team lead now wants a guarantee rather than a better-worded rule. What gives a "
           "dependable guarantee in Claude Code?"),
        opts=("A permission deny rule, or a PreToolUse hook, that blocks edits to .env files.",
              "The rule moved to the top of CLAUDE.md in capitals, so that the model gives it more weight.",
              "A path-scoped rule in .claude/rules/ that loads the instruction whenever .env files are touched.",
              "A /check-env slash command that developers run after each session to revert any .env changes."),
        ans=0,
        explain=("Permission rules and hooks are enforced by Claude Code itself, whatever the model decides. B and C are still "
                 "instructions, although C loads them at the right moment. D repairs the damage afterwards, if someone "
                 "remembers."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Claude Code on my Mac uses `grep` in Bash, not a Grep tool — is the guide wrong?",
     "The docs say the Grep and Glob tools are absent by default on macOS, Linux and WSL, where Claude runs grep and find through "
     "Bash. The exam's point is the same either way: content search vs path search."),
    ("When is replace_all right?",
     "When every occurrence should change — renaming a variable everywhere in a file, for example. Use a longer anchor, or "
     "Read + Write, when only one of several identical lines should change."),
    ("Isn't reading more files always safer?",
     "Not with a finite context. Everything read stays in the conversation. The guide's pattern — Grep for the entry point, "
     "Read along imports — keeps the context for what matters."),
    ("Built-in tool or MCP tool?",
     "Built-ins cover most coding tasks. An MCP tool earns its place when it can do something they can't, like search every "
     "repository or reach an external system. Its description must say so, or the agent reaches for Grep (TS 2.4 Skill 3)."),
)

PLAYGROUND_INTRO = """
The search tab runs whatever you type through Grep or Glob on the simulated repo, so you can see the difference. The other tabs
switch between the right and wrong way for one job. The last tab matches a need to an extension surface, using the docs'
comparison.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="builtin")


PLAYGROUND = (
    _tab("search", "⭐ Grep vs Glob", "search", "Search inside the pages, or read the spines.", "guide:2.5:K1",
         "Type text or a pattern; run it through Grep (contents) or Glob (paths).", "tools-reference § Grep, Glob",
         ("search_tool",), {"search_tool": "grep"}, ("process_refund(", "**/*.test.tsx", "needs a manager", "refund"),
         ("Grep process_refund( → the callers.", "Glob **/*.test.tsx → the test files.", "Glob refund → files NAMED refund, not callers.")),
    _tab("edit", "⭐ Edit & its fallback", "edit", "A sticker needs one exact spot.", "guide:2.5:S3",
         "Change only the [payments] timeout when “timeout = 30” appears twice.", "tools-reference § Edit; guide TS 2.5 K4, S3",
         ("edit_strategy",), {"edit_strategy": "read_write"}, ("Change the payments timeout to 60",),
         ("short anchor: Edit fails.", "longer anchor: works.", "replace_all: changes both.", "Read + Write: works.")),
    _tab("explore", "⭐ Explore incrementally", "explore", "Find the index entry, follow the references.", "guide:2.5:S4",
         "How does a refund get approved?", "guide TS 2.5 Skill 4", ("explore",), {"explore": "incremental"},
         ("How does a refund get approved?",), ("incremental: 3 files, 403 chars.", "read everything: 33 files, over the budget.")),
    _tab("wrapper", "⭐ Through a wrapper", "wrapper", "Search for the name on the shop sign.", "guide:2.5:S5",
         "Who calls the functions the payments wrapper exports?", "guide TS 2.5 Skill 5", ("wrapper_names",), {"wrapper_names": "exported"},
         ("Who uses the payments wrapper?",), ("exported names: the 3 shop files.", "original names: only legacy/old_pay.py.")),
    _tab("surface", "⭐ Which surface?", "surface", "Rules on the wall, manual on the shelf, lock on the door.", "guide:3.2:S5",
         "Match a need to CLAUDE.md, a skill, a hook, MCP or a subagent (docs' comparison).", "features-overview; guide TS 3.2 Skill 5",
         ("need", "surface"), {"need": "always_rule", "surface": "claude_md"}, ("Which surface fits?",),
         ("guardrail + CLAUDE.md: not enforced.", "deploy workflow + skill: right.", "external data + MCP: right.")),
)

CONTENT = ConceptContent(
    slug="agentic-tool-surface-selection", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("mcp", "tool-calling", "skills", "hooks"), exam_points=EXAM_POINTS, playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO, scenarios=("find_callers", "find_tests", "edit_nonunique", "trace_flow", "wrapper_usage"),
    show_ledger=False,
)
