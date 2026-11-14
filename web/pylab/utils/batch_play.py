"""
Playground engine for D4.3 Batch API, on the SIMULATED APIs in utils/batch_lab.py. In the cadence tab the message box is the
SLA in hours (e.g. "30"); elsewhere it's a note for the run.
"""

from __future__ import annotations

import contextlib
import io
import re
from dataclasses import dataclass

from utils import batch_lab as bl
from utils import lab_trace


@dataclass
class BatchConfig:
    mode: str = "route"
    job_pick: str = "premerge"
    api_pick: str = "sync"
    match_by: str = "custom_id"
    retry_mode: str = "failed_chunked"   # failed_chunked | failed_only | all
    window_hours: str = "4"
    sample_on: str = "yes"


def run_batch(message: str, cfg: BatchConfig) -> dict:
    lab_trace.reset()
    sc = {"route": cfg.job_pick, "order": "results_order", "failures": "partial_failure", "cadence": "sla_cadence", "sample": "sample_first"}[cfg.mode]
    bl.configure(sc)
    saved = dict(bl.JOBS[sc])
    m = re.search(r"\d+(?:\.\d+)?", message or "")
    if cfg.mode == "cadence" and m:
        bl.JOBS[sc]["sla_hours"] = float(m.group(0))
    choose = (lambda j: cfg.api_pick) if cfg.mode == "route" else (lambda j: "batch")

    def attach(results, docs, ids):
        if cfg.match_by == "custom_id":
            by = {r["custom_id"]: r["text"] for r in results}
            return {d["id"]: by.get(c) for d, c in zip(docs, ids)}
        return {d["id"]: r["text"] for d, r in zip(docs, results)}

    def retry(results):
        plan = {}
        for r in results:
            if r["type"] == "succeeded" and cfg.retry_mode != "all":
                continue
            long_ = r["type"] == "errored" and "too long" in r.get("error", "")
            plan[r["custom_id"]] = "resubmit_chunked" if (long_ and cfg.retry_mode != "failed_only") else "resubmit"
        return plan

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rec = bl.run(choose, lambda d: d["id"], attach, retry, float(cfg.window_hours), cfg.sample_on == "yes")
    finally:
        bl.JOBS[sc] = saved
    lines = list(rec["log"])
    if cfg.mode == "cadence":
        sla = float(m.group(0)) if m else 30.0
        lines.append(f"Largest window that keeps the SLA: {max(0.0, sla - bl.BATCH_HOURS):g} h (SLA {sla:g} h − {bl.BATCH_HOURS} h batch)")
    notes = [] if rec["ok"] else [{"blocking": "A blocking check waited on a batch with no latency guarantee.",
                                   "cost": "A latency-tolerant job paid the full synchronous price.",
                                   "order": "Results matched by position went to the wrong documents.",
                                   "resubmit_all": "Resubmitted documents that had already succeeded.",
                                   "no_chunk": "The over-long documents failed again unchanged.",
                                   "dropped": "Some failed documents were never resubmitted.",
                                   "cadence": "The worst-case delay breaks the SLA.",
                                   "tool_loop": "A tool-calling workflow can't finish inside a batch request.",
                                   "no_sample": "The untested prompt failed on 30% of 10,000 requests."}.get(rec["problem"], rec["problem"])]
    return {"lines": lines, "notes": notes, "ok": rec["ok"]}
