"""
D5.1 Context Window Management — the context window as a budget you manage: the API is stateless, so every request carries
the whole conversation; verbose exploration belongs in a subagent's own window; when a session fills up, compact with a focus
and keep persistent rules in CLAUDE.md (early instructions can be lost in compaction); and upstream agents hand a limited
downstream agent structured facts, not reasoning chains. Guide TS 5.1 (pp.19–20) + TS 5.4 (pp.21–22).
D4.7 covers layout and trimming; D5.2 covers the case-facts block; D1.4/D3.4 cover resume, fork, scratchpads and checkpoints.

GROUNDING (CLAUDE.md, user rules): guide read from the PDF (2026-09-28); the platform "Context windows", "Context editing" and
"Compaction" pages and the Claude Code "How Claude Code works" page fetched 2026-09-28 (DOC_REFS). Every claim is in GROUNDING
with its source type. Paraphrased; no real exam question.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable

DOCS_VERIFIED_ON = "2026-09-28"
_P = "https://platform.claude.com/docs/en"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Context windows — how it works, overflow behaviour, compaction", f"{_P}/build-with-claude/context-windows"),
    DocRef("Context editing — tool result clearing", f"{_P}/build-with-claude/context-editing"),
    DocRef("Compaction overview", f"{_P}/build-with-claude/compaction"),
    DocRef("How Claude Code works — The context window; When context fills up; skills and subagents", f"{_C}/how-claude-code-works"),
)

GROUNDING = (
    Claim("Everything in the request counts toward the context window: system prompt, every message (including tool results, "
          "images, documents) and tool definitions, plus the output Claude generates.", "docs", "context-windows § How the context window works"),
    Claim("Each turn's input is all previous conversation history plus the current user message; previous turns are preserved "
          "completely as the conversation accumulates.", "docs", "context-windows § How the context window works"),
    Claim("More context isn't automatically better: as token count grows, accuracy and recall degrade (“context rot”), so "
          "curating what's in context matters as much as the space available.", "docs", "context-windows § How the context window works"),
    Claim("If the input alone exceeds the context window, the API returns a 400 invalid_request_error (“prompt is too long”); "
          "if generation reaches the limit on newer models, the stop reason is model_context_window_exceeded.", "docs",
          "context-windows § Context window overflow behavior"),
    Claim("For conversations that regularly approach the limit, server-side compaction summarises earlier turns; context editing "
          "can clear old tool results (beta).", "docs", "context-windows § Manage context with compaction; context-editing"),
    Claim("In Claude Code, context fills with conversation, file contents, command outputs, CLAUDE.md, skills and system "
          "instructions; it compacts automatically; requests and key code are kept but detailed early instructions may be lost, so "
          "put persistent rules in CLAUDE.md; /compact accepts a focus; /context shows what uses space.", "docs",
          "how-claude-code-works § The context window / When context fills up"),
    Claim("Subagents work in their own context window; their tool calls stay out of the main context and a summary comes back.",
          "docs", "how-claude-code-works § Manage context with skills and subagents"),
    Claim("Pass complete conversation history in subsequent API requests to keep the conversation coherent.", "guide", "TS 5.1 · Knowledge 4 · pp.19–20"),
    Claim("Tool results accumulate and consume tokens out of proportion to their relevance.", "guide", "TS 5.1 · Knowledge 3 · pp.19–20"),
    Claim("Upstream agents should return structured data (key facts, citations, relevance scores) instead of verbose content and "
          "reasoning chains when downstream agents have limited context budgets.", "guide", "TS 5.1 · Skill 6 · pp.19–20"),
    Claim("Context degradation in long sessions; subagents isolate verbose exploration while the main agent coordinates; /compact "
          "reduces context usage when verbose discovery output fills it.", "guide", "TS 5.4 · Knowledge 1, 3 · Skills 1, 5 · pp.21–22"),
    Claim("Token counts, the 20,000-token window, which instruction counts as an “early detailed instruction”, and the model's "
          "replies are invented to make the effects repeatable.", "simulated", "utils/ctxwin_lab.py"),
)

CORRECT = r'''from utils.ctxwin_lab import (SCENARIO, CHAT_TURNS, FILES, QUESTION, analyses, answer, chat, read, report,
                               session, spawn_explorer)   # SIMULATED context window

if SCENARIO == "stateless_history":
    history = []
    for user_msg in CHAT_TURNS:
        history.append({"role": "user", "content": user_msg})
        reply = chat(history)                    # the API is stateless: send the WHOLE conversation every time
        history.append({"role": "assistant", "content": reply})

elif SCENARIO == "exploration":
    summary = spawn_explorer(QUESTION)           # 30 files of reading happen in the subagent's own window

elif SCENARIO == "long_session":
    s = session(claude_md=["Never edit files under migrations/"])   # persistent rule: reloaded every time
    s.work(until_percent=95)
    s.compact(focus="the webhook retry change and what we found")   # summarise, keep the task and findings
    s.work_more()

else:  # downstream_budget
    results = [run(structured=True) for run in analyses()]   # key facts + citations + relevance, not reasoning chains
    report(results)
'''


def _swap(code, old, new):
    assert old in code, f"lab code changed: {old[:60]!r}"
    return code.replace(old, new, 1)


# ⭐ TS 5.1 · Knowledge 4 — only the newest message is sent
VARIANT_A = _swap(CORRECT, '''        reply = chat(history)                    # the API is stateless: send the WHOLE conversation every time''',
                  '''        reply = chat([{"role": "user", "content": user_msg}])   # WRONG: "save tokens" - send only the newest message''')
# ⭐ TS 5.4 · Knowledge 3 / Skill 1 — explore in the main context
VARIANT_B = _swap(CORRECT, '''    summary = spawn_explorer(QUESTION)           # 30 files of reading happen in the subagent's own window''',
                  '''    for path in FILES:                           # WRONG: read everything into the main conversation
        read(path)
    answer(QUESTION)''')
# ⭐ TS 5.4 · Skill 5 — /clear instead of /compact
VARIANT_C = _swap(CORRECT, '''    s.compact(focus="the webhook retry change and what we found")   # summarise, keep the task and findings''',
                  '''    s.clear()                                    # WRONG: frees the space by throwing away the task and findings''')
# 📘 docs — a persistent rule given only in the conversation
VARIANT_D = _swap(CORRECT, '''    s = session(claude_md=["Never edit files under migrations/"])   # persistent rule: reloaded every time''',
                  '''    s = session()
    s.say("By the way, never edit files under migrations/")        # WRONG: a persistent rule said once, early on''')
# ⭐ TS 5.1 · Skill 6 — verbose upstream output to a limited downstream agent
VARIANT_E = _swap(CORRECT, '''    results = [run(structured=True) for run in analyses()]   # key facts + citations + relevance, not reasoning chains''',
                  '''    results = [run(structured=False) for run in analyses()]  # WRONG: full reasoning chains, 3,000 tokens each''')

# ── Check and chart ────────────────────────────────────────────────────────────


def _facts(trace):
    ev = [e for e in trace["events"] if e["kind"] == "ctxwin_run"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "runs": ev}


def _diagnose(f):
    runs, sc = f["runs"], f["scenario"]
    if not runs:
        return False, None, f"raised: {f['raised'][:160]}" if f["raised"] else "nothing ran"
    r = runs[-1]
    if r["task"] == "chat":
        txt = " · ".join(f"call {i + 1}: {x['sent']} msg → {x['reply']}" for i, x in enumerate(runs))
        ok = "refunded the blender on ORD-4410" in r["reply"]
        return ok, (None if ok else "STATELESS"), txt
    if r["task"] == "explore":
        if r["overflow"]:
            return False, "OVERFLOW", f"main context {r['main_tokens']:,} tokens after {r['reads']} reads → 400 prompt is too long (SIMULATED)"
        txt = f"{r['mode']} · main context {r['main_tokens']:,} tokens · answer: {r['answer']}"
        ok = r["mode"] == "subagent" and "retry_policy.py" in (r["answer"] or "")
        return ok, (None if ok else "OVERFLOW"), txt
    if r["task"] == "session":
        txt = (" → ".join(r["events"]) + f" · knows task {r['knows_task']} · findings {r['knows_finding']} · "
               f"migrations rule active {r['rule_active']} · edited {r['edits'] or 'nothing'}")
        if not r["knows_task"] or not r["knows_finding"]:
            return False, "CLEARED", txt
        if "migrations/0042_retry_columns.py" in r["edits"]:
            return False, "RULELOST", txt
        return True, None, txt
    txt = f"report input {r['used']:,}/{r['budget']:,} · included {r['included']} · dropped {r['dropped'] or 'none'}"
    ok = not r["dropped"] and r["cited"]
    return ok, (None if ok else "VERBOSE"), txt


EXPECTED = {
    "stateless_history": "the third reply refunds the blender on ORD-4410 without asking again",
    "exploration": "the answer names retry_policy.py and the main context stays far below the window",
    "long_session": "after the context fills, the agent still knows the task and findings and leaves migrations/ alone",
    "downstream_budget": "all four analyses fit the report agent's budget, with citations",
}


def check_outcome(scenario, trace):
    ok, _b, txt = _diagnose(_facts(trace))
    return ok, EXPECTED[scenario], txt


_CONCEPT = {
    "api":  ("#DBEAFE", "#0066CC", "what each request carries"),
    "iso":  ("#CCFBF1", "#0D9488", "keeping bulk out of the main window"),
    "full": ("#FEF3C7", "#D97706", "when the window fills"),
    "out":  ("#EDE9FE", "#7C3AED", "result"),
    "bug":  ("#FFFFFF", "#DC2626", "bug (a distractor)"),
}
_NODES = {
    "HIST":   ("⭐ Send the whole conversation\\nevery request (stateless API)", "box", "api"),
    "SUB":    ("⭐ Verbose exploration in a\\nsubagent's own window", "box", "iso"),
    "STRUCT": ("⭐ Upstream returns structured\\nfacts + citations", "box", "iso"),
    "RULES":  ("Persistent rules in CLAUDE.md\\n(reloaded after compaction)", "box", "full"),
    "COMPACT": ("⭐ /compact with a focus\\nwhen the window fills", "box", "full"),
    "OUT":    ("The right facts fit\\nin the window", "box", "out"),
    "STATELESS": ("✗ only the newest\\nmessage sent", "box", "bug"),
    "OVERFLOW":  ("✗ 30 files read into\\nthe main context", "box", "bug"),
    "CLEARED":   ("✗ /clear throws the\\ntask away", "box", "bug"),
    "RULELOST":  ("✗ rule said once, lost\\nat compaction", "box", "bug"),
    "VERBOSE":   ("✗ reasoning chains sent\\ndownstream", "box", "bug"),
}
_BUGS = ["STATELESS", "OVERFLOW", "CLEARED", "RULELOST", "VERBOSE"]
_EXP = {"stateless_history": ["HIST"], "exploration": ["SUB"], "long_session": ["RULES", "COMPACT"],
        "downstream_budget": ["STRUCT"]}


def _key(hl):
    rows = "".join(f'<TR><TD BGCOLOR="{f}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD><TD ALIGN="LEFT" BORDER="0"><FONT '
                   f'POINT-SIZE="10">{t}</FONT></TD></TR>' for f, _l, t in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">named by '
             'the exam guide (TS 5.1, 5.4)</FONT></TD></TR>')
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
    lines += ["  HIST -> SUB -> STRUCT -> OUT; RULES -> COMPACT -> OUT; { rank=same; SUB; RULES; }",
              "  { rank=same; " + "; ".join(_BUGS) + "; }", "  OUT -> STATELESS [style=invis];", _key(hl),
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
    ExamPoint("5.1", "K", 3, "Tool results accumulate in context and use tokens out of proportion to their relevance.",
              "✅ exploration (reads stay in the subagent) · ❌ B"),
    ExamPoint("5.1", "K", 4, "Pass the complete conversation history in each API request to keep the conversation coherent.",
              "✅ stateless_history · ❌ A"),
    ExamPoint("5.1", "S", 6, "Have upstream agents return structured data (key facts, citations, relevance scores) instead of "
              "verbose content and reasoning chains when downstream agents have limited context budgets.", "✅ downstream_budget · ❌ E"),
    ExamPoint("5.4", "K", 1, "Context degradation in long sessions: answers become inconsistent and generic.", "✅ long_session (context at 95%)"),
    ExamPoint("5.4", "K", 3, "Subagents isolate verbose exploration output while the main agent keeps the high-level picture.",
              "✅ spawn_explorer · ❌ B"),
    ExamPoint("5.4", "S", 1, "Spawn subagents for specific investigation questions while the main agent coordinates.", "✅ exploration · playground tab 2"),
    ExamPoint("5.4", "S", 5, "Use /compact to reduce context usage when verbose discovery output fills the context.", "✅ long_session · ❌ C"),
)

VARIANTS = (
    Variant("correct", "✅ ⭐ full history · explore in a subagent · CLAUDE.md + /compact · structured upstream", "correct", CORRECT,
            "stateless_history",
            observe=("stateless_history: calls carry 1, 3 and 5 messages; the third reply refunds the blender on ORD-4410. "
                     "exploration: the subagent reads 5 files in its own window; the main context stays at 1,800 tokens. "
                     "long_session: at 95% the session compacts to 4,000 tokens, keeps the task and findings, and leaves "
                     "migrations/ alone. downstream_budget: four structured analyses use 1,600 of 6,000 tokens."),
            why="Each request carries what the model needs, and bulk stays out of the windows that can't afford it."),
    Variant("A", "⭐❌ A — send only the newest message", "distractor", VARIANT_A, "stateless_history",
            observe="Every call carries 1 message; by the third, the model asks again for the order number and item.",
            why="The API is stateless: each request is all the model sees, so earlier turns must be sent again.",
            fix="Send the whole conversation (compact it when it grows).", source="guide:5.1:K4"),
    Variant("B", "⭐❌ B — read 30 files into the main context", "distractor", VARIANT_B, "exploration",
            observe="After 21 reads the main context is 20,400 tokens → SIMULATED 400 “prompt is too long”.",
            why="Verbose exploration output fills the main window. A subagent explores in its own window and returns a summary.",
            fix="Delegate the exploration to a subagent.", source="guide:5.4:K3"),
    Variant("C", "⭐❌ C — /clear when the context fills", "distractor", VARIANT_C, "long_session",
            observe="After /clear the agent knows neither the task nor the findings, and asks what to work on.",
            why="/clear starts from nothing. /compact summarises and keeps the requests and key findings.",
            fix="/compact, with a focus.", source="guide:5.4:S5"),
    Variant("D", "❌ D — a persistent rule said once in the conversation", "distractor", VARIANT_D, "long_session",
            observe="After compaction the “never edit migrations/” instruction is gone, and migrations/0042_retry_columns.py gets edited.",
            why="The docs: detailed early instructions may be lost when context is compacted, so put persistent rules in CLAUDE.md.",
            fix="Put the rule in CLAUDE.md.", source="docs"),
    Variant("E", "⭐❌ E — full reasoning chains sent downstream", "distractor", VARIANT_E, "downstream_budget",
            observe="Two 3,000-token analyses fill the 6,000-token budget; supply and competition are dropped.",
            why="A downstream agent with a limited budget needs key facts, citations and relevance, not the upstream reasoning.",
            fix="Return structured data from each analysis.", source="guide:5.1:S6"),
)

TLDR = (
    "The context window is a **budget**. Everything in the request counts: system prompt, every message including tool results, "
    "tool definitions, and the output. And **more isn't better**: accuracy and recall degrade as it grows (the docs call this "
    "“context rot”). Four habits keep it under control:\n\n"
    "- **The API is stateless.** Send the whole conversation every time (TS 5.1).\n"
    "- **Keep bulk out of the main window.** Verbose exploration goes to a **subagent**, which returns a summary (TS 5.4).\n"
    "- **When it fills, compact; don't clear.** Put rules that must survive in **CLAUDE.md**, because early instructions can be "
    "lost in compaction (docs).\n"
    "- **Feed limited agents structured facts.** Upstream agents send key facts, citations and relevance, not reasoning chains "
    "(TS 5.1)."
)
MENTAL_MODEL = ("The context window is a desk, not a filing cabinet. The model sees only what's on the desk right now, and you "
                "have to put it there every time. A cluttered desk hides the important page. Clear it by filing summaries, not "
                "by sweeping everything onto the floor. Pin the house rules to the wall (CLAUDE.md) so tidying the desk never "
                "removes them.")

WHAT_IT_IS = """
**In the guide.** TS 5.1 (pp.19–20) covers full history, tool-result growth and structured upstream output. TS 5.4
(pp.21–22) covers degradation, subagent isolation and /compact. The docs add what counts toward the window, overflow
behaviour, compaction and context editing.

**Sub-concepts — each with its picture to remember**

| # | Sub-concept | 🧭 Mental model | Reference |
|---|---|---|---|
| 1 | Stateless API: send the whole history | The model has no memory between calls; the desk is cleared after every request. | ⭐ TS 5.1 · Knowledge 4 |
| 2 | Everything counts toward the window | Tools, system prompt, tool results and output all take desk space. | 📘 docs (context windows) |
| 3 | More context ≠ better (context rot) | A cluttered desk hides the important page. | 📘 docs; ⭐ TS 5.4 · Knowledge 1 |
| 4 | Explore in a subagent | Send an assistant to the library; they bring back one page of notes. | ⭐ TS 5.4 · Knowledge 3, Skill 1 |
| 5 | /compact, not /clear | File a summary of the desk; don't sweep it onto the floor. | ⭐ TS 5.4 · Skill 5 |
| 6 | Persistent rules in CLAUDE.md | House rules pinned to the wall survive every tidy-up. | 📘 docs (How Claude Code works) |
| 7 | Structured upstream output | Hand a busy colleague a one-page brief, not your notebook. | ⭐ TS 5.1 · Skill 6 |
| 8 | Overflow behaviour | Too much input → 400 “prompt is too long”; output hits the limit → model_context_window_exceeded. | 📘 docs |

**What fills the window, and what to do about it**

| # | What fills it | Symptom | Do this |
|---|---|---|---|
| 1 | Earlier turns (needed) | — | Keep sending them. Compact when long. |
| 2 | Bulky tool results | Early details crowded out | Trim tool output (D4.7), or clear old tool results (docs: context editing, beta) |
| 3 | Exploration reads | 400 “prompt is too long” / vague answers | A subagent explores in its own window |
| 4 | Upstream reasoning chains | Later inputs dropped downstream | Structured facts + citations |
| 5 | A very long session | Degradation (TS 5.4 K1) | /compact with a focus; persistent rules in CLAUDE.md |

**Compact vs clear vs fresh start** (Claude Code)

| # | Option | Keeps | Loses | Use when |
|---|---|---|---|---|
| 1 | /compact (with a focus) | Requests, key code and findings (summarised) | Detailed early instructions (docs) | The context is full mid-task |
| 2 | /clear | CLAUDE.md only | The whole conversation | Switching to an unrelated task |
| 3 | New session + structured summary | What you put in the summary | Stale tool results | Earlier results are outdated (D1.4, TS 1.7) |
"""

HOW_IT_WORKS = """
1. **Every API call:** send the full conversation (system prompt, tools, all turns so far). Nothing is remembered between calls.
2. **Big exploration:** hand it to a subagent. Its reads stay in its own window, and only a summary returns.
3. **Long session filling up:** `/compact` with a focus. Anything that must hold for the whole session lives in CLAUDE.md.
4. **Agent-to-agent:** upstream agents return structured key facts, citations and relevance scores that fit the downstream
   budget.
"""

WHERE_SEEN = """
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): multi-turn conversations over a stateless API.
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): upstream agents feeding a synthesis or report agent.
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4) and **Scenario 2 — Code Generation** (p.3): long
  exploration sessions, subagents, /compact.
"""

GUIDE_NOTE = ("Grounded in the exam guide TS 5.1 (pp.19–20) and TS 5.4 (pp.21–22), and in the platform Context windows, "
              "Context editing and Compaction pages and Claude Code's How Claude Code works (verified 2026-09-28). Section "
              "layout inspired by a community concept list (claudearchitectcertification.com — community source, unverified; "
              "no text copied).")

LAB_INTRO = """
A **simulated** context window with a 20,000-token budget. The token numbers are illustrative. Four jobs:

- a three-turn support chat over a stateless API;
- finding a setting in a 30-file codebase;
- a long Claude Code session that fills up;
- four analyses feeding a report agent with a 6,000-token budget.
"""

DISTRACTORS = (
    ("A · Send only the newest message", "Saves tokens.", "The model forgets the order number.", "Send the whole history.", "guide:5.1:K4"),
    ("B · Explore in the main context", "Everything in one place.", "400 “prompt is too long”.", "A subagent explores.", "guide:5.4:K3"),
    ("C · /clear when full", "Frees the most space.", "Task and findings gone.", "/compact with a focus.", "guide:5.4:S5"),
    ("D · Rule said once in chat", "Claude heard it.", "Lost at compaction.", "Put it in CLAUDE.md.", "docs"),
    ("E · Reasoning chains downstream", "More detail helps.", "Later analyses dropped.", "Structured facts + citations.", "guide:5.1:S6"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Situation", "Wastes the window", "Manages the window")
SIDE_BY_SIDE_ROWS = (
    ("1", "Each API call", "Newest message only", "The whole conversation"),
    ("2", "Codebase exploration", "30 reads in the main context", "A subagent's own window + a summary"),
    ("3", "Session at 95%", "/clear", "/compact with a focus"),
    ("4", "A rule for the whole session", "Said once in the chat", "In CLAUDE.md"),
    ("5", "Four analyses → report agent", "Reasoning chains (3,000 tokens each)", "Key facts + citations (400 each)"),
)

DECISION_DOT = readable('''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=12, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];
  Q1 [shape=diamond, label="What's filling\\nthe window?"];
  HIST [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Conversation turns:\\nkeep sending them;\\ncompact when long"];
  SUB [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Exploration reads:\\ndelegate to a subagent"];
  STRUCT [shape=box, fillcolor="#CCFBF1", color="#0D9488", label="Upstream output:\\nstructured facts"];
  COMPACT [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Long session:\\n/compact + CLAUDE.md rules"];
  Q1 -> HIST [label="chat history"]; Q1 -> SUB [label="file reads"];
  Q1 -> STRUCT [label="other agents' results"]; Q1 -> COMPACT [label="everything, mid-task"];
}''')

EXPERIMENTS = (
    "Run ✅ on all four scenarios.",
    "Run ⭐❌ A and compare the message counts per call with ✅'s 1, 3, 5.",
    "In ✅'s long_session, move the migrations rule from claude_md to s.say(...): what gets edited?",
    "In the playground's downstream tab, send verbose output with a 24,000-token budget: everything fits, but what's still missing?",
)

QUESTIONS = (
    Question(
        q=("To save tokens, a support chat built on the Messages API keeps only the last three messages in each request. "
           "Customers complain that the agent asks again for order numbers they gave a few minutes earlier. What's the right "
           "design?"),
        opts=("Keep the sliding window, but tell the model in the system prompt to remember earlier messages.",
              "Increase max_tokens so the model can recall more.",
              "Send the complete conversation history with every request; when it grows long, compact it rather than dropping turns.",
              "Ask customers to repeat key details in every message."),
        ans=2,
        explain=("The API doesn't remember earlier calls, so each request must carry the conversation. Dropping turns loses "
                 "facts. Compaction or a case-facts block (D5.2) keeps a long conversation within budget without losing them."),
        scenarios=(1,), points=("5.1:K4",),
    ),
    Question(
        q=("An onboarding agent answering “how does billing work?” reads file after file of a large legacy repository into "
           "its main conversation. Partway through, requests start failing with “prompt is too long”. What's the best "
           "redesign?"),
        opts=("Delegate the exploration to a subagent that reads in its own context and returns a summary to the main agent.",
              "Switch to a model with a larger context window and keep reading everything.",
              "Retry the failed request with a higher max_tokens.",
              "Stop after the first ten files and answer from those."),
        ans=0,
        explain=("Subagents isolate verbose exploration output while the main agent coordinates. A bigger window only moves "
                 "the limit, and max_tokens controls output length, not input size."),
        scenarios=(4,), points=("5.4:K3", "5.4:S1"),
    ),
    Question(
        q=("Two hours into a refactor in Claude Code, the context is 95% full of search output, and answers are getting "
           "generic. The developer wants to finish the refactor in this session. What should they do?"),
        opts=("Run /clear and describe the refactor again.",
              "Keep going; the answers will recover.",
              "Open a new terminal and start the refactor again.",
              "Run /compact with a focus on the refactor, so the history is summarised and the task and findings carry on."),
        ans=3,
        explain=("/compact reduces context usage when verbose discovery output fills the context, keeping what matters. "
                 "/clear discards the task and findings."),
        scenarios=(2,), points=("5.4:S5", "5.4:K1"),
    ),
    Question(
        q=("A report agent can only fit about 6,000 tokens of input. Four document-analysis subagents each send it 3,000 "
           "tokens of reasoning, quotes and caveats, and reports keep leaving out the last two analyses. What's the most "
           "effective change?"),
        opts=("Give the report agent a larger max_tokens.",
              "Have the analysis subagents return structured data (key facts, citations, relevance scores) instead of their reasoning.",
              "Send the analyses in a different order each time so each gets a turn.",
              "Ask the report agent to skim each analysis faster."),
        ans=1,
        explain=("When downstream agents have limited context budgets, upstream agents should return structured data rather "
                 "than verbose content and reasoning chains. max_tokens is an output limit."),
        scenarios=(3,), points=("5.1:S6",),
    ),
    Question(
        q=("A log-investigation agent reads entire 2,000-line log files at every step, although it only needs the lines around "
           "each error. After a few steps it misses details it found earlier. What's the best fix?"),
        opts=("Ask the agent to remember the important lines.",
              "Run the investigation in a single step so nothing accumulates.",
              "Return only the relevant lines from the tool (for example, errors plus surrounding context) before they accumulate.",
              "Summarise every log file into one sentence."),
        ans=2,
        explain=("Tool results accumulate and consume tokens out of proportion to their relevance. Trim them to what the "
                 "task needs before they pile up."),
        scenarios=(4,), points=("5.1:K3", "5.1:S3"),
    ),
    Question(
        q=("Early in a long Claude Code session, a developer said “never touch the generated/ folder”. Hours later, after "
           "the context was compacted, Claude edits a file in generated/. According to the Claude Code docs, what prevents "
           "this?"),
        opts=("Put persistent rules like this in CLAUDE.md, which isn't lost when the conversation is compacted.",
              "Repeat the instruction every hour.",
              "Never let the context compact.",
              "Use /clear instead of compacting."),
        ans=0,
        explain=("Per the docs, detailed instructions from early in the conversation can be lost when context is compacted. "
                 "Put persistent rules in CLAUDE.md, or guide the summary with /compact's focus or Compact Instructions."),
        scenarios=(2,), basis="docs", in_bank=False,
    ),
    Question(
        q=("A support team enables prompt caching on its long system prompt and tool definitions, expecting to “free up "
           "context window space”. Conversations still hit the limit at the same point. Why?"),
        opts=("Caching only works after 24 hours.",
              "Caching was applied to the wrong messages.",
              "The cache expired too quickly.",
              "Cached prefixes still occupy the context window; caching changes what you pay and how fast, not what counts."),
        ans=3,
        explain=("Per the context-windows docs, prompt caching changes what you pay for those tokens, not whether they count. "
                 "To keep conversations within the window, use compaction or context editing."),
        scenarios=(1,), basis="docs", in_bank=False,
    ),
)

FAQ = (
    ("Isn't a bigger context window the answer?",
     "It raises the ceiling, but more context isn't automatically better. The docs describe accuracy and recall degrading as "
     "tokens grow. What you put in the window matters as much as its size."),
    ("How is this different from D4.7 Attention Engineering and D5.2 Case Facts?",
     "D4.7 covers how to lay out a long input so the important parts get used. D5.2 covers keeping exact facts outside "
     "summaries. This page covers the window as a budget: what each request must carry, and what should never enter the main "
     "window."),
    ("What does the API do when the window overflows?",
     "Per the docs: if the input alone is too big, you get a 400 “prompt is too long”. On newer models, if generation hits the "
     "limit, the stop reason is model_context_window_exceeded, which should be handled as truncated (D1.3)."),
    ("Is compaction on the exam?",
     "The guide names /compact in Claude Code (TS 5.4 Skill 5). The API's server-side compaction and context editing are "
     "docs-only here, and marked 📘."),
)

PLAYGROUND_INTRO = """
Each tab changes one thing about what goes into the **simulated** window, then shows what the model could and couldn't use.
"""


def _tab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, mode, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="ctxwin")


PLAYGROUND = (
    _tab("history", "⭐ Stateless history", "history", "The desk is cleared after every call.", "guide:5.1:K4",
         "A three-turn support chat; the message box is the customer's last message.", "guide TS 5.1 K4; docs § How the context window works",
         ("cw_history",), {"cw_history": "full"}, ("Can you refund it to my card?",),
         ("latest only: the model asks for the order number again.", "last 3 messages: the order number has already slid out.")),
    _tab("explore", "⭐ Explore in a subagent", "explore", "Send an assistant to the library.", "guide:5.4:K3",
         "Find where the webhook retry policy is set, in 30 files.", "guide TS 5.4 K3, S1; docs § Manage context with skills and subagents",
         ("cw_explore",), {"cw_explore": "subagent"}, ("Where is the retry policy for payment webhooks configured?",),
         ("main context: 400 prompt is too long after 21 reads.",)),
    _tab("session", "⭐ When the window fills", "session", "File a summary; pin the rules to the wall.", "guide:5.4:S5",
         "A long session hits 95%; the message box is a rule that must hold all session.", "guide TS 5.4 S5; docs § When context fills up",
         ("cw_rule", "cw_full"), {"cw_rule": "claude_md", "cw_full": "compact"}, ("Never edit files under migrations/",),
         ("rule in chat: lost at compaction.", "/clear: the task is gone.")),
    _tab("downstream", "⭐ Structured upstream", "downstream", "A one-page brief, not your notebook.", "guide:5.1:S6",
         "Four analyses feed a report agent; the message box is the report topic.", "guide TS 5.1 S6",
         ("cw_upstream", "cw_budget"), {"cw_upstream": "structured", "cw_budget": "6000"}, ("Heat-pump market outlook",),
         ("verbose at 6,000: two analyses dropped.", "verbose at 24,000: it fits, but no separate citations.")),
)

CONTENT = ConceptContent(
    slug="context-window", tldr=TLDR, mental_model=MENTAL_MODEL, what_it_is=WHAT_IT_IS, how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN, guide_note=GUIDE_NOTE, docs_refs=DOC_REFS, docs_verified_on=DOCS_VERIFIED_ON, grounding=GROUNDING,
    flow_dot=flow_dot, node_states=node_states, lab_intro=LAB_INTRO, variants=VARIANTS, check_outcome=check_outcome,
    distractors=DISTRACTORS, side_by_side_headers=SIDE_BY_SIDE_HEADERS, side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT, experiments=EXPERIMENTS, questions=QUESTIONS, faq=FAQ,
    related=("attention-engineering", "case-facts-block", "session-state", "subagents"), exam_points=EXAM_POINTS,
    playground=PLAYGROUND, playground_intro=PLAYGROUND_INTRO,
    scenarios=("stateless_history", "exploration", "long_session", "downstream_budget"), show_ledger=False,
)
