"""
D5.2 Case Facts Block — keeping the facts a long conversation depends on exact: a structured block, one record per issue,
updated as statuses change, holding what the customer said they need as well as what the tools returned, and included in
every prompt OUTSIDE the summarised history. Guide TS 5.1 (Knowledge 1, Skills 1–2, pp.19–20) + the docs' state-management
advice (structured formats for state data). D4.7 introduces the idea next to layout; D5.1 covers the window as a budget.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); platform prompting best practices (State management
best practices; Workflows across multiple context windows) and Context windows / Compaction pages fetched 2026-09-28
(DOC_REFS). Every claim is in GROUNDING with its source type. Paraphrased; no real exam question.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (
    DocRef("Prompting best practices — State management best practices; Workflows across multiple context windows",
           f"{_P}/build-with-claude/prompt-engineering/claude-prompting-best-practices"),
    DocRef("Context windows — how turns accumulate; compaction", f"{_P}/build-with-claude/context-windows"),
    DocRef("Compaction overview — write your own summarization prompt when the default drops something", f"{_P}/build-with-claude/compaction"),
)

GROUNDING = (
    Claim("Progressive summarisation risks condensing numerical values, percentages, dates and customer-stated expectations into "
          "vague summaries.", "guide", "TS 5.1 · Knowledge 1 · pp.19–20"),
    Claim("Extract transactional facts (amounts, dates, order numbers, statuses) into a persistent case-facts block included in "
          "each prompt, outside summarised history.", "guide", "TS 5.1 · Skill 1 · pp.19–20"),
    Claim("For multi-issue sessions, extract and persist structured issue data (order IDs, amounts, statuses) into a separate "
          "context layer.", "guide", "TS 5.1 · Skill 2 · pp.19–20"),
    Claim("Use structured formats such as JSON for state data (like test results or task status), and unstructured text for "
          "general progress notes.", "docs", "prompting best practices § State management best practices"),
    Claim("Compaction replaces older turns with a summary; if the default summary drops something a later turn needs, you can "
          "write your own summarisation prompt.", "docs", "compaction overview"),
    Claim("Keeping the block current (overwriting a status when it changes) and including customer-stated expectations are this "
          "page's reading of TS 5.1 K1/S1 (statuses; customer-stated expectations).", "recommendation", "TS 5.1 · Knowledge 1, Skill 1"),
    Claim("The events, the summariser, the prose-note writer and the agent's replies are invented to make the effects repeatable; "
          "facts arrive pre-extracted so the lab is about the block, not extraction.", "simulated", "utils/casefacts_lab.py"),
)

CORRECT = r'''import json
from utils.casefacts_lab import SCENARIO, prose_note, run_session   # SIMULATED support session


def update_facts(facts, event):
    for f in event["facts"]:                  # amounts, IDs, dates, statuses AND what the customer said they need
        facts.setdefault(f["issue"], {})[f["field"]] = f["value"]   # one record per issue; the newest value wins
    return facts


def build_prompt(facts, summary, recent):
    block = {"role": "system", "content": "CASE FACTS (current, verbatim)\n" + json.dumps(facts, ensure_ascii=False)}
    return [block] + summary + recent         # in EVERY prompt, outside the summarised history


run_session(update_facts, build_prompt)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


_RET = '''    return [block] + summary + recent         # in EVERY prompt, outside the summarised history'''
_SET = '''        facts.setdefault(f["issue"], {})[f["field"]] = f["value"]   # one record per issue; the newest value wins'''
# ⭐ TS 5.1 · Skill 1 / Knowledge 1 — no block: rely on the summarised history
VARIANT_A = _swap(CORRECT, _RET, '''    return summary + recent                   # WRONG: the facts live only in the (summarised) history''')
# 📘 docs — the block written as prose
VARIANT_B = _swap(CORRECT, '''    block = {"role": "system", "content": "CASE FACTS (current, verbatim)\\n" + json.dumps(facts, ensure_ascii=False)}''',
                  '''    block = {"role": "system", "content": "CASE FACTS\\n" + prose_note(facts)}   # WRONG: a friendly sentence, not data''')
# ⭐ TS 5.1 · Skill 2 — one flat block for every issue
VARIANT_C = _swap(CORRECT, _SET, '''        facts[f["field"]] = f["value"]        # WRONG: one flat record - each order overwrites the last''')
# ⭐ TS 5.1 · Skill 1 (statuses) — facts set once, never updated
VARIANT_D = _swap(CORRECT, _SET, '''        facts.setdefault(f["issue"], {}).setdefault(f["field"], f["value"])   # WRONG: first value kept forever''')
# ⭐ TS 5.1 · Knowledge 1 — customer-stated expectations left out
VARIANT_E = _swap(CORRECT, '''    for f in event["facts"]:                  # amounts, IDs, dates, statuses AND what the customer said they need''',
                  '''    for f in event["facts"]:
        if f["source"] != "tool":             # WRONG: only system data - what the customer said they need is dropped
            continue''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "casefacts_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "run": ev[-1] if ev else None}


def _diagnose(f):
    r, sc = f["run"], f["scenario"]
    if f["raised"]:
        return False, None, f"raised: {f['raised'][:160]}"
    if r is None:
        return False, None, "nothing ran"
    txt = f"case facts: {r['format']} · agent: “{r['reply']}” · missing {r['missing'] or 'nothing'}"
    if r["ok"]:
        return True, None, txt
    if r["format"] == "none":
        return False, "NOBLOCK", txt
    if r["format"] == "prose":
        return False, "PROSE", txt
    if r["format"] == "json-flat":
        return False, "FLAT", txt
    if sc == "status_change":
        return False, "STALE", txt
    return False, "NOEXPECT", txt   # a structured per-issue block that lacks what the customer said (deadline, need)


EXPECTED = {
    "refund_promise": "the reply repeats £84.20 and Friday 14 March exactly",
    "multi_issue": "the lamp's own facts: £45.00, replacement shipped",
    "status_change": "the refund is reported as approved (the latest status)",
    "customer_expectation": "express replacement before the wedding on Saturday 5 April",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "cap":  ("#FEF3C7", "#D97706", "what goes into the block"),
    "shape": ("#DBEAFE", "#0066CC", "how the block is shaped"),
    "use":  ("#CCFBF1", "#0D9488", "where it goes"),
    "out":  ("#EDE9FE", "#7C3AED", "result"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "CAP":    ("⭐ Capture amounts, IDs, dates,\\nstatuses + customer expectations", "box", "cap"),
    "UPD":    ("⭐ Update when a status\\nchanges (newest wins)", "box", "cap"),
    "ISSUE":  ("⭐ One record per issue\\n(separate layer)", "box", "shape"),
    "JSON":   ("Structured (JSON),\\nnot prose (docs)", "box", "shape"),
    "EVERY":  ("⭐ In every prompt, outside\\nthe summarised history", "box", "use"),
    "OUT":    ("Exact answers after\\nthe history is summarised", "box", "out"),
    "NOBLOCK": ("✗ facts only in the\\nsummarised history", "box", "bug"),
    "PROSE":   ("✗ block written\\nas prose", "box", "bug"),
    "FLAT":    ("✗ one flat block\\nfor all issues", "box", "bug"),
    "STALE":   ("✗ set once,\\nnever updated", "box", "bug"),
    "NOEXPECT": ("✗ customer expectations\\nleft out", "box", "bug"),
}
_BUGS = ["NOBLOCK", "PROSE", "FLAT", "STALE", "NOEXPECT"]
_EXP = {"refund_promise": ["CAP", "JSON", "EVERY"], "multi_issue": ["ISSUE", "EVERY"], "status_change": ["UPD", "EVERY"],
        "customer_expectation": ["CAP", "EVERY"]}


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
    lines += ["  CAP -> UPD -> ISSUE -> JSON -> EVERY -> OUT;",
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  OUT -> NOBLOCK [style=invis];", _key(hl),
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
    ExamPoint("5.1", "K", 1, "Progressive summarisation turns numbers, percentages, dates and customer-stated expectations into "
              "vague summaries.", "✅ refund_promise, customer_expectation · ❌ A, E"),
    ExamPoint("5.1", "S", 1, "Extract transactional facts (amounts, dates, order numbers, statuses) into a persistent case-facts "
              "block included in each prompt, outside summarised history.", "✅ build_prompt · ❌ A, D"),
    ExamPoint("5.1", "S", 2, "For multi-issue sessions, persist structured issue data (order IDs, amounts, statuses) in a separate "
              "context layer.", "✅ multi_issue · ❌ C"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ structured, per issue, kept current, with customer expectations, in every prompt", "correct", CORRECT,
            "refund_promise",
            observe=("refund_promise: “You're getting £84.20 back, marked urgent for Friday 14 March.” multi_issue: “For the "
                     "lamp: £45.00, replacement shipped.” status_change: “Your £199.00 refund is approved.” "
                     "customer_expectation: an express replacement before the wedding on Saturday 5 April. All of this after "
                     "every older turn was summarised to a vague sentence."),
            why="The facts live in their own structured layer that's rebuilt into every prompt, so summarising the history can't blur them."),
    Variant("A", "⭐❌ A — no block: facts only in the summarised history", "distractor", VARIANT_A, "refund_promise",
            observe="“Your refund is on its way and should arrive soon.” The amount and date were summarised away.",
            why="Progressive summarisation keeps the gist and drops numbers, dates and promises.",
            fix="Keep a case-facts block in every prompt, outside the summarised history.", source="guide:5.1:S1"),
    Variant("B", "❌ B — the block written as prose", "distractor", VARIANT_B, "refund_promise",
            observe="The block says the customer “is owed some money back soon”, and the reply is just as vague.",
            why="The docs: use structured formats (JSON) for state data; free text is for progress notes.",
            fix="Store the facts as structured data.", source="docs"),
    Variant("C", "⭐❌ C — one flat block for every issue", "distractor", VARIANT_C, "multi_issue",
            observe="“For the lamp: £9.99, refund approved” — the mug's values overwrote the lamp's.",
            why="Multi-issue sessions need structured data per issue, in a separate context layer.",
            fix="Key the block by order id.", source="guide:5.1:S2"),
    Variant("D", "⭐❌ D — facts set once, never updated", "distractor", VARIANT_D, "status_change",
            observe="“Your £199.00 refund is pending review” — although a later lookup said approved.",
            why="Statuses are case facts too; the block must reflect the latest value, or it confidently repeats stale data.",
            fix="Overwrite a field when a newer value arrives.", source="guide:5.1:S1"),
    Variant("E", "⭐❌ E — customer-stated expectations left out", "distractor", VARIANT_E, "customer_expectation",
            observe="“A replacement will arrive in 5–7 working days” — after the customer said the wedding is on Saturday 5 April.",
            why="The guide names customer-stated expectations among the facts summaries lose. Tool data alone misses them.",
            fix="Capture what the customer says they need, not only what tools return.", source="guide:5.1:K1"),
)

TLDR = (
    "Long conversations get summarised, and **summaries blur the facts that matter**: amounts, dates, order numbers, statuses, "
    "and what the customer said they need (guide TS 5.1). A **case-facts block** keeps them exact. For it to work, the block "
    "must be:\n\n"
    "- **Outside the summarised history**, rebuilt into **every** prompt.\n"
    "- **Structured** (JSON), not a friendly paragraph (docs: structured formats for state data).\n"
    "- **One record per issue** when the customer raises several (TS 5.1 Skill 2).\n"
    "- **Kept current**: a new status overwrites the old one.\n"
    "- **Complete**: it holds what the customer said (“before my wedding on Saturday”), not just what the tools returned."
)
MENTAL_MODEL = ("The summary is the story of the call. The case-facts block is the receipt stapled to the front of the file. "
                "Stories get retold vaguely; receipts don't. Keep one receipt per order, cross out the old status when it "
                "changes, and write down what the customer asked for — not just what the till printed.")

WHAT_IT_IS = """
**In the guide.** TS 5.1 (pp.19–20): Knowledge 1 (what summaries lose), Skill 1 (the block) and Skill 2 (a per-issue layer).
The docs' state-management advice adds: structured formats for state, free text for notes.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | Reference |
|---|---|---|---|
| 1 | What summaries lose | Stories get retold vaguely; the numbers go first. | ⭐ TS 5.1 · Knowledge 1 |
| 2 | Block outside the summarised history | The receipt is stapled to the front of the file, not folded into the story. | ⭐ TS 5.1 · Skill 1 |
| 3 | In every prompt | The model only sees today's desk; staple the receipt on every time. | ⭐ TS 5.1 · Skill 1 (“included in each prompt”) |
| 4 | Structured, not prose | A receipt has fields; a note says “about eighty quid, soon”. | 📘 docs (state management) |
| 5 | One record per issue | One receipt per order, or the last one overwrites the rest. | ⭐ TS 5.1 · Skill 2 |
| 6 | Kept current | Cross out the old status; don't keep the first one forever. | ⭐ TS 5.1 · Skill 1 (statuses) |
| 7 | Customer-stated expectations | Write down what they asked for, not only what the till printed. | ⭐ TS 5.1 · Knowledge 1 |

**What goes in the block**

| # | Fact | Example | Source |
|---|---|---|---|
| 1 | Amounts | £84.20 | Tool result |
| 2 | Order / case IDs | ORD-5512 | Customer or tool |
| 3 | Dates and deadlines | Friday 14 March | Customer |
| 4 | Statuses | refund approved | Tool result, updated as it changes |
| 5 | Customer-stated expectations | “before my wedding on Saturday 5 April” | Customer |
| 6 | Chit-chat, repeated explanations | — | Leave it to the summary |

**Block vs summary**

| # | Aspect | Summarised history | Case-facts block |
|---|---|---|---|
| 1 | Purpose | The story so far | The exact facts |
| 2 | Format | Prose | Structured (JSON) |
| 3 | Updated by | Re-summarising (loses detail) | Overwriting fields with newer values |
| 4 | Multi-issue | Blended together | One record per issue |
| 5 | Survives compaction | As a vague sentence | Word for word (rebuilt each prompt) |
"""

HOW_IT_WORKS = """
1. After every customer message and tool result, **update the block**: set each fact on its issue's record, and let a newer
   value replace an older one.
2. Build every prompt as **block + summary + recent turns**. The block is never itself summarised.
3. Keep it **structured**, and **per issue**, and include what the customer said they need.
"""

WHERE_SEEN = """
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): long, multi-issue conversations with refunds,
  statuses and promises.
- Any long agent task whose state must survive summarisation or compaction (docs: state management across context windows).
"""

GUIDE_NOTE = ("Grounded in the exam guide TS 5.1 (pp.19–20) and the platform prompting best practices (State management), "
              "Context windows and Compaction pages (verified 2026-09-28). Section layout inspired by a community concept list "
              "(claudearchitectcertification.com — community source, unverified; no text copied).")

LAB_INTRO = """
A **simulated** support session. Every event (customer message or tool result) arrives with its facts already picked out. You
write `update_facts` (how the block changes) and `build_prompt` (what the model sees). Before the customer's final question,
every event except the last two is summarised into one vague sentence, as long conversations are. Four scenarios:

- a refund promise;
- three orders at once;
- a status that changes;
- a customer with a hard deadline.
"""

DISTRACTORS = (
    ("A · No block", "The summary covers it.", "Amount and date blurred away.", "A block in every prompt, outside the summary.", "guide:5.1:S1"),
    ("B · Block as prose", "Readable notes.", "“Some money back soon.”", "Structured data (JSON).", "docs"),
    ("C · One flat block", "Simpler.", "The mug overwrote the lamp.", "One record per issue.", "guide:5.1:S2"),
    ("D · Set once", "Facts don't change.", "Stale “pending review”.", "Newest value wins.", "guide:5.1:S1"),
    ("E · Tool data only", "Tools are the source of truth.", "Missed the wedding date.", "Capture customer-stated expectations.", "guide:5.1:K1"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Question at the end", "Without a proper block", "With the block")
SIDE_BY_SIDE_ROWS = (
    ("1", "How much, and by when?", "“On its way, soon”", "£84.20, urgent for Friday 14 March"),
    ("2", "What about the lamp?", "£9.99, refund approved (the mug's)", "£45.00, replacement shipped"),
    ("3", "Approved yet?", "Pending review (stale)", "Approved"),
    ("4", "What will you do about my suit?", "5–7 working days", "Express, before Saturday 5 April"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="Will a later turn need\\nthis exact value?"];
  SUM [shape=box, label="Leave it to\\nthe summary"];
  Q2 [shape=diamond, label="Several issues\\nin the session?"];
  PER [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Record under its\\nissue (order id)"];
  ONE [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Record in the\\ncase's block"];
  EVERY [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Rebuild into every prompt;\\nnewer value overwrites"];
  Q1 -> SUM [label="no"]; Q1 -> Q2 [label="yes (amount, ID,\\ndate, status, promise)"];
  Q2 -> PER [label="yes"]; Q2 -> ONE [label="no"]; PER -> EVERY; ONE -> EVERY;
}''')

EXPERIMENTS = (
    "Run ✅ on all four scenarios.",
    "Run ⭐❌ C on multi_issue and look at the flat block the model received.",
    "In ✅, change update_facts to skip fields whose source is “customer”: which scenarios break?",
    "In the playground's updates tab, switch to “set once” and ask “Has my refund been approved yet?”.",
)

QUESTIONS = (
    Question(
        q=("A support agent summarises the conversation every ten turns. Early on, a customer explained they're moving house "
           "and need the replacement delivered before 3 June. Later, the agent books standard delivery for 8 June. Order "
           "numbers and amounts are handled correctly. What's the most effective fix?"),
        opts=("Summarise less often, so the detail survives longer.",
              "Include customer-stated expectations, such as deadlines, in the persistent case-facts block alongside amounts and IDs.",
              "Tell the agent to always offer express delivery.",
              "Ask the customer to restate their deadline before each booking."),
        ans=1,
        explain=("Summaries blur customer-stated expectations as well as numbers and dates. The block must hold what the "
                 "customer said they need, not only tool data. Always offering express ignores the real requirement."),
        scenarios=(1,), points=("5.1:K1", "5.1:S1"),
    ),
    Question(
        q=("A customer raises a billing dispute and two returns in one conversation. The agent keeps one facts record, and by "
           "the end it quotes the second return's refund amount for the billing dispute. What design keeps the issues apart?"),
        opts=("Handle each issue in a separate conversation.",
              "Summarise after each issue is resolved.",
              "Put the latest amount at the top of the prompt.",
              "Keep structured data for each issue, keyed by its order or case id, in a separate context layer."),
        ans=3,
        explain=("For multi-issue sessions, persist structured issue data in a separate context layer, so each issue's "
                 "amounts and statuses stay attached to it. A single record means the latest write wins."),
        scenarios=(1,), points=("5.1:S2",),
    ),
    Question(
        q=("A team adds a “case facts” message at the start of each support conversation. Once the conversation is long enough "
           "to be summarised, the agent starts giving vague answers about amounts again. What's wrong with the design?"),
        opts=("The block is part of the history being summarised; it must sit outside it and be included in every prompt.",
              "The block should go at the end of the conversation instead.",
              "The block needs more detail.",
              "Summarisation should be turned off."),
        ans=0,
        explain=("The case-facts block works because it lives outside the summarised history and is included in each "
                 "prompt. Put it inside the history and it gets summarised like everything else."),
        scenarios=(1,), points=("5.1:S1",),
    ),
    Question(
        q=("An agent records a refund as “pending” in its case-facts block. Twenty minutes later a lookup shows the refund "
           "approved, but the agent keeps telling the customer it's pending. What should change?"),
        opts=("Re-run the lookup before every reply.",
              "Remove statuses from the block, since they change.",
              "Update the block whenever a newer value arrives from a tool result, so it always shows the current status.",
              "Ask the customer to check their bank instead."),
        ans=2,
        explain=("Statuses are among the transactional facts the block carries. It must reflect the latest value, or the agent "
                 "repeats stale data confidently. Dropping statuses loses them to the summary."),
        scenarios=(1,), points=("5.1:S1",),
    ),
    Question(
        q=("An agent maintains its case state as a paragraph it writes itself (“customer owed about £80, wants it soon”). "
           "Values drift as the paragraph is rewritten. What does the docs' state-management advice suggest?"),
        opts=("Rewrite the paragraph less often.",
              "Keep state data in a structured format such as JSON, and use free text only for general progress notes.",
              "Ask the model to be more precise in the paragraph.",
              "Store the state in the system prompt as prose."),
        ans=1,
        explain=("Per the prompting docs, structured formats suit state data (status, values). Unstructured text is fine for "
                 "progress notes, not for facts that must stay exact."),
        scenarios=(1,), basis="docs", in_bank=False,
    ),
    Question(
        q=("A support platform switches on automatic compaction for long conversations. The default summary drops the "
           "“promised by Friday” commitments customers were given. Besides a case-facts block, what does the compaction "
           "documentation offer?"),
        opts=("Nothing; the summary format is fixed.",
              "Turning off compaction permanently.",
              "Writing your own summarisation prompt, so the summary keeps what later turns need.",
              "Compacting more often."),
        ans=2,
        explain=("Per the compaction docs, if the default summary drops something a later turn needs, you can provide your "
                 "own summarisation prompt. A case-facts block remains the guide's answer for exact values."),
        scenarios=(1,), basis="docs", in_bank=False,
    ),
)

FAQ = (
    ("How is this different from D4.7's case-facts tab?",
     "D4.7 shows that a block helps, next to other layout techniques. This page is about building the block properly: where it "
     "lives, its format, one record per issue, keeping it current, and capturing what the customer said."),
    ("Where does the block go — system prompt or a message?",
     "Anywhere that's rebuilt into every request and never summarised. The lab puts it first, as a system-style message. The "
     "guide's requirement is “included in each prompt, outside summarised history”."),
    ("Doesn't compaction make this unnecessary?",
     "No. Compaction is summarisation, and summaries are exactly what blur numbers, dates and promises. The block rides alongside "
     "whatever summary you use."),
)

PLAYGROUND_INTRO = """
Each tab plays the scenario for one sub-concept. The message box replaces the customer's final question; the **simulated** agent
answers that scenario's question whatever the wording. Change how the block is built and watch the reply.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="casefacts")


PLAYGROUND = (
    _tab("block", "⭐ The block itself", "block", "A receipt stapled to the front of the file.", "guide:5.1:S1",
         "A refund promise, then chit-chat that gets summarised.", "guide TS 5.1 K1, S1; docs § State management",
         ("cf_block", "cf_format"), {"cf_block": "every_prompt", "cf_format": "json"},
         ("Sorry - can you confirm how much I'm getting back and by when?",),
         ("no block: “on its way, soon”.", "prose: just as vague.")),
    _tab("issues", "⭐ One record per issue", "issues", "One receipt per order.", "guide:5.1:S2",
         "Three orders in one conversation.", "guide TS 5.1 S2", ("cf_per_issue",), {"cf_per_issue": "yes"},
         ("What's happening with the lamp?",), ("flat: the lamp gets the mug's £9.99.",)),
    _tab("updates", "⭐ Keep it current", "updates", "Cross out the old status.", "guide:5.1:S1",
         "A refund goes from pending review to approved mid-conversation.", "guide TS 5.1 S1", ("cf_updates",), {"cf_updates": "overwrite"},
         ("Has my refund been approved yet?",), ("set once: still “pending review”.",)),
    _tab("expect", "⭐ Customer expectations", "expect", "Write down what they asked for.", "guide:5.1:K1",
         "A torn suit and a wedding on Saturday 5 April.", "guide TS 5.1 K1", ("cf_customer",), {"cf_customer": "yes"},
         ("So what will you do about my suit?",), ("tools only: 5–7 working days, after the wedding.",)),
)

CONTENT = ConceptContent(
    slug="case-facts-block", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("context-window", "attention-engineering", "escalation"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("refund_promise", "multi_issue", "status_change", "customer_expectation"), show_ledger=False,
)
