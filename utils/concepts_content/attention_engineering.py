"""
D4.7 Attention Engineering — laying out long inputs so the important parts get used: a key-findings summary up front and
section headers (the "lost in the middle" effect), the question at the end, case facts kept outside summarised history, and
trimmed tool outputs. PARTIAL in the guide: TS 5.1 (pp.19–20) and TS 1.6 Skill 2 (attention dilution); the docs' long-context
tips supply layout rules. D1.8 covers per-file + integration passes.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); platform prompting best practices (long-context
section) fetched 2026-09-28 (DOC_REFS). Every claim is in GROUNDING with its source type. Paraphrased; no real exam question.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (DocRef("Prompting best practices — Long context prompting; Structure prompts with XML tags",
                   f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices"),)

GROUNDING = (
    Claim("For long inputs (20k+ tokens) put the long documents near the top, above the query, instructions and examples; queries "
          "at the end can improve response quality by up to 30% in tests, especially with complex multi-document inputs.",
          "docs", "prompting best practices § Long context prompting"),
    Claim("Wrap each document in <document> tags with <document_content> and <source> (and other metadata) subtags; ask Claude to "
          "quote the relevant parts first to focus on them.", "docs", "prompting best practices § Long context prompting"),
    Claim("XML tags help Claude parse prompts that mix instructions, context and inputs.", "docs", "prompting best practices § Structure prompts with XML tags"),
    Claim("Progressive summarisation risks condensing numbers, percentages, dates and customer expectations into vague summaries; "
          "models reliably process the beginning and end of long inputs but may omit middle sections; tool results accumulate and "
          "use tokens out of proportion to their relevance (40+ fields when 5 matter).", "guide", "TS 5.1 · Knowledge 1–3 · p.19"),
    Claim("Skills: keep transactional facts (amounts, dates, order numbers, statuses) in a persistent case-facts block outside "
          "summarised history; trim verbose tool outputs to relevant fields; put key-findings summaries at the beginning of "
          "aggregated inputs and organise details under explicit section headers.", "guide", "TS 5.1 · Skills 1, 3, 4 · pp.19–20"),
    Claim("Split large reviews into per-file passes plus a cross-file integration pass to avoid attention dilution.", "guide",
          "TS 1.6 · Skill 2 · p.8"),
    Claim("The guide has no task statement called attention engineering; this page gathers TS 5.1's layout and context skills "
          "with the docs' long-context tips.", "guide", "Guide v1.0 vs concept list"),
    Claim("How the simulated reader drops middle sections, the query-first behaviour, the summariser and the token budget are "
          "invented to make the effects repeatable.", "simulated", "utils/attention_lab.py"),
)

CORRECT = r'''from utils.attention_lab import (QUESTION, SCENARIO, SECTIONS, ask, facts_from, run_conversation, run_lookups,
                                  summarize)   # SIMULATED long-context reader

if SCENARIO in ("lost_in_middle", "query_placement"):
    # key findings FIRST, details under explicit headers, the question LAST
    summary = "KEY FINDINGS:\n" + "\n".join(f"- {s['key']}" for s in SECTIONS)
    details = "\n\n".join(f"## {s['title']}\n{s['text']}" for s in SECTIONS)
    ask(summary + "\n\n" + details + "\n\nQUESTION: " + QUESTION)

elif SCENARIO == "summary_drift":
    def build_context(turns):
        facts = facts_from(turns)                       # amounts, order ids, dates - copied verbatim, never summarised
        case_facts = "CASE FACTS: " + "; ".join(f"{k}={v}" for k, v in facts.items())
        return case_facts + "\n" + summarize(turns[:-1]) + "\n" + turns[-1]
    run_conversation(build_context)

else:  # verbose_tools
    KEEP = ("order_id", "status", "delivered_on", "total", "return_window_days")   # what a return question needs
    run_lookups(lambda order: {k: order[k] for k in KEEP})
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


_ASK = '''    ask(summary + "\\n\\n" + details + "\\n\\nQUESTION: " + QUESTION)'''
# ⭐ TS 5.1 · Skill 4 / Knowledge 2 — no key-findings summary up front
VARIANT_A = _swap(CORRECT, _ASK, '''    ask(details + "\\n\\nQUESTION: " + QUESTION)   # WRONG: the critical finding sits in section 4 of 9''')
# 📘 docs — the question before the long input
VARIANT_B = _swap(CORRECT, _ASK, '''    ask("QUESTION: " + QUESTION + "\\n\\n" + summary + "\\n\\n" + details)   # WRONG: question first, documents after''')
# ⭐ TS 5.1 · Skill 1 / Knowledge 1 — facts left to the summary
VARIANT_C = _swap(CORRECT, '''        return case_facts + "\\n" + summarize(turns[:-1]) + "\\n" + turns[-1]''',
                  '''        return summarize(turns[:-1]) + "\\n" + turns[-1]   # WRONG: the amount, order and date live only in the summary''')
# ⭐ TS 5.1 · Skill 3 / Knowledge 3 — full tool outputs kept
VARIANT_D = _swap(CORRECT, '''    run_lookups(lambda order: {k: order[k] for k in KEEP})''',
                  '''    run_lookups(lambda order: order)   # WRONG: all 40 fields of every lookup stay in context''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "attention_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "nothing ran"
    if r["task"] == "ask":
        txt = (f"question {'first' if r['question_first'] else 'last'} · summary up front: {r['summary_lead']} · headers "
               f"{r['headers']}/9 · drew on {r['used']} · answer: {r['answer']}")
        if r["question_first"]:
            return False, "QFIRST", txt
        if sc == "query_placement":
            return True, None, txt
        if not r["found_critical"]:
            return False, "MIDDLE", txt
        return True, None, txt
    if r["task"] == "conversation":
        txt = f"facts present {r['has']} · answer: {r['answer']}"
        ok = all(r["has"].values())
        return ok, (None if ok else "DRIFT"), txt
    txt = f"fields per lookup {r['fields_kept']} · tokens {r['tokens']:,} · evicted {r['evicted'] or 'none'} · answer: {r['answer']}"
    return r["ok"], (None if r["ok"] else "VERBOSE"), txt


EXPECTED = {
    "lost_in_middle": "the answer names the EU battery rule — the finding in section 4 of 9",
    "query_placement": "the question comes after the documents, and the answer uses all of them",
    "summary_drift": "the last reply repeats $1,240.00, ORD-7731 and Friday 14 March exactly",
    "verbose_tools": "no lookup evicted; ORD-1000's 14-day window is still visible",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "lay":  ("#DBEAFE", "#0066CC", "layout of long inputs"),
    "mem":  ("#FEF3C7", "#D97706", "what stays in context"),
    "out":  ("#EDE9FE", "#7C3AED", "result"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "SUM":    ("⭐ Key-findings summary\\nat the beginning", "box", "lay"),
    "HEAD":   ("⭐ Details under explicit\\nsection headers (or XML tags)", "box", "lay"),
    "QLAST":  ("Question at the END\\n(docs: up to 30% better)", "box", "lay"),
    "FACTS":  ("⭐ Case facts block (amounts,\\nIDs, dates) outside the summary", "box", "mem"),
    "TRIM":   ("⭐ Trim tool outputs to the\\nfields that matter", "box", "mem"),
    "OUT":    ("Nothing important is\\nlost in the middle", "box", "out"),
    "MIDDLE": ("✗ critical finding\\nburied mid-input", "box", "bug"),
    "QFIRST": ("✗ question before\\nthe documents", "box", "bug"),
    "DRIFT":  ("✗ facts only in a\\nprogressive summary", "box", "bug"),
    "VERBOSE": ("✗ full 40-field tool\\noutputs kept", "box", "bug"),
}
_BUGS = ["MIDDLE", "QFIRST", "DRIFT", "VERBOSE"]
_EXP = {"lost_in_middle": ["SUM", "HEAD", "QLAST"], "query_placement": ["SUM", "HEAD", "QLAST"], "summary_drift": ["FACTS"],
        "verbose_tools": ["TRIM"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 5.1 pp.19–20)</FONT></TD></TR>')
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
    lines += ["  SUM -> HEAD -> QLAST -> OUT; FACTS -> OUT; TRIM -> OUT; { rank=same; FACTS; TRIM; }",
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  OUT -> MIDDLE [style=invis];", _key(hl),
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
    ExamPoint("5.1", "K", 1, "Progressive summarisation turns numbers, dates and customer expectations into vague summaries.", "✅ summary_drift · ❌ C"),
    ExamPoint("5.1", "K", 2, "“Lost in the middle”: models use the beginning and end of long inputs reliably but may omit middle sections.",
              "✅ lost_in_middle · ❌ A"),
    ExamPoint("5.1", "K", 3, "Tool results pile up and use tokens out of proportion to their relevance (40+ fields when 5 matter).", "✅ verbose_tools · ❌ D"),
    ExamPoint("5.1", "S", 1, "Keep transactional facts in a persistent case-facts block, outside summarised history.", "✅ build_context · ❌ C"),
    ExamPoint("5.1", "S", 3, "Trim verbose tool outputs to the relevant fields before they accumulate.", "✅ KEEP · ❌ D"),
    ExamPoint("5.1", "S", 4, "Put key-findings summaries at the beginning of aggregated inputs; organise details under explicit headers.",
              "✅ summary + headers · ❌ A"),
    ExamPoint("1.6", "S", 2, "Split large reviews into per-file passes plus a cross-file integration pass to avoid attention dilution.",
              "See D1.8 (task decomposition) and D4.10"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ key findings first · headers · question last · case facts · trimmed tool output", "correct", CORRECT, "lost_in_middle",
            observe=("lost_in_middle / query_placement: the reader uses the summary up front and answers “the EU battery regulation bans our "
                     "pack design from 1 Jan 2027” — the finding in section 4 of 9. summary_drift: CASE FACTS keep $1,240.00, ORD-7731 "
                     "and Friday 14 March exact. verbose_tools: 5 fields per lookup, 800 tokens, nothing evicted — ORD-1000's 14-day "
                     "window is still visible."),
            why="What matters is placed where the model reliably reads it, and facts that must stay exact never pass through a summary."),
    Variant("A", "⭐❌ A — no key-findings summary up front", "distractor", VARIANT_A, "lost_in_middle",
            observe="The reader uses sections 1–3 and 7–9; the EU battery rule in section 4 is missed → “competitor price pressure”.",
            why="Middle sections of long inputs are the likeliest to be omitted; a leading summary puts every key finding at the start.",
            fix="Put a key-findings summary at the beginning.", source="guide:5.1:S4"),
    Variant("B", "❌ B — the question before the documents", "distractor", VARIANT_B, "query_placement",
            observe="The simulated reader answers from the first report only: “competitor prices +4% in Q2”.",
            why="The docs: long documents at the top, the query at the end — up to 30% better on complex multi-document inputs.",
            fix="Documents first, question last.", source="docs"),
    Variant("C", "⭐❌ C — facts left to a progressive summary", "distractor", VARIANT_C, "summary_drift",
            observe="The summary says “refund it soon” — the reply is “Your refund is on its way and should arrive soon”, no amount, order or date.",
            why="Summaries blur numbers, IDs and dates; a case-facts block carries them verbatim.",
            fix="A CASE FACTS block outside the summarised history.", source="guide:5.1:S1"),
    Variant("D", "⭐❌ D — full 40-field tool outputs kept", "distractor", VARIANT_D, "verbose_tools",
            observe="Eight 40-field lookups exceed the budget; ORD-1000 is evicted → “All eight orders can be returned within 30 days.”",
            why="Tool results pile up out of proportion to their relevance; trim them to the fields the question needs.",
            fix="Keep only order_id, status, delivered_on, total, return_window_days.", source="guide:5.1:S3"),
)

TLDR = (
    "Long inputs have weak spots. Models reliably use the **beginning and end** but may drop the **middle** (guide TS 5.1). "
    "Engineer the layout:\n\n"
    "- A **key-findings summary first**.\n"
    "- Details under **explicit headers or XML tags**.\n"
    "- **The question last** — the docs report up to 30% better answers on complex multi-document inputs.\n\n"
    "Engineer what stays in context:\n\n"
    "- A **case-facts block** carries amounts, IDs and dates verbatim, outside any summary.\n"
    "- **Trim tool outputs** to the fields that matter before they pile up.\n"
    "- For big reviews, **per-file passes plus an integration pass** avoid attention dilution (TS 1.6)."
)
MENTAL_MODEL = ("A long input is a long corridor: the model sees the entrance and the exit clearly and hurries past the middle "
                "doors. Put a map at the entrance (key findings), name every door (headers), and ask your question at the exit. "
                "Carry the facts that must stay exact in your pocket (case facts) — don't trust the corridor to remember them.")

WHAT_IT_IS = """
**Partly in the guide.** TS 5.1 (pp.19–20) covers the lost-in-the-middle effect, summarisation risks, tool-output bloat, and
layout skills. TS 1.6 Skill 2 (p.8) covers attention dilution in big reviews. The docs' long-context tips add where to put the
query and how to structure documents.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | Reference |
|---|---|---|---|
| 1 | Lost in the middle | The corridor's middle doors get skipped. | ⭐ TS 5.1 · Knowledge 2 |
| 2 | Key-findings summary first | A map at the entrance. | ⭐ TS 5.1 · Skill 4 |
| 3 | Explicit section headers / XML tags | Name every door. | ⭐ TS 5.1 · Skill 4; 📘 docs |
| 4 | Question at the end | Ask at the exit, after walking the corridor. | 📘 docs (up to 30% better) |
| 5 | Case facts outside summaries | Keep the receipt in your pocket, not in your memory. | ⭐ TS 5.1 · Knowledge 1, Skill 1 |
| 6 | Trim tool outputs | Carry the five facts you need, not the 40-page print-out. | ⭐ TS 5.1 · Knowledge 3, Skill 3 |
| 7 | Attention dilution | One reader, 40 files, no focus — split the review. | ⭐ TS 1.6 · Skill 2 (see D1.8, D4.10) |

**Long-input layout** (guide + docs)

| # | Part | Where | Why |
|---|---|---|---|
| 1 | ⭐ Key-findings summary | Start of the aggregated input | Middle content is the likeliest to be missed |
| 2 | Documents / detailed results | After the summary, each under a header or `<document>` tag with `<source>` | Structure and provenance |
| 3 | Instructions + question | End | Docs: queries at the end can improve quality by up to 30% |
| 4 | “Quote the relevant parts first” | In the instructions | Docs: grounds the answer in the documents |

**What to keep verbatim vs what can be summarised**

| # | Content | Keep verbatim (case facts) | Summarise |
|---|---|---|---|
| 1 | Amounts, order numbers, dates, statuses | ✅ | ❌ |
| 2 | Customer-stated expectations (“by Friday”) | ✅ | ❌ |
| 3 | Chit-chat, repeated explanations | — | ✅ |
| 4 | 40-field tool results | Only the relevant fields | Drop the rest |
"""

HOW_IT_WORKS = """
1. **Aggregating many results?** Put a key-findings summary first, the details under explicit headers (or `<document>` tags),
   and the question last.
2. **Long conversation?** Extract amounts, IDs, dates and promises into a **case-facts block** included on every turn,
   outside the summarised history.
3. **Tool-heavy?** Trim each tool result to the fields the task needs before adding it to the context.
4. **Huge review?** Per-file passes plus a cross-file integration pass (D1.8, D4.10).
"""

WHERE_SEEN = """
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): aggregating many subagents' findings.
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): case facts across long conversations; bulky order lookups.
"""

GUIDE_NOTE = ("Partly in the guide: TS 5.1 (pp.19–20) and TS 1.6 S2 (p.8); layout rules from the platform's long-context tips "
              "(verified 2026-09-28). Section layout inspired by a community concept list (claudearchitectcertification.com — "
              "community source, unverified; no text copied).")

LAB_INTRO = """
A **simulated** long-context reader with the weak spots the guide describes. It reliably uses the start and end of an input
but skips the middle, unless a leading summary mentions what's there. It also answers from the first document only when the
question comes first. Four tasks:

- aggregate nine subagents' findings (twice: layout, then question placement);
- keep a support conversation's facts exact;
- run eight bulky order lookups.
"""

DISTRACTORS = (
    ("A · No summary up front", "Everything is in the input.", "The middle finding is missed.", "Key findings first.", "guide:5.1:S4"),
    ("B · Question first", "Tell the model what to look for.", "Answers from the first document only (simulated).", "Question last.", "docs"),
    ("C · Facts in a summary", "The summary covers it.", "Amount, order and date blur away.", "Case-facts block.", "guide:5.1:S1"),
    ("D · Keep full tool outputs", "More data can't hurt.", "Early results evicted.", "Trim to relevant fields.", "guide:5.1:S3"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Unengineered input", "Engineered input")
SIDE_BY_SIDE_ROWS = (
    ("1", "Order", "Question → nine reports", "Key findings → nine reports under headers → question"),
    ("2", "Middle finding", "Missed", "Used (it's in the summary)"),
    ("3", "Conversation facts", "Inside a summary", "In a case-facts block"),
    ("4", "Tool results", "40 fields each", "5 relevant fields"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="What's long?"];
  LAY [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Summary first, headers,\\nquestion last"];
  FACTS [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Case-facts block\\n(verbatim)"];
  TRIM [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Trim to relevant\\nfields"];
  SPLIT [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Per-file passes +\\nintegration pass"];
  Q1 -> LAY [label="aggregated results"]; Q1 -> FACTS [label="a conversation"];
  Q1 -> TRIM [label="tool outputs"]; Q1 -> SPLIT [label="a big review"];
}''')

EXPERIMENTS = (
    "Run ✅ on all four scenarios.",
    "In ✅, move the EU battery report to section 1 and delete the summary: does it get used now?",
    "Run ⭐❌ C and compare what the model sees with ✅'s CASE FACTS line.",
    "In the playground's layout tab, type your own question and move it to the start.",
)

QUESTIONS = (
    Question(
        q=("A research coordinator concatenates nine subagents' reports (about 60,000 tokens) and asks for the single biggest "
           "risk. In 7 of 10 runs, a critical finding in the fifth report is left out, while findings from the first and "
           "last reports always make it in. What is the best fix?"),
        opts=("Move the fifth report to the start of the input, so that this particular finding is always read first.",
              "Open with a key-findings summary, and organise the detailed reports under explicit section headers.",
              "Switch to a model with a larger context window, so that all nine reports receive equal attention.",
              "Ask the model to read the reports twice before answering, paying special attention to the middle ones."),
        ans=1,
        explain=("Content in the middle of a long input gets less attention (the “lost in the middle” effect). Putting key "
                 "findings at the start and structuring the rest under clear headers counters it. A only moves the problem "
                 "to another report. C: a larger window doesn't fix positional attention. D is an instruction with no "
                 "mechanism behind it."),
        scenarios=(3,), points=("5.1:K2", "5.1:S4"),
    ),
    Question(
        q=("To save space, a long support conversation is summarised every ten turns. After three summaries, the agent tells "
           "a customer “your refund is on its way” but no longer knows it promised £84.20 by Friday on order ORD-5512. The "
           "summary now reads “customer is owed a refund”. What is the best fix?"),
        opts=("Summarise every 20 turns instead of 10, so that fewer details are lost at each summarisation step.",
              "Tell the summariser to “keep important details”, so that amounts and dates are more likely to survive.",
              "Stop summarising and keep the full history, raising the context limit as the conversation grows.",
              "Keep amounts, dates, order numbers and statuses in a persistent case-facts block outside the summary."),
        ans=3,
        explain=("Progressive summarisation turns exact figures and dates into vague statements. Moving transactional facts into "
                 "a persistent block that is included in every prompt keeps them exact. A and B only reduce the loss. C runs "
                 "into the context limit and to degradation over long contexts."),
        scenarios=(1,), points=("5.1:K1", "5.1:S1"),
    ),
    Question(
        q=("Each lookup_order call returns 40+ fields (warehouse codes, carrier events, internal flags), about 1,500 tokens, "
           "and the returns agent uses about five of them. After six lookups in one conversation, the agent confuses the "
           "return windows of two orders. What should change?"),
        opts=("Trim each lookup result to the return-relevant fields before it is added to the context.",
              "Tell the agent in its prompt to ignore warehouse codes, carrier events and internal flags.",
              "Limit each conversation to three lookups, and ask customers to start a new chat after that.",
              "Summarise the whole conversation after every lookup, so that older results take less space."),
        ans=0,
        explain=("Verbose tool output fills the context with irrelevant fields. Trimming results to what the task needs before "
                 "they accumulate keeps the relevant ones sharp. B still loads the noise. C pushes the problem onto the "
                 "customer. D summarises away exactly the details that were being mixed up."),
        scenarios=(1,), points=("5.1:K3", "5.1:S3"),
    ),
    Question(
        q=("In one session a customer raises problems with three orders. In about 1 of 8 such conversations, the agent quotes "
           "the right refund amount against the wrong order. All the agent's facts live in its running summary of the "
           "conversation. What design keeps multi-issue sessions straight?"),
        opts=("Handle only one order per conversation, and ask the customer to open new chats for each of the others.",
              "Ask the agent to repeat all three orders' details at the start of every reply that it writes.",
              "Extract structured data for each issue (order ID, amount, status) into a separate, current layer.",
              "Lengthen the running summary, so that all three orders' details fit into it without compression."),
        ans=2,
        explain=("Structured data per issue (order ID, amount, status), kept in its own context layer, stops values crossing "
                 "between issues. A pushes the work onto the customer. B adds repetition, not structure. D keeps the facts in "
                 "prose that is still summarised."),
        scenarios=(1,), points=("5.1:S2",),
    ),
    Question(
        q=("A developer builds a support chat on the Messages API and, to save tokens, sends only the newest customer message "
           "with each request. In testing, the agent asks for the order number again in 60% of conversations longer than "
           "three turns. What is wrong?"),
        opts=("The model's memory of earlier turns expires after a few minutes, so long chats need a session ID.",
              "Each request must carry the complete conversation history; the API doesn't remember earlier turns.",
              "The system prompt should tell the model to remember order numbers for the rest of the conversation.",
              "The requests should set a conversation_id, so the API can link them into one ongoing session."),
        ans=1,
        explain=("The Messages API is stateless: the model sees only what each request contains, so the history must be sent "
                 "every time. A and D invent server-side memory. C asks the model to remember something it was never sent."),
        scenarios=(1,), points=("5.1:K4",),
    ),
    Question(
        q=("An extraction prompt contains three contracts, about 90,000 tokens in total, and asks which one has the shortest "
           "notice period. The question currently sits at the top, before the documents, and the answer is wrong in about 1 "
           "run in 6. According to the long-context tips in the prompting docs, what should change?"),
        opts=("Repeat the question before each of the three contracts, so that it sits close to every document.",
              "Split the task into three calls, one per contract, and compare the notice periods afterwards in code.",
              "Keep the question first, but put its key words in bold so they stand out against the documents.",
              "Put the documents at the top of the prompt and the question at the end, after all the documents."),
        ans=3,
        explain=("The docs recommend putting long documents at the top and the query at the end, which can noticeably improve "
                 "response quality. A scatters the question around. B may work, but it is a redesign rather than the "
                 "documented fix. C doesn't change the placement."),
        scenarios=(6,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Is “attention engineering” on the exam?",
     "Not by that name. Its parts are: the lost-in-the-middle effect, case facts, trimming, and summaries up front (TS 5.1), "
     "plus attention dilution in big reviews (TS 1.6)."),
    ("Summary at the start and question at the end — isn't that contradictory?",
     "No. The key-findings summary opens the aggregated input, the detailed documents follow, and the instructions and question "
     "come last. The guide's advice covers the first part; the docs' covers the last."),
    ("Doesn't a bigger context window fix this?",
     "It gives more room but not better attention. The middle of a longer input is still the middle. Layout and trimming work "
     "regardless of size."),
)

PLAYGROUND_INTRO = """
Change the layout, what's kept verbatim, and how much of each tool result is kept, then see what the **simulated** reader uses.
In the layout tab, type your own question; in the case-facts tab, the customer's last message.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="attention")


PLAYGROUND = (
    _tab("layout", "⭐ Layout", "layout", "A map at the entrance, the question at the exit.", "guide:5.1:S4",
         "Nine reports; the critical one is fourth.", "prompting best practices § Long context; guide TS 5.1 K2, S4",
         ("lead_summary", "q_position"), {"lead_summary": "yes", "q_position": "end"},
         ("What is the single biggest risk to next year's product plan?",), ("no summary: the EU finding is missed.", "question first: first report only.")),
    _tab("facts", "⭐ Case facts", "facts", "Keep the receipt in your pocket.", "guide:5.1:S1",
         "Older turns are summarised; the customer asks to confirm the amount and date.", "guide TS 5.1 K1, S1",
         ("keep_facts",), {"keep_facts": "yes"}, ("Just confirm the refund amount and the date again please.",),
         ("no case facts: “should arrive soon”.",)),
    _tab("trim", "⭐ Trim tool output", "trim", "Carry five facts, not the print-out.", "guide:5.1:S3",
         "Eight order lookups, then “which orders can still be returned?”.", "guide TS 5.1 K3, S3",
         ("trim_fields",), {"trim_fields": "5"}, ("Which orders can still be returned?",), ("all 40 fields: ORD-1000 evicted.",)),
)

CONTENT = ConceptContent(
    slug="attention-engineering", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("task-decomposition", "multi-pass-review-architectures", "session-state"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("lost_in_middle", "query_placement", "summary_drift", "verbose_tools"), show_ledger=False,
)
