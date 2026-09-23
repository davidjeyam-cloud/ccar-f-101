"""
Gemini LLM wrapper — single place to configure the model that powers this
app's live demos. All pages import from here so swapping models means
editing one line. Mirrors agents101's utils/llm.py exactly (same function
names and retry behaviour), per the user's decision (2026-09-21) to reuse
the agents101 stack.

IMPORTANT — what this file is and is not:
- It runs the Gemini pattern demos every page in this course shows.
- The CCAR-F exam tests *Claude* behaviour (stop_reason, tool_choice,
  tool_result blocks, Message Batches). This file does not implement any
  of that — those mechanics are taught as st.code() snippets (see
  CLAUDE.md → Critical SDK Notes) until a page is flagged 🔑, at which
  point a CLAUDE_MODEL constant and the `anthropic` SDK are added here,
  next to MODEL below, per CLAUDE.md → Claude API Key Reminder Standard.
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception
)

load_dotenv()

MODEL = "gemini-2.5-flash"


def _is_retryable(exc: BaseException) -> bool:
    """Retry on 503 / UNAVAILABLE — transient Google capacity spikes."""
    msg = str(exc)
    return "503" in msg or "UNAVAILABLE" in msg


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set. Copy .env.example to .env and add your key.")
    return genai.Client(api_key=api_key)


@retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=1, min=3, max=20),
    stop=stop_after_attempt(4),
    reraise=True,
)
def _call(fn, *args, **kwargs):
    """Retry wrapper — retries up to 4x on 503, with 3-20s backoff. The final
    error (after retries are exhausted) is re-raised, never swallowed — the
    caller must show it (CLAUDE.md guardrail 8: never hide an API failure)."""
    return fn(*args, **kwargs)


def chat(prompt: str, history: list[dict] | None = None, system: str | None = None) -> str:
    """
    Simple single-turn or multi-turn chat.

    Args:
        prompt:  The user's message.
        history: Prior turns — each dict has keys 'role' ('user'/'model') and 'parts' (str).
        system:  Optional system instruction.

    Returns:
        The model's reply as a plain string.
    """
    client = _client()

    if history:
        config = types.GenerateContentConfig(system_instruction=system) if system else None
        convo = client.chats.create(model=MODEL, history=history, config=config)
        response = _call(convo.send_message, prompt)
    else:
        config = types.GenerateContentConfig(system_instruction=system) if system else None
        response = _call(
            client.models.generate_content,
            model=MODEL,
            contents=prompt,
            config=config,
        )

    return response.text


def chat_with_tools(
    prompt: str,
    tools: list,
    history: list[dict] | None = None,
    system: str | None = None,
) -> tuple[str, list]:
    """
    Chat with function-calling tools enabled (manual loop — automatic calling disabled,
    so every tool call is visible — see CLAUDE.md Critical SDK Notes A).

    Args:
        prompt:  The user's message.
        tools:   List of Python callables — SDK auto-generates the schema.
        history: Prior conversation turns.
        system:  Optional system instruction.

    Returns:
        Tuple of (reply_text, updated_history).
    """
    client = _client()
    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction=system,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    convo = client.chats.create(model=MODEL, history=history or [], config=config)
    response = _call(convo.send_message, prompt)
    return response.text, convo.get_history()
