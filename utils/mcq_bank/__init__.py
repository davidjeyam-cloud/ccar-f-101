"""
The exam question bank by task statement (docs/MCQ_BANK_PLAN.md). One module per task statement, ts_1_1.py … ts_5_6.py, each with:
  TS = "1.1"
  BULLETS = {"K1": "short paraphrase of the guide bullet", …}      never the guide's own words
  QUESTIONS = (MCQ(...), …)                                         ids Q1.1-01 …; the group is the first entry of `points`
Separate from utils/question_bank.py and section 10: no question here may repeat those (checked by utils/mcq_bank_verify.py).
Target per task statement = max(20, 3 × its bullets). Single-answer only. Original text only.
"""

import importlib
import pkgutil

from utils.guide_index import _TS


def target(ts: str) -> int:
    _, _, k, s = _TS[ts]
    return max(20, 3 * (k + s))


def load(only: str | None = None) -> dict:
    """ts -> module, for every ts_*.py present (reloaded, so edits show without restarting Streamlit).
    only="1.1" loads just that task statement, so a half-written sibling file cannot break the run."""
    out = {}
    for m in pkgutil.iter_modules(__path__):
        if not m.name.startswith("ts_"):
            continue
        if only and m.name != "ts_" + only.replace(".", "_"):
            continue
        mod = importlib.reload(importlib.import_module(f"{__name__}.{m.name}"))
        out[mod.TS] = mod
    return out
