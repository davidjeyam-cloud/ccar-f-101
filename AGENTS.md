# CCAR-F Study Workbench — ccar-f-101

> Canonical project index. Read this before anything else. Deep detail lives in `CLAUDE.md` and `docs/`.

---

## What This Is

A study workbench for the **Claude Certified Architect – Foundations** exam (CCAR-F, guide v1.0, effective July 2026), built as a **Streamlit multi-page app**. It mirrors the structure and conventions of the earlier repo `agents101`.

The learning happens in VS Code with Claude Code: each topic is built by hand (learn by doing), then quizzed. The app tracks progress and shows small visual demos.

**Ground truth:** the official exam guide (`docs/source/*.pdf`, local only, never committed). It wins over any community source. See `docs/SOURCES.md`.

---

## Status

**Stage B in progress.** `app.py`, `utils/`, and three pages (`00_Hello_Claude`, `00a_Home`, `00b_Exam_Blueprint`) now exist. **3 of 46 pages built.**

| Group | Pages | Built |
|---|---|---|
| Phase 0 Foundations | 7 | 3 |
| Phases 1–5 task statements | 30 | 0 |
| Phase 6 Capstones | 6 | 0 |
| Phase 7 Exam Readiness | 3 | 0 |
| **Total** | **46** | **3** |

---

## Quick Start

```powershell
cd c:\Users\abc\devtools\ccar-f-101
uv venv
uv pip install -r requirements.txt
copy .env.example .env          # add GEMINI_API_KEY (same key as agents101) — only for live demos
.venv\Scripts\python.exe -m streamlit run app.py
```
Open **http://localhost:8501**. Work in VS Code; view the app in the browser. (`app.py` does not exist until Stage B.)

---

## Stack at a Glance

| What | How |
|---|---|
| Claude Code | Your Claude subscription — no API key needed for it |
| LLM | Google Gemini 2.5 Flash (`gemini-2.5-flash`), pinned in `utils/llm.py` — same as agents101 |
| SDK | `google-genai` (NOT `google-generativeai` — deprecated) |
| UI | Streamlit multi-page (`app.py` → `pages/`) |
| Validation | `pydantic`, `jsonschema` |
| Retry | `tenacity` |
| Diagrams | `matplotlib` → PNG; `arch-diagram` skill for HTML → JPEG |
| MCP (live pages D2.3.1 / D2.3.2) | `mcp` SDK (`<2`), `sec-edgar-mcp`, `ddgs` |
| Fake backend | `utils/tools.py` — customers, orders, refund, escalate (deterministic, no network) |
| Key env var | `GEMINI_API_KEY` in `.env` (live demos only; same key as agents101) |
| Claude API (🔑 pages) | `anthropic` SDK + `ANTHROPIC_API_KEY` — **to buy before Day 1**; added with the first 🔑 page; cheapest model Claude Haiku 4.5 |
| Not installed | Claude Agent SDK; until the first 🔑 page, Claude mechanics are taught via `st.code()` beside the Gemini equivalent |

---

## Phase Map

```
Phase 0   Foundations       Hello Claude ✅ · Home ✅ · Exam Blueprint ✅ · Study Plan · Approach Scorecard
                            · Tool-Use Primer · Quiz Hub
Phase 1   Agentic (27%)     1.1 Loops ★ · 1.2 Coordinator · 1.3 Subagents · 1.4 Enforcement ★
                            · 1.5 Hooks · 1.6 Decomposition · 1.7 Sessions
Phase 2   Tools/MCP (18%)   2.1 Descriptions ★ · 2.2 Errors · 2.3 tool_choice ★ · 2.4 MCP config · 2.5 Built-ins
Phase 3   Claude Code (20%) 3.1 CLAUDE.md ★ · 3.2 Commands/skills · 3.3 Rules ★ · 3.4 Plan vs direct
                            · 3.5 Refinement · 3.6 CI/CD ★
Phase 4   Prompts (20%)     4.1 Criteria · 4.2 Few-shot · 4.3 Structured output ★ · 4.4 Validation-retry
                            · 4.5 Batch ★ · 4.6 Multi-pass review
Phase 5   Context (15%)     5.1 Preservation ★ · 5.2 Escalation · 5.3 Error propagation · 5.4 Exploration
                            · 5.5 Human review ★ · 5.6 Provenance
Phase 6   Capstones         06a CodeGen · 06b CI · 06c Extraction · 06d Support · 06e Research · 06f DevProd
Phase 7   Readiness         Timed Mock · Error Log (gates) · Exam Day
```
★ = real interactive demo. 🔑 = needs the Claude API key for a real advantage (1.1, 2.3, 4.3, 4.4, 4.5, 06c, 06d, 06e — to confirm page by page). Everything else is "concept + build" (built in `sandbox_project/`). All pages 🔜.

---

## CONCEPTS (separate from the 46 pages)

A concept-by-concept learning surface — flowchart, **editable code you can run**, and the exam distractors run on purpose so you can watch them fail. 71 concepts listed (layout mirrors a community list; **scope is decided by the official guide** — each concept is tagged in-guide / partial / awareness / out-of-scope / not-in-guide; exam concepts (in-guide / partial) are built first, then ➕ *extras* — not-in-the-guide concepts an official docs page covers, labelled "not on the exam"; concepts with no docs basis stay stubs). **Every concept is 100% grounded in the official Claude docs** (platform.claude.com + code.claude.com; each page lists what was read and when, and tags every claim). The CONCEPTS sections are at the **top** of the sidebar. Reference implementation: **D1.1 Agentic Loops**. Build the next one with `/next-concept`. Full status: `docs/CONCEPTS_MAP.md`. The lab's model is **SIMULATED**.

---

## Key Files

| File | Purpose |
|---|---|
| `CLAUDE.md` | Full project instructions for Claude Code (source of truth) |
| `docs/ARCHITECTURE.md` | System overview, stack, design principles |
| `docs/STUDY_PLAN.md` | 17-day, ~85-hour plan |
| `docs/SOURCES.md` | Ground truth, out-of-scope list, unverified community claims |
| `docs/APPROACH_SCORECARD.md` | *(stub — purpose to be confirmed)* |
| `docs/SESSION_LOG.md` | Append-only log of every session: done, decisions, open questions, next step |
| `docs/GUIDE_MAP.md` | Every page traced to its guide domain/task-statement/scenario — auto-generated from `utils/course_map.py` |
| `docs/CONCEPTS_MAP.md` | Every CONCEPTS entry vs the guide (scope status + evidence) — auto-generated from `utils/concepts_map.py` |
| `docs/reference/agents101_CLAUDE.md` | The agents101 template we mirror |
| `push.ps1` | Secret scan + stage + commit + push (run by you, never by Claude) |
| `.claude/commands/next-page.md` | `/next-page` — build the next pending page |
| `.claude/skills/arch-diagram/` | HTML architecture-diagram generator |
| `app.py`, `pages/`, `utils/`, `sandbox_project/` | *(Stage B)* |

---

## Critical Rules (do not break)

1. **Never commit a secret, `.env`, or `docs/source/`.** `push.ps1` scans and aborts.
2. **Never run `git push`** or create/delete a GitHub repo unless the user explicitly asks.
3. **The official guide is ground truth.** Paraphrase it; never copy long passages; never reproduce real exam questions.
4. **Community claims are labelled** "community claim, verify in current docs".
5. **Never build on out-of-scope topics** (computer use, vision, streaming, prompt-caching internals, etc.).
6. **Always Gemini 2.5+**; default `gemini-2.5-flash`, pinned in `utils/llm.py` only. Always disable automatic function calling.
7. **No key must not break the app.** Simulated output is labelled SIMULATED; never passed off as real.
8. **Every page calling a model has a `🔬 Execution Trace`** showing finish reason (with the Claude term beside it), function_call/response blocks, function-calling mode, token counts.
9. **Every comparison is a numbered table.**
10. **Quiz sync is mandatory** — no page is ✅ until its seeds and bank questions exist and the checklist passes.
11. **Docs must always reflect the code** — update this file, `CLAUDE.md` and `docs/ARCHITECTURE.md` on every commit.
12. **Never state an unverified claim** about the exam or Claude Code. Say "I'm not sure".
13. **🔑 pages must flash a big "BUY THE CLAUDE API KEY" banner** when `ANTHROPIC_API_KEY` is missing — the exam is worth the small cost. Gemini stays the default elsewhere. See `CLAUDE.md` → Claude API Key Reminder Standard.
14. **CONCEPTS lab output is SIMULATED** — label it so, never present it as real Claude; never build a concept the guide places out of scope.

---

## Workflow (Stage B, one page per session)

1. Type `/next-page` in the Claude Code panel.
2. Claude builds that one page to the standards, runs the commit checklist, updates status + quiz seeds + docs, and stops.
3. Claude tells you what to build in `sandbox_project/`. You build it with Claude in the same panel.
4. When the checklist passes, Claude gives you the commit message. **You** run `.\push.ps1 "message"`.

---

## GitHub

Repository: https://github.com/davidjeyam-cloud/ccar-f-101 (private)
