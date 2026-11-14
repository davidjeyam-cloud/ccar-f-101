"""
D3.1 CLAUDE.md Hierarchy — where instructions live (user / project / directory, .claude/rules/) and path-specific rules that
load only for matching files. Guide TS 3.1 (pp.12–13) and TS 3.3 (pp.13–14). D1.7 (Agent Instruction Files) covers @import,
modular packages and AGENTS.md; this page focuses on the hierarchy and conditional (path-scoped) loading.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); memory docs re-fetched 2026-09-28 (DOC_REFS). Every
claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("How Claude remembers your project — CLAUDE.md locations, loading, .claude/rules/, path-specific rules", f"{_C}/memory"),
    DocRef("Extend Claude Code — CLAUDE.md vs rules vs skills", f"{_C}/features-overview"),
)

GROUNDING = (
    Claim("CLAUDE.md locations: managed policy (all users in the organisation), user ~/.claude/CLAUDE.md (just you, all projects), "
          "project ./CLAUDE.md or ./.claude/CLAUDE.md (team, via source control), local ./CLAUDE.local.md (just you, this project).",
          "docs", "memory § Choose where to put CLAUDE.md files"),
    Claim("Files in the directory hierarchy above the working directory load at launch; CLAUDE.md files in subdirectories load "
          "on demand when Claude reads files in those subdirectories.", "docs", "memory § How CLAUDE.md files load"),
    Claim(".claude/rules/*.md are discovered recursively; rules without `paths` load at launch with the same priority as "
          ".claude/CLAUDE.md; rules with `paths` globs apply only when Claude works with matching files.", "docs", "memory § Organize rules"),
    Claim("Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use.", "docs", "memory § Path-specific rules"),
    Claim("Glob examples: **/*.ts = TypeScript files in any directory; src/**/* = all files under src/; *.md = Markdown files in "
          "the project ROOT; brace expansion like src/**/*.{ts,tsx} is supported.", "docs", "memory § Path-specific rules"),
    Claim("`paths` is the only frontmatter field Claude Code reads from a rule; any other field is ignored without an error; "
          "frontmatter that doesn't parse is ignored and the rule loads as if it had no paths.", "docs", "memory § rule frontmatter"),
    Claim("Personal rules in ~/.claude/rules/ apply to every project on that machine.", "docs", "memory § User-level rules"),
    Claim("Target under 200 lines per CLAUDE.md; use path-scoped rules so instructions load only when relevant; imported files "
          "still load at launch.", "docs", "memory § Write effective instructions"),
    Claim("CLAUDE.md is context, not enforced configuration — to block an action regardless, use a PreToolUse hook; run /context "
          "or /memory to check which memory files loaded.", "docs", "memory § CLAUDE.md vs auto memory; Troubleshoot"),
    Claim("Hierarchy: user-level (~/.claude/CLAUDE.md), project-level (.claude/CLAUDE.md or root CLAUDE.md), directory-level "
          "(subdirectory CLAUDE.md); user-level instructions are not shared with teammates; @import keeps CLAUDE.md modular; "
          ".claude/rules/ organises topic-specific files.", "guide", "TS 3.1 · Knowledge 1–4 · p.12"),
    Claim("Diagnose hierarchy issues (a teammate missing instructions kept at user level); @import per package; split large "
          "files into .claude/rules/; use /memory to verify which files loaded.", "guide", "TS 3.1 · Skills 1–4 · pp.12–13"),
    Claim(".claude/rules/ files with YAML `paths` globs load conditionally — only for matching files — reducing irrelevant "
          "context; glob rules beat directory CLAUDE.md files for conventions spread across directories (e.g. test files).",
          "guide", "TS 3.3 · Knowledge 1–3 · p.13"),
    Claim("Skills: rules scoped with paths such as [\"terraform/**/*\"]; glob patterns by file type regardless of directory "
          "(**/*.test.tsx); choose path-specific rules over subdirectory CLAUDE.md when conventions span the codebase.",
          "guide", "TS 3.3 · Skills 1–3 · pp.13–14"),
    Claim("The guide says path-scoped rules load 'when editing matching files'; the docs say they trigger when Claude READS a "
          "matching file. The lab follows the docs (reading a file you're about to edit triggers it).", "guide", "TS 3.3 K2 vs memory"),
    Claim("The repository, sessions and marker phrases are invented.", "simulated", "utils/rules_lab.py, utils/memory_lab.py"),
)

CORRECT = r'''from utils.rules_lab import simulate   # SIMULATED sessions on the memory loader (rules from the memory docs)

REPO = {   # checked into git - every teammate gets these
    "CLAUDE.md": "# Project\n- Run pnpm test before committing.\n",
    # a convention for TEST FILES, wherever they live -> a path-scoped rule with a ** glob
    ".claude/rules/testing.md": '---\npaths:\n  - "**/*.test.tsx"\n---\n# Test files\n- Structure every test as arrange-act-assert.\n',
    # Terraform conventions only matter when working on Terraform -> scoped to that tree
    ".claude/rules/terraform.md": '---\npaths:\n  - "terraform/**/*"\n---\n# Terraform\n- Pin provider versions.\n',
    # the team's API rule lives in the PROJECT, so a teammate's fresh clone has it
    ".claude/rules/api.md": '---\npaths: "src/api/**"\n---\n# API\n- Validate every request body.\n',
}
USER = {   # ~/.claude/ on YOUR machine only - personal preferences
    "~/.claude/CLAUDE.md": "- I like short answers.\n",
}

simulate(REPO, USER)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


_TEST = '''    ".claude/rules/testing.md": '---\\npaths:\\n  - "**/*.test.tsx"\\n---\\n# Test files\\n- Structure every test as arrange-act-assert.\\n','''
_TF = '''    ".claude/rules/terraform.md": '---\\npaths:\\n  - "terraform/**/*"\\n---\\n# Terraform\\n- Pin provider versions.\\n','''
_API = '''    ".claude/rules/api.md": '---\\npaths: "src/api/**"\\n---\\n# API\\n- Validate every request body.\\n','''

# ⭐ TS 3.3 · Skill 3 / Knowledge 3 — a directory CLAUDE.md for a convention that spans directories
VARIANT_A = _swap(CORRECT, _TEST, '''    "src/web/CLAUDE.md": "# Web\\n- Structure every test as arrange-act-assert.\\n",   # WRONG: only loads for files under src/web/''')
# ⭐ TS 3.3 · Knowledge 2 / Skill 1 — no paths: loaded in every session
VARIANT_B = _swap(CORRECT, _TF, '''    ".claude/rules/terraform.md": "# Terraform\\n- Pin provider versions.\\n",   # WRONG: no paths - loads in every session''')
# ⭐ TS 3.1 · Skill 1 / Knowledge 2 — the team rule kept at user level
VARIANT_C = _swap(_swap(CORRECT, _API, ""), '''    "~/.claude/CLAUDE.md": "- I like short answers.\\n",''',
                  '''    "~/.claude/CLAUDE.md": "- I like short answers.\\n",
    "~/.claude/rules/api.md": "# API\\n- Validate every request body.\\n",   # WRONG: a TEAM rule on one person's machine''')
# 📘 docs — `*` only matches in the project root
VARIANT_D = _swap(CORRECT, '''  - "**/*.test.tsx"''', '''  - "*.test.tsx"''')
VARIANT_D = _swap(VARIANT_D, "# a convention for TEST FILES, wherever they live -> a path-scoped rule with a ** glob",
                  "# WRONG: *.test.tsx only matches test files in the project ROOT")
# 📘 docs — `paths` misspelled: the field is ignored, the rule loads everywhere
VARIANT_E = _swap(CORRECT, _TF, '''    ".claude/rules/terraform.md": '---\\npath:\\n  - "terraform/**/*"\\n---\\n# Terraform\\n- Pin provider versions.\\n',   # WRONG: "path", not "paths"''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "rules_sessions"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "simulate() was never called"
    txt = " · ".join(f"[{x['session']}] loaded {[p for p, _w in x['loaded']]} → {'OK' if x['ok'] else 'WRONG'}" for x in r["rows"])
    if r["ok"]:
        return True, None, txt
    if sc == "test_convention":
        dir_md = any(p.endswith("/CLAUDE.md") and p != "CLAUDE.md" for p in r["repo_files"])
        return False, ("DIRMD" if dir_md else "ROOTGLOB"), txt
    if sc == "terraform_scoped":
        return False, "NOPATHS", txt
    return False, "USERLEVEL", txt


EXPECTED = {
    "test_convention": "the test convention loads for test files in src/web AND src/api — and not for src/api/orders.ts",
    "terraform_scoped": "the Terraform rule loads for terraform/… and NOT while editing src/web/App.tsx",
    "teammate_api": "a teammate's fresh clone gets the API rule (and the root team rule) when editing src/api/",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":     ("#EDE9FE", "#7C3AED", "the decision"),
    "scope": ("#DBEAFE", "#0066CC", "who gets it (hierarchy)"),
    "cond":  ("#CCFBF1", "#0D9488", "when it loads (conditional)"),
    "bug":   ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "Q":      ("Who needs the instruction?", "diamond", "q"),
    "USER":   ("⭐ Only me → ~/.claude/CLAUDE.md\\nor ~/.claude/rules/ (not shared)", "box", "scope"),
    "PROJ":   ("⭐ The team → project CLAUDE.md\\nor .claude/rules/ (in git)", "box", "scope"),
    "WHEN":   ("Needed in every session?", "diamond", "q"),
    "ALWAYS": ("Root CLAUDE.md / rule\\nwithout paths (at launch)", "box", "cond"),
    "SCOPED": ("⭐ Rule with paths: globs\\n(loads when a matching\\nfile is read)", "box", "cond"),
    "SPREAD": ("⭐ Files spread across dirs →\\n**/*.test.tsx glob, not a\\nsubdirectory CLAUDE.md", "box", "cond"),
    "VERIFY": ("⭐ /memory — check\\nwhat loaded", "box", "q"),
    "DIRMD":    ("✗ subdirectory CLAUDE.md for\\na cross-directory convention", "box", "bug"),
    "NOPATHS":  ("✗ no paths → loads\\nin every session", "box", "bug"),
    "USERLEVEL": ("✗ team rule kept\\nat user level", "box", "bug"),
    "ROOTGLOB": ("✗ *.test.tsx matches\\nthe root only", "box", "bug"),
}
_BUGS = ["DIRMD", "NOPATHS", "USERLEVEL", "ROOTGLOB"]
_EXP = {"test_convention": ["PROJ", "WHEN", "SCOPED", "SPREAD", "VERIFY"], "terraform_scoped": ["PROJ", "WHEN", "SCOPED", "VERIFY"],
        "teammate_api": ["PROJ", "VERIFY"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 3.1 pp.12–13, TS 3.3 pp.13–14)</FONT></TD></TR>')
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
    lines += ['  Q -> USER [label="only me"]; Q -> PROJ [label="the team"]; { rank=same; USER; PROJ; }', "  PROJ -> WHEN;",
              '  WHEN -> ALWAYS [label="yes"]; WHEN -> SCOPED [label="only for some files"]; { rank=same; ALWAYS; SCOPED; }',
              '  SCOPED -> SPREAD [label="spread across dirs"]; ALWAYS -> VERIFY; SPREAD -> VERIFY; USER -> VERIFY;',
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  VERIFY -> DIRMD [style=invis];", _key(hl),
              f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"Q": ("ok", "")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this scenario needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("3.1", "K", 1, "Hierarchy: user-level (~/.claude/CLAUDE.md), project-level (.claude/CLAUDE.md or root CLAUDE.md), directory-level (subdirectory CLAUDE.md).",
              "Grid 1 · playground “Where does it load?”"),
    ExamPoint("3.1", "K", 2, "User-level instructions apply only to that user — they are not shared through version control.", "✅ teammate_api · ❌ C"),
    ExamPoint("3.1", "K", 3, "@import references external files to keep CLAUDE.md modular.", "Grid 1 (lab: D1.7)"),
    ExamPoint("3.1", "K", 4, ".claude/rules/ organises topic-specific rule files instead of one monolithic CLAUDE.md.", "✅ REPO's .claude/rules/"),
    ExamPoint("3.1", "S", 1, "Diagnose hierarchy issues — e.g. a new teammate missing instructions kept at user level.", "✅ teammate_api · ❌ C"),
    ExamPoint("3.1", "S", 2, "Use @import to include each package's relevant standards.", "D1.7 lab (package_standards)"),
    ExamPoint("3.1", "S", 3, "Split large CLAUDE.md files into focused .claude/rules/ files (testing.md, api-conventions.md, deployment.md).", "✅ REPO"),
    ExamPoint("3.1", "S", 4, "Use /memory to verify which memory files loaded and diagnose inconsistent behaviour.", "every lab run prints a /memory view"),
    ExamPoint("3.3", "K", 1, ".claude/rules/ files with YAML `paths` glob patterns activate conditionally.", "✅ testing.md, terraform.md, api.md"),
    ExamPoint("3.3", "K", 2, "Path-scoped rules load only for matching files, cutting irrelevant context and tokens.", "✅ terraform_scoped · ❌ B"),
    ExamPoint("3.3", "K", 3, "Glob rules beat directory CLAUDE.md files for conventions spanning directories (test files everywhere).", "✅ test_convention · ❌ A"),
    ExamPoint("3.3", "S", 1, "Create path-scoped rules such as paths: [\"terraform/**/*\"].", "✅ terraform.md"),
    ExamPoint("3.3", "S", 2, "Use globs to apply conventions by file type regardless of directory (**/*.test.tsx).", "✅ testing.md · ❌ D"),
    ExamPoint("3.3", "S", 3, "Prefer path-specific rules over subdirectory CLAUDE.md files when conventions span the codebase.", "❌ A"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ team rules in the project · path-scoped rules with ** globs", "correct", CORRECT, "test_convention",
            observe=("test_convention: editing src/web/Button.test.tsx and src/api/orders.test.tsx both load .claude/rules/testing.md "
                     "(“path-scoped rule (**/*.test.tsx) matched …”); src/api/orders.ts doesn't. terraform_scoped: terraform.md loads "
                     "for terraform/modules/db/main.tf and not for src/web/App.tsx. teammate_api: a fresh clone loads CLAUDE.md and "
                     ".claude/rules/api.md."),
            why="Team conventions live in the repository. Conventions for some files load only when Claude reads those files, wherever they sit."),
    Variant("A", "⭐❌ A — a subdirectory CLAUDE.md for a cross-directory convention", "distractor", VARIANT_A, "test_convention",
            observe=("src/web/Button.test.tsx gets the convention (src/web/CLAUDE.md loads), but src/api/orders.test.tsx doesn't — "
                     "its directory has no such file."),
            why="A directory CLAUDE.md covers one tree; test files live everywhere. A glob rule follows the file type, not the folder.",
            fix=".claude/rules/testing.md with paths: [\"**/*.test.tsx\"].", source="guide:3.3:S3"),
    Variant("B", "⭐❌ B — a rule with no paths", "distractor", VARIANT_B, "terraform_scoped",
            observe="Editing src/web/App.tsx loads terraform.md too — it loads at launch in every session.",
            why="Without paths a rule is loaded unconditionally, spending context on every task.",
            fix="paths: [\"terraform/**/*\"].", source="guide:3.3:K2"),
    Variant("C", "⭐❌ C — the team's rule on one person's machine", "distractor", VARIANT_C, "teammate_api",
            observe="The teammate's session loads only CLAUDE.md — the API rule is in YOUR ~/.claude/rules/, which isn't in git.",
            why="User-level instructions apply to that user only; they are never shared through version control.",
            fix="Move it into the project's .claude/rules/.", source="guide:3.1:S1"),
    Variant("D", "❌ D — paths: \"*.test.tsx\"", "distractor", VARIANT_D, "test_convention",
            observe="Neither src/web/Button.test.tsx nor src/api/orders.test.tsx gets the convention.",
            why="In the docs' glob examples, *.md means Markdown files in the project ROOT — a single * doesn't cross directories.",
            fix="**/*.test.tsx.", source="docs"),
    Variant("E", "❌ E — “path:” instead of “paths:”", "distractor", VARIANT_E, "terraform_scoped",
            observe="Editing src/web/App.tsx loads terraform.md — the misspelled field is silently ignored, so the rule has no scope.",
            why="paths is the only frontmatter field Claude Code reads; any other field is ignored without an error (docs).",
            fix="paths:, and check with /memory.", source="docs"),
)

TLDR = (
    "**Where** an instruction lives decides **who** gets it:\n\n"
    "- **User** `~/.claude/` — only you, never shared.\n"
    "- **Project** `CLAUDE.md` / `.claude/rules/` — the team, via git.\n"
    "- **Directory** `sub/CLAUDE.md` — loads when Claude reads files there.\n\n"
    "**`paths` globs** decide **when** a rule loads. A rule with `paths: [\"**/*.test.tsx\"]` loads only when Claude reads a "
    "matching file, in any folder. It beats a subdirectory CLAUDE.md for conventions spread across the codebase, and saves "
    "context the rest of the time.\n\n"
    "- **`*`** stays in one folder; **`**`** crosses folders.\n"
    "- **`paths`** is the only field read.\n"
    "- Check what loaded with **/memory**."
)
MENTAL_MODEL = ("Instruction files are notices. Your ~/.claude/ notes are in your own pocket — nobody else sees them. "
                "CLAUDE.md is the notice at the front door that everyone reads. A path-scoped rule is a sign on a specific kind "
                "of door (every test file, every Terraform file) that only appears when you open one. A subdirectory CLAUDE.md "
                "is a sign in one corridor — it misses the same kind of door in other corridors.")

WHAT_IT_IS = """
The exam guide covers the CLAUDE.md hierarchy and modular organisation (Guide §6 · TS 3.1, pp.12–13) and path-specific rules
(TS 3.3, pp.13–14). The memory docs define exactly when each file loads. D1.7 covers `@import` and AGENTS.md in depth.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | User level `~/.claude/CLAUDE.md`, `~/.claude/rules/` | Notes in your pocket — nobody else has them. | ⭐ TS 3.1 · Knowledge 1–2 |
| 2 | Project level `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/` | The notice at the front door — everyone who clones reads it. | ⭐ TS 3.1 · Knowledge 1, 4 |
| 3 | Directory level `sub/CLAUDE.md` | A sign in one corridor — seen only by people in that corridor. | ⭐ TS 3.1 · Knowledge 1 |
| 4 | `.claude/rules/` topic files | One binder per topic instead of one giant manual. | ⭐ TS 3.1 · Knowledge 4, Skill 3 |
| 5 | Path-scoped rules (`paths:`) | A sign on a kind of door, appearing only when you open one. | ⭐ TS 3.3 · Knowledge 1–2 |
| 6 | `**/*.test.tsx` vs subdirectory CLAUDE.md | Label the door type, not the corridor — tests are in every corridor. | ⭐ TS 3.3 · Knowledge 3, Skills 2–3 |
| 7 | `*` vs `**` | `*` looks in one room; `**` searches the whole building. | 📘 docs |
| 8 | Only `paths` is read | A misspelled label is silently ignored — the sign goes up everywhere. | 📘 docs |
| 9 | `/memory` | Check the notice board before blaming the reader. | ⭐ TS 3.1 · Skill 4 |

**CLAUDE.md scope: user vs project vs directory** (the comparison CLAUDE.md requires)

| # | Aspect | User | Project | Directory |
|---|---|---|---|---|
| 1 | File | `~/.claude/CLAUDE.md` (+ `~/.claude/rules/`) | `./CLAUDE.md` or `./.claude/CLAUDE.md` (+ `.claude/rules/`) | `sub/dir/CLAUDE.md` |
| 2 | Who gets it | Just you, in every project | Everyone who clones the repo | Everyone — while Claude reads files in that directory |
| 3 | In git? | No | Yes | Yes |
| 4 | When it loads | At launch | At launch | On demand, when Claude reads a file under that directory |
| 5 | Use it for | Personal preferences | Team conventions, build commands | Conventions for one self-contained area |
| 6 | Trap | ⭐ Team rules put here never reach teammates | A monolith → split into `.claude/rules/` | ⭐ Conventions that span directories are missed |
| 7 | Guide reference | TS 3.1 K1–2, S1 | TS 3.1 K1, K4, S3 | TS 3.1 K1; TS 3.3 K3 |

*(Also in the docs: **managed policy** CLAUDE.md for a whole organisation, and **CLAUDE.local.md**, which is personal and
gitignored.)*

**Rule with `paths` vs rule without vs subdirectory CLAUDE.md**

| # | Aspect | Rule without `paths` | Rule with `paths` | Subdirectory CLAUDE.md |
|---|---|---|---|---|
| 1 | Loads | Every session, at launch | When Claude reads a matching file | When Claude reads a file in that directory |
| 2 | Matches by | — | File pattern, any directory | Folder |
| 3 | Test files everywhere | Loads for everything | ✅ `**/*.test.tsx` | ❌ Only that folder's tests |
| 4 | Context cost | Always | Only when relevant | Only in that folder |
"""

HOW_IT_WORKS = """
1. **Who needs it?** Only you → `~/.claude/`. The team → the project (`CLAUDE.md` or `.claude/rules/`), in git.
2. **When is it needed?** Every task → root `CLAUDE.md` or a rule without `paths`. Only for certain files → a rule with `paths`.
3. **Write the glob for the file type:** `**/*.test.tsx`, `terraform/**/*`, `src/api/**`. `*` alone stays in the root folder.
4. **Split a growing CLAUDE.md** into topic files under `.claude/rules/` (docs: under 200 lines per CLAUDE.md).
5. **Verify** with `/memory` (or `/context`) — if a file isn't listed, Claude can't see it.
"""

WHERE_SEEN = """
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): team conventions, test conventions, where rules live.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): a new teammate missing instructions.
- **Guide §8, Exercise 2** (p.25): configure a CLAUDE.md hierarchy and path-specific rules for a team.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 3.1 (pp.12–13) and TS 3.3 (pp.13–14), and the Claude Code memory docs "
              "(re-verified 2026-09-28 — pages listed above). Section layout inspired by a community concept list "
              "(claudearchitectcertification.com — community source, unverified; no text copied).")

LAB_INTRO = """
You write the repository's instruction files (`REPO`) and your own (`USER`). The **simulated** memory loader, following the
docs' loading rules, runs a few sessions: you or a teammate, reading particular files. For each session it prints a
**/memory** view — which files loaded and why — and checks the right instructions arrived, and only there.
"""

DISTRACTORS = (
    ("A · Subdirectory CLAUDE.md for tests", "Tests live in src/web, mostly.", "Tests in src/api miss the convention.",
     "paths: [\"**/*.test.tsx\"].", "guide:3.3:S3"),
    ("B · Rule without paths", "It's in .claude/rules/, so it's modular.", "Loads in every session.", "paths: [\"terraform/**/*\"].", "guide:3.3:K2"),
    ("C · Team rule in ~/.claude/", "It works for me.", "Teammates never get it.", "Project .claude/rules/.", "guide:3.1:S1"),
    ("D · paths: \"*.test.tsx\"", "Looks like it matches every test.", "* stays in the root folder.", "**/*.test.tsx.", "docs"),
    ("E · path: instead of paths:", "Close enough.", "Ignored without an error → loads everywhere.", "paths:, verify with /memory.", "docs"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Glob", "Matches", "Doesn't match")
SIDE_BY_SIDE_ROWS = (
    ("1", "**/*.test.tsx", "Button.test.tsx, src/api/orders.test.tsx", "src/api/orders.ts"),
    ("2", "*.test.tsx", "Root.test.tsx (project root only)", "src/web/Button.test.tsx"),
    ("3", "terraform/**/*", "terraform/main.tf, terraform/modules/db/main.tf", "src/web/App.tsx"),
    ("4", "src/api/**", "src/api/orders.ts, src/api/v2/x.ts", "src/web/App.tsx"),
    ("5", "src/**/*.{ts,tsx}", "src/a.ts, src/web/App.tsx", "README.md"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Only for you?"];
  USER [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="~/.claude/CLAUDE.md\\nor ~/.claude/rules/"];
  Q2 [shape=diamond, label="Needed for every task?"];
  ROOT [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="CLAUDE.md or a rule\\nwithout paths"];
  Q3 [shape=diamond, label="Files spread across\\ndirectories?"];
  GLOB [shape=box, fillcolor="#D1FAE5", color="#059669", label=".claude/rules/x.md with\\npaths: [\\"**/*.test.tsx\\"]"];
  DIR [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Rule with paths: [\\"area/**\\"]\\n(or that area's CLAUDE.md)"];
  CHECK [shape=box, fillcolor="#EDE9FE", color="#7C3AED", label="Verify with /memory"];
  Q1 -> USER [label="yes"]; Q1 -> Q2 [label="no — the team"]; Q2 -> ROOT [label="yes"]; Q2 -> Q3 [label="no"];
  Q3 -> GLOB [label="yes"]; Q3 -> DIR [label="no, one area"]; USER -> CHECK; ROOT -> CHECK; GLOB -> CHECK; DIR -> CHECK;
}''')

EXPERIMENTS = (
    "Run ✅ on all three scenarios and read each session's /memory list.",
    "In ✅, change **/*.test.tsx to src/web/**/*.test.tsx: which session loses the convention?",
    "Run ❌ E and notice there's no error — only /memory shows the rule loaded where it shouldn't.",
    "In the playground's “Who gets it?” tab, put the API rule in CLAUDE.local.md and read src/api/orders.ts as a teammate.",
    "In the “Spread-out conventions” tab, choose the subdirectory CLAUDE.md and read src/web/App.tsx (not a test).",
)

QUESTIONS = (
    Question(
        q=("A project's CLAUDE.md has grown to 700 lines covering testing, API conventions and deployment, and six "
           "contributors edit it. Claude follows some sections inconsistently, and edits to the file cause merge conflicts "
           "about once a week. What is the recommended restructuring?"),
        opts=("Summarise the 700 lines into a 100-line CLAUDE.md that keeps only the rules the team rates most important.",
              "Split it into focused files under .claude/rules/, such as testing.md, api-conventions.md and deployment.md.",
              "Move each contributor's sections into their own ~/.claude/CLAUDE.md, so nobody edits a shared file any more.",
              "Keep one file, but lock editing to a single owner who merges all of the proposed changes once every week."),
        ans=1,
        explain=("Topic-specific files in .claude/rules/ keep each area small, separately owned and easy to review, instead of "
                 "one monolithic file. A discards rules to save space. C takes team rules out of version control. D keeps "
                 "the monolith and adds a bottleneck."),
        scenarios=(2,), points=("3.1:K4", "3.1:S3"),
    ),
    Question(
        q=("Infrastructure conventions (tagging, naming, no hard-coded regions) apply to every Terraform file. These files "
           "live under terraform/ and also in the deploy/ folder of each of 40 services. The conventions sit in the root "
           "CLAUDE.md and use about 2,000 tokens in every session, including the 80% spent on the web app. What is the best "
           "setup?"),
        opts=("A CLAUDE.md with the conventions in terraform/ and in each of the 40 deploy/ folders beside the files.",
              "A /terraform skill that developers invoke before they begin work on any of the infrastructure changes.",
              "A rule file in .claude/rules/ with paths: [\"**/*.tf\"] in its YAML frontmatter.",
              "Keep them in the root CLAUDE.md, but move them to the bottom, where they compete less for attention."),
        ans=2,
        explain=("A path-scoped rule loads only when Claude works on matching files, wherever they live, so the web-app sessions "
                 "stop paying for it. A duplicates the rules 41 times. B depends on someone remembering to invoke it. D still "
                 "loads the conventions everywhere."),
        scenarios=(2,), points=("3.3:K1", "3.3:S1", "3.3:K2"),
    ),
    Question(
        q=("A team created .claude/rules/testing.md with paths: [\"tests/**/*\"]. But their test files live next to the "
           "components they test, across 40 directories (Button.test.tsx beside Button.tsx), and the rule loaded for only "
           "about 5% of test edits last week. What should they change?"),
        opts=("Move every test file into tests/, so that the rule's existing path pattern matches all of them.",
              "Remove the paths field, so that the testing rule loads in every session whichever file is edited.",
              "Add a CLAUDE.md with the testing rules to each of the 40 directories that contain test files.",
              "Change the paths pattern to a file-name glob such as **/*.test.tsx, which matches tests anywhere."),
        ans=3,
        explain=("A glob on the naming convention matches test files wherever they sit. Directory-based scoping can't do "
                 "that. A reorganises the codebase to suit a config file. B loads testing rules for all work. C scatters "
                 "40 copies that will drift apart."),
        scenarios=(2,), points=("3.3:K3", "3.3:S2", "3.3:S3"),
    ),
    Question(
        q=("Two engineers say Claude behaves differently on the same monorepo: in one of their sessions it insists on a "
           "deprecated logging library. One engineer suspects a leftover CLAUDE.md in packages/legacy and proposes deleting "
           "every directory-level CLAUDE.md to be safe. What should they do first?"),
        opts=("Run /memory in each session and compare which instruction files each one has loaded.",
              "Delete every directory-level CLAUDE.md, then re-add the ones the team confirms are still needed.",
              "Add a rule to the root CLAUDE.md forbidding the old library, so it overrides any lower-level file.",
              "Ask Claude in each session where its logging preference comes from, and compare the two answers."),
        ans=0,
        explain=("/memory shows exactly which memory files each session loaded, which confirms or rules out the suspicion in "
                 "seconds. B is destructive and made without a diagnosis. C adds a conflicting instruction instead of "
                 "finding the source. D relies on the model's account of its own context."),
        scenarios=(4,), points=("3.1:S4", "3.1:S1"),
    ),
    Question(
        q=("A developer writes a rule whose frontmatter says path: [\"docs/**\"] (singular) and expects it to load only for "
           "documentation work. /memory shows it loaded in every session, including 300 backend sessions last week. What is "
           "going on?"),
        opts=("Rules in .claude/rules/ always load in every session; path scoping only changes their load priority.",
              "Only paths is read, so the misspelt field is ignored and the rule behaves as if it had no scope.",
              "The glob docs/** is invalid, so it falls back to matching every file in the repository.",
              "Path-scoped rules load everywhere until Claude Code restarts after the rule file is created."),
        ans=1,
        explain=("Scoping is read from the paths field. An unknown field is ignored, and a rule without paths loads "
                 "unconditionally. A, C and D describe behaviour that doesn't exist."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Does a path-scoped rule load when Claude edits a file or when it reads one?",
     "The guide says “when editing matching files”. The docs say path-scoped rules trigger when Claude **reads** a matching file, "
     "not on every tool use. In practice Claude reads a file before editing it, so both hold for the exam's scenarios."),
    ("Subdirectory CLAUDE.md or a path-scoped rule?",
     "A subdirectory CLAUDE.md suits conventions that belong to one self-contained area. A rule with a glob suits conventions "
     "for a kind of file spread across the codebase — tests, migrations, Terraform — which is the guide's point in TS 3.3."),
    ("What about CLAUDE.local.md and managed CLAUDE.md?",
     "Both are in the docs, not the guide. CLAUDE.local.md is personal and gitignored, so teammates never get it. A managed-policy "
     "CLAUDE.md is deployed by IT for everyone in the organisation and can't be excluded."),
    ("Does CLAUDE.md guarantee behaviour?",
     "No. The docs say it's context, not enforced configuration. Rules that must hold every time belong in a hook (see D2.4)."),
)

PLAYGROUND_INTRO = """
Type the path of a file Claude reads, then move instructions around with the knobs. Each run shows a **/memory**-style list of
what loaded and why, and the instructions that reached the session, on the **simulated** loader.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="rules")


PLAYGROUND = (
    _tab("where", "⭐ Who gets it?", "where", "Pocket notes vs the notice at the front door.", "guide:3.1:K2",
         "Where the team's API rule lives, and whether you or a teammate's fresh clone receives it.", "memory § Choose where to put CLAUDE.md files",
         ("who", "api_rule_where"), {"who": "teammate", "api_rule_where": "project_rule"}, ("src/api/orders.ts",),
         ("user rule + teammate: missing.", "user rule + you: present.", "CLAUDE.local.md + teammate: missing (gitignored).")),
    _tab("scoped", "⭐ Scoped rules", "scoped", "A sign that only appears on the right kind of door.", "guide:3.3:K2",
         "The Terraform rule with paths, without, or with a misspelled field.", "memory § Path-specific rules",
         ("tf_paths",), {"tf_paths": "scoped"}, ("src/web/App.tsx", "terraform/modules/db/main.tf"),
         ("scoped + App.tsx: not loaded.", "no paths + App.tsx: loaded.", "“path:” + App.tsx: loaded — silently.")),
    _tab("spread", "⭐ Spread-out conventions", "spread", "Label the door type, not the corridor.", "guide:3.3:S3",
         "A test convention as a **/ glob rule, a src/web/CLAUDE.md, or a root-only *.test.tsx glob.", "memory § Path-specific rules; guide TS 3.3",
         ("test_rule_as",), {"test_rule_as": "glob_rule"}, ("src/api/orders.test.tsx", "src/web/Button.test.tsx", "src/web/App.tsx", "Root.test.tsx"),
         ("dir CLAUDE.md + src/api test: missing.", "dir CLAUDE.md + src/web/App.tsx: loaded for a non-test.", "root glob + src/web test: missing.")),
    _tab("memory", "⭐ /memory", "memory", "Check the notice board before blaming the reader.", "guide:3.1:S4",
         "Every knob at once — read any file and see exactly what loaded and why.", "memory § Troubleshoot",
         ("who", "api_rule_where", "tf_paths", "test_rule_as"),
         {"who": "you", "api_rule_where": "project_rule", "tf_paths": "scoped", "test_rule_as": "glob_rule"},
         ("terraform/modules/db/main.tf", "src/api/orders.test.tsx"), ("Read a Terraform file, then an API test.",)),
)

CONTENT = ConceptContent(
    slug="claude-md-hierarchy", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("agent-instruction-files", "skills", "agentic-tool-surface-selection"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("test_convention", "terraform_scoped", "teammate_api"), show_ledger=False,
)
