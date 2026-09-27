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
import re
from dataclasses import dataclass, field
from typing import Callable

from utils import lab_trace
from utils.research_backend import SUBTOPICS

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
    system: str = ""            # the system prompt of THIS call (the multi-agent labs read a "ROLE: x" marker from it)
    prompt: str = ""            # the first user message of THIS conversation
    tools: tuple = ()           # names of the tools offered in THIS call
    user_texts: tuple = ()      # every text the user (customer) has written so far, in order (D1.5 support labs)
    new_turn: bool = False      # the last message is a fresh customer text (not tool results)
    tool_defs: tuple = ()       # the full tool definitions offered in THIS call


@dataclass
class Turn:
    text: str | None = None
    tool: tuple[str, dict] | None = None      # a client tool_use  -> stop_reason "tool_use"
    tools: list | None = None                 # SEVERAL tool_use blocks in ONE response (parallel calls)
    final: str | None = None                  # a final answer     -> stop_reason "end_turn"
    refusal: dict | None = None               # stop_details       -> stop_reason "refusal"
    pause: tuple[str, dict] | None = None     # a server tool call -> stop_reason "pause_turn"
    empty: bool = False                       # an empty response  -> stop_reason "end_turn", content []
    special: str | None = None                # "max_tokens_tool" (cut mid tool call) | "context_full" (D1.3 stop-reason labs)


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



# ── Multi-agent research behaviours (D1.2 Subagents) ───────────────────────────
# One scripted "model" plays every ROLE in the lab; the role comes from a "ROLE: x" marker in the system prompt of
# the call (a subagent's system prompt is its AgentDefinition.prompt). The coordinator follows its system prompt by
# KEYWORD ("parallel", "gaps", "single most", "step 1", ...) — a stand-in for real instruction-following, which is
# far less literal. All of this is SIMULATION, not documentation.

_TASK_NAMES = ("Task", "Agent")   # the exam guide says "Task"; current docs say "Agent" (renamed v2.1.63, Task = legacy alias)


def _role(ctx: Ctx) -> str | None:
    m = re.search(r"ROLE:\s*([A-Za-z]+)", ctx.system)
    return m.group(1).lower() if m else None


def _topic_of(text: str) -> str | None:
    t = text.lower()
    for name in SUBTOPICS:
        if name in t:
            return name
    return "eiffel tower" if "eiffel" in t else None


def _extract_findings(text: str) -> list[dict]:
    """Pull every {"topic": ..., "findings": [...]} object out of free text (a prompt or a tool result)."""
    out, dec, i = [], json.JSONDecoder(), 0
    while True:
        i = text.find('{"topic"', i)
        if i == -1:
            return out
        try:
            obj, end = dec.raw_decode(text[i:])
        except ValueError:
            i += 1
            continue
        if isinstance(obj, dict) and "findings" in obj:
            out.append(obj)
        i += end


def _informative(result: str) -> bool:
    """Could a coordinator USE this subagent result? (findings, a named failure, or a report - not a bare acknowledgement)"""
    r = result.strip()
    return '"claim"' in r or "## " in r or r.startswith(("SEARCH_FAILED", "NO_FINDINGS", "I was not given", "I could not"))


def _searcher(seen: list[Seen], ctx: Ctx) -> Turn:
    topic = _topic_of(ctx.prompt)
    if "web_search" not in ctx.tools:   # AgentDefinition tool restriction: the tool is simply not in its session
        return Turn(final=f"SEARCH_FAILED: {topic}: this subagent has no search tool")
    if not seen:
        query = ("targeted " if "targeted" in ctx.prompt.lower() else "") + (topic or ctx.prompt[:60])
        return Turn(tool=("web_search", {"query": query}))
    result = seen[0].result
    if result.startswith("ERROR"):
        return Turn(final=f"SEARCH_FAILED: {topic}: {result}")
    return Turn(final=result)


def _analyst(seen: list[Seen], ctx: Ctx) -> Turn:
    blocks = _extract_findings(ctx.prompt)
    if not blocks:
        return Turn(final="NO_FINDINGS_PROVIDED: I was not given any findings to verify.")
    return Turn(final="\n".join(json.dumps({"topic": b["topic"], "findings": b["findings"], "verified": True})
                                for b in blocks))


def _synthesizer(seen: list[Seen], ctx: Ctx) -> Turn:
    blocks = _extract_findings(ctx.prompt)
    if not blocks:
        return Turn(final="I was not given any findings, so I cannot write a sourced report.")
    merged: dict[str, dict] = {}
    for b in blocks:
        rows = merged.setdefault(b["topic"], {})
        for f in b["findings"]:
            rows.setdefault(f.get("source_url") or f["claim"], f)
    order = [t for t in SUBTOPICS if t in merged] + [t for t in merged if t not in SUBTOPICS]
    lines = []
    for t in order:
        cites = " ".join(f"{f['claim']} [{f['document']}, p.{f['page']}]" if "document" in f
                         else f"{f['claim']} [no source]" for f in merged[t].values())
        lines.append(f"## {t.title()}\n{cites}")
    return Turn(final="\n".join(lines))


def _coordinator(seen: list[Seen], ctx: Ctx) -> Turn:
    sysl = ctx.system.lower()
    simple = "eiffel" in ctx.prompt.lower()
    tname = next((n for n in _TASK_NAMES if n in ctx.tools), None)
    if tname is None:   # the spawn tool is not in the allowed tools: the coordinator cannot delegate
        fact = ("it opened around 1889" if simple else "AI is changing music, film and visual arts in many ways")
        return Turn(final=f"I could not delegate, so this is from general knowledge with no sources: {fact}. [no sources]")

    rigid, parallel = "step 1" in sysl, "parallel" in sysl
    narrow, refine, overlap = "single most" in sysl, "gaps" in sysl, "allow overlapping" in sysl
    subs = ["eiffel tower"] if simple else list(SUBTOPICS)
    if narrow and not simple:
        subs = subs[:1]
    if overlap and not simple:
        subs = subs[:2] + ["music"] + subs[2:]

    def task(kind: str, desc: str, prompt: str) -> tuple:
        return (tname, {"subagent_type": kind, "description": desc, "prompt": prompt})

    def search_prompt(t: str, targeted: bool = False) -> str:
        head = (f"TARGETED retry for '{t}': the first attempt failed or coverage was missing - use a narrower query. "
                if targeted else f"Research ONLY the area '{t}'. ")
        return head + f"Overall topic: {ctx.prompt} Return findings as JSON with source url, document and page."

    tasks = [x for x in seen if x.name in _TASK_NAMES]
    kind_of = lambda x: x.args.get("subagent_type")   # noqa: E731
    S = [x for x in tasks if kind_of(x) == "searcher"]
    A = [x for x in tasks if kind_of(x) == "analyst"]
    Y = [x for x in tasks if kind_of(x) == "synthesizer"]
    targeted = [x for x in S if "targeted" in x.args.get("prompt", "").lower()]
    initial = [x for x in S if x not in targeted]

    if simple and not rigid:   # dynamic selection: a simple question needs ONE subagent, not the whole pipeline
        if not S:
            return Turn(text="A single lookup is enough here.",
                        tools=[task("searcher", "Find opening year", search_prompt("eiffel tower"))])
        blocks = _extract_findings(S[0].result)
        if blocks and blocks[0]["findings"]:
            f = blocks[0]["findings"][0]
            return Turn(final=f"{f['claim']} [{f['document']}, p.{f['page']}]")
        return Turn(final="I could not confirm the answer.")

    remaining = subs[len(initial):]
    if remaining:
        batch = remaining if parallel else remaining[:1]
        text = "I'll split this into distinct areas and delegate them." if not initial else None
        return Turn(text=text, tools=[task("searcher", f"Research {t}", search_prompt(t)) for t in batch])
    if not A:
        found = "\n".join(x.result for x in initial if x.result.strip().startswith("{"))
        return Turn(tools=[task("analyst", "Verify findings",
                                "Verify and annotate these findings. Keep every source.\n" + found)])
    if not Y:
        return Turn(tools=[task("synthesizer", "Write cited report",
                                "Write a cited report covering each area, using ONLY these verified findings:\n"
                                + A[0].result)])
    if len(Y) == 1 and refine:   # the coordinator evaluates the synthesis for gaps and re-delegates
        report = Y[0].result.lower()
        missing = [t for t in dict.fromkeys(subs) if t not in report]
        done = {_topic_of(x.args.get("prompt", "")) for x in targeted}
        pending = [t for t in missing if t not in done]
        if pending:
            batch = pending if parallel else pending[:1]
            return Turn(text="The draft has gaps - re-delegating targeted searches.",
                        tools=[task("searcher", f"Retry {t}", search_prompt(t, targeted=True)) for t in batch])
        if targeted:
            extra = "\n".join(x.result for x in targeted if x.result.strip().startswith("{"))
            return Turn(tools=[task("synthesizer", "Revise cited report",
                                    "Write a cited report covering each area, using ONLY these verified findings:\n"
                                    + A[0].result + "\n" + extra)])
    return Turn(final=Y[-1].result)


def _research(seen: list[Seen], ctx: Ctx) -> Turn:
    role = _role(ctx) or "coordinator"
    return {"searcher": _searcher, "analyst": _analyst, "synthesizer": _synthesizer}.get(role, _coordinator)(seen, ctx)


@dataclass
class Scenario:
    id: str
    title: str
    description: str
    backend_status: str                      # state of ORD-1001 in the fake backend
    behavior: Callable[[list, Ctx], Turn] = field(repr=False, default=_support_flow)
    final_tokens: int | None = None          # simulated size of the final answer, for max_tokens truncation
    research: dict | None = None             # multi-agent labs: kwargs for research_backend.configure()


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

SCENARIO_ORDER = list(SCENARIOS)      # the D1.1 (single-agent) scenarios, in display order

# ── Multi-agent research scenarios (D1.2 Subagents) — kept out of SCENARIO_ORDER on purpose ──
RESEARCH_SCENARIOS: dict[str, Scenario] = {s.id: s for s in [
    Scenario("broad_topic", "Broad topic — needs several distinct areas",
             "A broad question about AI and the creative industries. A good coordinator splits it into distinct areas "
             "(visual arts, music, film), delegates them, verifies, and synthesises a cited report.",
             "DELIVERED", _research, research={"query_kind": "broad"}),
    Scenario("simple_question", "Simple question — one lookup is enough",
             "A one-fact question. A good coordinator picks ONE subagent; a fixed pipeline runs everything anyway.",
             "DELIVERED", _research, research={"query_kind": "simple"}),
    Scenario("source_fails", "One source times out (film)",
             "Same broad question, but the first film search fails. Whether the report ends up complete depends on "
             "whether the coordinator sees the failure and re-delegates.",
             "DELIVERED", _research, research={"query_kind": "broad", "fail_topic": "film"}),
]}
RESEARCH_SCENARIO_ORDER = list(RESEARCH_SCENARIOS)
SCENARIOS.update(RESEARCH_SCENARIOS)   # so MockClaude(scenario="broad_topic") and the harness can find them


# ── Single-call stop-reason scenarios (D1.3 Stop Reason) ───────────────────────
# Each scenario makes ONE model call that ends for a different reason, so a handler can be judged per stop_reason.
# Grounding: platform.claude.com/docs/en/build-with-claude/handling-stop-reasons and .../refusals-and-fallback (2026-09-26).
# The scripted texts and the truncation point are simulation.

STOP_SEQUENCE = "END_REPORT"


def _sr_tool_use(seen, ctx):
    return Turn(text="That's everything I need - I'm done checking. Verifying the customer now.",
                tool=("get_customer", {"email": "alice@example.com"}))


def _sr_end_turn(seen, ctx):
    return Turn(final="Refund issued for ORD-1001. Customer A has been taken care of.")


def _sr_max_tokens(seen, ctx):
    return Turn(final=_LONG_FINAL)


def _sr_max_tokens_tool(seen, ctx):
    return Turn(text="Let me issue the refund now.", special="max_tokens_tool")


def _sr_refusal(seen, ctx):
    # docs: category and explanation are BOTH null when the refusal maps to no named category - a normal, permanent value
    return Turn(refusal={"type": "refusal", "category": None, "explanation": None})


def _sr_pause(seen, ctx):
    return Turn(text="Let me check the carrier's damage-claim policy online first.",
                pause=("web_search", {"query": "carrier damage claim policy"}))


def _sr_stop_sequence(seen, ctx):
    return Turn(final=f"Refund issued for ORD-1001. {STOP_SEQUENCE} Customer A has been taken care of.")


def _sr_context(seen, ctx):
    return Turn(text="Refund issued for ORD-1001. Here is the full summary for", special="context_full")


def _sr_empty(seen, ctx):
    return Turn(empty=True)


def _sr_api_error(seen, ctx):
    raise MockAPIError("overloaded_error (SIMULATED HTTP 529): the API is temporarily overloaded - this is an ERROR, "
                       "not a stop reason (there is no stop_reason to read)")


STOP_SCENARIOS: dict[str, Scenario] = {s.id: s for s in [
    Scenario("sr_tool_use", "tool_use — text AND a tool request",
             "The model says something that sounds finished, and asks for a tool in the same response.", "DELIVERED", _sr_tool_use),
    Scenario("sr_end_turn", "end_turn — a normal, complete answer",
             "The model finishes naturally.", "DELIVERED", _sr_end_turn),
    Scenario("sr_max_tokens", "max_tokens — the answer is cut off",
             "The request's max_tokens is smaller than the answer, so the text stops mid-sentence.", "DELIVERED",
             _sr_max_tokens, final_tokens=300),
    Scenario("sr_max_tokens_tool", "max_tokens — cut off in the middle of a tool call",
             "The limit hits while the model is writing a tool_use block: the last block is an INCOMPLETE tool call.",
             "DELIVERED", _sr_max_tokens_tool),
    Scenario("sr_refusal", "refusal — HTTP 200, empty content, null category",
             "The model declines. Content is empty; stop_details is present but its category and explanation are null.",
             "DELIVERED", _sr_refusal),
    Scenario("sr_pause_turn", "pause_turn — a server-tool loop paused",
             "A server-side tool loop hit its iteration limit; the response ends with an unanswered server tool call.",
             "DELIVERED", _sr_pause),
    Scenario("sr_stop_sequence", "stop_sequence — your tripwire text fired",
             "The request sets a stop sequence; the model reaches it and generation halts there.", "DELIVERED",
             _sr_stop_sequence),
    Scenario("sr_context_window", "model_context_window_exceeded — the context window filled",
             "Generation stopped because the context window is full (not because of max_tokens). The content is valid but limited.",
             "DELIVERED", _sr_context),
    Scenario("sr_empty_end_turn", "end_turn with EMPTY content",
             "A pitfall from the docs: the response ends its turn with no content at all.", "DELIVERED", _sr_empty),
    Scenario("sr_api_error", "An API error — no stop_reason at all",
             "The call itself fails (simulated HTTP 529 overloaded). It raises instead of returning a response.",
             "DELIVERED", _sr_api_error),
]}
STOP_SCENARIO_ORDER = list(STOP_SCENARIOS)
SCENARIOS.update(STOP_SCENARIOS)



# ── Simulated support agent (D1.5 Escalation) ──────────────────────────────────
# Follows its system prompt by KEYWORD (a stand-in for instruction-following — real models are far less literal):
#   "asks for a human ... immediately"      escalate at once when the customer asks for a human
#   "first investigate"                      investigate before honouring a human request
#   "ambiguous or silent"                    escalate when the policy doesn't cover the request
#   "meaningful progress"                    escalate when tools keep failing
#   "do not escalate just because"           acknowledge frustration, offer to resolve
#   "upset or frustrated" / "confidence" / "complex cases"   the distractor triggers
#   "another identifier" / "most recent order"               multiple matches: ask vs pick
# It skips verification when the customer says "skip the checks" (a scripted instance of the guide's point that prompt
# instructions alone have a non-zero failure rate). All of this is SIMULATION, not documentation.

_HUMAN_WORDS = ("human", "a person", "manager", "real agent", "someone real")
_ANGRY_WORDS = ("!!", "furious", "ridiculous", "fed up", "third time")


def _support_agent(seen: list[Seen], ctx: Ctx) -> Turn:
    sysl = ctx.system.lower()
    f = {"human_now": "asks for a human" in sysl and "immediately" in sysl, "human_after": "first investigate" in sysl,
         "policy": "ambiguous or silent" in sysl, "progress": "meaningful progress" in sysl,
         "calm": "do not escalate just because" in sysl, "upset": "upset or frustrated" in sysl,
         "confidence": "confidence" in sysl, "complex": "complex cases" in sysl,
         "ask_id": "another identifier" in sysl, "pick_recent": "most recent order" in sysl}
    texts = list(ctx.user_texts) or [ctx.prompt]
    latest, alltext = texts[-1], " ".join(texts)
    low = alltext.lower()
    names = [x.name for x in seen]
    structured = any(_get(t, "name") == "escalate_to_human"
                     and "root_cause" in json.dumps(_get(t, "input_schema", {})) for t in ctx.tool_defs)

    def parse(x):
        try:
            return json.loads(x.result)
        except (ValueError, TypeError):
            return None

    single = [parse(x) for x in seen if x.name == "get_customer" and x.result.startswith("{")]
    multi = [parse(x) for x in seen if x.name == "get_customer" and x.result.startswith("[")]
    verified = single[-1]["customer_id"] if single else None
    order_m = re.findall(r"ORD-\d+", alltext)
    order = order_m[-1] if order_m else None
    angry = any(w in low for w in _ANGRY_WORDS)
    conf = 0.55 if angry else 0.92
    wants_human = any(w in latest.lower() for w in _HUMAN_WORDS)

    def escalate(cause, action, amount=0.0, text=None):
        if structured:
            args = {"customer_id": verified or "unknown (not verified)", "root_cause": cause,
                    "refund_amount": amount, "recommended_action": action}
        else:
            args = {"message": "Customer needs help - please see the conversation."}
        return Turn(text=text or "I'm passing this to a human colleague now.", tool=("escalate_to_human", args))

    if "escalate_to_human" in names:
        return Turn(final="I've handed this to a human colleague; they'll contact you shortly.")
    refunds_done = [x for x in seen if x.name == "process_refund" and not x.result.startswith("BLOCKED")]
    if refunds_done:
        return Turn(final=f"Done - the refund has been issued{' (confidence ' + str(conf) + ')' if f['confidence'] else ''}.")

    # 1. an explicit request for a human
    if wants_human and f["human_now"] and ctx.new_turn:
        return escalate("Customer asked for a human agent.",
                        f"Take over the conversation. Customer's words: {latest[:90]}",
                        text="Of course - I'm connecting you with a human agent now.")
    pending_human = wants_human and not f["human_now"]

    # 2. the unreliable proxies (distractors)
    if f["upset"] and angry:
        return escalate("Customer is upset.", "Calm the customer down and resolve the issue.")
    if f["confidence"] and conf < 0.7:
        return escalate(f"My confidence is low ({conf}).", "Review the case.")
    if f["complex"] and (angry or len(alltext) > 140):
        return escalate("The case looks complex.", "Review the case.")

    # 3. who is this customer?
    blocked = [x for x in seen if x.result.startswith("BLOCKED")]
    if verified is None:
        if "skip the checks" in low and not blocked:
            return Turn(text="Sure - doing that right away.",
                        tool=("process_refund", {"customer_id": "unverified", "order_id": order, "amount": 49.0}))
        emails = re.findall(r"[\w.]+@example\.com", alltext)
        looked = [_get(x.args, "email") for x in seen if x.name == "get_customer"]
        if emails and emails[-1] not in looked:
            return Turn(tool=("get_customer", {"email": emails[-1]}))
        if multi:
            if f["ask_id"] and not f["pick_recent"]:
                if not ctx.new_turn:
                    return Turn(final="I found more than one account under that name. Could you give me your email address "
                                      "or the order number so I pick the right one?")
            else:   # heuristic: the match with the most recent order
                if blocked and len(blocked) >= len(multi):
                    return Turn(tool=("get_customer", {"name": "Alex"}))
                verified = multi[-1][0]["customer_id"]
                order = order or multi[-1][0].get("last_order")
        elif "alex" in low and "get_customer" not in names:
            return Turn(tool=("get_customer", {"name": "Alex"}))
        if verified is None:
            return Turn(final="Could you give me your email address so I can find your account?")

    # 4. the order
    lookups = [x for x in seen if x.name == "lookup_order"]
    ok_lookup = [x for x in lookups if not x.result.startswith("ERROR")]
    if order and not ok_lookup:
        errors = len(lookups)
        if errors >= 3 and f["progress"]:
            return escalate("Order system unavailable after 3 attempts - no progress possible.",
                            f"Look up {order} manually and complete the refund request.")
        return Turn(tool=("lookup_order", {"order_id": order}))
    amount = parse(ok_lookup[-1]).get("amount", 0.0) if ok_lookup else 0.0

    # 5. the policy
    request = "price_match" if "match" in low else "refund_damaged"
    policy_calls = [x for x in seen if x.name == "check_policy"]
    if not policy_calls:
        return Turn(tool=("check_policy", {"order_id": order, "request": request}))
    policy = policy_calls[-1].result
    if "not addressed" in policy:
        if f["policy"]:
            return escalate("Policy is silent on competitor price matching (it only covers our own price drops).",
                            f"Decide whether to match Competitor X's price on {order} ($30 difference).", amount=30.0)
        return Turn(text="I'll match that price for you.",
                    tool=("process_refund", {"customer_id": verified, "order_id": order, "amount": 30.0}))
    if pending_human:
        return escalate("Customer asked for a human agent (after investigation).", f"Take over {order}.")
    if '"refund_allowed": false' in policy:
        return Turn(final=f"I'm sorry - {order} isn't eligible for a refund under our policy.")
    if f["calm"] and angry and len(texts) == 1:
        return Turn(final=f"I'm really sorry - that's frustrating. I can refund the ${amount:.0f} for {order} right now. "
                          "Shall I go ahead?")
    return Turn(text="Issuing the refund.", tool=("process_refund", {"customer_id": verified, "order_id": order,
                                                                       "amount": amount}))

# ── Session scenarios (D1.4) — the model is not called; utils/session_lab.py simulates the session layer ──
SESSION_SCENARIOS: dict[str, Scenario] = {s.id: s for s in [
    Scenario("next_day_unchanged", "Next day — nothing changed",
             "Yesterday you analysed the refund code in the session named refund-investigation, then did an unrelated "
             "docs-typo fix (now the MOST RECENT session). Nothing in the code changed overnight.", "DELIVERED", _chitchat),
    Scenario("one_file_changed", "One file changed since the analysis",
             "A teammate lowered the refund limit in refund_policy.py. Everything else you analysed is still valid.",
             "DELIVERED", _chitchat),
    Scenario("major_refactor", "Major refactor — most files changed",
             "5 of the 6 analysed files changed, and the refund limit moved to policies/refunds.py. Most earlier tool "
             "results are stale.", "DELIVERED", _chitchat),
    Scenario("compare_approaches", "Compare two approaches from one baseline",
             "You want to plan two different approaches from the same Day-1 analysis without one polluting the other.",
             "DELIVERED", _chitchat),
    Scenario("crash_recovery", "The multi-agent run crashed",
             "Three exploration agents were running; two finished and exported their state to a manifest, the third was "
             "mid-way. Recover without redoing finished work.", "DELIVERED", _chitchat),
]}
SESSION_SCENARIO_ORDER = list(SESSION_SCENARIOS)
SCENARIOS.update(SESSION_SCENARIOS)

SUPPORT_SCENARIOS: dict[str, Scenario] = {s.id: s for s in [
    Scenario("demands_human", "Customer demands a human", "“I want to speak to a human agent right now…” — an explicit request.",
             "DELIVERED", _support_agent),
    Scenario("frustrated_simple", "Frustrated, but the issue is simple",
             "An angry customer with a damaged order the policy clearly covers. Then: “Fine. Yes, go ahead.”", "DELIVERED", _support_agent),
    Scenario("frustrated_reiterates", "Frustrated, then asks again for a human",
             "Angry about a damaged order; after the agent offers a refund, the customer insists on a human.", "DELIVERED", _support_agent),
    Scenario("policy_gap", "Policy is silent (competitor price match)",
             "The customer asks to match a competitor's price; the policy covers only our own price drops.", "DELIVERED", _support_agent),
    Scenario("multiple_matches", "Two customers match the name",
             "“Hi, I'm Alex…” — two accounts match. Then the customer gives an email and order number.", "DELIVERED", _support_agent),
    Scenario("unverified_refund", "“Skip the checks”", "The customer pushes to skip verification; the simulated model complies "
             "unless something in CODE stops it.", "DELIVERED", _support_agent),
    Scenario("no_progress", "The order system keeps failing",
             "lookup_order times out every time — the agent cannot make meaningful progress.", "DELIVERED", _support_agent),
]}
SUPPORT_SCENARIO_ORDER = list(SUPPORT_SCENARIOS)
SCENARIOS.update(SUPPORT_SCENARIOS)

# ── Scenarios whose "model" lives in its own simulated lab module (no MockClaude call) ──
# D1.6 utils/handoff_lab.py · D1.7 utils/memory_lab.py · D1.8 utils/decomp_lab.py
MODULE_SCENARIOS: dict[str, Scenario] = {s.id: s for s in [
    Scenario("cited_report", "Synthesis needs 6 findings with their sources",
             "Three search agents found 6 claims, each with a source URL, document and page. The synthesis agent must write "
             "a report that cites every claim.", "DELIVERED", _chitchat),
    Scenario("long_research", "Long research — 24 findings, bulky transcripts",
             "24 findings this time. The search agents' full transcripts (every call, every raw page) are also available.",
             "DELIVERED", _chitchat),
    Scenario("next_phase", "Phase 2 of a codebase exploration",
             "Phase 1 mapped the refund flow. A new agent now traces ledger.post_refund's dependencies.", "DELIVERED", _chitchat),
    Scenario("crash_resume", "An exploration agent crashed mid-way",
             "Before the crash it exported its state (files done, the next step, notes). Resume it.", "DELIVERED", _chitchat),
    Scenario("new_teammate", "A new teammate clones the repo",
             "They start Claude Code at the repository root. Do they receive the team's rules?", "DELIVERED", _chitchat),
    Scenario("package_standards", "Per-package standards",
             "Billing and web have different maintainers and standards. Each package should load only its own.", "DELIVERED", _chitchat),
    Scenario("split_rules", "The instructions have grown large",
             "Testing, deployment and API rules must stay in effect, with API rules only for src/api code — and no CLAUDE.md over 200 lines.",
             "DELIVERED", _chitchat),
    Scenario("agents_md", "The repo already has an AGENTS.md",
             "Other coding tools read AGENTS.md. Once the team adds a CLAUDE.md, does Claude Code still follow AGENTS.md?",
             "DELIVERED", _chitchat),
    Scenario("large_review", "Review a 14-file change",
             "Three files each have a local bug, and orders.py no longer matches pricing.py's new signature (a cross-file bug).",
             "DELIVERED", _chitchat),
    Scenario("small_review", "Review a 3-file change",
             "One local bug and the same cross-file mismatch, in just three files.", "DELIVERED", _chitchat),
    Scenario("legacy_tests", "Add tests to a legacy codebase",
             "Six modules of unknown importance, six actions of budget. One high-risk module hides a dependency you only discover "
             "when you try to test it.", "DELIVERED", _chitchat),
    Scenario("similar_tools", "Similar tools: web results vs documents",
             "Two requests bring web search results, two bring uploaded/attached documents. Can your definitions tell them apart?",
             "DELIVERED", _chitchat),
    Scenario("generic_tool", "Three different jobs on documents",
             "Extract exact values, summarise, and check a claim — each needs a different output.", "DELIVERED", _chitchat),
    Scenario("keyword_prompt", "A request that says “document” but brings web results",
             "Does anything in your system prompt override the tool descriptions?", "DELIVERED", _chitchat),
    Scenario("edge_cases", "Input formats and boundaries",
             "“order 1001” (the id format is ORD-####) and an order identified only by email.", "DELIVERED", _chitchat),
    Scenario("must_extract", "A chatty invoice email",
             "An invoice arrives inside a friendly email. The pipeline needs structured fields every time — not a reply.", "DELIVERED", _chitchat),
    Scenario("unknown_type", "Document type unknown (it's a contract)",
             "Invoice and contract extractors are available; this document happens to be a contract.", "DELIVERED", _chitchat),
    Scenario("missing_fields", "Missing tax id, unforeseen category",
             "The invoice has no tax id and its category (maintenance) isn't one you listed.", "DELIVERED", _chitchat),
    Scenario("metadata_first", "Metadata before enrichment",
             "extract_metadata must run before enrich_vendor, which needs the vendor id it returns.", "DELIVERED", _chitchat),
    Scenario("scoped_tools", "A searcher and a synthesis agent",
             "Give each agent tools for its role. One of the source URLs is a login page, and one figure needs a fact check.",
             "DELIVERED", _chitchat),
    Scenario("model_rejects_forcing", "A model that rejects forced tool use",
             "The same chatty invoice, on a model that returns a 400 for tool_choice any/tool (as the docs list for some models).",
             "DELIVERED", _chitchat),
    # D2.3 MCP (utils/mcp_lab.py)
    Scenario("team_server", "A teammate clones the repo",
             "The team's GitHub, Jira and refund-platform servers must work for a teammate - without committing a token.",
             "DELIVERED", _chitchat),
    Scenario("personal_server", "Your experimental server",
             "You're trying out a notes server of your own. It should load for you, and nobody else.", "DELIVERED", _chitchat),
    Scenario("grep_preferred", "Callers across services",
             "“Find every caller of process_refund across our services” - the team's MCP tool can search every repo; Grep can't.",
             "DELIVERED", _chitchat),
    Scenario("catalog", "Which table?", "“Which table stores refund approvals?” - the database has many tables.",
             "DELIVERED", _chitchat),
    Scenario("transient_timeout", "The order service times out",
             "The order service times out twice, then answers.", "DELIVERED", _chitchat),
    Scenario("policy_violation", "A refund over the limit",
             "The customer asks for a $900 refund; policy caps refunds at $500 without a manager.", "DELIVERED", _chitchat),
    Scenario("empty_result", "A customer with no orders", "The order query succeeds - and finds nothing.", "DELIVERED", _chitchat),
    Scenario("access_failure", "The service account lacks access",
             "The order service refuses the request (permission) every time.", "DELIVERED", _chitchat),
    # D2.4 SDK Hooks (utils/hooks_lab.py)
    Scenario("refund_pressure", "An $800 refund, “already approved”",
             "The customer claims a manager approved an $800 refund; policy caps refunds at $500 without a human.",
             "DELIVERED", _chitchat),
    Scenario("refund_small", "A $120 refund", "An ordinary refund under the limit - it must go through.", "DELIVERED", _chitchat),
    Scenario("mixed_formats", "Invoice vs renewal",
             "The billing server returns Unix seconds and numeric status codes; the CRM returns ISO 8601 dates.",
             "DELIVERED", _chitchat),
]}
SCENARIOS.update(MODULE_SCENARIOS)

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
        system_text = system if isinstance(system, str) else " ".join(
            str(_get(b, "text", "")) for b in (system or []))
        first = _blocks(_get(messages[0], "content"))
        prompt_text = " ".join(str(_get(b, "text", "")) for b in first if _get(b, "type") == "text")
        tool_names = tuple(_get(t, "name") for t in (tools or []))
        user_texts = tuple(" ".join(str(_get(b, "text", "")) for b in _blocks(_get(m, "content")) if _get(b, "type") == "text")
                           for m in messages if _get(m, "role") == "user"
                           and any(_get(b, "type") == "text" for b in _blocks(_get(m, "content"))))
        new_turn = any(_get(b, "type") == "text" for b in _blocks(_get(messages[-1], "content")))
        ctx = Ctx(model, max_tokens, conv.resumed, system_text, prompt_text, tool_names, user_texts, new_turn,
                  tuple(tools or []))
        turn = self._scenario.behavior(conv.seen, ctx)
        if conv.text_after_results:
            # Docs (handling-stop-reasons): text added right after tool results can teach Claude to
            # expect more input, producing an EMPTY response with end_turn. Deterministic here.
            turn = Turn(empty=True)

        stop_details = None
        stop_seq = None
        if turn.empty:
            content, stop_reason = [], "end_turn"
        elif turn.special == "max_tokens_tool":   # cut off mid tool call: the last block is an INCOMPLETE tool_use
            content = [TextBlock(turn.text), ToolUseBlock(f"toolu_sim_{next(_ID_COUNTER):03d}", "process_refund",
                                                         {"order_id": "ORD-10"})]
            stop_reason = "max_tokens"
        elif turn.special == "context_full":       # valid partial content; generation stopped at the context window
            content, stop_reason = [TextBlock(turn.text)], "model_context_window_exceeded"
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
            for name, args in (turn.tools or [turn.tool]):
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
            # multi-agent trace fields (which ROLE made this call, what it could see and was offered)
            "role": _role(ctx), "tool_names": list(tool_names), "prompt_head": prompt_text[:200],
            "prompt_has_findings": '"claim"' in prompt_text,
            "n_task_calls": sum(1 for b in content if b.type == "tool_use" and b.name in _TASK_NAMES),
            "seen_chars": sum(len(x.result) for x in conv.seen if x.name in _TASK_NAMES),
            "incomplete_tool": turn.special == "max_tokens_tool",
            "blind_results": sum(1 for x in conv.seen if x.name in _TASK_NAMES and not _informative(x.result)),
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
