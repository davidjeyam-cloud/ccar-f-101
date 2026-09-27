"""
D4.10 Multi-Instance & Multi-Pass Review Architectures — an independent reviewer instead of self-review, per-file passes plus a
cross-file integration pass instead of one diluted pass, and a verification pass with per-finding confidence for routing.
Guide TS 4.6 (p.19). D1.8 (task decomposition) covers the per-file + integration split from the planning side.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); platform prompting best practices fetched 2026-09-28
(DOC_REFS). Every claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (DocRef("Prompting best practices — Chain complex prompts (self-correction)",
                   f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices"),)

GROUNDING = (
    Claim("Explicit prompt chaining is useful when you need to inspect intermediate outputs or enforce a pipeline; the most common "
          "pattern is self-correction: generate a draft → have Claude review it against criteria → refine, each step a separate "
          "API call you can log, evaluate or branch.", "docs", "prompting best practices § Chain complex prompts"),
    Claim("Self-review is limited: a model keeps its reasoning context from generation and is less likely to question its own "
          "decisions in the same session; an independent review instance without that context catches subtle issues more "
          "effectively than self-review instructions or extended thinking; split large reviews into per-file local passes plus "
          "cross-file integration passes to avoid attention dilution and contradictory findings.", "guide", "TS 4.6 · Knowledge 1–3 · p.19"),
    Claim("Skills: a second, independent Claude instance reviews generated code without the generator's reasoning; per-file passes "
          "for local issues plus separate integration passes for cross-file data flow; verification passes where the model "
          "self-reports confidence per finding to enable calibrated review routing.", "guide", "TS 4.6 · Skills 1–3 · p.19"),
    Claim("Per-file passes plus a separate cross-file integration pass avoid attention dilution.", "guide", "TS 1.6 · Skill 2 · p.8"),
    Claim("Self-reported confidence is a routing signal here (TS 4.6 S3) and must be calibrated (TS 5.5); TS 5.2 warns that it's an "
          "unreliable proxy for deciding when to ESCALATE a customer case — different decisions.", "guide", "TS 4.6 S3 vs TS 5.2 K / TS 5.5"),
    Claim("The generator's bug, the reviewers' behaviour (same session misses, new instance catches), the 14-file PR and the "
          "calibrated confidences are invented.", "simulated", "utils/mpreview_lab.py"),
)

CORRECT = r'''from utils.mpreview_lab import (CANDIDATES, FILES, SCENARIO, finish, generate, integration_review, per_file_review,
                                 review, route, verify)   # SIMULATED generator + reviewers

if SCENARIO in ("self_review", "extended_thinking"):
    code = generate("paginate the orders list")
    # a SECOND, independent instance reviews the code - without the generator's reasoning
    review(code, session="new")

elif SCENARIO in ("large_pr", "cross_file"):
    # focused per-file passes for local issues...
    local = [f for path in FILES for f in per_file_review(path)]
    # ...plus an integration pass for data flow across files
    integration_review(FILES, summaries=local)

else:  # calibrated_routing
    verified = verify(CANDIDATES, with_confidence=True)   # each finding carries the model's confidence
    route(verified, auto_post_at=0.8)                        # high confidence -> auto-comment; the rest -> a human

finish()
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ TS 4.6 · Knowledge 1 / Skill 1 — self-review in the generator's session
VARIANT_A = _swap(CORRECT, '''    review(code, session="new")''', '''    review(code, session="same", instructions="review your code critically")   # WRONG: same session''')
# ⭐ TS 4.6 · Knowledge 2 — extended thinking instead of an independent instance
VARIANT_B = _swap(CORRECT, '''    review(code, session="new")''', '''    review(code, session="same", extended_thinking=True)   # WRONG: more thinking, same reasoning context''')
# ⭐ TS 4.6 · Knowledge 3 — one pass over the whole PR
VARIANT_C = _swap(CORRECT, '''    local = [f for path in FILES for f in per_file_review(path)]
    # ...plus an integration pass for data flow across files
    integration_review(FILES, summaries=local)''', '''    from utils.mpreview_lab import one_pass_review
    one_pass_review(FILES)   # WRONG: all 14 files in one pass''')
# ⭐ TS 4.6 · Skill 2 — per-file passes only
VARIANT_D = _swap(CORRECT, '''    # ...plus an integration pass for data flow across files
    integration_review(FILES, summaries=local)''', '''    # WRONG: no integration pass''')
# ⭐ TS 4.6 · Skill 3 — no confidence, so no calibrated routing
VARIANT_E = _swap(CORRECT, '''    verified = verify(CANDIDATES, with_confidence=True)   # each finding carries the model's confidence
    route(verified, auto_post_at=0.8)                        # high confidence -> auto-comment; the rest -> a human''',
                  '''    verified = verify(CANDIDATES, with_confidence=False)
    route(verified, auto_post_at=None)   # WRONG: no confidence - everything auto-posted''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "mpreview_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "finish() was never called"
    txt = (" · ".join(r["passes"]) + f" · generator bug caught: {r['caught_gen_bug']} · local issues caught: {len(r['local_caught'])}/4 · "
           f"cross-file caught: {r['cross_caught']} · contradictions: {r['contradictions']} · routed: {r['routed']}")
    if sc in ("self_review", "extended_thinking"):
        if r["caught_gen_bug"]:
            return True, None, txt
        return False, ("THINKING" if (r["reviewer"] or {}).get("extended_thinking") else "SELF"), txt
    if sc == "large_pr":
        ok = len(r["local_caught"]) == 4 and not r["contradictions"]
        return ok, (None if ok else "ONEPASS"), txt
    if sc == "cross_file":
        ok = r["cross_caught"]
        return ok, (None if ok else ("ONEPASS" if r["contradictions"] else "NOINTEG")), txt
    rt = r["routed"] or {}
    ok = not rt.get("auto_false") and rt.get("human_load", 99) <= 3
    return ok, (None if ok else "NOCONF"), txt


EXPECTED = {
    "self_review": "the page=0 bug is caught by an independent reviewer",
    "extended_thinking": "the page=0 bug is caught — by an independent instance, not by thinking longer",
    "large_pr": "all 4 local issues caught, no contradictory findings",
    "cross_file": "the cross-file rename (total → amount) is caught by an integration pass",
    "calibrated_routing": "no false positive auto-posted; only the low-confidence findings go to a human",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "gen":  ("#EDE9FE", "#7C3AED", "generation"),
    "rev":  ("#DBEAFE", "#0066CC", "independent review"),
    "pass": ("#CCFBF1", "#0D9488", "multi-pass"),
    "ver":  ("#FEF3C7", "#D97706", "verification & routing"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "GEN":   ("Generator writes the code\\n(its session holds its reasoning)", "box", "gen"),
    "INDEP": ("⭐ A NEW instance reviews\\nthe code only", "box", "rev"),
    "LOCAL": ("⭐ Per-file passes\\n(local issues)", "box", "pass"),
    "INTEG": ("⭐ Integration pass\\n(cross-file data flow)", "box", "pass"),
    "VERIFY": ("⭐ Verification pass: a\\nconfidence per finding", "box", "ver"),
    "ROUTE": ("High → auto-comment;\\nlow → a human", "box", "ver"),
    "SELF":     ("✗ self-review in the\\ngenerator's session", "box", "bug"),
    "THINKING": ("✗ “think longer” instead\\nof a fresh reviewer", "box", "bug"),
    "ONEPASS":  ("✗ one pass over\\n14 files", "box", "bug"),
    "NOINTEG":  ("✗ per-file passes,\\nno integration pass", "box", "bug"),
    "NOCONF":   ("✗ no confidence →\\nno routing", "box", "bug"),
}
_BUGS = ["SELF", "THINKING", "ONEPASS", "NOINTEG", "NOCONF"]
_EXP = {"self_review": ["GEN", "INDEP"], "extended_thinking": ["GEN", "INDEP"], "large_pr": ["LOCAL"], "cross_file": ["LOCAL", "INTEG"],
        "calibrated_routing": ["VERIFY", "ROUTE"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 4.6 p.19)</FONT></TD></TR>')
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
    lines += ['  GEN -> INDEP [label="small change"]; GEN -> LOCAL [label="large PR"]; { rank=same; INDEP; LOCAL; }',
              "  LOCAL -> INTEG; INDEP -> VERIFY; INTEG -> VERIFY; VERIFY -> ROUTE;",
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  ROUTE -> SELF [style=invis];", _key(hl),
              f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this scenario needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("4.6", "K", 1, "Self-review is limited: the model keeps its generation reasoning and is less likely to question its own decisions in the same session.",
              "✅ self_review · ❌ A"),
    ExamPoint("4.6", "K", 2, "Independent review instances (no prior reasoning context) catch subtle issues better than self-review instructions or extended thinking.",
              "✅ extended_thinking · ❌ B"),
    ExamPoint("4.6", "K", 3, "Multi-pass review: per-file local passes plus cross-file integration passes avoid attention dilution and contradictory findings.",
              "✅ large_pr, cross_file · ❌ C · ❌ D"),
    ExamPoint("4.6", "S", 1, "Use a second, independent Claude instance to review generated code without the generator's reasoning.", "✅ review(session=\"new\")"),
    ExamPoint("4.6", "S", 2, "Split large multi-file reviews into focused per-file passes plus separate integration passes for cross-file data flow.",
              "✅ per_file_review + integration_review · ❌ D"),
    ExamPoint("4.6", "S", 3, "Run verification passes where the model reports confidence per finding, to enable calibrated review routing.",
              "✅ calibrated_routing · ❌ E"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ independent reviewer · per-file + integration passes · confidence-based routing", "correct", CORRECT, "self_review",
            observe=("self_review / extended_thinking: a new instance given only the code finds “page(items, 0, size) returns an empty "
                     "page”. large_pr: 14 per-file passes catch all 4 local issues, no contradictions. cross_file: the integration pass "
                     "catches “file_04 renames total → amount; file_12 still reads total”. calibrated_routing: 3 high-confidence findings "
                     "auto-posted, 3 low-confidence to a human, no false positive posted."),
            why="Each check is done by a reviewer with the right context: none of the generator's reasoning, one file at a time, then the whole flow."),
    Variant("A", "⭐❌ A — self-review in the generator's session", "distractor", VARIANT_A, "self_review",
            observe="Told to “review your code critically”, the same session finds nothing — it shares the reasoning “I handled the empty page”.",
            why="A model keeps its generation reasoning and is less likely to question its own decisions in the same session.",
            fix="A second, independent instance with only the code.", source="guide:4.6:K1"),
    Variant("B", "⭐❌ B — extended thinking instead of a fresh reviewer", "distractor", VARIANT_B, "extended_thinking",
            observe="More thinking, same session, same blind spot — 0 findings.",
            why="The guide: independent instances catch subtle issues better than self-review instructions or extended thinking.",
            fix="An independent reviewer instance.", source="guide:4.6:K2"),
    Variant("C", "⭐❌ C — one pass over a 14-file PR", "distractor", VARIANT_C, "large_pr",
            observe="Files 5–10 are skimmed (2 of 4 local issues found) and file_03 is judged both “looks fine” and “missing validation”.",
            why="Attention dilutes across many files, producing misses and contradictory findings.",
            fix="Per-file passes plus an integration pass.", source="guide:4.6:K3"),
    Variant("D", "⭐❌ D — per-file passes only", "distractor", VARIANT_D, "cross_file",
            observe="All 4 local issues found, but the rename that breaks file_12 (total → amount in file_04) is missed.",
            why="Cross-file data flow is invisible to a pass that sees one file; it needs a separate integration pass.",
            fix="Add an integration pass fed with the per-file summaries.", source="guide:4.6:S2"),
    Variant("E", "⭐❌ E — no confidence, no routing", "distractor", VARIANT_E, "calibrated_routing",
            observe="All 6 findings auto-posted, including “util.py:3 unused variable?” and “api.py:10 naming” — both false positives.",
            why="A per-finding confidence (from a verification pass) is what makes calibrated routing possible.",
            fix="Verification pass with confidence; auto-post above a calibrated threshold.", source="guide:4.6:S3"),
)

TLDR = (
    "Don't let the author mark their own homework. A model reviewing its code **in the same session** shares the reasoning that "
    "produced the bug. Telling it to be critical, or giving it **extended thinking**, doesn't fix that. A **second, independent "
    "instance** given only the code does.\n\n"
    "For big PRs:\n\n"
    "- **Per-file passes** catch local issues.\n"
    "- A separate **integration pass** catches cross-file data flow.\n"
    "- One giant pass dilutes attention and contradicts itself.\n\n"
    "A **verification pass with a confidence per finding** lets you auto-post the sure ones and route the rest to a person, "
    "once the confidence is **calibrated**. The docs describe the same draft → review → refine chain as separate calls."
)
MENTAL_MODEL = ("Proof-reading your own essay, you read what you meant, not what you wrote — thinking harder doesn't help; a "
                "friend who never saw your notes spots the typo at once. For a 14-chapter book, check each chapter on its own, "
                "then read the whole plot once for continuity. And sort the friend's notes by how sure they are.")

WHAT_IT_IS = """
The exam guide covers multi-instance and multi-pass review architectures (Guide §6 · TS 4.6, p.19). The docs describe the
self-correction chain (generate → review against criteria → refine) as separate API calls. D1.8 plans the per-file +
integration split.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Self-review limits | Proof-reading your own essay: you read what you meant. | ⭐ TS 4.6 · Knowledge 1 |
| 2 | Independent reviewer instance | A friend who never saw your notes. | ⭐ TS 4.6 · Knowledge 2, Skill 1 |
| 3 | Extended thinking isn't a fresh pair of eyes | Re-reading harder doesn't un-know your intent. | ⭐ TS 4.6 · Knowledge 2 |
| 4 | Per-file passes | Check each chapter on its own. | ⭐ TS 4.6 · Knowledge 3, Skill 2 |
| 5 | Integration pass | Then read the whole plot once for continuity. | ⭐ TS 4.6 · Skill 2 |
| 6 | Verification pass + confidence | Sort the friend's notes by how sure they are. | ⭐ TS 4.6 · Skill 3 |
| 7 | Self-correction chain as separate calls | Draft, review, refine — each step logged. | 📘 docs |

**Self-review vs independent review**

| # | Aspect | Self-review (same session) | Independent instance |
|---|---|---|---|
| 1 | Context | The generator's reasoning | Only the code (+ criteria) |
| 2 | Questions its own decisions | Rarely | Yes |
| 3 | Fixed by “be critical” or extended thinking? | No (guide) | — |
| 4 | Result here | 0 findings | The page=0 bug found |

**One pass vs multi-pass** (a 14-file PR)

| # | Plan | Local issues | Cross-file flow | Contradictions |
|---|---|---|---|---|
| 1 | One pass | 2 / 4 | Missed | Yes (file_03 both ways) |
| 2 | Per-file passes only | 4 / 4 | Missed | No |
| 3 | ⭐ Per-file + integration pass | 4 / 4 | Caught | No |

**Confidence: routing vs escalation** (don't mix them up)

| # | Use of self-reported confidence | Guide |
|---|---|---|
| 1 | Routing review findings (auto-post vs human), once calibrated | ⭐ TS 4.6 · Skill 3; TS 5.5 |
| 2 | Deciding when to escalate a customer case to a human | ⭐ TS 5.2 — an unreliable proxy |
"""

HOW_IT_WORKS = """
1. **Generated code?** Review it with a **new instance** that gets only the code and the criteria, not the generator's
   session.
2. **Large PR?** Run a **per-file pass** for each file, then an **integration pass** given the per-file summaries to check
   data flow across files.
3. **Many findings?** Run a **verification pass** that attaches a confidence to each finding. Calibrate the threshold on
   labelled data, auto-post above it, and send the rest to a person.
"""

WHERE_SEEN = """
- **Scenario 5 — Claude Code for Continuous Integration** (Guide §5, p.4): automated PR review at scale.
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): reviewing generated code.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 4.6 (p.19) and the platform prompting best practices (verified 2026-09-28). "
              "Section layout inspired by a community concept list (claudearchitectcertification.com — community source, "
              "unverified; no text copied).")

LAB_INTRO = """
A **simulated** generator writes a pagination function with a page=0 bug. Its session holds the reasoning “I handled the empty
page”. You wire up the review:

- which instance reviews the function;
- how a 14-file PR is split into passes;
- how verified findings are routed.

Five scenarios.
"""

DISTRACTORS = (
    ("A · Self-review in the same session", "It wrote it, it knows it.", "It shares the blind spot.", "An independent instance.", "guide:4.6:K1"),
    ("B · Extended thinking", "More reasoning finds more.", "Same context, same blind spot.", "A fresh reviewer.", "guide:4.6:K2"),
    ("C · One pass over 14 files", "It sees everything at once.", "Diluted attention, contradictions.", "Per-file + integration.", "guide:4.6:K3"),
    ("D · Per-file passes only", "Each file gets full attention.", "Cross-file flow is invisible.", "Add an integration pass.", "guide:4.6:S2"),
    ("E · No confidence", "Post every finding.", "False positives posted.", "Verification pass + threshold.", "guide:4.6:S3"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Pass", "Sees", "Catches")
SIDE_BY_SIDE_ROWS = (
    ("1", "Per-file", "One file", "Local bugs (off-by-one, SQL from input, None, timezone)"),
    ("2", "Integration", "All files + per-file summaries", "Cross-file data flow (renamed fields, mismatched contracts)"),
    ("3", "Independent review", "The code only, no generator reasoning", "What the author took for granted"),
    ("4", "Verification", "The findings", "A confidence per finding, for routing"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Reviewing code\\nClaude just wrote?"];
  INDEP [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Independent instance\\n(code only)"];
  Q2 [shape=diamond, label="Many files?"];
  PASSES [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Per-file passes +\\nintegration pass"];
  ONE [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="One focused pass"];
  VER [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Verification pass:\\nconfidence → routing"];
  Q1 -> INDEP [label="yes"]; Q1 -> Q2 [label="no"]; INDEP -> Q2; Q2 -> PASSES [label="yes"]; Q2 -> ONE [label="no"];
  PASSES -> VER; ONE -> VER;
}''')

EXPERIMENTS = (
    "Run ✅ on all five scenarios.",
    "In ✅, switch the reviewer to session=\"same\" and add instructions=\"be very critical\": does it help?",
    "Run ⭐❌ D on cross_file and compare with ✅'s integration line.",
    "In the playground's routing tab, try thresholds 0.8 and 0.5 and see what reaches a human.",
)

QUESTIONS = (
    Question(
        q=("Claude Code generates a pagination feature, and in the same session the developer asks it to “review your code "
           "critically”. It reports no issues, yet QA finds that page 0 returns an empty page, the third such miss this "
           "month. The team proposes enabling extended thinking for the self-review. What is the most effective change?"),
        opts=("Enable extended thinking as proposed, so the self-review reasons far more deeply about its own code.",
              "Review with a second, independent instance that sees only the code, not the generator's reasoning.",
              "Ask the same session to review the code three times, and treat any issue found even once as real.",
              "Add “be extremely critical of your own work” to the review request made in the same session."),
        ans=1,
        explain=("A model reviewing its own output in the same session keeps the reasoning that produced the bug, so it is "
                 "unlikely to question it. An independent instance without that context catches more. A and C deepen or "
                 "repeat the same biased review. D is an instruction that doesn't remove the bias."),
        scenarios=(2, 5), points=("4.6:K1", "4.6:K2", "4.6:S1"),
    ),
    Question(
        q=("A single review pass over a 30-file pull request misses issues in the middle files, and in one review it called "
           "the same file both “fine” and “missing validation”. A teammate proposes switching to a model with a larger context "
           "window. How should you evaluate this?"),
        opts=("Adopt it, since a larger window gives each of the 30 files more room and therefore more attention.",
              "Adopt it, and sort the files by size so the largest ones come first in the review prompt.",
              "Reject it: use per-file passes for local issues plus a separate integration pass for data flow.",
              "Reject it, and instead ask the single pass to give equal attention to every one of the files."),
        ans=2,
        explain=("The cause is attention dilution across many files, not space. Per-file passes give each file consistent depth, "
                 "and an integration pass covers what crosses files. A and B misread the cause as a lack of space. D "
                 "instructs the model to do something one pass can't reliably do."),
        scenarios=(5,), points=("4.6:K3", "4.6:S2"),
    ),
    Question(
        q=("Per-file review passes now find every local bug in a PR. But file_04 renames total to amount while file_12 still "
           "reads total, and nothing flags it. This kind of break reached production twice last quarter. What is missing?"),
        opts=("A rule telling each per-file pass to look up every renamed field across the rest of the repository.",
              "A larger per-file context that also includes the files each file imports and is imported by.",
              "A linter step that bans renaming fields in any PR that touches more than one file at a time.",
              "A separate integration pass that checks data flow across files, given the per-file results."),
        ans=3,
        explain=("Per-file passes see one file at a time, so cross-file breaks need a dedicated integration pass. A asks each "
                 "per-file pass to do the integration pass's job. B blurs the focus that makes per-file passes work. D bans "
                 "a legitimate change."),
        scenarios=(5,), points=("4.6:S2",),
    ),
    Question(
        q=("A CI reviewer posts every finding as a PR comment, about 25 per PR, and developers now ignore most of them. The "
           "team wants confident findings posted automatically and uncertain ones sent to a person. It already has 500 "
           "findings labelled valid or invalid. What enables this?"),
        opts=("A verification pass giving a confidence per finding, with a threshold calibrated on the labelled set.",
              "Posting only the first ten findings on each PR, since those tend to be the most important ones overall.",
              "Adding “only report findings you are confident about” to the reviewer's main review prompt.",
              "Sending every finding to a person first, so that nothing uncertain is ever posted automatically."),
        ans=0,
        explain=("A verification pass that attaches a confidence to each finding enables routing. Calibrating the threshold on "
                 "labelled data is what makes the score trustworthy, because raw self-reported confidence is poorly "
                 "calibrated. B cuts findings by position. C is a vague instruction. D gives up the automation."),
        scenarios=(5,), points=("4.6:S3",),
    ),
    Question(
        q=("A team builds a documentation pipeline as three API calls: draft, then review against a checklist, then refine. "
           "A colleague says one call with “write it and then fix it” would be simpler and save about 4 seconds per document. "
           "Auditors must be shown how each document was checked. What does the prompting guidance say about the chained "
           "version?"),
        opts=("It is obsolete on current models, since a single call now corrects all of its own work just as well.",
              "It is only worth keeping when each of the three calls uses a different model.",
              "It is the self-correction pattern; separate calls let you log, inspect and evaluate each step.",
              "It should be replaced by extended thinking, which records every check the model makes."),
        ans=2,
        explain=("The docs describe draft, review and refine as separate calls, a self-correction chain, because each step can "
                 "be logged, inspected and evaluated. That is exactly what the auditors need. A and D lose the inspectable "
                 "steps. B invents a condition."),
        scenarios=(5,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Isn't a separate API call the same as an independent instance?",
     "What matters is the context. A new call that doesn't include the generator's reasoning is independent. A call that "
     "replays the whole generation conversation isn't. The docs' self-correction chain is separate calls you can log and "
     "evaluate."),
    ("D1.5 says self-reported confidence is unreliable — why use it here?",
     "Different decisions. TS 5.2 rejects confidence as the trigger for escalating a customer case. TS 4.6 uses per-finding "
     "confidence from a verification pass to route review findings, and TS 5.5 says to calibrate it against labelled data "
     "first."),
    ("How is this different from D1.8?",
     "D1.8 is about planning: choosing prompt chaining for predictable reviews. This page is about running the review: "
     "independent instances, per-file and integration passes, and routing by confidence."),
)

PLAYGROUND_INTRO = """
Choose who reviews, how a big PR is split, and how findings are routed, all on the **simulated** generator and reviewers. In
the reviewer tab, type the instruction you'd give the reviewer. Try “be very critical” in the same session.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="mpreview")


PLAYGROUND = (
    _tab("reviewer", "⭐ Who reviews?", "reviewer", "A friend who never saw your notes.", "guide:4.6:K2",
         "Review generated pagination code with a page=0 bug.", "guide TS 4.6 K1–K2, S1; docs § Chain complex prompts",
         ("reviewer_kind",), {"reviewer_kind": "new_instance"}, ("Review this pagination code for bugs.", "Be very critical."),
         ("same session: 0 findings.", "same session + extended thinking: still 0.")),
    _tab("passes", "⭐ Passes", "passes", "Each chapter alone, then the whole plot.", "guide:4.6:S2",
         "A 14-file PR: 4 local issues and 1 cross-file rename.", "guide TS 4.6 K3, S2", ("pass_plan",), {"pass_plan": "per_file_integration"},
         ("Review PR #812",), ("one pass: 2/4 + contradictions.", "per-file only: rename missed.")),
    _tab("routing", "⭐ Routing by confidence", "routing", "Sort the notes by how sure they are.", "guide:4.6:S3",
         "Six verified findings, two of them false positives.", "guide TS 4.6 S3; TS 5.5", ("auto_threshold",), {"auto_threshold": "0.8"},
         ("Route the findings",), ("no confidence: false positives posted.", "0.5: fewer to a human, still no false positive posted.")),
)

CONTENT = ConceptContent(
    slug="multi-pass-review-architectures", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("task-decomposition", "system-prompts", "attention-engineering"), exam_points=EXAM_POINTS, playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO,
    scenarios=("self_review", "extended_thinking", "large_pr", "cross_file", "calibrated_routing"), show_ledger=False,
)
