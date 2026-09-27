"""
D3.4 Checkpoints & Session Management — undoing Claude's edits with /rewind (and what it can't undo), freeing context by
summarizing, branching to try another approach, and resuming a named session to rewind yesterday's work. PARTIAL in the
guide: TS 1.7 (named resume, fork_session; pp.8–9) and TS 5.4 Skill 5 (/compact; p.22); the word "checkpoints" is not in the
guide — the checkpoint mechanics are docs-only.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); checkpointing docs fetched 2026-09-28 (DOC_REFS). D1.4
Session State covers resume vs fresh-with-summary and crash recovery in depth. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Checkpointing — rewind, summarize, limitations", f"{_C}/checkpointing"),
    DocRef("Manage sessions — resume by name, branch (fork)", f"{_C}/sessions"),
)

GROUNDING = (
    Claim("Checkpointing captures the state of your code before each prompt you send that starts a turn; file snapshots are kept "
          "for the 100 most recent checkpoints; checkpoints are saved with the conversation, so /rewind works after you resume a "
          "session.", "docs", "checkpointing § How checkpoints work"),
    Claim("/rewind (or Esc twice on an empty prompt) opens the rewind menu: restore code and conversation, restore conversation, "
          "restore code, summarize from here, summarize up to here.", "docs", "checkpointing § Rewind and summarize"),
    Claim("Summarize keeps you in the same session and compresses context, like a targeted /compact; it doesn't change files. To "
          "try a different approach while preserving the original session, use /branch or claude --continue --fork-session.",
          "docs", "checkpointing § Guide a summary (note)"),
    Claim("Checkpointing does not track files modified by Bash commands (rm, mv, cp); only edits made through Claude's file "
          "editing tools are tracked. Background subagents' edits and external changes aren't restored either.", "docs",
          "checkpointing § Limitations"),
    Claim("Checkpoints are for quick, session-level recovery, not a replacement for version control such as git.", "docs",
          "checkpointing § Not a replacement for version control"),
    Claim("Named session resumption with --resume <session-name>; fork_session creates independent branches from a shared "
          "baseline to explore divergent approaches.", "guide", "TS 1.7 · Knowledge 1–2, Skills 1–2 · pp.8–9"),
    Claim("Use /compact to reduce context usage during extended sessions when context fills with verbose output.", "guide",
          "TS 5.4 · Skill 5 · p.22"),
    Claim("The guide never uses the word “checkpoints”; rewinding code is docs-only (📘) on this page.", "guide", "Guide v1.0 (keyword search)"),
    Claim("The files, prompts and token counts are invented.", "simulated", "utils/checkpoint_lab.py"),
)

CORRECT = r'''from utils.checkpoint_lab import run, session   # SIMULATED Claude Code session with checkpoints


def recover(s):
    problem = s["scenario"]
    if problem == "bad_edit":
        # undo Claude's file edits, keep the conversation (you still want the discussion)
        session.rewind(to_prompt=s["bad_prompt"], action="code")
    elif problem == "bash_rm":
        session.rewind(to_prompt=s["bad_prompt"], action="code")   # checkpoints undo Claude's file-tool edits...
        for path in s["deleted_by_bash"]:
            session.git_restore(path)                               # ...not Bash side effects: use git for those
    elif problem == "context_full":
        # compress everything AFTER the task brief; the brief itself stays word for word
        session.rewind(to_prompt=s["after_instructions"], action="summarize_from_here")
    elif problem == "try_alternative":
        session.branch()            # a new session with a copy of the history; approach A stays intact
    elif problem == "undo_yesterday":
        session.resume(s["session_name"])                          # checkpoints live in THAT session
        session.rewind(to_prompt=s["bad_prompt"], action="code")


run(recover)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# 📘 docs — "restore conversation" keeps the broken code
VARIANT_A = _swap(CORRECT, '''        # undo Claude's file edits, keep the conversation (you still want the discussion)
        session.rewind(to_prompt=s["bad_prompt"], action="code")''',
                  '''        session.rewind(to_prompt=s["bad_prompt"], action="conversation")   # WRONG: rewinds the chat, keeps the broken code''')
# 📘 docs — trusting rewind to undo a Bash deletion
VARIANT_B = _swap(CORRECT, '''        for path in s["deleted_by_bash"]:
            session.git_restore(path)                               # ...not Bash side effects: use git for those''',
                  '''        # WRONG: assumes the checkpoint also brings back what Bash deleted''')
# ⭐ TS 5.4 · Skill 5 — /clear instead of compacting
VARIANT_C = _swap(CORRECT, '''        # compress everything AFTER the task brief; the brief itself stays word for word
        session.rewind(to_prompt=s["after_instructions"], action="summarize_from_here")''',
                  '''        session.clear()   # WRONG: frees the context by throwing the task brief away too''')
# ⭐ TS 1.7 · Skill 2 — rewinding instead of branching
VARIANT_D = _swap(CORRECT, '''        session.branch()            # a new session with a copy of the history; approach A stays intact''',
                  '''        session.rewind(to_prompt=2, action="code_and_conversation")   # WRONG: throws approach A away to start B''')
# ⭐ TS 1.7 · Skill 1 — rewinding in a new session
VARIANT_E = _swap(CORRECT, '''        session.resume(s["session_name"])                          # checkpoints live in THAT session''',
                  '''        # WRONG: stays in today's new session - which has no checkpoints of yesterday's edits''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "checkpoint_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    from utils.checkpoint_lab import GIT
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "run() was never called"
    files = r["files"]
    code_ok = files.get("src/cart.py") == GIT["src/cart.py"] and files.get("src/tax.py") == GIT["src/tax.py"]
    txt = " · ".join(r["log"]) + f" · cart/tax restored: {code_ok} · config.json: {'present' if 'config.json' in files else 'MISSING'} · " \
          f"context {r['tokens']:,} · task brief kept: {r['instructions_kept']} · session '{r['session']}'"
    if sc in ("bad_edit", "undo_yesterday"):
        ok = code_ok and (sc != "bad_edit" or 2 in r["prompts"])
        return ok, (None if ok else ("NORESUME" if sc == "undo_yesterday" else "CONVONLY")), txt
    if sc == "bash_rm":
        ok = files.get("src/cart.py") == GIT["src/cart.py"] and "config.json" in files
        return ok, (None if ok else "BASHGONE"), txt
    if sc == "context_full":
        ok = r["tokens"] < 150_000 and r["instructions_kept"]
        return ok, (None if ok else "CLEARED"), txt
    ok = r["branches"] >= 1 and 2 in r["prompts"]
    return ok, (None if ok else "REWOUNDAWAY"), txt


EXPECTED = {
    "bad_edit": "cart.py and tax.py back to before prompt 2, with the conversation (prompt 2) still there",
    "bash_rm": "cart.py restored by the checkpoint AND config.json restored from git",
    "context_full": "context well below the window, with the task brief from prompt 1 kept word for word",
    "try_alternative": "a branch for approach B, with approach A's session still intact",
    "undo_yesterday": "yesterday's edits to cart.py and tax.py undone — by resuming that named session and rewinding",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":    ("#EDE9FE", "#7C3AED", "what went wrong"),
    "rw":   ("#DBEAFE", "#0066CC", "checkpoints & /rewind (📘 docs)"),
    "ses":  ("#CCFBF1", "#0D9488", "sessions: resume, branch, compact"),
    "git":  ("#FEF3C7", "#D97706", "version control"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "Q":      ("What do you need?", "diamond", "q"),
    "CODE":   ("Undo Claude's edits →\\n/rewind: restore code", "box", "rw"),
    "GIT":    ("Bash changes (rm, mv, cp),\\nexternal edits → git", "box", "git"),
    "SUMM":   ("⭐ Context full → summarize from\\nhere / /compact (keep the brief)", "box", "ses"),
    "BRANCH": ("⭐ Try another approach →\\n/branch · fork_session", "box", "ses"),
    "RESUME": ("⭐ Yesterday's work →\\n--resume <name>, then /rewind", "box", "ses"),
    "CONVONLY":    ("✗ “restore conversation”\\nkeeps the broken code", "box", "bug"),
    "BASHGONE":    ("✗ expecting /rewind to\\nundo a Bash rm", "box", "bug"),
    "CLEARED":     ("✗ /clear throws the\\nbrief away", "box", "bug"),
    "REWOUNDAWAY": ("✗ rewinding instead\\nof branching", "box", "bug"),
    "NORESUME":    ("✗ rewinding in a new\\nsession", "box", "bug"),
}
_BUGS = ["CONVONLY", "BASHGONE", "CLEARED", "REWOUNDAWAY", "NORESUME"]
_EXP = {"bad_edit": ["CODE"], "bash_rm": ["CODE", "GIT"], "context_full": ["SUMM"], "try_alternative": ["BRANCH"],
        "undo_yesterday": ["RESUME", "CODE"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 1.7 pp.8–9, TS 5.4 p.22)</FONT></TD></TR>')
    if hl:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = what this situation '
                 'needs · <B>red</B> = the bug your run shows</FONT></TD></TR>')
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
    lines += ['  Q -> CODE [label="undo edits"]; Q -> SUMM [label="context full"]; Q -> BRANCH [label="another approach"];',
              '  Q -> RESUME [label="an earlier session"]; CODE -> GIT [label="Bash / outside changes"]; RESUME -> CODE;',
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  GIT -> CONVONLY [style=invis];", _key(hl),
              f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"Q": ("ok", "")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this situation needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("1.7", "K", 1, "Named session resumption with --resume <session-name> continues a specific earlier conversation.",
              "✅ undo_yesterday · ❌ E"),
    ExamPoint("1.7", "K", 2, "fork_session creates independent branches from a shared baseline to explore divergent approaches.",
              "✅ try_alternative · ❌ D"),
    ExamPoint("1.7", "S", 1, "Use --resume with session names to continue named sessions across work sessions.", "✅ undo_yesterday"),
    ExamPoint("1.7", "S", 2, "Use fork_session for parallel exploration branches (two testing strategies, two refactoring approaches).",
              "✅ try_alternative · ❌ D"),
    ExamPoint("5.4", "S", 5, "Use /compact to reduce context usage when an extended session fills with verbose output.",
              "✅ context_full (summarize from here = a targeted /compact) · ❌ C"),
)

VARIANTS = (
    Variant("correct", "✅ restore code · git for Bash · summarize from here · ⭐ branch · ⭐ resume then rewind", "correct", CORRECT, "bad_edit",
            observe=("bad_edit: /rewind → restore code at prompt 2 → cart.py and tax.py restored, the conversation (prompt 2) kept. "
                     "bash_rm: the checkpoint restores cart.py; config.json (deleted by `rm`) comes back via git restore. "
                     "context_full: summarize from prompt 2 frees ~162,000 tokens; the brief in prompt 1 stays word for word. "
                     "try_alternative: /branch → 'work-branch'; 'work' (approach A) stays intact. undo_yesterday: --resume cart-pence, "
                     "then /rewind to prompt 2."),
            why="Each tool undoes exactly what it can: checkpoints undo Claude's file-tool edits in their own session; git covers the rest; summarize and branch keep what you still need."),
    Variant("A", "❌ A — “restore conversation” to undo broken code", "distractor", VARIANT_A, "bad_edit",
            observe="The conversation goes back to before prompt 2, but cart.py and tax.py keep their bugs.",
            why="Restore conversation keeps the current code; restore code is the option that reverts files (docs).",
            fix="Restore code (or code and conversation).", source="docs"),
    Variant("B", "❌ B — expecting /rewind to undo a Bash rm", "distractor", VARIANT_B, "bash_rm",
            observe="cart.py is restored, but “NOT restored (changed by Bash): ['config.json']” — config.json is still MISSING.",
            why="Checkpoints track only edits made by Claude's file-editing tools; rm, mv and cp through Bash aren't tracked (docs).",
            fix="Restore Bash-changed files from git.", source="docs"),
    Variant("C", "⭐❌ C — /clear when the context fills", "distractor", VARIANT_C, "context_full",
            observe="The context drops to 8,000 tokens — along with the task brief (“never touch tax.py”) and every finding.",
            why="/compact (or summarize from a point) keeps what matters while freeing space; /clear starts from nothing.",
            fix="Summarize from after the brief, or /compact.", source="guide:5.4:S5"),
    Variant("D", "⭐❌ D — rewinding instead of branching", "distractor", VARIANT_D, "try_alternative",
            observe="Restore code and conversation at prompt 2 throws away approach A's edits and discussion to make room for B.",
            why="To compare approaches from a shared baseline, fork the session (fork_session / /branch) — both stay available.",
            fix="/branch (or --fork-session).", source="guide:1.7:S2"),
    Variant("E", "⭐❌ E — rewinding in a new session", "distractor", VARIANT_E, "undo_yesterday",
            observe="“/rewind: no checkpoint for prompt 2 in session '(new)'” — cart.py and tax.py stay broken.",
            why="Checkpoints are saved with their conversation; resume that named session first, then rewind.",
            fix="claude --resume cart-pence, then /rewind.", source="guide:1.7:S1"),
)

TLDR = (
    "**Checkpoints** (docs) snapshot your code before every prompt. **`/rewind`** (or `Esc Esc`) offers:\n\n"
    "- **Restore code** — undo Claude's edits, keep the chat.\n"
    "- **Restore conversation** — rewind the chat, keep the code.\n"
    "- **Restore both.**\n"
    "- **Summarize from/up to here** — free context, like a targeted `/compact`.\n\n"
    "**Limits:**\n\n"
    "- Checkpoints **don't** undo **Bash** changes (`rm`, `mv`, `cp`) or outside edits; use **git** for those.\n"
    "- They live **in their session**. To undo yesterday's edits, **`--resume <name>`** first, then rewind.\n"
    "- **To try another approach, branch** (`/branch`, `fork_session`) instead of rewinding over the first one.\n\n"
    "The exam names `--resume`, `fork_session` and `/compact`. **Rewind itself is docs-only.**"
)
MENTAL_MODEL = ("Checkpoints are the undo history of Claude's own pen — they can erase what Claude wrote in this notebook, not "
                "what a shell command shredded (that's what git's filing cabinet is for). Summarizing folds up old pages; "
                "/clear throws the notebook away. Branching photocopies the notebook so you can try a second idea. Yesterday's "
                "undo history is in yesterday's notebook — open it (--resume) before you erase.")

WHAT_IT_IS = """
**Partly in the guide:** TS 1.7 covers named resumption and `fork_session` (pp.8–9). TS 5.4 Skill 5 covers `/compact` (p.22).
The **checkpoint and rewind mechanics are docs-only** — the guide never uses the word "checkpoints". D1.4 covers resuming vs
starting fresh with a summary, and crash recovery, in depth.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | Source |
|---|---|---|---|
| 1 | Checkpoint per prompt | Claude's pen keeps an undo history, one step per prompt you send. | 📘 docs |
| 2 | Restore code | Erase what the pen wrote; keep the conversation. | 📘 docs |
| 3 | Restore conversation | Tear out the chat pages; the code stays as it is. | 📘 docs |
| 4 | Bash & outside changes | The pen's undo can't un-shred — use git's filing cabinet. | 📘 docs |
| 5 | Summarize / `/compact` | Fold up old pages instead of throwing the notebook away. | ⭐ TS 5.4 · Skill 5 |
| 6 | Branch / `fork_session` | Photocopy the notebook to try a second idea. | ⭐ TS 1.7 · Knowledge 2, Skill 2 |
| 7 | `--resume <name>` | Yesterday's undo history is in yesterday's notebook. | ⭐ TS 1.7 · Knowledge 1, Skill 1 |
| 8 | Not version control | Checkpoints are a quick undo, not your history of record. | 📘 docs |

**The rewind menu** (docs)

| # | Option | Code | Conversation | Use it when |
|---|---|---|---|---|
| 1 | Restore code and conversation | Reverted | Reverted | Start that step over completely |
| 2 | Restore conversation | **Kept** | Reverted | The chat went off track but the code is fine |
| 3 | Restore code | Reverted | **Kept** | Claude's edits broke something; keep the discussion |
| 4 | Summarize from here | Unchanged | Later messages compressed | Context is full; keep your opening brief intact |
| 5 | Summarize up to here | Unchanged | Earlier messages compressed | Keep recent detail; compress the start |

**Undo, compress, branch or resume?** (session actions side by side)

| # | Need | Action | Keeps the original? | Exam reference |
|---|---|---|---|---|
| 1 | Undo Claude's file edits | `/rewind` → restore code | — | 📘 docs |
| 2 | Undo `rm` / `mv` / outside edits | git | — | 📘 docs |
| 3 | Free context, keep the essentials | Summarize from here / `/compact` | Same session | ⭐ TS 5.4 · Skill 5 |
| 4 | Try a second approach | `/branch`, `--fork-session`, `fork_session` | ✅ Yes — both sessions | ⭐ TS 1.7 · Skill 2 |
| 5 | Continue (or undo) yesterday's work | `claude --resume <name>` (then `/rewind`) | Same session | ⭐ TS 1.7 · Skill 1 |
| 6 | Prior tool results are stale | New session + a structured summary | — | ⭐ TS 1.7 · Skill 3 (see D1.4) |
"""

HOW_IT_WORKS = """
1. **Claude broke something?** Run `/rewind` → **restore code** at the prompt before the damage.
2. **Did a Bash command change files?** (`rm`, `mv`, `cp`) Checkpoints can't bring those back; restore them from **git**.
3. **Context full?** Summarize **from** the point after your brief, or run `/compact` — not `/clear`.
4. **Want to try another approach?** **Branch** (`/branch`, `--fork-session`). Rewinding would replace the first approach.
5. **Undoing yesterday?** `claude --resume <name>` first; that session's checkpoints are saved with it.
"""

WHERE_SEEN = """
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): exploring alternatives, recovering from bad edits.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): named sessions, compacting long explorations.
"""

GUIDE_NOTE = ("Partly in the guide: TS 1.7 (pp.8–9) and TS 5.4 Skill 5 (p.22); checkpoints and /rewind come from the Claude Code "
              "docs (verified 2026-09-28 — pages listed above). Section layout inspired by a community concept list "
              "(claudearchitectcertification.com — community source, unverified; no text copied).")

LAB_INTRO = """
Five things went wrong in a **simulated** Claude Code session. You write `recover(situation)` using documented actions:

- `rewind(to_prompt, action)` — the options in the /rewind menu;
- `compact()` and `clear()`;
- `git_restore(path)`;
- `branch()`;
- `resume(name)`.

The lab shows what came back, what didn't, and what you kept.
"""

DISTRACTORS = (
    ("A · Restore conversation to fix code", "Go back to before the mistake.", "The code keeps its bugs.", "Restore code.", "docs"),
    ("B · /rewind for a Bash rm", "Rewind undoes the step.", "Bash changes aren't tracked.", "git restore.", "docs"),
    ("C · /clear when the context fills", "A clean slate.", "The brief and findings are gone.", "Summarize / /compact.", "guide:5.4:S5"),
    ("D · Rewind to try approach B", "Start B from the same point.", "Approach A is thrown away.", "/branch · fork_session.", "guide:1.7:S2"),
    ("E · Rewind in a new session", "Rewind is global.", "Yesterday's checkpoints are in yesterday's session.", "--resume <name> first.", "guide:1.7:S1"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Checkpoints (/rewind)", "Git")
SIDE_BY_SIDE_ROWS = (
    ("1", "Tracks", "Edits by Claude's file-editing tools, per prompt", "Everything you commit"),
    ("2", "Bash rm / mv / cp", "Not tracked", "Tracked (if committed)"),
    ("3", "Outside edits, other sessions", "Normally not tracked", "Tracked (if committed)"),
    ("4", "Lifetime", "The session (last 100 checkpoints; ~30-day cleanup by default)", "Permanent"),
    ("5", "Undoes the conversation too", "Yes (optional)", "—"),
    ("6", "Purpose", "Quick session-level recovery", "History of record, collaboration"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="What do you need?"];
  Q2 [shape=diamond, label="Changed by Claude's\\nfile tools?"];
  RW [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="/rewind → restore code"];
  GIT [shape=box, fillcolor="#FEF3C7", color="#D97706", label="git"];
  SUM [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Summarize from here\\nor /compact"];
  BR [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="/branch · fork_session"];
  RES [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="--resume <name>,\\nthen /rewind"];
  Q1 -> Q2 [label="undo changes"]; Q2 -> RW [label="yes"]; Q2 -> GIT [label="no (Bash, outside)"];
  Q1 -> SUM [label="free context"]; Q1 -> BR [label="try another way"]; Q1 -> RES [label="yesterday's session"];
}''')

EXPERIMENTS = (
    "Run ✅ on all five situations and read which files came back and which didn't.",
    "In ✅'s bad_edit branch, try action=\"code_and_conversation\": what else did you lose?",
    "Run ❌ B and find the “NOT restored (changed by Bash)” line.",
    "In the playground's context tab, compare “summarize up to here” with “summarize from here”.",
    "In the resume tab, turn “resume first” off and rewind to prompt 2.",
)

QUESTIONS = (
    Question(
        q=("Two hours into exploring a legacy codebase, the session is full of verbose search and file output, and Claude's "
           "answers are getting vaguer. The developer wants to keep working in this session with the key findings intact, "
           "without losing the thread of the investigation. What should they do?"),
        opts=("Run /clear, then paste in whatever they remember of the key findings to start the next part.",
              "Run /compact, so the history is summarised and the key findings carry on in less context.",
              "Run /rewind to the start of the session, so the verbose output is removed from the history.",
              "Open a second terminal with a new session, and alternate between the two sessions as needed."),
        ans=1,
        explain=("/compact summarises the history, freeing context from verbose discovery output while keeping the thread. A "
                 "throws everything away and relies on memory. C also rewinds away the findings. D splits the work across "
                 "two contexts, and neither has the full picture."),
        scenarios=(2, 4), points=("5.4:S5",),
    ),
    Question(
        q=("After a shared 40-minute analysis, a developer tried refactoring approach A, rewound, then tried approach B. "
           "Now they can't compare the two properly, because A's exploration is gone. The team lead asks what they should "
           "have used to explore both from the same starting point. What is the answer?"),
        opts=("Forked sessions from the analysis point, one branch per approach.",
              "Two /compact runs, one after each approach, to keep both summaries.",
              "One session, exploring both approaches one after the other in turn.",
              "/clear between the approaches, with a scratchpad note about approach A."),
        ans=0,
        explain=("Forking creates independent branches from a shared baseline, so both explorations survive side by side. B and "
                 "C let A's exploration influence B's. D keeps only a note about A and loses the shared analysis as well."),
        scenarios=(2,), points=("1.7:K2", "1.7:S2"),
    ),
    Question(
        q=("A developer plans to /clear the session before the next part of a long investigation. The findings so far (which "
           "classes own which of 14 tables, and two confirmed bugs) must not be lost. Last time they relied on memory and got "
           "3 of the table owners wrong. What is the best practice?"),
        opts=("Skip /clear and keep going, since the findings are safer in the current context than anywhere else.",
              "Run /compact instead of /clear, and trust the summary to keep all 14 owners and both bugs exact.",
              "Write the key findings to a scratchpad file first, and point the new context at that file.",
              "Ask Claude after the /clear to restate the findings from what it recalls of the earlier context."),
        ans=2,
        explain=("A scratchpad file persists findings across context boundaries and can be referenced later. A keeps a degrading "
                 "context. B hopes a summary keeps 16 exact facts. D asks for recall of a context that /clear has "
                 "discarded."),
        scenarios=(4,), points=("5.4:K2", "5.4:S2"),
    ),
    Question(
        q=("In one session, Claude ran rm old_config.json through Bash, then edited two source files with its edit tools. "
           "The developer opens /rewind to go back to before both changes, expecting all three files to come back. What "
           "will be restored?"),
        opts=("All three files, because checkpoints capture every change that is made during the session.",
              "Only old_config.json, since checkpoints track file deletions but not the contents of edits.",
              "Nothing, because /rewind restores only the conversation and never the files that were changed.",
              "The two edited files; checkpoints don't track Bash, so old_config.json stays deleted."),
        ans=3,
        explain=("Checkpoints track changes made by Claude's file-editing tools. Changes made through Bash commands aren't "
                 "tracked, so they can't be rewound. A, B and C each misstate what checkpoints cover."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
    Question(
        q=("Claude's last three edits broke the build, but the conversation itself (a 30-minute analysis and an agreed "
           "approach) is valuable. The developer wants the files back without losing the discussion. Which /rewind choice "
           "fits?"),
        opts=("Restore conversation only, which rewinds the discussion and keeps the broken edits on disk.",
              "Restore code and conversation, which rewinds both and starts the discussion over again.",
              "Restore code only, which reverts the file changes and keeps the conversation as it is.",
              "Summarize from here, which condenses the later messages and leaves every file unchanged."),
        ans=2,
        explain=("Restoring code only reverts the files and keeps the conversation. A does the opposite. B loses the analysis. "
                 "D compresses messages but doesn't fix the build."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
    Question(
        q=("A team decides that since Claude Code has checkpoints, they no longer need to commit work in progress. A week "
           "later, a teammate's laptop is replaced and three days of uncommitted work are gone. What do the docs say about "
           "checkpoints?"),
        opts=("They sync to the cloud, so the work can be restored on the new laptop from the account.",
              "They are local session undo, not a replacement for version control; keep committing to git.",
              "They replace commits for work in progress, but must be exported before a machine is replaced.",
              "They keep 30 days of history, so the work can be restored by resuming the old session."),
        ans=1,
        explain=("The docs describe checkpoints as local undo for a session, alongside version control, not instead of it. A, C "
                 "and D invent sync, export and retention features."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Is “checkpoints” on the exam?",
     "The word isn't in guide v1.0. What the exam covers nearby is TS 1.7 (--resume <name>, fork_session, resume vs fresh start) "
     "and TS 5.4 (/compact, scratchpads, subagents). Checkpoints are a docs feature worth knowing for real work."),
    ("Do checkpoints survive closing Claude Code?",
     "Yes — they're saved with the conversation, so /rewind works after you resume that session. File snapshots are kept for "
     "the 100 most recent checkpoints and cleaned up about 30 days after the session last saved one (configurable)."),
    ("Summarize from here or /compact?",
     "Both compress context in the same session. Summarize from here lets you pick the point, so your opening brief stays word "
     "for word. /compact compresses the whole conversation. /clear throws it away."),
    ("Does rewinding undo what a subagent changed?",
     "Usually not. Only a foreground forked skill's edits are captured. For other subagents, including background forks, the "
     "docs say to use git."),
)

PLAYGROUND_INTRO = """
Each tab is one of the lab's situations. In the rewind tabs, type the prompt number to rewind to; in the context tab, type
what the summary should focus on. It all runs on the **simulated** session with checkpoints.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="checkpoint")


PLAYGROUND = (
    _tab("rewind", "The rewind menu", "rewind", "Erase what the pen wrote — or tear out the chat pages.", "",
         "📘 Docs only: Claude's prompt 2 broke cart.py and tax.py.", "checkpointing § Rewind and summarize",
         ("rw_action",), {"rw_action": "code"}, ("2", "1"),
         ("restore conversation: code still broken.", "code and conversation: code fixed, discussion gone.")),
    _tab("bash", "Bash changes", "bash", "The pen's undo can't un-shred.", "",
         "📘 Docs only: prompt 1 edited cart.py and ran rm config.json.", "checkpointing § Limitations",
         ("git_too",), {"git_too": "yes"}, ("1",), ("no git: config.json stays missing.",)),
    _tab("context", "⭐ Context full", "context", "Fold up old pages; don't throw the notebook away.", "guide:5.4:S5",
         "184k of 200k tokens used; the brief is in prompt 1.", "checkpointing § Summarize; guide TS 5.4 Skill 5",
         ("ctx_action",), {"ctx_action": "summarize_from_here"}, ("keep the billing brief",),
         ("clear: brief gone.", "summarize up to here: brief only a summary, context still ~180k.", "compact: brief kept.")),
    _tab("branch", "⭐ Try another approach", "branch", "Photocopy the notebook for the second idea.", "guide:1.7:S2",
         "Approach A is half done; try B from the same analysis.", "checkpointing note; sessions § branch; guide TS 1.7",
         ("alt_action",), {"alt_action": "branch"}, ("Try approach B",), ("rewind: approach A is gone.",)),
    _tab("resume", "⭐ Yesterday's session", "resume", "Open yesterday's notebook before you erase.", "guide:1.7:S1",
         "Undo edits made yesterday in the named session cart-pence.", "checkpointing § How checkpoints work; guide TS 1.7",
         ("resume_first",), {"resume_first": "yes"}, ("2",), ("no resume: nothing to rewind.",)),
)

CONTENT = ConceptContent(
    slug="checkpoints", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("session-state", "plan-mode", "skills"), exam_points=EXAM_POINTS, playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO, scenarios=("bad_edit", "bash_rm", "context_full", "try_alternative", "undo_yesterday"),
    show_ledger=False,
)
