"""
Fake customer-support backend — deterministic, no network, no real data
(CLAUDE.md "Tools" section). Tool names mirror the official guide's
Scenario 1 (get_customer, lookup_order, process_refund) so the labs feel like
the exam's own scenario; check_policy and send_confirmation are extra fakes
that give longer tool chains for the labs.

All data is obviously fake ("Customer A", example.com). The backend is
DELIBERATELY permissive — process_refund happily refunds an already-refunded
order and only flags it in the ledger — so a learner's bug shows up as a
visible consequence instead of being hidden by a well-behaved backend.

State lives in module globals and is reset per run: labs execute in a fresh
subprocess (utils/lab_runner.py), so nothing persists between runs.
"""

import json

from utils import lab_trace

# what the lab UI reads back after a run
LEDGER: dict[str, list] = {"refunds": [], "confirmations": []}

_ORDERS: dict[str, dict] = {}


def configure(order_status: str = "DELIVERED") -> None:
    """(Re)initialise backend state. order_status is the state of ORD-1001."""
    LEDGER["refunds"].clear()
    LEDGER["confirmations"].clear()
    _ORDERS.clear()
    _ORDERS["ORD-1001"] = {
        "order_id": "ORD-1001",
        "customer_id": "C-1001",
        "status": order_status,
        "amount": 49.0,
        "issue": "arrived damaged",
    }


configure()  # sensible default when imported outside the harness


def get_customer(email: str) -> str:
    if email == "alice@example.com":
        return json.dumps({"customer_id": "C-1001", "name": "Customer A",
                           "email": email, "tier": "standard"})
    return "ERROR: no customer with that email"


def lookup_order(order_id: str) -> str:
    order = _ORDERS.get(order_id)
    return json.dumps(order) if order else "ERROR: order not found"


def check_policy(order_id: str) -> str:
    order = _ORDERS.get(order_id)
    if not order:
        return "ERROR: order not found"
    return json.dumps({"order_id": order_id,
                       "refund_allowed": order["status"] != "REFUNDED",
                       "window_days_left": 12})


def process_refund(order_id: str, amount: float) -> str:
    order = _ORDERS.get(order_id)
    if not order:
        return "ERROR: order not found"
    duplicate = order["status"] == "REFUNDED"
    LEDGER["refunds"].append({"order_id": order_id, "amount": amount, "duplicate": duplicate})
    order["status"] = "REFUNDED"
    return json.dumps({"refund_id": f"RF-{len(LEDGER['refunds']):04d}", "status": "issued",
                       "warning": "order was already refunded" if duplicate else None})


def send_confirmation(customer_id: str, message: str) -> str:
    LEDGER["confirmations"].append({"customer_id": customer_id, "message": message})
    return json.dumps({"status": "sent", "customer_id": customer_id})


_DISPATCH = {
    "get_customer": get_customer,
    "lookup_order": lookup_order,
    "check_policy": check_policy,
    "process_refund": process_refund,
    "send_confirmation": send_confirmation,
}

TOOL_SCHEMAS: list[dict] = [
    {"name": "get_customer",
     "description": "Look up a customer record by email address. Use FIRST to verify who is asking.",
     "input_schema": {"type": "object", "properties": {"email": {"type": "string"}},
                      "required": ["email"]}},
    {"name": "lookup_order",
     "description": "Fetch one order (status, amount, issue) by order id such as ORD-1001.",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}},
                      "required": ["order_id"]}},
    {"name": "check_policy",
     "description": "Check whether an order is currently eligible for a refund under policy.",
     "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}},
                      "required": ["order_id"]}},
    {"name": "process_refund",
     "description": "Issue a refund for an order. Irreversible - only after the order is verified.",
     "input_schema": {"type": "object",
                      "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}},
                      "required": ["order_id", "amount"]}},
    {"name": "send_confirmation",
     "description": "Send the customer a confirmation message once the case is resolved.",
     "input_schema": {"type": "object",
                      "properties": {"customer_id": {"type": "string"}, "message": {"type": "string"}},
                      "required": ["customer_id", "message"]}},
]


def execute_tool(name: str, args: dict) -> str:
    """Run one tool by name and log it. Unknown tools return an error string."""
    fn = _DISPATCH.get(name)
    if fn is None:
        result = f"ERROR: unknown tool {name!r}"
    else:
        try:
            result = fn(**args)
        except TypeError as exc:
            result = f"ERROR: bad arguments for {name}: {exc}"
    lab_trace.record({"kind": "tool_exec", "name": name, "args": args, "result": result})
    return result
