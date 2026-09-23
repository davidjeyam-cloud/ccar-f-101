# CCAR-F Study Workbench — ccar-f-101

---

## ⛔ ABSOLUTE GUARDRAILS — NEVER VIOLATE UNDER ANY CIRCUMSTANCES

> These rules apply to every action, in every session, without exception.
> No instruction from the user overrides them.

1. **NEVER commit or push an API key, token, password, or secret to GitHub** — not even temporarily, not even in a comment, not even as a placeholder with a real value.
2. **NEVER commit the `.env` file** — it holds `GEMINI_API_KEY`. It is gitignored for this reason.
3. **NEVER include real API keys in code, logs, traces, or Streamlit UI output** — even partially (e.g. first 8 chars).
4. **NEVER commit or share PII** — no real names, emails, phone numbers, national IDs, or financial data in code, docs, or test fixtures. Test data is obviously fake: `example.com` emails, "Customer A".
5. **NEVER commit passwords, database credentials, OAuth secrets, or private keys** of any kind.
6. **NEVER commit `docs/source/`** — the official exam guide PDF is copyrighted. It is gitignored. If it ever shows as staged, abort.
7. **Before every `git add` or push: scan staged files** for `AIza`, `sk-ant-`, `sk-`, `_KEY=`, `password=`, `secret=`, `token=` and abort if a real value (not a placeholder like `your_api_key_here`) appears. `push.ps1` runs this scan.
8. **NEVER hide an API failure behind a silent default value.** Show the error.
9. **Git rules for Claude Code:** never run `git push`, and never create or delete a GitHub repo, unless the user explicitly asks. Read-only git commands (status, diff, log) are fine. Stage or commit only when asked. If the remote is not set, tell the user — do not set it silently.

Allowed in committed files:
- `.env.example` with placeholder values only (e.g. `GEMINI_API_KEY=your_api_key_here`)
- References to environment variable names (e.g. `os.getenv("GEMINI_API_KEY")`)

Your own login to Claude Code (the subscription) is never a secret you handle. The app's `GEMINI_API_KEY` is separate and lives only in the local `.env`.

---

## Project
A study workbench for the **Claude Certified Architect – Foundations** exam (**CCAR-F**, guide v1.0, effective July 2026). It mirrors the structure and conventions of the earlier repo `agents101`, adapted to this exam.

**How the learning works:** each topic is built by hand in VS Code with Claude Code (learn by doing). The Streamlit app tracks progress and shows small visual demos — it is not where the learning mainly happens.

Remote: https://github.com/davidjeyam-cloud/ccar-f-101.git (private)
Push script: `.\push.ps1 "message"` — runs the secret scan, stages the tracked folders, commits, pushes. Claude Code never pushes.

### Source-of-truth rules
1. The **official exam guide** (`docs/source/*.pdf`, local only) wins over any community repo, blog or forum. If they disagree, follow the guide and note the disagreement in `docs/SOURCES.md`.
2. **Paraphrase** the guide. Never copy long passages. Never reproduce or try to recall real exam questions. Every question in this repo is original.
3. Anything from community sources is labelled **"community claim, verify in current docs"**. This includes CLI flags beyond `-p`, `--output-format json` and `--json-schema`; model-specific behaviour; and exam-policy claims not in the guide.
4. Respect the guide's **out-of-scope list**. Never build pages or questions on those topics (see below). Prompt caching is "know that it exists" only.
5. If unsure, ask the user. Never fill a gap with a plausible guess. Never state a claim about the exam or Claude Code behaviour that has not been verified against the guide or current docs — say "I'm not sure".

### Exam at a glance (from the official guide)
| # | Item | Value |
|---|---|---|
| 1 | Items | 60, multiple-choice and multiple-response (each item states how many to select) |
| 2 | Structure | 4 scenarios drawn at random from a bank of 6 |
| 3 | Time | 120 minutes |
| 4 | Passing score | scaled 720 on a 100–1,000 scale |
| 5 | Validity | 12 months |
| 6 | Report | pass/fail + scaled score + percent-correct by domain |

| Domain | Name | Weight | Task statements |
|---|---|---|---|
| 1 | Agentic Architecture & Orchestration | 27% | 1.1 – 1.7 |
| 2 | Tool Design & MCP Integration | 18% | 2.1 – 2.5 |
| 3 | Claude Code Configuration & Workflows | 20% | 3.1 – 3.6 |
| 4 | Prompt Engineering & Structured Output | 20% | 4.1 – 4.6 |
| 5 | Context Management & Reliability | 15% | 5.1 – 5.6 |

30 task statements in total (the 30-cell coverage map on `00a_Home`).

### Out of scope (never build pages or questions on these)
Fine-tuning or training models · API authentication, billing, account management · language- or framework-specific implementation detail beyond tool/schema config · deploying or hosting MCP servers · Claude internals, training, weights · Constitutional AI / RLHF / safety training · embedding models and vector databases · computer use · vision / image analysis · streaming / SSE implementation · rate limits, quotas, pricing calculations · OAuth / key rotation / auth protocols · specific cloud-provider config · benchmarking / model comparison metrics · prompt caching internals (know it exists) · token counting / tokenisation.

---

## Learning Sequence
```
Phase 0 : Foundations — setup, exam blueprint, study plan, scorecard, tool-use primer, quiz hub
Phase 1 : Agentic Architecture & Orchestration (27%) — loops, coordinator-subagent, hooks, sessions
Phase 2 : Tool Design & MCP Integration (18%) — descriptions, errors, tool_choice, .mcp.json, built-ins
Phase 3 : Claude Code Configuration & Workflows (20%) — CLAUDE.md, commands/skills, rules, plan mode, CI
Phase 4 : Prompt Engineering & Structured Output (20%) — criteria, few-shot, schemas, retry, batch
Phase 5 : Context Management & Reliability (15%) — context, escalation, error propagation, provenance
Phase 6 : Capstones — the 6 exam scenarios, built and deliberately broken
Phase 7 : Exam Readiness — timed mock, error log with readiness gates, exam-day page
```
**Why this order (deviation 7):** official guide first, then build, then quiz. Patterns before frameworks.

---

## Stack
- **UI:** Streamlit multi-page app. Python managed with `uv`. Windows + PowerShell paths.
- **LLM (app demos):** Google Gemini — **same model, SDK and key setup as agents101** (decision by the user, 2026-09-21). SDK: `google-genai` (NOT `google-generativeai`, which is deprecated). **Key:** `GEMINI_API_KEY` in `.env` (never commit) — the same key agents101 uses.
- **Claude Code** (the thing you build with in VS Code) runs on your Claude subscription — no API key involved. `sandbox_project/` exercises use real Claude Code.
- **Not installed yet:** the `anthropic` SDK (added when the first 🔑 page is built — see Claude API Key Reminder Standard) and the Claude Agent SDK (do not add without explicit user instruction). Until then, Claude-specific API mechanics are taught with `st.code()` snippets (Claude SDK shown, not run) beside the Gemini equivalent the demo actually executes — the same approach agents101 used for ADK and CrewAI.
- **Why this matters for the exam:** the exam tests *Claude* behaviour (`stop_reason`, `tool_choice` modes, `tool_result` blocks, Message Batches). A Gemini demo shows the *pattern*, not Claude's exact fields. Every ★ page therefore shows the Claude term next to the Gemini one (mapping table in Critical SDK Notes), and the quiz and question bank stay Claude-specific.
- **Cost note:** the Gemini key is the same one agents101 uses; pricing/free-tier limits are Google's — check them on your account. Use short prompts.

## Model Rules
- **ALWAYS use Gemini 2.5+** — never 1.5-flash, 2.0-flash, or any sub-2.5 model.
- **Default model: `gemini-2.5-flash`**, pinned in `utils/llm.py` as a single `MODEL` constant (same as agents101). Change it only there.
- `gemini-2.5-flash-lite` is unreliable for function calling — avoid it for tool/agent demos.
- `utils/llm.py` mirrors agents101: a `_call()` retry wrapper (tenacity, 4 attempts, exponential backoff 3–20 s) for 503 / UNAVAILABLE, and a `_client()` that raises a clear error when `GEMINI_API_KEY` is missing. The final error is shown in the UI — never swallowed.
- **No key must not break the app.** Pure-Python demos and quizzes work without a key. A demo that calls Gemini shows a clear "needs GEMINI_API_KEY" message when there is none. If a page offers a simulated fallback, label it **SIMULATED** on screen and in the trace. Never present simulated output as a real model response.

## Claude API Key Reminder Standard (🔑 pages)

**Decision (user, 2026-09-21):** this is an exam, so a small cost is never a reason to compromise. Gemini stays the default for demos (cheap, already set up), but wherever the **Claude API key gives a real advantage**, the app must loudly remind the user to buy it.

**When a page gets the 🔑 flag:** the exam mechanic it teaches can only be exercised for real against the Claude API — not on Gemini, and not in Claude Code. Examples: the `stop_reason` loop, `tool_choice` modes, structured output via `tool_use`, Message Batches with `custom_id`. If unsure whether a page qualifies, ask the user.

**Initial 🔑 list** (confirm page by page when built): 1.1 · 2.3 · 4.3 (+ 4.4 which shares its demo) · 4.5 · capstones 06c, 06d, 06e. *To confirm:* 1.3 (subagent spawning / Agent SDK — not sure whether it needs an API key).

**The banner** — `utils/styles.py::claude_key_banner(reason)`, shown at the TOP of every 🔑 page (right after the title, before the diagram):
- **Key missing** (`ANTHROPIC_API_KEY` not set): **big** text (heading size, ≥ 28 px), high-contrast red/orange block, **flashing** via a slow CSS pulse. Text: `🔑 BUY THE CLAUDE API KEY — <one-line reason this page needs it>`, plus where (Claude Console, https://platform.claude.com/) and the suggested cheapest model (Claude Haiku 4.5 — $1 in / $5 out per million tokens, checked 2026-09-21).
- **Key present:** a small green "Claude API key detected" note. No flashing.
- Flashing must respect `@media (prefers-reduced-motion: reduce)` (then a static bold banner) and stay slow (about one pulse per 1–2 s).
- The banner never blocks the page: the Gemini pattern demo still runs. Only check that the env var is set; never print or log the key.
- `pages/00a_Home.py` shows a "Claude API key status" card listing the 🔑 pages.
- **Claude Code's hand-over message** for a 🔑 page must also remind the user, in one line, to buy the key.

**Claude model + SDK for 🔑 pages:** the `anthropic` SDK is added to `requirements.txt` when the first 🔑 page is built (update `AGENTS.md` and `docs/ARCHITECTURE.md` stack tables in the same commit). Pin ONE `CLAUDE_MODEL` constant in `utils/llm.py`, next to the Gemini `MODEL`. Default: Claude Haiku 4.5 (ID `claude-haiku-4-5-20251001` per this session's environment info — **verify against current docs when writing `llm.py`**). Env var: `ANTHROPIC_API_KEY` in the local `.env` (never commit; the `sk-ant-` scan rule already covers it).

**Suggested purchase time:** before Day 1 of the study plan (page 1.1 is the first 🔑 page). Set a low credit/spend limit in the Console.

## Structure
```
app.py                    # Streamlit entry point — run this
pages/                    # One page per task statement / capstone / readiness page
utils/
  llm.py                  # Gemini wrapper (google-genai) — pinned model, retry wrapper (mirrors agents101)
  tools.py                # Fake customer-support backend: customers, orders, refund, escalate
                          #   deterministic, no network, no real data
  diagrams.py             # Diagrams (matplotlib → PNG → st.image)
  styles.py               # Design tokens, apply_theme() — called once from app.py only
  trace.py                # render_trace() — standard Execution Trace expander
  quiz.py                 # PHASE_SEEDS + LLM question generator (output labelled "unverified")
  question_bank.py        # NEW: curated, original, verified questions tagged by task statement + scenario
  progress.py             # NEW: personal progress (progress.json — gitignored)
  course_map.py           # NEW: structured mirror of the Phase Status tables below — drives app.py's
                          #   sidebar nav and (from page 2) the Home page's 30-cell coverage map. Keep
                          #   in sync with this file's Phase Status tables (docs-sync checklist item 5).
  placeholder.py          # NEW: shared "coming soon" page for every 🔜 entry in course_map.py — see
                          #   its docstring for the 3-step checklist when a placeholder becomes real
sandbox_project/          # NEW: real Claude Code exercises (CLAUDE.md, .claude/rules, commands,
                          #   skills, .mcp.json) — fake data only
docs/
  source/                 # official guide PDF — LOCAL ONLY, gitignored
  reference/              # agents101_CLAUDE.md (template we mirror)
  images/                 # exported diagrams
  ARCHITECTURE.md · APPROACH_SCORECARD.md · SOURCES.md · STUDY_PLAN.md
  GUIDE_MAP.md            # auto-generated from utils/course_map.py — every page traced to a guide
                          #   domain/task-statement/scenario. Regenerate, don't hand-edit (see that
                          #   module's render_guide_map_markdown() docstring).
  SESSION_LOG.md          # append-only record of every session — Claude adds an entry before stopping
.claude/
  skills/arch-diagram/    # HTML architecture-diagram generator (from agents101)
  commands/next-page.md   # /next-page — builds the next pending page
.streamlit/config.toml    # Light theme (same as agents101)
.env / .env.example       # key (gitignored) / template
```

## Running
```powershell
cd c:\Users\abc\devtools\ccar-f-101
uv venv                                # first time only
uv pip install -r requirements.txt     # use uv, not pip directly
copy .env.example .env                 # add GEMINI_API_KEY (only needed for live demos)
.venv\Scripts\python.exe -m streamlit run app.py
```
App runs at http://localhost:8501 in the browser; you work in VS Code.

---

## Page Structure Standard (apply to ALL pages)

Every learning page follows this order:
```
1. st.set_page_config(...)                        ← FIRST call
2. st.title(...)  +  st.caption(...)
3. st.image(diagram_Xn(), ...)                    ← diagram always first
4. with st.expander("📖 What is X — concept"):
5. with st.expander("📐 Core Code Pattern — X"):  ← minimal code + inline comments + explanation
6. st.markdown("---")
7. Interactive demo  (★ pages only; other pages are "concept + build")
8. with st.expander("🔍 What just happened"):
9. Traps table  (numbered: tempting wrong answer | why it fails | what to do instead)
10. with st.expander("🛠️ Build it in VS Code with Claude Code"):  ← prompt + done-when checklist
11. Progress ticks: ☐ Read  ☐ Demo  ☐ Built  ☐ Quiz passed
12. st.markdown("### What's next → <next page>")
```
Pages with no live demo are allowed. Mark them **concept + build** in the status table; the learning for those happens in `sandbox_project/`.

## Comparison Standard (apply to ALL comparisons)
**Every comparison is a table — no exceptions.** Numbered rows so items align side by side. Never drop a row because it applies to one side only — leave the other cell `—`.

```markdown
| # | Option A | Option B |
|---|---|---|
| 1 | Applies to A            | Equivalent or opposite for B |
| 2 | Unique to A             | —                            |
| 3 | —                       | Unique to B                  |
```

**Mandatory tables** (must exist somewhere in the app):
1. `tool_choice`: auto vs any vs forced
2. CLAUDE.md scope: user vs project vs directory
3. Message Batches API vs synchronous API
4. Plan mode vs direct execution
5. Hooks vs prompt instructions
6. Session: resume vs fork vs fresh start with summary

## Critical SDK Notes

### A. What the demos actually run — Gemini (`google-genai`)
- **Automatic function calling is ON by default** in `client.chats.create()` — always disable it, or tools run silently and you cannot see them:
  `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)`
- History format: `[{"role": "user", "parts": [{"text": "..."}]}]` — `parts` is a list of dicts, not a string. Use `convo.get_history()` after a tool cycle to capture tool call/response parts.
- Never use a silent `except Exception:` fallback that hides an API failure — raise or show the error.

### B. Claude terms the exam tests → nearest Gemini equivalent the demo shows
*(Gemini column: community claim, verify in current Google docs before relying on it. Claude column: from the official guide.)*

| # | Concept | Claude (exam) | Gemini (what the demo runs) |
|---|---|---|---|
| 1 | Loop continues | `stop_reason == "tool_use"` | response contains a `function_call` part |
| 2 | Loop ends | `stop_reason == "end_turn"` | response has text and no `function_call` part |
| 3 | Tool result returned | `tool_result` block in a **user** message, matched to the `tool_use` id | `function_response` part sent back |
| 4 | Model may answer in text | `tool_choice: "auto"` | function-calling mode `AUTO` |
| 5 | Model must call a tool | `tool_choice: "any"` | function-calling mode `ANY` |
| 6 | Model must call one named tool | `{"type": "tool", "name": "..."}` | mode `ANY` limited to a single allowed function name |
| 7 | Token counts | `usage` input / output tokens | `usage_metadata` |
| 8 | Batch processing | Message Batches API (50% saving, up to 24 h, `custom_id`) | no equivalent run in the app — `st.code()` + concept only |
| 9 | Subagent spawning | Task tool, `allowedTools` includes `"Task"` | no equivalent — `st.code()` + built for real in `sandbox_project/` |

### C. Claude API facts (exam ground truth — taught with `st.code()`, not executed)
- **Agentic loop:** read `stop_reason`. Keep looping only while it is `"tool_use"`; stop on `"end_turn"`. Do not parse assistant text to decide termination; do not use an iteration cap as the primary stop condition.
- **Tool results** go back in a **user** message as `tool_result` blocks, matched to the `tool_use` id. Append them to the history so the model can reason about the next step.
- **Three `tool_choice` modes:** `auto` (may answer in text), `any` (must call some tool), forced `{"type": "tool", "name": "..."}` (must call that tool).
- **Verify:** one community source says a newer model may reject a forced `tool_choice`. *(community claim, verify in current docs)*
- Schema-conformant tool output removes JSON *syntax* errors but not *semantic* errors (totals that don't add up, values in the wrong field).
- Batch API facts from the guide: 50% cost saving, up to 24 h window, no latency SLA, no multi-turn tool calling inside one request, correlate with `custom_id`.
- Subagents do **not** inherit the coordinator's history — pass context explicitly in the prompt.

## Execution Trace Standard (apply to ALL interactive pages)
Every page that calls a model includes a **`🔬 Execution Trace`** expander after the results. Use `utils/trace.py::render_trace()`.

It must show, in addition to agents101's requirements (exact system prompt, exact user message, raw response, parsed values, scoring/threshold decisions with real numbers):
```
- finish reason / loop state of each response, with the Claude term beside it (e.g. "function_call present -> Claude: stop_reason = tool_use")
- every function_call (name, args) and every function_response sent back
- the function-calling mode used (AUTO / ANY / single allowed function) with the Claude tool_choice term beside it
- token counts (input / output) per call, from usage_metadata
```

## Tools (utils/tools.py) — fake, deterministic, no network
| Function | What it does |
|---|---|
| `get_customer(...)` | Returns a fake customer record (or several matches, to test clarification) |
| `lookup_order(...)` | Returns a fake order (deliberately verbose, to test context trimming) |
| `process_refund(...)` | Fake refund with a policy threshold |
| `escalate_to_human(...)` | Records a structured handoff summary |

All data is obviously fake (`example.com`, "Customer A"). No real data ever.

---

## Commit Baseline — Checklist Before Every Push

### 1. Syntax
```powershell
.venv\Scripts\python.exe -m py_compile app.py pages/*.py utils/*.py
# no output = all files parse
```
### 2. App starts clean
```powershell
.venv\Scripts\python.exe -m streamlit run app.py --server.headless true
# http://localhost:8501 — Home loads with no red error banner, with AND without a key
```
### 3. New page checklist
- [ ] Added to `app.py` navigation under the correct phase group
- [ ] `st.set_page_config(...)` is the first call
- [ ] Diagram before any interactive section
- [ ] `📖` concept expander and `📐 Core Code Pattern` expander present
- [ ] `🔬 Execution Trace` present for every model call (finish reason with Claude term beside it, function_call/response blocks, function-calling mode, tokens)
- [ ] Traps table present
- [ ] `🛠️ Build it in VS Code with Claude Code` expander (prompt + done-when checklist) present
- [ ] Four progress ticks wired to `utils/progress.py`
- [ ] Works with no `GEMINI_API_KEY` (clear message; SIMULATED labelled if used)
- [ ] If the page is 🔑: `claude_key_banner(...)` at the top; works with no `ANTHROPIC_API_KEY`; hand-over message reminds the user to buy the key
- [ ] No out-of-scope topic, no copied guide text, no real exam question
- [ ] `### What's next` points to the correct next page
- [ ] Phase Status table below updated 🔜 → ✅ — **only after this whole checklist passes**

### 4. Quiz sync (MANDATORY when any page/phase is built)
- [ ] `utils/quiz.py` — `PHASE_SEEDS["<phase_key>"]` exists: `title`, `icon`, `status`, `concepts` (8–12), `snippets` (3)
- [ ] `utils/question_bank.py` — at least one original question per task statement built, tagged by task statement; scenario questions tagged 1–6
- [ ] Concepts are Claude-specific but test **judgment, trade-offs and failure modes**, never recall
- [ ] Question wording hides the qualifier the way real stems do (first step, guarantee, most maintainable, root cause)
- [ ] Generated questions are labelled **"unverified"**; only bank questions count as verified
- [ ] Verify: `python -c "from utils.quiz import PHASE_SEEDS; print(list(PHASE_SEEDS))"`

**No phase is done until the quiz seed bank includes it.**

### 5. Documentation sync (MANDATORY on EVERY commit)
`docs/` always reflects the code. Treat docs as part of the code.
- [ ] Phase Status table (this file) — status changed
- [ ] `pages/00a_Home.py` — completed count and coverage map cell
- [ ] `AGENTS.md` — page count and Phase Map row
- [ ] `docs/ARCHITECTURE.md` — Learning Phases table row
- [ ] New diagram function → export PNG to `docs/images/` and reference it
- [ ] `requirements.txt` changed → update `AGENTS.md` Stack table and `docs/ARCHITECTURE.md` stack table
- [ ] New source consulted → `docs/SOURCES.md`
- [ ] `utils/course_map.py`'s matching `PageEntry.built` flipped to `True` → regenerate `docs/GUIDE_MAP.md` (see that module's `render_guide_map_markdown()` docstring)

### 6. Commit message convention
```
feat: <page id> — <title> complete       ← new page done
fix: <short description>                 ← bug fix
chore: <tooling, deps, config>           ← non-code
docs: <what doc was updated>             ← docs only
```
### 7. Never commit
`.env` · `.venv/` · `__pycache__/` · `docs/source/` · `progress.json` · `output/` · any file with a real key, password or token.

---

## Phase Status
All pages are 🔜 (Stage A: docs and config only). 🔑 = the Claude API key gives a real advantage — page shows the flashing key reminder. ★ = page gets a real interactive demo; all other pages are **concept + build**. Task-statement titles use the guide's wording, paraphrased.

### Phase 0 — Foundations  (weight n/a)
| Page file | Module | Status |
|---|---|---|
| `00_Hello_Claude.py` | Hello Claude — three-key setup & first live call (works without ANTHROPIC_API_KEY) | ✅ |
| `00a_Home.py` | Home — dashboard, guide-grounded project intent, 30-cell coverage map | ✅ |
| `00b_Exam_Blueprint.py` | Exam Blueprint — format, timing, scoring, policies, out-of-scope (domains/weights/scenarios moved to Home's blueprint table) | ✅ |
| `00c_Study_Plan.py` | Study Plan — 17-day plan | 🔜 |
| `00d_Approach_Scorecard.py` | Approach Scorecard — *(purpose to be confirmed with user)* | 🔜 |
| `00e_ToolUse_Primer.py` | Tool-Use Primer — the request/response mechanics | 🔜 |
| `0q_Quiz_Hub.py` | Quiz Hub — curated bank + generator (unverified) | 🔜 |

### Phase 1 — Agentic Architecture & Orchestration  (27%)
| Page file | Module | Status |
|---|---|---|
| `01a_*.py` | 1.1 Agentic loops ★ 🔑 | 🔜 |
| `01b_*.py` | 1.2 Coordinator-subagent patterns | 🔜 |
| `01c_*.py` | 1.3 Subagent invocation and context | 🔜 |
| `01d_*.py` | 1.4 Enforcement and handoff ★ | 🔜 |
| `01e_*.py` | 1.5 Hooks | 🔜 |
| `01f_*.py` | 1.6 Task decomposition | 🔜 |
| `01g_*.py` | 1.7 Session state | 🔜 |

### Phase 2 — Tool Design & MCP Integration  (18%)
| Page file | Module | Status |
|---|---|---|
| `02a_*.py` | 2.1 Tool descriptions ★ | 🔜 |
| `02b_*.py` | 2.2 Structured errors | 🔜 |
| `02c_*.py` | 2.3 Tool distribution and tool_choice ★ 🔑 | 🔜 |
| `02d_*.py` | 2.4 MCP config | 🔜 |
| `02e_*.py` | 2.5 Built-in tools | 🔜 |

### Phase 3 — Claude Code Configuration & Workflows  (20%)
| Page file | Module | Status |
|---|---|---|
| `03a_*.py` | 3.1 CLAUDE.md hierarchy ★ | 🔜 |
| `03b_*.py` | 3.2 Commands and skills | 🔜 |
| `03c_*.py` | 3.3 Path-specific rules ★ | 🔜 |
| `03d_*.py` | 3.4 Plan vs direct | 🔜 |
| `03e_*.py` | 3.5 Iterative refinement | 🔜 |
| `03f_*.py` | 3.6 CI/CD ★ | 🔜 |

### Phase 4 — Prompt Engineering & Structured Output  (20%)
| Page file | Module | Status |
|---|---|---|
| `04a_*.py` | 4.1 Explicit criteria | 🔜 |
| `04b_*.py` | 4.2 Few-shot | 🔜 |
| `04c_*.py` | 4.3 Structured output ★ 🔑 | 🔜 |
| `04d_*.py` | 4.4 Validation-retry (shares the 04c demo) 🔑 | 🔜 |
| `04e_*.py` | 4.5 Batch ★ 🔑 | 🔜 |
| `04f_*.py` | 4.6 Multi-pass review | 🔜 |

### Phase 5 — Context Management & Reliability  (15%)
| Page file | Module | Status |
|---|---|---|
| `05a_*.py` | 5.1 Context preservation ★ | 🔜 |
| `05b_*.py` | 5.2 Escalation | 🔜 |
| `05c_*.py` | 5.3 Error propagation | 🔜 |
| `05d_*.py` | 5.4 Codebase exploration | 🔜 |
| `05e_*.py` | 5.5 Human review and calibration ★ | 🔜 |
| `05f_*.py` | 5.6 Provenance | 🔜 |

### Phase 6 — Capstones  (the 6 exam scenarios)
| Page file | Module | Status |
|---|---|---|
| `06a_*.py` | CodeGen — Code Generation with Claude Code (guide scenario 2) | 🔜 |
| `06b_*.py` | CI — Claude Code for Continuous Integration (guide scenario 5) | 🔜 |
| `06c_*.py` | Extraction — Structured Data Extraction (guide scenario 6) 🔑 | 🔜 |
| `06d_*.py` | Support — Customer Support Resolution Agent (guide scenario 1) 🔑 | 🔜 |
| `06e_*.py` | Research — Multi-Agent Research System (guide scenario 3) 🔑 | 🔜 |
| `06f_*.py` | DevProd — Developer Productivity with Claude (guide scenario 4) | 🔜 |

### Phase 7 — Exam Readiness  (weight n/a)
| Page file | Module | Status |
|---|---|---|
| `07a_Timed_Mock.py` | Timed Mock — 4 random scenarios | 🔜 |
| `07b_Error_Log.py` | Error Log + readiness gates | 🔜 |
| `07c_Exam_Day.py` | Exam Day — logistics, rules of conduct | 🔜 |

---

## Capstone Protocol
The exam draws 4 of 6 scenarios at random, so all six are built. Each is a training tool of about 1.5–3 hours; the point is to have made **and broken** the decisions the exam tests.

**Scenario numbers below follow the official guide** (1 Support, 2 CodeGen, 3 Research, 4 DevProd, 5 CI, 6 Extraction). Tag bank questions with these numbers.

| Page | Guide scenario | Primary domains (guide) | Unlock after | Time |
|---|---|---|---|---|
| 06a | 2 Code Generation with Claude Code | D3, D5 | Phase 3 | ~1.5h |
| 06b | 5 Claude Code for CI | D3, D4 | Phase 4 | ~2.5h |
| 06c | 6 Structured Data Extraction | D4, D5 | Phase 5 | ~2h |
| 06d | 1 Customer Support Resolution Agent | D1, D2, D5 | Phase 5 | ~3h |
| 06e | 3 Multi-Agent Research System | D1, D2, D5 | after 06d | ~3h |
| 06f | 4 Developer Productivity with Claude | D2, D3, D1 | last | ~2h |

Same protocol for every capstone:
1. Read the brief; write the acceptance checklist from the task-statement checklists **first**.
2. Use plan mode, then build in `sandbox_project/` or a scratch folder.
3. Run **three break tests** — deliberately trigger the failure the exam tempts you to misdiagnose.
4. Write a decision-notes table: symptom · root cause · right first fix · two tempting wrong fixes.
5. Take 8–10 scenario-tagged questions. Log each miss with a reason.

**Done only when:** checklist passes · all three break tests ran · notes written · quiz ≥ 80%.
06a, 06b and 06f cannot be auto-graded — self-verify in VS Code and tick manually. If time is short, shrink 06e and 06f first (design + break tests only). **Never cut the break tests of 06a and 06b.**

## Study Plan and Gates
About 85 hours over 17 days. Full table in `docs/STUDY_PLAN.md`. Every day starts with a 15-minute review of yesterday's error-log items. Building a page IS the study step for that topic. Keep app-building to about 20% of total hours. If the baseline shows a domain at ≥ 80%, skip that domain's "concept + build" pages and keep only its quiz and capstone.

**Readiness gates** (shown on `07b_Error_Log`):
1. Every domain ≥ 80% (at least 5 questions answered per domain)
2. All six capstones done
3. Official practice exam ≥ 900 — treated as a **floor**, because candidate reports say real scores land 40–190 points lower *(community claim, verify in current docs)*
4. No repeated "misread the qualifier" errors in the last two mocks

Every wrong answer offers a "log this mistake" reason: misread · two looked right · didn't know · second-guessed · rushed.
The timed mock draws 4 random scenarios and pulls tagged questions. Target 60 items at 2 minutes each once the bank is big enough — until then the page says so honestly.

## Deviations from agents101
| # | agents101 rule | Change for CCAR-F |
|---|---|---|
| 1 | Quiz concepts must be LLM-agnostic | Reversed. Concepts are Claude-specific (`stop_reason`, `.mcp.json`, CLAUDE.md scoping, `-p`) but test judgment, trade-offs and failure modes, never recall. Never touch out-of-scope topics. |
| 2 | Quiz questions come from the LLM | Added a curated bank of original questions in `utils/question_bank.py`, tagged by task statement and scenario. Generator kept; its questions are labelled "unverified". |
| 3 | Page standard has no build step | After the demo add "🛠️ Build it in VS Code with Claude Code" (prompt, done-when checklist) and four progress ticks: Read, Demo, Built, Quiz passed. |
| 4 | Diagram → concept → Core Code Pattern → demo → "What just happened" → "What's next" | Kept exactly, plus a traps table. |
| 5 | Comparisons are numbered tables | Kept. Mandatory tables listed above. |
| 6 | Execution Trace standard | Kept, plus finish reason (with the Claude term beside it), function_call/response blocks, function-calling mode and token counts. |
| 8 | Gemini everywhere (LLM, SDK, key) | **Kept from agents101 by the user's decision (2026-09-21)**, reversing the build prompt's `anthropic` SDK / `ANTHROPIC_API_KEY`. Claude-specific mechanics are taught via `st.code()` and real Claude Code in `sandbox_project/`; quiz and bank stay Claude-specific. **Exception:** 🔑 pages use the real Claude API and remind the user to buy the key (see Claude API Key Reminder Standard). |
| 7 | Patterns first, frameworks last | Official guide first, then build, then quiz. |

## Deferred Work
*(empty)*
