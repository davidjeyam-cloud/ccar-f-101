"""
Playground engine for D1.5 Human-in-the-Loop Escalation: type the customer's message, choose the developer-side settings
(which escalation criteria the system prompt contains, how a human request is handled, what to do with several matches,
whether verification is a CODE gate or only a prompt line, and the handoff format), and watch the simulated support
agent handle it. Trusted workbench code in the Streamlit process; the model is the SIMULATED keyword-driven support agent
in utils/mock_claude.py and the backend is utils/support_lab.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from utils import lab_trace, mock_claude as mc, support_lab as sb

MAX_TURNS = 14


@dataclass
class EscalationConfig:
    scenario: str = "frustrated_simple"      # which backend state + scripted follow-ups the tab uses
    triggers: str = "explicit"               # explicit | sentiment | confidence | complex
    human_request: str = "immediate"         # immediate | investigate_first
    matches: str = "ask"                     # ask | pick_recent
    gate: str = "code"                       # code | prompt_only
    handoff: str = "structured"              # structured | free_text


def build_system(cfg: EscalationConfig) -> str:
    lines = ["ROLE: support agent. Resolve customer issues within policy."
             + (" Always verify the customer with get_customer before any refund." if cfg.gate == "prompt_only" else "")]
    human = ("1. The customer asks for a human -> escalate immediately, before investigating anything."
             if cfg.human_request == "immediate" else
             "1. The customer asks for a human -> first investigate the issue fully, then escalate.")
    if cfg.triggers == "explicit":
        lines += ["<escalation_criteria>", "Call escalate_to_human when ANY of these applies:", human,
                  "2. The policy is ambiguous or silent on what the customer asks for -> escalate.",
                  "3. You cannot make meaningful progress (tools keep failing) -> escalate.",
                  "Do not escalate just because the customer is frustrated: acknowledge it and offer to resolve; escalate only if "
                  "they then ask for a human again."]
    elif cfg.triggers == "sentiment":
        lines += ["<escalation_criteria>", human, "Escalate to a human whenever the customer is upset or frustrated."]
    elif cfg.triggers == "confidence":
        lines += ["<escalation_criteria>", human, "Otherwise report your confidence from 0 to 1 and escalate when it is below 0.7."]
    else:
        lines += ["<escalation_criteria>", "Escalate complex cases to a human; resolve the rest yourself."]
    lines.append("If a customer lookup returns more than one match, ask for another identifier (email or order number) - never guess."
                 if cfg.matches == "ask" else
                 "If a customer lookup returns more than one match, pick the one with the most recent order.")
    lines.append("</escalation_criteria>")
    if cfg.triggers == "explicit":
        lines += ["<examples>", '<example>"Get me a manager now." -> escalate_to_human at once.</example>',
                  '<example>"Third damaged kettle, I\'m furious!" (refund within policy) -> apologise, verify, offer the refund.</example>',
                  '<example>"Will you match Competitor X\'s price?" (policy covers only our own price drops) -> escalate_to_human.</example>',
                  "</examples>"]
    return "\n".join(lines)


def run_escalation(message: str, cfg: EscalationConfig) -> dict:
    lab_trace.reset()
    mc.reset()
    sb.configure(cfg.scenario, first_message=message)
    system = build_system(cfg)
    tools = sb.TOOLS if cfg.handoff == "structured" else sb.TOOLS_FREETEXT_HANDOFF
    client = mc.MockClaude(cfg.scenario)
    verified: set = set()
    steps = [("customer", message)]
    messages = [{"role": "user", "content": message}]
    error = None
    for _ in range(MAX_TURNS):
        r = client.messages.create(model=mc.PRIMARY_MODEL, max_tokens=1024, system=system, tools=tools, messages=messages)
        text = "".join(b.text for b in r.content if b.type == "text")
        if r.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": r.content})
            results = []
            for b in r.content:
                if b.type != "tool_use":
                    continue
                if cfg.gate == "code" and b.name == "process_refund" and b.input.get("customer_id") not in verified:
                    out = "BLOCKED: process_refund needs a customer verified by get_customer first."
                    steps.append(("blocked", f"{b.name}({b.input}) → {out}"))
                else:
                    out = sb.execute_tool(b.name, b.input)
                    if b.name == "get_customer" and out.startswith("{"):
                        verified.add(json.loads(out)["customer_id"])
                    steps.append(("tool", f"{b.name}({b.input}) → {out[:110]}"))
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
            if text:
                steps.insert(len(steps) - len(results), ("agent_note", text))
            messages.append({"role": "user", "content": results})
            continue
        steps.append(("agent", text))
        nxt = sb.next_customer_message()
        if nxt is None:
            break
        steps.append(("customer", nxt))
        messages.append({"role": "assistant", "content": r.content})
        messages.append({"role": "user", "content": nxt})
    else:
        error = f"no resolution within {MAX_TURNS} model calls"

    ev = lab_trace.EVENTS
    esc_i = next((i for i, e in enumerate(ev) if e["kind"] == "tool_exec" and e["name"] == "escalate_to_human"), None)
    tools_before = sum(1 for e in ev[:esc_i] if e["kind"] == "tool_exec") if esc_i is not None else None
    handoffs, refunds = sb.LEDGER["handoffs"], sb.LEDGER["refunds"]
    notes = []
    if any(not r["verified_first"] for r in refunds):
        notes.append("A refund was issued to a customer who had NOT been verified first.")
    if handoffs and not sb.handoff_complete(handoffs[-1]):
        notes.append("The handoff is missing fields a human needs (customer id, root cause, refund amount, recommended action).")
    if esc_i is not None and tools_before and any(w in message.lower() for w in mc._HUMAN_WORDS):
        notes.append(f"The customer asked for a human, but {tools_before} tool call(s) ran before the escalation.")
    follow_ups_before = sum(1 for e in ev[:esc_i] if e["kind"] == "customer") if esc_i is not None else None
    asked_human = any(w in message.lower() for w in mc._HUMAN_WORDS)
    policy_request = "match" in message.lower()
    if esc_i is not None and follow_ups_before == 0 and not (asked_human or policy_request or cfg.scenario == "no_progress"):
        notes.append("Escalated on the first message although the customer didn't ask for a human and the request is within "
                     "policy — tone, self-reported confidence or “looks complex” is not a reason to escalate.")
    if policy_request and refunds:
        notes.append("The policy is silent on competitor price matching, yet the agent granted an adjustment itself instead of escalating.")
    if error:
        notes.append(f"The agent never finished ({error}).")
    return {"steps": steps, "system": system, "handoffs": [dict(h) for h in handoffs], "refunds": [dict(r) for r in refunds],
            "escalated": bool(handoffs), "tools_before": tools_before, "notes": notes}
