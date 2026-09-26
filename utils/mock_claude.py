"""
SIMULATED Claude — a scripted stand-in that speaks the Claude Messages-API
*shape*, so a lab's code reads exactly like real SDK code:

    response = client.messages.create(model=..., max_tokens=..., tools=..., messages=...)
    response.stop_reason    # "end_turn" | "tool_use" | "max_tokens" | "pause_turn" | "refusal" | ...
    response.content        # blocks with .type == "text" | "tool_use" | "server_tool_use"
    response.stop_details   # None, except on a refusal
    {"type": "tool_result", "tool_use_id": ..., "content": ...}   # sent back in a USER message

Everything here is SIMULATED and must always be labelled so on screen
(CLAUDE.md: never present simulated output as a real model response).
What it is for: deterministic, free, offline labs that reproduce the exact
FAILURE MODES the exam and the official docs warn about. What it is not: a
real model — real Claude is non-deterministic, so the 🔑 pages later check
the same mechanics against the real API.

Grounding (official docs, fetched 2026-09-26 — see CLAUDE.md "Ground truth"):
- stop_reason values and how to handle them ........ platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
- a refusal is HTTP 200, content may be empty,
  stop_details {type, category, explanation},
  retry on a DIFFERENT model .......................... platform.claude.com/docs/en/build-with-claude/refusals-and-fallback
- tool_result formatting rules (must immediately follow the tool_use turn,
  tool_result blocks FIRST, text only after them) ... platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls
- an empty end_turn can follow text added right after tool results
  (the mock makes this deterministic; the docs say "typically") ... handling-stop-reasons
The scripted BEHAVIOURS (what the "model" says in each scenario) are invented
for teaching and are simulation, not documentation. Error wording is an
approximation, marked SIMULATED; the docs quote only the fragment
"tool_use ids were found without tool_result blocks immediately after".

Design choices worth knowing:
- The mock is STATELESS about your loop: it decides what to say next only from
  the `messages` you send (which tool results it can see). If your loop forgets
  to append tool results, the model behaves like a real one that never saw them.
- The model ids in these labs are placeholders ("mock-claude",
  "mock-claude-fallback"): real ids are pinned in one place and never
  hard-coded from memory (CLAUDE.md model rules).
"""

from __future__ import annotations

import itertools
import json
import os
from dataclasses import dataclass, field
from typing import Callable

from utils import lab_trace

PRIMARY_MODEL = "mock-claude"
FALLBACK_MODEL = "mock-claude-fallback"
MAX_CALLS_PER_RUN = 40


class MockAPIError(Exception):
    """Stands in for the API's 400 invalid_request_error (SIMULATED)."""


class RunawayGuard(Exception):
    """Simulated spend guard so a buggy infinite loop cannot hang the lab."""


# ── Response objects (attribute access, like the real SDK's blocks) ────────────


@dataclass
class TextBlock:
    text: str
    type: str = "text"

    def to_dict(self) -> dict:
        return {"type": "text", "text": self.text}


@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict
    type: str = "tool_use"

    def to_dict(self) -> dict:
        return {"type": "tool_use", "id": self.id, "name": self.name, "input": self.input}


@dataclass
class ServerToolUseBlock:
    """A server tool (e.g. web search) Anthropic runs itself — shown when the server-side loop pauses."""
    id: str
    name: str
    input: dict
    type: str = "server_tool_use"

    def to_dict(self) -> dict:
        return {"type": "server_tool_use", "id": self.id, "name": self.name, "input": self.input}


@dataclass
class Usage:
    input_tokens: int
    output_tokens: int


@dataclass
class Message:
    content: list
    stop_reason: str
    usage: Usage
    stop_details: dict | None = None     # None for every stop reason except "refusal" (per the docs)
    stop_sequence: str | None = None     # which custom stop sequence was hit (docs: read it when stop_reason is stop_sequence)
    model: str = PRIMARY_MODEL
    role: str = "assistant"


# ── Reading a conversation ─────────────────────────────────────────────────────


@dataclass
class Seen:
    """One tool call the model can see the result of, in conversation order."""
    name: str
    args: dict
    result: str


@dataclass
class Conversation:
    seen: list
    resumed: bool               # the last message is a paused assistant turn being sent back as-is
    text_after_results: bool    # the last user message put text right after its tool results


def _get(obj, key, default=None):
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def _blocks(content) -> list:
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return list(content) if content is not None else []


def _read_conversation(messages) -> Conversation:
    """Validate the message shape and return what the model can see."""
    if not isinstance(messages, list) or not messages:
        raise MockAPIError("messages must be a non-empty list (SIMULATED)")

    last = messages[-1]
    resumed = False
    if _get(last, "role") == "assistant":
        resumed = any(_get(b, "type") == "server_tool_use" for b in _blocks(_get(last, "content")))
        if not resumed:
            raise MockAPIError("the last message must have role 'user' (SIMULATED)")
    elif _get(last, "role") != "user":
        raise MockAPIError(f"invalid role {_get(last, 'role')!r} (SIMULATED)")

    seen: list[Seen] = []
    pending: dict[str, tuple[str, dict]] = {}  # tool_use id -> (name, input) awaiting a result
    text_after_results = False
    for index, m in enumerate(messages):
        role = _get(m, "role")
        blocks = _blocks(_get(m, "content"))
        if role == "assistant":
            if pending:
                raise MockAPIError(
                    "invalid_request_error (SIMULATED): an assistant turn contains tool_use blocks "
                    f"that were not answered by tool_result blocks: {sorted(pending)}")
            for b in blocks:
                if _get(b, "type") == "tool_use":
                    pending[_get(b, "id")] = (_get(b, "name"), _get(b, "input") or {})
        elif role == "user":
            kinds = [_get(b, "type") for b in blocks]
            results = [b for b in blocks if _get(b, "type") == "tool_result"]
            ids = {_get(b, "tool_use_id") for b in results}
            # Docs (handle-tool-calls): in the user message that carries tool results, the
            # tool_result blocks must come FIRST; any text must come AFTER all of them.
            if "tool_result" in kinds:
                first_other = next((i for i, k in enumerate(kinds) if k != "tool_result"), None)
                last_result = max(i for i, k in enumerate(kinds) if k == "tool_result")
                if first_other is not None and first_other < last_result:
                    raise MockAPIError(
                        "invalid_request_error (SIMULATED): in the user message that carries tool "
                        "results, tool_result blocks must come first - any text must come after all "
                        "of them")
                if index == len(messages) - 1 and last_result < len(kinds) - 1:
                    text_after_results = True
            missing = set(pending) - ids
            if missing:
                raise MockAPIError(
                    "invalid_request_error (SIMULATED): tool_use ids were found without tool_result "
                    f"blocks immediately after: {sorted(missing)}")
            unknown = ids - set(pending)
            if unknown:
                raise MockAPIError(
                    "invalid_request_error (SIMULATED): unexpected tool_use_id in tool_result blocks: "
                    f"{sorted(unknown)}")
            for b in results:
                name, args = pending[_get(b, "tool_use_id")]
                seen.append(Seen(name, args, str(_get(b, "content"))))
            pending = {}
        else:
            raise MockAPIError(f"invalid role {role!r} (SIMULATED)")
    return Conversation(seen, resumed, text_after_results)


# ── Scripted behaviours ────────────────────────────────────────────────────────


@dataclass
class Ctx:
    model: str
    max_tokens: int
    resumed: bool


@dataclass
class Turn:
    text: str | None = None
    tool: tuple[str, dict] | None = None      # a client tool_use  -> stop_reason "tool_use"
    final: str | None = None                  # a final answer     -> stop_reason "end_turn"
    refusal: dict | None = None               # stop_details       -> stop_reason "refusal"
    pause: tuple[str, dict] | None = None     # a server tool call -> stop_reason "pause_turn"
    empty: bool = False                       # an empty response  -> stop_reason "end_turn", content []


def _order_status(seen: list[Seen]) -> str | None:
    for s in seen:
        if s.name == "lookup_order":
            try:
                return json.loads(s.result).get("status")
            except (ValueError, AttributeError):
                return None
    return None


def _support_flow(seen: list[Seen], ctx: Ctx) -> Turn:
    """The model decides from what it has SEEN: verify -> look up -> refund, unless already refunded."""
    n = len(seen)
    if n == 0:
        return Turn(text="Let me verify the customer first.",
                    tool=("get_customer", {"email": "alice@example.com"}))
    if n == 1:
        return Turn(tool=("lookup_order", {"order_id": "ORD-1001"}))
    if n == 2:
        if _order_status(seen) == "REFUNDED":
            return Turn(final="Order ORD-1001 was already refunded, so no further action is needed.")
        return Turn(tool=("process_refund", {"order_id": "ORD-1001", "amount": 49.0}))
    return Turn(final="Refund issued for ORD-1001. Customer A has been taken care of.")


def _long_task(seen: list[Seen], ctx: Ctx) -> Turn:
    n = len(seen)
    if n == 0:
        return Turn(text="Let me verify the customer first.",
                    tool=("get_customer", {"email": "alice@example.com"}))
    if n == 1:
        return Turn(tool=("lookup_order", {"order_id": "ORD-1001"}))
    if n == 2:
        return Turn(tool=("check_policy", {"order_id": "ORD-1001"}))
    if n == 3:
        return Turn(tool=("process_refund", {"order_id": "ORD-1001", "amount": 49.0}))
    if n == 4:
        return Turn(tool=("send_confirmation",
                          {"customer_id": "C-1001", "message": "Your refund has been issued."}))
    return Turn(final="All done: the refund was issued and the customer was notified.")


def _narrates_done(seen: list[Seen], ctx: Ctx) -> Turn:
    """Prose that SOUNDS finished while a tool call is still pending."""
    n = len(seen)
    if n == 0:
        return Turn(text="Let me verify the customer first.",
                    tool=("get_customer", {"email": "alice@example.com"}))
    if n == 1:
        return Turn(tool=("lookup_order", {"order_id": "ORD-1001"}))
    if n == 2:
        return Turn(text="That's everything I need - I'm done checking. Issuing the refund now.",
                    tool=("process_refund", {"order_id": "ORD-1001", "amount": 49.0}))
    return Turn(final="Refund issued for ORD-1001.")


def _runaway(seen: list[Seen], ctx: Ctx) -> Turn:
    """Never converges: keeps retrying an order that does not exist."""
    return Turn(text="Let me look that order up again." if len(seen) == 0 else None,
                tool=("lookup_order", {"order_id": "ORD-9999"}))


_LONG_FINAL = (
    "Refund issued for ORD-1001. Here is the full summary for your records: the order arrived damaged, "
    "the customer Customer A was verified by email, the order status was DELIVERED and the amount of "
    "$49.00 was refunded to the original payment method. The refund reference is RF-0001. Expect the "
    "funds within five to seven business days. No further action is needed on your side - "
    "thank you for your patience.")


def _truncated_answer(seen: list[Seen], ctx: Ctx) -> Turn:
    turn = _support_flow(seen, ctx)
    if turn.final and len(seen) >= 3:
        turn.final = _LONG_FINAL
    return turn


def _refusal(seen: list[Seen], ctx: Ctx) -> Turn:
    """The primary model's safety classifier declines; a DIFFERENT model serves the request."""
    if ctx.model == PRIMARY_MODEL:
        return Turn(refusal={"type": "refusal", "category": "general_harms",
                             "explanation": "This request was declined under a usage-policy area."})
    return _support_flow(seen, ctx)


def _pause_turn(seen: list[Seen], ctx: Ctx) -> Turn:
    """A server-side tool loop hits its iteration limit; the paused turn must be sent back as-is."""
    if not seen and not ctx.resumed:
        return Turn(text="Let me check the carrier's damage-claim policy online first.",
                    pause=("web_search", {"query": "carrier damage claim policy"}))
    return _support_flow(seen, ctx)


def _chitchat(seen: list[Seen], ctx: Ctx) -> Turn:
    """No order to deal with: a model-driven agent simply answers, without calling any tool."""
    return Turn(final="Hello! I can look up a customer, check an order and issue refunds. "
                      "Tell me which order you need help with.")


@dataclass
class Scenario:
    id: str
    title: str
    description: str
    backend_status: str                      # state of ORD-1001 in the fake backend
    behavior: Callable[[list, Ctx], Turn] = field(repr=False, default=_support_flow)
    final_tokens: int | None = None          # simulated size of the final answer, for max_tokens truncation


SCENARIOS: dict[str, Scenario] = {s.id: s for s in [
    Scenario("damaged_order", "Damaged order — the normal 3-tool path",
             "Customer reports a damaged order. The model verifies, looks up, refunds, then finishes. "
             "Note its very first reply carries text AND a tool request.",
             "DELIVERED", _support_flow),
    Scenario("already_refunded", "Order was already refunded",
             "Same request, but the backend says ORD-1001 is already REFUNDED. A model-driven loop "
             "notices and stops; a hard-coded sequence would refund twice.",
             "REFUNDED", _support_flow),
    Scenario("long_task", "Long task — 5 sequential tool calls",
             "Verify, look up, check policy, refund, notify. Needs more turns than a small fixed "
             "loop allows.",
             "DELIVERED", _long_task),
    Scenario("narrates_done", "Model narrates 'done' while a tool call is pending",
             "On its third turn the model writes prose that sounds finished ('I'm done checking') "
             "yet still requests process_refund.",
             "DELIVERED", _narrates_done),
    Scenario("runaway", "Runaway — the model never converges",
             "The model keeps retrying a lookup for an order that does not exist and never returns "
             "end_turn.",
             "DELIVERED", _runaway),
    Scenario("truncated_answer", "Long final answer — the max_tokens limit cuts it off",
             "The normal path, but the final answer needs about 300 tokens. With a smaller max_tokens "
             "the response is truncated and stop_reason is max_tokens, not end_turn.",
             "DELIVERED", _truncated_answer, final_tokens=300),
    Scenario("refusal", "Refusal — HTTP 200, not an error",
             "The primary model declines the request (stop_reason refusal, empty content, stop_details). "
             "Per the docs, retrying the same model usually refuses again; a different model can serve it.",
             "DELIVERED", _refusal),
    Scenario("pause_turn", "pause_turn — a server-side tool loop pauses",
             "The model starts a server tool (web search) and its server-side loop hits the iteration "
             "limit. The paused turn has to be sent back as-is to continue.",
             "DELIVERED", _pause_turn),
]}

SCENARIO_ORDER = list(SCENARIOS)

# ── The client ─────────────────────────────────────────────────────────────────

_ID_COUNTER = itertools.count(1)
_CALLS = 0
_LAST_N_MESSAGES: int | None = None


def _dump(obj) -> str:
    return json.dumps(obj, default=lambda o: o.to_dict() if hasattr(o, "to_dict") else str(o))


class _Messages:
    def __init__(self, scenario: Scenario, context_window: int | None = None):
        self._scenario = scenario
        self._context_window = context_window

    def create(self, *, model: str = PRIMARY_MODEL, max_tokens: int = 1024, messages=None,
               tools=None, system=None, tool_choice=None, stop_sequences=None, **_ignored) -> Message:
        global _CALLS, _LAST_N_MESSAGES
        _CALLS += 1
        if _CALLS > MAX_CALLS_PER_RUN:
            raise RunawayGuard(
                f"SIMULATED spend guard: more than {MAX_CALLS_PER_RUN} API calls in one run - "
                "aborting. A real runaway loop would keep spending tokens.")

        conv = _read_conversation(messages)
        in_tokens = max(1, len(_dump(messages)) // 4)
        if self._context_window is not None and in_tokens > self._context_window:
            # SIMULATED context-window limit (a lab setting, not an API parameter). The docs list
            # model_context_window_exceeded as a stop reason (beta) and say to treat it as truncated.
            lab_trace.record({
                "kind": "api_call", "call": _CALLS, "stop_reason": "model_context_window_exceeded", "model": model,
                "max_tokens": max_tokens, "n_messages": len(messages), "advanced": None,
                "input_tokens": in_tokens, "output_tokens": 0, "stop_details": None, "blocks": [],
                "stop_sequence": None})
            return Message(content=[], stop_reason="model_context_window_exceeded",
                           usage=Usage(input_tokens=in_tokens, output_tokens=0), model=model)
        turn = self._scenario.behavior(conv.seen, Ctx(model, max_tokens, conv.resumed))
        if conv.text_after_results:
            # Docs (handling-stop-reasons): text added right after tool results can teach Claude to
            # expect more input, producing an EMPTY response with end_turn. Deterministic here.
            turn = Turn(empty=True)

        stop_details = None
        stop_seq = None
        if turn.empty:
            content, stop_reason = [], "end_turn"
        elif turn.refusal is not None:
            content, stop_reason, stop_details = [], "refusal", turn.refusal
        elif turn.pause is not None:
            name, args = turn.pause
            content = ([TextBlock(turn.text)] if turn.text else []) + [
                ServerToolUseBlock(f"srvtoolu_sim_{next(_ID_COUNTER):03d}", name, dict(args))]
            stop_reason = "pause_turn"
        elif turn.final is not None:
            text, stop_reason = turn.final, "end_turn"
            need = self._scenario.final_tokens
            if need and max_tokens < need:  # truncated: the response stopped at the max_tokens limit
                text, stop_reason = text[: int(len(text) * max_tokens / need)], "max_tokens"
            hit = None
            for seq in (stop_sequences or []):
                i = text.find(seq)
                if i != -1 and (hit is None or i < hit[0]):
                    hit = (i, seq)
            if hit is not None:   # SIMULATED: generation halts at the earliest stop sequence
                text, stop_reason, stop_seq = text[: hit[0]], "stop_sequence", hit[1]
            content = [TextBlock(text)]
        else:
            content = [TextBlock(turn.text)] if turn.text else []
            name, args = turn.tool
            content.append(ToolUseBlock(f"toolu_sim_{next(_ID_COUNTER):03d}", name, dict(args)))
            stop_reason = "tool_use"

        out_tokens = 0 if stop_reason == "refusal" else max(1, sum(len(_dump(b)) for b in content) // 4)
        if stop_reason == "max_tokens":
            out_tokens = max_tokens
        usage = Usage(input_tokens=in_tokens, output_tokens=out_tokens)
        advanced = None if _LAST_N_MESSAGES is None else len(messages) > _LAST_N_MESSAGES
        _LAST_N_MESSAGES = len(messages)
        lab_trace.record({
            "kind": "api_call", "call": _CALLS, "stop_reason": stop_reason, "model": model,
            "max_tokens": max_tokens, "n_messages": len(messages), "advanced": advanced,
            "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens,
            "stop_details": stop_details, "blocks": [b.to_dict() for b in content],
            "stop_sequence": stop_seq,
        })
        return Message(content=content, stop_reason=stop_reason, usage=usage,
                       stop_details=stop_details, stop_sequence=stop_seq, model=model)


class MockClaude:
    """Drop-in shape of `anthropic.Anthropic()` for the labs. SIMULATED."""

    def __init__(self, scenario: "str | Scenario | None" = None, context_window: int | None = None):
        if isinstance(scenario, Scenario):        # the agent playground builds its own scenario per run
            self.scenario = scenario
        else:
            sid = scenario or os.environ.get("LAB_SCENARIO", "damaged_order")
            if sid not in SCENARIOS:
                raise ValueError(f"unknown lab scenario {sid!r}; choose from {SCENARIO_ORDER}")
            self.scenario = SCENARIOS[sid]
        self.messages = _Messages(self.scenario, context_window)


def reset() -> None:
    """Clear the per-process call counters (the agent playground runs in the Streamlit process, not a fresh child)."""
    global _CALLS, _LAST_N_MESSAGES
    _CALLS, _LAST_N_MESSAGES = 0, None
