"""
SIMULATED long support session for D5.2 Case Facts Block (guide TS 5.1).

Grounding: guide TS 5.1 (read 2026-09-28): progressive summarisation condenses numbers, percentages, dates and
customer-stated expectations into vague summaries (Knowledge 1); extract transactional facts (amounts, dates, order numbers,
statuses) into a persistent "case facts" block included in each prompt, outside summarised history (Skill 1); for multi-issue
sessions, persist structured issue data (order IDs, amounts, statuses) in a separate context layer (Skill 2). Platform
prompting best practices § State management best practices (fetched 2026-09-28): use structured formats such as JSON for
state data, unstructured text for progress notes.
INVENTED (simulation): the events, the summariser (which keeps the gist and drops every number, date and promise), the
"prose note" writer, and the agent that answers the final question from whatever the prompt holds. Every event arrives with
its candidate facts already extracted, so the lab is about how the block is built, not about extraction.
"""

from __future__ import annotations

import json

from utils import lab_trace

SCENARIO_IDS = ("refund_promise", "multi_issue", "status_change", "customer_expectation")
SCENARIO = "refund_promise"
KEEP_RECENT = 2          # the last two events stay word for word; everything older is summarised


def _f(issue, field, value, source):
    return {"issue": issue, "field": field, "value": value, "source": source}


_CHAT = [{"kind": "customer", "text": "Also, can you update my email to customer.a@example.com?", "facts": []},
         {"kind": "agent", "text": "Done - your email is updated.", "facts": []},
         {"kind": "customer", "text": "And please unsubscribe me from the newsletter.", "facts": []},
         {"kind": "agent", "text": "You're unsubscribed.", "facts": []}]

EVENTS = {
    "refund_promise": [
        {"kind": "customer", "text": "Hi, my kettle order ORD-5512 arrived broken.", "facts": [_f("ORD-5512", "item", "kettle", "customer")]},
        {"kind": "tool", "text": "lookup_order -> ORD-5512, total £84.20, delivered",
         "facts": [_f("ORD-5512", "amount", "£84.20", "tool"), _f("ORD-5512", "status", "delivered", "tool")]},
        {"kind": "customer", "text": "I need the money back by Friday 14 March.",
         "facts": [_f("ORD-5512", "customer_deadline", "Friday 14 March", "customer")]},
        {"kind": "tool", "text": "process_refund -> approved, £84.20", "facts": [_f("ORD-5512", "refund_status", "approved", "tool")]},
        {"kind": "agent", "text": "Your refund of £84.20 is approved and marked urgent for Friday 14 March.", "facts": []},
    ] + _CHAT,
    "multi_issue": [
        {"kind": "customer", "text": "Three problems: the lamp ORD-6001, the rug ORD-6002 and a mug ORD-6003.",
         "facts": [_f("ORD-6001", "item", "lamp", "customer"), _f("ORD-6002", "item", "rug", "customer"),
                   _f("ORD-6003", "item", "mug", "customer")]},
        {"kind": "tool", "text": "lookup_order ORD-6001 -> £45.00; replacement shipped",
         "facts": [_f("ORD-6001", "amount", "£45.00", "tool"), _f("ORD-6001", "status", "replacement shipped", "tool")]},
        {"kind": "tool", "text": "lookup_order ORD-6002 -> £120.00; refund pending",
         "facts": [_f("ORD-6002", "amount", "£120.00", "tool"), _f("ORD-6002", "status", "refund pending", "tool")]},
        {"kind": "tool", "text": "lookup_order ORD-6003 -> £9.99; refund approved",
         "facts": [_f("ORD-6003", "amount", "£9.99", "tool"), _f("ORD-6003", "status", "refund approved", "tool")]},
    ] + _CHAT,
    "status_change": [
        {"kind": "customer", "text": "Where's my refund for the headphones, ORD-7020?", "facts": [_f("ORD-7020", "item", "headphones", "customer")]},
        {"kind": "tool", "text": "lookup_refund -> £199.00, pending review",
         "facts": [_f("ORD-7020", "amount", "£199.00", "tool"), _f("ORD-7020", "refund_status", "pending review", "tool")]},
        {"kind": "agent", "text": "It's pending review - I'll check again shortly.", "facts": []},
    ] + _CHAT[:2] + [
        {"kind": "tool", "text": "lookup_refund -> £199.00, approved", "facts": [_f("ORD-7020", "refund_status", "approved", "tool")]},
    ] + _CHAT[2:],
    "customer_expectation": [
        {"kind": "customer", "text": "The suit I ordered, ORD-8100, has a torn seam.", "facts": [_f("ORD-8100", "item", "suit", "customer")]},
        {"kind": "tool", "text": "lookup_order -> ORD-8100, £310.00; standard replacement 5-7 working days; express 2 days available",
         "facts": [_f("ORD-8100", "amount", "£310.00", "tool"), _f("ORD-8100", "replacement_options", "standard 5-7 days; express 2 days", "tool")]},
        {"kind": "customer", "text": "I need it before my wedding on Saturday 5 April - that's non-negotiable.",
         "facts": [_f("ORD-8100", "customer_deadline", "Saturday 5 April (wedding)", "customer")]},
    ] + _CHAT,
}

FINAL = {
    "refund_promise": ("Sorry - can you confirm how much I'm getting back and by when?", "ORD-5512", ["£84.20", "Friday 14 March"]),
    "multi_issue": ("What's happening with the lamp?", "ORD-6001", ["£45.00", "replacement shipped"]),
    "status_change": ("Has my refund been approved yet?", "ORD-7020", ["approved"]),
    "customer_expectation": ("So what will you do about my suit?", "ORD-8100", ["express", "Saturday 5 April"]),
}


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "refund_promise"


def summarize(events: list) -> str:
    """A SIMULATED progressive summary: keeps the gist, loses the numbers, dates, statuses and promises."""
    return ("Summary of earlier conversation: the customer contacted us about one or more orders; the agent looked them up "
            "and is handling refunds or replacements; the customer updated some account details.") if events else ""


def prose_note(facts: dict) -> str:
    """A SIMULATED free-text note the model writes about the case - readable, but vague."""
    return "Case notes: customer is owed some money back soon on their order(s); some items being replaced; customer is in a hurry."


def _answer(prompt: list, final: tuple) -> tuple:
    question, issue, _need = final
    facts, fmt = None, "none"
    for m in prompt:
        c = str(m.get("content", ""))
        if c.startswith("CASE FACTS"):
            body = c.split("\n", 1)[1] if "\n" in c else ""
            try:
                facts, fmt = json.loads(body), "json"
            except ValueError:
                fmt = "prose"
    rec = (facts or {}).get(issue) if isinstance(facts, dict) else None
    if isinstance(facts, dict) and rec is None and any(k in facts for k in ("amount", "status", "refund_status", "item")):
        rec, fmt = facts, "json-flat"                    # a single flat block (no per-issue keys)
    rec = rec or {}
    if SCENARIO == "refund_promise":
        a, d = rec.get("amount"), rec.get("customer_deadline")
        return (f"You're getting {a} back, marked urgent for {d}." if a and d else
                f"You're getting {a} back soon." if a else "Your refund is on its way and should arrive soon."), fmt, facts
    if SCENARIO == "multi_issue":
        a, s = rec.get("amount"), rec.get("status")
        return (f"For the lamp: {a}, {s}." if a and s else "I'm looking into your orders and will update you soon."), fmt, facts
    if SCENARIO == "status_change":
        s = rec.get("refund_status")
        return (f"Your £199.00 refund is {s}." if s else "Your refund is being processed."), fmt, facts
    d = rec.get("customer_deadline")
    return (f"I'll send an express replacement (2 days) so it arrives before your wedding on {d.split(' (')[0]}." if d
            else "I'll send a replacement - it will arrive in 5-7 working days."), fmt, facts


def run_session(update_facts, build_prompt) -> str:
    """Plays the session. After each event your update_facts(facts, event) returns the facts; at the end your
    build_prompt(facts, summary, recent) returns the messages the model sees for the customer's final question."""
    events = EVENTS[SCENARIO]
    facts: dict = {}
    for ev in events:
        facts = update_facts(facts, ev)
        if facts is None:
            raise ValueError("update_facts must return the facts")
    older, recent = events[:-KEEP_RECENT], events[-KEEP_RECENT:]
    summary = [{"role": "user", "content": summarize(older)}] if older else []
    recent_msgs = [{"role": "assistant" if e["kind"] == "agent" else "user", "content": e["text"]} for e in recent]
    question = FINAL[SCENARIO][0]
    prompt = build_prompt(facts, summary, recent_msgs + [{"role": "user", "content": question}])
    reply, fmt, seen = _answer(prompt, FINAL[SCENARIO])
    need = FINAL[SCENARIO][2]
    missing = [n for n in need if n not in reply]
    rec = {"kind": "casefacts_run", "scenario": SCENARIO, "format": fmt, "facts": seen if seen is not None else None,
           "reply": reply, "need": need, "missing": missing, "ok": not missing, "question": question}
    lab_trace.record(rec)
    print(f"case facts in the prompt: {fmt}")
    if seen is not None:
        print(json.dumps(seen, ensure_ascii=False)[:400])
    print(f"customer: {question}\nagent: {reply}")
    return reply
