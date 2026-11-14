"""
The stop-reason INSPECTOR engine (D1.3 Stop Reason): type a message, pick which condition ends the simulated model's
response, choose HOW YOUR HANDLER decides what to do (the correct branch-on-stop_reason handler, or one of the
distractor policies), and see the raw response plus what your handler did with it.

Trusted workbench code in the Streamlit process. The model is SIMULATED (utils/mock_claude.py); the expected action per
condition comes from the official docs (utils/stop_lab.py, docs fetched 2026-09-26).
"""

from __future__ import annotations

from dataclasses import dataclass

from utils import lab_trace, mock_claude as mc, stop_lab as sl


@dataclass
class StopConfig:
    condition: str = "sr_end_turn"
    handler: str = "correct"            # a key of stop_lab.POLICIES
    max_tokens: int = 60                # per request — only matters on the max_tokens tab
    stop_sequences: str = mc.STOP_SEQUENCE   # your tripwire text (stop_sequence tab)
    mid_tool_call: str = "no"           # max_tokens tab: is the limit hit in the middle of a tool call?


def _block(b) -> dict:
    d = b.to_dict()
    if d["type"] == "text":
        return {"type": "text", "text": d["text"]}
    return {"type": d["type"], "name": d["name"], "input": d["input"]}


def run_stop(user_text: str, cfg: StopConfig) -> dict:
    lab_trace.reset()
    mc.reset()
    sid = "sr_max_tokens_tool" if (cfg.condition == "sr_max_tokens" and cfg.mid_tool_call == "yes") else cfg.condition
    max_tokens = cfg.max_tokens if sid in ("sr_max_tokens", "sr_max_tokens_tool") else 1024
    seqs = [cfg.stop_sequences] if (sid == "sr_stop_sequence" and cfg.stop_sequences.strip()) else None
    request = {"model": "mock-claude", "max_tokens": max_tokens, "stop_sequences": seqs,
               "messages": [{"role": "user", "content": user_text}]}
    client = mc.MockClaude(sid)
    out = {"scenario": sid, "request": request, "raised": None, "response": None, "http": "200 (a successful response)"}
    expected = sl.EXPECTED[sid]

    try:
        r = client.messages.create(model="mock-claude", max_tokens=max_tokens, tools=sl.TOOLS,
                                   messages=request["messages"], stop_sequences=seqs)
    except mc.MockAPIError as e:
        out["raised"] = f"{type(e).__name__}: {e}"
        out["http"] = "529 (simulated API error — no response body to inspect)"
        chosen = "crash" if cfg.handler == "no_try" else "handle_api_error"
    else:
        out["response"] = {"stop_reason": r.stop_reason, "stop_details": r.stop_details, "stop_sequence": r.stop_sequence,
                           "content": [_block(b) for b in r.content],
                           "usage": {"input_tokens": r.usage.input_tokens, "output_tokens": r.usage.output_tokens}}
        # a stop sequence that never appears (or a max_tokens that is big enough) simply ends normally
        expected = {"end_turn": "finish" if r.content else "continue_new_user_message",
                    "tool_use": "run_tools"}.get(r.stop_reason, sl.EXPECTED.get(sid, expected)) \
            if sid in ("sr_stop_sequence", "sr_max_tokens") and r.stop_reason == "end_turn" else expected
        chosen = sl.POLICIES[cfg.handler][1](out["response"])
    out.update({"action": chosen, "expected": expected, "ok": chosen == expected,
                "chosen_meaning": sl.ACTIONS.get(chosen, "the run crashed / raised: nothing handled this"),
                "expected_meaning": sl.ACTIONS[expected], "consequence": sl.CONSEQUENCE[sid]})
    return out
