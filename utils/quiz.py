"""
Quiz system: seed concepts per page + Gemini-powered MCQ generation.

Two sources of questions, per CLAUDE.md deviation 2 (reversed from agents101):
  1. utils/question_bank.py — curated, original, HUMAN-VERIFIED questions,
     tagged by task statement / scenario. These are the only ones that count
     as "verified" for the readiness gates.
  2. generate_questions() below — Gemini generates fresh variants from the
     PHASE_SEEDS concepts every quiz session. Its output MUST be labelled
     "unverified" wherever it is shown (CLAUDE.md checklist item 4).

Concepts here are Claude/CCAR-F-specific (reversed from agents101's
LLM-agnostic rule) but must test judgment, trade-offs and failure modes —
never bare recall — and must never touch an out-of-scope topic
(see docs/SOURCES.md and CLAUDE.md's out-of-scope list).
"""
import json
import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

load_dotenv()

MODEL = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Seed bank — concept strings per built page/phase.
# Gemini generates fresh MCQ variants from these every quiz session.
# ---------------------------------------------------------------------------
PHASE_SEEDS: dict[str, dict] = {
    "0": {
        "title": "Phase 0 — Foundations",
        "icon": "🏗️",
        "status": "complete",
        "concepts": [
            "CCAR-F tests practical judgment about architecture, configuration and tradeoffs across Claude Code, the Claude Agent SDK, the Claude API and MCP — not recall of facts",
            "The exam draws 4 scenarios at random from a published bank of 6 (Support, CodeGen, Research, DevProd, CI, Extraction) — every scenario must be prepared, since any 4 may appear",
            "The official exam guide is the single ground truth for this workbench; a community claim that disagrees with it is labelled 'community claim, verify in current docs' rather than treated as fact",
            "This app's live demos run on Gemini for cost reasons (a deliberate, explicit decision), while the exam itself tests exact Claude API mechanics — so every interactive page shows the Claude term beside the Gemini one it actually ran, rather than presenting the Gemini call as if it were the Claude behaviour being tested",
            "Claude Code itself runs on a subscription with no API key involved; the Claude API (ANTHROPIC_API_KEY) is a separate, metered product only needed for the small set of 🔑-flagged pages where the exact Claude mechanic cannot be shown any other way",
            "A page marked 'concept + build' has no live demo in the app on purpose — the learning for that task statement happens by building the real thing in sandbox_project/ with real Claude Code, not by watching a simulation",
            "Passing this exam (scaled 720 of 1,000) is a fixed criterion-referenced bar, not a curve against other candidates — the score report also breaks down percent-correct by domain, though that breakdown does not itself decide pass/fail",
            "Topics the guide explicitly places out of scope (e.g. fine-tuning, computer use, vision, streaming implementation, prompt-caching internals) are excluded from this workbench even where they would be interesting to build, because studying them would not move the score",
            "A study approach that only reads about a task statement without building it violates this course's design: the Page Structure Standard requires a 'Build it in VS Code with Claude Code' step precisely because reading is not the same skill the exam measures",
        ],
        "snippets": [
            "# .env.example — real key values are never committed, only the variable name\nGEMINI_API_KEY=your_api_key_here\n# ANTHROPIC_API_KEY=your_api_key_here   (uncommented once bought, before Day 1)",
            "# push.ps1's secret scan runs before every commit -\n# it aborts if a real-looking key/token/password appears anywhere in the staged diff,\n# not just in .env (which is gitignored and never staged at all)",
            "# A 🔑-flagged page's banner logic (built with page 1.1):\n# if ANTHROPIC_API_KEY missing: show a big, slow-flashing reminder to buy the key\n# else: small static 'key detected' note - the page never blocks either way",
        ],
    },
}

_BANNED_TOPICS = (
    "fine-tuning or training models; API authentication, billing or account "
    "management; language/framework implementation detail beyond tool/schema "
    "config; deploying or hosting MCP servers; Claude's internal architecture, "
    "training or weights; Constitutional AI/RLHF/safety training; embedding "
    "models or vector databases; computer use; vision/image analysis; "
    "streaming/SSE implementation; rate limits, quotas or pricing calculations; "
    "OAuth/key rotation/auth protocol details; cloud-provider configuration; "
    "benchmarking or model comparison metrics; prompt-caching internals "
    "(knowing it exists is fine); token counting or tokenisation algorithms"
)

_PROMPT_TEMPLATE = """You are writing practice questions for the CCAR-F (Claude Certified \
Architect - Foundations) certification exam, for the page "{phase_title}".

━━━ SOURCE CONCEPTS (write questions that test judgment about these, not recall) ━━━
{concepts}

━━━ REPRESENTATIVE SNIPPETS ━━━
{snippets}

━━━ NEVER TOUCH THESE TOPICS (guide's explicit out-of-scope list) ━━━
{banned}

━━━ STYLE ━━━
Bad (recall):
  ✗  "What is the exam fee?"
Good (judgment/trade-off/failure-mode):
  ✓  "A learner reads every page in this workbench but skips every 'Build it in VS Code \
with Claude Code' step. What specific exam-relevant skill will their preparation most \
likely fail to develop, and why does reading alone not substitute for it?"
  ✓  "A page in this workbench runs its live demo on Gemini rather than the Claude API. \
Under what condition does that choice risk teaching the wrong lesson for the exam, and \
what does this workbench do to mitigate it?"

The wrong options must represent genuine misconceptions a thoughtful but surface-level \
learner would pick - plausible, not absurd.

Generate exactly {n} questions with this type distribution:
  - 3 x "scenario"  : a realistic situation, which approach, and WHY
  - 2 x "tradeoff"  : X vs Y under a specific constraint - which and why
  - 2 x "failure"   : a symptom is described - what is the root cause
  - 1 x "design"    : given a requirement, justify a decision

Return ONLY a valid JSON array, no markdown fences, no commentary.
Each element:
{{"q":"full question text","opts":["a","b","c","d"],"ans":0,"type":"scenario","explain":"2-3 sentence explanation citing the specific mechanism, not just 'because it is correct'"}}

Hard rules:
1. opts must contain exactly 4 plain-text strings - no "A.", "B)" prefixes
2. ans is 0-indexed
3. Never write or imply a real CCAR-F exam question - these are original practice items only
4. FINAL CHECK: if any banned topic appears anywhere, rewrite that question
"""


def _is_retryable(exc: BaseException) -> bool:
    msg = str(exc)
    return "503" in msg or "UNAVAILABLE" in msg


def generate_questions(phase_key: str, num_questions: int = 8) -> list[dict]:
    """
    Generate MCQ questions for a page using Gemini JSON mode.
    Returns list of dicts: {q, opts, ans, type, explain}.
    Callers MUST label this output "unverified" in the UI (CLAUDE.md rule) -
    only utils/question_bank.py entries are verified.
    Raises on API error, missing key, or malformed JSON - never fails silently.
    """
    if phase_key not in PHASE_SEEDS:
        raise ValueError(f"No seed concepts for phase '{phase_key}' yet")

    phase = PHASE_SEEDS[phase_key]
    prompt = _PROMPT_TEMPLATE.format(
        phase_title=phase["title"],
        n=num_questions,
        concepts="\n".join(f"- {c}" for c in phase["concepts"]),
        snippets="\n".join(f"- {s}" for s in phase["snippets"]),
        banned=_BANNED_TOPICS,
    )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_exponential(multiplier=1, min=3, max=20),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    def _call():
        return client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )

    response = _call()
    questions = json.loads(response.text)

    if not isinstance(questions, list) or len(questions) == 0:
        raise ValueError(f"Gemini returned unexpected structure: {response.text[:200]}")

    validated = []
    for q in questions[:num_questions]:
        if not all(k in q for k in ("q", "opts", "ans")):
            continue
        if not isinstance(q["opts"], list) or len(q["opts"]) != 4:
            continue
        if not isinstance(q["ans"], int) or not (0 <= q["ans"] <= 3):
            continue
        clean_opts = [
            re.sub(r'^\s*[\(\[]?[A-Da-d]\s*[\.\)\]\:\-]\s*', '', opt).strip()
            for opt in q["opts"]
        ]
        validated.append({
            "q": q["q"],
            "opts": clean_opts,
            "ans": q["ans"],
            "type": q.get("type", "scenario"),
            "explain": q.get("explain", ""),
            "verified": False,   # generator output is always "unverified"
        })

    if len(validated) < max(4, num_questions // 2):
        raise ValueError(f"Too few valid questions generated ({len(validated)}). Try regenerating.")

    return validated
