"""
D1.1 Agentic Loops — the reference concept page.

GROUNDING (CLAUDE.md, user rule 2026-09-26): built from the OFFICIAL Claude
documentation, fetched and read on 2026-09-26 (see DOC_REFS), plus the exam
guide's Task Statement 1.1 for what is examinable. Every substantive claim is
listed in GROUNDING with its provenance: docs / guide / recommendation /
simulated. Where the exam guide and the docs differ in detail (the guide names
two stop reasons, the docs list seven), the page says so — docs win on technical
facts, the guide wins on what the exam expects.

Everything is paraphrased. No guide or docs passages are copied at length and no
real exam question is reproduced. The docs' own code snippets are not copied
either; the lab's code is written for the simulated client.
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.guide_index import scenario_ref

DOCS_VERIFIED_ON = "2026-09-26"

_P = "https://platform.claude.com/docs/en"
_C = "https://code.claude.com/docs/en"

DOC_REFS = (
    DocRef("Stop reasons and fallback", f"{_P}/build-with-claude/handling-stop-reasons"),
    DocRef("Refusals and fallback", f"{_P}/build-with-claude/refusals-and-fallback"),
    DocRef("How tool use works", f"{_P}/agents-and-tools/tool-use/how-tool-use-works"),
    DocRef("Handle tool calls", f"{_P}/agents-and-tools/tool-use/handle-tool-calls"),
    DocRef("Tool use with Claude (overview)", f"{_P}/agents-and-tools/tool-use/overview"),
    DocRef("Tutorial: Build a tool-using agent", f"{_P}/agents-and-tools/tool-use/build-a-tool-using-agent"),
    DocRef("How the agent loop works (Agent SDK)", f"{_C}/agent-sdk/agent-loop"),
)

GROUNDING = (
    Claim("The canonical client-tool loop is a while-loop keyed on stop_reason: keep going while it is \"tool_use\".",
          "docs", "how-tool-use-works § The agentic loop (client tools)"),
    Claim("The loop exits on any other stop reason (end_turn, max_tokens, stop_sequence, refusal) and your application "
          "must handle it — end_turn is not the only way a loop ends.",
          "docs", "how-tool-use-works § The agentic loop; handling-stop-reasons § Best Practices"),
    Claim("There are seven documented stop_reason values and what to do for each (end_turn, max_tokens, stop_sequence, "
          "tool_use, pause_turn, refusal, model_context_window_exceeded).",
          "docs", "handling-stop-reasons § Quick Reference Table"),
    Claim("Tool results go back as tool_result blocks in ONE user message that follows the assistant's tool_use turn; "
          "results first, text (if any) only after them; text before them is a 400 error.",
          "docs", "handle-tool-calls § Important formatting requirements"),
    Claim("A response can carry text together with a tool_use block (\"text, tool calls, or both\").",
          "docs", "handle-tool-calls (example response); agent-loop § The loop at a glance"),
    Claim("Text added right after tool results can lead to an empty end_turn response; send results without extra text.",
          "docs", "handling-stop-reasons § Handle Empty Responses with end_turn"),
    Claim("max_tokens means the response is truncated: raise max_tokens or continue; an incomplete tool_use is retried "
          "with a higher max_tokens.",
          "docs", "handling-stop-reasons § max_tokens; § Handle Incomplete Tool Use at max_tokens"),
    Claim("pause_turn (server-tool loop hit its iteration limit): send the paused assistant content back as-is to continue.",
          "docs", "handling-stop-reasons § pause_turn; how-tool-use-works § The server-side loop"),
    Claim("A refusal is a normal HTTP 200 response (stop_reason \"refusal\", possibly empty content, stop_details) — not an "
          "error. Retry on a DIFFERENT model and stay on it; retrying the same model usually refuses again; treat partial "
          "output as incomplete; branch on stop_reason, not on content or the explanation text.",
          "docs", "refusals-and-fallback § What a refusal looks like; § Writing the retry yourself; § Common pitfalls"),
    Claim("Stop reasons are successful responses; API failures are HTTP 4xx/5xx errors — catch those separately.",
          "docs", "handling-stop-reasons § Stop Reasons vs. Errors"),
    Claim("Failed tool executions are reported with is_error: true and an instructive message.",
          "docs", "handle-tool-calls § Handling errors with is_error"),
    Claim("The Agent SDK runs the loop for you until Claude replies with no tool calls; max_turns (counts tool-use turns "
          "only) and max_budget_usd are optional limits, default none; hitting one returns an error subtype "
          "(error_max_turns / error_max_budget_usd) and the result field exists only on success.",
          "docs", "agent-sdk/agent-loop § Turns and budget; § Handle the result"),
    Claim("A PreToolUse hook can block a tool call; Claude then receives the rejection message instead of a result.",
          "docs", "agent-sdk/agent-loop § Hooks"),
    Claim("Tool Runner (SDK) can manage the tool_use loop, result formatting and retries for you.",
          "docs", "tool-use/overview; handle-tool-calls (Note)"),
    Claim("Exam anti-patterns for loop control: parsing natural-language completion signals, an arbitrary iteration cap as "
          "the PRIMARY stopping mechanism, treating assistant text as the completion indicator.",
          "guide", "TS 1.1 · Skill 3 · p.5 (Guide §6)"),
    Claim("Model-driven decisions vs pre-configured decision trees / tool sequences.",
          "guide", "TS 1.1 · Knowledge 3 · p.5; TS 1.6 · p.8 for when a fixed pipeline is right"),
    Claim("The exam names two stop reasons (tool_use, end_turn); the docs list seven — production loops handle all of them.",
          "guide", "TS 1.1 · Knowledge 1 and Skill 1 · p.5, vs handling-stop-reasons"),
    Claim("The specific MAX_TURNS value (10) and the for/else shape are this page's choices, modelled on the SDK's max_turns.",
          "recommendation", "the docs give the mechanism, not a value"),
    Claim("stop_sequence: the model emitted one of your custom stop sequences; the stop sequence text is NOT included in the "
          "content, and the stop_sequence field says which one fired (re-checked against the docs on 2026-09-26 while building D1.3).",
          "docs", "handling-stop-reasons § stop_sequence"),
    Claim("model_context_window_exceeded is a stop reason (beta per the docs): the model filled its context window; treat the "
          "response as truncated.", "docs", "handling-stop-reasons § Quick Reference Table"),
    Claim("The playground's result labels error_max_turns / error_max_budget_usd / error_during_execution are the Agent SDK's "
          "documented ResultMessage subtypes; labels prefixed \"playground:\" are this workbench's own.",
          "docs", "code.claude.com/docs/en/agent-sdk/agent-loop § Handle the result"),
    Claim("The playground's model replies, token sizes, illustrative $ rates, the simulated context-window number, when the budget "
          "is checked (after every model call) are simulation choices — the docs page I read does not specify the budget timing.",
          "simulated", "utils/agent_playground.py; utils/mock_claude.py"),
    Claim("What the simulated model says in each scenario (narrating \"done\", never converging, the primary model "
          "refusing, a long answer, a pausing server tool) is invented to make each documented behaviour reproducible.",
          "simulated", "utils/mock_claude.py"),
    Claim("The simulated API's error wording is an approximation; the docs quote only the fragment \"tool_use ids were found "
          "without tool_result blocks immediately after\". The empty-end_turn behaviour is made deterministic here; the "
          "docs say it typically occurs.",
          "simulated", "utils/mock_claude.py; handle-tool-calls; handling-stop-reasons"),
    Claim("Model ids in the lab (mock-claude, mock-claude-fallback) are placeholders; real ids are pinned in one place.",
          "simulated", "CLAUDE.md model rules"),
)

# ── Flowchart (Graphviz DOT) ───────────────────────────────────────────────────
# Layout: one left-to-right spine (request -> send -> read stop_reason), then ONE aligned column of
# branches (one per stop_reason), and a single "loop back" node, so no handler draws its own edge back.
# Colour = concept (see the key on the chart). After a run, fill = what happened (green ok / red wrong /
# grey not reached) and the border keeps the concept colour.

_CONCEPT = {                     # key -> (fill, border, label in the key)
    "round":   ("#DBEAFE", "#0066CC", "tool round — keep looping"),
    "decide":  ("#EDE9FE", "#7C3AED", "decision — read stop_reason"),
    "finish":  ("#D1FAE5", "#059669", "finish — end_turn"),
    "recover": ("#FEF3C7", "#D97706", "recover — then loop again"),
    "guard":   ("#E5E7EB", "#6B7280", "guard / other — fail loudly"),
    "bug":     ("#FFFFFF", "#DC2626", "bug (an exam distractor)"),
}

# node -> (label, shape, concept)
_NODES = {
    "START":    ("Build messages\\n(the user's request)", "box", "round"),
    "SEND":     ("Send request\\nmessages.create(messages, tools)", "box", "round"),
    "INSPECT":  ("Read\\nstop_reason", "diamond", "decide"),
    "EXEC":     ("⭐ tool_use\\n→ run every tool", "box", "round"),
    "APPEND":   ("Append assistant turn +\\none user message of tool_results", "box", "round"),
    "DONE":     ("⭐ end_turn\\n→ the final answer", "box", "finish"),
    "TRUNC":    ("max_tokens (truncated)\\n→ raise max_tokens", "box", "recover"),
    "REFUSAL":  ("refusal (HTTP 200)\\n→ retry on a DIFFERENT model", "box", "recover"),
    "PAUSE":    ("pause_turn\\n→ send the response back as-is", "box", "recover"),
    "HANDLE":   ("stop_sequence / anything else\\n→ handle explicitly", "box", "guard"),
    "LOOP":     ("↺ next turn", "box", "round"),
    "BACKSTOP": ("turn > MAX_TURNS\\n→ fail loudly (SDK: error_max_turns)", "box", "guard"),
    "ABANDON":  ("✗ leave the loop while the model\\nstill wants to continue", "box", "bug"),
    "NOMODEL":  ("✗ developer hard-codes the\\ntool order (no model call)", "box", "bug"),
}

_BRANCHES = ["EXEC", "TRUNC", "REFUSAL", "PAUSE", "DONE", "HANDLE"]   # top-to-bottom column
_NOT_REACHED = ("#F3F4F6", "#9CA3AF")
_OK = "#BBF7D0"
_BAD = "#FECACA"


def _key(highlighted: bool) -> str:
    rows = "".join(
        f'<TR><TD BGCOLOR="{fill}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD>'
        f'<TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">{text}</FONT></TD></TR>'
        for fill, _line, text in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0">'
             '<FONT POINT-SIZE="10">named by the exam guide (TS 1.1, p.5)</FONT></TD></TR>')
    if highlighted:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">'
                 'Your run: <B>green</B> = handled correctly · <B>red</B> = went wrong · grey = not reached'
                 '</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3">'
            '<TR><TD COLSPAN="2" BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states: dict) -> str:
    highlighted = bool(states)
    lines = [
        "digraph G {",
        '  rankdir=TB; bgcolor="transparent"; nodesep=0.28; ranksep=0.55; newrank=true;',
        '  node [fontname="Helvetica", fontsize=12, style="rounded,filled", penwidth=2];',
        '  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];',
    ]
    for node, (label, shape, concept) in _NODES.items():
        fill, line, _ = _CONCEPT[concept]
        style = "rounded,filled"
        text = label
        if highlighted:
            state, suffix = states.get(node, (None, ""))
            fill = {"ok": _OK, "bad": _BAD}.get(state, _NOT_REACHED[0])
            if state is None and concept != "bug":
                line = _NOT_REACHED[1] if node not in ("START",) else line
            if suffix:
                text = f"{label}\\n{suffix}"
        if concept == "bug":
            style = "rounded,filled,dashed"
        lines.append(f'  {node} [label="{text}", shape={shape}, style="{style}", fillcolor="{fill}", color="{line}"];')

    # spine
    lines += ["  START -> SEND -> INSPECT;"]
    # one aligned column of branches
    lines += [f"  INSPECT -> {n};" for n in _BRANCHES]
    lines += ["  { rank=same; " + "; ".join(_BRANCHES) + "; }"]
    # every 'continue' branch joins ONE loop-back node
    lines += ["  EXEC -> APPEND -> LOOP;", "  TRUNC -> LOOP;", "  REFUSAL -> LOOP;", "  PAUSE -> LOOP;",
              '  LOOP -> SEND [constraint=false, label="repeat", color="#0066CC", fontcolor="#0066CC"];',
              '  LOOP -> BACKSTOP [style=dashed, label="limit"];']
    # bugs sit under the spine, unconnected (they are things that go wrong, not steps)
    lines += ['  START -> NOMODEL [style=invis];', '  INSPECT -> ABANDON [style=invis];',
              '  DONE -> KEY [style=invis];']
    lines.append(_key(highlighted))
    lines.append("}")
    return "\n".join(lines)


def node_states(trace) -> dict:
    """Turn a lab run's events into flowchart colours: green = handled correctly,
    red = where the run went wrong, missing = never reached."""
    if not trace:
        return {}
    events = trace["events"]
    raised = trace["status"]["raised"] or ""
    calls = [e for e in events if e["kind"] == "api_call"]
    execs = [e for e in events if e["kind"] == "tool_exec"]

    s = {"START": ("ok", "")}
    if calls:
        s["SEND"] = ("ok", f"×{len(calls)}")
        s["INSPECT"] = ("ok", "")
    if execs:
        s["EXEC"] = ("ok" if calls else "bad", f"×{len(execs)}")

    def followed(i, test) -> bool:
        return i + 1 < len(calls) and test(calls[i], calls[i + 1])

    # After a tool_use response the conversation must grow (assistant turn + tool results).
    tool_pairs = [(a, b) for a, b in zip(calls, calls[1:]) if a["stop_reason"] == "tool_use"]
    if tool_pairs:
        grew = all(b["advanced"] for _, b in tool_pairs)
        s["APPEND"] = ("ok" if grew else "bad", "" if grew else "messages never grew")

    if len(calls) > 1 and any(e["advanced"] for e in calls[1:]):
        s["LOOP"] = ("ok", "")

    trunc = [i for i, c in enumerate(calls) if c["stop_reason"] == "max_tokens"]
    if trunc:
        handled = all(followed(i, lambda a, b: b["max_tokens"] > a["max_tokens"]) for i in trunc)
        s["TRUNC"] = ("ok" if handled else "bad", "" if handled else "treated as a final answer")

    refused = [i for i, c in enumerate(calls) if c["stop_reason"] == "refusal"]
    if refused:
        handled = all(followed(i, lambda a, b: b["model"] != a["model"]) for i in refused)
        s["REFUSAL"] = ("ok" if handled else "bad", "" if handled else "no different model tried")

    paused = [i for i, c in enumerate(calls) if c["stop_reason"] == "pause_turn"]
    if paused:
        handled = all(followed(i, lambda a, b: b["advanced"]) for i in paused)
        s["PAUSE"] = ("ok" if handled else "bad", "" if handled else "paused turn not sent back")

    last = calls[-1] if calls else None
    if last and last["stop_reason"] == "end_turn":
        empty = not any(b["type"] == "text" and b["text"] for b in last["blocks"])
        s["DONE"] = ("bad", "empty answer") if empty else ("ok", "")
    if last and last["stop_reason"] in ("tool_use", "pause_turn") and not raised:
        s["ABANDON"] = ("bad", f"loop ended on {last['stop_reason']}")

    if raised.startswith("RunawayGuard"):
        s["BACKSTOP"] = ("bad", "no backstop of your own")
    elif raised.startswith("MockAPIError"):
        s["SEND"] = ("bad", f"×{len(calls)} then API error")
    elif "unhandled stop_reason" in raised:
        s["HANDLE"] = ("ok", "")
    elif "escalate" in raised and "refused" in raised:
        s["REFUSAL"] = ("ok", "escalated")
    elif raised:
        s["BACKSTOP"] = ("ok", "raised loudly")
    if execs and not calls:
        s["NOMODEL"] = ("bad", "no model call at all")
    return s


# ── Result check per scenario ──────────────────────────────────────────────────


def check_outcome(scenario: str, trace: dict):
    ledger = trace["ledger"]
    raised = trace["status"]["raised"]
    calls = [e for e in trace["events"] if e["kind"] == "api_call"]
    refunds, confs = ledger["refunds"], ledger["confirmations"]
    dupes = sum(1 for r in refunds if r["duplicate"])
    last = calls[-1] if calls else None
    last_stop = last["stop_reason"] if last else None
    answered = bool(last and any(b["type"] == "text" and b["text"] for b in last["blocks"]))
    used_fallback = any(c["model"] == "mock-claude-fallback" for c in calls)
    observed = (f"refunds issued: {len(refunds)} ({dupes} duplicate) · confirmations sent: {len(confs)} · "
                f"last stop_reason: {last_stop or '—'} · raised: {raised or 'no'}")

    # last_stop None = no model call at all. That may pass on the happy path (a hard-coded sequence CAN
    # give the right answer when nothing unexpected happens) — the flowchart still shows it was never
    # model-driven, and already_refunded is where it breaks.
    if scenario == "damaged_order":
        expected = "exactly one refund (and, if a model is driving, the run ends on end_turn with an answer)"
        ok = len(refunds) == 1 and dupes == 0 and (last_stop is None or (last_stop == "end_turn" and answered))
    elif scenario == "already_refunded":
        expected = "no refund at all (already refunded); a model-driven run ends on end_turn"
        ok = len(refunds) == 0 and (last_stop is None or last_stop == "end_turn")
    elif scenario == "long_task":
        expected = "one refund AND one confirmation, ending on end_turn"
        ok = len(refunds) == 1 and len(confs) == 1 and last_stop == "end_turn"
    elif scenario == "narrates_done":
        expected = "the refund is actually issued before the agent finishes"
        ok = len(refunds) == 1 and last_stop == "end_turn"
    elif scenario == "runaway":
        expected = "a LOUD failure from your own turn limit (exception / escalation), not a silent 'success'"
        ok = bool(raised) and not raised.startswith(("RunawayGuard", "MockAPIError"))
    elif scenario == "truncated_answer":
        expected = "the COMPLETE answer: a final end_turn (not max_tokens) and the refund issued"
        ok = len(refunds) == 1 and last_stop == "end_turn" and answered
    elif scenario == "refusal":
        expected = "the request is served by a DIFFERENT model: one refund, ending on end_turn"
        ok = used_fallback and len(refunds) == 1 and last_stop == "end_turn"
    elif scenario == "pause_turn":
        expected = "the paused turn is sent back as-is and the work finishes: one refund, ending on end_turn"
        ok = len(refunds) == 1 and last_stop == "end_turn"
    else:
        expected, ok = "(no expectation defined for this scenario)", True
    return ok, expected, observed


# ── Lab code variants ──────────────────────────────────────────────────────────

_HEADER = '''from utils.mock_claude import MockClaude      # SIMULATED stand-in. Real SDK: import anthropic
from utils.tools import TOOL_SCHEMAS, execute_tool

client = MockClaude()                          # real SDK: client = anthropic.Anthropic()
MODEL = "mock-claude"                          # real code pins ONE model id in one place

messages = [{"role": "user", "content":
    "Customer alice@example.com says order ORD-1001 arrived damaged. Please resolve it."}]
'''

CORRECT = _HEADER + '''FALLBACK_MODEL = "mock-claude-fallback"        # docs: retry a refusal on a DIFFERENT model
MAX_TURNS = 10                                 # like the Agent SDK's max_turns: a limit that FAILS LOUDLY
model, max_tokens = MODEL, 256

for turn in range(1, MAX_TURNS + 1):
    response = client.messages.create(model=model, max_tokens=max_tokens,
                                      tools=TOOL_SCHEMAS, messages=messages)
    print(f"turn {turn}: stop_reason = {response.stop_reason}")

    if response.stop_reason == "tool_use":     # docs: keep looping WHILE stop_reason is tool_use
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                output = execute_tool(block.name, block.input)
                print(f"   ran {block.name}({block.input}) -> {output}")
                tool_results.append({"type": "tool_result",
                                     "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": tool_results})   # ONE message, results only
        continue

    if response.stop_reason == "pause_turn":   # a server-tool loop paused: send it back as-is
        messages.append({"role": "assistant", "content": response.content})
        continue

    if response.stop_reason == "max_tokens":   # truncated: raise max_tokens and ask again
        max_tokens *= 2
        continue

    if response.stop_reason == "refusal":      # HTTP 200, NOT an error: retry on a different model
        print("   refused:", response.stop_details)
        if model == FALLBACK_MODEL:
            raise RuntimeError("the fallback model refused too - escalate to a human")
        model = FALLBACK_MODEL                 # and stay on it for the rest of the conversation
        continue

    if response.stop_reason == "end_turn":     # the model finished: this is the answer
        answer = "".join(b.text for b in response.content if b.type == "text")
        print("FINAL ANSWER:", answer)
        break

    raise RuntimeError(f"unhandled stop_reason: {response.stop_reason}")   # stop_sequence, ...
else:
    raise RuntimeError("no end_turn within MAX_TURNS - fail loudly (cf. the SDK's error_max_turns)")
'''

DISTRACTOR_A = _HEADER + '''
for turn in range(1, 9):
    response = client.messages.create(model=MODEL, max_tokens=1024,
                                      tools=TOOL_SCHEMAS, messages=messages)
    text = "".join(b.text for b in response.content if b.type == "text")
    print(f"turn {turn}: stop_reason = {response.stop_reason} | text = {text!r}")

    if "done" in text.lower():                 # WRONG: reading the model's PROSE as a control signal
        print("FINAL ANSWER:", text)
        break

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                output = execute_tool(block.name, block.input)
                print(f"   ran {block.name}({block.input}) -> {output}")
                tool_results.append({"type": "tool_result",
                                     "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": tool_results})
'''

DISTRACTOR_B = _HEADER + '''
for turn in range(1, 9):
    response = client.messages.create(model=MODEL, max_tokens=1024,
                                      tools=TOOL_SCHEMAS, messages=messages)
    text = "".join(b.text for b in response.content if b.type == "text")
    print(f"turn {turn}: stop_reason = {response.stop_reason} | text = {text!r}")

    if any(b.type == "text" for b in response.content):   # WRONG: "there is text, so this must be the answer"
        print("FINAL ANSWER:", text)
        break

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                output = execute_tool(block.name, block.input)
                print(f"   ran {block.name}({block.input}) -> {output}")
                tool_results.append({"type": "tool_result",
                                     "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": tool_results})
'''

DISTRACTOR_C = _HEADER + '''
final_text = ""
for turn in range(3):                          # WRONG: the iteration cap IS the stop condition
    response = client.messages.create(model=MODEL, max_tokens=1024,
                                      tools=TOOL_SCHEMAS, messages=messages)
    print(f"turn {turn + 1}: stop_reason = {response.stop_reason}")
    for b in response.content:
        if b.type == "text":
            final_text = b.text

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                output = execute_tool(block.name, block.input)
                print(f"   ran {block.name}({block.input}) -> {output}")
                tool_results.append({"type": "tool_result",
                                     "tool_use_id": block.id, "content": output})
        messages.append({"role": "user", "content": tool_results})

print("FINAL ANSWER:", final_text or "(none)")  # runs after 3 turns no matter what happened
'''

DISTRACTOR_D = _HEADER + '''
for turn in range(1, 7):                       # cap of 6 only so this demo terminates
    response = client.messages.create(model=MODEL, max_tokens=1024,
                                      tools=TOOL_SCHEMAS, messages=messages)
    print(f"turn {turn}: stop_reason = {response.stop_reason}  (messages sent: {len(messages)})")

    if response.stop_reason == "end_turn":
        print("FINAL ANSWER:", "".join(b.text for b in response.content if b.type == "text"))
        break

    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":
                output = execute_tool(block.name, block.input)
                print(f"   ran {block.name}({block.input}) -> {output}")
        # WRONG: the output was printed but never added to `messages`, so the model
        # can never see it - and never sees that it already asked.
'''

DISTRACTOR_E = '''from utils.tools import execute_tool

# WRONG (for a task that needs judgment): the developer decides which tools run and in what
# order. No model is consulted, so nothing can react to what a tool returns.
customer = execute_tool("get_customer", {"email": "alice@example.com"})
order = execute_tool("lookup_order", {"order_id": "ORD-1001"})
refund = execute_tool("process_refund", {"order_id": "ORD-1001", "amount": 49.0})
print("FINAL ANSWER: refund processed ->", refund)
'''

_HEADER_ASK = _HEADER + '''

def ask(model=MODEL, max_tokens=256):
    return client.messages.create(model=model, max_tokens=max_tokens,
                                  tools=TOOL_SCHEMAS, messages=messages)
'''

DISTRACTOR_F = _HEADER_ASK + '''
response = ask()
while response.stop_reason == "tool_use":      # the docs' loop shape: continue while tool_use
    messages.append({"role": "assistant", "content": response.content})
    tool_results = [{"type": "tool_result", "tool_use_id": b.id,
                     "content": execute_tool(b.name, b.input)}
                    for b in response.content if b.type == "tool_use"]
    messages.append({"role": "user", "content": tool_results})
    response = ask()

# WRONG: whatever ended the loop is assumed to be "the final answer"
print("stop_reason =", response.stop_reason)
print("FINAL ANSWER:", "".join(b.text for b in response.content if b.type == "text"))
'''

DISTRACTOR_G = _HEADER_ASK + '''
for attempt in range(1, 4):
    response = ask(model=MODEL)                # WRONG: the same model, the same request, every time
    print(f"attempt {attempt}: stop_reason = {response.stop_reason}")
    if response.stop_reason != "refusal":
        break
    print("   refused - trying again")

print("FINAL ANSWER:", "".join(b.text for b in response.content if b.type == "text") or "(empty)")
'''

DISTRACTOR_H = _HEADER_ASK + '''
for turn in range(1, 9):
    response = ask()
    print(f"turn {turn}: stop_reason = {response.stop_reason}")

    if response.stop_reason == "end_turn":
        print("FINAL ANSWER:", "".join(b.text for b in response.content if b.type == "text") or "(empty)")
        break

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                output = execute_tool(block.name, block.input)
                print(f"   ran {block.name}({block.input}) -> {output}")
                tool_results.append({"type": "tool_result",
                                     "tool_use_id": block.id, "content": output})
        # WRONG: a friendly text nudge right after the results
        messages.append({"role": "user",
                         "content": tool_results + [{"type": "text", "text": "Thanks! Please continue."}]})
'''

DISTRACTOR_I = _HEADER_ASK + '''
for turn in range(1, 9):
    response = ask()
    print(f"turn {turn}: stop_reason = {response.stop_reason}")

    if response.stop_reason == "end_turn":
        print("FINAL ANSWER:", "".join(b.text for b in response.content if b.type == "text"))
        break

    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                output = execute_tool(block.name, block.input)
                print(f"   ran {block.name}({block.input}) -> {output}")
                tool_results.append({"type": "tool_result",
                                     "tool_use_id": block.id, "content": output})
        # WRONG: explanatory text BEFORE the tool results
        messages.append({"role": "user",
                         "content": [{"type": "text", "text": "Here are the results:"}] + tool_results})
'''

VARIANTS = (
    Variant(
        "correct", "✅ ⭐ The canonical loop (every stop_reason handled)", "correct", CORRECT, "damaged_order",
        observe=("Turns 1–3 end with stop_reason = tool_use and run one tool each; turn 4 returns end_turn with the "
                 "answer. One refund in the ledger, every node on the flowchart's path green. Now switch the scenario: "
                 "already_refunded (the model stops after the lookup — no refund), refusal (the loop retries on a "
                 "different model), truncated_answer (max_tokens is raised and the request repeated), pause_turn "
                 "(the paused turn is sent back), runaway (YOUR turn limit fires and the run fails loudly)."),
        why=("The loop is keyed on stop_reason: it continues on tool_use, and every other stop reason gets an explicit "
             "branch instead of being assumed to mean 'done'. Tool results go back every round so the next turn can use "
             "them. The turn limit mirrors the Agent SDK's max_turns: hitting it is a loud error, never a silent success."),
    ),
    Variant(
        "A", "⭐❌ A — stop when the reply says “done”", "distractor", DISTRACTOR_A, "narrates_done",
        observe=("On turn 3 the model writes “I'm done checking. Issuing the refund now.” while stop_reason is STILL "
                 "tool_use. The loop quits on the word — FINAL ANSWER is that sentence, the ledger shows no refund, and "
                 "the flowchart's red “leave the loop” node lights up. On easy scenarios it appears to work, which is "
                 "the trap."),
        why=("Prose is narration, not control flow: one response can announce completion and still ask for a tool. "
             "The guide names natural-language completion signals as an anti-pattern (TS 1.1), and the docs' refusal "
             "guidance says the same in general form: branch on stop_reason, not on content."),
        fix="Branch on response.stop_reason: continue on tool_use, finish on end_turn.",
        source="guide:1.1:S3",
    ),
    Variant(
        "B", "⭐❌ B — any text block means “final answer”", "distractor", DISTRACTOR_B, "damaged_order",
        observe=("Turn 1 already contains text (“Let me verify the customer first.”) next to a tool request. The loop "
                 "exits after ONE call: no tool ran, and the “final answer” is a status line."),
        why=("Intermediate turns routinely carry text alongside tool requests — the docs' own example response has a "
             "text block followed by a tool_use block. Treating assistant text as the completion indicator is a named "
             "anti-pattern in the guide (TS 1.1)."),
        fix="Branch on response.stop_reason, not on the shape of response.content.",
        source="guide:1.1:S3",
    ),
    Variant(
        "C", "⭐❌ C — the iteration cap is the stop condition", "distractor", DISTRACTOR_C, "long_task",
        observe=("The cap of 3 ends the loop mid-workflow: no refund, no confirmation, no error — and the script "
                 "still prints a “FINAL ANSWER” (just the last status line). Change 3 to 8 and it “works”, which is "
                 "the trap: the number is a guess, and this loop reports partial work as if it were finished."),
        why=("A cap that decides WHEN you stop replaces the model's own signal, so any task longer than your guess is "
             "silently cut short. The guide flags an arbitrary iteration cap as the PRIMARY stopping mechanism as an "
             "anti-pattern. Limits themselves are fine — the Agent SDK's max_turns and max_budget_usd exist — but "
             "hitting one returns an error result (error_max_turns / error_max_budget_usd) with no result text, "
             "never a success."),
        fix=("Stop on the model's signal (no more tool calls / end_turn). Keep a turn or budget limit as a guard that "
             "raises, and handle that error result explicitly."),
        source="guide:1.1:S3",
    ),
    Variant(
        "D", "⭐❌ D — run the tool but never append the result", "distractor", DISTRACTOR_D, "damaged_order",
        observe=("The same request repeats: get_customer is executed 6 times because “messages sent” never grows. The "
                 "flowchart's APPEND node turns red (“messages never grew”)."),
        why=("The model can only reason about what is in the conversation. Without the assistant turn and the "
             "tool_result message the docs prescribe, it cannot see that it already asked — so it asks again."),
        fix="Append the assistant turn AND a user message of tool_result blocks on every round.",
        source="guide:1.1:K2",
    ),
    Variant(
        "E", "⭐❌ E — hard-code the tool sequence", "distractor", DISTRACTOR_E, "already_refunded",
        observe=("On damaged_order it even passes — a fixed sequence works while nothing unexpected happens. On "
                 "already_refunded process_refund runs anyway: the ledger shows a DUPLICATE refund. No model call "
                 "happens at all, so nothing could have noticed."),
        why=("A pre-configured sequence is a workflow, not an agentic loop — it cannot react to results. It is the "
             "right choice only when the steps really are predictable (guide TS 1.6); it is the distractor when the "
             "next step depends on what a tool returns."),
        fix=("Let the model pick the next tool from context. Where a rule must be GUARANTEED, enforce it in code "
             "around the loop: the docs describe PreToolUse hooks that block a call (Claude then receives the "
             "rejection), and the guide names hooks and prerequisite gates (TS 1.4, 1.5)."),
        source="guide:1.1:K3",
    ),
    Variant(
        "F", "❌ F — anything that isn't tool_use is the final answer", "distractor", DISTRACTOR_F, "truncated_answer",
        observe=("The docs-shaped while-loop ends on the first non-tool_use response — and F prints whatever it holds. "
                 "truncated_answer: a half-finished sentence, stop_reason max_tokens. refusal: an EMPTY answer. "
                 "pause_turn: the ‘let me check…’ line, work abandoned. No exception in any of them."),
        why=("The docs are explicit that the loop exits on any stop reason other than tool_use, which means Claude either "
             "finished or stopped for another reason your application must handle. A refusal is an HTTP 200, so no "
             "exception will save you; max_tokens is a truncated response; pause_turn is unfinished work."),
        fix="Give every documented stop_reason an explicit branch (see the canonical loop) and fail loudly on the ones you don't handle.",
        source="docs",
    ),
    Variant(
        "G", "❌ G — retry a refusal on the same model", "distractor", DISTRACTOR_G, "refusal",
        observe=("Three attempts, three refusals: same model, same request, same result — and finally an empty answer. "
                 "The flowchart's REFUSAL node turns red (“no different model tried”)."),
        why=("The docs' pitfall list: re-sending a refused request to the same model usually earns another refusal. A "
             "refusal is a normal response (HTTP 200), not a transient error, so exponential backoff does not help."),
        fix=("Retry on a DIFFERENT model and stay on it for the following turns; if that refuses too, escalate. Don't "
             "parse the explanation text — the docs say it isn't stable, so display it instead."),
        source="docs",
    ),
    Variant(
        "H", "❌ H — add a friendly text nudge after the tool results", "distractor", DISTRACTOR_H, "damaged_order",
        observe=("After the first tool round the model returns an EMPTY response with stop_reason end_turn: “FINAL "
                 "ANSWER: (empty)” and no refund. (The simulator makes this deterministic; the docs say it typically "
                 "happens.)"),
        why=("The docs list this as a cause of empty end_turn responses: text blocks added right after tool results "
             "teach Claude to expect input after every tool use. The API accepts the text (it is allowed AFTER the "
             "results) — it just backfires."),
        fix=("Send tool results directly with no extra text. If empty responses persist, add a continuation prompt in a "
             "NEW user message rather than blindly retrying."),
        source="docs",
    ),
    Variant(
        "I", "❌ I — put explanatory text before the tool results", "distractor", DISTRACTOR_I, "damaged_order",
        observe=("The next request is rejected (simulated 400 invalid_request_error): in the user message that carries "
                 "tool results, tool_result blocks must come first. The flowchart's SEND node turns red."),
        why=("The docs state the ordering rule outright: tool_result blocks come FIRST in the content array and any text "
             "only after them — the text-first example is the docs' own illustration of a 400 error."),
        fix="Put every tool_result first (all of them, in one user message); send no text, or only text after them.",
        source="docs",
    ),
)

# ── What the guide demands (Guide §6 · TS 1.1, p.5) — paraphrased; bullet numbers = order under each heading ──

EXAM_POINTS = (
    ExamPoint("1.1", "K", 1, "The loop lifecycle: send a request, inspect stop_reason (tool_use vs end_turn), run the "
              "requested tools, return the results for the next iteration.", "✅ canonical loop · flowchart"),
    ExamPoint("1.1", "K", 2, "Tool results are appended to the conversation history so the model can reason about its "
              "next action.", "✅ · ❌ D (never appends)"),
    ExamPoint("1.1", "K", 3, "Model-driven decisions (Claude picks the next tool from context) versus pre-set decision "
              "trees or tool sequences.", "❌ E (hard-coded order) · decision tree"),
    ExamPoint("1.1", "S", 1, "Write loop control that continues on stop_reason \"tool_use\" and ends on \"end_turn\".",
              "✅ canonical loop"),
    ExamPoint("1.1", "S", 2, "Add tool results to the context between iterations so the model can use the new "
              "information.", "✅ · ❌ D"),
    ExamPoint("1.1", "S", 3, "Avoid three anti-patterns: parsing natural-language signals to end the loop; an arbitrary "
              "iteration cap as the primary stop; treating assistant text as the completion indicator.",
              "❌ A · ❌ B · ❌ C"),
)


# ── Agent playground: one message box per sub-concept (each gets a mental model, per CLAUDE.md) ─────────────────────

_ORDER_MSG = "Customer alice@example.com says order ORD-1001 arrived damaged. Please refund it."

PLAYGROUND_INTRO = """
Type a message and watch a docs-shaped agent handle it. Each tab is one **sub-concept** — a stop reason or a limit — with
its own message box and the **developer-side constraints** that sub-concept is about (`max_tokens`, `max_turns`, a spending
limit, how you handle a refusal…). Change a knob, send the same message again, and compare. The 🧭 line on each tab is the
picture to remember; ⭐ tabs are named in the exam guide, the rest come from the official docs.
"""

PLAYGROUND = (
    PlayTab(
        "loop", "⭐ tool_use → end_turn", "none",
        "`tool_use` means “I need something before I can answer”; `end_turn` means “I'm finished”. You steer by those signals, never by the words the model uses.",
        "guide:1.1:K1",
        "The normal loop: the model asks for a tool (`tool_use`), your code runs it and returns a `tool_result`, and the loop "
        "repeats until the model replies with `end_turn`. **Model-driven** means the model decides whether it needs a tool at "
        "all — send a greeting and it answers straight away (one call, no tools); mention an order and it works through the tools.",
        "how-tool-use-works § The agentic loop; handling-stop-reasons § tool_use, end_turn",
        (), {}, (_ORDER_MSG, "hello, what can you do?"),
        ("Send the order message and count the calls: 3 tool rounds, then `end_turn` on call 4.",
         "Send “hello, what can you do?” — no order, so no tools: the model decides that itself (guide TS 1.1 Knowledge 3).",
         "Look at the input tokens on each call: they grow because every request re-sends the whole conversation.")),
    PlayTab(
        "max_tokens", "max_tokens", "long_answer",
        "`max_tokens` is the size of the answer box: hit its edge and the sentence is cut off mid-word — that's truncation, not “done”.",
        "",
        "`max_tokens` is YOUR cap on one response. If the answer is longer, generation stops there and `stop_reason` is "
        "`max_tokens` — the text is incomplete. The docs say to raise `max_tokens` or continue the response, and that an "
        "**incomplete `tool_use`** should be retried with a higher limit. Here the final answer needs about 300 (simulated) tokens.",
        "handling-stop-reasons § max_tokens; § Handle Incomplete Tool Use at max_tokens",
        ("max_tokens", "max_tokens_policy"), {"max_tokens": 100, "max_tokens_policy": "raise"}, (_ORDER_MSG,),
        ("Keep 100 with “raise”: it doubles to 200 (still cut), then 400 (fits) — three calls on the last turn.",
         "Switch to “report it as a result”: the run ends with a `playground:max_tokens` result and a cut-off sentence.",
         "Set max_tokens to 400: nothing to handle at all. What did the limit cost you when it was too small?")),
    PlayTab(
        "refusal", "refusal", "refusal",
        "A refusal is a locked door, not a dropped call: redialling the same door gets the same answer — try a different door (model).",
        "",
        "A refusal is a **normal HTTP 200 response** with `stop_reason: \"refusal\"`, usually empty content and a `stop_details` "
        "object — so no exception is raised and error-rate monitoring never sees it. The docs say to retry on a **different "
        "model** and stay on it for the following turns (the same model usually refuses again), and to branch on `stop_reason`, "
        "not on the explanation text. Here the primary simulated model always declines.",
        "refusals-and-fallback § What a refusal looks like; § Writing the retry yourself; § Common pitfalls",
        ("refusal_policy",), {"refusal_policy": "different_model"}, (_ORDER_MSG, "hello, what can you do?"),
        ("Run with “different model”: call 1 is a refusal, then the fallback model serves the request to `end_turn`.",
         "Switch to “SAME model”: three refusals, then it gives up — the docs' pitfall.",
         "Switch to “stop”: the run ends without an answer and without any error — that is what an unhandled refusal looks like.",
         "Send “hello…” too: the refusal applies to any message in this simulation.")),
    PlayTab(
        "pause_turn", "pause_turn", "pause",
        "`pause_turn` is a bookmark: the server-side work isn't finished — hand the book back exactly as it is to carry on.",
        "",
        "When the model uses a **server tool** (like web search) and its server-side loop hits the iteration limit, the response "
        "ends with `pause_turn`. The docs say to send that assistant content back **as-is** in the next request to let it continue. "
        "Treating it as the end shows unfinished work as if it were the answer.",
        "handling-stop-reasons § pause_turn; how-tool-use-works § The server-side loop",
        ("pause_policy",), {"pause_policy": "resume"}, (_ORDER_MSG,),
        ("“Send back as-is”: the loop continues and finishes normally.",
         "“Treat it as the final answer”: you get the model's ‘let me check…’ line as the answer — work abandoned.")),
    PlayTab(
        "stop_sequence", "stop_sequence", "none",
        "A stop sequence is a tripwire word you set: the moment the model would say it, generation halts — and `stop_reason` tells you it was the tripwire, not a natural finish.",
        "",
        "If you pass custom stop sequences and the model emits one, generation stops and `stop_reason` is `stop_sequence`; read the "
        "`stop_sequence` field to see which one fired. The stop sequence text itself is NOT "
        "included in the content (docs); the simulation cuts the reply right before it.",
        "handling-stop-reasons § stop_sequence",
        ("stop_sequences",), {"stop_sequences": "Customer"}, (_ORDER_MSG,),
        ("The final answer is “Refund issued for ORD-1001. Customer A has been taken care of.” With the tripwire “Customer” it "
         "stops after “…ORD-1001. ”.",
         "Try a word that never appears (“zebra”): a normal `end_turn`.",
         "Clear the box: no tripwire, normal `end_turn`.")),
    PlayTab(
        "context", "context window", "none",
        "The context window is the desk: every message and tool result stays on it; when the desk is full the model can't continue, whatever the task.",
        "",
        "Every request re-sends the whole conversation, so input grows each turn. `model_context_window_exceeded` (listed as a beta "
        "stop reason in the docs) means the model filled its context window — treat the response as truncated. The window size below "
        "is a **simulated number** for teaching. Real remedies (trim, summarise, a fresh session with a summary) are Domain 5 topics.",
        "handling-stop-reasons § Quick Reference Table (model_context_window_exceeded)",
        ("context_window",), {"context_window": 150}, (_ORDER_MSG,),
        ("With 150 the desk fills on the third call. Read the input-token column: 28 → 134 → 229…",
         "Raise it to 400: the run completes. What changed? Only the desk size.",
         "Set 0 for unlimited.")),
    PlayTab(
        "max_turns", "max_turns", "runaway",
        "`max_turns` is a fuse: a healthy loop never touches it; when it trips you get an error result, not an answer.",
        "",
        "In the Agent SDK, `max_turns` caps **tool-use turns** (default: no limit). When the agent wants another tool round beyond "
        "it, the run ends with the result subtype `error_max_turns` — and, per the docs, the `result` text exists only on success, "
        "so check the subtype first. Here the simulated model never converges (it keeps looking up an order that doesn't exist).",
        "code.claude.com agent-sdk/agent-loop § Turns and budget; § Handle the result",
        ("max_turns",), {"max_turns": 4}, (_ORDER_MSG,),
        ("max_turns = 4: four tool rounds, then `error_max_turns`.",
         "Set 0 (no limit): nothing but this playground's own safety net stops it after 25 calls — that is why a limit exists.",
         "Change the condition mentally: a healthy run needs 3 tool rounds — set max_turns = 2 on the “tool_use → end_turn” tab and see the fuse trip on a healthy task.")),
    PlayTab(
        "budget", "max_budget_usd", "runaway",
        "`max_budget_usd` is a spending limit on the card: the run stops when the money does — check the result type before you read any text.",
        "",
        "The Agent SDK also has `max_budget_usd`. When it is hit the run ends with `error_max_budget_usd`, again with no `result` text. "
        "Dollars here use **illustrative rates**, not real pricing (pricing maths is outside the exam) — the mechanism is the lesson: "
        "cost accrues on every call, and later calls cost more because the conversation keeps growing. In this playground the budget is "
        "checked after every model call.",
        "code.claude.com agent-sdk/agent-loop § Turns and budget",
        ("max_budget_usd", "max_turns"), {"max_budget_usd": 0.004, "max_turns": 0}, (_ORDER_MSG,),
        ("Budget 0.004: the run stops after 5 calls with `error_max_budget_usd`.",
         "Set both a budget and max_turns = 2: whichever trips first ends the run — which one was it?",
         "Set both to 0: no guard at all, and the safety net has to stop it.")),
)

# ── Prose ──────────────────────────────────────────────────────────────────────

TLDR = (
    "An agentic loop is the round trip that lets Claude use tools: Claude asks for a tool, **your code runs it**, the "
    "result goes back, and Claude continues. The canonical shape is a loop keyed on `stop_reason` — keep going **while it "
    "is `\"tool_use\"`**. Any other stop reason ends the loop and **your code must handle it**: `end_turn` is the answer, "
    "but `max_tokens` means truncated, `refusal` is a normal HTTP 200 response to retry on a *different* model, and "
    "`pause_turn` means send the paused turn back. The exam names two of these (`tool_use`, `end_turn`); the docs list "
    "seven."
)

MENTAL_MODEL = ("`stop_reason` is the steering wheel — text is just what the model said out loud. And “the loop ended” "
                "is not the same as “the task succeeded”.")

WHAT_IT_IS = """
The docs describe tool use as a **contract**: you say what operations exist, Claude decides when and how to call them,
and **the model never executes anything itself** — it emits a structured request, your code (or Anthropic's servers) runs
it, and the result flows back into the conversation. What makes the loop *agentic* (exam guide, Task Statement 1.1) is that
**the model decides the next action from context** — as opposed to a developer-written decision tree or a pre-set tool
sequence.

**Where the loop runs** — three different layers, all in the docs:

| # | Layer | Who drives the loop | What you handle |
|---|---|---|---|
| 1 | Messages API + client tools (**this lab**) | Your code: a loop keyed on `stop_reason` | Running tools, appending results, every `stop_reason` |
| 2 | Claude Agent SDK / Claude Code | The SDK runs tools and feeds results back for you; you set options (`max_turns`, `max_budget_usd`, allowed tools, hooks) | The final `ResultMessage`: check its `subtype` before reading `result` |
| 3 | Server tools (web search, code execution…) | Anthropic runs its own loop server-side; if it hits its iteration limit the response is `pause_turn` | Continuing a paused turn; a turn may also mix server and client tool calls |

**The seven documented `stop_reason` values** and what a loop does with each:

| # | `stop_reason` | What it means | What your loop does | ⭐ Exam? |
|---|---|---|---|---|
| 1 | `tool_use` | Claude is calling a tool | Run it, send back a `tool_result`, loop | ⭐ **EXAM** — TS 1.1 · Knowledge 1, Skill 1 · p.5 |
| 2 | `end_turn` | Claude finished naturally | Use the response (and check it isn't empty) | ⭐ **EXAM** — TS 1.1 · Knowledge 1, Skill 1 · p.5 |
| 3 | `max_tokens` | Hit your `max_tokens` limit — truncated | Raise `max_tokens` or continue; an incomplete `tool_use` is retried with a higher limit | — |
| 4 | `stop_sequence` | Emitted one of your custom stop sequences | Read the `stop_sequence` field to see which | — |
| 5 | `pause_turn` | A server-tool loop hit its iteration limit | Send the assistant content back as-is to continue | — |
| 6 | `refusal` | Declined by a safety classifier — HTTP 200, **not** an error | Read `stop_details`; retry on a different model | — |
| 7 | `model_context_window_exceeded` | Filled the model's context window (beta per the docs) | Treat the response as truncated | — |

**⭐ Exam focus:** Guide §6 · TS 1.1 (p.5) names only `tool_use` and `end_turn`, plus three anti-patterns (Skill 3). Know those cold. The
rest of the table is what a production loop must also handle — and what the docs' own guidance is built around.
"""

HOW_IT_WORKS = """
1. **Send** the conversation so far, plus the tool definitions.
2. **Inspect** `response.stop_reason`.
3. On `tool_use`, **execute** every `tool_use` block in the response. Claude may request several at once and may also
   include text in the same response.
4. **Append** the assistant turn *and* one user message containing a `tool_result` block for each call (matched by
   `tool_use_id`). Results go **first** in that message; any text may only come after them, and the message must
   immediately follow the assistant's `tool_use` turn. Report a failed tool with `is_error: true` and an *instructive*
   message.
5. **Repeat** from step 1. Every other stop reason leaves the loop — into its own handler (table above).

**How a loop is allowed to end.** With the raw API there is no built-in limit; the docs' own tutorial loop has none. The
Agent SDK offers `max_turns` (counts tool-use turns only) and `max_budget_usd`, both unlimited by default; hitting one
returns an *error result* (`error_max_turns` / `error_max_budget_usd`) without result text. The lesson is the same either
way: a limit is a guard that **fails loudly**, never the way a healthy loop ends.
"""

WHERE_SEEN = """
- **Scenario 1 — Customer Support Resolution Agent** (Guide §5, p.3): the agent decides among `get_customer`, `lookup_order`,
  `process_refund` and `escalate_to_human` based on what each returns. This lab uses the same tool names.
- **Scenario 3 — Multi-Agent Research System** (Guide §5, p.4): a coordinator delegates to specialised subagents; each agent in the system
  is ultimately driven by this same cycle (my reading of the scenario — the guide names the scenario, not the loop).
- **Scenario 4 — Developer Productivity with Claude** (Guide §5, p.4): an agent working through built-in tools (Read, Grep, Glob…) until
  the question is answered.
- **The Agent SDK:** the guide's appendix lists “agentic loops” and “stop_reason handling” under the Claude Agent SDK; the
  SDK docs describe the same loop, run for you, ending in a `ResultMessage`.
- **Tool Runner:** an SDK helper that manages the tool_use loop, result formatting and retries so you don't write it by hand
  — worth knowing exists, but the exam tests the mechanics underneath.
"""

GUIDE_NOTE = (
    "Grounded in the official Claude docs (verified 2026-09-26 — pages listed above) and the exam guide §6 Task Statement 1.1 "
    "(Domain 1 — Agentic Architecture & Orchestration, 27%). Section layout inspired by a community concept list "
    "(claudearchitectcertification.com — community source, unverified; no text copied)."
)

LAB_INTRO = """
Pick a starting point, pick a scenario, **edit the code if you like, and press Run.** The variants are the canonical loop plus
nine ways to get it wrong — five from the exam guide (A–E) and four from the official docs' own pitfalls (F–I). Run each one and
watch where it breaks. Some only break on the right scenario; that is what makes them distractors.
"""

DISTRACTORS = (
    ("A · Stop when the reply says “done”",
     "The model literally announces it is finished.",
     "One response can say “I'm done” and still request a tool; prose is not a control signal.",
     "Branch on `stop_reason`.", "guide:1.1:S3"),
    ("B · Any text block = the final answer",
     "Final answers are text.",
     "Intermediate tool_use turns often carry text too, so you exit on turn 1.",
     "Branch on `stop_reason`, not on what `content` contains.", "guide:1.1:S3"),
    ("C · The iteration cap decides when to stop",
     "It bounds cost and always terminates.",
     "Tasks longer than N are silently cut short and reported as finished; the SDK's own limits return an error result, not a success.",
     "Stop on the model's signal; keep a limit as a guard that raises.", "guide:1.1:S3"),
    ("D · Run the tool, print the result, move on",
     "The tool did run.",
     "The model never sees the result, so it repeats itself.",
     "Append the assistant turn and the `tool_result` message every round.", "guide:1.1:K2"),
    ("E · Hard-code the tool order",
     "Deterministic and simple.",
     "It cannot react to results — it refunds an already-refunded order. Fine only when steps are predictable (TS 1.6).",
     "Let the model choose; enforce must-hold rules with hooks / prerequisite gates (TS 1.4, 1.5).", "guide:1.1:K3"),
    ("F · Anything that isn't tool_use is the final answer",
     "The docs' loop does exit on the first non-tool_use response.",
     "Exiting is only the start: max_tokens is truncated, refusal is empty, pause_turn is unfinished — and none of them raises.",
     "An explicit branch for every documented stop_reason.", "docs"),
    ("G · Retry a refusal on the same model",
     "Retrying usually fixes transient failures.",
     "A refusal is a normal HTTP 200 response, not a transient error; the same model usually refuses again.",
     "Retry on a different model and stay on it; escalate if that refuses too.", "docs"),
    ("H · Add friendly text after the tool results",
     "A nudge should help the model keep going.",
     "Text right after tool results can lead to an empty end_turn response.",
     "Send results with no extra text; add a continuation prompt in a new user message if needed.", "docs"),
    ("I · Explain the results before the tool_result blocks",
     "Context first, data second reads naturally.",
     "tool_result blocks must come first; text before them is a 400 error.",
     "tool_result blocks first, in one user message; any text only after them.", "docs"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Agentic loop", "Single request", "Fixed pipeline (prompt chain)",
                        "Subagent delegation")
SIDE_BY_SIDE_ROWS = (
    ("1", "Who picks the next step", "The model, from context (TS 1.1)", "Nobody — one request, one reply",
     "The developer's pre-set order (TS 1.6)",
     "A coordinator chooses which subagent to invoke; each runs its own loop with isolated context (TS 1.2, 1.3)"),
    ("2", "Ends when", "The model stops asking for tools (`end_turn`); every other stop reason has its own handler",
     "The single reply arrives", "The last fixed step finishes",
     "The coordinator judges coverage sufficient and synthesises (TS 1.2)"),
    ("3", "Best for", "Unpredictable, tool-dependent work", "One-shot transforms with no tools",
     "Predictable multi-aspect work (TS 1.6)", "Broad tasks that split into specialised parts"),
    ("4", "Typical failure", "Steering by prose, a cap, or missing tool results; unhandled stop reasons",
     "Cannot act on the world", "Cannot adapt to what it finds", "Context not passed explicitly to the subagent (TS 1.3)"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.4; ranksep=0.45;
  node [fontname="Helvetica", fontsize=11, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=10, color="#6B7280"];
  Q1 [shape=diamond, label="Is the sequence of steps\\nknown in advance?"];
  FIX [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="Fixed pipeline / prompt chaining\\n(guide TS 1.6)"];
  Q2 [shape=diamond, label="Does what happens next depend\\non what the tools return?"];
  ONE [shape=box, label="Single request\\n(no loop needed)"];
  LOOP [shape=box, fillcolor="#D1FAE5", color="#059669", label="Agentic loop — model-driven\\n(guide TS 1.1, docs: how tool use works)"];
  Q3 [shape=diamond, label="Must some step be GUARANTEED?\\n(e.g. verify identity before a refund)"];
  GATE [shape=box, fillcolor="#FEF3C7", color="#D97706", label="Enforce it in code around the loop:\\nhooks / prerequisite gates (guide TS 1.4, 1.5)"];
  Q1 -> FIX [label="yes"]; Q1 -> Q2 [label="no"];
  Q2 -> LOOP [label="yes"]; Q2 -> ONE [label="no"];
  LOOP -> Q3; Q3 -> GATE [label="yes"];
}'''

EXPERIMENTS = (
    "Run ✅ on `damaged_order`, then switch the scenario to `already_refunded` and run again. Same code, different ending — "
    "who made that decision?",
    "Run ✅ on `refusal`, then ❌ G on the same scenario. Same refusal, opposite outcomes — what did the correct loop do "
    "differently? Read the flowchart.",
    "Run ✅ on `truncated_answer`. Now change the `256` in `model, max_tokens = MODEL, 256` to `1024` and run again: nothing to handle. "
    "Then run ❌ F on `truncated_answer` and read the half-finished answer it accepted.",
    "Run ✅ on `runaway`: your own turn limit fires and the run fails loudly. Then set `MAX_TURNS = 3` and run `long_task`: "
    "still loud. Compare with ❌ C, which fails silently.",
    "In ✅, delete the line that appends the `assistant` turn and run. Read the simulated API error — a `tool_result` needs the "
    "`tool_use` turn before it. Then compare with ❌ D, which appended nothing at all.",
    "Add `print(len(messages))` at the top of each turn and watch the conversation grow by 2 per tool round.",
)

QUESTIONS = (
    Question(
        q=("Your support agent's loop ends the conversation when the assistant's text contains “resolved” or “all set”. "
           "Over a week, 8% of refund conversations close with “Your refund is all set!”, yet no process_refund call "
           "appears in the tool logs. The traces show that each of these responses held a text block followed by a "
           "process_refund tool_use block. What is the most likely root cause?"),
        opts=("The system prompt doesn't tell the model to call process_refund before announcing that a refund is complete.",
              "The loop infers completion from the assistant's wording, not from stop_reason, which was tool_use in these cases.",
              "process_refund is failing silently in these cases, so the model is right but the backend never logs the call.",
              "The model's temperature is set too high, so it announces outcomes before it has finished planning its tool calls."),
        ans=1,
        explain=("These responses ended with stop_reason tool_use: the model asked for the refund and narrated first, which is "
                 "normal. The loop read the text instead of stop_reason, so it exited before running the tool. A blames the "
                 "prompt, but the model did request the tool. C gets the order wrong: the tool never ran, so there was "
                 "nothing to fail. D treats normal text-before-tool behaviour as randomness."),
        scenarios=(1,), points=("1.1:S3",),
    ),
    Question(
        q=("A code-migration agent needs between 2 and 15 tool calls, depending on the repository. Its loop is "
           "`for _ in range(5)`, and it returns the last assistant message when the loop ends. Across 200 runs, 23% "
           "report success but leave the migration half-done, and none of them raise an error. Which change most "
           "effectively fixes this?"),
        opts=("Raise the range to 20, so that even the largest repositories fit within the fixed number of iterations.",
              "Tell the model to print “MIGRATION COMPLETE” when it is done, and end the loop as soon as that phrase appears.",
              "Continue while stop_reason is tool_use and finish on end_turn, keeping any cap only as a guard that raises.",
              "Ask the model to estimate its tool-call count up front, then set the loop's iteration limit from that estimate."),
        ans=2,
        explain=("The loop should be driven by stop_reason: keep going on tool_use, finish on end_turn. A cap can stay as a "
                 "safety guard, but hitting it must surface as an error, never as success. A only moves the silent cut-off. "
                 "B parses prose to decide termination, which is the same anti-pattern. D trusts a self-estimate the model "
                 "has no way to make accurately."),
        scenarios=(4,), points=("1.1:S3", "1.1:S1"),
    ),
    Question(
        q=("After each tool call, your loop runs the tool, writes the result to your monitoring system and sends the next "
           "request with the original messages. In production, 40% of conversations hit the 25-turn guard, and traces "
           "show the agent requesting get_customer with identical arguments on every turn. The tool returns valid data "
           "each time. What is the most likely cause?"),
        opts=("The tool result is never appended to the conversation as a tool_result block, so the model never sees it.",
              "The tool's description is ambiguous, so the model can't tell that get_customer has already answered its query.",
              "The 25-turn guard is too low for these conversations, so the agent runs out of turns before it can progress.",
              "get_customer returns more data than the model can use, so it retries in the hope of getting a shorter answer."),
        ans=0,
        explain=("The model knows only what is in the conversation. A result that is logged but never sent back as a tool_result "
                 "block (matched to the tool_use id) is invisible to it, so it asks again. B would cause wrong tool choices, "
                 "not identical repeats. C: the guard is doing its job here, and raising it just repeats the call more times. "
                 "D invents a retry behaviour."),
        scenarios=(1,), points=("1.1:K2", "1.1:S2"),
    ),
    Question(
        q=("Your loop treats every response whose stop_reason is not tool_use as the final answer and shows its text to "
           "the customer. Support tickets report two problems: about 3% of answers are blank, and about 2% stop "
           "mid-sentence. Nothing is logged as an error. What is the best first fix?"),
        opts=("Increase max_tokens on every request so that no response can ever be cut off before the model finishes.",
              "Add a system-prompt instruction asking the model to always write a complete, non-empty closing message.",
              "Retry any response whose text is shorter than 20 characters, up to three times, before showing it to anyone.",
              "Branch on each stop_reason: end_turn is an answer, max_tokens means truncated, refusal needs another model."),
        ans=3,
        explain=("The docs list seven stop reasons, and each one that exits the loop needs its own handling. The mid-sentence "
                 "answers are max_tokens truncations; the blank ones fit refusals (or empty end_turn). A fixes only the "
                 "truncation. B cannot change how refusals behave. C re-sends identical requests, and a refusal repeats."),
        scenarios=(1,), basis="docs", in_bank=False,
    ),
    Question(
        q=("A support request returns HTTP 200 with stop_reason refusal and no content. Your retry logic re-sends the "
           "identical request to the same model up to three times, and every attempt refuses. The dashboard counts these "
           "as API errors, and 0.4% of conversations end with no reply at all. What should the handler do instead?"),
        opts=("Treat it as a transient error and add exponential backoff between the three retries on the same model.",
              "Retry on a different model and stay on it for the rest of the conversation; escalate if it refuses too.",
              "Rephrase the customer's message automatically and keep resending it to the same model until it gets a response.",
              "Show the customer a generic error and log the request so engineers can review it on the following day."),
        ans=1,
        explain=("A refusal is a normal HTTP 200 response, not an API error. The documented fallback is to retry on a different "
                 "model and stay on it. A treats it as transient, but the same model refuses again. C tries to get around the "
                 "refusal by rewording the customer's request. D gives up without trying the documented fallback."),
        scenarios=(1,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Can one response contain both text and a tool_use block?",
     "Yes — the docs' own example response has a text block followed by a tool_use block, and turn 1 of the lab does exactly "
     "that. It is why text can never be your completion signal; `stop_reason` is authoritative."),
    ("Is a turn limit wrong, then?",
     "No. The Agent SDK offers `max_turns` and `max_budget_usd` precisely to stop runaway loops, and the docs use "
     "`max_turns=30` in their example \"to prevent runaway sessions\". The exam's anti-pattern is an arbitrary cap as the "
     "*primary* stopping mechanism. Note what a limit does in the SDK: it returns an *error result* "
     "(`error_max_turns`), never a success — so a loop should fail loudly too."),
    ("Where do tool results go?",
     "Back into the conversation: keep the assistant turn, then send **one** user message with a `tool_result` block per "
     "`tool_use_id`, results first. The simulated API in the lab rejects messages that break that pairing."),
    ("Why isn't a refusal an exception?",
     "By the docs' design it is a successful HTTP 200 response with `stop_reason: \"refusal\"` — so monitoring built on error "
     "rates never sees it. Check the stop reason, and retry on a different model."),
    ("Do I have to write this loop myself?",
     "Not necessarily. The docs point to Tool Runner (an SDK helper that manages the `tool_use` loop, result formatting and "
     "retries) and, further up, the Claude Agent SDK (which runs the loop for you). The exam still tests the mechanics "
     "underneath."),
    ("Does the simulated model behave exactly like the real API?",
     "No. It is a scripted stand-in that speaks the same shape, so failures are reproducible and free. Real Claude is "
     "non-deterministic; the 🔑 page for Task Statement 1.1 will check the same mechanics against the real API once the key "
     "is bought."),
)

CONTENT = ConceptContent(
    slug="agentic-loops",
    tldr=TLDR,
    mental_model=MENTAL_MODEL,
    what_it_is=WHAT_IT_IS,
    how_it_works=HOW_IT_WORKS,
    where_seen=WHERE_SEEN,
    guide_note=GUIDE_NOTE,
    docs_refs=DOC_REFS,
    docs_verified_on=DOCS_VERIFIED_ON,
    grounding=GROUNDING,
    flow_dot=flow_dot,
    node_states=node_states,
    lab_intro=LAB_INTRO,
    variants=VARIANTS,
    check_outcome=check_outcome,
    distractors=DISTRACTORS,
    side_by_side_headers=SIDE_BY_SIDE_HEADERS,
    side_by_side_rows=SIDE_BY_SIDE_ROWS,
    decision_dot=DECISION_DOT,
    experiments=EXPERIMENTS,
    questions=QUESTIONS,
    faq=FAQ,
    exam_points=EXAM_POINTS,
    playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO,
    related=("stop-reason", "subagents", "session-state", "tool-calling"),
)
