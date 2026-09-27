"""
SIMULATED extraction pipeline for D4.4 Structured Outputs (guide TS 4.3 + 4.4): schema-valid output is guaranteed, so what's
left is semantic validation, retry-with-feedback, knowing when a retry can't help, conflict flags, format normalisation and a
detected_pattern field for analysing dismissed findings.

Documented behaviour it follows (platform.claude.com/docs/en/build-with-claude/structured-outputs, fetched 2026-09-28):
structured outputs / strict tool use guarantee schema-valid JSON — valid syntax, types and required fields — but not semantic
correctness; invalid values can still be produced, and retries for semantic failures are yours to implement.
INVENTED (simulation): the documents, the misread line item, the model fixing it only when told the specific error, the PO
number that lives in a separate document, the conflicting totals, the date formats and the dismissed findings.
"""

from __future__ import annotations

import re

from utils import lab_trace

SCENARIO_IDS = ("sum_mismatch", "absent_info", "conflicting_source", "mixed_formats", "dismissal_patterns")
SCENARIO = "sum_mismatch"

DOCS = {
    "sum_mismatch": "INVOICE INV-31 · Acme Parts Ltd · 2026-03-02 · server fans 700.00 · rack rails 500.00 · cable ties 40.00 · TOTAL 1,240.00",
    "absent_info": "INVOICE INV-32 · Northwind Repairs · 2026-03-05 · lift maintenance 310.50 · TOTAL 310.50 · PO: see attached purchase order",
    "conflicting_source": "INVOICE INV-33 · Brightline · header TOTAL 980.00 · consulting 980.00 · footer AMOUNT DUE 1,080.00",
    "mixed_formats": "INVOICE INV-34 · Example Corp · issued 3 March 2026 · due 05/04/2026 · support plan 120.00 · TOTAL 120.00",
    "dismissal_patterns": "(code review findings, not an invoice)",
}

LOG: dict = {}


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in DOCS else "sum_mismatch"
    LOG.clear()
    LOG.update(calls=[], retries=0, stored=None, human=None, feedback=[])


configure("sum_mismatch")


def document() -> str:
    return DOCS[SCENARIO]


def _props(schema):
    return (schema or {}).get("properties", {})


def _nullable(schema, field):
    t = _props(schema).get(field, {}).get("type")
    return isinstance(t, list) and "null" in t


def extract(doc: str, schema: dict, rules: str = "", feedback: list | None = None) -> dict:
    """The SIMULATED model's schema-valid extraction (types always right; values not necessarily)."""
    props = _props(schema)
    fb = " ".join(feedback or []).lower()
    x = {}
    if SCENARIO == "sum_mismatch":
        fixed = bool(re.search(r"sum|add up|total", fb)) and re.search(r"\d", fb)
        items = [700.0, 500.0, 40.0 if fixed else 400.0]            # SIMULATED misread: 40.00 → 400.00 until told specifically
        x = {"invoice_id": "INV-31", "line_items": items, "stated_total": 1240.0}
    elif SCENARIO == "absent_info":
        x = {"invoice_id": "INV-32", "line_items": [310.5], "stated_total": 310.5,
             "po_number": None if _nullable(schema, "po_number") else "PO-00000"}   # required non-null → fabricated
    elif SCENARIO == "conflicting_source":
        x = {"invoice_id": "INV-33", "line_items": [980.0], "stated_total": 980.0}
        if "conflict_detected" in props:
            x["conflict_detected"] = True
    elif SCENARIO == "mixed_formats":
        iso = "iso 8601" in rules.lower() or "yyyy-mm-dd" in rules.lower()
        uk = "day/month" in rules.lower() or "dd/mm" in rules.lower()
        x = {"invoice_id": "INV-34", "line_items": [120.0], "stated_total": 120.0,
             "issued": "2026-03-03" if iso else "3 March 2026",
             "due": ("2026-04-05" if uk else "2026-05-04") if iso else "05/04/2026"}
    if "calculated_total" in props and "line_items" in x:
        x["calculated_total"] = round(sum(x["line_items"]), 2)
    LOG["calls"].append({"feedback": list(feedback or []), "out": dict(x)})
    return x


def retry_with_feedback(doc: str, failed: dict, errors: list, schema: dict, rules: str = "") -> dict:
    """A follow-up request carrying the original document, the failed extraction and the specific validation errors."""
    LOG["retries"] += 1
    LOG["feedback"].append(list(errors))
    return extract(doc, schema, rules, feedback=errors)


def store(x: dict, flags=()) -> None:
    LOG["stored"] = {"record": dict(x), "flags": list(flags)}


def route_to_human(x: dict, reason: str) -> None:
    LOG["human"] = {"record": dict(x), "reason": reason}


FINDINGS = [  # (id, detected_pattern, dismissed by developers?)
    ("f1", "broad-except-in-tests", True), ("f2", "broad-except-in-tests", True), ("f3", "broad-except-in-tests", True),
    ("f4", "broad-except-in-tests", True), ("f5", "sql-string-format", False), ("f6", "unused-import", True),
    ("f7", "off-by-one-range", False), ("f8", "sql-string-format", False), ("f9", "unused-import", False), ("f10", "off-by-one-range", False),
]


def analyse_dismissals(finding_fields: list) -> dict:
    """Group developer dismissals — only possible if findings carry a detected_pattern field."""
    dismissed = [f for f in FINDINGS if f[2]]
    if "detected_pattern" not in finding_fields:
        out = {"can_group": False, "dismissed": len(dismissed)}
    else:
        counts = {}
        for _id, pat, _d in dismissed:
            counts[pat] = counts.get(pat, 0) + 1
        top = max(counts.items(), key=lambda kv: kv[1])
        out = {"can_group": True, "dismissed": len(dismissed), "by_pattern": counts, "top": top}
    LOG["analysis"] = out
    return out


def finish() -> None:
    rec = {"kind": "extract_run", "scenario": SCENARIO, "calls": LOG["calls"], "retries": LOG["retries"], "stored": LOG["stored"],
           "human": LOG["human"], "feedback": LOG["feedback"], "analysis": LOG.get("analysis")}
    lab_trace.record(rec)
    for i, c in enumerate(LOG["calls"], 1):
        print(f"call {i}{' (retry with: ' + '; '.join(c['feedback']) + ')' if c['feedback'] else ''}: {c['out']}")
    if LOG["stored"]:
        print(f"stored: {LOG['stored']['record']}{' · flags ' + str(LOG['stored']['flags']) if LOG['stored']['flags'] else ''}")
    if LOG["human"]:
        print(f"sent to a human: {LOG['human']['reason']}")
    if LOG.get("analysis"):
        print(f"dismissal analysis: {LOG['analysis']}")
