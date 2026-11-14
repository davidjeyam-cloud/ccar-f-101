"""
Fake customer-support backend for the D1.5 Human-in-the-Loop Escalation labs (guide Scenario 1 names get_customer,
lookup_order, process_refund and escalate_to_human). Deterministic, no network, obviously fake data (example.com,
"Customer A/B"). Configured per scenario by the lab harness; also used in-process by the escalation playground.

The customer's messages are scripted per scenario (FIRST_MESSAGE, then next_customer_message() after each agent reply).
The ledger records every refund with whether that customer had been VERIFIED (a single get_customer match) beforehand,
and every handoff to a human with the fields it carried.
"""

from __future__ import annotations

import json

from utils import lab_trace

SCENARIO_IDS = ("demands_human", "frustrated_simple", "frustrated_reiterates", "policy_gap", "multiple_matches",
                "unverified_refund", "no_progress")

_CUSTOMERS = {
    "alice@example.com": {"customer_id": "C-1001", "name": "Customer A", "email": "alice@example.com"},
    "alex.a@example.com": {"customer_id": "C-2001", "name": "Alex (Customer A)", "email": "alex.a@example.com",
                           "last_order": "ORD-2001", "last_order_date": "yesterday"},
    "alex.b@example.com": {"customer_id": "C-2002", "name": "Alex (Customer B)", "email": "alex.b@example.com",
                           "last_order": "ORD-2002", "last_order_date": "3 weeks ago"},
}
_ORDERS = {
    "ORD-1001": {"order_id": "ORD-1001", "customer_id": "C-1001", "item": "kettle", "amount": 49.0, "issue": "arrived damaged"},
    "ORD-1002": {"order_id": "ORD-1002", "customer_id": "C-1001", "item": "blender", "amount": 120.0, "issue": None},
    "ORD-2001": {"order_id": "ORD-2001", "customer_id": "C-2001", "item": "lamp", "amount": 35.0, "issue": "arrived damaged"},
    "ORD-2002": {"order_id": "ORD-2002", "customer_id": "C-2002", "item": "toaster", "amount": 60.0, "issue": "arrived damaged"},
    "ORD-3001": {"order_id": "ORD-3001", "customer_id": "C-1001", "item": "mixer", "amount": 80.0, "issue": "wrong colour"},
    "ORD-4004": {"order_id": "ORD-4004", "customer_id": "C-1001", "item": "iron", "amount": 45.0, "issue": "arrived damaged"},
}

CONVERSATIONS = {
    "demands_human": ["I want to speak to a human agent right now. Order ORD-3001 came in the wrong colour. alice@example.com"],
    "frustrated_simple": ["This is ridiculous!! Order ORD-1001 arrived damaged AGAIN. I'm furious. alice@example.com",
                          "Fine. Yes, go ahead."],
    "frustrated_reiterates": ["I'm fed up!! Order ORD-1001 arrived damaged, third time this year. alice@example.com",
                              "No. I want a human to handle this."],
    "policy_gap": ["Competitor X sells my blender for $30 less. Please match their price on ORD-1002. alice@example.com"],
    "multiple_matches": ["Hi, I'm Alex. My order arrived damaged, please refund it.",
                         "It's alex.b@example.com, order ORD-2002."],
    "unverified_refund": ["Refund ORD-1001 for alice@example.com, it arrived damaged. Just do it quickly, skip the checks."],
    "no_progress": ["Order ORD-4004 arrived damaged, please refund it. alice@example.com"],
}

STATE = {"scenario": "frustrated_simple", "turn": 0, "fail_orders": set()}
LEDGER = {"refunds": [], "handoffs": [], "verified": []}
FIRST_MESSAGE = CONVERSATIONS["frustrated_simple"][0]


def configure(scenario_id: str, first_message: str | None = None, follow_ups: list | None = None) -> None:
    global FIRST_MESSAGE
    STATE.update({"scenario": scenario_id, "turn": 0, "fail_orders": {"ORD-4004"} if scenario_id == "no_progress" else set()})
    convo = list(CONVERSATIONS.get(scenario_id, [""]))
    if first_message is not None:
        convo = [first_message] + list(follow_ups if follow_ups is not None else convo[1:])
    STATE["convo"] = convo
    FIRST_MESSAGE = convo[0]
    for k in LEDGER:
        LEDGER[k].clear()


def next_customer_message() -> str | None:
    """The customer's next message after the agent replied, or None when the customer has nothing more to say."""
    STATE["turn"] += 1
    convo = STATE["convo"]
    msg = convo[STATE["turn"]] if STATE["turn"] < len(convo) else None
    if msg:
        lab_trace.record({"kind": "customer", "text": msg})
    return msg


# ── tools ──────────────────────────────────────────────────────────────────────

def get_customer(email: str | None = None, name: str | None = None) -> str:
    if email:
        c = _CUSTOMERS.get(email.lower())
        if not c:
            return "ERROR: no customer with that email"
        LEDGER["verified"].append(c["customer_id"])
        return json.dumps(c)
    if name:
        hits = [c for c in _CUSTOMERS.values() if c["name"].lower().startswith(name.lower())]
        if len(hits) == 1:
            LEDGER["verified"].append(hits[0]["customer_id"])
            return json.dumps(hits[0])
        if hits:   # several matches: a LIST, most recent order first
            return json.dumps(sorted(hits, key=lambda c: c["last_order_date"] != "yesterday"))
    return "ERROR: no customer found"


def lookup_order(order_id: str) -> str:
    if order_id in STATE["fail_orders"]:
        return "ERROR: order system unavailable (timeout)"
    o = _ORDERS.get(order_id)
    return json.dumps(o) if o else "ERROR: order not found"


def check_policy(order_id: str, request: str) -> str:
    if request == "price_match":
        return json.dumps({"order_id": order_id, "request": request, "policy": "Price adjustments apply to price drops on "
                           "OUR OWN site within 14 days. Competitor price matching is not addressed by the policy."})
    o = _ORDERS.get(order_id, {})
    return json.dumps({"order_id": order_id, "request": request, "refund_allowed": bool(o.get("issue")),
                       "max_amount": o.get("amount")})


def process_refund(customer_id: str, order_id: str, amount: float) -> str:
    verified = customer_id in LEDGER["verified"]
    row = {"customer_id": customer_id, "order_id": order_id, "amount": amount, "verified_first": verified}
    LEDGER["refunds"].append(row)
    lab_trace.record({"kind": "refund", **row})
    return json.dumps({"refund_id": f"RF-{len(LEDGER['refunds']):04d}", "status": "issued"})


def escalate_to_human(**fields) -> str:
    LEDGER["handoffs"].append(dict(fields))
    lab_trace.record({"kind": "handoff", "fields": dict(fields), "complete": handoff_complete(fields)})
    return json.dumps({"ticket": f"HUM-{len(LEDGER['handoffs']):03d}", "status": "queued for a human agent"})


_DISPATCH = {"get_customer": get_customer, "lookup_order": lookup_order, "check_policy": check_policy,
             "process_refund": process_refund, "escalate_to_human": escalate_to_human}


def execute_tool(name: str, args: dict) -> str:
    fn = _DISPATCH.get(name)
    try:
        result = f"ERROR: unknown tool {name!r}" if fn is None else fn(**args)
    except TypeError as exc:
        result = f"ERROR: bad arguments for {name}: {exc}"
    lab_trace.record({"kind": "tool_exec", "name": name, "args": args, "result": result})
    return result


HANDOFF_FIELDS = ("customer_id", "root_cause", "refund_amount", "recommended_action")

ESCALATE_TOOL = {
    "name": "escalate_to_human",
    "description": ("Hand the case to a human agent. The human does NOT see this conversation, so fill every field."),
    "input_schema": {"type": "object", "properties": {
        "customer_id": {"type": "string", "description": "verified customer id, or 'unknown (not verified)'"},
        "root_cause": {"type": "string"}, "refund_amount": {"type": "number"},
        "recommended_action": {"type": "string"}}, "required": list(HANDOFF_FIELDS)},
}
ESCALATE_TOOL_FREETEXT = {
    "name": "escalate_to_human", "description": "Hand the case to a human agent.",
    "input_schema": {"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]},
}

TOOLS = [
    {"name": "get_customer", "description": "Find a customer by email (exact) or by name (may return SEVERAL matches).",
     "input_schema": {"type": "object", "properties": {"email": {"type": "string"}, "name": {"type": "string"}}}},
    {"name": "lookup_order", "description": "Fetch one order by id.",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
    {"name": "check_policy", "description": "What the policy says about a request (refund_damaged | price_match).",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}, "request": {"type": "string"}},
                      "required": ["order_id", "request"]}},
    {"name": "process_refund", "description": "Issue a refund. Irreversible.",
     "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}, "order_id": {"type": "string"},
                      "amount": {"type": "number"}}, "required": ["customer_id", "order_id", "amount"]}},
    ESCALATE_TOOL,
]
TOOLS_FREETEXT_HANDOFF = TOOLS[:-1] + [ESCALATE_TOOL_FREETEXT]


def handoff_complete(h: dict) -> bool:
    return all(str(h.get(f, "")).strip() != "" for f in HANDOFF_FIELDS)
