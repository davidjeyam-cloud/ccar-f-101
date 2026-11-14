"""
Playground engine for D4.10 Multi-Pass Review, on the SIMULATED generator and reviewers in utils/mpreview_lab.py. In the
reviewer tab the message box is the instruction you give the reviewer.
"""

from __future__ import annotations

import contextlib
import io
from dataclasses import dataclass

from utils import lab_trace
from utils import mpreview_lab as ml


@dataclass
class MPReviewConfig:
    mode: str = "reviewer"
    reviewer_kind: str = "new_instance"      # new_instance | same_session | same_session_thinking
    pass_plan: str = "per_file_integration"  # per_file_integration | per_file_only | one_pass
    auto_threshold: str = "0.8"              # 0.8 | 0.5 | none


def run_mpreview(message: str, cfg: MPReviewConfig) -> dict:
    lab_trace.reset()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if cfg.mode == "reviewer":
            ml.configure("self_review")
            code = ml.generate("paginate the orders list")
            kind = cfg.reviewer_kind
            ml.review(code, session="new" if kind == "new_instance" else "same", instructions=message.strip(),
                      extended_thinking=kind == "same_session_thinking")
        elif cfg.mode == "passes":
            ml.configure("cross_file")
            if cfg.pass_plan == "one_pass":
                ml.one_pass_review(ml.FILES)
            else:
                local = [f for p in ml.FILES for f in ml.per_file_review(p)]
                if cfg.pass_plan == "per_file_integration":
                    ml.integration_review(ml.FILES, summaries=local)
        else:
            ml.configure("calibrated_routing")
            with_c = cfg.auto_threshold != "none"
            ml.route(ml.verify(ml.CANDIDATES, with_confidence=with_c), auto_post_at=float(cfg.auto_threshold) if with_c else None)
        ml.finish()
    r = lab_trace.EVENTS[-1]
    lines = [l for l in r["passes"] if not l.startswith("per-file pass") or "→ 1" in l]
    if cfg.mode == "reviewer":
        code = ml.generate("")
        lines = [f"Generated: `{code['code']}`", f"Generator's reasoning (in its session): “{code['reasoning']}”"] + lines
    lines += [f"• {f}" for f in r["findings"]]
    notes = []
    if cfg.mode == "reviewer" and not r["caught_gen_bug"]:
        notes.append("The page=0 bug was missed — the reviewer shared the generator's reasoning.")
    if cfg.mode == "passes":
        lines.append(f"Local issues caught: {len(r['local_caught'])}/4 · cross-file rename caught: {r['cross_caught']} · contradictions: {r['contradictions']}")
        if len(r["local_caught"]) < 4:
            notes.append("Local issues in the middle files were missed.")
        if r["contradictions"]:
            notes.append("file_03 was judged both “fine” and “missing validation”.")
        if not r["cross_caught"]:
            notes.append("The cross-file rename (total → amount) was missed.")
    if cfg.mode == "routing":
        rt = r["routed"]
        lines.append(f"Auto-posted: {rt['auto']}")
        lines.append(f"To a human: {rt['human']}")
        if rt["auto_false"]:
            notes.append(f"False positives auto-posted: {rt['auto_false']}")
        if rt["human_load"] > 3:
            notes.append(f"{rt['human_load']} findings sent to a human.")
    return {"lines": lines, "notes": notes, "ok": not notes}
