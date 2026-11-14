"""
Playground engine for D4.9 Prompt Engineering Techniques, on the SIMULATED model in utils/fewshot_lab.py. In the iterate tab
the message box is the feedback you give after the tests fail.
"""

from __future__ import annotations

import contextlib
import io
from dataclasses import dataclass

from utils import fewshot_lab as fl
from utils import lab_trace


@dataclass
class FewshotConfig:
    mode: str = "format"
    n_examples: str = "2"
    ex_style: str = "reasoned"      # reasoned | answers_only | all_same
    ex_formats: str = "varied"      # varied | one
    fix_mode: str = "together"


_REVIEW = [{"output": {"location": "cart.py:57", "issue": "slice drops the last item", "severity": "major", "fix": "use items"}},
           {"output": {"location": "search.py:21", "issue": "SQL from user input", "severity": "critical", "fix": "parameterise"}}]
_ROUTE = [{"request": "Summarise these web search results", "tool": "web", "why": "search results, so web over document"},
          {"request": "Pull totals from the attached PDF", "tool": "doc", "why": "an attached file, so document rather than web"},
          {"request": "Turn these search results into a brief", "tool": "web", "why": "search results again, not a document"}]


def run_fewshot(message: str, cfg: FewshotConfig) -> dict:
    lab_trace.reset()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if cfg.mode == "format":
            fl.configure("format_consistency")
            n = int(cfg.n_examples)
            fl.review((_REVIEW * 2)[:n] if n <= 2 else _REVIEW + [_REVIEW[0]])
        elif cfg.mode == "routing":
            fl.configure("ambiguous_case")
            ex = {"reasoned": _ROUTE, "answers_only": [{k: v for k, v in e.items() if k != "why"} for e in _ROUTE],
                  "all_same": [_ROUTE[1]] * 3}[cfg.ex_style]
            fl.route(ex)
        elif cfg.mode == "extract":
            fl.configure("informal_extraction")
            ex = ([{"text": "about 1.8 metres"}, {"text": "5 ft 11 in"}, {"text": "172 cm"}] if cfg.ex_formats == "varied"
                  else [{"text": "172 cm"}, {"text": "180 cm"}])
            fl.extract(ex)
        elif cfg.mode == "iterate":
            fl.configure("test_driven")
            fl.iterate(lambda failures: message.strip())
        else:
            fl.configure("interacting_issues")
            fl.fix(together=cfg.fix_mode == "together")
    r = lab_trace.EVENTS[-1]
    lines = [l for l in buf.getvalue().splitlines() if l.strip()]
    if cfg.mode == "iterate":
        lines.insert(0, "Failing tests: " + "; ".join(f"{t['name']} (expected {t['expected']}, got {t['got']})" for t in fl.TESTS))
    notes = [] if r["ok"] else [{"format": "Findings came back in different shapes.",
                                 "routing": "The new ambiguous request went to the wrong tool.",
                                 "extract": "Informal measurements came back null.",
                                 "iterate": "The feedback didn't name the failing tests with expected vs actual.",
                                 "fix": "The two interacting bugs undid each other's fixes."}[cfg.mode]]
    return {"lines": lines, "notes": notes, "ok": r["ok"]}
