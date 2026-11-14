"""
Playground engine for D2.5 Tool Evaluation & Testing. Each knob switches on one of the page's own lab variants (the same code
changes, applied line by line to the correct harness), so combinations can be tried; the harness then runs on the SIMULATED
router and release gate in utils/eval_lab.py. The "Try a request" tab routes one typed request through the vague (v1) and the
sharpened (v2) tool sets side by side.
"""

from __future__ import annotations

import contextlib
import difflib
import io
from dataclasses import dataclass

from utils import eval_lab as el
from utils import lab_trace
from utils.tool_select_lab import route


@dataclass
class EvalConfig:
    mode: str = "coverage"
    candidate: str = "v1"              # v1 vague web tool · v2 sharpened · v3 sharpened but lost ORD- formatting
    cover_ambiguous: str = "yes"
    criteria_style: str = "per_category"   # per_category | overall_80
    grader: str = "exact"              # exact | job_only | any_tool
    rerun: str = "full"                # full | failures_only


def _apply(code: str, variant: str) -> str:
    from utils.concepts_content import evaluation as ev
    a, b = ev.CORRECT.splitlines(keepends=True), variant.splitlines(keepends=True)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag != "equal":
            old, new = "".join(a[i1:i2]), "".join(b[j1:j2])
            if old and old in code:
                code = code.replace(old, new, 1)
            elif not old:                                       # pure insertion: anchor on the line before
                anchor = "".join(a[max(i1 - 1, 0):i1])
                code = code.replace(anchor, anchor + new, 1)
    return code


_SCEN = {"v1": "ambiguous_traffic", "v2": "fixed_tools", "v3": "regression"}


def run_eval(message: str, cfg: EvalConfig) -> dict:
    from utils.concepts_content import evaluation as ev
    lab_trace.reset()
    if cfg.mode == "try":
        v = el.versions()
        req = message.strip() or "Pull the key facts out of these web search results about solar panel prices."
        lines, notes = [f"Request: “{req}”"], []
        picks = {}
        for name in ("v1", "v2"):
            r = route(req, v[name], el.SYSTEM)
            picks[name] = r["tool"]
            top = sorted(r["scores"].items(), key=lambda x: -x[1])[:3]
            lines.append(f"{name} ({'vague web tool' if name == 'v1' else 'sharpened descriptions'}) → **{r['tool']}** "
                         f"(job: {el.job(r['tool'])}) · {r['why']} · top scores {top}")
        if picks["v1"] != picks["v2"] or el.job(picks["v1"]) != el.job(picks["v2"]):
            lines.append("💡 The two tool sets **disagree** on this request — add it to your test set (probably as an ambiguous case).")
        else:
            lines.append("The two tool sets agree on this request.")
        return {"lines": lines, "notes": notes, "ok": not notes}
    code = ev.CORRECT
    if cfg.cover_ambiguous == "no":
        code = _apply(code, ev.VARIANT_A)
    if cfg.criteria_style == "overall_80":
        code = _apply(code, ev.VARIANT_B)
    if cfg.grader == "any_tool":
        code = _apply(code, ev.VARIANT_C)
    elif cfg.grader == "job_only":
        code = _apply(code, ev.VARIANT_E)
    if cfg.rerun == "failures_only":
        code = _apply(code, ev.VARIANT_D)
    el.configure(_SCEN[cfg.candidate])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<eval harness>", "exec"), {})
    r = [e for e in lab_trace.EVENTS if e["kind"] == "eval_release"][-1]
    lines = [f"Candidate **{r['candidate']}** · test cases run: {r['cases_run']} of {r['test_set_size']}"
             + (f" · baseline v1 failures: {r['baseline_failures']}" if r["candidate"] == "v3" else ""),
             "Your report: " + " · ".join(f"{k} {d['passed']}/{d['n']} ({d['accuracy']:.0%})" for k, d in r["report"].items()),
             f"Your decision: **{'SHIP' if r['ship'] else 'BLOCK'}**",
             f"Production (the truth you didn't test): {r['prod']} → the release is **{'GOOD' if r['prod_ok'] else 'BAD'}**"]
    lines += [f"✗ [{x['category']}] {x['request'][:70]} → {x['tool']}{x['input'] or ''}" + (" (stale v1 result)" if x.get("stale") else "")
              for x in r["rows"] if not x["passed"]]
    notes = []
    if r["ship"] and not r["prod_ok"]:
        notes.append("You shipped a bad release — your eval didn't catch what production hit.")
    if not r["ship"] and r["prod_ok"]:
        notes.append("You blocked a good release.")
    return {"lines": lines, "notes": notes, "ok": not notes}
