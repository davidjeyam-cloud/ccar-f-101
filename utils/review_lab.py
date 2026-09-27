"""
SIMULATED code reviewer for D4.1 System Prompts & Instructions (guide TS 4.1): you write the review system prompt (and which
categories are switched off); the simulated reviewer reads it and reviews a fixed pull request whose true issues are known,
so precision (how many reported findings are real) and recall (how many real issues were found) can be measured.

How the SIMULATED reviewer reads a prompt (INVENTED — a stand-in for the docs' point that explicit, specific instructions
beat vague ones; platform prompting best practices, fetched 2026-09-28):
- explicit categories: a line starting "Report" lists what to report; a line starting "Skip" lists what to leave out;
- a comment rule mentioning "contradict" flags only comments whose claim contradicts the code; "accurate" alone flags any
  comment that looks stale;
- vague filters ("conservative", "high-confidence", "important") do NOT remove style findings — the reviewer is confident
  about style;
- severity: levels defined with a concrete example each ("e.g.") give identical bugs identical severities; levels without
  examples don't;
- categories listed in DISABLED are not reported at all.
"""

from __future__ import annotations

import re

from utils import lab_trace

SCENARIO_IDS = ("comment_accuracy", "style_noise", "severity_consistency", "noisy_category")
SCENARIO = "comment_accuracy"

# the pull request's candidate findings: (id, category, real issue?, text)
CANDIDATES = [
    ("c1", "comment", False, "cart.py:12 comment says “returns the items as a list” — looks old, but the code does return a list"),
    ("c2", "comment", True, "cart.py:40 comment says “returns None on failure” but the code raises ValueError"),
    ("b1", "bug", True, "cart.py:57 off-by-one: range(len(items) - 1) drops the last item"),
    ("b2", "bug", True, "orders.py:88 off-by-one: range(len(lines) - 1) drops the last line"),
    ("s1", "security", True, "search.py:21 SQL built with an f-string from user input"),
    ("y1", "style", False, "cart.py:3 variable name `tmp` is not descriptive"),
    ("y2", "style", False, "orders.py:14 line is 104 characters long"),
    ("y3", "style", False, "search.py:9 prefer a list comprehension"),
    ("l1", "local_pattern", False, "orders.py:30 early return — this codebase uses early returns everywhere"),
    ("p1", "performance", True, "search.py:40 query inside a loop over 10,000 rows"),
    ("p2", "performance", False, "cart.py:70 len() called twice"),
    ("p3", "performance", False, "orders.py:5 dictionary created per call"),
    ("p4", "performance", False, "search.py:2 import inside a function"),
    ("p5", "performance", False, "cart.py:8 string concatenation in a 3-item loop"),
]
REAL = {c[0] for c in CANDIDATES if c[2]}


def configure(scenario_id: str) -> None:
    global SCENARIO
    SCENARIO = scenario_id if scenario_id in SCENARIO_IDS else "comment_accuracy"


def _lines(prompt, word):
    return " ".join(l.lower() for l in prompt.splitlines() if l.strip().lower().startswith(word))


_ALIASES = {"bug": ("bug",), "security": ("security",), "comment": ("comment",), "style": ("style", "formatting", "naming"),
            "local_pattern": ("local pattern", "patterns this codebase", "existing pattern", "established pattern"),
            "performance": ("performance",)}


def _mentions(text, cat):
    return any(a in text for a in _ALIASES[cat])


def review(system_prompt: str, disabled=()) -> list:
    p = system_prompt or ""
    low = p.lower()
    report, skip = _lines(p, "report"), _lines(p, "skip")
    explicit = bool(report)
    found = []
    for cid, cat, real, text in CANDIDATES:
        if cat in disabled:
            continue
        if explicit and not _mentions(report, cat):
            continue
        if skip and _mentions(skip, cat):
            continue
        if cat == "comment":
            if "contradict" in low and cid == "c1":
                continue                                   # precise criterion: c1 doesn't contradict the code
        found.append({"id": cid, "category": cat, "real": real, "text": text})
    # severity
    levels = re.findall(r"^\s*-?\s*(critical|major|minor)\s*:(.*)$", p, re.I | re.M)
    with_examples = bool(levels) and all(("e.g." in d or "example" in d.lower()) for _l, d in levels)
    for f in found:
        if f["category"] in ("bug", "security"):
            if f["category"] == "security":
                f["severity"] = "critical"
            elif with_examples:
                f["severity"] = "major"
            else:
                f["severity"] = "major" if f["id"] == "b1" else "minor"   # SIMULATED inconsistency without examples
    tp = [f for f in found if f["real"]]
    precision = round(len(tp) / len(found), 2) if found else 1.0
    recall = round(len(tp) / len(REAL - {c for c in REAL if CANDIDATES_BY_ID[c][1] in disabled}), 2) if REAL else 1.0
    sev_b = {f["id"]: f.get("severity") for f in found if f["id"] in ("b1", "b2")}
    rec = {"kind": "review_run", "scenario": SCENARIO, "found": found, "precision": precision, "recall": recall,
           "fp": [f["id"] for f in found if not f["real"]],
           "missed": sorted(c for c in REAL - {f["id"] for f in found} if CANDIDATES_BY_ID[c][1] not in disabled),
           "not_checked": sorted(c for c in REAL if CANDIDATES_BY_ID[c][1] in disabled),
           "disabled": list(disabled), "explicit": explicit, "severity_b": sev_b,
           "vague": bool(re.search(r"conservative|high[- ]confidence|only .*important", low))}
    lab_trace.record(rec)
    for f in found:
        print(f"  {'✓' if f['real'] else '✗ FALSE POSITIVE'} [{f['category']}{'/' + f['severity'] if f.get('severity') else ''}] {f['text']}")
    print(f"reported {len(found)} · precision {precision:.0%} · recall {recall:.0%} · disabled: {list(disabled) or 'none'}")
    return found


CANDIDATES_BY_ID = {c[0]: c for c in CANDIDATES}
