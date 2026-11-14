"""
The agent PLAYGROUND engine — the "type a message and watch how the agent handles it" box on a concept page.

Unlike the code lab (the learner's own Python, run in a separate process), this is TRUSTED workbench code
that runs in the Streamlit process: a docs-shaped agent loop whose *developer-side constraints* the learner
sets with knobs — max_tokens, max_turns, a spending limit, how a refusal / pause_turn / max_tokens is
handled — against the SIMULATED model (utils/mock_claude.py). Everything the "model" says is scripted and
labelled SIMULATED on screen.

Grounding (official docs, fetched 2026-09-26; see agentic_loops.py DOC_REFS):
- the seven stop_reason values and how to handle each ...... build-with-claude/handling-stop-reasons
- refusal = HTTP 200; retry on a DIFFERENT model .............. build-with-claude/refusals-and-fallback
- max_turns (counts tool-use turns only), max_budget_usd and the result subtypes error_max_turns /
  error_max_budget_usd / error_during_execution ............... code.claude.com/docs/en/agent-sdk/agent-loop
Result labels that are NOT SDK subtypes are prefixed "playground:" so they are never mistaken for the SDK's.
What is invented (simulation, not docs): the scripted replies, the token sizes, the illustrative price
rates below, the simulated context-window number, and *when* the budget is checked (after every model call).
"""

from __future__ import annotations

from dataclasses import dataclass

from utils import lab_trace, mock_claude as mc, tools
from utils.mock_claude import Ctx, Scenario, Turn

# Illustrative rates ONLY, so a "budget" has something to count. NOT real pricing (pricing maths is out of
# scope for the exam); the mechanism — a spend cap that ends the run with an error result — is what is taught.
IN_RATE_PER_1K = 0.003
OUT_RATE_PER_1K = 0.015

MAX_LOOP_ITERATIONS = 25          # the playground's own safety net (separate from the knobs below)
_ORDER_WORDS = ("order", "refund", "damaged", "broken", "return", "ord-", "package", "arrived")

CONDITIONS = ("none", "long_answer", "refusal", "pause", "runaway")


@dataclass
class PlayConfig:
    condition: str = "none"             # which simulated behaviour the model shows (see CONDITIONS)
    max_tokens: int = 1024              # per request — the API parameter
    max_turns: int = 0                  # 0 = no limit (the SDK default); counts tool-use turns only
    max_budget_usd: float = 0.0         # 0 = no limit (the SDK default)
    refusal_policy: str = "different_model"   # "different_model" (docs) | "same_model" | "stop"
    max_tokens_policy: str = "raise"          # "raise" (handle it) | "surface" (report it as a result)
    pause_policy: str = "resume"              # "resume" (send back as-is) | "treat_as_final" (a bug)
    stop_sequences: tuple = ()
    context_window: int = 0             # 0 = unlimited; otherwise a SIMULATED window size in tokens


def wants_order(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in _ORDER_WORDS)


def _wrap(base, condition: str):
    def behavior(seen, ctx: Ctx) -> Turn:
        if condition == "refusal" and ctx.model == mc.PRIMARY_MODEL:
            return Turn(refusal={"type": "refusal", "category": "general_harms",
                                 "explanation": "This request was declined under a usage-policy area."})
        if condition == "pause" and not seen and not ctx.resumed:
            return Turn(text="Let me check the carrier's damage-claim policy online first.",
                        pause=("web_search", {"query": "carrier damage claim policy"}))
        if condition == "runaway":
            return mc._runaway(seen, ctx)
        turn = base(seen, ctx)
        if condition == "long_answer" and turn.final and len(seen) >= 3:
            turn.final = mc._LONG_FINAL
        return turn
    return behavior


def build_scenario(condition: str, intent: bool) -> Scenario:
    base = mc._support_flow if intent else mc._chitchat
    return Scenario("playground", "Agent playground", "", "DELIVERED", _wrap(base, condition),
                    final_tokens=300 if condition == "long_answer" else None)


def _text_of(blocks) -> str:
    return "".join(b["text"] for b in blocks if b["type"] == "text")


def run_agent(user_text: str, cfg: PlayConfig) -> dict:
    """Run one agent query and return {'events': [...], 'result': {...}} for the UI."""
    lab_trace.reset()
    mc.reset()
    tools.configure("DELIVERED")

    intent = wants_order(user_text)
    client = mc.MockClaude(build_scenario(cfg.condition, intent), context_window=cfg.context_window or None)
    messages = [{"role": "user", "content": user_text}]
    events: list[dict] = [{"type": "user", "text": user_text, "intent": intent}]

    model, max_tokens = mc.PRIMARY_MODEL, cfg.max_tokens
    tool_turns = calls = doublings = same_model_refusals = 0
    spent = 0.0
    last_text = ""

    def finish(subtype: str, text: str, why: str, source: str) -> dict:
        return {"events": events, "result": {
            "subtype": subtype, "text": text, "why": why, "source": source, "api_calls": calls,
            "tool_turns": tool_turns, "spent": round(spent, 6), "ok": subtype == "success"}}

    for _ in range(MAX_LOOP_ITERATIONS):
        try:
            response = client.messages.create(
                model=model, max_tokens=max_tokens, tools=tools.TOOL_SCHEMAS, messages=messages,
                stop_sequences=list(cfg.stop_sequences) or None)
        except (mc.MockAPIError, mc.RunawayGuard) as e:
            return finish("error_during_execution", last_text, f"{type(e).__name__}: {e}", "sdk")

        calls += 1
        api = lab_trace.EVENTS[-1]
        cost = api["input_tokens"] / 1000 * IN_RATE_PER_1K + api["output_tokens"] / 1000 * OUT_RATE_PER_1K
        spent += cost
        reason = response.stop_reason
        blocks = api["blocks"]
        text = _text_of(blocks)
        last_text = text or last_text
        ev = {"type": "api", "call": calls, "model": model, "max_tokens": max_tokens, "stop_reason": reason,
              "stop_details": api["stop_details"], "stop_sequence": api["stop_sequence"], "blocks": blocks,
              "in": api["input_tokens"], "out": api["output_tokens"], "cost": round(cost, 6),
              "spent": round(spent, 6), "action": ""}
        events.append(ev)

        if cfg.max_budget_usd and spent > cfg.max_budget_usd:
            ev["action"] = "spend passed max_budget_usd → run stopped"
            return finish("error_max_budget_usd", last_text,
                          f"Simulated spend ${spent:.4f} passed the ${cfg.max_budget_usd:.4f} budget. The SDK reports "
                          "this as an error result; there is no final answer to trust.", "sdk")

        if reason == "tool_use":
            if cfg.max_turns and tool_turns >= cfg.max_turns:
                ev["action"] = f"wants another tool round but max_turns={cfg.max_turns} is used up → run stopped"
                return finish("error_max_turns", last_text,
                              f"The agent asked for tool round {tool_turns + 1} but max_turns={cfg.max_turns}. "
                              "max_turns counts tool-use turns; hitting it is an error result, never a success.", "sdk")
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for b in response.content:
                if b.type == "tool_use":
                    out = tools.execute_tool(b.name, b.input)
                    events.append({"type": "tool", "name": b.name, "args": b.input, "result": out})
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
            messages.append({"role": "user", "content": results})
            tool_turns += 1
            ev["action"] = f"ran {len(results)} tool(s), appended the assistant turn + one tool_result message, loop again"
            continue

        if reason == "end_turn":
            if not response.content:
                ev["action"] = "end_turn but the content is EMPTY → nothing to show"
                return finish("playground:empty_end_turn", "", "end_turn with no content. The docs list causes such as "
                              "text added right after tool results; don't just retry blindly.", "playground")
            ev["action"] = "end_turn → this is the final answer"
            return finish("success", text, "The model finished on its own signal (end_turn).", "sdk")

        if reason == "max_tokens":
            if cfg.max_tokens_policy == "raise" and doublings < 3:
                doublings += 1
                ev["action"] = f"truncated → raise max_tokens {max_tokens} → {max_tokens * 2} and ask again"
                max_tokens *= 2
                continue
            ev["action"] = "truncated → reported as a result (not shown as a final answer)"
            return finish("playground:max_tokens", text, "Stopped at the max_tokens limit — the text above is cut off. "
                          "Raise max_tokens or continue the response; do not present this as complete.", "playground")

        if reason == "refusal":
            if cfg.refusal_policy == "stop":
                ev["action"] = "refusal → run stopped (no retry)"
                return finish("playground:refusal", "", "The model declined (HTTP 200, not an error). Nothing was retried.",
                              "playground")
            if cfg.refusal_policy == "same_model":
                same_model_refusals += 1
                if same_model_refusals >= 3:
                    ev["action"] = "refused 3 times on the SAME model → gave up"
                    return finish("playground:refusal", "", "Retrying the same model refused every time — the docs say "
                                  "it usually will. Switch to a different model.", "playground")
                ev["action"] = f"refusal → retry the same model (attempt {same_model_refusals + 1})"
                continue
            if model == mc.FALLBACK_MODEL:
                ev["action"] = "the fallback model refused too → escalate"
                return finish("playground:refusal", "", "Both models declined — escalate to a human.", "playground")
            model = mc.FALLBACK_MODEL
            ev["action"] = f"refusal → retry on a DIFFERENT model ({model}) and stay on it"
            continue

        if reason == "pause_turn":
            if cfg.pause_policy == "treat_as_final":
                ev["action"] = "pause_turn treated as the end → unfinished work shown as the answer"
                return finish("playground:pause_turn_ignored", text, "A paused server-tool turn is unfinished work; "
                              "the docs say to send it back as-is to continue.", "playground")
            messages.append({"role": "assistant", "content": response.content})
            ev["action"] = "pause_turn → sent the assistant content back as-is to continue"
            continue

        if reason == "stop_sequence":
            ev["action"] = f"stop_sequence {api['stop_sequence']!r} hit → generation halted there"
            return finish("success", text, f"Halted by your stop sequence {api['stop_sequence']!r}, not by end_turn. "
                          "Read the stop_sequence field to know which one.", "sdk")

        if reason == "model_context_window_exceeded":
            ev["action"] = "context window full → cannot continue"
            return finish("playground:context_window", last_text, "The conversation no longer fits the (simulated) "
                          "context window. The docs say to treat the response as truncated. Trim, summarise or start "
                          "a new session.", "playground")

        ev["action"] = f"unhandled stop_reason {reason!r}"
        return finish("error_during_execution", last_text, f"unhandled stop_reason {reason!r}", "sdk")

    return finish("playground:safety_net", last_text, f"No limit of yours stopped this run, so the playground's own "
                  f"{MAX_LOOP_ITERATIONS}-iteration safety net did. A real loop with no limits would keep spending.",
                  "playground")
