"""
my-laptop — a small MCP server written for learning (page D2.3.2, ➕ extra — not on the CCAR-F exam).

Run it directly to speak MCP over stdio:
    .venv\\Scripts\\python.exe mcp_servers\\laptop_server.py

It uses every server-side feature of MCP once, so each can be seen working:

    TOOLS        the MODEL decides when to call them
        get_hardware_spec · get_storage · get_folder_sizes · summarize_file_types · get_top_processes
        estimate_disk_runway · check_internet · web_search · save_note
    RESOURCES    the APPLICATION decides which to read and attach as context — data, not actions
        laptop://catalog/folders   a CSV saying what each folder is for and whether it may be cleared (MOCK)
        laptop://policy/cleanup    the clean-up rules (MOCK)
        laptop://notes             the notes that save_note writes
        laptop://drive/{letter}    a resource TEMPLATE: live figures for one drive
    PROMPTS      the USER picks one — ready-made questions with blanks to fill in
        health_check · cleanup_plan · can_it_run
    NOTIFICATIONS  progress and log messages sent WHILE a slow tool runs (get_folder_sizes, summarize_file_types)
    ELICITATION    the server asks the user a question mid-call: save_note asks before it writes
    ANNOTATIONS    hints on each tool: read-only or not, touches the outside world or not

What a server author controls — and what the exam cares about:
- The DESCRIPTION of each tool is the only thing a model reads when it chooses (guide TS 2.1).
- A FAILURE is reported as a failure (guide TS 2.2): `fail()` raises, the SDK sets `isError: true`, and the
  message carries errorCategory, isRetryable and a plain explanation. An empty result is not an error.
- RESOURCES give the agent a catalogue up front, so it does not have to explore with tool calls (guide TS 2.4).
- The server decides what it will NOT reveal. No tool returns the computer name, user name, serial numbers,
  network addresses or file contents, and file-system tools are limited to the home folder. Whatever a tool
  does return is sent to the model, so treat every field as leaving the machine.

Standard library only, plus `mcp` and (for web_search) `ddgs`. stdout carries the protocol, so logging goes
to stderr. A line starting with "NET " records each outgoing web request; the workbench's client reads those
lines to show when the web was contacted.
"""

from __future__ import annotations

import ctypes
import datetime
import json
import logging
import os
import platform
import shutil
import socket
import string
import subprocess
import sys
import time
from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel

log = logging.getLogger("my-laptop")
mcp = FastMCP("my-laptop")

HOME = Path.home().resolve()
DATA = Path(__file__).resolve().parent / "data"
NOTES = DATA / "my_notes.txt"          # written by save_note; gitignored
WALK_BUDGET_S = 8                      # file-system tools stop counting after this long and say so
MAX_FOLDERS = 25
GB = 1024 ** 3
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
READ_WEB = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
WRITES = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
FILE_TYPES = {
    "documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv", ".odt"},
    "images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic", ".webp", ".svg", ".tif", ".tiff"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm"},
    "audio": {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"},
    "archives and installers": {".zip", ".7z", ".rar", ".tar", ".gz", ".iso", ".exe", ".msi"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json", ".ipynb", ".java", ".c", ".cpp", ".go", ".rs", ".sql", ".yml", ".yaml"},
}


def fail(category: str, retryable: bool, message: str):
    """Report a tool failure the way guide TS 2.2 asks: a category, whether a retry can help, and why."""
    raise ToolError(json.dumps({"errorCategory": category, "isRetryable": retryable, "message": message}))


def _gb(n: int) -> float:
    return round(n / GB, 1)


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _home_folder(path: str) -> Path:
    """Turn the caller's path into a folder inside the home folder, or fail with a structured error."""
    target = (HOME / path).resolve() if path and not os.path.isabs(path) else Path(path or HOME).resolve()
    if target != HOME and HOME not in target.parents:
        fail("permission", False, "Only folders inside the home folder can be inspected. "
                                  "Give a path under the home folder, or leave it empty.")
    if not target.is_dir():
        fail("validation", False, f"'{path}' is not a folder inside the home folder. Check the name and try again.")
    return target


def _powershell(script: str, timeout: int = 12):
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                             capture_output=True, text=True, timeout=timeout)
        return json.loads(out.stdout) if out.returncode == 0 and out.stdout.strip() else None
    except Exception as exc:
        log.info("PowerShell query failed: %s", exc)
        return None


# ══ TOOLS — the model decides when to call them ══════════════════════════════
def _registry(path: str, name: str) -> str:
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
            return str(winreg.QueryValueEx(key, name)[0]).strip()
    except Exception:
        return ""


def _memory() -> dict:
    if platform.system() != "Windows":
        return {}

    class Status(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

    st = Status()
    st.dwLength = ctypes.sizeof(Status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
        return {}
    return {"ram_total_gb": _gb(st.ullTotalPhys), "ram_available_gb": _gb(st.ullAvailPhys),
            "ram_in_use_percent": int(st.dwMemoryLoad)}


@mcp.tool(annotations=READ_ONLY)
def get_hardware_spec() -> dict:
    """Describe this computer's hardware and operating system: maker and model, processor name, physical
    and logical core counts, total and currently available memory (RAM) in GB, graphics adapters, battery
    charge if it has a battery, and the Windows version.

    Takes no input. Use it for questions like "what laptop is this?", "how much RAM do I have?" or
    "is this machine good enough for X?".
    It does NOT report disk space (use get_storage), which folders are large (use get_folder_sizes) or
    which programs are using memory right now (use get_top_processes).
    It never returns the computer name, user name, serial numbers or network addresses.
    """
    cpu_key = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
    bios_key = r"HARDWARE\DESCRIPTION\System\BIOS"
    cim = (_powershell(
        "$p = Get-CimInstance Win32_Processor | Select-Object -First 1; "
        "$g = Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name }; "
        "$b = Get-CimInstance Win32_Battery | Select-Object -First 1; "
        "@{ cores = $p.NumberOfCores; graphics = @($g); "
        "battery = $(if ($b) { $b.EstimatedChargeRemaining } else { $null }) } | ConvertTo-Json -Compress")
        if platform.system() == "Windows" else None) or {}
    spec = {
        "maker": _registry(bios_key, "SystemManufacturer") or "unknown",
        "model": _registry(bios_key, "SystemProductName") or "unknown",
        "processor": _registry(cpu_key, "ProcessorNameString") or platform.processor() or "unknown",
        "physical_cores": cim.get("cores"),
        "logical_cores": os.cpu_count(),
        **_memory(),
        "graphics": cim.get("graphics") or [],
        "battery_percent": cim.get("battery"),
        "operating_system": f"{platform.system()} {platform.release()} (build {platform.version()})",
        "architecture": platform.machine(),
        "measured_at": _now(),
    }
    if not cim and platform.system() == "Windows":
        spec["note"] = "Core count, graphics and battery were unavailable: the Windows inventory query failed."
    return spec


def _drives() -> list:
    roots = ([f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]
             if platform.system() == "Windows" else ["/"])
    rows = []
    for root in roots:
        try:
            u = shutil.disk_usage(root)
        except OSError as exc:                       # e.g. an empty card reader — report it, keep going
            rows.append({"drive": root, "error": str(exc)})
            continue
        rows.append({"drive": root, "total_gb": _gb(u.total), "used_gb": _gb(u.used), "free_gb": _gb(u.free),
                     "used_percent": round(100 * u.used / u.total, 1) if u.total else 0})
    return rows


@mcp.tool(annotations=READ_ONLY)
def get_storage() -> dict:
    """Report how full each disk drive on this computer is: total size, space used, space free (in GB) and
    the percentage used, one row per drive.

    Takes no input. Use it for "how much disk space is left?" or "which drive is nearly full?".
    It reports whole drives only. To see WHICH folders take the space use get_folder_sizes; for WHAT KIND of
    files use summarize_file_types; to project when a drive fills up use estimate_disk_runway.
    """
    drives = _drives()
    return {"drives": drives, "count": len(drives), "measured_at": _now()}


def _tree_size(top: Path, deadline: float) -> tuple:
    total = files = 0
    complete = True
    for dirpath, dirnames, filenames in os.walk(top, onerror=lambda e: None, followlinks=False):
        if time.time() > deadline:
            complete = False
            dirnames[:] = []
            break
        for name in filenames:
            try:
                total += os.lstat(os.path.join(dirpath, name)).st_size
                files += 1
            except OSError:
                pass
    return total, files, complete


@mcp.tool(annotations=READ_ONLY)
async def get_folder_sizes(ctx: Context, path: str = "") -> dict:
    """List the folders directly inside one folder with the size of each (GB) and its file count, largest
    first. Use it to find WHICH folders take up disk space.

    Input: `path` — a folder inside your home folder, either absolute ("C:\\Users\\you\\Downloads") or
    relative to home ("Downloads", "Documents\\Projects"). Leave it empty for the home folder itself.
    Example questions: "what's using the space in my Downloads folder?", "which of my folders is biggest?".

    Limits: only folders inside the home folder are allowed (anything else is refused); it returns names
    and sizes, never file contents; counting stops after about 8 seconds, and `complete` is then false with
    the sizes counted so far. For whole-drive totals use get_storage; for a breakdown by kind of file
    (documents, images, video…) use summarize_file_types.
    """
    target = _home_folder(path)
    deadline = time.time() + WALK_BUDGET_S
    rows, complete, loose = [], True, 0
    try:
        children = sorted(target.iterdir(), key=lambda p: p.name.lower())
    except OSError as exc:
        fail("permission", False, f"The folder could not be read: {exc}")
    await ctx.info(f"Counting {len(children)} entries (budget {WALK_BUDGET_S} s)")
    for n, child in enumerate(children, 1):
        await ctx.report_progress(n, len(children), f"entry {n} of {len(children)}")
        try:
            if child.is_symlink():
                continue
            if child.is_file():
                loose += child.lstat().st_size
            elif child.is_dir():
                if time.time() > deadline:
                    complete = False
                    continue
                size, files, done = _tree_size(child, deadline)
                complete = complete and done
                rows.append({"folder": child.name, "size_gb": round(size / GB, 2), "files": files})
        except OSError:
            continue
    if not complete:
        await ctx.warning("Time budget reached: the sizes are partial")
    rows.sort(key=lambda r: r["size_gb"], reverse=True)
    return {"inside": "home folder" if target == HOME else str(target.relative_to(HOME)),
            "folders": rows[:MAX_FOLDERS], "folders_found": len(rows),
            "files_directly_inside_gb": round(loose / GB, 2), "complete": complete,
            "note": "" if complete else f"Counting stopped after {WALK_BUDGET_S} seconds: sizes are partial "
                                        "and some folders were not counted."}


@mcp.tool(annotations=READ_ONLY)
async def summarize_file_types(ctx: Context, path: str = "") -> dict:
    """Break a folder's contents down by KIND of file — documents, images, video, audio, archives and
    installers, code, other — with the total size (GB) and file count of each kind, largest first.

    Input: `path` — a folder inside your home folder (absolute, or relative to home such as "Downloads").
    Leave it empty for the whole home folder.
    Use it for "what kind of files fill my Downloads?" or "how much of my space is video?".
    It returns totals per kind only: no file or folder names. Counting stops after about 8 seconds and
    `complete` is then false. For sizes per folder use get_folder_sizes instead.
    """
    target = _home_folder(path)
    kind_of = {ext: kind for kind, exts in FILE_TYPES.items() for ext in exts}
    totals = {kind: [0, 0] for kind in [*FILE_TYPES, "other"]}
    deadline, complete, seen = time.time() + WALK_BUDGET_S, True, 0
    for dirpath, dirnames, filenames in os.walk(target, onerror=lambda e: None, followlinks=False):
        if time.time() > deadline:
            complete = False
            break
        for name in filenames:
            try:
                size = os.lstat(os.path.join(dirpath, name)).st_size
            except OSError:
                continue
            kind = kind_of.get(os.path.splitext(name)[1].lower(), "other")
            totals[kind][0] += size
            totals[kind][1] += 1
            seen += 1
            if seen % 5000 == 0:
                await ctx.report_progress(seen, None, f"{seen:,} files counted")
    if not complete:
        await ctx.warning("Time budget reached: the totals are partial")
    kinds = sorted(({"kind": k, "size_gb": round(v[0] / GB, 2), "files": v[1]} for k, v in totals.items()),
                   key=lambda r: r["size_gb"], reverse=True)
    return {"inside": "home folder" if target == HOME else str(target.relative_to(HOME)), "kinds": kinds,
            "files_counted": seen, "complete": complete,
            "note": "" if complete else f"Counting stopped after {WALK_BUDGET_S} seconds: totals are partial."}


@mcp.tool(annotations=READ_ONLY)
def get_top_processes(by: str = "memory", limit: int = 8) -> dict:
    """List the programs currently using the most memory or processor time on this computer: program name,
    memory in MB, processor seconds used so far, and how many copies are running.

    Input: `by` — "memory" (default) or "cpu". `limit` — 1 to 20, default 8.
    Use it for "what is using my memory?", "why is my laptop slow right now?".
    It reports what is running NOW. For the computer's total and free memory use get_hardware_spec.
    It returns program names only: no window titles, file paths or user names.
    """
    if by not in ("memory", "cpu"):
        fail("validation", False, "`by` must be \"memory\" or \"cpu\".")
    if platform.system() != "Windows":
        fail("configuration", False, "This tool is written for Windows.")
    limit = max(1, min(int(limit or 8), 20))
    rows = _powershell(
        "Get-Process | Group-Object ProcessName | ForEach-Object { [pscustomobject]@{ name = $_.Name; "
        "memory_mb = [math]::Round((($_.Group | Measure-Object WorkingSet64 -Sum).Sum) / 1MB, 0); "
        "cpu_seconds = [math]::Round((($_.Group | Measure-Object CPU -Sum).Sum), 0); copies = $_.Count } } "
        "| ConvertTo-Json -Compress")
    if rows is None:
        fail("transient", True, "Windows did not return the process list. Try again.")
    rows = rows if isinstance(rows, list) else [rows]
    rows.sort(key=lambda r: r.get("memory_mb" if by == "memory" else "cpu_seconds") or 0, reverse=True)
    return {"sorted_by": by, "processes": rows[:limit], "programs_running": len(rows), "measured_at": _now()}


@mcp.tool(annotations=READ_ONLY)
def estimate_disk_runway(daily_growth_gb: float, drive: str = "C") -> dict:
    """Project when a drive will be full if it keeps filling at a steady rate. Returns the days left until
    full, the date it would fill up, and the expected used space (GB) today and after 30, 90, 180 and 365
    days.

    Input: `daily_growth_gb` — GB added per day, e.g. 0.5 (must be above 0). `drive` — the drive letter,
    default "C".
    Use it for "how long until my disk is full if I add 2 GB a day?". It is arithmetic on today's free
    space: a projection, not a measurement. For today's figures alone use get_storage.
    """
    try:
        growth = float(daily_growth_gb)
    except (TypeError, ValueError):
        fail("validation", False, "`daily_growth_gb` must be a number, e.g. 0.5.")
    if growth <= 0:
        fail("validation", False, "`daily_growth_gb` must be above 0.")
    root = (str(drive).strip()[:1] or "C").upper() + ":\\"
    row = next((d for d in _drives() if d["drive"] == root and "error" not in d), None)
    if row is None:
        fail("validation", False, f"There is no readable drive '{root}'. Call get_storage to see the drives.")
    days = row["free_gb"] / growth
    full_on = (datetime.date.today() + datetime.timedelta(days=int(days))).isoformat()
    points = [{"after_days": d, "used_gb": round(min(row["total_gb"], row["used_gb"] + growth * d), 1)}
              for d in (0, 30, 90, 180, 365)]
    return {"drive": root, "total_gb": row["total_gb"], "used_gb_today": row["used_gb"], "free_gb_today": row["free_gb"],
            "daily_growth_gb": growth, "days_until_full": int(days), "full_on": full_on, "projection": points,
            "note": "A straight-line projection from today's free space. Real growth is rarely steady."}


@mcp.tool(annotations=READ_WEB)
def check_internet() -> dict:
    """Test whether this computer can reach the internet right now, and how quickly: it opens a connection
    to three well-known websites and reports, for each, whether it worked and the time taken in ms.

    Takes no input. Use it for "am I online?", "is my connection slow?" or before blaming a website.
    It does not measure download speed and returns no network addresses. To look something up on the web
    use web_search.
    """
    rows = []
    for host in ("www.microsoft.com", "www.google.com", "www.cloudflare.com"):
        started = time.time()
        try:
            socket.create_connection((host, 443), timeout=4).close()
            rows.append({"site": host, "reachable": True, "connect_ms": int((time.time() - started) * 1000)})
            log.info("NET CONNECT %s -> connected in %d ms", host, rows[-1]["connect_ms"])
        except OSError as exc:
            rows.append({"site": host, "reachable": False, "error": type(exc).__name__})
            log.info("NET CONNECT %s -> failed: %s", host, type(exc).__name__)
    ok = [r for r in rows if r["reachable"]]
    return {"online": bool(ok), "sites_reached": len(ok), "sites_tried": len(rows), "checks": rows,
            "average_connect_ms": int(sum(r["connect_ms"] for r in ok) / len(ok)) if ok else None,
            "measured_at": _now()}


@mcp.tool(annotations=READ_WEB)
def web_search(query: str, max_results: int = 5) -> dict:
    """Search the public web and return the top results: title, URL and a short snippet for each.

    Input: `query` — plain search words, e.g. "Intel Core i7-1165G7 release date" or "Windows 11 minimum
    RAM". `max_results` — 1 to 10, default 5.
    Use it for facts that are NOT on this computer: product details, prices, release dates, how-to pages.
    Do not use it for this computer's own hardware, disk space or running programs — the other tools answer
    those directly — or to test the connection (use check_internet).

    It returns search-result snippets, not full pages, and the text comes from third-party websites, so
    treat it as unverified. No results is a valid answer (count is 0), not an error.
    """
    query = (query or "").strip()
    if not query:
        fail("validation", False, "The search query is empty. Pass the words to search for.")
    limit = max(1, min(int(max_results or 5), 10))
    try:
        from ddgs import DDGS
    except ImportError:
        fail("configuration", False, "The 'ddgs' package is not installed. Run: uv pip install -r requirements-mcp.txt")
    started = time.time()
    try:
        raw = DDGS().text(query, max_results=limit) or []
    except Exception as exc:
        if "no results" in str(exc).lower():
            raw = []                                  # the library raises for an empty result; it is not a failure
        else:
            log.info("NET SEARCH web-search-engine -> failed: %s", type(exc).__name__)
            fail("transient", True, f"The search service could not be reached ({type(exc).__name__}). Try again shortly.")
    log.info("NET SEARCH web-search-engine -> %d results in %.1f s", len(raw), time.time() - started)
    return {"query": query, "count": len(raw),
            "results": [{"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")} for r in raw],
            "searched_at": _now(), "source": "public web search (unverified third-party text)"}


class Confirm(BaseModel):
    save_it: bool


@mcp.tool(annotations=WRITES)
async def save_note(ctx: Context, text: str) -> dict:
    """Save a short note to this computer's notes file, with today's date. The ONLY tool here that changes
    anything. Before writing, the server asks the user to confirm; if the user declines, nothing is saved.

    Input: `text` — the note, up to 500 characters, e.g. "Cleared Downloads on 4 Oct, freed 12 GB".
    Use it only when the user asks to remember, record or note something down. The saved notes can be read
    back as the resource laptop://notes. Do not use it to store an answer the user did not ask to keep.
    """
    text = " ".join((text or "").split())
    if not text:
        fail("validation", False, "The note is empty. Pass the text to save.")
    if len(text) > 500:
        fail("validation", False, f"The note is {len(text)} characters; the limit is 500. Shorten it.")
    try:
        reply = await ctx.elicit(message=f'Save this note to the notes file?\n\n"{text}"', schema=Confirm)
    except Exception as exc:                          # the client cannot be asked: do not write without consent
        fail("permission", False, f"The user could not be asked to confirm ({type(exc).__name__}), so nothing was saved.")
    if reply.action != "accept" or not reply.data.save_it:
        return {"saved": False, "reason": "The user declined, so nothing was written.", "user_action": reply.action}
    NOTES.parent.mkdir(exist_ok=True)
    with open(NOTES, "a", encoding="utf-8") as f:
        f.write(f"{datetime.date.today().isoformat()}  {text}\n")
    count = sum(1 for _ in open(NOTES, encoding="utf-8"))
    return {"saved": True, "notes_in_file": count, "read_them_at": "laptop://notes", "saved_at": _now()}


# ══ RESOURCES — data the application reads and attaches; nothing here acts ════
@mcp.resource("laptop://catalog/folders", name="folder_catalog", title="Folder catalogue (MOCK)", mime_type="text/csv",
              description="What each common folder is for, whether it is safe to clear, and how many days to keep "
                          "its files. Example data for learning — not read from this computer.")
def folder_catalog() -> str:
    return (DATA / "folder_catalog.csv").read_text(encoding="utf-8")


@mcp.resource("laptop://policy/cleanup", name="cleanup_policy", title="Clean-up policy (MOCK)", mime_type="text/markdown",
              description="The rules for clearing disk space: what may be deleted, what needs a person to review, "
                          "and how much free space to keep. Example data for learning.")
def cleanup_policy() -> str:
    return (DATA / "cleanup_policy.md").read_text(encoding="utf-8")


@mcp.resource("laptop://notes", name="my_notes", title="My notes", mime_type="text/plain",
              description="The notes saved with the save_note tool, one per line with its date. Empty until a note is saved.")
def my_notes() -> str:
    return NOTES.read_text(encoding="utf-8") if NOTES.exists() else "(no notes saved yet)"


@mcp.resource("laptop://drive/{letter}", name="drive", title="One drive, live", mime_type="application/json",
              description="Live figures for one drive: total, used and free space in GB. Put the drive letter in the "
                          "URI, e.g. laptop://drive/C. A resource TEMPLATE: one definition, many URIs.")
def drive(letter: str) -> str:
    root = f"{letter[:1].upper()}:\\"
    row = next((d for d in _drives() if d["drive"] == root), None)
    return json.dumps(row or {"drive": root, "error": "no such drive"}, indent=2)


# ══ PROMPTS — ready-made questions the user picks and fills in ═══════════════
@mcp.prompt(title="Laptop health check", description="A full check of this laptop: hardware, memory in use, disk space and connection.")
def health_check() -> str:
    return ("Give me a health check of this laptop. Report its hardware, how much memory is free and which "
            "programs use the most, how full each drive is, and whether the internet connection works. "
            "Finish with the one thing I should look at first.")


@mcp.prompt(title="Clean-up plan for a folder", description="Find what fills a folder and propose what to clear, following the clean-up policy.")
def cleanup_plan(folder: str = "Downloads") -> str:
    return (f"Make a clean-up plan for my {folder} folder. Show which folders inside it are largest and what kinds "
            f"of files fill it. Follow the attached folder catalogue and clean-up policy if they are provided: say "
            f"what may be cleared, what needs my review, and what must be kept. Do not delete anything.")


@mcp.prompt(title="Can this laptop run it?", description="Compare this laptop's hardware with a program's or game's published requirements.")
def can_it_run(software: str) -> str:
    return (f"Can this laptop run {software}? Read this laptop's hardware, search the web for the minimum and "
            f"recommended requirements of {software}, and compare them line by line: processor, memory, graphics, "
            f"free disk space. Say clearly whether it meets the minimum and the recommended level.")


if __name__ == "__main__":
    sys.exit(mcp.run())           # stdio transport
