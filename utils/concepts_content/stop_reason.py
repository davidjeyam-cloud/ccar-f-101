"""
D1.3 Stop Reason — stop_reason as the control signal (guide TS 1.1: Knowledge 1, Skills 1 and 3).

GROUNDING (CLAUDE.md, user rule 2026-09-26): written from the OFFICIAL docs fetched and read on 2026-09-26 (DOC_REFS) plus
the exam guide's TS 1.1 (p.5). The guide names only tool_use vs end_turn and two anti-patterns about reading text; the docs
define seven stop reasons, an empty-end_turn pitfall, and the difference between stop reasons and API errors — the page
shows both and marks which is which. Everything is paraphrased; no real exam question is reproduced.

How this page differs from D1.1: D1.1 is the LOOP around the model (repeat, append results, limits). This page is the
DECISION at the top of every iteration: given a response, which stop_reason is it and what exactly do you do?
"""

from utils.concept_types import Claim, ConceptContent, DocRef, ExamPoint, PlayTab, Question, Variant
from utils.flow_style import readable
from utils.stop_lab import EXPECTED

DOCS_VERIFIED_ON = "2026-09-26"
_P = "https://platform.claude.com/docs/en"

DOC_REFS = (
    DocRef("Stop reasons and fallback", f"{_P}/build-with-claude/handling-stop-reasons"),
    DocRef("Refusals and fallback", f"{_P}/build-with-claude/refusals-and-fallback"),
)

GROUNDING = (
    Claim("There are seven stop_reason values: end_turn (finished naturally), max_tokens (hit your limit), stop_sequence (emitted one "
          "of your custom sequences), tool_use (calling a tool), pause_turn (a server-tool loop reached its iteration limit), refusal "
          "(declined for safety-policy reasons) and model_context_window_exceeded (the response filled the context window).",
          "docs", "handling-stop-reasons § Quick Reference Table"),
    Claim("What to do: end_turn — use the response as-is; max_tokens — raise the limit or continue in a new request; stop_sequence — "
          "read the stop_sequence field; tool_use — run the tool and send tool_result blocks back; pause_turn — send the assistant "
          "response back as a new assistant message to continue; refusal — read stop_details and retry on a fallback model; "
          "model_context_window_exceeded — treat the response as truncated.",
          "docs", "handling-stop-reasons § What to do for each stop reason"),
    Claim("Stop reasons come on successful responses (HTTP 200). Errors are HTTP 4xx/5xx, carry error details instead of a "
          "stop_reason, and are caught with the SDK's error types in a try/except.",
          "docs", "handling-stop-reasons § Stop Reasons vs. Errors"),
    Claim("max_tokens: the content holds what was generated before the limit. If the last block is an incomplete tool_use, retry with "
          "a higher max_tokens to get the complete tool call.",
          "docs", "handling-stop-reasons § max_tokens; Handle Incomplete Tool Use at max_tokens"),
    Claim("pause_turn happens when server-side sampling for server tools reaches its iteration limit (default 10). Don't send "
          "tool_result blocks; send the whole assistant response back as a new assistant message, resend the same tools array "
          "(required), and Claude continues.",
          "docs", "handling-stop-reasons § pause_turn; Best Practices"),
    Claim("Empty end_turn: typically 2–3 tokens of nothing. Causes include text right after tool_result blocks and sending Claude's "
          "completed response back unmodified. Don't blindly retry (the model already decided it is done); fix the message "
          "structure; as a last resort add a continuation prompt as a NEW user message.",
          "docs", "handling-stop-reasons § Handle Empty Responses with end_turn"),
    Claim("stop_sequence: the stop sequence text is NOT included in the content; the stop_sequence field (a string) says which one fired.",
          "docs", "handling-stop-reasons § stop_sequence"),
    Claim("model_context_window_exceeded is in beta: the response filled the model's whole context window before reaching max_tokens; "
          "the content is valid but limited by context — treat it as truncated and consider reducing input or summarising earlier messages.",
          "docs", "handling-stop-reasons § model_context_window_exceeded"),
    Claim("A refusal is an HTTP 200 with stop_reason \"refusal\" and (usually) empty content. stop_details holds type, category and "
          "explanation; category and explanation are both null when the refusal maps to no named category (a normal, permanent value); "
          "stop_details is null for every other stop reason. Named categories: cyber, bio, frontier_llm, reasoning_extraction, "
          "general_harms. The explanation text is not stable — display it, don't parse it.",
          "docs", "refusals-and-fallback § What a refusal looks like"),
    Claim("Refusal handling: retry on a DIFFERENT model (the same model usually refuses again) and stay on it for later turns; treat "
          "partial output from a mid-stream refusal as incomplete and discard it; branch on stop_reason (or stop_details.type), not "
          "on content or the inner stop_details fields; instrument refusals as their own signal because monitoring built on "
          "error rates never sees an HTTP 200.",
          "docs", "refusals-and-fallback § Writing the retry yourself; Common pitfalls"),
    Claim("Best practice: always check stop_reason in response handling; handle truncation gracefully (e.g. note that output was cut); "
          "distinguish HTTP errors from stop reasons; never add text after tool_result blocks in the same user message.",
          "docs", "handling-stop-reasons § Best Practices"),
    Claim("The loop lifecycle includes inspecting stop_reason (\"tool_use\" vs \"end_turn\"), executing requested tools and returning results.",
          "guide", "TS 1.1 · Knowledge 1 · p.5"),
    Claim("Loop control continues when stop_reason is \"tool_use\" and terminates when it is \"end_turn\".",
          "guide", "TS 1.1 · Skill 1 · p.5"),
    Claim("Anti-patterns: parsing natural-language signals to decide termination, and checking assistant text content as a completion "
          "indicator.", "guide", "TS 1.1 · Skill 3 · p.5"),
    Claim("The guide names only tool_use and end_turn; the docs list seven stop reasons plus an empty-end_turn pitfall and the "
          "stop-reason-vs-error distinction. Handling the rest is what a production loop needs — and what the docs' guidance is built around.",
          "guide", "TS 1.1 · Knowledge 1 and Skill 1 · p.5, vs handling-stop-reasons"),
    Claim("The action vocabulary (run_tools, raise_max_tokens, retry_other_model, …) and the scenario scripts are this workbench's "
          "labels for the docs' guidance; the simulated model's texts, the cut-off point and the incomplete tool call's arguments "
          "are invented to make each condition reproducible.",
          "simulated", "utils/stop_lab.py; utils/mock_claude.py"),
)

# ── Lab code ───────────────────────────────────────────────────────────────────

_HEADER = r'''from utils.mock_claude import MockClaude      # SIMULATED stand-in. Real SDK: import anthropic
from utils.stop_lab import MAX_TOKENS, MESSAGES, STOP_SEQUENCES, TOOLS, act   # act(...) records the action your handler chose

client = MockClaude()

try:
    response = client.messages.create(model="mock-claude", max_tokens=MAX_TOKENS, tools=TOOLS,
                                      messages=MESSAGES, stop_sequences=STOP_SEQUENCES)
except Exception as error:          # an API ERROR (HTTP 4xx/5xx) is not a stop reason: catch it separately
    act("handle_api_error", error)
    raise SystemExit

print("stop_reason =", response.stop_reason, "| stop_details =", response.stop_details, "| stop_sequence =", response.stop_sequence)
print("content     =", [(b.type, getattr(b, "text", None) or getattr(b, "input", None)) for b in response.content])

'''

_DECIDE = r'''def decide(response):
    reason = response.stop_reason
    if reason == "tool_use":                        # keep going: run the tool(s), send tool_result blocks back
        return "run_tools"
    if reason == "end_turn":                        # finished - but check the content is not EMPTY
        return "finish" if response.content else "continue_new_user_message"
    if reason == "max_tokens":                      # truncated (an incomplete tool_use is retried with a higher limit, never run)
        return "raise_max_tokens"
    if reason == "refusal":                         # HTTP 200, not an error: retry on a DIFFERENT model
        return "retry_other_model"
    if reason == "pause_turn":                      # a server-tool loop paused: send the response back as-is
        return "resume_as_is"
    if reason == "stop_sequence":                   # your tripwire fired: read response.stop_sequence
        return "read_stop_sequence"
    if reason == "model_context_window_exceeded":   # content is valid but truncated
        return "treat_truncated"
    raise RuntimeError(f"unhandled stop_reason: {reason}")   # never assume - fail loudly


act(decide(response), response)
'''

CORRECT = _HEADER + _DECIDE


def _swap(code: str, old: str, new: str) -> str:
    assert old in code, f"lab code changed, cannot apply variant edit: {old[:60]!r}"
    return code.replace(old, new, 1)


_TOP = "def decide(response):\n    reason = response.stop_reason\n"

VARIANT_A = _swap(CORRECT, _TOP, _TOP.replace("    reason = response.stop_reason\n", "") +
                  '    text = "".join(b.text for b in response.content if b.type == "text")\n'
                  '    if "done" in text.lower() or "complete" in text.lower():   # WRONG: reading the model\'s PROSE as a control signal\n'
                  '        return "finish"\n    reason = response.stop_reason\n')
VARIANT_B = _swap(CORRECT, _TOP, "def decide(response):\n"
                  '    if any(b.type == "text" for b in response.content):   # WRONG: "there is text, so it must be the answer"\n'
                  '        return "finish"\n    reason = response.stop_reason\n')
VARIANT_C = _swap(CORRECT, _TOP, "def decide(response):\n"
                  '    if any(b.type == "tool_use" for b in response.content):   # WRONG: looks at the blocks, not at stop_reason\n'
                  '        return "run_tools"\n    reason = response.stop_reason\n')
VARIANT_D = CORRECT[:CORRECT.index("def decide(response):")] + r'''def decide(response):
    if response.stop_reason == "tool_use":
        return "run_tools"
    return "finish"        # WRONG: anything else is "the final answer" - max_tokens, refusal, pause_turn, empty...


act(decide(response), response)
'''
VARIANT_E = _swap(CORRECT, '        return "retry_other_model"',
                  '        return "retry_same_model"   # WRONG: re-sending to the SAME model usually earns another refusal')
VARIANT_F = _swap(CORRECT, '        return "finish" if response.content else "continue_new_user_message"',
                  '        return "finish" if response.content else "retry_same_request"   # WRONG: the model already decided it is done; an identical retry stays empty')
VARIANT_G = _swap(CORRECT, _HEADER[_HEADER.index("try:"):_HEADER.index("print(")],
                  'response = client.messages.create(model="mock-claude", max_tokens=MAX_TOKENS, tools=TOOLS,\n'
                  '                                  messages=MESSAGES, stop_sequences=STOP_SEQUENCES)   # WRONG: no try/except - an API error raises right here\n\n')
VARIANT_H = _swap(CORRECT, '    if reason == "refusal":                         # HTTP 200, not an error: retry on a DIFFERENT model\n        return "retry_other_model"\n',
                  '    details = response.stop_details or {}\n'
                  '    if "declined" in (details.get("explanation") or ""):   # WRONG: the explanation text is not stable and may be null\n'
                  '        return "retry_other_model"\n')

# ── Chart, states, result check ────────────────────────────────────────────────

_CONCEPT = {
    "decide":  ("#EDE9FE", "#7C3AED", "the decision — read stop_reason"),
    "go":      ("#DBEAFE", "#0066CC", "keep going (tool_use, pause_turn)"),
    "finish":  ("#D1FAE5", "#059669", "finish (end_turn, stop_sequence)"),
    "recover": ("#FEF3C7", "#D97706", "recover (max_tokens, refusal, context window, empty)"),
    "error":   ("#E5E7EB", "#6B7280", "an API error — not a stop reason"),
}

_NODES = {
    "CALL":  ("messages.create(…)\\ninside try / except", "box", "decide"),
    "ERR":   ("API error (HTTP 4xx/5xx)\\n→ catch separately\\n(there is no stop_reason)", "box", "error"),
    "INSPECT": ("Read\\nstop_reason", "diamond", "decide"),
    "TOOL":  ("⭐ tool_use\\n→ run the tools,\\nsend tool_result back", "box", "go"),
    "PAUSE": ("pause_turn\\n→ send the response\\nback as-is", "box", "go"),
    "END":   ("⭐ end_turn\\n→ finish (content not empty)", "box", "finish"),
    "SEQ":   ("stop_sequence\\n→ read the stop_sequence field", "box", "finish"),
    "EMPTY": ("end_turn + EMPTY content\\n→ new user message\\n(no blind retry)", "box", "recover"),
    "TRUNC": ("max_tokens\\n→ raise / continue\\n(incomplete tool_use: retry, never run)", "box", "recover"),
    "REF":   ("refusal (HTTP 200)\\n→ retry on a DIFFERENT model", "box", "recover"),
    "CTX":   ("model_context_window_exceeded\\n→ treat as truncated", "box", "recover"),
}
_BRANCHES = ["TOOL", "PAUSE", "END", "SEQ", "EMPTY", "TRUNC", "REF", "CTX"]
_ACTION_NODE = {"run_tools": "TOOL", "finish": "END", "raise_max_tokens": "TRUNC", "retry_other_model": "REF",
                "resume_as_is": "PAUSE", "read_stop_sequence": "SEQ", "treat_truncated": "CTX",
                "continue_new_user_message": "EMPTY", "handle_api_error": "ERR",
                "retry_same_model": "REF", "retry_same_request": "EMPTY"}
_NOT_REACHED = ("#F3F4F6", "#9CA3AF")


def _key(highlighted: bool) -> str:
    rows = "".join(
        f'<TR><TD BGCOLOR="{fill}" WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14"></TD>'
        f'<TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">{text}</FONT></TD></TR>'
        for fill, _l, text in _CONCEPT.values())
    rows += ('<TR><TD WIDTH="18" FIXEDSIZE="TRUE" HEIGHT="14">⭐</TD><TD ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">'
             'named by the exam guide (TS 1.1, p.5)</FONT></TD></TR>')
    if highlighted:
        rows += ('<TR><TD COLSPAN="2" ALIGN="LEFT" BORDER="0"><FONT POINT-SIZE="10">Your run: <B>green</B> = handled as the docs '
                 'say · <B>red</B> = the branch your handler took wrongly · grey = not this response</FONT></TD></TR>')
    return ('  KEY [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="3" CELLPADDING="3">'
            '<TR><TD COLSPAN="2" BORDER="0" ALIGN="LEFT"><B>Key</B></TD></TR>' + rows + '</TABLE>>];')


def flow_dot(states: dict) -> str:
    highlighted = bool(states)
    lines = ["digraph G {", '  rankdir=TB; bgcolor="transparent"; nodesep=0.22; ranksep=0.5; newrank=true;',
             '  node [fontname="Helvetica", fontsize=12, style="rounded,filled", penwidth=2];',
             '  edge [fontname="Helvetica", fontsize=11, color="#6B7280"];']
    for node, (label, shape, concept) in _NODES.items():
        fill, line, _ = _CONCEPT[concept]
        text = label
        if highlighted:
            state, suffix = states.get(node, (None, ""))
            fill = {"ok": "#BBF7D0", "bad": "#FECACA"}.get(state, _NOT_REACHED[0])
            if state is None:
                line = _NOT_REACHED[1]
            if suffix:
                text = f"{label}\\n{suffix}"
        lines.append(f'  {node} [label="{text}", shape={shape}, style="rounded,filled", fillcolor="{fill}", color="{line}"];')
    lines.append('  CALL -> INSPECT [label="HTTP 200"];')
    lines.append('  CALL -> ERR [label="raises", style=dashed];')
    lines += [f"  INSPECT -> {n};" for n in _BRANCHES]
    lines.append("  { rank=same; " + "; ".join(_BRANCHES) + "; }")
    lines.append("  ERR -> KEY [style=invis];")
    lines.append(_key(highlighted))
    lines.append("}")
    return readable("\n".join(lines))   # FLOWCHART RULE: 18pt, max 2 nodes per row


def _facts(trace: dict) -> dict:
    ev = trace["events"]
    calls = [e for e in ev if e["kind"] == "api_call"]
    acts = [e for e in ev if e["kind"] == "action"]
    return {"scenario": trace["status"].get("scenario"), "raised": trace["status"]["raised"], "calls": calls,
            "chosen": acts[-1]["action"] if acts else None}


def node_states(trace) -> dict:
    if not trace:
        return {}
    f = _facts(trace)
    expected = EXPECTED.get(f["scenario"])
    s = {"CALL": ("ok", "")}
    if f["calls"]:
        s["INSPECT"] = ("ok", f["calls"][-1]["stop_reason"])
    chosen_node = _ACTION_NODE.get(f["chosen"])
    exp_node = _ACTION_NODE.get(expected)
    if f["chosen"] == expected:
        s[exp_node] = ("ok", "")
    else:
        if chosen_node:
            s[chosen_node] = ("bad", "your handler took this")
        elif f["chosen"] is None and not f["calls"]:
            s["ERR"] = ("bad", "uncaught — the run crashed")
        elif f["chosen"] is None:
            s["INSPECT"] = ("bad", "no branch for this stop_reason")
        if exp_node and exp_node != chosen_node:
            s[exp_node] = ("ok", "the docs' branch")
    return s


def check_outcome(scenario: str, trace: dict):
    f = _facts(trace)
    expected = EXPECTED[scenario]
    last = f["calls"][-1]["stop_reason"] if f["calls"] else None
    observed = (f"stop_reason seen: {last or 'none (the call raised an API error)'} · your handler chose: "
                f"{f['chosen'] or '— (nothing)'} · the docs call for: {expected} · raised: {f['raised'] or 'no'}")
    return f["chosen"] == expected and not f["raised"], f"the action `{expected}`", observed


# ── What the guide demands (TS 1.1, p.5): only the items about reading stop_reason ──

EXAM_POINTS = (
    ExamPoint("1.1", "K", 1, "The loop lifecycle includes inspecting stop_reason (\"tool_use\" vs \"end_turn\"), running the requested "
              "tools and returning results.", "✅ decide() · flowchart · playground “tool_use”, “end_turn”"),
    ExamPoint("1.1", "S", 1, "Loop control continues on stop_reason \"tool_use\" and ends on \"end_turn\".",
              "✅ · ❌ D (else-branch) · playground “end_turn”"),
    ExamPoint("1.1", "S", 3, "Avoid the anti-patterns of parsing natural-language signals to end the loop and of using assistant text "
              "as the completion indicator.", "❌ A · ❌ B · playground “tool_use”"),
)

# ── Variants ───────────────────────────────────────────────────────────────────

VARIANTS = (
    Variant(
        "correct", "✅ ⭐ Branch on stop_reason (every case handled)", "correct", CORRECT, "sr_tool_use",
        observe=("On sr_tool_use the handler sees stop_reason = tool_use and chooses run_tools — although the reply says “I'm done "
                 "checking”. Now walk the scenario list: each one ends for a different reason and gets a different action, and the "
                 "chart lights up the branch taken. Even the API error (no response at all) is handled, by the try/except."),
        why=("The decision looks at the one field that is the control signal, `stop_reason`, and gives every documented value its own "
             "branch — including the empty end_turn special case — instead of assuming a default. Anything it doesn't know raises."),
    ),
    Variant(
        "A", "⭐❌ A — finish when the reply says “done” / “complete”", "distractor", VARIANT_A, "sr_tool_use",
        observe=("The tool_use response's text says “I'm done checking”. The handler reads that prose first and chooses finish — the "
                 "tool is never run. On the other scenarios the words rarely appear, so it looks fine: only sr_tool_use breaks."),
        why=("Text is what the model said, not why it stopped. One response can announce “done” and still request a tool; the guide "
             "names parsing natural-language completion signals as an anti-pattern."),
        fix="Branch on `response.stop_reason`.",
        source="guide:1.1:S3",
    ),
    Variant(
        "B", "⭐❌ B — any text block means the final answer", "distractor", VARIANT_B, "sr_tool_use",
        observe=("Every response that carries a text block is called “finished”: tool_use with text, max_tokens, max_tokens mid tool "
                 "call, pause_turn, stop_sequence and the context-window stop all choose finish. Only responses WITHOUT text (refusal, "
                 "empty end_turn, the error) reach the correct branches."),
        why=("Non-final responses carry text all the time — a tool request, a truncated answer, a paused turn. Using assistant text as "
             "the completion indicator is another anti-pattern the guide names."),
        fix="Branch on `response.stop_reason`, not on what `content` contains.",
        source="guide:1.1:S3",
    ),
    Variant(
        "C", "❌ C — look for tool_use blocks instead of stop_reason", "distractor", VARIANT_C, "sr_max_tokens_tool",
        observe=("On the normal tool_use scenario this works. On sr_max_tokens_tool the response was cut off in the middle of a tool "
                 "call: stop_reason is max_tokens, but the last block IS a tool_use — with input {'order_id': 'ORD-10'}, missing the "
                 "amount and a truncated id. The handler chooses run_tools and would execute a tool with partial arguments."),
        why=("A tool_use block's presence doesn't mean the call is complete. With stop_reason max_tokens, the docs say to retry with a "
             "higher max_tokens to get the complete tool call."),
        fix="Check `stop_reason` first; on max_tokens raise the limit (or continue) and never run an incomplete tool_use.",
        source="docs",
    ),
    Variant(
        "D", "❌ D — anything that isn't tool_use is the final answer", "distractor", VARIANT_D, "sr_refusal",
        observe=("It gets tool_use and end_turn right — the two values the guide names — and mishandles every other case: max_tokens "
                 "and context-window truncation are shown as finished, a refusal (empty content) becomes an empty “answer”, pause_turn "
                 "is abandoned, a stop_sequence isn't read, and an empty end_turn is treated as finished."),
        why=("The docs' handling table has a different action for each of the seven values (plus the empty end_turn case). An else "
             "branch quietly turns five of them into “done” — and a refusal raises no exception to catch."),
        fix="Give every documented stop_reason its own branch and raise on values you don't handle.",
        source="docs",
    ),
    Variant(
        "E", "❌ E — retry a refusal on the same model", "distractor", VARIANT_E, "sr_refusal",
        observe=("The refusal is detected, but the chosen action is retry_same_model. The chart marks the refusal branch red: the docs "
                 "say re-sending to the same model usually earns another refusal, so the retry is expected to fail again."),
        why="A refusal is a normal response, not a transient fault: backoff and repetition on the same model don't change the outcome.",
        fix="Retry on a DIFFERENT model and stay on it for later turns; escalate if that refuses too.",
        source="docs",
    ),
    Variant(
        "F", "❌ F — blindly retry an empty end_turn", "distractor", VARIANT_F, "sr_empty_end_turn",
        observe=("The response is end_turn with content []. The handler chooses retry_same_request. The docs' point is that this "
                 "stays empty: the model already decided its turn is over."),
        why=("An empty end_turn usually comes from how the conversation was built (for example text right after tool_result blocks). "
             "Retrying the identical request repeats the cause."),
        fix=("Fix the message structure; if it still happens, add a continuation prompt as a NEW user message (a last resort, not a retry)."),
        source="docs",
    ),
    Variant(
        "G", "❌ G — no try/except around the API call", "distractor", VARIANT_G, "sr_api_error",
        observe=("The simulated API returns an overloaded error (HTTP 529). There is no response and no stop_reason — the call raises. "
                 "With no try/except, the script dies right there and the handler never runs. On every other scenario it behaves "
                 "exactly like the correct code."),
        why=("Stop reasons arrive on successful responses; errors are a different channel (HTTP 4xx/5xx with error details, no "
             "stop_reason). A loop that only inspects stop_reason has no answer for a call that never returned."),
        fix="Wrap the call in try/except for the SDK's error types, handled separately from stop_reason.",
        source="docs",
    ),
    Variant(
        "H", "❌ H — decide from the refusal's explanation text", "distractor", VARIANT_H, "sr_refusal",
        observe=("This refusal has stop_details {'type': 'refusal', 'category': None, 'explanation': None}. The handler's check for "
                 "“declined” in the explanation finds nothing to read, no branch takes the refusal, and it raises “unhandled "
                 "stop_reason: refusal”."),
        why=("Per the docs, `category` and `explanation` are both null when a refusal maps to no named category — a normal, permanent "
             "value — and the explanation text isn't stable. Branch on `stop_reason` (or `stop_details.type`)."),
        fix="Branch on `stop_reason == \"refusal\"`; display the explanation to a person instead of parsing it.",
        source="docs",
    ),
)

# ── Prose ──────────────────────────────────────────────────────────────────────

TLDR = (
    "Every model response ends for a **reason**, and that reason — `stop_reason` — is the control signal. It says what the model wants "
    "from you next: **`tool_use`** = run the tool; **`end_turn`** = it finished; **`max_tokens`** = it was cut off; **`refusal`** = it "
    "declined (an HTTP 200, not an error); **`pause_turn`** = give the paused turn back; **`stop_sequence`** = your tripwire fired; "
    "**`model_context_window_exceeded`** = the context window filled. The exam guide names two of them; a production handler needs "
    "all seven — plus the empty `end_turn` case and the difference between a stop reason and an API **error**."
)

MENTAL_MODEL = ("`stop_reason` is the traffic light: it says go (`tool_use`), stop (`end_turn`) or “something needs handling” "
                "(everything else). What the model *said* is just what the driver shouted — never the light.")

WHAT_IT_IS = """
A response from the Messages API carries a `stop_reason` saying why generation stopped. It is the **reliable** signal for what to do
next. The exam guide asks you to inspect it in the loop lifecycle and to branch on `"tool_use"` vs `"end_turn"` (Guide §6 · TS 1.1,
p.5); the official docs define seven values and the right action for each.

**The seven values — one picture and one action each**

| # | `stop_reason` | What it means (docs) | What your code does | 🧭 Mental model | ⭐ Exam |
|---|---|---|---|---|---|
| 1 | `tool_use` | Claude is calling a tool | Run it; send `tool_result` blocks back | A hand raised: “I need something first” — answer, then let them continue. | ⭐ TS 1.1 · Knowledge 1, Skill 1 · p.5 |
| 2 | `end_turn` | Finished naturally | Use it as-is (check it isn't empty) | The speaker sets the microphone down — but check they actually said something. | ⭐ TS 1.1 · Knowledge 1, Skill 1 · p.5 |
| 3 | `max_tokens` | Hit your `max_tokens` | Raise it or continue; an **incomplete `tool_use`** is retried with a higher limit | The answer box ran out of room: a sentence cut mid-word is truncation, not an ending — and a half-written tool call is never run. | — |
| 4 | `refusal` | Declined for safety-policy reasons (HTTP 200) | Read `stop_details`; retry on a **different** model | A locked door, not a dropped call: redialling the same door gets the same answer. | — |
| 5 | `pause_turn` | A server-tool loop hit its iteration limit | Send the assistant response back as-is (keep the tools) | A bookmark: hand the book back exactly as it is. | — |
| 6 | `stop_sequence` | Emitted one of your stop sequences | Read the `stop_sequence` field; the sequence text is not in the content | A tripwire you set: the reply stops right before it and the field says which wire. | — |
| 7 | `model_context_window_exceeded` | Filled the context window (beta) | Treat as truncated — content is valid but limited; trim or summarise | The desk is full: what's written is valid, but there's no room to continue. | — |

**Two cases that aren't a seventh-and-a-half stop reason, but that handlers get wrong**

| # | Case | What happens | What your code does | 🧭 Mental model |
|---|---|---|---|---|
| 8 | `end_turn` with **empty content** | 2–3 tokens of nothing; typically caused by how the conversation was built | Don't blindly retry; fix the structure; last resort: a continuation prompt as a **new user message** | Someone says “I'm done” with nothing in their hands: asking again won't change it — change the question. |
| 9 | An **API error** (HTTP 4xx/5xx) | No response body to inspect: **no `stop_reason`** | Catch it in try/except, separately | A receipt vs a broken till: stop reasons are receipts for completed sales; an error means no sale happened. |

**`stop_details` on a refusal** (docs)

| # | Field | What it holds |
|---|---|---|
| 1 | `type` | `"refusal"` — safe to branch on |
| 2 | `category` | `cyber` · `bio` · `frontier_llm` · `reasoning_extraction` · `general_harms` — or **null** |
| 3 | `explanation` | Human-readable text — **not stable**: display it, don't parse it; may be **null** |
| 4 | *(the object itself)* | `null` for every stop reason other than `refusal` |

**How this differs from D1.1.** D1.1 is the *loop* (repeat, append results, limits). This page is the *decision at the top of every
iteration*: given one response, which value is it and what exactly do you do?
"""

HOW_IT_WORKS = """
1. **Call inside try/except.** An API error is a different channel from a stop reason; catch it separately.
2. **Read `stop_reason` — never the text.** It is present on every successful response.
3. **Dispatch — one branch per value.** Use a table or `match`; end with a branch that raises on anything you didn't expect.
4. **Special-case what looks like success.** `end_turn` with empty content, `max_tokens` with an incomplete `tool_use`, and a `refusal`
   with empty content all *look* like a normal response.
5. **Report truncation honestly.** For `max_tokens` and the context-window stop, say the output was cut short rather than presenting it
   as complete.
6. **Watch refusals as their own signal.** A refusal is an HTTP 200, so error-rate monitoring never sees it.
"""

WHERE_SEEN = """
- **Every agent loop in the guide's scenarios** (for example Scenario 1, the Customer Support Resolution Agent — Guide §5, p.3): the
  loop's next move is always decided by the last response's `stop_reason`.
- **Long or tool-heavy answers:** `max_tokens` (and its incomplete-tool-call variant) appears as soon as a limit is tight.
- **Safety-sensitive requests:** `refusal` and its `stop_details`.
- **Server tools such as web search:** `pause_turn`.
"""

GUIDE_NOTE = (
    "Grounded in the official docs (verified 2026-09-26 — pages listed above) and the exam guide §6 TS 1.1 (p.5), Domain 1 — Agentic "
    "Architecture & Orchestration (27%). The guide names only two stop reasons; the rest of this page is docs-based and is not gold. "
    "Section layout inspired by a community concept list (claudearchitectcertification.com — community source, unverified; no text copied)."
)

LAB_INTRO = """
Each scenario makes ONE simulated model call that ends for a different reason. **You write the handler** — the `decide()` function that
turns a response into an action — pick a starting point and a scenario, edit, and press **Run**. The result check compares your action
with what the official docs call for. The variants are the correct handler plus eight ways to get it wrong: two from the exam guide (⭐)
and six from the docs. Most bugs are invisible on the easy scenarios; walk through all ten to see where each one breaks.
"""

DISTRACTORS = (
    ("A · Finish when the reply says “done”",
     "The model literally says it is finished.",
     "One response can say “done” and still request a tool; prose isn't a control signal.",
     "Branch on `stop_reason`.", "guide:1.1:S3"),
    ("B · Any text block means the final answer",
     "Final answers are text.",
     "Tool requests, truncated answers and paused turns all carry text too.",
     "Branch on `stop_reason`, not on the shape of `content`.", "guide:1.1:S3"),
    ("C · Look for tool_use blocks instead of stop_reason",
     "A tool_use block means there is a tool to run.",
     "With `max_tokens` the block can be incomplete — running it uses partial arguments.",
     "Check `stop_reason` first; retry an incomplete tool call with a higher `max_tokens`.", "docs"),
    ("D · Anything that isn't tool_use is the final answer",
     "It handles the two values the loop needs.",
     "Truncation, refusal, pause_turn, stop_sequence and empty responses all become “done”, and none of them raises.",
     "One branch per documented value; raise on the unknown.", "docs"),
    ("E · Retry a refusal on the same model",
     "Retrying fixes transient failures.",
     "A refusal is a normal response, not a fault; the same model usually refuses again.",
     "Retry on a different model and stay on it.", "docs"),
    ("F · Blindly retry an empty end_turn",
     "An empty response looks like a glitch.",
     "The model already decided its turn is over, so the identical request stays empty.",
     "Fix the message structure; last resort: a continuation prompt as a new user message.", "docs"),
    ("G · No try/except around the call",
     "All the interesting information is in the response.",
     "An API error raises instead of returning a response — there is no stop_reason to read.",
     "Catch API errors separately from stop reasons.", "docs"),
    ("H · Decide from the refusal's explanation text",
     "The explanation says what happened.",
     "It can be null and its text isn't stable — the branch never fires.",
     "Branch on `stop_reason`; display the explanation, don't parse it.", "docs"),
)

SIDE_BY_SIDE_HEADERS = ("#", "Aspect", "Branch on stop_reason", "Read the reply text", "Look at content blocks", "Else = final answer")
SIDE_BY_SIDE_ROWS = (
    ("1", "What it inspects", "The one control field", "What the model said", "Which blocks are present", "Only “is it tool_use?”"),
    ("2", "tool_use + a text block", "Runs the tool", "May finish early (“done”)", "Runs the tool", "Runs the tool"),
    ("3", "max_tokens (cut mid tool call)", "Raises the limit, never runs it", "Depends on the words", "Runs an incomplete tool call", "Shows truncated text as final"),
    ("4", "refusal (empty content)", "Retries on a different model", "Nothing to read", "Nothing to run → maybe “done”", "Shows an empty answer"),
    ("5", "Typical failure", "— (if every value has a branch)", "Fooled by narration", "Fooled by truncation", "Silent on 5 of 7 values"),
)

DECISION_DOT = '''digraph D {
  rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.4;
  node [fontname="Helvetica", fontsize=11, style="rounded,filled", fillcolor="#F3F4F6", color="#9CA3AF", penwidth=1.5];
  edge [fontname="Helvetica", fontsize=10, color="#6B7280"];
  E1 [shape=diamond, label="Did the call raise?"];
  ERR [shape=box, fillcolor="#E5E7EB", color="#6B7280", label="API error: catch it separately\\n(no stop_reason exists)"];
  R [shape=diamond, label="stop_reason ?"];
  TU [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="tool_use: run tools,\\nsend tool_result back"];
  ET [shape=diamond, label="end_turn: is content empty?"];
  FIN [shape=box, fillcolor="#D1FAE5", color="#059669", label="finish"];
  CONT [shape=box, fillcolor="#FEF3C7", color="#D97706", label="new user message\\n(no blind retry)"];
  MT [shape=diamond, label="max_tokens: is the last block\\nan incomplete tool_use?"];
  UP [shape=box, fillcolor="#FEF3C7", color="#D97706", label="retry with a higher max_tokens;\\nnever run it"];
  RAISE [shape=box, fillcolor="#FEF3C7", color="#D97706", label="raise max_tokens\\nor continue"];
  REF [shape=box, fillcolor="#FEF3C7", color="#D97706", label="refusal: retry on a\\nDIFFERENT model"];
  PT [shape=box, fillcolor="#DBEAFE", color="#0066CC", label="pause_turn: send back\\nas-is, keep tools"];
  SS [shape=box, fillcolor="#D1FAE5", color="#059669", label="stop_sequence: read\\nthe stop_sequence field"];
  CW [shape=box, fillcolor="#FEF3C7", color="#D97706", label="context window: treat as\\ntruncated; trim / summarise"];
  E1 -> ERR [label="yes"]; E1 -> R [label="no"];
  R -> TU; R -> ET; R -> MT; R -> REF; R -> PT; R -> SS; R -> CW;
  ET -> CONT [label="yes"]; ET -> FIN [label="no"];
  MT -> UP [label="yes"]; MT -> RAISE [label="no"];
}'''

EXPERIMENTS = (
    "Run ✅ on every scenario in turn and watch the chart: a different branch lights up each time, and the API error is caught rather than "
    "crashing.",
    "Run ⭐❌ A on sr_tool_use, then on sr_end_turn. Same code — why does it only break on one?",
    "Run ⭐❌ B across all scenarios and count how many it gets right. Which ones does it get right for the wrong reason?",
    "Run ❌ C on sr_tool_use (fine) and sr_max_tokens_tool (not). Read the incomplete tool call in the output.",
    "Run ❌ D on every scenario: it is right on the two values the guide names (and on the API error, which its try/except still catches) and wrong on the other seven — and none of those raises.",
    "In ✅, delete the `raise RuntimeError(...)` line and add a scenario your decide() doesn't know: what does the run do now?",
)

QUESTIONS = (
    Question(
        q=("Mid-conversation, your support agent returns a response with stop_reason “tool_use”. Its content is a text "
           "block (“Everything checks out, your refund is on its way!”) followed by a process_refund tool_use block. "
           "What should your loop do with this response?"),
        opts=("Show the text to the customer and end the conversation, since the model says the refund is done.",
              "Show the text, skip the tool call, and ask the customer to confirm the refund first.",
              "Treat it as an error, because a tool_use response shouldn't contain text.",
              "Run process_refund, send its result back as a tool_result, and keep looping."),
        ans=3,
        explain=("stop_reason is the control signal: “tool_use” means run the requested tool, return the result, and "
                 "continue. The text is just what the model said out loud. The refund hasn't happened until your code "
                 "runs the tool."),
        scenarios=(1,), points=("1.1:K1", "1.1:S1"),
    ),
    Question(
        q=("A team's loop decides the agent is finished whenever a response contains a text block. Order lookups often "
           "end early with “Let me check that order for you…”, and nothing more happens. Why?"),
        opts=("Text is often sent together with a tool_use block, so the loop stops before running the tool it just asked for.",
              "The model is producing text because the tools are described poorly.",
              "The loop needs a higher max_tokens so the model can finish its sentence.",
              "The customer's message is too vague for the model to call a tool."),
        ans=0,
        explain=("Treating assistant text as the completion signal is a named anti-pattern. A response can carry text "
                 "and a tool_use block together, with stop_reason “tool_use”. Branch on stop_reason, not on whether "
                 "text is present."),
        scenarios=(1,), points=("1.1:S3",),
    ),
    Question(
        q=("To make the support agent “predictable”, a team hard-codes every request to run get_customer → lookup_order "
           "→ process_refund in that order. Billing disputes and account questions, which need different tools or no "
           "refund at all, now fail or trigger wrong refunds. What's the better design?"),
        opts=("Add more fixed sequences, one for each request type, chosen by keyword.",
              "Remove process_refund from the tool list and handle refunds manually.",
              "Let the model choose the next tool from context; enforce only true prerequisites (like verification before refunds) in code.",
              "Ask the model to say in text which sequence it wants, then run that sequence."),
        ans=2,
        explain=("The guide contrasts model-driven decisions, where Claude picks the next tool from context, with "
                 "pre-set decision trees. Hard prerequisites belong in programmatic gates (TS 1.4). Keyword-chosen "
                 "sequences and parsed text keep the brittleness."),
        scenarios=(1,), points=("1.1:K3", "1.4:K1"),
    ),
    Question(
        q=("A codebase-exploration agent requests Grep, your code runs it, and then you send the next request "
           "containing only the developer's follow-up question. The agent keeps asking for the same Grep again and "
           "again. What's the root cause?"),
        opts=("Grep is the wrong tool; the agent should be using Glob.",
              "The tool result never went back into the conversation, so the model can't see it and asks again.",
              "The loop should end after the first tool call to stop the repetition.",
              "The model needs a system prompt instruction not to repeat tool calls."),
        ans=1,
        explain=("Each iteration returns the tool results to the conversation so the model can reason about its next "
                 "action. Without them, from the model's point of view the tool never ran. Capping calls or adding "
                 "prompt rules hides the bug."),
        scenarios=(4,), points=("1.1:K1", "1.1:K2"),
    ),
    Question(
        q=("An extraction call returns stop_reason “max_tokens”. Its last content block is a tool_use for save_invoice "
           "whose input JSON is cut off halfway. What should the handler do?"),
        opts=("Run save_invoice with whatever fields arrived.",
              "Treat it as the final answer and move to the next document.",
              "Retry the request with a higher max_tokens instead of running the incomplete tool call.",
              "Ask the model in a new user message to finish the JSON."),
        ans=2,
        explain=("Per the docs, max_tokens means the response was truncated. An incomplete tool_use block should be "
                 "retried with a higher limit rather than executed with partial input."),
        scenarios=(6,), basis="docs", in_bank=False,
    ),
    Question(
        q=("During a traffic spike your support agent's API call raises an overloaded error. The handler, which only "
           "branches on stop_reason, crashes, and the customer sees a blank page. What's missing?"),
        opts=("Error handling around the API call itself; an API error isn't a stop_reason and never returns a response to branch on.",
              "A branch for stop_reason “error”.",
              "A higher max_tokens, so responses finish before the spike.",
              "Streaming, so the partial response is shown."),
        ans=0,
        explain=("stop_reason only exists on a successful response. API errors surface as exceptions or HTTP errors and "
                 "need their own handling, such as retrying with backoff for transient errors. There is no “error” stop reason."),
        scenarios=(1,), basis="docs", in_bank=False,
    ),
    Question(
        q=("After each tool round, a developer appends “Please continue.” after the tool_result blocks. The model now "
           "sometimes returns end_turn with empty content, and retrying the same request gives the same result. What's "
           "the best fix?"),
        opts=("Retry up to five times, since the empty reply is transient.",
              "Treat the empty reply as a successful final answer.",
              "Move “Please continue.” before the tool results instead.",
              "Send tool results on their own, with no added text after them, in the user message."),
        ans=3,
        explain=("The docs name text added after tool results as a cause of empty end_turn responses. Blind retries "
                 "repeat it, and putting text before the tool_result blocks is an error. Send the results on their own."),
        scenarios=(1,), basis="docs", in_bank=False,
    ),
    Question(
        q=("A synthesis step over many long sources returns stop_reason “model_context_window_exceeded”. The pipeline "
           "currently publishes whatever text came back. What should it do instead?"),
        opts=("Publish it, since any non-tool_use stop means the model finished.",
              "Treat it as truncated: reduce or trim the context, then continue.",
              "Retry the identical request on the same model.",
              "Switch to the Batch API, which has no context limit."),
        ans=1,
        explain=("Every stop reason other than tool_use exits the loop but must be handled. This one means the response was truncated because the context "
                 "window filled. Batch requests have the same context limits."),
        scenarios=(3,), basis="docs", in_bank=False,
    ),
)


FAQ = (
    ("Doesn't D1.1 already cover stop reasons?",
     "D1.1 is the loop around the model — repeating, appending results, limits. It shows the seven values inside a working loop. This page "
     "isolates the *decision*: given one response, which value is it and what exactly is the action. The playground here lets you feed each "
     "condition to different handlers one at a time."),
    ("Do I need all seven on the exam?",
     "The guide (TS 1.1, p.5) names `tool_use` and `end_turn` and two text-reading anti-patterns. The other five plus the empty-end_turn and "
     "error distinctions come from the official docs — worth knowing for real code, but they're not gold on this page."),
    ("Is a refusal an error?",
     "No. It's an HTTP 200 response with `stop_reason: \"refusal\"`, usually empty content and a `stop_details` object. Nothing is raised, so "
     "you have to look for it. Retry on a different model and stay on it."),
    ("Is `model_context_window_exceeded` always available?",
     "The docs mark it as beta (use the beta client; older models may need a beta header). Treat it as truncation when you see it."),
    ("What do I do about `pause_turn`?",
     "Send the assistant response back as a new assistant message — no tool_result blocks — and resend the same tools array; Claude continues "
     "where it paused. D1.1's playground has a pause_turn tab inside a loop."),
    ("Is the simulated model like the real one?",
     "No — it's scripted so each condition is reproducible. The response shapes and the expected actions come from the docs; real Claude is "
     "non-deterministic."),
)

# ── Agent playground: the stop-reason inspector (one tab per sub-concept) ───────

_ORDER = "Customer alice@example.com says order ORD-1001 arrived damaged. Please resolve it."

PLAYGROUND_INTRO = """
Pick a **sub-concept tab**, type a message, choose **how your handler decides** — the correct branch-on-`stop_reason` handler, or one of
the distractor policies — and press Send. You'll see the request, the **raw response** (`stop_reason`, `stop_details`, content blocks,
tokens), the action your handler chose, the action the docs call for, and why it matters. The scripted model always answers about the same
order; the tab decides *why* the response stops.
"""


def _tab(key, label, sid, mental, exam, meaning, docs, knobs, defaults, examples, try_this):
    return PlayTab(key, label, sid, mental, exam, meaning, docs, knobs, defaults, examples, try_this, engine="stop")


PLAYGROUND = (
    _tab("tool_use", "⭐ tool_use", "sr_tool_use",
         "A hand raised: “I need something first” — answer it, then let them continue.", "guide:1.1:K1",
         "`tool_use` means Claude is calling a tool and waits for the result. Run it and send back a `tool_result`. Note the response "
         "carries text (“I'm done checking…”) **and** a tool call: the text is narration, the `stop_reason` is the signal.",
         "handling-stop-reasons § tool_use; guide TS 1.1 Knowledge 1, Skill 3",
         ("handler",), {"handler": "correct"}, (_ORDER,),
         ("“branch on stop_reason” chooses run_tools.",
          "“finish when the reply says done” and “any text block means the final answer” both choose finish — the tool never runs.",
          "“anything that isn't tool_use…” gets this one right — which is why that bug hides.")),
    _tab("end_turn", "⭐ end_turn", "sr_end_turn",
         "The speaker sets the microphone down — the answer is complete, so use it.", "guide:1.1:S1",
         "`end_turn` means Claude finished naturally — use the response as-is. Every handler gets this one right, which is exactly why a "
         "loop that only knows tool_use and end_turn seems to work until another stop reason shows up.",
         "handling-stop-reasons § end_turn; guide TS 1.1 Skill 1",
         ("handler",), {"handler": "correct"}, (_ORDER,),
         ("Try every handler: they all choose finish.",
          "Then go to the max_tokens, refusal and pause_turn tabs and repeat with “anything that isn't tool_use…”.")),
    _tab("max_tokens", "max_tokens", "sr_max_tokens",
         "The answer box ran out of room: a sentence cut mid-word is truncation, not an ending — and a half-written tool call is never run.", "",
         "`max_tokens` means the response reached YOUR limit: the content is what was generated before it. Raise the limit or continue in a "
         "new request. If the last block is an **incomplete `tool_use`**, retry with a higher `max_tokens` to get the whole call — never "
         "run it. Here the final answer needs about 300 (simulated) tokens.",
         "handling-stop-reasons § max_tokens; Handle Incomplete Tool Use at max_tokens",
         ("handler", "max_tokens", "mid_tool_call"), {"handler": "correct", "max_tokens": 60, "mid_tool_call": "no"}, (_ORDER,),
         ("Default (limit 60): the text is cut off; the correct handler chooses raise_max_tokens.",
          "“anything that isn't tool_use…” and “any text block…” both call the truncated text finished.",
          "Set max_tokens to 400: it fits, so the response is a normal end_turn and every handler finishes.",
          "Set “mid tool call” to yes: the last block is a tool_use with input {'order_id': 'ORD-10'} — incomplete. “look for tool_use blocks” chooses run_tools.")),
    _tab("refusal", "refusal", "sr_refusal",
         "A locked door, not a dropped call: redialling the same door gets the same answer — try another door (model).", "",
         "A refusal is an **HTTP 200** with `stop_reason: \"refusal\"`, usually empty content, and a `stop_details` object. Here its "
         "`category` and `explanation` are both **null** — a normal value. Retry on a **different** model and stay on it; branch on "
         "`stop_reason`, not on the explanation text. Nothing raises, so error-rate monitoring never sees it.",
         "refusals-and-fallback § What a refusal looks like; Writing the retry yourself; Common pitfalls",
         ("handler",), {"handler": "correct"}, (_ORDER,),
         ("“branch on stop_reason” → retry_other_model.",
          "“retry a refusal on the SAME model” → retry_same_model, which the docs say usually refuses again.",
          "“decide from the refusal's explanation text” → unhandled: the explanation is null, so its check never fires.",
          "“anything that isn't tool_use…” → finish, with an EMPTY answer and no error.")),
    _tab("pause_turn", "pause_turn", "sr_pause_turn",
         "A bookmark: the server-side work isn't finished — hand the book back exactly as it is.", "",
         "`pause_turn` means a server-side tool loop (like web search) reached its iteration limit (default 10). Don't send `tool_result` "
         "blocks: send the whole assistant response back as a new assistant message and resend the same tools array; Claude continues.",
         "handling-stop-reasons § pause_turn; Best Practices",
         ("handler",), {"handler": "correct"}, (_ORDER,),
         ("“branch on stop_reason” → resume_as_is.",
          "“any text block…” and “anything that isn't tool_use…” treat the paused, unfinished turn as final.")),
    _tab("stop_sequence", "stop_sequence", "sr_stop_sequence",
         "A tripwire you set: the reply stops right before it, and the stop_sequence field tells you which wire.", "",
         "If you pass stop sequences and the model emits one, generation halts and `stop_reason` is `stop_sequence`. The sequence text is "
         "**not included** in the content; the `stop_sequence` field says which one fired.",
         "handling-stop-reasons § stop_sequence",
         ("handler", "stop_sequences"), {"handler": "correct", "stop_sequences": "END_REPORT"}, (_ORDER,),
         ("Default tripwire END_REPORT: the content ends “…ORD-1001. ” — the tripwire text is not in it — and stop_sequence = 'END_REPORT'.",
          "Change the tripwire to a word that never appears (“zebra”): a normal end_turn.",
          "Clear the box: no tripwire, a normal end_turn.")),
    _tab("context", "context window", "sr_context_window",
         "The desk is full: what's written is valid, but there's no room to continue.", "",
         "`model_context_window_exceeded` (beta in the docs) means the response filled the model's whole context window before `max_tokens`. "
         "The content is valid but limited: treat it as truncated, and consider reducing input or summarising earlier messages.",
         "handling-stop-reasons § model_context_window_exceeded",
         ("handler",), {"handler": "correct"}, (_ORDER,),
         ("“branch on stop_reason” → treat_truncated.",
          "“any text block…” and “anything that isn't tool_use…” show a sentence cut off mid-word as the finished answer.")),
    _tab("empty", "empty end_turn", "sr_empty_end_turn",
         "Someone says “I'm done” with nothing in their hands: asking the same question again won't change it — change the question.", "",
         "An `end_turn` with an empty `content` list is a docs-listed pitfall (often caused by text right after tool_result blocks). The "
         "model already decided its turn is over, so a blind retry stays empty. Fix the message structure; as a last resort add a "
         "continuation prompt as a **new user message**.",
         "handling-stop-reasons § Handle Empty Responses with end_turn",
         ("handler",), {"handler": "correct"}, (_ORDER,),
         ("“branch on stop_reason” notices the empty content → continue_new_user_message.",
          "“blindly retry an empty end_turn” → retry_same_request.",
          "“anything that isn't tool_use…” → finish, showing an empty answer.")),
    _tab("errors", "stop_reason vs errors", "sr_api_error",
         "A receipt vs a broken till: stop reasons are receipts for completed sales; an error means no sale happened.", "",
         "Stop reasons arrive on successful responses (HTTP 200). An **API error** (HTTP 4xx/5xx) carries error details instead and has **no "
         "`stop_reason`** — you catch it with try/except, separately. Here the simulated API is overloaded (a 529).",
         "handling-stop-reasons § Stop Reasons vs. Errors",
         ("handler",), {"handler": "correct"}, (_ORDER,),
         ("“branch on stop_reason” (with a try/except) → handle_api_error.",
          "“no try/except around the API call” → the run crashes; every other policy here assumes the call is wrapped.")),
)

DECISION_DOT = readable(DECISION_DOT)   # FLOWCHART RULE: 18pt, max 2 nodes per row

CONTENT = ConceptContent(
    slug="stop-reason",
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
    related=("agentic-loops", "subagents", "escalation"),
    exam_points=EXAM_POINTS,
    playground=PLAYGROUND,
    playground_intro=PLAYGROUND_INTRO,
    scenarios=tuple(EXPECTED),
    show_ledger=False,
)
