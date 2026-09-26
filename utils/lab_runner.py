"""
Runs a learner's edited lab code in a SEPARATE Python process and returns what
it printed plus the event trace.

Why a subprocess instead of exec() inside Streamlit:
- a hard timeout — an accidental `while True:` cannot hang the app;
- isolation — the lab's code never touches Streamlit's state;
- a clean environment — API keys are deliberately NOT passed to the child
  (CLAUDE.md guardrail 3), the working directory is a throw-away temp folder
  (so a relative `.env` read finds nothing), and any secret value that still
  appears in the output is redacted before it can reach the UI.

Honest limit: this is not a security sandbox. The code runs on your own
machine with your own permissions — it is meant for code you write or edit
yourself in this lab. Do not paste code you do not understand.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

from utils.lab_trace import TRACE_MARK

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS = Path(__file__).resolve().parent / "lab_harness.py"

MAX_CODE_CHARS = 20_000
MAX_OUTPUT_CHARS = 20_000


@dataclass
class LabResult:
    stdout: str
    stderr: str
    trace: dict | None      # None when the run timed out or the harness could not report
    timed_out: bool
    returncode: int | None
    seconds: float
    error: str | None = None


def _redact_values() -> list[str]:
    """Secret values that must never reach the screen (env + local .env)."""
    values = [os.environ.get(n, "") for n in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY")]
    try:
        values += [v or "" for k, v in dotenv_values(REPO_ROOT / ".env").items()
                   if any(w in k.upper() for w in ("KEY", "TOKEN", "SECRET", "PASSWORD"))]
    except OSError:
        pass
    return [v for v in values if len(v) >= 8]


def _clean(text: str, redact: list[str]) -> str:
    for value in redact:
        text = text.replace(value, "[REDACTED]")
    if len(text) > MAX_OUTPUT_CHARS:
        text = text[:MAX_OUTPUT_CHARS] + f"\n... [output truncated at {MAX_OUTPUT_CHARS} characters]"
    return text


def _as_text(data) -> str:
    if data is None:
        return ""
    return data.decode("utf-8", errors="replace") if isinstance(data, bytes) else str(data)


def run_lab(code: str, scenario: str, timeout: float = 10.0) -> LabResult:
    if len(code) > MAX_CODE_CHARS:
        return LabResult("", "", None, False, None, 0.0,
                         error=f"Code is longer than {MAX_CODE_CHARS} characters - trim it.")

    redact = _redact_values()
    env = {  # deliberately minimal: no API keys, no proxy settings, nothing secret
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "SYSTEMDRIVE": os.environ.get("SYSTEMDRIVE", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "LAB_SCENARIO": scenario,
        "LAB_REPO_ROOT": str(REPO_ROOT),
    }

    started = time.time()
    with tempfile.TemporaryDirectory(prefix="ccar_lab_") as tmp:
        code_file = Path(tmp) / "lab_code.py"
        code_file.write_text(code, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, "-X", "utf8", str(HARNESS), str(code_file)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=timeout, cwd=tmp, env=env,
            )
        except subprocess.TimeoutExpired as exc:
            return LabResult(_clean(_as_text(exc.stdout), redact), _clean(_as_text(exc.stderr), redact),
                             None, True, None, time.time() - started)

    head, marker, tail = proc.stdout.rpartition(TRACE_MARK)
    trace = None
    if marker:
        try:
            trace = json.loads(tail.strip())
        except ValueError:
            trace = None
    stdout = head if marker else proc.stdout
    return LabResult(_clean(stdout.rstrip("\n"), redact), _clean(proc.stderr, redact),
                     trace, False, proc.returncode, time.time() - started)
