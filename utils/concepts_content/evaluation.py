"""
D2.5 Tool Evaluation & Testing — measuring whether an agent picks the right tool (with the right input) before a tool set
ships: an eval set that includes ambiguous and edge requests, per-category success criteria, exact code-based grading and a
full re-run after every change. PARTIAL in the guide: §7 (p.24) says to test tool-selection reliability with ambiguous
requests; TS 2.1 (p.9) supplies what goes wrong. The method comes from the platform docs.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); platform docs fetched 2026-09-28 (DOC_REFS). Every
claim is in GROUNDING with its source type. Paraphrased; no real exam question reproduced.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"
GUIDE_S7 = "⭐ EXAM — Guide §7 · How to Prepare · p.24"

DOC_REFS = (
    DocRef("Define success and build evaluations", f"{_P}/test-and-evaluate/develop-tests"),
    DocRef("Troubleshooting tool use — Claude calls the wrong tool", f"{_P}/agents-and-tools/tool-use/troubleshooting-tool-use"),
    DocRef("Define tools — best practices for tool definitions", f"{_P}/agents-and-tools/tool-use/define-tools"),
)

GROUNDING = (
    Claim("Good success criteria are specific, measurable, achievable and relevant; most use cases need several criteria "
          "(multidimensional evaluation), not one number.", "docs", "develop-tests § Defining success criteria; Multidimensional"),
    Claim("Evals should mirror the real task distribution and include edge cases — including ambiguous cases where even humans "
          "would disagree.", "docs", "develop-tests § Eval design principles; edge cases"),
    Claim("Automate grading where possible (exact match, string match, code-graded, LLM-graded); more automated questions beat "
          "fewer hand-graded ones.", "docs", "develop-tests § Eval design principles"),
    Claim("Exact-match evaluation suits categorical answers with a clear correct value.", "docs", "develop-tests § Exact match"),
    Claim("When LLM-based grading is used, grade with a different model from the one that produced the output.", "docs",
          "develop-tests § LLM-based Likert"),
    Claim("Claude calls tool A instead of B → sharpen descriptions, differentiating tools by WHEN to use them; wrong parameter "
          "types → strict: true or input_examples.", "docs", "troubleshooting-tool-use § Claude calls the wrong tool"),
    Claim("Preparation advice: test tool-selection reliability with ambiguous requests, alongside descriptions that clearly "
          "differentiate similar tools.", "guide", "Guide §7 · How to Prepare · p.24"),
    Claim("Tool descriptions are the main way the model selects tools; minimal ones make selection among similar tools "
          "unreliable, and ambiguous or overlapping descriptions cause misrouting (analyze_content vs analyze_document).",
          "guide", "TS 2.1 · Knowledge 1, 3 · p.9"),
    Claim("The guide has no task statement on evaluation; the evaluation method on this page comes from the platform docs.",
          "guide", "Guide §6 (no TS) vs develop-tests"),
    Claim("Re-running the whole suite after every change (not just the cases that failed before) is this page's recommendation, "
          "following the docs' 'mirror the real task distribution' principle.", "recommendation", "develop-tests § Eval design principles"),
    Claim("The router, the tool-set versions, the production traffic and the 90 % bar that judges a release are invented.",
          "simulated", "utils/eval_lab.py, utils/tool_select_lab.py"),
)

CORRECT = r'''from utils.eval_lab import job, release     # SIMULATED tool router + release gate

C = lambda request, expect, category, expect_input=None: {
    "request": request, "expect": expect, "category": category, "expect_input": expect_input}

# 1. A test set that mirrors real traffic: clear requests, AMBIGUOUS ones and edge cases
TEST_SET = [
    C("Does the attached report actually support the claim that churn fell 5%?", "verify", "clear"),
    C("Does the attached audit actually support the claim that prices rose 8%?", "verify", "clear"),
    C("Extract every price and date from the uploaded contract PDF.", "extract", "clear"),
    C("Pull the payment terms and amounts out of the attached invoice PDF.", "extract", "clear"),
    C("Where is the order for carol@example.com?", "customer", "clear"),
    C("Find the customer record for erin@example.com.", "customer", "clear"),
    C("Give me a short summary of the attached quarterly report.", "summarize", "clear"),
    C("Condense the attached annual report into a short overview.", "summarize", "clear"),
    C("Does the attached report actually support the claim that sales doubled?", "verify", "clear"),
    C("Extract all names and dates from the attached PDF agreement.", "extract", "clear"),
    C("Pull the key facts out of these web search results about solar panel prices.", "web", "ambiguous"),
    C("Turn these web search results into a short summary for the team.", "web", "ambiguous"),
    C("Summarize the key facts from these web results on heat pumps.", "web", "ambiguous"),
    C("What's the status of order 1001?", "order", "edge", {"order_id": "ORD-1001"}),
    C("order 2002 - has it shipped?", "order", "edge", {"order_id": "ORD-2002"}),
    C("Has order 5005 arrived yet?", "order", "edge", {"order_id": "ORD-5005"}),
]

# 2. Specific, measurable criteria - one per category, not one overall number
CRITERIA = {"clear": 0.95, "ambiguous": 0.90, "edge": 1.00}


def grade(case, result):
    """Code-based exact match: the right JOB, and the right INPUT where it matters."""
    if job(result["tool"]) != case["expect"]:
        return False
    return case["expect_input"] is None or result["input"] == case["expect_input"]


def decide(report):
    """Ship only if EVERY category meets its bar."""
    for category, bar in CRITERIA.items():
        if category not in report:
            print(f"no test cases for '{category}' - can't claim it works")
            return False
        if report[category]["accuracy"] < bar:
            print(f"'{category}' at {report[category]['accuracy']:.0%} is below its bar of {bar:.0%}")
            return False
    return True


def select_cases(test_set, previous_failures):
    """After a change, re-run the WHOLE suite - a fix in one place can break another."""
    return test_set


release(TEST_SET, grade, decide, select_cases)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ Guide §7 + TS 2.1 K3 — no ambiguous requests in the test set
VARIANT_A = _swap(CORRECT, '''    C("Pull the key facts out of these web search results about solar panel prices.", "web", "ambiguous"),
    C("Turn these web search results into a short summary for the team.", "web", "ambiguous"),
    C("Summarize the key facts from these web results on heat pumps.", "web", "ambiguous"),
''', '''    # WRONG: only clear, easy requests - no ambiguous ones
''')
VARIANT_A = _swap(VARIANT_A, '''CRITERIA = {"clear": 0.95, "ambiguous": 0.90, "edge": 1.00}''', '''CRITERIA = {"clear": 0.95, "edge": 1.00}''')
# 📘 docs — one overall number instead of per-category criteria
VARIANT_B = _swap(CORRECT, '''def decide(report):
    """Ship only if EVERY category meets its bar."""''', '''def decide(report):
    return report["_overall"]["accuracy"] >= 0.80   # WRONG: one overall number hides a failing category''')
# 📘 docs — a grader that doesn't check the answer
VARIANT_C = _swap(CORRECT, '''    """Code-based exact match: the right JOB, and the right INPUT where it matters."""''',
                  '''    return result["tool"] is not None   # WRONG: "a tool was called" counts as a pass''')
# 💡 recommendation (docs principle) — only re-run what failed last time
VARIANT_D = _swap(CORRECT, '''    return test_set


release(''', '''    return previous_failures   # WRONG: only re-checks what failed last time


release(''')
# 📘 docs — grade the tool, not its input
VARIANT_E = _swap(CORRECT, '''    return case["expect_input"] is None or result["input"] == case["expect_input"]''',
                  '''    return True   # WRONG: right tool counts as right - the input isn't checked''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "eval_release"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "rel": ev[-1] if ev else None}


def _diagnose(f):
    r = f["rel"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "release() was never called"
    rep = r["report"]
    txt = (f"candidate {r['candidate']} · ran {r['cases_run']}/{r['test_set_size']} cases · categories tested: {r['categories']} · "
           + " · ".join(f"{k} {d['accuracy']:.0%}" for k, d in rep.items())
           + f" · decision: {'SHIP' if r['ship'] else 'BLOCK'} · production: {r['prod']} → {'GOOD' if r['prod_ok'] else 'BAD'} release")
    if r["ship"] == r["prod_ok"]:
        return True, None, txt
    if not r["ship"]:
        return False, "BLOCKGOOD", txt
    if "ambiguous" not in r["categories"]:
        return False, "NOAMBIG", txt
    if r["cases_run"] < r["test_set_size"]:
        return False, "PARTIAL", txt
    failed_rows = [x for x in r["rows"] if not x["passed"]]
    if not failed_rows and any(x["tool"] and x["expect"] and x["expect"] != "?" for x in r["rows"]):
        wrong_job = [x for x in r["rows"] if x["expect"] and x["tool"] and x["expect"] != _job(x["tool"])]
        wrong_input = [x for x in r["rows"] if x["category"] == "edge"]
        if wrong_job:
            return False, "LENIENT", txt
        if wrong_input:
            return False, "NOINPUT", txt
    return False, "OVERALL", txt


def _job(tool):
    from utils.tool_select_lab import KIND
    return KIND.get(tool, "unknown")


EXPECTED = {
    "ambiguous_traffic": "BLOCK — the candidate misroutes ambiguous web-results requests in production",
    "fixed_tools": "SHIP — the candidate is good in every category",
    "regression": "BLOCK — the new version fixed the web requests but broke order-id formatting",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "set":   ("#DBEAFE", "#0066CC", "the test set"),
    "crit":  ("#FEF3C7", "#D97706", "success criteria & grading (docs)"),
    "run":   ("#CCFBF1", "#0D9488", "running and deciding"),
    "bug":   ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "SET":    ("⭐ Test set mirrors real traffic:\\nclear + AMBIGUOUS + edge requests", "box", "set"),
    "CRIT":   ("Criteria per category\\n(specific, measurable)", "box", "crit"),
    "GRADE":  ("Exact code-based grading:\\nright job AND right input", "box", "crit"),
    "RUN":    ("Run the WHOLE suite\\non the candidate", "box", "run"),
    "REPORT": ("Report per category", "box", "run"),
    "DECIDE": ("Every category\\nat its bar?", "diamond", "run"),
    "SHIP":   ("Ship", "box", "run"),
    "BLOCK":  ("⭐ Block → sharpen the\\ndescriptions, re-run", "box", "run"),
    "NOAMBIG": ("✗ no ambiguous\\ntest cases", "box", "bug"),
    "OVERALL": ("✗ one overall\\nnumber", "box", "bug"),
    "LENIENT": ("✗ “a tool was called”\\ncounts as a pass", "box", "bug"),
    "PARTIAL": ("✗ re-ran only last\\ntime's failures", "box", "bug"),
    "NOINPUT": ("✗ graded the tool,\\nnot its input", "box", "bug"),
    "BLOCKGOOD": ("✗ blocked a good\\nrelease", "box", "bug"),
}
_BUGS = ["NOAMBIG", "OVERALL", "LENIENT", "PARTIAL", "NOINPUT", "BLOCKGOOD"]
_EXP = {"ambiguous_traffic": ["SET", "CRIT", "GRADE", "RUN", "REPORT", "DECIDE", "BLOCK"],
        "fixed_tools": ["SET", "CRIT", "GRADE", "RUN", "REPORT", "DECIDE", "SHIP"],
        "regression": ["SET", "CRIT", "GRADE", "RUN", "REPORT", "DECIDE", "BLOCK"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (§7 p.24, TS 2.1 p.9)</FONT></TD></TR>')
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
    lines += ["  SET -> CRIT -> GRADE -> RUN -> REPORT -> DECIDE;", '  DECIDE -> SHIP [label="yes"]; DECIDE -> BLOCK [label="no"];',
              "  { rank=same; SHIP; BLOCK; }", '  BLOCK -> RUN [label="after the fix", style=dashed, constraint=false];',
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  SHIP -> NOAMBIG [style=invis];", _key(hl),
              f"  {_BUGS[0]} -> KEY [style=invis];", "}"]
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def node_states(trace):
    if not trace:
        return {}
    f = _facts(trace)
    ok, bug, _ = _diagnose(f)
    s = {}
    for n in _EXP.get(f["scenario"], []):
        s[n] = ("ok", "") if ok else ("ok", "")
    if not ok:
        want = _EXP.get(f["scenario"], [])[-1]
        s[want] = ("bad", "what should have happened")
    if bug:
        s[bug] = ("bad", "your run")
    return s


EXAM_POINTS = (
    ExamPoint("2.1", "K", 1, "Tool descriptions are the main mechanism for tool selection; minimal ones make selection among similar tools unreliable.",
              "✅ ambiguous_traffic (v1's minimal descriptions) · playground “Try a request”"),
    ExamPoint("2.1", "K", 3, "Ambiguous or overlapping descriptions (analyze_content vs analyze_document) cause misrouting.",
              "✅ the ambiguous category catches v1 · ❌ A"),
    ExamPoint("2.1", "S", 1, "Write descriptions that clearly differentiate each tool's purpose, inputs, outputs and when to use it.",
              "✅ BLOCK → sharpen the descriptions → fixed_tools ships"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ ambiguous cases in the suite · per-category bars · exact grading · full re-run", "correct", CORRECT, "ambiguous_traffic",
            observe=("ambiguous_traffic: clear 10/10, edge 3/3, but ambiguous 0/3 — every web-results request goes to a document tool "
                     "(extract_data_points / summarize_content). “'ambiguous' at 0% is below its bar of 90%” → BLOCK, and production "
                     "agrees (ambiguous 0.0). fixed_tools: 16/16 → SHIP, production all 1.0. regression: v3 fixed the web requests but "
                     "order ids come back as '1001' not 'ORD-1001' → edge 0/3 → BLOCK."),
            why=("The suite looks like real traffic (including the ambiguous requests the guide says to test), every category has its "
                 "own measurable bar, the grader checks the exact job AND input, and the whole suite runs after every change.")),
    Variant("A", "⭐❌ A — no ambiguous requests in the test set", "distractor", VARIANT_A, "ambiguous_traffic",
            observe="clear 10/10, edge 3/3 → 100% → SHIP. Production: ambiguous 0.0 — every web-results request misroutes.",
            why="An eval can only find failures it has cases for; ambiguous requests are exactly where similar tools get confused.",
            fix="Add ambiguous (and edge) requests to the suite, with their own bar.", source=GUIDE_S7),
    Variant("B", "❌ B — one overall number", "distractor", VARIANT_B, "ambiguous_traffic",
            observe=("The report shows ambiguous 0/3, but overall is 13/16 = 81% ≥ 80% → SHIP. Production: ambiguous 0.0. In "
                     "regression the same 81% ships v3 with edge 0/3."),
            why="An average of a big healthy category and a small broken one looks fine; the docs call for specific criteria along several dimensions.",
            fix="A bar per category; ship only if every category meets its bar.", source="docs"),
    Variant("C", "❌ C — “a tool was called” counts as a pass", "distractor", VARIANT_C, "ambiguous_traffic",
            observe="Every case passes (16/16) even though v1 sends all three web requests to document tools → SHIP a bad release. Same in regression.",
            why="A grader must compare with the right answer; the docs recommend exact-match grading for categorical outputs like a tool choice.",
            fix="Grade the exact job (and the input when it matters).", source="docs"),
    Variant("D", "❌ D — re-run only last time's failures", "distractor", VARIANT_D, "regression",
            observe=("Only the 3 previously failing web cases are re-run on v3 (they now pass); the other 13 keep their stale v1 "
                     "results, so edge shows 3/3 → SHIP. Production: edge 0.0 — the ORD- formatting broke."),
            why="A fix in one description can break another behaviour; only a full re-run sees it.",
            fix="Re-run the whole suite after every change.", source="💡 my recommendation — from the docs' “mirror the real task distribution” principle"),
    Variant("E", "❌ E — grade the tool, not its input", "distractor", VARIANT_E, "regression",
            observe="lookup_order is chosen for “order 1001”, with order_id '1001' instead of 'ORD-1001' — graded as a pass → SHIP. Production: edge 0.0.",
            why="Picking the right tool with the wrong arguments still fails the user; the docs list wrong parameters as its own tool-use failure.",
            fix="Check the input where it matters (and use strict / input_examples to prevent it).", source="docs"),
)

TLDR = (
    "Before a tool set ships, **measure** whether the model picks the right tool **with the right input**. The guide's "
    "instruction (§7): **test tool-selection reliability with ambiguous requests**. The method comes from the docs:\n\n"
    "- A test set that mirrors real traffic, including **ambiguous and edge cases**.\n"
    "- **Specific, measurable bars per category**, not one average.\n"
    "- **Automated exact grading**: the right job and the right input.\n"
    "- **Re-run everything after every change.**\n\n"
    "When a category fails, the fix the docs and guide point to is **sharper tool descriptions**, not a bigger model."
)
MENTAL_MODEL = ("An eval is a driving test with the hard junctions on the route. A test that only has straight roads (clear "
                "requests) passes a driver who can't handle a roundabout (ambiguous requests). One overall score hides the "
                "roundabout. And after a repair you re-drive the whole route, not just the corner that failed last time.")

WHAT_IT_IS = """
The exam guide has **no task statement on evaluation**. Its study advice says to test tool selection with ambiguous requests
(Guide §7 · How to Prepare · p.24). Task statement 2.1 (p.9) explains why it matters: minimal or overlapping descriptions make
selection unreliable. The **method** on this page comes from the platform docs (*Define success and build evaluations*,
*Troubleshooting tool use*).

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | Source |
|---|---|---|---|
| 1 | Ambiguous test cases | Put the roundabout on the test route, or you'll never see the driver fail it. | ⭐ Guide §7 · p.24; TS 2.1 · Knowledge 3 |
| 2 | Per-category success criteria | A report card with a mark per subject — an average hides the failed one. | 📘 docs |
| 3 | Specific, measurable bars | “Ambiguous ≥ 90%” can fail; “works well” can't. | 📘 docs |
| 4 | Exact, automated grading | Check the answer against the key, not whether the student wrote something. | 📘 docs |
| 5 | Grade the input too | The right tool with the wrong order id still sends the customer the wrong parcel. | 📘 docs |
| 6 | Full re-run after a change | Re-drive the whole route after a repair — the fix can break another corner. | 💡 my recommendation (docs principle) |
| 7 | Fix = sharper descriptions | When the tool choice fails, rewrite WHEN to use each tool, not the test. | ⭐ TS 2.1 · Knowledge 1, Skill 1; 📘 docs |

**Grading methods** (docs)

| # | Method | Good for | In this lab |
|---|---|---|---|
| 1 | Exact match (code) | Categorical answers with one right value | ✅ The tool's job, and the order id |
| 2 | String match (code) | Output that must contain a phrase | — |
| 3 | LLM-based grading | Nuance: tone, empathy (use a **different** model to grade) | — |
| 4 | Human grading | Small, hard sets | — (the docs prefer more automated cases) |

**What a good tool-selection eval looks like**

| # | Part | This lab |
|---|---|---|
| 1 | Clear requests | 10 — one right tool each |
| 2 | ⭐ Ambiguous requests | 3 — web search results that sound like documents |
| 3 | Edge cases | 3 — bare order numbers that must be formatted `ORD-####` |
| 4 | Bars | clear 95% · ambiguous 90% · edge 100% |
| 5 | Grader | exact job + exact input |
| 6 | After a change | the whole suite again |
"""

HOW_IT_WORKS = """
1. **Collect requests that mirror real traffic,** including ambiguous and edge cases, each labelled with the right job
   (and input).
2. **Set a bar per category** — specific and measurable.
3. **Grade automatically and exactly:** the job the chosen tool does, and its input where it matters.
4. **Report per category and decide:** ship only if every category meets its bar.
5. **When a category fails,** sharpen the descriptions (say WHEN to use each tool; add boundaries). Then re-run the
   **whole** suite.
"""

WHERE_SEEN = """
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): tools with overlapping purposes that must be told apart.
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): web results vs documents — the ambiguity this lab tests.
- **Guide §8, Exercise 1** (pp.24–25): build tools with similar functionality and test that the agent picks correctly.
"""

GUIDE_NOTE = ("Partly in the guide: §7 (p.24) and TS 2.1 (p.9) set what to test; the evaluation method is from the platform "
              "docs (verified 2026-09-28 — pages listed above). Section layout inspired by a community concept list "
              "(claudearchitectcertification.com — community source, unverified; no text copied).")

LAB_INTRO = """
You write an **eval harness**: a test set, success criteria, a grader, a release decision and a re-run policy. The lab runs it
on a candidate tool set through the **simulated** tool router from D2.1. It then shows what that tool set does on
**production traffic you never saw**. The question every time: **did your harness make the right call?**

- **v1:** a vague web tool.
- **v2:** sharpened descriptions.
- **v3:** v2, but the order-id formatting rule was lost.
"""

DISTRACTORS = (
    ("A · No ambiguous test cases", "The clear cases all pass.", "The failure lives in the cases you didn't write.",
     "Ambiguous + edge cases with their own bar.", GUIDE_S7),
    ("B · One overall number", "81% sounds fine.", "A 0% category hides inside the average.", "A bar per category.", "docs"),
    ("C · “Any tool call” passes", "The agent did call a tool.", "Wrong tool, still a pass.", "Exact grading.", "docs"),
    ("D · Re-run only last failures", "Saves time.", "Stale results hide the new breakage.", "Full re-run after a change.",
     "💡 my recommendation (docs principle)"),
    ("E · Grade the tool, not its input", "The right tool was chosen.", "'1001' instead of 'ORD-1001' passes.", "Check the input too.", "docs"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Eval choice", "Weak version", "Strong version", "What the weak version misses here")
SIDE_BY_SIDE_ROWS = (
    ("1", "Test cases", "Clear requests only", "Clear + ambiguous + edge", "v1's misrouted web requests"),
    ("2", "Success criteria", "Overall ≥ 80%", "Per category", "ambiguous 0% inside an 81% average"),
    ("3", "Grader", "A tool was called", "Exact job + input", "Everything"),
    ("4", "After a change", "Re-run last failures", "Re-run everything", "v3's broken order ids"),
    ("5", "Fix for a failing category", "Edit the test", "Sharpen the tool descriptions", "—"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Does the suite have\\nambiguous + edge cases?"];
  ADD [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Add them\\n(with a bar each)"];
  Q2 [shape=diamond, label="Every category\\nat its bar?"];
  SHIP [shape=box, fillcolor="#D1FAE5", color="#059669", label="Ship"];
  FIX [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Sharpen the descriptions\\n(when to use each tool)"];
  RERUN [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Re-run the WHOLE suite"];
  Q1 -> ADD [label="no"]; ADD -> Q2; Q1 -> Q2 [label="yes"]; Q2 -> SHIP [label="yes"]; Q2 -> FIX [label="no"];
  FIX -> RERUN; RERUN -> Q2;
}''')

EXPERIMENTS = (
    "Run ✅ on all three scenarios and read the per-category report next to production.",
    "In ✅, delete the three ambiguous cases and run ambiguous_traffic — that's ❌ A.",
    "In ✅, lower the ambiguous bar to 0.0: what does the harness decide for v1?",
    "Run ❌ D on regression and find the “reused 13 results” line.",
    "Type your own request in the playground's “Try a request” tab; if v1 and v2 disagree, it belongs in the suite.",
)

QUESTIONS = (
    Question(
        q=("A team's tool-selection eval scores 100% on 200 requests, yet in production the agent keeps routing questions "
           "about web search results to the document-analysis tool. All 200 eval requests were clear-cut, such as “search "
           "the web for…” or “analyse this PDF…”. What should change first?"),
        opts=("Increase the eval to 2,000 requests of the same kind.",
              "Lower the release threshold from 100% to 95%.",
              "Add ambiguous requests that could plausibly fit either tool, since that's where misrouting happens.",
              "Evaluate a different model on the same set."),
        ans=2,
        explain=("Misrouting comes from ambiguous or overlapping cases, so the eval must test tool selection on "
                 "ambiguous requests. More of the same easy requests measures nothing new."),
        scenarios=(3,), points=("2.1:K3",),
    ),
    Question(
        q=("A support agent's eval shows it picks get_customer instead of lookup_order on about half the requests that "
           "mention both a name and an order. Which fix addresses the root cause?"),
        opts=("Rewrite both descriptions to state what each accepts and when to use it rather than the other.",
              "Add a system prompt rule: “if an order is mentioned, always call lookup_order”.",
              "Remove get_customer from the agent.",
              "Retry the request when the wrong tool is chosen."),
        ans=0,
        explain=("Descriptions that separate each tool's purpose, inputs, outputs and when to use it versus similar "
                 "tools fix selection at the source. A keyword rule in the system prompt creates new unintended associations."),
        scenarios=(1,), points=("2.1:S1", "2.1:K4"),
    ),
    Question(
        q=("An eval reports clear requests 100%, ambiguous requests 0% and edge cases 100%, which is 81% overall. The "
           "release rule is “ship if overall ≥ 80%”. What's the problem with this gate?"),
        opts=("80% is too low; it should be 90%.",
              "Edge cases should count double.",
              "Nothing; the agent passes.",
              "An overall average hides a segment that fails completely; gate on each segment's criterion as well."),
        ans=3,
        explain=("Following the testing docs, success criteria should be specific and measurable per behaviour you care "
                 "about. A single average lets a total failure on ambiguous requests ship."),
        scenarios=(3,), basis="docs", in_bank=False,
    ),
    Question(
        q=("After a description change fixes the misrouted requests, a developer re-runs only the cases that failed "
           "before, sees them pass, and ships. A week later previously correct requests start failing. What should the "
           "process have been?"),
        opts=("Re-run only the failures, but twice.",
              "Re-run the whole eval suite after every change to catch regressions.",
              "Skip evals for description-only changes.",
              "Test the change directly in production with a feature flag."),
        ans=1,
        explain=("A description change affects every routing decision, not just the ones it was meant to fix. Re-running "
                 "the full, automated suite catches regressions. That's the purpose of an eval."),
        scenarios=(3,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Is tool evaluation on the exam?",
     "The guide has no task statement for it. Its study advice (§7, p.24) says to test tool selection with ambiguous requests. "
     "TS 2.1 covers why selection fails. Questions tend to ask about the fix — sharper descriptions — rather than eval design."),
    ("Why grade the input and not just the tool?",
     "A call to the right tool with a wrong argument (1001 instead of ORD-1001) still fails. The docs treat wrong parameters as a "
     "failure of their own, fixed with strict: true or input_examples."),
    ("Should an LLM grade tool selection?",
     "Not usually — the right tool is a categorical answer, so exact matching in code is simpler and more reliable. The docs keep "
     "LLM grading for nuance like tone, and say to grade with a different model."),
    ("How big should the suite be?",
     "The docs favour more automated cases over fewer hand-graded ones. Make every category big enough that its bar means "
     "something."),
)

PLAYGROUND_INTRO = """
Switch the harness's choices on and off and pick a candidate tool set. Each run shows your per-category report, your ship or
block decision, and the production truth. The last tab routes any request you type through the vague and the sharpened tool
sets. If they disagree, that request belongs in your test set.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="evaltools")


PLAYGROUND = (
    _tab("coverage", "⭐ Test-set coverage", "coverage", "Put the roundabout on the route.", "",
         "Does the suite contain ambiguous requests?", "Guide §7 p.24; develop-tests § edge cases",
         ("candidate", "cover_ambiguous"), {"candidate": "v1", "cover_ambiguous": "yes"}, ("Release check",),
         ("v1 + ambiguous cases: BLOCK (right).", "v1 without them: SHIP a bad release.", "v2 either way: SHIP (right).")),
    _tab("criteria", "Success criteria", "criteria", "A mark per subject, not an average.", "",
         "📘 Per-category bars vs one overall number.", "develop-tests § Defining success criteria; Multidimensional",
         ("candidate", "criteria_style"), {"candidate": "v1", "criteria_style": "per_category"}, ("Release check",),
         ("overall ≥ 80% on v1: SHIP at 81% with ambiguous 0%.", "overall ≥ 80% on v3: SHIP with edge 0%.")),
    _tab("grader", "Grader", "grader", "Check the answer against the key.", "",
         "📘 Exact grading of job + input, job only, or “a tool was called”.", "develop-tests § Exact match; troubleshooting-tool-use",
         ("candidate", "grader"), {"candidate": "v1", "grader": "exact"}, ("Release check",),
         ("any tool on v1: 16/16, SHIP a bad release.", "job only on v3: misses the '1001' ids.", "job only on v1: still blocks (the jobs are wrong).")),
    _tab("rerun", "Re-run after a change", "rerun", "Re-drive the whole route after a repair.", "",
         "💡 v3 fixed v1's failures: re-run everything, or only what failed last time?", "develop-tests § Eval design principles",
         ("candidate", "rerun"), {"candidate": "v3", "rerun": "full"}, ("Release check",),
         ("full: BLOCK (edge 0/3).", "failures only: 3 cases re-run, 13 stale results reused → SHIP a bad release.")),
    _tab("try", "Try a request", "try", "If the two tool sets disagree, the request belongs in the suite.", "guide:2.1:K3",
         "Route any request through v1 (vague web tool) and v2 (sharpened).", "troubleshooting-tool-use § Claude calls the wrong tool",
         (), {}, ("Pull the key facts out of these web search results about solar panel prices.",
                  "Summarize the attached report", "What's the status of order 1001?"),
         ("A web-results request: v1 and v2 disagree.", "A document request: they agree.")),
)

CONTENT = ConceptContent(
    slug="evaluation", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("tool-calling", "tool-choice", "mcp"), exam_points=EXAM_POINTS, playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO, scenarios=("ambiguous_traffic", "fixed_tools", "regression"), show_ledger=False,
)
