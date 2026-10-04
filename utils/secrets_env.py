"""
Copy the app's settings from Streamlit's Secrets into environment variables.

On your PC the settings live in `.env` (loaded by python-dotenv). A hosted copy of the app has no `.env`:
there they are entered in the app's Settings → Secrets, and Streamlit exposes them as `st.secrets`. The rest of
the code reads `os.getenv(...)` only, so this one function bridges the two. A value already in the environment
wins. Only the names listed here are copied, and no value is ever printed or logged.
"""

import os

import streamlit as st

NAMES = ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "SEC_EDGAR_USER_AGENT")


def load_secrets_into_env() -> None:
    try:
        available = {name: st.secrets[name] for name in NAMES if name in st.secrets}
    except Exception:                 # no secrets file at all (the normal case on a PC)
        return
    for name, value in available.items():
        if value and not os.environ.get(name):
            os.environ[name] = str(value)
