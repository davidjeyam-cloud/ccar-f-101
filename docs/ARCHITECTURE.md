# Architecture — CCAR-F Study Workbench (ccar-f-101)

> Progressive-disclosure doc, same pattern as agents101. Canonical index is `AGENTS.md`; full rules are in `CLAUDE.md`.

**Status: Stage B in progress.** `app.py`, `utils/` and the first page (`00_Hello_Claude`) exist and pass the commit checklist. Everything else below still describes the *target* structure. Update this file whenever it changes.

---

## Overview

`ccar-f-101` is a study workbench for the **Claude Certified Architect – Foundations** exam (CCAR-F). It has two halves:

| # | Half | Where | Role |
|---|---|---|---|
| 1 | **Build** | VS Code + Claude Code panel, in `sandbox_project/` | Where the learning mainly happens: each topic is built by hand, then deliberately broken |
| 2 | **Track** | Streamlit app in the browser (`localhost:8501`) | Progress, small visual demos, the question bank, timed mocks, the error log |

The official exam guide (`docs/source/`, local only) is the ground truth for topics, weights, scenarios and the out-of-scope list.

---

## System Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│  VS Code                                                              │
│   ├─ editor            read / review files                            │
│   ├─ terminal          streamlit run · uv · git (push.ps1)            │
│   └─ Claude Code panel  /next-page · builds pages · sandbox exercises │
└───────────────┬──────────────────────────────────┬────────────────────┘
                │ builds                            │ runs
                ▼                                   ▼
┌───────────────────────────────┐   ┌──────────────────────────────────┐
│  sandbox_project/             │   │  Streamlit app  (app.py → pages/) │
│  real Claude Code exercises   │   │                                   │
│  CLAUDE.md · .claude/rules    │   │  Ph0 Foundations                  │
│  commands · skills · .mcp.json│   │  Ph1 Agentic (27%)  Ph2 Tools (18%)│
│  (fake data only)             │   │  Ph3 Claude Code (20%) Ph4 Prompts │
└───────────────────────────────┘   │  (20%)  Ph5 Context (15%)         │
                                    │  Ph6 Capstones (6 scenarios)      │
                                    │  Ph7 Exam Readiness               │
                                    └───────────────┬───────────────────┘
                                                    │
                       ┌────────────────────────────▼───────────────────┐
                       │  utils/                                          │
                       │  llm.py           Gemini SDK, pinned model,     │
                       │                   retry wrapper                 │
                       │  tools.py         fake support backend          │
                       │  diagrams.py      matplotlib → PNG              │
                       │  styles.py · trace.py                           │
                       │  quiz.py          PHASE_SEEDS + generator       │
                       │  question_bank.py curated original questions    │
                       │  progress.py      progress.json (gitignored)    │
                       └───────────────┬─────────────────────────────────┘
                                       │ only for live demos
                       ┌───────────────▼─────────────────────────────────┐
                       │  Google Gemini 2.5 Flash (GEMINI_API_KEY in .env)│
                       │  No key → clear message; app still works         │
                       └──────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Why |
|---|---|---|
| **Claude Code** | Claude subscription | Where the building happens; no API key needed for it |
| **LLM** | Google Gemini 2.5 Flash (`gemini-2.5-flash`), pinned in `utils/llm.py` | Same model and key as agents101; change in one place only |
| **SDK** | `google-genai` | Current non-deprecated Gemini SDK (same as agents101) |
| **UI** | Streamlit multi-page | Same as agents101; zero boilerplate |
| **Validation** | `pydantic`, `jsonschema` | Domain 4 validation-retry demos |
| **Retry** | `tenacity` | Overload and rate-limit handling |
| **Diagrams** | `matplotlib` → PNG; `arch-diagram` skill → HTML → JPEG | Same pipelines as agents101 |
| **Env** | `python-dotenv`, `.env` (gitignored), `.env.example` (committed) | Key never enters the repo |
| **Not installed** | `anthropic` SDK, Claude Agent SDK | Claude-specific mechanics taught with `st.code()` beside the Gemini equivalent, and built for real with Claude Code in `sandbox_project/` |

---

## Learning Phases

| Phase | Title | Weight | Pages | Status |
|---|---|---|---|---|
| 0 | Foundations | n/a | Hello Claude ✅, Home ✅, Exam Blueprint ✅, Study Plan, Approach Scorecard, Tool-Use Primer, Quiz Hub | 🔜 (3/7) |
| 1 | Agentic Architecture & Orchestration | 27% | 1.1 ★ · 1.2 · 1.3 · 1.4 ★ · 1.5 · 1.6 · 1.7 | 🔜 |
| 2 | Tool Design & MCP Integration | 18% | 2.1 ★ · 2.2 · 2.3 ★ · 2.4 · 2.5 | 🔜 |
| 3 | Claude Code Configuration & Workflows | 20% | 3.1 ★ · 3.2 · 3.3 ★ · 3.4 · 3.5 · 3.6 ★ | 🔜 |
| 4 | Prompt Engineering & Structured Output | 20% | 4.1 · 4.2 · 4.3 ★ · 4.4 · 4.5 ★ · 4.6 | 🔜 |
| 5 | Context Management & Reliability | 15% | 5.1 ★ · 5.2 · 5.3 · 5.4 · 5.5 ★ · 5.6 | 🔜 |
| 6 | Capstones | n/a | 06a CodeGen · 06b CI · 06c Extraction · 06d Support · 06e Research · 06f DevProd | 🔜 |
| 7 | Exam Readiness | n/a | Timed Mock, Error Log (gates), Exam Day | 🔜 |

★ = real interactive demo; all other pages are "concept + build".
Coverage: **30 task statements** across 5 domains + **6 scenarios** = the full guide blueprint.

---

## CONCEPTS section

A second learning surface beside the phases (added 2026-09-26). It changes none of the structure above.

```
sidebar:  (top)  CONCEPTS ─ All concepts (index: domain tabs + cards)
          CONCEPTS · D1 … D5 ─ the 30 numbered concepts   (41 cross-cutting concepts: registered, hidden)
          (then) the 8 phase groups, unchanged; Hello Claude remains the landing page (default=True)

concept page = utils/concept_page.py  ← utils/concepts_content/<slug>.py  (ConceptContent)
  code lab: editor ─ Run ─▶ utils/lab_runner.py ─▶ separate Python process (10 s timeout, no API keys)
                                                     ├─ utils/mock_claude.py  SIMULATED Claude-shaped client
                                                     └─ utils/tools.py        fake support backend
            events ◀─ utils/lab_trace.py ─ JSON ─▶ step table + flowchart coloured along the path taken
```

| # | Design point | Why |
|---|---|---|
| 1 | Scope follows the official guide; the community list only supplies the layout | 30 of the 71 listed concepts have no matching guide content; 3 are explicitly out of scope |
| 2 | Learner code runs in a child process with a timeout and no keys | An accidental infinite loop can't hang the app; no secret can leak into a lab |
| 3 | The model is simulated and labelled SIMULATED | Deterministic, free, offline — and honest: it is not real Claude |
| 4 | Distractors are runnable variants whose failure was observed | Every "why it fails" claim was seen happening before it was written |
| 5 | Every concept is grounded in the official Claude docs (platform.claude.com + code.claude.com); pages list what was read, when, and tag each claim docs / guide / recommendation / simulated | The first Agentic Loops page taught two stop reasons where the docs list seven — grounding is now a rule, not a habit |
| 6 | Kinds: exam · ➕ extra (not in the guide, docs-covered) · ungroundable · excluded | The guide decides scope; the docs decide what can be built and how it behaves. Extras never enter the exam question bank |

---

## Key Design Principles

### 1. The official guide is ground truth
Topics, weights, scenarios and the out-of-scope list come from the guide. Community material is labelled "community claim, verify in current docs". See `SOURCES.md`.

### 2. Learn by building; the app tracks
Each page ends with "🛠️ Build it in VS Code with Claude Code" (prompt + done-when checklist) and four ticks: Read · Demo · Built · Quiz passed. Pages without a live demo are "concept + build".

### 3. Break things on purpose
Every capstone has three break tests: deliberately trigger the failure the exam tempts you to misdiagnose, then record symptom · root cause · right first fix · two tempting wrong fixes.

### 4. Every Claude call shows its work
The `🔬 Execution Trace` shows exact prompts, raw responses, finish reason (with the Claude term beside it), function_call/response blocks, function-calling mode and token counts.

### 5. No key must not break the app
Pure-Python demos and quizzes need no key. Live demos show a clear "needs GEMINI_API_KEY" message. Any simulated fallback is labelled SIMULATED and is never passed off as a real Claude response.

### 6. Original questions only
`utils/question_bank.py` holds curated, original, scenario-tagged questions. Generated questions are labelled "unverified". Real exam questions are never reproduced.

### 7. Comparisons are numbered tables
Six comparison tables are mandatory (see `CLAUDE.md`).

---

## File Structure (target)

```
ccar-f-101/
├── app.py                      # Streamlit entry — navigation           (Stage B)
├── pages/                      # 46 pages + concepts_index.py           (Stage B)
├── utils/
│   ├── llm.py · tools.py · diagrams.py · styles.py · trace.py · quiz.py
│   ├── question_bank.py        # curated, original questions
│   ├── progress.py             # personal progress (progress.json, gitignored)
│   ├── concepts_map.py · concept_page.py · concept_types.py     # CONCEPTS taxonomy / renderer / types
│   ├── lab_runner.py · lab_harness.py · lab_trace.py · mock_claude.py   # CONCEPTS code lab engine
│   ├── agent_playground.py · research_playground.py · playground_ui.py  # CONCEPTS agent playgrounds (single agent / multi-agent / fork)
│   ├── session_lab.py · session_play.py · support_lab.py · escalation_play.py  # D1.4 / D1.5 simulated backends + playgrounds
│   ├── handoff_lab/play · memory_lab/play · decomp_lab/play  # D1.6 / D1.7 / D1.8 simulated backends + playgrounds
│   ├── tool_select_lab · toolsel_play · toolchoice_lab/play · mcp_lab/play  # D2.1 / D2.2 / D2.3 simulated backends + playgrounds
│   ├── hooks_lab · hooks_play  # D2.4 simulated Agent SDK hook runner + playground
│   ├── research_backend.py · guide_index.py                              # fake research backend · exact guide-PDF positions
│   └── concepts_content/       # one module per built concept (agentic_loops.py = template)
├── sandbox_project/            # real Claude Code exercises, fake data only
├── docs/
│   ├── ARCHITECTURE.md         # this file
│   ├── APPROACH_SCORECARD.md   # stub — purpose to be confirmed
│   ├── SOURCES.md · STUDY_PLAN.md
│   ├── source/                 # official guide PDF — LOCAL ONLY, gitignored
│   ├── reference/              # agents101_CLAUDE.md
│   └── images/                 # exported diagrams
├── .claude/
│   ├── skills/arch-diagram/    # HTML architecture-diagram generator
│   └── commands/next-page.md   # /next-page
├── .streamlit/config.toml      # light theme (same as agents101)
├── AGENTS.md · CLAUDE.md · push.ps1 · requirements.txt
└── .env.example                # template — copy to .env
```

Present today (Stage A): `AGENTS.md`, `CLAUDE.md`, `push.ps1`, `requirements.txt`, `.env.example`, `.gitignore`, `.streamlit/`, `docs/`, `.claude/`.

---

## Running Locally

```powershell
cd c:\Users\abc\devtools\ccar-f-101
uv venv
uv pip install -r requirements.txt
copy .env.example .env               # add GEMINI_API_KEY — live demos only
.venv\Scripts\python.exe -m streamlit run app.py
```
Open http://localhost:8501.
