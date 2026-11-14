"""
Shared pieces for the stop_reason labs (D1.3 Stop Reason): the request each scenario sends, the action vocabulary a
handler can choose from, the EXPECTED action per scenario, and reference handler policies (correct + the wrong ones the
lab's distractors show) used by the playground.

Every expected action below is what the official docs say to do for that stop reason (fetched 2026-09-26):
platform.claude.com/docs/en/build-with-claude/handling-stop-reasons and .../refusals-and-fallback. The scenarios are
SIMULATED (utils/mock_claude.py).
"""

from __future__ import annotations

from utils import lab_trace
from utils.mock_claude import STOP_SEQUENCE
from utils.tools import TOOL_SCHEMAS

# the action vocabulary: name -> what it means
ACTIONS = {
    "run_tools": "run the requested tool(s) and send tool_result blocks back",
    "finish": "use the response as-is: it is complete",
    "raise_max_tokens": "truncated: raise max_tokens or continue; an incomplete tool_use is retried with a higher limit, never run",
    "retry_other_model": "read stop_details, then retry on a DIFFERENT model and stay on it",
    "resume_as_is": "send the assistant response back unchanged (and keep the tools) to let it continue",
    "read_stop_sequence": "read the stop_sequence field to see which sequence fired, then act on that",
    "treat_truncated": "treat as truncated: the content is valid but limited by the context window; trim or summarise, then continue",
    "continue_new_user_message": "empty end_turn: don't blindly retry — add a continuation prompt as a NEW user message",
    "handle_api_error": "catch it separately: an API error (HTTP 4xx/5xx) is not a stop reason",
    # wrong choices the distractors make (never expected)
    "retry_same_model": "re-send the same request to the same model",
    "retry_same_request": "re-send the identical request unchanged",
}

# scenario -> the action the docs call for
EXPECTED = {
    "sr_tool_use": "run_tools", "sr_end_turn": "finish", "sr_max_tokens": "raise_max_tokens",
    "sr_max_tokens_tool": "raise_max_tokens", "sr_refusal": "retry_other_model", "sr_pause_turn": "resume_as_is",
    "sr_stop_sequence": "read_stop_sequence", "sr_context_window": "treat_truncated",
    "sr_empty_end_turn": "continue_new_user_message", "sr_api_error": "handle_api_error",
}

# what goes wrong when a scenario is mishandled (docs-grounded statements, used by the playground)
CONSEQUENCE = {
    "sr_tool_use": "The response asked for a tool. If you treat it as finished, the work stops and the tool never runs — even though the text sounded final.",
    "sr_end_turn": "Nothing to handle: end_turn is the model finishing on its own signal.",
    "sr_max_tokens": "The text is cut off. Showing it as a finished answer gives users a truncated reply that looks complete.",
    "sr_max_tokens_tool": "The last block is an INCOMPLETE tool_use. Running it executes a tool with partial arguments; the docs say to retry with a higher max_tokens.",
    "sr_refusal": "A refusal is HTTP 200 with empty content: no exception, and error-rate monitoring never sees it. Re-sending to the same model usually refuses again.",
    "sr_pause_turn": "The response ends with an unanswered server tool call. Treating it as final shows unfinished work; the docs say to send it back as-is.",
    "sr_stop_sequence": "Generation halted at your tripwire, not at a natural end. The stop_sequence field says which one fired — and the sequence text is not in the content.",
    "sr_context_window": "The context window filled. The content is valid but truncated: keep sending the same conversation and it will fill again.",
    "sr_empty_end_turn": "The model already decided its turn is complete, so an identical retry stays empty. Fix the message structure, or add a continuation prompt as a NEW user message.",
    "sr_api_error": "A raised API error has no stop_reason to inspect. Without a try/except around the call the whole run crashes.",
}

STATE = {"scenario": "sr_end_turn"}
MAX_TOKENS = 1024
MESSAGES = [{"role": "user", "content": "Customer alice@example.com says order ORD-1001 arrived damaged. Please resolve it."}]
TOOLS = TOOL_SCHEMAS
STOP_SEQUENCES = [STOP_SEQUENCE]


def configure(scenario_id: str) -> None:
    global MAX_TOKENS
    STATE["scenario"] = scenario_id
    MAX_TOKENS = 60 if scenario_id in ("sr_max_tokens", "sr_max_tokens_tool") else 1024


def act(action: str, detail=None) -> None:
    """The lab calls this with the action its handler chose; the page compares it with the docs' action."""
    print(f"ACTION chosen: {action}  ({ACTIONS.get(action, 'not in the action vocabulary')})")
    lab_trace.record({"kind": "action", "action": action, "detail": str(detail)[:200]})


# ── Reference handler policies (the playground applies one to the simulated response) ──────────────────────────────
# Each takes a response-like dict {stop_reason, stop_details, content:[{type,text?}]} and returns an action name.

def _text(r) -> str:
    return " ".join(b.get("text", "") for b in r["content"] if b["type"] == "text")


def _correct(r) -> str:
    reason = r["stop_reason"]
    if reason == "tool_use":
        return "run_tools"
    if reason == "end_turn":
        return "finish" if r["content"] else "continue_new_user_message"
    return {"max_tokens": "raise_max_tokens", "refusal": "retry_other_model", "pause_turn": "resume_as_is",
            "stop_sequence": "read_stop_sequence", "model_context_window_exceeded": "treat_truncated"}[reason]


def _prose_done(r) -> str:
    t = _text(r).lower()
    return "finish" if ("done" in t or "complete" in t) else _correct(r)


def _any_text(r) -> str:
    return "finish" if any(b["type"] == "text" for b in r["content"]) else _correct(r)


def _tool_blocks(r) -> str:
    return "run_tools" if any(b["type"] == "tool_use" for b in r["content"]) else _correct(r)


def _else_finish(r) -> str:
    return "run_tools" if r["stop_reason"] == "tool_use" else "finish"


def _same_model(r) -> str:
    return "retry_same_model" if r["stop_reason"] == "refusal" else _correct(r)


def _blind_retry(r) -> str:
    return "retry_same_request" if (r["stop_reason"] == "end_turn" and not r["content"]) else _correct(r)


def _explanation_text(r) -> str:
    if "declined" in ((r.get("stop_details") or {}).get("explanation") or ""):
        return "retry_other_model"
    if r["stop_reason"] == "refusal":
        return "unhandled"
    return _correct(r)


def _no_try(r) -> str:
    return _correct(r)


POLICIES = {
    "correct": ("✅ branch on stop_reason (correct)", _correct),
    "prose_done": ("⭐❌ finish when the reply says “done” / “complete”", _prose_done),
    "any_text": ("⭐❌ any text block means the final answer", _any_text),
    "tool_blocks": ("❌ look for tool_use blocks instead of stop_reason", _tool_blocks),
    "else_finish": ("❌ anything that isn't tool_use is the final answer", _else_finish),
    "same_model": ("❌ retry a refusal on the SAME model", _same_model),
    "blind_retry": ("❌ blindly retry an empty end_turn", _blind_retry),
    "explanation_text": ("❌ decide from the refusal's explanation text", _explanation_text),
    "no_try": ("❌ no try/except around the API call", _no_try),
}
