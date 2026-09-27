"""
D4.9 Prompt Engineering Techniques — few-shot examples (format, ambiguous-case reasoning, generalisation, varied formats) and
iterative refinement (concrete input/output examples, test-driven iteration with specific failures, the interview pattern,
fixing interacting issues together). Guide TS 4.2 (pp.16–17) and TS 3.5 (pp.14–15); explicit criteria (TS 4.1) are on D4.1.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); platform prompting best practices fetched 2026-09-28
(DOC_REFS). Every claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (DocRef("Prompting best practices — Use examples effectively; Be clear and direct",
                   f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices"),)

GROUNDING = (
    Claim("Examples are one of the most reliable ways to steer output format, tone and structure; few-shot (multishot) prompting "
          "improves accuracy and consistency.", "docs", "prompting best practices § Use examples effectively"),
    Claim("Make examples relevant (mirror the real use case), diverse (cover edge cases; vary enough that Claude doesn't pick up "
          "unintended patterns) and structured (wrap them in <example> / <examples> tags); 3–5 examples are suggested.", "docs",
          "prompting best practices § Use examples effectively"),
    Claim("Few-shot examples are the most effective technique for consistently formatted, actionable output when instructions "
          "alone are inconsistent; they demonstrate ambiguous-case handling; they let the model generalise judgment to new "
          "patterns; they reduce hallucination in extraction (informal measurements, varied structures).", "guide", "TS 4.2 · Knowledge 1–4 · pp.16–17"),
    Claim("Skills: 2–4 targeted examples for ambiguous cases that show why one action beat plausible alternatives; examples of the "
          "exact output format (location, issue, severity, fix); examples distinguishing acceptable patterns from real issues; "
          "examples of varied document structures; examples with varied formats to fix empty/null required fields.", "guide",
          "TS 4.2 · Skills 1–5 · p.17"),
    Claim("Iterative refinement: concrete input/output examples beat prose when descriptions are interpreted inconsistently; "
          "write tests first and iterate by sharing failures; the interview pattern (Claude asks questions first); describe "
          "interacting problems together, independent ones one at a time.", "guide", "TS 3.5 · Knowledge 1–4 · p.14"),
    Claim("Skills: 2–3 concrete input/output examples; tests covering behaviour, edge cases and performance, then share failures; "
          "the interview pattern for unfamiliar domains; specific test cases with example input and expected output for edge "
          "cases; one detailed message for interacting issues.", "guide", "TS 3.5 · Skills 1–5 · pp.14–15"),
    Claim("The guide suggests 2–4 targeted examples (TS 4.2 S1); the docs suggest 3–5. Both agree on a handful of relevant, varied examples.",
          "guide", "TS 4.2 S1 vs prompting best practices"),
    Claim("How the simulated model reacts to examples, feedback and fix order is invented (rules listed in utils/fewshot_lab.py).",
          "simulated", "utils/fewshot_lab.py"),
)

CORRECT = r'''from utils.fewshot_lab import SCENARIO, extract, fix, iterate, review, route   # SIMULATED model

# 1. Show the exact output format - every field, in every example
REVIEW_EXAMPLES = [
    {"input": "def total(items): return sum(i.price for i in items[:-1])",
     "output": {"location": "cart.py:57", "issue": "slice drops the last item", "severity": "major", "fix": "use items, not items[:-1]"}},
    {"input": "query = f\"SELECT * FROM users WHERE name = '{name}'\"",
     "output": {"location": "search.py:21", "issue": "SQL built from user input", "severity": "critical", "fix": "use a parameterised query"}},
]

# 2. Ambiguous cases: show the REASONING - why this tool over the plausible alternative - with more than one outcome
ROUTING_EXAMPLES = [
    {"request": "Summarise these web search results about heat pumps", "tool": "web",
     "why": "the input is search results, so the web tool over the document tool, even though it says summarise"},
    {"request": "Pull the totals out of the attached PDF invoice", "tool": "doc",
     "why": "an attached file, so the document tool rather than the web tool"},
    {"request": "Turn these search results into a one-page brief", "tool": "web",
     "why": "search results again - the web tool, not the document tool, whatever the output format"},
]

# 3. Varied input formats, so informal values aren't left null
EXTRACT_EXAMPLES = [{"text": "about 1.8 metres", "height_m": 1.8}, {"text": "5 ft 11 in", "height_m": 1.80},
                    {"text": "172 cm", "height_m": 1.72}]


def feedback(failures):
    """Iterate by sharing the failing tests: name, expected, actual."""
    return "\n".join(f"{t['name']}: expected {t['expected']}, got {t['got']}" for t in failures)


FIX_TOGETHER = True   # the two bugs interact (tax relies on total()'s rounding) -> one detailed message

if SCENARIO == "format_consistency":
    review(REVIEW_EXAMPLES)
elif SCENARIO == "ambiguous_case":
    route(ROUTING_EXAMPLES)
elif SCENARIO == "informal_extraction":
    extract(EXTRACT_EXAMPLES)
elif SCENARIO == "test_driven":
    iterate(feedback)
else:
    fix(together=FIX_TOGETHER)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ TS 4.2 · Knowledge 1 / Skill 2 — instructions only, no examples
VARIANT_A = _swap(CORRECT, '''    review(REVIEW_EXAMPLES)''', '''    review([])   # WRONG: "report location, issue, severity and fix" in prose only''')
# ⭐ TS 4.2 · Skill 1 / Knowledge 3 — answers without reasoning
VARIANT_B = _swap(CORRECT, '''    route(ROUTING_EXAMPLES)''', '''    route([{k: v for k, v in e.items() if k != "why"} for e in ROUTING_EXAMPLES])   # WRONG: answers only, no reasoning''')
# 📘 docs — examples that all look alike
VARIANT_C = _swap(CORRECT, '''    route(ROUTING_EXAMPLES)''', '''    route([e for e in ROUTING_EXAMPLES if e["tool"] == "doc"] * 3)   # WRONG: every example has the same outcome''')
# ⭐ TS 4.2 · Skill 5 / Knowledge 4 — one input format only
VARIANT_D = _swap(CORRECT, '''EXTRACT_EXAMPLES = [{"text": "about 1.8 metres", "height_m": 1.8}, {"text": "5 ft 11 in", "height_m": 1.80},
                    {"text": "172 cm", "height_m": 1.72}]''', '''EXTRACT_EXAMPLES = [{"text": "172 cm", "height_m": 1.72}, {"text": "180 cm", "height_m": 1.80}]   # WRONG: one format only''')
# ⭐ TS 3.5 · Skill 2 / Knowledge 2 — vague iteration feedback
VARIANT_E = _swap(CORRECT, '''    return "\\n".join(f"{t['name']}: expected {t['expected']}, got {t['got']}" for t in failures)''',
                  '''    return "The migration still doesn't work, please fix it."   # WRONG: no failing test, no expected vs actual''')
# ⭐ TS 3.5 · Skill 5 / Knowledge 4 — interacting issues one at a time
VARIANT_F = _swap(CORRECT, '''FIX_TOGETHER = True   # the two bugs interact (tax relies on total()'s rounding) -> one detailed message''',
                  '''FIX_TOGETHER = False  # WRONG: interacting bugs fixed one message at a time''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "fewshot_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "nothing ran"
    txt = " · ".join(f"{k}={v}" for k, v in r.items() if k not in ("kind", "scenario"))
    if r["ok"]:
        return True, None, txt
    if r["task"] == "route":
        return False, ("SAMEEX" if len(r["tools"]) == 1 else "NOREASON"), txt
    return False, {"review": "NOEXAMPLES", "extract": "ONEFORMAT", "iterate": "VAGUEFB", "fix": "SEQUENTIAL"}[r["task"]], txt


EXPECTED = {
    "format_consistency": "all three findings in the same shape: location, issue, severity, fix",
    "ambiguous_case": "the new “news search results” request goes to the web tool",
    "informal_extraction": "all four heights extracted — none left null",
    "test_driven": "the failing tests pass after 2 rounds",
    "interacting_issues": "both interacting bugs fixed in one round",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "ex":   ("#DBEAFE", "#0066CC", "few-shot examples (TS 4.2)"),
    "it":   ("#FEF3C7", "#D97706", "iterative refinement (TS 3.5)"),
    "out":  ("#EDE9FE", "#7C3AED", "result"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "FMT":    ("⭐ Examples showing the exact\\noutput format", "box", "ex"),
    "WHY":    ("⭐ Ambiguous cases: show WHY\\nthis over the alternative", "box", "ex"),
    "DIV":    ("Varied examples (docs:\\nrelevant, diverse, <example>)", "box", "ex"),
    "VAR":    ("⭐ Varied input formats →\\nno null extractions", "box", "ex"),
    "TDD":    ("⭐ Tests first; share failures\\n(expected vs actual)", "box", "it"),
    "TOG":    ("⭐ Interacting issues in one\\nmessage; independent ones\\nin turn", "box", "it"),
    "OUT":    ("Consistent output that\\ngeneralises", "box", "out"),
    "NOEXAMPLES": ("✗ instructions only,\\nno examples", "box", "bug"),
    "NOREASON":   ("✗ answers without\\nreasoning", "box", "bug"),
    "SAMEEX":     ("✗ examples all\\nalike", "box", "bug"),
    "ONEFORMAT":  ("✗ one input format\\nin the examples", "box", "bug"),
    "VAGUEFB":    ("✗ “it still doesn't\\nwork”", "box", "bug"),
    "SEQUENTIAL": ("✗ interacting bugs fixed\\none at a time", "box", "bug"),
}
_BUGS = ["NOEXAMPLES", "NOREASON", "SAMEEX", "ONEFORMAT", "VAGUEFB", "SEQUENTIAL"]
_EXP = {"format_consistency": ["FMT"], "ambiguous_case": ["WHY", "DIV"], "informal_extraction": ["VAR"], "test_driven": ["TDD"],
        "interacting_issues": ["TOG"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 4.2 pp.16–17, TS 3.5 pp.14–15)</FONT></TD></TR>')
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
    lines += ["  FMT -> WHY -> DIV -> VAR -> OUT; TDD -> TOG -> OUT; { rank=same; FMT; TDD; }",
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  OUT -> NOEXAMPLES [style=invis];", _key(hl),
              f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {"OUT": ("ok", "") if ok else ("bad", "not achieved")}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "" if ok else "what this scenario needs")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("4.2", "K", 1, "Few-shot examples are the most effective way to get consistently formatted, actionable output when instructions alone are inconsistent.",
              "✅ format_consistency · ❌ A"),
    ExamPoint("4.2", "K", 2, "Few-shot examples demonstrate how to handle ambiguous cases (e.g. tool selection).", "✅ ambiguous_case"),
    ExamPoint("4.2", "K", 3, "Examples let the model generalise judgment to new patterns, not just match the listed cases.", "✅ ambiguous_case · ❌ B"),
    ExamPoint("4.2", "K", 4, "Examples reduce hallucination in extraction (informal measurements, varied structures).", "✅ informal_extraction · ❌ D"),
    ExamPoint("4.2", "S", 1, "Write 2–4 targeted examples for ambiguous cases that show why one action beat plausible alternatives.", "✅ ROUTING_EXAMPLES · ❌ B"),
    ExamPoint("4.2", "S", 2, "Include examples of the exact output format (location, issue, severity, suggested fix).", "✅ REVIEW_EXAMPLES · ❌ A"),
    ExamPoint("4.2", "S", 3, "Include examples separating acceptable code patterns from real issues, to cut false positives while generalising.",
              "See D4.1 (explicit criteria) — same technique"),
    ExamPoint("4.2", "S", 4, "Show correct handling of varied document structures (inline citations vs bibliographies).", "Same idea as ✅ EXTRACT_EXAMPLES"),
    ExamPoint("4.2", "S", 5, "Add examples with varied formats to fix empty/null extraction of required fields.", "✅ informal_extraction · ❌ D"),
    ExamPoint("3.5", "K", 1, "Concrete input/output examples communicate transformations best when prose is read inconsistently.", "✅ every example list"),
    ExamPoint("3.5", "K", 2, "Test-driven iteration: write tests first, iterate by sharing failures.", "✅ test_driven · ❌ E"),
    ExamPoint("3.5", "K", 3, "The interview pattern: Claude asks questions to surface considerations before implementing.", "FAQ · playground “Iterate”"),
    ExamPoint("3.5", "K", 4, "Interacting problems in one message; independent problems one at a time.", "✅ interacting_issues · ❌ F"),
    ExamPoint("3.5", "S", 2, "Write tests for behaviour, edge cases and performance first, then share failures.", "✅ feedback() · ❌ E"),
    ExamPoint("3.5", "S", 5, "Address interacting issues in a single detailed message; iterate sequentially on independent ones.", "✅ FIX_TOGETHER · ❌ F"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ format examples · reasoned, varied ambiguous-case examples · varied formats · specific test failures · interacting fixes together",
            "correct", CORRECT, "format_consistency",
            observe=("format_consistency: all three findings share location / issue / severity / fix. ambiguous_case: the new “news "
                     "search results” request goes to the web tool — it generalised. informal_extraction: all four heights extracted. "
                     "test_driven: passes after 2 rounds. interacting_issues: both bugs fixed in round 1."),
            why="The examples show the format and the reasoning, the feedback names what failed, and interacting problems travel together."),
    Variant("A", "⭐❌ A — instructions only, no examples", "distractor", VARIANT_A, "format_consistency",
            observe="Three findings, three shapes: a dict with two fields, a sentence, and a dict with different keys.",
            why="When instructions alone give inconsistent output, few-shot examples are the most effective fix.",
            fix="2–4 examples showing every field.", source="guide:4.2:K1"),
    Variant("B", "⭐❌ B — examples with answers but no reasoning", "distractor", VARIANT_B, "ambiguous_case",
            observe="The new request “key points from these news search results” goes to the document tool — nothing to generalise from.",
            why="Showing why one action beat a plausible alternative lets the model apply the judgment to new wording.",
            fix="Add “why X over Y” to each ambiguous example.", source="guide:4.2:S1"),
    Variant("C", "❌ C — examples that all look alike", "distractor", VARIANT_C, "ambiguous_case",
            observe="Every example routes to the document tool; the model learned “always doc”.",
            why="The docs: make examples diverse so Claude doesn't pick up unintended patterns.",
            fix="Cover both outcomes and the edge cases.", source="docs"),
    Variant("D", "⭐❌ D — one input format in the examples", "distractor", VARIANT_D, "informal_extraction",
            observe="“about two metres”, “6 ft 2 in” and “roughly a metre and a half” come back as null.",
            why="Examples with varied formats teach the model to extract informal values instead of leaving required fields empty.",
            fix="Examples in approximate, imperial and metric forms.", source="guide:4.2:S5"),
    Variant("E", "⭐❌ E — “it still doesn't work”", "distractor", VARIANT_E, "test_driven",
            observe="Still failing after 4 rounds — the model is guessing.",
            why="Test-driven iteration shares the failing tests: name, expected, actual.",
            fix="Paste the failures.", source="guide:3.5:S2"),
    Variant("F", "⭐❌ F — interacting issues one at a time", "distractor", VARIANT_F, "interacting_issues",
            observe="Round 1 fixes rounding and breaks tax; round 2 fixes tax and reverts rounding; round 3 breaks tax again.",
            why="When fixes interact, describe the issues together in one detailed message; iterate one by one only for independent issues.",
            fix="One message describing both.", source="guide:3.5:S5"),
)

TLDR = (
    "**Few-shot examples** are the most reliable way to get **consistent format** and **judgment that generalises**:\n\n"
    "- **2–4 targeted examples** (the docs say 3–5), wrapped in `<example>` tags.\n"
    "- **Show every output field.**\n"
    "- For ambiguous cases, show **why this action over the plausible alternative**.\n"
    "- **Vary the examples**, so the model doesn't copy an unintended pattern.\n"
    "- **Cover varied input formats**, so informal values aren't left null.\n\n"
    "When **iterating**, share **specific test failures** (expected vs actual). Use the **interview pattern** in unfamiliar "
    "domains. Send **interacting** problems in **one** message, and independent ones one at a time."
)
MENTAL_MODEL = ("Examples are worked solutions on the whiteboard: students copy their format exactly, and if you show your "
                "reasoning they can solve new problems — but if every worked example has the same answer, they learn the answer, "
                "not the method. And when marking homework, “wrong” teaches nothing; “question 3: expected 12, you wrote 21” does.")

WHAT_IT_IS = """
The exam guide covers few-shot prompting (Guide §6 · TS 4.2, pp.16–17) and iterative refinement (TS 3.5, pp.14–15). The
docs' prompting best practices give the rules for examples. D4.1 covers explicit criteria (TS 4.1).

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | ⭐ Exam reference |
|---|---|---|---|
| 1 | Format examples | Students copy the worked solution's layout exactly. | ⭐ TS 4.2 · Knowledge 1, Skill 2 |
| 2 | Ambiguous-case examples with reasoning | Show the working, not just the answer. | ⭐ TS 4.2 · Knowledge 2–3, Skill 1 |
| 3 | Diverse examples | If every example has the same answer, they learn the answer. | 📘 docs |
| 4 | Varied input formats | Worked examples in cm, feet and “about two metres”. | ⭐ TS 4.2 · Knowledge 4, Skill 5 |
| 5 | Concrete input/output examples | “This goes in, that comes out” beats a paragraph. | ⭐ TS 3.5 · Knowledge 1, Skill 1 |
| 6 | Test-driven iteration | Mark the homework: “Q3 expected 12, you wrote 21”. | ⭐ TS 3.5 · Knowledge 2, Skill 2 |
| 7 | Interview pattern | Let the new hire ask questions before building. | ⭐ TS 3.5 · Knowledge 3, Skill 3 |
| 8 | Together vs one at a time | Tangled knots are untied together; separate ones one by one. | ⭐ TS 3.5 · Knowledge 4, Skill 5 |

**Good examples** (docs + guide)

| # | Property | Why |
|---|---|---|
| 1 | Relevant — mirror the real inputs | The model copies what it sees |
| 2 | Diverse — different outcomes and edge cases | Avoids unintended patterns (“always doc”) |
| 3 | Complete — every output field | Consistent format |
| 4 | Reasoned (for ambiguous cases) — why this over that | Judgment that generalises |
| 5 | Structured — in `<example>` / `<examples>` tags | Kept apart from instructions |
| 6 | A handful — guide 2–4, docs 3–5 | Enough to show the pattern |

**Iterating with Claude** (guide TS 3.5)

| # | Situation | Do | Don't |
|---|---|---|---|
| 1 | Prose is read inconsistently | Give 2–3 concrete input → output examples | Rewrite the paragraph again |
| 2 | Building something testable | Write the tests first; share failures (expected vs actual) | “It doesn't work” |
| 3 | Unfamiliar domain | Interview pattern: let Claude ask about caching, failure modes, … first | Jump straight to code |
| 4 | Issues that interact | One detailed message covering all of them | Fix one, then the other |
| 5 | Independent issues | One at a time | — |
"""

HOW_IT_WORKS = """
1. **Inconsistent output?** Add 2–4 examples that show every field of the format you want.
2. **Ambiguous cases?** Make the examples show why one action beat the plausible alternative, and vary the outcomes.
3. **Extraction nulls?** Add examples covering the informal and varied formats you actually receive.
4. **Iterating on code?** Write tests first, then share the failures with expected vs actual. In unfamiliar territory, let
   Claude interview you first.
5. **Several problems?** If they interact, send them in one detailed message. If they're independent, fix them one at a time.
"""

WHERE_SEEN = """
- **Scenario 5 — Claude Code for Continuous Integration** (Guide §5, p.4): consistent review output via examples.
- **Scenario 6 — Structured Data Extraction** (Guide §5, p.4): examples for varied document formats.
- **Scenario 2 — Code Generation with Claude Code** (Guide §5, p.3): test-driven iteration, the interview pattern.
"""

GUIDE_NOTE = ("Grounded in the exam guide §6 TS 4.2 (pp.16–17) and TS 3.5 (pp.14–15), and the platform prompting best practices "
              "(verified 2026-09-28). Section layout inspired by a community concept list (claudearchitectcertification.com — "
              "community source, unverified; no text copied).")

LAB_INTRO = """
You write the examples and the iteration choices. A **simulated** model follows deterministic stand-in rules, listed in
`utils/fewshot_lab.py`: it copies the format it's shown, generalises only from reasoned and varied examples, extracts informal
values only if it has seen varied formats, converges only on specific test feedback, and ping-pongs on interacting bugs fixed
separately.
"""

DISTRACTORS = (
    ("A · Instructions only", "The prompt lists the fields.", "Three shapes for three findings.", "Format examples.", "guide:4.2:K1"),
    ("B · Answers without reasoning", "The examples are right.", "No judgment to generalise.", "Show why X over Y.", "guide:4.2:S1"),
    ("C · All-alike examples", "Consistent examples.", "Learns “always doc”.", "Diverse outcomes.", "docs"),
    ("D · One input format", "Examples are clean.", "Informal values → null.", "Varied formats.", "guide:4.2:S5"),
    ("E · “Still doesn't work”", "Claude can see the code.", "It guesses for 4 rounds.", "Share the failing tests.", "guide:3.5:S2"),
    ("F · Interacting fixes one by one", "Smaller steps are safer.", "The fixes undo each other.", "One message.", "guide:3.5:S5"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Instructions only", "Instructions + few-shot examples")
SIDE_BY_SIDE_ROWS = (
    ("1", "Output format", "Varies", "Matches the examples"),
    ("2", "Ambiguous cases", "Guessed", "Reasoned like the examples"),
    ("3", "New patterns", "—", "Generalised (when the examples show reasoning)"),
    ("4", "Informal inputs", "Often null", "Extracted (when the examples vary)"),
    ("5", "Guide reference", "—", "⭐ TS 4.2 · Knowledge 1–4"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="What's wrong\\nwith the output?"];
  FMT [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Format examples\\n(every field)"];
  AMB [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Reasoned, varied\\nambiguous-case examples"];
  NUL [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Examples in varied\\ninput formats"];
  Q2 [shape=diamond, label="Iterating on\\ncode?"];
  TDD [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Share failing tests\\n(expected vs actual)"];
  TOG [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Interacting issues:\\none message"];
  Q1 -> FMT [label="inconsistent shape"]; Q1 -> AMB [label="wrong on edge cases"]; Q1 -> NUL [label="nulls on informal input"];
  Q1 -> Q2 [label="code keeps failing"]; Q2 -> TDD; TDD -> TOG [label="fixes interact"];
}''')

EXPERIMENTS = (
    "Run ✅ on all five scenarios.",
    "In ✅, drop the “why” from just one routing example: does it still generalise? (the lab needs ≥ 2 reasoned examples)",
    "Run ❌ C and read which tool the “news search results” request went to.",
    "In the playground's iterate tab, write your own feedback and find the minimum that converges.",
)

QUESTIONS = (
    Question(
        q=("A CI review prompt lists the fields every finding needs (location, issue, severity, suggested fix), but "
           "findings still come back in varying shapes that the comment bot can't post. What's the most effective fix?"),
        opts=("Add a few examples that show findings in exactly the required format.",
              "Repeat the field list in capital letters.",
              "Post-process the output with a formatter.",
              "Lower the temperature."),
        ans=0,
        explain=("When instructions alone give inconsistent results, few-shot examples are the most effective way to get "
                 "consistently formatted, actionable output."),
        scenarios=(5,), points=("4.2:K1", "4.2:S2"),
    ),
    Question(
        q=("A support agent hesitates between get_customer and lookup_order on requests like “it's about my last "
           "purchase”, and picks inconsistently. What's the best prompt addition?"),
        opts=("A rule: “when in doubt, call both tools”.",
              "A longer description of each tool's parameters.",
              "Two to four targeted examples of ambiguous requests, each showing the chosen tool and why it beat the alternative.",
              "An instruction to ask the customer which tool to use."),
        ans=2,
        explain=("Targeted examples for ambiguous cases show why one action beats plausible alternatives, which teaches "
                 "the model how to handle the ambiguity."),
        scenarios=(1,), points=("4.2:K2", "4.2:S1"),
    ),
    Question(
        q=("Every time the agent mishandles a new kind of ambiguous request, the team adds another rule to the prompt. "
           "After 30 rules it still fails on phrasings nobody anticipated. What approach generalises better?"),
        opts=("Keep adding rules, since coverage will eventually be complete.",
              "Replace the rules with one instruction: “use your best judgment”.",
              "Send unusual requests to a human by default.",
              "A few well-chosen examples that demonstrate the reasoning, so the model can apply the same judgment to new patterns."),
        ans=3,
        explain=("Examples let the model generalise judgment to new patterns, not just match the listed cases. Rule lists "
                 "only cover what was anticipated."),
        scenarios=(1, 3), points=("4.2:K3",),
    ),
    Question(
        q=("Extracting product dimensions, the pipeline returns null for required measurements whenever documents use "
           "informal wording like “about two metres” or “a shade under 50cm”. What's the best fix?"),
        opts=("Make the measurement fields optional.",
              "Add examples covering varied and informal ways measurements are written, with the correct extraction for each.",
              "Tell the model never to return null.",
              "Pre-process documents with a regex that finds numbers."),
        ans=1,
        explain=("Examples with varied formats fix empty or null extraction of required fields, and reduce hallucination "
                 "on informal measurements. Forbidding null invites made-up values."),
        scenarios=(6,), points=("4.2:K4", "4.2:S5"),
    ),
    Question(
        q=("The CI reviewer keeps flagging the team's standard retry decorator as “unsafe error handling”, while also "
           "missing real cases of swallowed exceptions. What's the most effective prompt change?"),
        opts=("Examples that contrast the acceptable decorator pattern with genuinely swallowed exceptions.",
              "An instruction to skip all error-handling findings.",
              "A rule to ignore any function with a decorator.",
              "A higher severity threshold for error-handling findings."),
        ans=0,
        explain=("Examples that separate acceptable code patterns from real issues cut false positives while still "
                 "generalising to the real problems. Blanket skips hide genuine bugs."),
        scenarios=(5,), points=("4.2:S3",),
    ),
    Question(
        q=("A citation extractor works on papers with a bibliography at the end, but misses or duplicates citations in "
           "papers that cite inline (Author, 2021) with no bibliography. What's the best fix?"),
        opts=("Tell the model that all papers have bibliographies.",
              "Pre-convert inline citations into a bibliography with a script.",
              "Add examples showing correct extraction from both structures: inline citations and end-of-paper bibliographies.",
              "Only process papers that have bibliographies."),
        ans=2,
        explain=("Examples showing correct handling of varied document structures, such as inline citations vs "
                 "bibliographies, teach the model both shapes."),
        scenarios=(6, 3), points=("4.2:S4",),
    ),
    Question(
        q=("A developer describes in prose how Claude Code should convert API field names (snake_case to camelCase, but "
           "keep “ID” uppercase and leave “_links” alone). Each run interprets the rules slightly differently. What "
           "communicates the transformation best?"),
        opts=("A longer, more precise paragraph.",
              "Asking Claude to restate the rules before starting.",
              "Running the conversion several times and keeping the most common result.",
              "Two or three concrete input → output examples, including the exceptions."),
        ans=3,
        explain=("Concrete input/output examples are the most effective way to communicate a transformation when prose "
                 "is interpreted inconsistently."),
        scenarios=(2,), points=("3.5:K1", "3.5:S1"),
    ),
    Question(
        q=("A developer asks Claude Code to fix a data migration script and replies “still broken” after each attempt. "
           "It takes many rounds. What's the more effective way to iterate?"),
        opts=("Describe the bug in more detail each time.",
              "Write tests covering the expected behaviour and edge cases first, then share the specific test failures after each attempt.",
              "Ask Claude to try a completely different approach each round.",
              "Switch to plan mode for every attempt."),
        ans=1,
        explain=("Test-driven iteration means writing tests first, then iterating by sharing test failures. That gives "
                 "each round a precise target instead of “still broken”."),
        scenarios=(2,), points=("3.5:K2", "3.5:S2"),
    ),
    Question(
        q=("A developer who has never built a caching layer asks Claude Code to add one to a busy API. They're not sure "
           "what they haven't thought of. What's the best way to start?"),
        opts=("Have Claude interview them first, asking about invalidation, failure modes and consistency needs, before implementing.",
              "Ask Claude to implement the most common caching approach straight away.",
              "Enable extended thinking and let Claude decide everything.",
              "Copy a caching layer from another project."),
        ans=0,
        explain=("The interview pattern has Claude ask questions that surface considerations the developer may not have "
                 "anticipated, such as cache invalidation and failure modes, before implementing in an unfamiliar domain."),
        scenarios=(2,), points=("3.5:K3", "3.5:S3"),
    ),
    Question(
        q=("A migration script generated by Claude Code crashes on rows where middle_name is null, and a vague bug report "
           "didn't fix it. What's the most effective next message?"),
        opts=("“Please handle all edge cases.”",
              "“The script fails sometimes; be more careful.”",
              "Specific test cases with example input rows (including null middle_name) and the exact expected output.",
              "The full production database dump."),
        ans=2,
        explain=("Specific test cases with example input and expected output fix edge-case handling, such as nulls in "
                 "migration scripts, far better than general appeals."),
        scenarios=(2,), points=("3.5:S4",),
    ),
    Question(
        q=("Two bugs interact: the tax calculation depends on how the order total is rounded, and both are wrong. A third "
           "bug, a typo in an email template, is unrelated. How should the developer raise them with Claude Code?"),
        opts=("All three in one message.",
              "One at a time, starting with the typo.",
              "The tax bug first, then rounding, then the typo, each in turn.",
              "The rounding and tax bugs together in one detailed message; the typo separately."),
        ans=3,
        explain=("Interacting problems go in a single detailed message so the fixes fit together. Independent problems "
                 "are best fixed one at a time."),
        scenarios=(2,), points=("3.5:K4", "3.5:S5"),
    ),
)


FAQ = (
    ("2–4 examples or 3–5?",
     "The guide says 2–4 targeted examples for ambiguous scenarios; the docs suggest 3–5. Both mean a handful of relevant, varied "
     "examples, not dozens."),
    ("Won't examples make Claude copy them too literally?",
     "It can, if they're all alike. The docs' answer is diversity: vary the outcomes and edge cases so no unintended pattern "
     "stands out. Reasoning in the examples helps the model take the method, not the surface."),
    ("What's the interview pattern?",
     "Before implementing in an unfamiliar area, ask Claude to question you: about cache invalidation, failure modes, edge "
     "cases. It surfaces considerations you hadn't planned for (TS 3.5)."),
)

PLAYGROUND_INTRO = """
One tab per technique. In the iterate tab, type the feedback you'd give after the tests fail. The **simulated** model converges
only if you name the failing tests with expected vs actual.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="fewshot")


PLAYGROUND = (
    _tab("format", "⭐ Format examples", "format", "Students copy the layout of the worked solution.", "guide:4.2:K1",
         "How many complete format examples the prompt includes.", "prompting best practices § Use examples; guide TS 4.2 S2",
         ("n_examples",), {"n_examples": "2"}, ("Review this diff",), ("0 or 1 example: three different shapes.",)),
    _tab("routing", "⭐ Ambiguous cases", "routing", "Show the working, not just the answer.", "guide:4.2:S1",
         "Three routing examples, then a request worded differently.", "guide TS 4.2 K2–K3, S1; docs § diverse examples",
         ("ex_style",), {"ex_style": "reasoned"}, ("Route the new request",), ("answers only: wrong tool.", "all alike: “always doc”.")),
    _tab("extract", "⭐ Varied formats", "extract", "Worked examples in cm, feet and “about”.", "guide:4.2:S5",
         "Heights written four different ways.", "guide TS 4.2 K4, S5", ("ex_formats",), {"ex_formats": "varied"},
         ("Extract the heights",), ("one format: three nulls.",)),
    _tab("iterate", "⭐ Iterate", "iterate", "“Q3 expected 12, you wrote 21.”", "guide:3.5:S2",
         "Your message is the feedback after two tests fail.", "guide TS 3.5 K2, S2", (), {},
         ("test_null_email: expected row skipped, warning logged, got TypeError. test_duplicate_id: expected second row merged, got IntegrityError",
          "It still doesn't work, please fix it."), ("vague: 4 rounds, still failing.",)),
    _tab("fix", "⭐ Together or one by one", "fix", "Untie tangled knots together.", "guide:3.5:S5",
         "Two bugs that interact.", "guide TS 3.5 K4, S5", ("fix_mode",), {"fix_mode": "together"}, ("Fix the rounding and tax bugs",),
         ("one by one: fixes undo each other.",)),
)

CONTENT = ConceptContent(
    slug="prompt-engineering-techniques", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("system-prompts", "structured-outputs", "evaluation"), exam_points=EXAM_POINTS, playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO,
    scenarios=("format_consistency", "ambiguous_case", "informal_extraction", "test_driven", "interacting_issues"), show_ledger=False,
)
