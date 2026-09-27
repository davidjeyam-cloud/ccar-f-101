"""
SIMULATED built-in-tools lab for D2.6 (guide TS 2.5): a small fake repository and Claude Code-shaped tools — grep (content
search), glob (file-path patterns), read, edit (exact, unique string replacement) and write — that you call from code to do
five tasks. The lab checks the answer and counts how much you read (a stand-in for context used).

Documented behaviour it follows (code.claude.com/docs/en/tools-reference, fetched 2026-09-28): Grep searches file CONTENTS
for a (ripgrep) regex; Glob finds files by path pattern, `**` recursive; Read returns a file's contents; Write creates or
overwrites a file; Edit replaces an exact old_string that must appear exactly ONCE (else: add surrounding context, or
replace_all=True to change every occurrence); Claude reads a file before editing or writing it.
INVENTED (simulation): the repository, the tasks, the "chars read" budget, and the error texts.
"""

from __future__ import annotations

import fnmatch
import re

from utils import lab_trace

SCENARIO_IDS = ("find_callers", "find_tests", "edit_nonunique", "trace_flow", "wrapper_usage")
SCENARIO = "find_callers"
TASK = "find_callers"
READ_BUDGET = 1600          # chars — the simulated context budget for the trace_flow task

_BASE = {
    "billing/refunds.py": "from billing.approvals import approve_refund\n\ndef process_refund(order_id, amount):\n    approve_refund(order_id, amount)\n    return {'refund': amount}\n",
    "billing/approvals.py": "from billing.limits import within_limit\n\ndef approve_refund(order_id, amount):\n    if not within_limit(amount):\n        raise ValueError('needs a manager')\n    return True\n",
    "billing/limits.py": "REFUND_LIMIT = 500\n\ndef within_limit(amount):\n    return amount <= REFUND_LIMIT\n",
    "support/bot.py": "from billing.refunds import process_refund\n\ndef handle(msg):\n    return process_refund(msg.order, msg.amount)\n",
    "support/escalate.py": "def escalate(ticket):\n    # a refund over the limit goes to a person\n    return {'queued': ticket}\n",
    "web/checkout.py": "from billing.refunds import process_refund\n\ndef cancel(order):\n    return process_refund(order.id, order.total)\n",
    "docs/refund_policy.md": "# Refund policy\nRefunds over $500 need a manager. See process_refund in billing.\n",
    "scripts/refund_report.py": "# prints last month's refunds from the ledger\nprint('report')\n",
    "config/app.toml": "[orders]\ntimeout = 30\nretries = 2\n\n[payments]\ntimeout = 30\nretries = 5\n",
    "ui/Button.tsx": "export const Button = () => null;\n",
    "ui/Button.test.tsx": "test('renders', () => {});\n",
    "ui/forms/Field.tsx": "export const Field = () => null;\n",
    "ui/forms/Field.test.tsx": "test('field', () => {});\n",
    "ui/testing-utils.tsx": "// helpers used by every test\nexport const render = () => null;\n",
    "ui/README.md": "Run the test suite with npm test. Each test lives next to its component.\n",
    "payments/__init__.py": "from payments.core import charge as charge_card, refund as issue_refund\n__all__ = ['charge_card', 'issue_refund']\n",
    "payments/core.py": "def charge(card, amount):\n    return True\n\ndef refund(card, amount):\n    return True\n",
    "shop/cart.py": "from payments import charge_card\n\ndef pay(cart):\n    return charge_card(cart.card, cart.total)\n",
    "shop/returns.py": "from payments import issue_refund\n\ndef give_back(item):\n    return issue_refund(item.card, item.price)\n",
    "shop/admin.py": "import payments\n\ndef force(card):\n    return payments.charge_card(card, 1)\n",
    "legacy/old_pay.py": "from payments.core import charge\n\ndef old(card):\n    return charge(card, 5)\n",
}
# padding: many unrelated files so "read everything" is expensive
for i in range(12):
    _BASE[f"reports/monthly_{i:02d}.py"] = f"# monthly report {i}\n" + "\n".join(f"row_{j} = {j}" for j in range(40)) + "\n"

FILES: dict = {}
_LOG: dict = {}


class EditError(Exception):
    """Edit could not apply: old_string not found, or found more than once without replace_all."""


def configure(scenario_id: str) -> None:
    global SCENARIO, TASK
    SCENARIO = TASK = scenario_id if scenario_id in SCENARIO_IDS else "find_callers"
    FILES.clear()
    FILES.update(_BASE)
    _LOG.clear()
    _LOG.update(calls=[], chars_read=0, read=set(), answer=None)


configure("find_callers")


def _log(tool, arg, note=""):
    _LOG["calls"].append(f"{tool}({arg})" + (f" → {note}" if note else ""))


def grep(pattern: str, path_glob: str | None = None) -> list:
    """Search file CONTENTS for a regex; returns [(path, line_no, line)]."""
    rx = re.compile(pattern)
    hits = []
    for path, text in sorted(FILES.items()):
        if path_glob and not fnmatch.fnmatch(path, path_glob):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append((path, n, line))
    _log("Grep", repr(pattern), f"{len(hits)} lines in {len({h[0] for h in hits})} files")
    return hits


def glob(pattern: str) -> list:
    """Find files whose PATH matches a glob pattern (** = any depth)."""
    rx = "^" + re.escape(pattern).replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*").replace(r"\*", "[^/]*").replace(r"\?", ".") + "$"
    out = sorted(p for p in FILES if re.match(rx, p))
    _log("Glob", repr(pattern), f"{len(out)} files")
    return out


def read(path: str) -> str:
    if path not in FILES:
        _log("Read", path, "no such file")
        raise FileNotFoundError(path)
    _LOG["chars_read"] += len(FILES[path])
    _LOG["read"].add(path)
    _log("Read", path, f"{len(FILES[path])} chars")
    return FILES[path]


def edit(path: str, old_string: str, new_string: str, replace_all: bool = False) -> None:
    if path not in _LOG["read"]:
        raise EditError(f"{path}: read the file before editing it")
    n = FILES[path].count(old_string)
    if n == 0:
        _log("Edit", path, "old_string not found")
        raise EditError("old_string not found")
    if n > 1 and not replace_all:
        _log("Edit", path, f"old_string appears {n} times")
        raise EditError(f"old_string appears {n} times - add surrounding context, or replace_all=True")
    FILES[path] = FILES[path].replace(old_string, new_string) if replace_all else FILES[path].replace(old_string, new_string, 1)
    _log("Edit", path, f"replaced {n if replace_all else 1}")


def write(path: str, content: str) -> None:
    if path in FILES and path not in _LOG["read"]:
        raise EditError(f"{path}: read the file before overwriting it")
    FILES[path] = content
    _log("Write", path, f"{len(content)} chars")


def all_paths() -> list:
    """Every file path in the repo (a directory listing - no contents)."""
    return sorted(FILES)


EXPECTED = {
    "find_callers": ["support/bot.py", "web/checkout.py"],
    "find_tests": ["ui/Button.test.tsx", "ui/forms/Field.test.tsx"],
    "trace_flow": ["billing/approvals.py", "billing/limits.py", "billing/refunds.py"],
    "wrapper_usage": ["shop/admin.py", "shop/cart.py", "shop/returns.py"],
}


def submit(answer) -> None:
    """Hand in your answer for the current task."""
    _LOG["answer"] = answer
    toml = FILES["config/app.toml"]
    rec = {"kind": "builtin_task", "task": TASK, "answer": sorted(answer) if isinstance(answer, (list, set, tuple)) else answer,
           "calls": list(_LOG["calls"]), "chars_read": _LOG["chars_read"], "files_read": sorted(_LOG["read"]),
           "budget": READ_BUDGET, "toml": toml}
    if TASK == "edit_nonunique":
        orders = toml.split("[payments]")[0]
        payments = toml.split("[payments]")[1]
        rec["correct"] = "timeout = 30" in orders and "timeout = 60" in payments
    else:
        rec["correct"] = rec["answer"] == EXPECTED[TASK]
    lab_trace.record(rec)
    print("tool calls:", *rec["calls"], sep="\n  ")
    print(f"answer: {rec['answer'] if TASK != 'edit_nonunique' else toml}")
    print(f"chars read: {rec['chars_read']} (budget {READ_BUDGET} for trace_flow) · correct: {rec['correct']}")
