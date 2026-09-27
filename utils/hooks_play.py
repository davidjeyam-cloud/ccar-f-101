"""
Playground engine for D2.4 SDK Hooks, on the SIMULATED Agent SDK runner and support agent in utils/hooks_lab.py (see its
docstring for what is documented vs invented). Hooks are built from the tab's knobs; the customer message drives the agent.
"""

from __future__ import annotations

from dataclasses import dataclass

from utils import hooks_lab as hl
from utils import lab_trace


@dataclass
class HooksConfig:
    mode: str = "hook_vs_prompt"
    enforcement: str = "hook"        # hook | prompt | both
    deny_reason: str = "redirect"    # redirect | reason_only | none
    normalize: str = "hook"          # hook | prompt | none
    pre_matcher: str = "mcp__billing__process_refund"
    logger: str = "allow"            # allow | none
    policy_mode: str = "sync"        # sync | async
    policy_event: str = "PreToolUse" # PreToolUse | PostToolUse


_STATUS = {0: "draft", 1: "open", 2: "overdue", 3: "paid"}


def _policy(reason_style="redirect", async_=False):
    def enforce_refund_limit(input_data, tool_use_id, context):
        if async_:
            return {"async_": True}
        if input_data["tool_input"].get("amount", 0) > 500:
            hso = {"hookEventName": input_data["hook_event_name"], "permissionDecision": "deny"}
            if reason_style == "redirect":
                hso["permissionDecisionReason"] = ("Refunds over $500 need a human. Call mcp__support__escalate_to_human "
                                                   "with a summary instead.")
            elif reason_style == "reason_only":
                hso["permissionDecisionReason"] = "Refunds over $500 are not allowed."
            return {"hookSpecificOutput": hso}
        return {}
    return enforce_refund_limit


def _audit_logger(input_data, tool_use_id, context):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
                                   "permissionDecisionReason": "audit logger: logged, no objection"}}


def _normalize(input_data, tool_use_id, context):
    from datetime import datetime, timezone
    out = dict(input_data["tool_response"])
    for k, v in out.items():
        if k.endswith("_date") and isinstance(v, (int, float)):
            out[k] = datetime.fromtimestamp(v, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(out.get("status"), int):
        out["status"] = _STATUS.get(out["status"], f"unknown({out['status']})")
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": out}}


def run_hooks(message: str, cfg: HooksConfig) -> dict:
    lab_trace.reset()
    H = hl.HookMatcher
    system = hl.SYSTEM_PROMPT
    pre, post = [], [H(matcher="mcp__.*", hooks=[_normalize])]
    if cfg.mode == "hook_vs_prompt":
        if cfg.enforcement == "hook":
            system = "You are a support agent for Example Corp."
        if cfg.enforcement in ("hook", "both"):
            pre.append(H(matcher="mcp__billing__process_refund", hooks=[_policy()]))
    elif cfg.mode == "block_redirect":
        pre.append(H(matcher="mcp__billing__process_refund", hooks=[_policy(cfg.deny_reason)]))
    elif cfg.mode == "normalize":
        pre.append(H(matcher="mcp__billing__process_refund", hooks=[_policy()]))
        if cfg.normalize != "hook":
            post = []
        if cfg.normalize == "prompt":
            system += " Billing dates are Unix seconds; billing status 2 means overdue."
    elif cfg.mode == "matchers":
        pre.append(H(matcher=cfg.pre_matcher, hooks=[_policy()]))
    elif cfg.mode == "multi_hooks":
        if cfg.logger == "allow":
            pre.append(H(hooks=[_audit_logger]))
        pre.append(H(matcher="mcp__billing__process_refund", hooks=[_policy(async_=cfg.policy_mode == "async")]))
    else:  # pre_vs_post
        (pre if cfg.policy_event == "PreToolUse" else post).append(H(matcher="mcp__billing__process_refund", hooks=[_policy()]))
    hooks = {"PreToolUse": pre, "PostToolUse": post}
    msg = message.strip() or hl.MESSAGES["refund_pressure"]
    rec = hl._Agent(system, hooks, msg).run()
    lines = [f"System prompt: “{system}”",
             "Hooks registered: " + (", ".join(f"{ev} matcher={m.matcher!r} → {[f.__name__ for f in m.hooks]}"
                                              for ev, ms in hooks.items() for m in ms) or "none")]
    if cfg.mode == "matchers":
        lines.append(f"Does {cfg.pre_matcher!r} match 'mcp__billing__process_refund'? "
                     f"{'yes' if hl.matches(cfg.pre_matcher, 'mcp__billing__process_refund') else 'NO'} · matches "
                     f"'mcp__billing__get_invoice'? {'yes' if hl.matches(cfg.pre_matcher, 'mcp__billing__get_invoice') else 'no'}")
    for c in rec["calls"]:
        extra = f" · reason → model: “{c['reason']}”" if c.get("reason") else (f" · {c['note']}" if c.get("note") else "")
        lines.append(f"{c['tool']}({c['input']}) → {c['result']}{extra}")
    lines += [f"Hooks fired: {rec['fired'] or 'none'}", f"Refunds executed: {rec['ledger'] or 'none'} · escalations: {len(rec['escalations'])}",
              f"Agent: “{rec['answer']}”"]
    notes = []
    if any(a > 500 for a in rec["ledger"]):
        notes.append("A refund above $500 was executed.")
    if rec["refund_attempts"] > 1:
        notes.append(f"The model retried the denied refund {rec['refund_attempts']}× — it wasn't told why.")
    asked_refund = "refund" in msg.lower()
    if asked_refund and not rec["ledger"] and not rec["escalations"]:
        notes.append("Blocked, but not redirected: nobody will handle the request.")
    if asked_refund and rec["escalations"] and not any(a > 500 for a in rec["ledger"]):
        import re
        m = re.search(r"\$\s?(\d+(?:\.\d+)?)", msg)
        if m and float(m.group(1)) <= 500:
            notes.append("A refund within policy was blocked.")
    if not asked_refund and "invoice is due first" not in rec["answer"]:
        notes.append("The agent misread the mixed formats.")
    return {"lines": lines, "notes": notes, "ok": not notes}
