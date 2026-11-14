"""
D4.1 System Prompts & Instructions — explicit, categorical criteria instead of vague instructions, severity levels defined by
concrete examples, and switching off a noisy category to keep developers' trust. Guide TS 4.1 (p.16).

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); platform prompting best practices fetched 2026-09-28
(DOC_REFS). Every claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (
    DocRef("Prompting best practices — Be clear and direct; Add context; Give Claude a role; Use examples",
           f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices"),
)

GROUNDING = (
    Claim("Claude responds well to clear, explicit instructions; be specific about the desired output and constraints; think of "
          "Claude as a brilliant new employee who lacks context on your norms.", "docs", "prompting best practices § Be clear and direct"),
    Claim("Golden rule: show the prompt to a colleague with minimal context — if they'd be confused, Claude will be too.", "docs",
          "prompting best practices § Be clear and direct"),
    Claim("Explaining why an instruction matters helps Claude generalise from it.", "docs", "prompting best practices § Add context"),
    Claim("A role in the system prompt focuses Claude's behaviour and tone; even one sentence helps.", "docs",
          "prompting best practices § Give Claude a role"),
    Claim("Examples are one of the most reliable ways to steer format, tone and structure.", "docs", "prompting best practices § Use examples"),
    Claim("Explicit criteria beat vague instructions (flag comments only when claimed behaviour contradicts the code, vs check "
          "that comments are accurate); 'be conservative' or 'only high-confidence findings' don't improve precision the way "
          "specific categorical criteria do; high false-positive categories undermine trust in accurate ones.", "guide",
          "TS 4.1 · Knowledge 1–3 · p.16"),
    Claim("Skills: write criteria for what to report (bugs, security) vs skip (minor style, local patterns) instead of "
          "confidence-based filtering; temporarily disable high false-positive categories while improving their prompts; define "
          "severity levels with concrete code examples for consistent classification.", "guide", "TS 4.1 · Skills 1–3 · p.16"),
    Claim("The pull request, its known true issues, and how the simulated reviewer reads a prompt (Report/Skip lines, 'contradict', "
          "severity examples) are invented.", "simulated", "utils/review_lab.py"),
)

CORRECT = r'''from utils.review_lab import review   # SIMULATED code reviewer on a pull request with known true issues

SYSTEM_PROMPT = """You review pull requests for a payments team.
Report only: bugs (wrong results, crashes), security issues, performance problems with measurable impact, and comments
whose claimed behaviour contradicts what the code actually does.
Skip: style and formatting, naming preferences, and local patterns this codebase already uses consistently.
Severity:
- critical: exploitable or loses data, e.g. SQL built from user input.
- major: a wrong result in normal use, e.g. an off-by-one that drops the last item.
- minor: wrong only in rare edge cases, e.g. a date bug at midnight on a DST change."""

# developers dismissed 4 of 5 performance findings last sprint -> off while its criteria are rewritten
DISABLED = ["performance"]

review(SYSTEM_PROMPT, DISABLED)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ TS 4.1 · Knowledge 1 — "check that comments are accurate"
VARIANT_A = _swap(CORRECT, "and comments\nwhose claimed behaviour contradicts what the code actually does.",
                  "and comments -\ncheck that comments are accurate.")
# ⭐ TS 4.1 · Knowledge 2 / Skill 1 — "be conservative" instead of report/skip criteria
VARIANT_B = _swap(CORRECT, '''Report only: bugs (wrong results, crashes), security issues, performance problems with measurable impact, and comments
whose claimed behaviour contradicts what the code actually does.
Skip: style and formatting, naming preferences, and local patterns this codebase already uses consistently.''',
                  '''Be conservative: only report high-confidence findings.''')
# ⭐ TS 4.1 · Skill 3 — severity levels without examples
VARIANT_C = _swap(CORRECT, '''- critical: exploitable or loses data, e.g. SQL built from user input.
- major: a wrong result in normal use, e.g. an off-by-one that drops the last item.
- minor: wrong only in rare edge cases, e.g. a date bug at midnight on a DST change.''',
                  '''- critical: very serious.
- major: serious.
- minor: not very serious.''')
# ⭐ TS 4.1 · Skill 2 / Knowledge 3 — leaving the noisy category on
VARIANT_D = _swap(CORRECT, '''DISABLED = ["performance"]''', '''DISABLED = []   # WRONG: the category developers keep dismissing stays on''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "review_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "review() was never called"
    ids = [x["id"] for x in r["found"]]
    txt = (f"reported {ids} · false positives {r['fp'] or 'none'} · missed {r['missed'] or 'none'} · precision {r['precision']:.0%} "
           f"· recall {r['recall']:.0%} · off-by-one severities {r['severity_b']} · disabled {r['disabled'] or 'none'}")
    if sc == "comment_accuracy":
        ok = "c1" not in ids and "c2" in ids
        return ok, (None if ok else "VAGUECOMMENT"), txt
    if sc == "style_noise":
        ok = not any(x in r["fp"] for x in ("y1", "y2", "y3", "l1")) and {"b1", "b2", "s1"} <= set(ids)
        return ok, (None if ok else "CONFIDENCE"), txt
    if sc == "severity_consistency":
        sev = r["severity_b"]
        ok = len(sev) == 2 and len(set(sev.values())) == 1
        return ok, (None if ok else "NOEXAMPLES"), txt
    ok = r["precision"] >= 0.9
    return ok, (None if ok else "NOISY"), txt


EXPECTED = {
    "comment_accuracy": "the comment that contradicts the code is flagged; the old-looking but correct comment isn't",
    "style_noise": "no style or local-pattern findings; the bugs and the SQL injection are all reported",
    "severity_consistency": "the two identical off-by-one bugs get the same severity",
    "noisy_category": "precision ≥ 90% — the category developers keep dismissing is switched off for now",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "q":    ("#EDE9FE", "#7C3AED", "the prompt"),
    "crit": ("#DBEAFE", "#0066CC", "explicit criteria"),
    "sev":  ("#FEF3C7", "#D97706", "severity & trust"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "ROLE":   ("Role + context (who reads\\nthe findings, why)", "box", "q"),
    "REPORT": ("⭐ Report: bugs, security,\\ncomments that CONTRADICT code", "box", "crit"),
    "SKIP":   ("⭐ Skip: style, naming,\\nlocal patterns", "box", "crit"),
    "SEV":    ("⭐ Severity levels, each with\\na concrete code example", "box", "sev"),
    "OFF":    ("⭐ Noisy category? Switch it off\\nwhile its criteria are fixed", "box", "sev"),
    "OUT":    ("Precise, consistent findings\\ndevelopers trust", "box", "q"),
    "VAGUECOMMENT": ("✗ “check comments\\nare accurate”", "box", "bug"),
    "CONFIDENCE":   ("✗ “be conservative /\\nhigh-confidence only”", "box", "bug"),
    "NOEXAMPLES":   ("✗ severity levels\\nwithout examples", "box", "bug"),
    "NOISY":        ("✗ noisy category\\nleft on", "box", "bug"),
}
_BUGS = ["VAGUECOMMENT", "CONFIDENCE", "NOEXAMPLES", "NOISY"]
_EXP = {"comment_accuracy": ["REPORT"], "style_noise": ["REPORT", "SKIP"], "severity_consistency": ["SEV"], "noisy_category": ["OFF"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 4.1 p.16)</FONT></TD></TR>')
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
    lines += ["  ROLE -> REPORT; ROLE -> SKIP; { rank=same; REPORT; SKIP; }", "  REPORT -> SEV; SKIP -> SEV; SEV -> OFF; OFF -> OUT;",
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  OUT -> VAGUECOMMENT [style=invis];", _key(hl),
              f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"ROLE": ("ok", ""), "OUT": ("ok", "") if ok else ("bad", "not achieved")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this scenario needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("4.1", "K", 1, "Explicit criteria beat vague instructions (“flag comments only when the claim contradicts the code” vs “check comments are accurate”).",
              "✅ comment_accuracy · ❌ A"),
    ExamPoint("4.1", "K", 2, "General instructions like “be conservative” or “only high-confidence findings” don't improve precision the way specific categorical criteria do.",
              "✅ style_noise · ❌ B"),
    ExamPoint("4.1", "K", 3, "High false-positive categories undermine developers' trust in the accurate ones.", "✅ noisy_category · ❌ D"),
    ExamPoint("4.1", "S", 1, "Write criteria for what to report (bugs, security) and what to skip (minor style, local patterns) instead of confidence filtering.",
              "✅ Report/Skip lines · ❌ B"),
    ExamPoint("4.1", "S", 2, "Temporarily disable high false-positive categories to restore trust while their prompts are improved.", "✅ DISABLED · ❌ D"),
    ExamPoint("4.1", "S", 3, "Define severity levels with concrete code examples for consistent classification.", "✅ severity_consistency · ❌ C"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ explicit Report/Skip criteria · severity with examples · noisy category off", "correct", CORRECT, "comment_accuracy",
            observe=("Every scenario: reported c2 (comment contradicts the code), b1 and b2 (off-by-ones) and s1 (SQL injection) — "
                     "precision 100%, recall 100%, both off-by-ones “major”. The one real performance issue (p1) is “not checked” "
                     "while that category is switched off."),
            why="The reviewer is told exactly what counts, what doesn't, and what each severity looks like — like a new colleague given a clear brief."),
    Variant("A", "⭐❌ A — “check that comments are accurate”", "distractor", VARIANT_A, "comment_accuracy",
            observe="The old-looking comment at cart.py:12 is flagged (c1) although the code does what it says — precision 80%.",
            why="“Accurate” is vague; “flag only when the claimed behaviour contradicts the code” is a criterion the reviewer can apply.",
            fix="Say what counts: a contradiction between comment and code.", source="guide:4.1:K1"),
    Variant("B", "⭐❌ B — “be conservative: only report high-confidence findings”", "distractor", VARIANT_B, "style_noise",
            observe="Style (y1–y3), a local pattern (l1) and the correct comment (c1) are all reported — 5 false positives, precision 44%.",
            why="The reviewer is confident about style nits; confidence isn't the filter — categories are.",
            fix="Report / Skip lists by category.", source="guide:4.1:K2"),
    Variant("C", "⭐❌ C — severity levels without examples", "distractor", VARIANT_C, "severity_consistency",
            observe="Two identical off-by-one bugs come back as “major” and “minor”.",
            why="“Serious / very serious” can't be applied consistently; a concrete code example per level can.",
            fix="One concrete example for each severity level.", source="guide:4.1:S3"),
    Variant("D", "⭐❌ D — leaving the noisy category on", "distractor", VARIANT_D, "noisy_category",
            observe="Performance adds p1 (real) and p2–p5 (dismissed) — precision falls to 56%.",
            why="A category developers keep dismissing teaches them to ignore every finding, including the accurate ones.",
            fix="Switch it off while its criteria are rewritten; switch it back on when they're precise.", source="guide:4.1:S2"),
)

TLDR = (
    "Precision comes from **explicit criteria**, not from vague adjectives:\n\n"
    "- **What to report:** bugs, security issues, comments whose claim **contradicts** the code.\n"
    "- **What to skip:** style, naming, patterns the codebase already uses.\n"
    "- **Severity levels:** each with a **concrete code example**.\n\n"
    "“Be conservative” or “only high-confidence findings” don't cut false positives. When one category keeps producing false "
    "positives, **switch it off while you fix its criteria**, or developers stop trusting every finding. The docs' framing: "
    "write for a brilliant new colleague who doesn't know your norms."
)
MENTAL_MODEL = ("Your reviewer is a brilliant new hire on day one. “Be careful” tells them nothing; a checklist of what to flag, "
                "what to ignore and what “critical” looks like tells them everything. And a smoke alarm that goes off every time "
                "you make toast gets its battery pulled — noisy categories cost trust in the accurate ones.")

WHAT_IT_IS = """
The exam guide covers designing prompts with explicit criteria to improve precision and reduce false positives (Guide §6 ·
TS 4.1, p.16). The platform's prompting best practices give the general principle: be clear, direct and specific.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Explicit criteria vs vague instructions | A checklist for a new hire, not “be careful”. | ⭐ TS 4.1 · Knowledge 1 |
| 2 | Confidence filters don't fix precision | A confident reviewer is confidently wrong about style. | ⭐ TS 4.1 · Knowledge 2 |
| 3 | Report / Skip categories | Two lists on the wall: flag these, ignore those. | ⭐ TS 4.1 · Skill 1 |
| 4 | Severity with examples | “Critical looks like this” beats “critical means very serious”. | ⭐ TS 4.1 · Skill 3 |
| 5 | False positives erode trust | A smoke alarm that fires at toast gets unplugged. | ⭐ TS 4.1 · Knowledge 3 |
| 6 | Switch off a noisy category (for now) | Take one alarm offline while you fix its sensor. | ⭐ TS 4.1 · Skill 2 |
| 7 | Role + reason in the system prompt | Tell the new hire who they are and why the rule exists. | 📘 docs |

**Vague vs explicit** (this lab's pull request)

| # | Instruction | False positives | What happened |
|---|---|---|---|
| 1 | “Check that comments are accurate” | 1 | A correct but old-looking comment flagged |
| 2 | “Be conservative, high-confidence only” | 5 | Style, naming and a house pattern all reported |
| 3 | ⭐ Report: bugs, security, comments that contradict code · Skip: style, naming, local patterns | 0 | Only the 4 real issues |
| 4 | Severity “very serious / serious” | — | Identical bugs rated differently |
| 5 | ⭐ Severity with a code example per level | — | Identical bugs rated the same |
"""

HOW_IT_WORKS = """
1. **Give a role and a reason:** who reviews, and who reads the findings (docs: context helps Claude generalise).
2. **List what to report** as categories: bugs, security, comments that contradict the code.
3. **List what to skip:** style, naming, patterns the codebase already uses.
4. **Define severity** with one concrete code example per level.
5. **Watch dismissal rates.** A category developers keep dismissing gets switched off until its criteria are rewritten.
"""

WHERE_SEEN = """
- **Scenario 5 — Claude Code for Continuous Integration** (Guide §5, p.4): automated PR review, false positives, developer trust.
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): review criteria and severities.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 4.1 (p.16) and the platform prompting best practices (verified 2026-09-28). "
              "Section layout inspired by a community concept list (claudearchitectcertification.com — community source, "
              "unverified; no text copied).")

LAB_INTRO = """
You write a code reviewer's **system prompt** and choose which categories are switched off. The **simulated** reviewer reads
the prompt and reviews one pull request whose true issues are known: 4 real issues in the report categories, 1 real
performance issue, and 9 look-alikes. The lab measures **precision** (how many findings are real), **recall** (how many real
issues were found) and **severity consistency**.
"""

DISTRACTORS = (
    ("A · “Check comments are accurate”", "Sounds thorough.", "Flags correct but old-looking comments.", "“…contradicts the code”.", "guide:4.1:K1"),
    ("B · “Be conservative / high-confidence”", "Should cut noise.", "Style nits are reported confidently.", "Report / Skip categories.", "guide:4.1:K2"),
    ("C · Severity without examples", "Everyone knows “serious”.", "Identical bugs rated differently.", "An example per level.", "guide:4.1:S3"),
    ("D · Keep the noisy category on", "It found one real issue.", "Four dismissals per real one erode trust.", "Switch it off for now.", "guide:4.1:S2"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Vague instruction", "Explicit criterion")
SIDE_BY_SIDE_ROWS = (
    ("1", "Comments", "“Check comments are accurate”", "“Flag a comment only when its claim contradicts the code”"),
    ("2", "Noise", "“Be conservative”", "“Skip: style, naming, local patterns”"),
    ("3", "Severity", "“Critical = very serious”", "“Critical, e.g. SQL built from user input”"),
    ("4", "Result here", "44–80% precision", "100% precision"),
    ("5", "Docs principle", "—", "Be clear, direct and specific; explain why"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Too many false\\npositives?"];
  Q2 [shape=diamond, label="Concentrated in\\none category?"];
  OFF [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Switch that category off;\\nrewrite its criteria"];
  CRIT [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Replace vague words with\\nReport / Skip categories"];
  Q3 [shape=diamond, label="Severities\\ninconsistent?"];
  SEV [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Add a code example\\nper severity level"];
  OK [shape=box, fillcolor="#D1FAE5", color="#059669", label="Keep measuring\\ndismissal rates"];
  Q1 -> Q2 [label="yes"]; Q2 -> OFF [label="yes"]; Q2 -> CRIT [label="no"]; Q1 -> Q3 [label="no"];
  OFF -> Q3; CRIT -> Q3; Q3 -> SEV [label="yes"]; Q3 -> OK [label="no"]; SEV -> OK;
}''')

EXPERIMENTS = (
    "Run ✅ on all four scenarios and note the 100% precision.",
    "In ✅, delete the Skip line and run style_noise: what comes back?",
    "In ✅, remove “e.g. …” from the minor level only and run severity_consistency.",
    "In the playground's “Your prompt” tab, write your own one-line review prompt and try to reach 100% precision and recall.",
)

QUESTIONS = (
    Question(
        q=("Your CI reviewer flags about 40 code comments a week as “inaccurate” when they are merely old-fashioned but still "
           "true, and developers now dismiss most of its comment findings. The prompt says “check that comments are "
           "accurate”. What is the best change?"),
        opts=("Add “be careful and only flag comments you are sure about” to the existing comment instruction.",
              "Replace it with an explicit criterion: flag a comment only when its claim contradicts what the code does.",
              "Remove comment checking from the reviewer entirely, since comments are too subjective for an automated review.",
              "Cap the reviewer at five comment findings per pull request, so that the false positives are fewer."),
        ans=1,
        explain=("An explicit criterion says exactly what counts as a problem, which removes the ambiguity behind the false "
                 "positives. A is a vague confidence instruction, which doesn't improve precision. C throws away a useful "
                 "check. D cuts real and false findings alike."),
        scenarios=(5,), points=("4.1:K1", "4.1:S1"),
    ),
    Question(
        q=("A reviewer's prompt says “be conservative and only report issues you're highly confident about”, yet 55% of its "
           "findings are style nits or speculative concerns that developers dismiss. Adding “be even more conservative” last "
           "month changed nothing measurable. What will improve precision most?"),
        opts=("Ask the reviewer to attach a confidence score to each finding, and report only those scored 9 or 10.",
              "Run the reviewer twice on each PR, and keep only the findings that appear in both independent runs.",
              "Name the categories to report (bugs, security) and those to skip (minor style, accepted local patterns).",
              "Switch to a larger model, which will interpret “conservative” more consistently across all of its reviews."),
        ans=2,
        explain=("General instructions such as “be conservative” don't improve precision; specific report and skip categories "
                 "do. A relies on self-reported confidence, which is poorly calibrated. B suppresses real findings that only "
                 "show up intermittently. D hopes a bigger model will resolve an ambiguity the prompt created."),
        scenarios=(5,), points=("4.1:K2", "4.1:S1"),
    ),
    Question(
        q=("Developers dismiss about 80% of the reviewer's “performance” findings. A survey shows they now also skim past its "
           "security findings, although those are right 90% of the time. Rewriting the performance criteria properly will "
           "take about three weeks. What is the best immediate step?"),
        opts=("Temporarily disable the performance category while its criteria are rewritten, so trust recovers.",
              "Keep every category, but add a note to each performance finding saying these are often false positives.",
              "Mark security findings in bold red, so developers notice them among the noisy performance findings.",
              "Keep performance findings, but move them to the end of each review, after all the security findings."),
        ans=0,
        explain=("A high false-positive category erodes trust in the accurate ones. Disabling it while its criteria are fixed "
                 "restores trust straight away. B and D keep the noise in front of developers. C treats the symptom, and "
                 "developers who distrust the tool will skim past red text as well."),
        scenarios=(5,), points=("4.1:K3", "4.1:S2"),
    ),
    Question(
        q=("Two identical unchecked-null bugs in different files come back as “critical” in one review and “minor” in "
           "another. Over a month, 30% of findings changed severity when the same PR was re-reviewed. The prompt lists the "
           "four severity names with no further detail. Which change gives consistent classification?"),
        opts=("Lower the temperature to zero, so the reviewer gives the same severity each time it sees similar code.",
              "Remove the severity field and report every finding at one level, so there is nothing to disagree about.",
              "Run a second reviewer that re-grades each finding's severity, and keep the higher of the two grades.",
              "Define each severity level in the prompt, with concrete code examples of what belongs at that level."),
        ans=3,
        explain=("Severity names without definitions leave the boundary to chance. Explicit criteria with code examples for each "
                 "level make classification consistent. A may make repeat runs more alike, but it doesn't fix an undefined "
                 "boundary between different code. B removes useful information. C adds a second undefined judgement."),
        scenarios=(5,), points=("4.1:S3",),
    ),
    Question(
        q=("The team deliberately catches broad exceptions in its plugin loader, a documented local pattern. The CI reviewer "
           "flags it on every pull request that touches the loader, about 12 a week, and developers now reflexively dismiss "
           "all exception-handling findings, including real ones. What is the best prompt change?"),
        opts=("Tell the reviewer to skip every exception-handling finding, since developers dismiss them all anyway.",
              "State that this local pattern is accepted and should be skipped, while real exception bugs are reported.",
              "Add “use good judgement about exception handling” to the reviewer's instructions for the plugin loader.",
              "Exclude the plugin loader's directory from review entirely, so that none of its code is checked any more."),
        ans=1,
        explain=("Explicit criteria include what not to report: here, an accepted local pattern. Real issues stay in scope. A "
                 "throws away real findings. C is a vague instruction. D stops reviewing the loader altogether."),
        scenarios=(5,), points=("4.1:S1",),
    ),
)


FAQ = (
    ("Isn't “only report high-confidence findings” a reasonable safety net?",
     "It feels like one, but the guide's point is that it doesn't improve precision. The model can be confident about a style "
     "nit. Categories say what's in and out."),
    ("Does switching a category off mean losing real issues?",
     "For a while, yes. In the lab, one real performance issue goes unchecked. The guide treats it as temporary: restore trust, "
     "fix that category's criteria, then switch it back on."),
    ("Where does the role go?",
     "In the system prompt. The docs say even one sentence of role focuses Claude's behaviour, and explaining why a rule exists "
     "helps it generalise."),
)

PLAYGROUND_INTRO = """
Write your own review prompt in the first tab — one line is fine, because sentences starting “Report”, “Skip” or a severity
level become separate lines. The other tabs switch between vague and explicit versions. Every run shows the findings,
precision and recall on the **simulated** reviewer.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="review")


PLAYGROUND = (
    _tab("yours", "⭐ Your prompt", "yours", "A checklist for the new hire.", "guide:4.1:S1",
         "Your message IS the system prompt.", "prompting best practices § Be clear and direct; guide TS 4.1",
         ("perf_off",), {"perf_off": "yes"},
         ("Report only: bugs, security issues, and comments whose claimed behaviour contradicts the code. Skip: style, naming, "
          "and local patterns. - critical: e.g. SQL built from user input. - major: e.g. an off-by-one that drops the last item. "
          "- minor: e.g. a date bug at midnight on a DST change.",
          "Review this PR carefully and be conservative."),
         ("“be conservative” → 5 false positives.", "Add severity levels with “e.g.” examples to fix inconsistent severities.")),
    _tab("vague", "⭐ Vague vs explicit", "vague", "“Be careful” tells the new hire nothing.", "guide:4.1:K2",
         "The same reviewer with three instructions.", "guide TS 4.1 K1–K2", ("instruction_style",), {"instruction_style": "explicit"},
         ("Review the pull request",), ("accurate: 1 false positive.", "conservative: 5 false positives.")),
    _tab("severity", "⭐ Severity", "severity", "Show what “critical” looks like.", "guide:4.1:S3",
         "Severity levels with and without examples.", "guide TS 4.1 S3", ("sev_examples",), {"sev_examples": "yes"},
         ("Review the pull request",), ("no examples: major vs minor for identical bugs.",)),
    _tab("noisy", "⭐ Noisy category", "noisy", "Unplug the alarm that fires at toast — for now.", "guide:4.1:S2",
         "Performance: 1 real finding, 4 dismissed.", "guide TS 4.1 K3, S2", ("perf_off",), {"perf_off": "yes"},
         ("Review the pull request",), ("on: precision 56%.", "off: 100%, with p1 not checked.")),
)

CONTENT = ConceptContent(
    slug="system-prompts", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("prompt-engineering-techniques", "multi-pass-review-architectures", "structured-outputs"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("comment_accuracy", "style_noise", "severity_consistency", "noisy_category"), show_ledger=False,
)
