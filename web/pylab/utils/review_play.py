"""
Playground engine for D4.1 System Prompts: the message box is YOUR review system prompt (one line is fine — sentences become
lines, so "Report only: bugs, security. Skip: style." works). Runs the SIMULATED reviewer in utils/review_lab.py.
"""

from __future__ import annotations

import contextlib
import io
import re
from dataclasses import dataclass

from utils import lab_trace
from utils import review_lab as rl


@dataclass
class ReviewConfig:
    mode: str = "yours"
    instruction_style: str = "explicit"    # explicit | accurate | conservative
    sev_examples: str = "yes"
    perf_off: str = "yes"


_EXPLICIT = ("Report only: bugs, security issues, performance problems with measurable impact, and comments whose claimed "
             "behaviour contradicts the code. Skip: style, naming, and local patterns this codebase uses consistently.")
_SEV_EX = ("- critical: exploitable or loses data, e.g. SQL built from user input.\n- major: a wrong result in normal use, e.g. an "
           "off-by-one that drops the last item.\n- minor: rare edge cases, e.g. a date bug at midnight on a DST change.")
_SEV_NO = "- critical: very serious.\n- major: serious.\n- minor: not very serious."


def _lines(text: str) -> str:
    return re.sub(r"(?<=[.;])\s+(?=(?:Report|Skip|Severity|critical|major|minor)\b|- )", "\n", text.strip())


def run_review(message: str, cfg: ReviewConfig) -> dict:
    lab_trace.reset()
    if cfg.mode == "yours":
        prompt = _lines(message or _EXPLICIT)
        disabled = ["performance"] if cfg.perf_off == "yes" else []
    else:
        body = {"explicit": _EXPLICIT, "accurate": "Report bugs, security issues, performance problems and comments - check that comments are accurate.",
                "conservative": "Be conservative: only report high-confidence findings."}[cfg.instruction_style if cfg.mode == "vague" else "explicit"]
        sev = _SEV_EX if (cfg.mode != "severity" or cfg.sev_examples == "yes") else _SEV_NO
        prompt = _lines(body) + "\nSeverity:\n" + sev
        disabled = ["performance"] if (cfg.mode != "noisy" or cfg.perf_off == "yes") else []
    with contextlib.redirect_stdout(io.StringIO()):
        rl.review(prompt, disabled)
    r = [e for e in lab_trace.EVENTS if e["kind"] == "review_run"][-1]
    lines = [f"System prompt the reviewer read:\n```\n{prompt}\n```", f"Switched off: {r['disabled'] or 'nothing'}"]
    lines += [f"{'✓' if x['real'] else '✗ FALSE POSITIVE'} [{x['category']}{'/' + x['severity'] if x.get('severity') else ''}] {x['text']}"
              for x in r["found"]]
    lines.append(f"**Precision {r['precision']:.0%}** (how many findings are real) · **recall {r['recall']:.0%}** (how many real "
                 f"issues were found) · missed: {r['missed'] or 'none'}"
                 + (f" · not checked (category switched off): {r['not_checked']}" if r["not_checked"] else ""))
    notes = []
    if r["fp"]:
        notes.append(f"{len(r['fp'])} false positive(s): {r['fp']}")
    sev = r["severity_b"]
    if len(sev) == 2 and len(set(sev.values())) > 1:
        notes.append(f"The two identical off-by-one bugs got different severities: {sev}")
    if r["recall"] < 1:
        notes.append(f"Real issues missed: {r['missed']}")
    return {"lines": lines, "notes": notes, "ok": not notes}
