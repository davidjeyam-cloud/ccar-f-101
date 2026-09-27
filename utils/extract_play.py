"""
Playground engine for D4.4 Structured Outputs, on the SIMULATED extraction model in utils/extract_lab.py. In the retry tab the
message box is the feedback you send on retry (the model fixes the misread line item only when the feedback names the sum /
total and a number — a simulation stand-in for "specific errors guide correction").
"""

from __future__ import annotations

import copy
from dataclasses import dataclass

from utils import extract_lab as el


@dataclass
class ExtractConfig:
    mode: str = "validate"
    sem_check: str = "yes"
    absent_policy: str = "flag"      # flag | retry
    po_nullable: str = "yes"
    conflict_field: str = "yes"
    norm_rules: str = "iso_uk"       # iso_uk | iso_only | none
    pattern_field: str = "yes"


_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {
    "invoice_id": {"type": "string"}, "line_items": {"type": "array", "items": {"type": "number"}},
    "stated_total": {"type": "number"}, "calculated_total": {"type": "number"}, "conflict_detected": {"type": "boolean"},
    "po_number": {"type": ["string", "null"]}, "issued": {"type": ["string", "null"]}, "due": {"type": ["string", "null"]}}}


def run_extract(message: str, cfg: ExtractConfig) -> dict:
    schema = copy.deepcopy(_SCHEMA)
    lines, notes = [], []
    if cfg.mode in ("validate", "retry"):
        el.configure("sum_mismatch")
        doc = el.document()
        x = el.extract(doc, schema)
        lines += [f"Document: {doc}", f"Extraction (schema-valid): {x}"]
        if cfg.mode == "validate" and cfg.sem_check == "no":
            notes.append(f"Stored as-is: line items {x['line_items']} sum to {x['calculated_total']}, not the stated {x['stated_total']}.")
            return {"lines": lines, "notes": notes, "ok": False}
        err = f"line items sum to {x['calculated_total']} but stated_total is {x['stated_total']} - re-read each line item"
        fb = [message.strip()] if (cfg.mode == "retry" and message.strip()) else [err]
        lines.append(f"Validation error: {err}")
        x2 = el.retry_with_feedback(doc, x, fb, schema)
        lines += [f"Retry sent with: “{fb[0]}” (plus the original document and the failed extraction)", f"Retry result: {x2}"]
        if abs(x2["calculated_total"] - x2["stated_total"]) > 0.01:
            notes.append("The retry repeated the mistake — the feedback didn't say what was wrong.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    if cfg.mode == "absent":
        el.configure("absent_info")
        if cfg.po_nullable == "no":
            schema["properties"]["po_number"] = {"type": "string"}
        doc = el.document()
        x = el.extract(doc, schema)
        lines += [f"Document: {doc}", f"Extraction: {x}"]
        if x["po_number"] not in (None,):
            notes.append(f"po_number is required and non-null, so the model invented one: {x['po_number']}.")
        elif cfg.absent_policy == "retry":
            for _ in range(2):
                x = el.retry_with_feedback(doc, x, ["po_number is missing - find it"], schema)
            lines.append(f"After 2 retries: po_number = {x['po_number']}")
            notes.append("Two retries spent on information that is only in an attached document.")
        else:
            lines.append("Stored with po_number null and a flag: the PO is only in an attached document that wasn't provided.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    if cfg.mode == "conflict":
        el.configure("conflicting_source")
        if cfg.conflict_field == "no":
            schema["properties"].pop("conflict_detected")
        doc = el.document()
        x = el.extract(doc, schema)
        lines += [f"Document: {doc}", f"Extraction: {x}"]
        if x.get("conflict_detected"):
            lines.append("conflict_detected = true → sent to a human, not stored")
        else:
            notes.append("Stored 980.00 silently — the footer says 1,080.00.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    if cfg.mode == "formats":
        el.configure("mixed_formats")
        rules = {"iso_uk": "Dates: ISO 8601 (YYYY-MM-DD); numeric dates are UK day/month.", "iso_only": "Dates: ISO 8601 (YYYY-MM-DD).",
                 "none": ""}[cfg.norm_rules]
        doc = el.document()
        x = el.extract(doc, schema, rules)
        lines += [f"Document: {doc}", f"Rules in the prompt: “{rules or '(none)'}”", f"issued = {x['issued']} · due = {x['due']}"]
        if x["issued"] != "2026-03-03" or x["due"] != "2026-04-05":
            notes.append("Dates came back in mixed or wrong formats (05/04 is 5 April in the UK, May 4 in the US).")
        return {"lines": lines, "notes": notes, "ok": not notes}
    el.configure("dismissal_patterns")
    fields = ["location", "issue", "severity"] + (["detected_pattern"] if cfg.pattern_field == "yes" else [])
    a = el.analyse_dismissals(fields)
    lines += [f"Finding fields: {fields}", f"Dismissed findings: {a['dismissed']} of {len(el.FINDINGS)}"]
    if a["can_group"]:
        lines.append(f"By pattern: {a['by_pattern']} → fix the prompt for “{a['top'][0]}” first")
    else:
        notes.append("Nothing to group dismissals by — you can't tell which construct causes the false positives.")
    return {"lines": lines, "notes": notes, "ok": not notes}
