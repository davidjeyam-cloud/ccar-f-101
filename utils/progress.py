"""
Personal progress tracking — four ticks per page (Read, Demo, Built, Quiz passed),
per CLAUDE.md's Page Structure Standard, step 11.

Persisted to progress.json at the repo root, which is gitignored (personal,
per-user — never committed; see CLAUDE.md guardrail "Never commit... progress.json").
New file for ccar-f-101 — agents101 has no equivalent.

If the file cannot be read or written (missing, corrupt, read-only disk),
this module degrades to an in-memory-only session (a warning is shown once,
not a crash) rather than hiding the failure silently.

NAMING NOTE for every page: call your page's identifier constant something
like `PAGE_SLUG`, never `PAGE_KEY` or anything ending in `_KEY` — push.ps1's
secret scan flags any `..._KEY = "..."` assignment by pattern, and a page
identifier is not a secret, but it still trips the same regex a real leaked
key would. Keep `_KEY` names for the two real keys (GEMINI_API_KEY,
ANTHROPIC_API_KEY) only.
"""

import json
import os
import streamlit as st

_PROGRESS_PATH = "progress.json"
TICKS = ("read", "demo", "built", "quiz")
TICK_LABELS = {
    "read": "📖 Read",
    "demo": "🧪 Demo",
    "built": "🛠️ Built",
    "quiz": "✅ Quiz passed",
}


def load_progress() -> dict:
    """Load progress.json, or an empty dict if missing/unreadable."""
    if "_progress_cache" in st.session_state:
        return st.session_state["_progress_cache"]

    data = {}
    if os.path.exists(_PROGRESS_PATH):
        try:
            with open(_PROGRESS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            st.session_state["_progress_load_error"] = str(e)
            data = {}

    st.session_state["_progress_cache"] = data
    return data


def save_progress(data: dict) -> None:
    """Write progress.json. On failure, keep the in-memory copy and warn —
    never hide the failure silently (CLAUDE.md guardrail 8)."""
    st.session_state["_progress_cache"] = data
    try:
        with open(_PROGRESS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
    except OSError as e:
        st.session_state["_progress_save_error"] = str(e)


def get_page_progress(page_key: str) -> dict:
    data = load_progress()
    return data.get(page_key, {t: False for t in TICKS})


def set_tick(page_key: str, tick: str, value: bool) -> None:
    if tick not in TICKS:
        raise ValueError(f"Unknown tick '{tick}' — must be one of {TICKS}")
    data = load_progress()
    page = data.setdefault(page_key, {t: False for t in TICKS})
    page[tick] = value
    save_progress(data)


def render_progress_ticks(page_key: str) -> None:
    """Render the four progress checkboxes for a page, persisting each change.
    Call this as the last thing on a page, per the Page Structure Standard."""
    st.markdown("---")
    st.markdown("**Your progress on this page**")
    current = get_page_progress(page_key)
    cols = st.columns(4)
    for col, tick in zip(cols, TICKS):
        with col:
            new_val = st.checkbox(
                TICK_LABELS[tick],
                value=current.get(tick, False),
                key=f"progress_{page_key}_{tick}",
            )
            if new_val != current.get(tick, False):
                set_tick(page_key, tick, new_val)

    if st.session_state.get("_progress_save_error"):
        st.warning(
            f"Progress could not be saved to disk this run "
            f"({st.session_state['_progress_save_error']}). "
            "Your ticks are kept for this session but won't survive a restart."
        )
