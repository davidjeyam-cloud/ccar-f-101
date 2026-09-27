"""
D3.3 Skills — custom slash commands and skills: where they live (project vs personal), SKILL.md frontmatter (context: fork,
allowed-tools / disallowed-tools, argument-hint), and choosing a skill vs CLAUDE.md. Guide TS 3.2 (p.13).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); skills docs fetched 2026-09-28 (DOC_REFS). The guide
says allowed-tools "restricts" tool access; the current docs say allowed-tools PRE-APPROVES tools and does not restrict them —
disallowed-tools is the field that removes tools. Both are shown; the lab follows the docs. Paraphrased; no real exam question.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Extend Claude with skills — locations, frontmatter, arguments, context: fork, pre-approving tools", f"{_C}/skills"),
    DocRef("Extend Claude Code — CLAUDE.md vs skill; context cost", f"{_C}/features-overview"),
    DocRef("Configure permissions — acceptEdits auto-approves file operations", f"{_C}/agent-sdk/permissions"),
)

GROUNDING = (
    Claim("Skill locations: enterprise (managed), personal ~/.claude/skills/<name>/SKILL.md (all your projects), project "
          ".claude/skills/<name>/SKILL.md (this repository), nested, plugin (/plugin:name), bundled. Same name: enterprise over "
          "personal, personal over project; a skill over a .claude/commands/ file.", "docs", "skills § where skills live; precedence"),
    Claim("Custom commands in .claude/commands/ still work; skills add supporting files, frontmatter control and automatic "
          "invocation. Both create / commands.", "docs", "skills"),
    Claim("context: fork runs the skill in an isolated subagent with no conversation history; `agent` picks the subagent type "
          "(e.g. Explore); the result returns to the main conversation.", "docs", "skills § frontmatter (context, agent)"),
    Claim("allowed-tools lists tools Claude can use without asking during the turn that invokes the skill; the grant clears on "
          "your next message; it does not restrict which tools are available — every tool stays callable.", "docs",
          "skills § Pre-approve tools for a skill"),
    Claim("disallowed-tools removes tools from Claude's available pool while the skill is active; the restriction clears on your "
          "next message.", "docs", "skills § frontmatter (disallowed-tools)"),
    Claim("argument-hint is shown during autocomplete to indicate expected arguments (e.g. [issue-number]); $ARGUMENTS expands to "
          "what was typed; if no placeholder receives an argument, Claude Code appends ARGUMENTS: <value>.", "docs",
          "skills § frontmatter; arguments"),
    Claim("disable-model-invocation: true — only you can invoke the skill (for /deploy, /commit and other side effects).",
          "docs", "skills § frontmatter"),
    Claim("CLAUDE.md loads every session; a skill's description loads each session and its full content when used.", "docs",
          "features-overview § CLAUDE.md vs Skill; context cost"),
    Claim("In acceptEdits mode, file edits and filesystem commands (mkdir, touch, rm, rmdir, mv, cp, sed) inside the working "
          "directory are auto-approved.", "docs", "agent-sdk/permissions § acceptEdits"),
    Claim("Project commands in .claude/commands/ are shared via version control; user commands in ~/.claude/commands/ are personal; "
          "skills in .claude/skills/ with SKILL.md support frontmatter (context: fork, allowed-tools, argument-hint); context: fork "
          "isolates skill output from the main conversation; personal variants go in ~/.claude/skills/ with different names.",
          "guide", "TS 3.2 · Knowledge 1–4 · p.13"),
    Claim("Skills: project commands for team availability; context: fork for verbose or exploratory skills; allowed-tools to "
          "restrict tool access during a skill; argument-hint to prompt for required parameters; skills for on-demand workflows "
          "vs CLAUDE.md for always-loaded standards.", "guide", "TS 3.2 · Skills 1–5 · p.13"),
    Claim("The guide says allowed-tools restricts tool access; the docs say allowed-tools pre-approves and disallowed-tools "
          "restricts. For exam answers use the guide's wording; in real skills use disallowed-tools to take tools away.",
          "guide", "TS 3.2 S3 vs skills docs"),
    Claim("Token counts, the scaffold skill's stray rm -rf, the developer following the argument hint and the unmatched request "
          "are invented.", "simulated", "utils/skills_lab.py"),
)

CORRECT = r'''from utils.skills_lab import TEAM_REVIEW, simulate   # SIMULATED command/skill loader + sessions

PROJECT = {   # in the repository - every teammate gets these
    # a team command, shared through git
    ".claude/commands/review-pr.md": TEAM_REVIEW,
    # verbose output -> run it in an isolated subagent; only the summary comes back
    ".claude/skills/analyze-codebase/SKILL.md": ("---\nname: analyze-codebase\n"
        "description: Maps every module and dependency in the codebase\ncontext: fork\nagent: Explore\n---\n"
        "Map every module and its dependencies. Return a one-page summary."),
    # only file writing: pre-approve Write/Edit, and REMOVE Bash while the skill runs
    ".claude/skills/scaffold/SKILL.md": ("---\nname: scaffold\ndescription: Creates boilerplate files for a new component\n"
        "allowed-tools: Write Edit\ndisallowed-tools: Bash\n---\nCreate the component, its test and its story."),
    # needs an issue number -> show it in autocomplete, use it via $ARGUMENTS
    ".claude/skills/fix-issue/SKILL.md": ("---\nname: fix-issue\ndescription: Fixes a GitHub issue by number\n"
        "argument-hint: [issue-number]\ndisable-model-invocation: true\n---\nFix issue $ARGUMENTS: reproduce it, fix it, add a test."),
}
CLAUDE_MD = "# Project\n- Use pnpm, never npm.\n"   # a universal standard: always loaded

USER = {   # ~/.claude/ on your machine - a personal variant with its OWN name
    "~/.claude/skills/review-pr-terse/SKILL.md": ("---\nname: review-pr-terse\ndescription: My terse PR review\n---\n"
        "Review the PR; report only blocking issues, one line each."),
}

simulate(PROJECT, USER, CLAUDE_MD)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ TS 3.2 · Knowledge 1 / Skill 1 — the team command in ~/.claude/commands/
VARIANT_A = _swap(_swap(CORRECT, '''    # a team command, shared through git
    ".claude/commands/review-pr.md": TEAM_REVIEW,
''', ""), '''USER = {   # ~/.claude/ on your machine - a personal variant with its OWN name
''', '''USER = {   # ~/.claude/ on your machine - a personal variant with its OWN name
    "~/.claude/commands/review-pr.md": TEAM_REVIEW,   # WRONG: the TEAM command on one person's machine
''')
# ⭐ TS 3.2 · Skill 2 / Knowledge 3 — verbose skill without context: fork
VARIANT_B = _swap(CORRECT, '''description: Maps every module and dependency in the codebase\\ncontext: fork\\nagent: Explore\\n---\\n"''',
                  '''description: Maps every module and dependency in the codebase\\n---\\n"   # WRONG: no context: fork''')
# 📘 docs (guide words this as allowed-tools) — relying on allowed-tools to restrict
VARIANT_C = _swap(CORRECT, '''"allowed-tools: Write Edit\\ndisallowed-tools: Bash\\n---\\nCreate''',
                  '''"allowed-tools: Write Edit\\n---\\nCreate''')
VARIANT_C = _swap(VARIANT_C, "    # only file writing: pre-approve Write/Edit, and REMOVE Bash while the skill runs",
                  "    # WRONG: assumes allowed-tools restricts the skill to Write/Edit - it only pre-approves them")
# ⭐ TS 3.2 · Skill 4 — no argument-hint
VARIANT_D = _swap(CORRECT, '''"argument-hint: [issue-number]\\ndisable-model-invocation''', '''"disable-model-invocation''')
VARIANT_D = _swap(VARIANT_D, "    # needs an issue number -> show it in autocomplete, use it via $ARGUMENTS",
                  "    # WRONG: needs an issue number, but nothing tells the developer")
# ⭐ TS 3.2 · Skill 5 — a universal standard as a skill
VARIANT_E = _swap(_swap(CORRECT, '''CLAUDE_MD = "# Project\\n- Use pnpm, never npm.\\n"   # a universal standard: always loaded''',
                        '''CLAUDE_MD = "# Project\\n"'''),
                  '''PROJECT = {   # in the repository - every teammate gets these
''', '''PROJECT = {   # in the repository - every teammate gets these
    # WRONG: an always-needed standard as an on-demand skill
    ".claude/skills/package-manager/SKILL.md": ("---\\nname: package-manager\\ndescription: Package manager conventions\\n---\\n"
        "Use pnpm, never npm."),
''')
# ⭐ TS 3.2 · Knowledge 4 — editing the team skill instead of a personal variant
VARIANT_F = _swap(_swap(CORRECT, '''    ".claude/commands/review-pr.md": TEAM_REVIEW,''',
                        '''    ".claude/commands/review-pr.md": "Review the PR; report only blocking issues, one line each.",   # WRONG: edited the TEAM command'''),
                  '''    "~/.claude/skills/review-pr-terse/SKILL.md": ("---\\nname: review-pr-terse\\ndescription: My terse PR review\\n---\\n"
        "Review the PR; report only blocking issues, one line each."),
''', "")

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "skills_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


_BUG = {"team_command": "USERCMD", "verbose_analysis": "NOFORK", "restrict_tools": "ALLOWEDONLY", "missing_argument": "NOHINT",
        "always_standard": "SKILLSTD", "personal_variant": "EDITTEAM"}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "simulate() was never called"
    txt = " · ".join(r["log"])
    return (True, None, txt) if r["ok"] else (False, _BUG[sc], txt)


EXPECTED = {
    "team_command": "a teammate's fresh clone has /review-pr",
    "verbose_analysis": "/analyze-codebase runs in a forked subagent — only a ~2,000-token summary reaches the main context",
    "restrict_tools": "/scaffold writes its 3 files and cannot run Bash — build/ survives",
    "missing_argument": "autocomplete shows [issue-number]; the skill receives issue 4521",
    "always_standard": "“run the tests” uses pnpm — the standard is always in context",
    "personal_variant": "the team's /review-pr is unchanged for everyone, and you have your own terse variant under another name",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":     ("#EDE9FE", "#7C3AED", "the decision"),
    "where": ("#DBEAFE", "#0066CC", "where it lives"),
    "fm":    ("#FEF3C7", "#D97706", "SKILL.md frontmatter"),
    "vs":    ("#CCFBF1", "#0D9488", "skill vs CLAUDE.md"),
    "bug":   ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "Q":      ("Always needed, or\\na task you invoke?", "diamond", "q"),
    "MD":     ("⭐ Always → CLAUDE.md", "box", "vs"),
    "WHO":    ("⭐ Team → .claude/commands/ or\\n.claude/skills/ (in git)\\nMe → ~/.claude/skills/ (new name)", "box", "where"),
    "FORK":   ("⭐ Verbose / exploratory →\\ncontext: fork (+ agent)", "box", "fm"),
    "TOOLS":  ("⭐ Limit tools → disallowed-tools\\n(guide: “allowed-tools”);\\nallowed-tools pre-approves", "box", "fm"),
    "HINT":   ("⭐ Needs a parameter →\\nargument-hint + $ARGUMENTS", "box", "fm"),
    "USERCMD":   ("✗ team command in\\n~/.claude/commands/", "box", "bug"),
    "NOFORK":    ("✗ verbose skill\\nwithout context: fork", "box", "bug"),
    "ALLOWEDONLY": ("✗ allowed-tools taken\\nas a restriction", "box", "bug"),
    "NOHINT":    ("✗ no argument-hint", "box", "bug"),
    "SKILLSTD":  ("✗ universal standard\\nin a skill", "box", "bug"),
    "EDITTEAM":  ("✗ edited the team's skill\\nfor a personal taste", "box", "bug"),
}
_BUGS = ["USERCMD", "NOFORK", "ALLOWEDONLY", "NOHINT", "SKILLSTD", "EDITTEAM"]
_EXP = {"team_command": ["WHO"], "verbose_analysis": ["WHO", "FORK"], "restrict_tools": ["WHO", "TOOLS"],
        "missing_argument": ["WHO", "HINT"], "always_standard": ["MD"], "personal_variant": ["WHO"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 3.2 p.13)</FONT></TD></TR>')
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
    lines += ['  Q -> MD [label="always"]; Q -> WHO [label="a task"]; { rank=same; MD; WHO; }',
              '  WHO -> FORK [label="verbose output"]; WHO -> TOOLS [label="risky tools"]; WHO -> HINT [label="needs input"];',
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  HINT -> USERCMD [style=invis]; FORK -> USERCMD [style=invis];",
              _key(hl), f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
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
    ExamPoint("3.2", "K", 1, "Project commands in .claude/commands/ are shared via version control; user commands in ~/.claude/commands/ are personal.",
              "✅ team_command · ❌ A"),
    ExamPoint("3.2", "K", 2, "Skills live in .claude/skills/ with a SKILL.md whose frontmatter supports context: fork, allowed-tools and argument-hint.",
              "✅ PROJECT's skills"),
    ExamPoint("3.2", "K", 3, "context: fork runs a skill in an isolated sub-agent so its output doesn't pollute the main conversation.",
              "✅ verbose_analysis · ❌ B"),
    ExamPoint("3.2", "K", 4, "Personal variants go in ~/.claude/skills/ under different names so teammates aren't affected.",
              "✅ personal_variant · ❌ F"),
    ExamPoint("3.2", "S", 1, "Create project-scoped commands in .claude/commands/ for team-wide availability.", "✅ review-pr · ❌ A"),
    ExamPoint("3.2", "S", 2, "Use context: fork for skills with verbose output (codebase analysis) or exploratory context (brainstorming).",
              "✅ analyze-codebase · ❌ B"),
    ExamPoint("3.2", "S", 3, "Configure allowed-tools in skill frontmatter to restrict tool access during the skill (e.g. only file writes).",
              "✅ restrict_tools (docs: disallowed-tools does the removing) · ❌ C"),
    ExamPoint("3.2", "S", 4, "Use argument-hint so developers are prompted for required parameters.", "✅ missing_argument · ❌ D"),
    ExamPoint("3.2", "S", 5, "Choose skills for on-demand task workflows and CLAUDE.md for always-loaded universal standards.",
              "✅ always_standard · ❌ E"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ team commands in git · fork verbose skills · take risky tools away · argument-hint · CLAUDE.md for standards", "correct", CORRECT, "team_command",
            observe=("team_command: a fresh clone has /review-pr. verbose_analysis: /analyze-codebase runs in a forked Explore subagent → "
                     "+2,000 tokens. restrict_tools: Bash isn't available while /scaffold runs → build/ survives. missing_argument: "
                     "autocomplete shows [issue-number] → “Fix issue 4521 …”. always_standard: “run the tests” → pnpm test. "
                     "personal_variant: the team's /review-pr is unchanged; you also have /review-pr-terse."),
            why="Each piece is where its audience can see it, and does only what its frontmatter allows."),
    Variant("A", "⭐❌ A — the team command in ~/.claude/commands/", "distractor", VARIANT_A, "team_command",
            observe="A teammate's fresh clone has /analyze-codebase, /fix-issue, /scaffold — /review-pr is unknown to them.",
            why="~/.claude/ is personal; only .claude/commands/ and .claude/skills/ in the repository reach the team.",
            fix="Move it to .claude/commands/ (or .claude/skills/).", source="guide:3.2:S1"),
    Variant("B", "⭐❌ B — a verbose skill without context: fork", "distractor", VARIANT_B, "verbose_analysis",
            observe="/analyze-codebase runs in the main conversation — +40,000 tokens of listings and dependency dumps stay there.",
            why="context: fork runs the skill in an isolated subagent; only its result comes back.",
            fix="context: fork (with agent: Explore for read-only analysis).", source="guide:3.2:S2"),
    Variant("C", "❌ C — trusting allowed-tools to restrict tools", "distractor", VARIANT_C, "restrict_tools",
            observe=("Write/Edit are pre-approved, but Bash is still available; in acceptEdits mode rm inside the project is "
                     "auto-approved → build/ DELETED."),
            why=("In current Claude Code, allowed-tools only pre-approves tools for the turn; it “does not restrict which tools are "
                 "available”. disallowed-tools removes them. (The guide calls restriction “allowed-tools” — see the table.)"),
            fix="disallowed-tools: Bash (keep allowed-tools for pre-approval).", source="docs"),
    Variant("D", "⭐❌ D — no argument-hint", "distractor", VARIANT_D, "missing_argument",
            observe="Autocomplete shows no hint; the developer types /fix-issue alone → “Fix issue : …” → Claude picks #4519, the wrong issue.",
            why="argument-hint tells developers which parameter the skill needs.",
            fix="argument-hint: [issue-number] (and $ARGUMENTS in the body).", source="guide:3.2:S4"),
    Variant("E", "⭐❌ E — a universal standard as a skill", "distractor", VARIANT_E, "always_standard",
            observe="“run the tests before you commit” doesn't match the package-manager skill's description, so it never loads → npm test.",
            why="Skills load on demand; standards every task needs belong in CLAUDE.md, which loads every session.",
            fix="Put “use pnpm” in CLAUDE.md.", source="guide:3.2:S5"),
    Variant("F", "⭐❌ F — editing the team's command for a personal taste", "distractor", VARIANT_F, "personal_variant",
            observe="The teammate's /review-pr is now “report only blocking issues, one line each” — everyone got your preference.",
            why="Personal variants belong in ~/.claude/skills/ under a different name, so teammates aren't affected.",
            fix="~/.claude/skills/review-pr-terse/SKILL.md.", source="guide:3.2:K4"),
)

TLDR = (
    "**Commands and skills are / workflows you invoke.**\n\n"
    "- **Team ones** go in the repository: `.claude/commands/` or `.claude/skills/<name>/SKILL.md`.\n"
    "- **Personal ones** go in `~/.claude/skills/`, under a **different name** from the team's.\n\n"
    "**Frontmatter:**\n\n"
    "- **`context: fork`** runs a verbose skill in an isolated subagent, so only the result comes back.\n"
    "- **`argument-hint`** tells developers which parameter to pass.\n"
    "- **Tool limits:** the guide says `allowed-tools`. ⚠️ In current Claude Code, `allowed-tools` **pre-approves** tools and "
    "**`disallowed-tools` removes them**.\n\n"
    "**Skill vs CLAUDE.md:** use a **skill** for on-demand tasks and **CLAUDE.md** for standards every task needs."
)
MENTAL_MODEL = ("A skill is a recipe card in the shared kitchen drawer (.claude/skills/) — everyone can pull it out when they "
                "cook that dish. Your own twist goes on a card in your apron pocket with a different name, not scribbled over "
                "the shared card. CLAUDE.md is the sign on the wall everybody sees every time. context: fork cooks in the back "
                "kitchen and sends out only the plate.")

WHAT_IT_IS = """
The exam guide covers creating and configuring custom slash commands and skills (Guide §6 · TS 3.2, p.13). The skills docs
define every frontmatter field — in one place differently from the guide (see the ⚠️ table).

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Project commands `.claude/commands/` | A recipe card in the shared drawer — everyone has it. | ⭐ TS 3.2 · Knowledge 1, Skill 1 |
| 2 | User commands `~/.claude/commands/` | A card in your apron pocket — only you have it. | ⭐ TS 3.2 · Knowledge 1 |
| 3 | Skills `.claude/skills/<name>/SKILL.md` | A recipe card with notes in the margin (frontmatter). | ⭐ TS 3.2 · Knowledge 2 |
| 4 | `context: fork` | Cook in the back kitchen; send out only the plate. | ⭐ TS 3.2 · Knowledge 3, Skill 2 |
| 5 | Limiting tools | Lock the knife drawer while this recipe runs. | ⭐ TS 3.2 · Skill 3 (see ⚠️ below) |
| 6 | `argument-hint` | “Serves: __” printed on the card, so nobody forgets to fill it in. | ⭐ TS 3.2 · Skill 4 |
| 7 | Personal variant, new name | Your twist on your own card, not scribbled on the shared one. | ⭐ TS 3.2 · Knowledge 4 |
| 8 | Skill vs CLAUDE.md | A recipe you pull out when needed vs the sign on the wall everyone sees. | ⭐ TS 3.2 · Skill 5 |
| 9 | `disable-model-invocation` | A card only a person may pull out (deploy, commit). | 📘 docs |

**⚠️ Tool limits — the guide's wording vs current Claude Code**

| # | Question | Exam guide (TS 3.2 Skill 3) | Claude Code docs (2026-09-28) |
|---|---|---|---|
| 1 | Which field restricts tools during a skill? | `allowed-tools` | **`disallowed-tools`** removes tools while the skill is active |
| 2 | What does `allowed-tools` do? | Restricts tool access | **Pre-approves** the listed tools for that turn — “does not restrict which tools are available” |
| 3 | How long does it last? | — | Until you send your next message |
| 4 | For an exam answer | ⭐ Pick **allowed-tools** for “restrict tools in a skill” | — |
| 5 | In a real skill | — | `allowed-tools` to skip prompts **+** `disallowed-tools` to take tools away |

**Where commands and skills live**

| # | Location | Who gets it | In git? | Same name wins? |
|---|---|---|---|---|
| 1 | `.claude/commands/<name>.md` | The team | Yes | A skill with the same name wins over it |
| 2 | `.claude/skills/<name>/SKILL.md` | The team | Yes | Personal beats project |
| 3 | `~/.claude/commands/`, `~/.claude/skills/` | Only you, all projects | No | Personal beats project (docs) — so use a **new name** for variants |
| 4 | Enterprise (managed) | Everyone in the organisation | — | Beats personal |

**Frontmatter fields the exam names** (plus two docs-only fields)

| # | Field | Does (docs) | Use it for |
|---|---|---|---|
| 1 | ⭐ `context: fork` (+ `agent`) | Runs in an isolated subagent, no conversation history; the result returns | Verbose analysis, brainstorming |
| 2 | ⭐ `allowed-tools` | Pre-approves tools for the turn | Skipping prompts (guide: restricting) |
| 3 | `disallowed-tools` | Removes tools while the skill is active | Actually taking tools away |
| 4 | ⭐ `argument-hint` | Shown in autocomplete, e.g. `[issue-number]` | Required parameters |
| 5 | `disable-model-invocation` | Only a person can invoke it | Deploy, commit, side effects |
"""

HOW_IT_WORKS = """
1. **Always needed?** Put it in CLAUDE.md. **A task someone invokes?** Make it a command or skill.
2. **For the team?** Put it in `.claude/commands/` or `.claude/skills/` in git. **Just you?** Use `~/.claude/skills/`, with
   a new name if it's a variant of a team skill.
3. **Verbose or exploratory?** Add `context: fork` (and `agent: Explore` for read-only work).
4. **Risky tools?** Take them away with `disallowed-tools`; pre-approve safe ones with `allowed-tools`. The guide calls this
   "allowed-tools".
5. **Needs a parameter?** Add an `argument-hint` and use `$ARGUMENTS` in the body.
"""

WHERE_SEEN = """
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): team commands, verbose analysis skills.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): skills vs CLAUDE.md, personal variants.
- **Guide §8, Exercise 2** (p.25): custom slash commands and skills with frontmatter for a team.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 3.2 (p.13) and the Claude Code skills docs (verified 2026-09-28 — pages listed "
              "above). The guide and the docs differ on allowed-tools; both are shown. Section layout inspired by a community "
              "concept list (claudearchitectcertification.com — community source, unverified; no text copied).")

LAB_INTRO = """
You write the repository's commands and skills (`PROJECT`), the project `CLAUDE_MD`, and your own `USER` skills. The
**simulated** loader, following the skills docs, runs six situations and checks the result each time:

- what a teammate can invoke;
- how much a skill adds to the main context;
- which tools a skill can reach in `acceptEdits` mode;
- what a skill receives as arguments;
- whether a standard is in context;
- whether your preference leaked to the team.
"""

DISTRACTORS = (
    ("A · Team command in ~/.claude/commands/", "It works on my machine.", "Teammates don't have it.", ".claude/commands/.", "guide:3.2:S1"),
    ("B · Verbose skill without fork", "The output is useful.", "+40,000 tokens in the main conversation.", "context: fork.", "guide:3.2:S2"),
    ("C · allowed-tools as a restriction", "The exam says allowed-tools restricts.", "In current Claude Code it only pre-approves — Bash stays.",
     "disallowed-tools (exam wording: allowed-tools).", "docs"),
    ("D · No argument-hint", "Developers know what to pass.", "/fix-issue with no number → the wrong issue.", "argument-hint.", "guide:3.2:S4"),
    ("E · Standard in a skill", "Skills keep CLAUDE.md short.", "The skill doesn't load for everyday requests.", "CLAUDE.md.", "guide:3.2:S5"),
    ("F · Edit the team's skill for yourself", "It's just a tweak.", "Every teammate gets your preference.", "A personal skill with a new name.",
     "guide:3.2:K4"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Skill", "CLAUDE.md")
SIDE_BY_SIDE_ROWS = (
    ("1", "Loads", "Description every session; content when invoked or matched", "Every session, in full"),
    ("2", "Triggered by", "/name, or a request that matches the description", "Always there"),
    ("3", "Can run in isolation", "Yes — context: fork", "—"),
    ("4", "Frontmatter controls", "allowed-tools, disallowed-tools, argument-hint, context, agent …", "—"),
    ("5", "Best for", "⭐ On-demand workflows (review, deploy, fix-issue)", "⭐ Universal standards (pnpm, conventions)"),
    ("6", "Context cost", "Low until used", "Every request"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Needed by every task?"];
  MD [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="CLAUDE.md"];
  Q2 [shape=diamond, label="For the team?"];
  PROJ [shape=box, fillcolor="#DBEAFE", color="#0066CC", label=".claude/commands/ or\\n.claude/skills/ (in git)"];
  USER [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="~/.claude/skills/\\n(new name for a variant)"];
  Q3 [shape=diamond, label="Verbose output?"];
  FORK [shape=box, fillcolor="#FEF3C7", color="#D97706", label="context: fork"];
  Q4 [shape=diamond, label="Risky tools?"];
  DIS [shape=box, fillcolor="#FEF3C7", color="#D97706", label="disallowed-tools\\n(exam: allowed-tools)"];
  Q1 -> MD [label="yes"]; Q1 -> Q2 [label="no"]; Q2 -> PROJ [label="yes"]; Q2 -> USER [label="no"];
  PROJ -> Q3; USER -> Q3; Q3 -> FORK [label="yes"]; Q3 -> Q4 [label="no"]; FORK -> Q4; Q4 -> DIS [label="yes"];
}''')

EXPERIMENTS = (
    "Run ✅ on all six scenarios and read each log line.",
    "In ✅, delete “disallowed-tools: Bash” from /scaffold and run restrict_tools — that's ❌ C.",
    "In ✅, give USER a skill named review-pr too and run personal_variant: which /review-pr do YOU get? (docs: personal beats project).",
    "In the playground's “Tool limits” tab, switch the session to default mode with no disallowed-tools.",
    "In “Skill or CLAUDE.md?”, keep the standard in a skill and type “add a dependency”, then “run the tests”.",
)

QUESTIONS = (
    Question(
        q=("A team lead created a /release-notes command in ~/.claude/commands/ and told the team to use it. Teammates "
           "say the command doesn't exist in their sessions. What's the fix?"),
        opts=("Each teammate should restart Claude Code.",
              "Move it to the project's .claude/commands/ and commit it, so everyone gets it through version control.",
              "Add “use /release-notes” to CLAUDE.md.",
              "Rename it without the slash."),
        ans=1,
        explain=("Commands in ~/.claude/commands/ are personal. Project commands in .claude/commands/ are shared "
                 "through version control, which makes them available team-wide."),
        scenarios=(2,), points=("3.2:K1", "3.2:S1"),
    ),
    Question(
        q=("A /map-dependencies skill prints thousands of lines of analysis into the conversation, crowding out the "
           "developer's actual task. The developer only needs the summary. What's the best change?"),
        opts=("Add context: fork to the skill's frontmatter, so it runs in an isolated sub-agent and returns only its result.",
              "Tell the skill to be brief.",
              "Run /clear after using the skill.",
              "Move the skill into CLAUDE.md."),
        ans=0,
        explain=("context: fork runs a skill in an isolated sub-agent so verbose output doesn't pollute the main "
                 "conversation. /clear would throw away the developer's own context too."),
        scenarios=(2,), points=("3.2:K3", "3.2:S2", "3.2:K2"),
    ),
    Question(
        q=("A /generate-docs skill should only ever write documentation files, never run shell commands. According to "
           "the exam guide, which frontmatter setting restricts its tool access?"),
        opts=("argument-hint",
              "context: fork",
              "disable-model-invocation",
              "allowed-tools"),
        ans=3,
        explain=("The guide names allowed-tools in skill frontmatter as the way to restrict tool access during a skill. "
                 "Note: the current docs describe allowed-tools as pre-approving tools and disallowed-tools as removing "
                 "them. The concept page shows both; for the exam, follow the guide."),
        scenarios=(2,), points=("3.2:S3",),
    ),
    Question(
        q=("Developers keep invoking /fix-issue without the issue number, and Claude ends up fixing whatever issue it "
           "guesses. Which frontmatter addition helps most?"),
        opts=("context: fork",
              "allowed-tools: Read",
              "argument-hint: [issue-number]",
              "A longer description"),
        ans=2,
        explain=("argument-hint prompts developers for required parameters when they invoke the skill."),
        scenarios=(2,), points=("3.2:S4",),
    ),
    Question(
        q=("A developer wants a terser version of the team's shared /review-pr skill for their own use, without "
           "changing what teammates get. What should they do?"),
        opts=("Edit the project's skill and ask teammates not to pull.",
              "Add a note to CLAUDE.md telling Claude to be terse when they run it.",
              "Put a copy with the same name in ~/.claude/skills/ so it overrides the team version for everyone.",
              "Create a personal variant under a different name in ~/.claude/skills/."),
        ans=3,
        explain=("Personal variants go in ~/.claude/skills/ under different names, so teammates aren't affected and "
                 "there's no confusion about which version runs."),
        scenarios=(2, 4), points=("3.2:K4",),
    ),
    Question(
        q=("A skill's frontmatter lists allowed-tools: Read, Write, yet during the skill Claude still runs a Bash "
           "command (after asking permission). A developer expected Bash to be impossible. According to the current "
           "docs, why, and what would block it?"),
        opts=("allowed-tools pre-approves the listed tools but doesn't remove others; use disallowed-tools to take Bash away.",
              "allowed-tools only applies with context: fork.",
              "The frontmatter was cached; restart the session.",
              "Bash can never be restricted inside a skill."),
        ans=0,
        explain=("Per the skills docs, allowed-tools grants listed tools without prompting but doesn't restrict the "
                 "others; disallowed-tools removes them. The exam guide describes allowed-tools as restricting, which "
                 "is a guide-vs-docs difference recorded in SOURCES."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Commands or skills — which should I create?",
     "Both create / commands, and .claude/commands/ files still work. Skills add a folder for supporting files, frontmatter, and "
     "automatic invocation when a request matches their description. If both share a name, the skill wins."),
    ("So which answer do I give on the exam for “restrict tools in a skill”?",
     "allowed-tools — that's the guide's wording (TS 3.2 Skill 3). In current Claude Code, allowed-tools pre-approves tools. "
     "disallowed-tools is what removes them. This workbench teaches both and logs the difference in docs/SOURCES.md."),
    ("What does context: fork NOT carry over?",
     "The conversation history. The forked subagent sees only the skill's content as its task, so write self-contained "
     "instructions. Choose the subagent with `agent` (Explore for read-only analysis)."),
    ("Why a different name for a personal variant?",
     "The guide says so, to avoid affecting teammates. The docs add that a personal skill with the same name overrides the "
     "project one for you, so you'd silently stop getting the team's version."),
)

PLAYGROUND_INTRO = """
Type what the developer types — a /command with arguments, or a request — and move commands and skills around with the knobs.
Everything runs on the **simulated** loader and follows the skills docs.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="skills")


PLAYGROUND = (
    _tab("where", "⭐ Who can run it?", "where", "Shared drawer vs apron pocket.", "guide:3.2:K1",
         "Where /review-pr is stored and who can run it.", "skills § where skills live",
         ("who", "cmd_where"), {"who": "teammate", "cmd_where": "project_commands"}, ("/review-pr",),
         ("~/.claude/commands + teammate: unknown.", "~/.claude/commands + you: works.", ".claude/skills: works for everyone.")),
    _tab("fork", "⭐ context: fork", "fork", "Cook in the back kitchen, send out the plate.", "guide:3.2:K3",
         "A verbose analysis skill with and without context: fork.", "skills § context: fork",
         ("fork_on", "fork_agent"), {"fork_on": "yes", "fork_agent": "Explore"}, ("/analyze-codebase",),
         ("fork: +2,000 tokens.", "no fork: +40,000 tokens.")),
    _tab("tools", "⭐ Tool limits", "tools", "Lock the knife drawer while this recipe runs.", "guide:3.2:S3",
         "allowed-tools vs disallowed-tools for a scaffolding skill that strays into rm -rf.", "skills § Pre-approve tools; frontmatter",
         ("allowed_list", "disallowed_list", "session_mode"), {"allowed_list": "write_edit", "disallowed_list": "bash", "session_mode": "acceptEdits"},
         ("/scaffold Card",), ("no disallowed-tools + acceptEdits: build/ deleted.", "no disallowed-tools + default: a prompt is all that stops it.")),
    _tab("args", "⭐ argument-hint", "args", "“Serves: __” printed on the card.", "guide:3.2:S4",
         "/fix-issue with and without a hint.", "skills § frontmatter; arguments", ("hint_on",), {"hint_on": "yes"},
         ("/fix-issue", "/fix-issue 77"), ("no hint + /fix-issue: no number.", "no hint + /fix-issue 77: fine.")),
    _tab("skillmd", "⭐ Skill or CLAUDE.md?", "skillmd", "A recipe you pull out vs the sign on the wall.", "guide:3.2:S5",
         "Where the “use pnpm” standard lives, and whether an ordinary request gets it.", "features-overview § CLAUDE.md vs Skill",
         ("std_where",), {"std_where": "claude_md"}, ("run the tests before you commit", "add a dependency", "/package-manager then run tests"),
         ("skill + “run the tests”: npm.", "skill + “add a dependency”: matched → pnpm.", "CLAUDE.md: pnpm every time.")),
)

CONTENT = ConceptContent(
    slug="skills", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("claude-md-hierarchy", "agentic-tool-surface-selection", "subagents"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("team_command", "verbose_analysis", "restrict_tools", "missing_argument", "always_standard", "personal_variant"),
    show_ledger=False,
)
