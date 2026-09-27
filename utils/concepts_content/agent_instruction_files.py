"""
D1.7 Agent Instruction Files (CLAUDE.md / AGENTS.md) — guide TS 3.1 (CLAUDE.md hierarchy, scoping, @import, .claude/rules/,
/memory; pp.12–13). AGENTS.md is NOT in the guide: that part comes only from the official docs and is marked 📘, not gold.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-27); code.claude.com memory docs fetched 2026-09-27
(DOC_REFS). Every claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant

DOCS_VERIFIED_ON = "2026-09-27"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("How Claude remembers your project (CLAUDE.md, AGENTS.md, rules, /memory)", f"{_C}/memory"),
    DocRef("Best practices for Claude Code — write an effective CLAUDE.md", f"{_C}/best-practices"),
)

GROUNDING = (
    Claim("Scopes: user ~/.claude/CLAUDE.md (personal, all projects); project ./CLAUDE.md or ./.claude/CLAUDE.md (team-shared via "
          "version control); local ./CLAUDE.local.md (personal, add to .gitignore); plus an organisation-managed policy file.",
          "docs", "memory § Choose where to put CLAUDE.md files"),
    Claim("CLAUDE.md and CLAUDE.local.md in the working directory and above load at launch; files in subdirectories load on demand "
          "when Claude reads files there. All discovered files are concatenated, not overridden — ordered from the filesystem root "
          "down to the working directory.", "docs", "memory § How CLAUDE.md files load"),
    Claim("@path imports: relative and absolute paths; relative paths resolve relative to the file containing the import, not the "
          "working directory; imports can recurse up to four hops; imports outside the project prompt for approval the first time.",
          "docs", "memory § Import additional files"),
    Claim(".claude/rules/*.md: one topic per file; rules without `paths` frontmatter load at launch like .claude/CLAUDE.md; rules with "
          "`paths` globs load only when Claude reads matching files.", "docs", "memory § Organize rules with .claude/rules/"),
    Claim("Target under 200 lines per CLAUDE.md; longer files consume more context and reduce adherence. Be specific, structured and "
          "consistent — contradictory rules may be resolved arbitrarily.", "docs", "memory § Write effective instructions"),
    Claim("/memory lists the CLAUDE.md, CLAUDE.local.md and other memory files across user and project scopes and opens them; /context "
          "shows under Memory files which files actually loaded.", "docs", "memory § View and edit with /memory; Troubleshoot"),
    Claim("CLAUDE.md is context, not enforced configuration; it is delivered as a user message after the system prompt, with no "
          "guarantee of strict compliance — use a hook for things that must always happen.", "docs", "memory § CLAUDE.md vs auto memory; Troubleshoot"),
    Claim("AGENTS.md: by default Claude Code reads it only when there is no CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md in the "
          "working directory or above; with a CLAUDE.md present, import it (@AGENTS.md) or change the Project instructions setting. "
          "Reading AGENTS.md directly needs Claude Code v2.1.277 or later.", "docs", "memory § AGENTS.md"),
    Claim("Hierarchy: user-level ~/.claude/CLAUDE.md, project-level .claude/CLAUDE.md or root CLAUDE.md, directory-level subdirectory "
          "CLAUDE.md files.", "guide", "TS 3.1 · Knowledge 1 · pp.12–13"),
    Claim("User-level instructions apply only to that user — they are not shared with teammates through version control.",
          "guide", "TS 3.1 · Knowledge 2 · pp.12–13"),
    Claim("@import keeps CLAUDE.md modular (e.g. importing the standards relevant to each package); .claude/rules/ holds topic-specific "
          "rule files as an alternative to one monolithic CLAUDE.md.", "guide", "TS 3.1 · Knowledge 3–4 · pp.12–13"),
    Claim("Skills: diagnose hierarchy problems (a new teammate missing instructions kept at user level); @import standards per package "
          "by maintainer knowledge; split a large CLAUDE.md into .claude/rules/ topic files (testing.md, api-conventions.md, "
          "deployment.md); use /memory to see which memory files loaded.", "guide", "TS 3.1 · Skills 1–4 · pp.12–13"),
    Claim("AGENTS.md does not appear in the exam guide; this page covers it from the docs only.", "guide", "guide v1.0 (keyword search)"),
    Claim("The loader simplifies: the working directory is the repo root; managed files, claudeMdExcludes, --add-dir and the Project "
          "instructions setting aren't modelled; instructions are recognised by marker phrases.", "simulated", "utils/memory_lab.py"),
)

CORRECT = r'''from utils.memory_lab import simulate   # SIMULATED Claude Code memory loader (rules from the memory docs)

# Your OWN machine only - never shared through git. Personal preferences belong here.
USER = {"~/.claude/CLAUDE.md": "- I prefer short answers."}

# The repository - everything here except CLAUDE.local.md is committed and reaches every teammate.
REPO = {
    "CLAUDE.md": "\n".join([
        "# Project instructions (keep this file short - topic rules live in .claude/rules/)",
        "@AGENTS.md",                                        # the file other coding tools read, imported so Claude reads it too
        "- Run `pnpm test` before committing.",
    ]),
    "AGENTS.md": "- Use conventional commit messages.",
    ".claude/rules/testing.md": "# Testing\n- Every bug fix gets a regression test.",
    ".claude/rules/deployment.md": "# Deployment\n- Deploy only from main.",
    ".claude/rules/api-conventions.md": '---\npaths:\n  - "src/api/**"\n---\n# API conventions\n- Validate every request body.',
    # each package imports only the standards its maintainers chose (paths are relative to THIS file)
    "packages/billing/CLAUDE.md": "@../../standards/money.md\n- Billing owners review every change.",
    "packages/web/CLAUDE.md": "@../../standards/ui.md",
    "standards/money.md": "- Store money as integer cents.",
    "standards/ui.md": "- Use design-system components.",
}

simulate(REPO, USER)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


VARIANT_A = _swap(_swap(CORRECT, '''        "- Run `pnpm test` before committing.",\n''', ""),
                  '''USER = {"~/.claude/CLAUDE.md": "- I prefer short answers."}''',
                  '''USER = {"~/.claude/CLAUDE.md": "- I prefer short answers.\\n- Run `pnpm test` before committing."}   # WRONG: a TEAM rule at user level''')
VARIANT_B = _swap(_swap(_swap(CORRECT, '''        "- Run `pnpm test` before committing.",\n''',
                              '''        "- Run `pnpm test` before committing.",\n        "@standards/money.md",   # WRONG: every standard imported for every package\n        "@standards/ui.md",\n'''),
                        '''    "packages/billing/CLAUDE.md": "@../../standards/money.md\\n- Billing owners review every change.",\n''', ""),
                  '''    "packages/web/CLAUDE.md": "@../../standards/ui.md",\n''', "")
VARIANT_C = _swap(CORRECT, '''    ".claude/rules/testing.md": "# Testing\\n- Every bug fix gets a regression test.",
    ".claude/rules/deployment.md": "# Deployment\\n- Deploy only from main.",
    ".claude/rules/api-conventions.md": '---\\npaths:\\n  - "src/api/**"\\n---\\n# API conventions\\n- Validate every request body.',''',
                  '''    # WRONG: one monolithic CLAUDE.md - every topic in one ever-growing file (appended below)''')
VARIANT_C = _swap(VARIANT_C, "\nsimulate(REPO, USER)", '''
REPO["CLAUDE.md"] += "\\n".join(["", "# Testing", "- Every bug fix gets a regression test.", "# Deployment", "- Deploy only from main.",
                                "# API conventions", "- Validate every request body."]
                               + [f"- detailed guideline {i}" for i in range(1, 251)])   # ...and it keeps growing

simulate(REPO, USER)''')
VARIANT_D = _swap(CORRECT, '''        "@AGENTS.md",                                        # the file other coding tools read, imported so Claude reads it too\n''',
                  '''        # WRONG: a new CLAUDE.md, but AGENTS.md is not imported\n''')
VARIANT_E = _swap(_swap(CORRECT, '''        "- Run `pnpm test` before committing.",\n''', ""),
                  '''    "AGENTS.md":''', '''    "CLAUDE.local.md": "- Run `pnpm test` before committing.",   # WRONG: a TEAM rule in the personal, gitignored file
    "AGENTS.md":''')
VARIANT_F = _swap(CORRECT, '''"packages/billing/CLAUDE.md": "@../../standards/money.md''',
                  '''"packages/billing/CLAUDE.md": "@standards/money.md''')
VARIANT_F = _swap(VARIANT_F, "    # each package imports only the standards its maintainers chose (paths are relative to THIS file)",
                  "    # WRONG in billing: the import path is written relative to the repo root, not to the importing file")


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "memory_check"]
    return ev[-1] if ev else None


EXPECTED = {
    "new_teammate": "a teammate on a fresh clone receives the team rule (pnpm test)",
    "package_standards": "billing gets the money standard only; web gets the UI standard only",
    "split_rules": "no CLAUDE.md over 200 lines; testing + deployment rules at launch; API rule only when editing src/api",
    "agents_md": "the AGENTS.md rule (conventional commits) still reaches Claude now that a CLAUDE.md exists",
}


def check_outcome(scenario, trace):
    e = _facts(trace)
    if e is None:
        return False, EXPECTED[scenario], f"simulate() was not called ({trace['status']['raised'] or 'no result'})"
    extra = f" · missing imports: {e['missing_imports']}" if e["missing_imports"] else ""
    return bool(e["ok"]) and not trace["status"]["raised"], EXPECTED[scenario], e["detail"] + extra


_CONCEPT = {
    "user":   ("#EDE9FE", "#7C3AED", "user scope — this person only"),
    "proj":   ("#DBEAFE", "#0066CC", "project scope — shared through git"),
    "lazy":   ("#FEF3C7", "#D97706", "loads on demand (subdirectory files, path-scoped rules)"),
    "ctx":    ("#D1FAE5", "#059669", "what ends up in Claude's context"),
    "docs":   ("#F3F4F6", "#6B7280", "📘 docs-only (not in the exam guide)"),
    "bug":    ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "USER":   ("⭐ ~/.claude/CLAUDE.md\\nyour machine only", "box", "user"),
    "LOCAL":  ("CLAUDE.local.md\\npersonal, gitignored", "box", "user"),
    "PROJ":   ("⭐ ./CLAUDE.md or\\n./.claude/CLAUDE.md\\n(checked in)", "box", "proj"),
    "RULES":  ("⭐ .claude/rules/*.md\\n(no paths: at launch)", "box", "proj"),
    "AGENTS": ("AGENTS.md\\n(read only if no CLAUDE.md —\\nor via @AGENTS.md)", "box", "docs"),
    "IMPORT": ("⭐ @import\\n(relative to the importing file)", "box", "proj"),
    "SUB":    ("⭐ subdirectory CLAUDE.md\\n(when Claude reads files there)", "box", "lazy"),
    "PATHR":  ("path-scoped rule\\n(paths: glob matched)", "box", "lazy"),
    "CTX":    ("Session context\\n(check with /memory)", "box", "ctx"),
    "USERBUG": ("✗ team rule at user level", "box", "bug"),
    "LOCALBUG": ("✗ team rule in CLAUDE.local.md", "box", "bug"),
    "ROOTIMP": ("✗ every standard imported\\nat the root", "box", "bug"),
    "MONO":   ("✗ one monolithic CLAUDE.md", "box", "bug"),
    "NOAG":   ("✗ CLAUDE.md added,\\nAGENTS.md not imported", "box", "bug"),
    "BADPATH": ("✗ import path relative\\nto the repo root", "box", "bug"),
}
_BUGS = ["USERBUG", "LOCALBUG", "ROOTIMP", "MONO", "NOAG", "BADPATH"]
_EXP = {"new_teammate": ["PROJ"], "package_standards": ["SUB", "IMPORT"], "split_rules": ["RULES", "PATHR"], "agents_md": ["AGENTS", "IMPORT"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 3.1, pp.12–13)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = what this scenario '
                 'relies on · <B>red</B> = the bug your layout shows · grey = not involved</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3"><TR><TD COLSPAN="2" '
            'BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states):
    hl = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.25; ranksep=0.55; newrank=true;',
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
    lines.append('  USER -> CTX [label="launch"]; LOCAL -> CTX [label="launch"]; PROJ -> CTX [label="launch"]; RULES -> CTX [label="launch"];')
    lines.append('  AGENTS -> CTX [style=dashed]; PROJ -> IMPORT [label="@"]; SUB -> IMPORT [label="@"]; IMPORT -> CTX;')
    lines.append('  SUB -> CTX [label="on demand"]; PATHR -> CTX [label="on demand"];')
    lines.append("  { rank=same; USER; LOCAL; PROJ; RULES; AGENTS; SUB; PATHR; }")
    lines.append("  { rank=same; " + "; ".join(_BUGS) + "; }")
    lines.append("  CTX -> USERBUG [style=invis];")
    lines.append(_key(hl))
    lines.append("  BADPATH -> KEY [style=invis];")
    lines.append("}")
    return "\n".join(lines)


def _bug(e):
    if e["missing_imports"]:
        return "BADPATH"
    sc = e["scenario"]
    if sc == "new_teammate":
        return "LOCALBUG" if (e.get("team_rule_where") or "").endswith("CLAUDE.local.md") else "USERBUG"
    return {"package_standards": "ROOTIMP", "split_rules": "MONO"}.get(sc, "NOAG")


def node_states(trace):
    if not trace:
        return {}
    e = _facts(trace)
    if e is None:
        return {}
    s = {"CTX": ("ok", "") if e["ok"] else ("bad", "missing or extra rules")}
    for n in _EXP.get(e["scenario"], []):
        s[n] = ("ok", "" if e["ok"] else "should carry it")
    if not e["ok"]:
        s[_bug(e)] = ("bad", "your layout")
    return s


EXAM_POINTS = (
    ExamPoint("3.1", "K", 1, "The hierarchy: user-level ~/.claude/CLAUDE.md, project-level .claude/CLAUDE.md or root CLAUDE.md, and "
              "directory-level CLAUDE.md files in subdirectories.", "✅ REPO/USER layout · flowchart · playground “Hierarchy”"),
    ExamPoint("3.1", "K", 2, "User-level instructions apply only to that user — they don't reach teammates through version control.",
              "❌ A · playground “Hierarchy”"),
    ExamPoint("3.1", "K", 3, "@import references external files to keep CLAUDE.md modular (e.g. the standards relevant to each package).",
              "✅ packages/*/CLAUDE.md · ❌ B · playground “@import”"),
    ExamPoint("3.1", "K", 4, ".claude/rules/ organises topic-specific rule files as an alternative to one monolithic CLAUDE.md.",
              "✅ .claude/rules/ · ❌ C · playground “Rules”"),
    ExamPoint("3.1", "S", 1, "Diagnose hierarchy issues — e.g. a new teammate not getting instructions that live at user level.",
              "✅ new_teammate · ❌ A · playground “/memory”"),
    ExamPoint("3.1", "S", 2, "Use @import to include just the standards each package needs, based on its maintainers' knowledge.",
              "✅ package_standards · ❌ B"),
    ExamPoint("3.1", "S", 3, "Split a large CLAUDE.md into focused .claude/rules/ files (testing.md, api-conventions.md, deployment.md).",
              "✅ split_rules · ❌ C"),
    ExamPoint("3.1", "S", 4, "Use /memory to check which memory files loaded and diagnose inconsistent behaviour across sessions.",
              "the printed “/memory” views in every lab run · playground “/memory”"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ Right scope, modular, path-scoped", "correct", CORRECT, "new_teammate",
            observe=("Each lab run prints a “/memory” view for four sessions. A teammate at the root gets CLAUDE.md (with AGENTS.md "
                     "imported) plus the testing and deployment rules; editing billing adds packages/billing/CLAUDE.md and "
                     "standards/money.md; editing src/api adds the path-scoped API rule. Your own session also shows your "
                     "~/.claude/CLAUDE.md — the teammate's doesn't."),
            why=("Team rules live in checked-in files; personal ones in user scope; packages import only their standards with "
                 "paths relative to the importing file; topics sit in .claude/rules/ with the API rule path-scoped.")),
    Variant("A", "⭐❌ A — the team rule lives in ~/.claude/CLAUDE.md", "distractor", VARIANT_A, "new_teammate",
            observe="Your session has the pnpm test rule; the teammate's /memory view doesn't — their clone has no such file.",
            why="User-level instructions are on your machine only; version control never carries them to teammates.",
            fix="Move team rules into the project CLAUDE.md (or .claude/CLAUDE.md / .claude/rules/).", source="guide:3.1:K2"),
    Variant("B", "⭐❌ B — import every standard at the root", "distractor", VARIANT_B, "package_standards",
            observe="Both money.md and ui.md load at launch for everyone: a web edit carries the billing money rule, and vice versa.",
            why="The guide's pattern is selective: each package's CLAUDE.md imports the standards its maintainers know it needs.",
            fix="Put an @import in each package's CLAUDE.md for just its standards.", source="guide:3.1:S2"),
    Variant("C", "⭐❌ C — one monolithic CLAUDE.md", "distractor", VARIANT_C, "split_rules",
            observe=("CLAUDE.md grows to ~260 lines (the docs target under 200), and the API rule loads at launch for every task, "
                     "not just src/api work."),
            why=("Long files consume more context and reduce adherence (docs); .claude/rules/ splits topics into focused files and "
                 "path-scoped rules load only when relevant."),
            fix="Split into .claude/rules/testing.md, api-conventions.md (with paths: src/api/**), deployment.md.", source="guide:3.1:S3"),
    Variant("D", "❌ D — add a CLAUDE.md but don't import AGENTS.md", "distractor", VARIANT_D, "agents_md",
            observe="The conventional-commit rule from AGENTS.md disappears: with a CLAUDE.md present, AGENTS.md isn't read by default.",
            why="Per the docs, Claude reads AGENTS.md only when there's no CLAUDE.md / .claude/CLAUDE.md / CLAUDE.local.md in the "
                "working directory or above.",
            fix="Import it: put @AGENTS.md in CLAUDE.md (or change the Project instructions setting).", source="docs"),
    Variant("E", "❌ E — a team rule in CLAUDE.local.md", "distractor", VARIANT_E, "new_teammate",
            observe="It works on your machine; the teammate's clone doesn't have CLAUDE.local.md, so they never get the rule.",
            why="CLAUDE.local.md is for personal project preferences and belongs in .gitignore — it doesn't travel.",
            fix="Team rules go in the checked-in CLAUDE.md.", source="docs"),
    Variant("F", "❌ F — an import path relative to the repo root", "distractor", VARIANT_F, "package_standards",
            observe=("packages/billing/CLAUDE.md imports @standards/money.md, which resolves to packages/billing/standards/money.md — "
                     "not found. The billing session loads without the money standard."),
            why="Relative import paths resolve relative to the file that contains the import, not the working directory (docs).",
            fix="Write @../../standards/money.md, or an absolute path.", source="docs"),
)

TLDR = (
    "Instruction files are **context Claude reads**, and *where* a file lives decides **who** gets it and **when**. "
    "`~/.claude/CLAUDE.md` is yours alone; the project `CLAUDE.md` (or `.claude/CLAUDE.md`) is shared through git; a subdirectory's "
    "`CLAUDE.md` loads when Claude works in that folder. Keep files modular with **`@import`** and split topics into **`.claude/rules/`** "
    "(path-scoped when they only matter for some files). When behaviour differs between people, **`/memory`** shows what actually loaded. "
    "AGENTS.md isn't in the exam guide — the docs say Claude reads it only when there's no CLAUDE.md, unless you import it."
)
MENTAL_MODEL = ("Instruction files are notices on walls: the one on your fridge (user) only you see; the one in the office lobby "
                "(project) everyone sees; the one on a lab door (subdirectory) you see when you walk into that lab — and /memory is "
                "the walk-around that shows which notices a given person actually passed.")

WHAT_IT_IS = """
The exam guide covers CLAUDE.md scoping and organisation in Guide §6 · TS 3.1 (pp.12–13). The Claude Code memory docs describe how files
load. AGENTS.md is docs-only (📘, not gold).

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | Source |
|---|---|---|---|
| 1 | User scope `~/.claude/CLAUDE.md` | The note on your own fridge: nobody else walks into your kitchen. | ⭐ TS 3.1 · Knowledge 1–2 · pp.12–13 |
| 2 | Project scope `CLAUDE.md` / `.claude/CLAUDE.md` | The notice in the office lobby — everyone who comes in (clones) sees it. | ⭐ TS 3.1 · Knowledge 1 · pp.12–13 |
| 3 | Directory scope (subdirectory `CLAUDE.md`) | A sign on the lab door: you read it when you walk into that lab. | ⭐ TS 3.1 · Knowledge 1 · pp.12–13 |
| 4 | `@import` | A notice that says “see binder 3”: the binder is fetched and read with it — found relative to where the notice hangs. | ⭐ TS 3.1 · Knowledge 3, Skill 2 · pp.12–13 |
| 5 | `.claude/rules/` | Filing by topic instead of one thick manual — and some folders open only in the room they're about (`paths`). | ⭐ TS 3.1 · Knowledge 4, Skill 3 · pp.12–13 |
| 6 | `/memory` | A walk-around audit: which notices did this person actually pass? | ⭐ TS 3.1 · Skill 4 · pp.12–13 |
| 7 | `CLAUDE.local.md` | A sticky note on your own desk in the office — it doesn't get photocopied for others. | 📘 docs |
| 8 | AGENTS.md | The same notice written for a different visitor; Claude reads it when there's no CLAUDE.md, or when CLAUDE.md points to it. | 📘 docs (not in the guide) |

**The scopes** (docs)

| # | File | Who gets it | Committed? | Loads |
|---|---|---|---|---|
| 1 | `~/.claude/CLAUDE.md` | only you, in every project | no | at launch |
| 2 | `./CLAUDE.md` or `./.claude/CLAUDE.md` | everyone on the project | yes | at launch |
| 3 | `./CLAUDE.local.md` | only you, in this project | no (add to `.gitignore`) | at launch |
| 4 | `sub/dir/CLAUDE.md` | everyone | yes | when Claude reads files in `sub/dir/` |
| 5 | `.claude/rules/x.md` (no `paths`) | everyone | yes | at launch |
| 6 | `.claude/rules/x.md` with `paths:` | everyone | yes | when Claude reads a matching file |
| 7 | `AGENTS.md` | everyone | yes | only if no CLAUDE.md above, or via `@AGENTS.md` |

Files **add up**; they don't override each other — ordered from the root down to the working directory. CLAUDE.md is context, not
enforcement: for something that must always happen, the docs point to hooks.
"""

HOW_IT_WORKS = """
1. **Team rules → project `CLAUDE.md`** (or `.claude/CLAUDE.md`), committed. **Personal preferences → `~/.claude/CLAUDE.md`**, or
   `CLAUDE.local.md` for one project.
2. **Keep the root file short** (the docs target under 200 lines). Move topics into **`.claude/rules/`** — `testing.md`,
   `api-conventions.md`, `deployment.md`.
3. **Path-scope** rules that only matter for some files (`paths: ["src/api/**"]`), so they load only there.
4. **Per package, `@import`** just the standards its maintainers chose — with paths relative to the importing file.
5. **AGENTS.md already there?** Add `@AGENTS.md` to your CLAUDE.md, or Claude won't read it once a CLAUDE.md exists.
6. **Behaviour differs between people or sessions?** Run **`/memory`** (and `/context`) to see which files actually loaded.
"""

WHERE_SEEN = """
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): “CLAUDE.md configurations” for a team's workflow.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): configuring Claude Code across a codebase and its packages.
- **This workbench itself:** this repo's own CLAUDE.md is a project file; your ~/.claude/CLAUDE.md holds your personal profile.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 3.1 (pp.12–13) and the Claude Code memory docs (verified 2026-09-27). AGENTS.md parts "
              "are docs-only. Section layout inspired by a community concept list (claudearchitectcertification.com — community source, "
              "unverified; no text copied).")

LAB_INTRO = """
You design a repository's **instruction files** (`REPO`) and your own user file (`USER`). A **simulated** loader applies the memory docs'
rules and prints a **/memory view** for four sessions: you at the root, a teammate on a fresh clone, the teammate editing billing, and
editing src/api. Four situations are checked. Three mistakes come from the exam guide (⭐), three from the docs.
"""

DISTRACTORS = (
    ("A · Team rule in ~/.claude/CLAUDE.md", "It works when I use Claude.",
     "It's on your machine only — a new teammate never gets it.", "Project CLAUDE.md, committed.", "guide:3.1:K2"),
    ("B · Import every standard at the root", "One place to see all standards.",
     "Every package loads every standard — noise and conflicts.", "@import per package.", "guide:3.1:S2"),
    ("C · One monolithic CLAUDE.md", "Everything in one place is easy to find.",
     "Over 200 lines, lower adherence; path-specific rules load everywhere.", ".claude/rules/ topic files, path-scoped where useful.", "guide:3.1:S3"),
    ("D · CLAUDE.md added, AGENTS.md not imported", "Claude reads AGENTS.md anyway.",
     "Only when there's no CLAUDE.md; now it's skipped.", "@AGENTS.md in CLAUDE.md.", "docs"),
    ("E · Team rule in CLAUDE.local.md", "It's in the project folder.",
     "It's personal and gitignored; teammates don't have it.", "The checked-in CLAUDE.md.", "docs"),
    ("F · Import path relative to the repo root", "Paths usually start at the root.",
     "Imports resolve relative to the importing file — not found.", "@../../standards/money.md", "docs"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "User ~/.claude/CLAUDE.md", "Project CLAUDE.md", "Subdirectory CLAUDE.md", ".claude/rules/*.md")
SIDE_BY_SIDE_ROWS = (
    ("1", "Shared with teammates", "No", "Yes (git)", "Yes (git)", "Yes (git)"),
    ("2", "When it loads", "Launch, every project", "Launch", "When Claude reads files in that folder", "Launch — or on matching files with `paths`"),
    ("3", "Best for", "Personal preferences", "Team-wide rules, kept short", "Package/folder-specific rules", "One topic per file"),
    ("4", "Typical mistake", "Team rules put here", "Grows into a monolith", "Import paths written from the root", "Forgetting `paths` for area-specific rules"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=11, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=10, color="#6B7280"];
  Q1 [shape=diamond, label="Should teammates\\nget this rule?"];
  U [shape=box, fillcolor="#EDE9FE", color="#7C3AED", label="~/.claude/CLAUDE.md\\n(or CLAUDE.local.md for one project)"];
  Q2 [shape=diamond, label="Only for one package\\nor folder?"];
  S [shape=box, fillcolor="#FEF3C7", color="#D97706", label="That folder's CLAUDE.md\\n(+ @import its standards)"];
  Q3 [shape=diamond, label="Only for some file types\\nor paths?"];
  R [shape=box, fillcolor="#FEF3C7", color="#D97706", label=".claude/rules/topic.md\\nwith paths: frontmatter"];
  Q4 [shape=diamond, label="Is the root file getting\\nlong (> ~200 lines)?"];
  T [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Topic files in .claude/rules/"];
  P [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Project CLAUDE.md"];
  Q1 -> U [label="no"]; Q1 -> Q2 [label="yes"]; Q2 -> S [label="yes"]; Q2 -> Q3 [label="no"];
  Q3 -> R [label="yes"]; Q3 -> Q4 [label="no"]; Q4 -> T [label="yes"]; Q4 -> P [label="no"];
}'''

EXPERIMENTS = (
    "Run ✅ and read the four /memory views: which files does the teammate get that you also get, and which only you?",
    "Run ⭐❌ A, then move the pnpm line back into REPO['CLAUDE.md'] and run again.",
    "In ✅, remove the `paths:` block from api-conventions.md and run split_rules: where does the API rule load now?",
    "Run ❌ F and read the “FILE NOT FOUND” line in the billing /memory view — then fix the path.",
    "In ✅, delete the whole CLAUDE.md entry and run agents_md: AGENTS.md is read on its own again.",
)

QUESTIONS = (
    Question(
        q=("A new team member says Claude Code ignores the team's conventions (always run the linter, use pnpm). Experienced engineers "
           "don't see the problem. The conventions were written into a senior engineer's ~/.claude/CLAUDE.md months ago. What's the root cause?"),
        opts=("The new member's Claude Code version is out of date.",
              "The conventions are in user-level configuration, which isn't shared through version control.",
              "The conventions file is longer than 200 lines.",
              "The project needs a .claude/rules/ directory before CLAUDE.md is read."),
        ans=1,
        explain="User-level instructions apply only to that user. Team conventions belong in the project CLAUDE.md, which travels with the repo.",
        scenarios=(2,), ts="3.1"),
    Question(
        q=("In a monorepo, the payments package must follow money-handling standards and the frontend package must follow UI standards. "
           "Both standards documents already exist. What is the most maintainable setup?"),
        opts=("Paste both standards into the root CLAUDE.md.",
              "In each package's CLAUDE.md, @import only the standards file that package needs.",
              "Put both standards in every developer's ~/.claude/CLAUDE.md.",
              "Ask developers to mention the standards in each prompt."),
        ans=1,
        explain="The guide's pattern: @import selectively per package, based on maintainer knowledge — modular, and each package gets only what applies.",
        scenarios=(2, 4), ts="3.1"),
    Question(
        q=("A project's CLAUDE.md has grown to 700 lines covering testing, API conventions and deployment, and Claude is following it "
           "less consistently. What change fits best?"),
        opts=("Move the whole file to ~/.claude/CLAUDE.md.",
              "Split it into focused files in .claude/rules/ (e.g. testing.md, api-conventions.md, deployment.md).",
              "Repeat the most important rules at the top and bottom.",
              "Delete the file and rely on prompts."),
        ans=1,
        explain=".claude/rules/ is the guide's alternative to a monolithic CLAUDE.md; the docs add that long files reduce adherence and that path-scoped rules load only when relevant.",
        scenarios=(2,), ts="3.1"),
    Question(
        q=("Two developers on the same repo see Claude Code behave differently on the same task. What's the most direct first diagnostic step?"),
        opts=("Reinstall Claude Code on both machines.",
              "Run /memory (and check /context) on both to compare which memory files are loaded.",
              "Switch both to plan mode.",
              "Delete the project CLAUDE.md."),
        ans=1,
        explain="The guide's skill: use /memory to verify which memory files are loaded and diagnose inconsistent behaviour across sessions.",
        scenarios=(2,), ts="3.1"),
    Question(
        q=("A repository has an AGENTS.md used by other coding tools. The team adds a CLAUDE.md with Claude-specific notes, and Claude "
           "stops following AGENTS.md. Per the docs, why?"),
        opts=("AGENTS.md is never read by Claude Code.",
              "By default Claude reads AGENTS.md only when there's no CLAUDE.md; with one present, import it (@AGENTS.md) or change the setting.",
              "AGENTS.md must be in .claude/.",
              "CLAUDE.md overrides AGENTS.md line by line."),
        ans=1,
        explain="The memory docs: AGENTS.md is read by default only when no CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md is present above.",
        basis="docs", in_bank=False),
)

FAQ = (
    ("Do files override each other?",
     "No — per the docs, all discovered files are concatenated, ordered from the filesystem root down to the working directory. If two "
     "files contradict, Claude may pick one arbitrarily, so remove conflicts."),
    ("Is CLAUDE.md enforced?",
     "No. It's context delivered after the system prompt, and Claude tries to follow it. For something that must happen every time, the "
     "docs point to hooks (see D1.5)."),
    ("./CLAUDE.md or ./.claude/CLAUDE.md?",
     "Either is a project file (guide and docs). Rules without `paths` in .claude/rules/ load with the same priority as .claude/CLAUDE.md."),
    ("Is AGENTS.md on the exam?",
     "It isn't in guide v1.0. It's here because the docs describe it and real repos have it."),
    ("How is this related to 3.1 in the phases?",
     "The phase page 3.1 (Claude Code Configuration, Domain 3) covers the same task statement; the community concept list files it under "
     "D1.7. The guide reference is TS 3.1 either way."),
)

PLAYGROUND_INTRO = """
Type the **file Claude opens** (for example `packages/billing/invoice.py` or `src/api/orders.ts`), pick **who** is running Claude Code
and how the files are arranged, and see the **/memory view**: every instruction file that loads, and why.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="memory")


PLAYGROUND = (
    _tab("hierarchy", "⭐ Hierarchy", "hierarchy",
         "Your fridge, the office lobby, the lab door — each notice reaches a different set of people.", "guide:3.1:K2",
         "Put the team rule (pnpm test) in the project file, your user file or CLAUDE.local.md, and compare you vs a teammate.",
         "memory § Choose where to put CLAUDE.md files; guide TS 3.1 Knowledge 1–2, Skill 1",
         ("team_rule_in", "persona"), {"team_rule_in": "project", "persona": "teammate"}, ("README.md",),
         ("project: both of you get it.", "user: only you.", "local: only you — it's gitignored.")),
    _tab("imports", "⭐ @import", "imports",
         "“See binder 3” — fetched with the notice, found relative to where the notice hangs.", "guide:3.1:S2",
         "Where the standards are imported (per package or all at the root) and how the path is written.",
         "memory § Import additional files; guide TS 3.1 Knowledge 3, Skill 2",
         ("import_at", "import_path"), {"import_at": "package", "import_path": "relative_to_file"}, ("packages/billing/invoice.py", "packages/web/page.tsx"),
         ("Per package, relative to the file: billing gets money.md only.",
          "At the root: web also gets money.md.", "Path relative to the repo root: FILE NOT FOUND.")),
    _tab("rules", "⭐ Rules", "rules",
         "File by topic instead of one thick manual — and some folders only open in the room they're about.", "guide:3.1:S3",
         "One monolithic CLAUDE.md, or topic files in .claude/rules/ — with or without `paths` on the API rule.",
         "memory § Organize rules with .claude/rules/; Write effective instructions; guide TS 3.1 Knowledge 4, Skill 3",
         ("layout", "api_paths"), {"layout": "rules", "api_paths": "yes"}, ("src/api/orders.ts", "README.md"),
         ("Rules + paths: the API rule loads only for src/api files.", "Rules without paths: it loads everywhere.",
          "Monolith: one ~260-line file, everything always loaded.")),
    _tab("memory", "⭐ /memory", "memory",
         "A walk-around audit: which notices did this person actually pass?", "guide:3.1:S4",
         "The same repository, seen by two people. Change who is running Claude Code and which file is open.",
         "memory § View and edit with /memory; Troubleshoot; guide TS 3.1 Skill 4",
         ("persona",), {"persona": "you"}, ("packages/billing/invoice.py", "src/api/orders.ts"),
         ("you: your ~/.claude/CLAUDE.md appears.", "teammate: it doesn't — the difference in behaviour starts here.")),
    _tab("agents", "AGENTS.md", "agents",
         "The same notice written for a different visitor — read when there's no CLAUDE.md, or when CLAUDE.md points to it.", "",
         "📘 Docs only (not in the exam guide). Does the repo have a CLAUDE.md, and does it import AGENTS.md?",
         "memory § AGENTS.md",
         ("claude_md",), {"claude_md": "imports"}, ("README.md",),
         ("No CLAUDE.md: AGENTS.md is read on its own.", "CLAUDE.md without the import: AGENTS.md is skipped.",
          "CLAUDE.md with @AGENTS.md: both.")),
)

CONTENT = ConceptContent(
    slug="agent-instruction-files", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("session-state", "subagents", "escalation"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("new_teammate", "package_standards", "split_rules", "agents_md"), show_ledger=False,
)
