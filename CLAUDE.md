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
5. **Official Claude docs = technical truth (user rule, 2026-09-26).** "The official docs" means BOTH `platform.claude.com/docs` (Messages API, tool use, stop reasons, refusals, batch, structured outputs, prompt engineering, guardrails, models, Managed Agents) AND `code.claude.com/docs` (Claude Code and the Agent SDK — the platform docs redirect `/agent-sdk/*` there). Hierarchy: **the guide decides SCOPE (what is examinable); the official docs decide TECHNICAL FACTS (how it actually behaves); community sources are unverified.** Where the guide and the docs differ in detail, show both, follow the docs on technical facts, follow the guide on what the exam expects, and note it in `docs/SOURCES.md`. Example: the guide names two `stop_reason` values for the loop (`tool_use`, `end_turn`); the docs list seven.
6. If unsure, ask the user. Never fill a gap with a plausible guess. Never state a claim about the exam or Claude Code behaviour that has not been verified against the guide or current docs — say "I'm not sure".

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
- **Hosting:** the PC is the main copy (`.env` for keys). A private copy runs on Streamlit Community Cloud (https://ccar-f.streamlit.app/, redeployed on every push to `master`); its keys live in the app's Settings → Secrets and reach the code through `utils/secrets_env.py`. Its storage is temporary, so progress ticks reset there.
- **MCP (live pages D2.3.1 / D2.3.2):** `mcp` Python SDK (pinned `<2`), `sec-edgar-mcp`, `ddgs`.
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

## CONCEPTS section (added 2026-09-26 at the user's request)

A second learning surface next to the phases: learn **one concept at a time** by reading it, watching a flowchart, and **editing and running code** against a simulated Claude — including the exam distractors, run on purpose so you can watch them fail. It has its own sidebar sections ("CONCEPTS", "CONCEPTS · D1 …") shown at the **TOP of the sidebar** (moved there 2026-09-26; `pages/00_Hello_Claude.py` stays the landing page via `default=True`) and **does not change the 46-page phase structure, `utils/course_map.py`, Home's counts, or any existing page.**

- **Taxonomy:** 71 concepts mirroring the layout of a community concept list (claudearchitectcertification.com/concepts — third-party, unverified, structure only, no content copied). 30 are numbered D1.1 – D5.2 (sidebar, under their domain); 41 are unnumbered "cross-cutting" (registered but hidden from the sidebar; reachable from the index page's cards).
- **The official guide decides scope, not that list.** Every concept has a status — Claude's judgment from a keyword search and reading of guide v1.0 on 2026-09-26, so verify it in `docs/CONCEPTS_MAP.md`: 🎯 in the guide · ◐ partly in the guide · ℹ️ awareness only · ⛔ explicitly out of scope · ⚪ not in the guide. **Exam concepts = 🎯 and ◐**, built first. ⛔ / ℹ️ get an honest stub — never a page or question on an out-of-scope topic. (At creation: 22 in the guide, 15 partial, 1 awareness, 3 out of scope, 30 not in the guide.)
- **EXTRAS (user decision, 2026-09-26: "yes" to building the not-in-the-guide concepts).** A ⚪ concept can be built as an **➕ extra** — labelled "not on the CCAR-F exam" on screen — **only if an official docs page covers it** (`concepts_map.EXTRA_DOCS` lists candidate pages, fetched and read at build time). Those with no docs basis are **ungroundable**: they stay stubs that say so, because of the grounding rule below. Kinds (`concepts_map.kind()`): exam 37 · extra 9 · ungroundable 21 · excluded 4. Extras are built after the exam concepts; out-of-scope (⛔) topics stay unbuilt unless the user explicitly overrides. Extras' practice items are shown on the page but never enter the exam question bank (`in_bank=False`).
- **GROUNDING RULE — every concept is 100% grounded in the official Claude docs (user rule, 2026-09-26).** Before writing a concept: **fetch and read** the relevant official docs pages (WebFetch), plus the guide's task statements for exam concepts. The content module must carry `docs_refs` (pages read) + `docs_verified_on` (date) + `grounding` (each substantive claim tagged 📘 docs / 🎓 guide / 💡 my recommendation / 🧪 simulated, with where it comes from); the page shows all of it. No claim from memory; if a claim cannot be grounded, label it or omit it; **if a concept cannot be grounded at all, do not build it.** Distractors come from the guide's anti-pattern lists AND the docs' own pitfall lists, each with its Source. Reason for the rule: the first Agentic Loops page taught only the guide's two stop reasons and treated every other stop as an error — the docs list seven and require each to be handled.
- **MENTAL MODEL RULE (user rule, 2026-09-26): every concept AND every sub-concept gets a mental model.** A *mental model* is one or two plain sentences that give the learner a picture to hold — an analogy plus the one trap it protects against — shown in a 🧭 box. Example (D1.1): "`stop_reason` is the steering wheel — text is just what the model said out loud. And 'the loop ended' is not the same as 'the task succeeded'." **Concept** = a CONCEPTS page: its `mental_model` field is required (shown under the Summary). **Sub-concept** = each distinct mechanism, term or branch the page teaches on its own (e.g. each `stop_reason` value and each docs-derived distractor on D1.1; each hook type, each `tool_choice` mode, each CLAUDE.md scope elsewhere): it gets its own one-line 🧭 mental model beside its explanation — in the sub-concept table or the distractor row, not buried in prose. Rules: it must be *true* (grounded like everything else — an analogy may simplify, never contradict the docs/guide); short enough to remember; plain words, no jargon it doesn't explain; and it names the failure it prevents. A concept or sub-concept without one is not finished. The same rule applies to the 46 phase pages: their `📖` concept expander opens with a 🧭 mental model line.
- **EXAM HIGHLIGHT RULE (user rule, 2026-09-26): always mark what the exam demands, pinned to the exact place in the guide PDF.** Everything the guide requires is shown with a **⭐ and gold colour**; everything else (docs pitfalls, extras, my recommendations) is visibly not gold, so the learner always knows "this is an EXAM topic". Reference format (`utils/guide_index.py`): `Guide §6 · TS 1.1 · Knowledge 2 · p.5` — §6 = "Detailed Objectives by Domain", TS = task statement, Knowledge/Skill N = the Nth bullet under "Knowledge of:" / "Skills in:" (the guide does not number its bullets; this workbench counts them in order and says so on the page), p. = the PDF page. Scenarios: `Guide §5 · Scenario N · p.3–4`; out-of-scope list: `§17 Appendix · p.36`. On every **exam** concept page: (1) a gold **⭐ EXAM TOPIC** chip with the TS and page; (2) a gold **"What the exam demands"** box — one `ExamPoint` per guide bullet, paraphrased (never copied), with its exact reference and where the page exercises it; (3) ⭐ on exam-named items in the stop-reason-style tables, the flowchart (plus a key row) and the lab's variant labels; (4) every distractor carries `source="guide:<ts>:<K|S><n>"` so its Source cell reads `⭐ EXAM — TS 1.1 · Skill 3 · p.5` (docs-only pitfalls read `📘 official docs (beyond the guide)`); (5) sidebar/index/stub markers ⭐ for exam concepts. `guide_index.point_ref()` raises if a cited bullet doesn't exist, so a wrong reference fails loudly. Positions were read from the PDF on 2026-09-26 and cross-checked twice; re-derive them if the guide is reissued. The same rule applies to the 46 phase pages: their `📖` expander and traps table cite the guide reference the same way.
- **AGENT PLAYGROUND RULE (user request, 2026-09-26): every concept whose sub-concepts are behaviours or limits gets a message box per sub-concept.** Next to the code lab, the page has an **Agent playground** (`utils/playground_ui.py`, engine `utils/agent_playground.py`): one tab per sub-concept (for D1.1: `tool_use → end_turn`, `max_tokens`, `refusal`, `pause_turn`, `stop_sequence`, context window, `max_turns`, `max_budget_usd`), each with its **own message box**, its **own knobs for the developer-side constraints** that sub-concept is about (hard-coded stubs the learner can change: `max_tokens`, `max_turns`, a spending limit, refusal / pause / max_tokens handling policy, stop sequence, simulated context window), and a transcript of exactly how the agent handled the message (each call's `stop_reason`, the action taken, tokens, simulated cost, the final result subtype). Defined by a `PlayTab` per sub-concept in the concept's `playground` tuple: `mental_model` (MENTAL MODEL RULE), `exam_source` (`guide:<ts>:<K|S><n>` for ⭐ tabs, empty for docs-only), docs-grounded `meaning` + a `docs` page/section, `knobs`, `defaults`, example messages, experiments. Rules: the agent loop is trusted workbench code in the Streamlit process (learner *code* still runs in the subprocess lab); the model is SIMULATED and labelled so; result labels are the Agent SDK's documented subtypes (`error_max_turns`, `error_max_budget_usd`, `error_during_execution`, `success`) or prefixed `playground:` so they are never mistaken for SDK subtypes; **dollar figures are illustrative rates, not real pricing** (pricing maths is out of scope); every playground behaviour must be run (all tabs, default and changed knobs) and its "try this" text seen happening before it is written; anything the docs don't specify (e.g. when a budget is checked) is stated as a simulation choice. Extend `mock_claude.py` additively for new conditions.
- **FLOWCHART RULE (user feedback, 2026-09-27): every concept flowchart and decision tree is TOP-DOWN** (`rankdir=TB`) — left-to-right charts were not legible. Branches that belong together sit in one row (`rank=same`), bug/distractor nodes sit together in one row at the bottom (never an invisible left-to-right chain), the colour key sits at the bottom. **Readable size (user, 2026-09-28, approved on D1.2):** node font **18pt**, edge labels **16pt**, key text **16pt** (title 18pt), node margin 0.2,0.1. Streamlit scales a chart to the column width, so keep charts **tall and narrow** — at most **2 nodes per row** (bug rows included: stack them 2 per row with invisible edges); scrolling down is fine, shrinking text is not. Applied through `utils/flow_style.py::readable()`. Every chart keeps its concept colour key and ⭐ for exam-named nodes.
- **Page template** (`utils/concept_page.py` + `utils/concepts_content/<slug>.py`): Summary + mental model · What it is · How it works (flowchart) · Where you'll see it · **Code lab** · **Agent playground** · Looks right, isn't · Side-by-side · Decision tree · Practice · FAQ · Related.
- **Code lab:** the learner edits Python and presses Run. It executes in a **separate Python process** (`utils/lab_runner.py`: 10 s timeout, throw-away working directory, **no API keys in its environment**, secret values redacted from output) against a **SIMULATED** Claude-shaped client (`utils/mock_claude.py`) and a fake backend (`utils/tools.py`). It is **not a security sandbox** — it runs on the user's machine with their permissions. The flowchart then lights up along the path the run took (green = correct, red = where it went wrong).
- **Distractors are observed, not asserted.** Every distractor is a runnable variant, and its failure was seen (all variants × all scenarios through the real runner) before its explanation was written. Distractors come from the guide's own anti-pattern lists; anything else is labelled "my recommendation".
- **SIMULATED rule:** the lab's model is scripted; it must be labelled SIMULATED on screen and in traces and never presented as real Claude. Real-API twins are the 🔑 phase pages.
- **Adding a concept:** `/next-concept` (`.claude/commands/next-concept.md`) — one concept per session, template `utils/concepts_content/agentic_loops.py`. A concept is *built* when its content module exists (no flag to flip); then regenerate `docs/CONCEPTS_MAP.md`.
- **Questions:** each built concept's exam-basis practice items are registered in `utils/question_bank.py` under its primary task statement, flagged `reviewed_by_user: False` until the owner signs them off.
- **QUESTION RULE (user request, 2026-09-28): every practice question is grounded in a guide scenario and pinned to what the exam tests.**
  - **Framing.** Each `Question` names its guide scenario(s) in `scenarios=` (1 Support … 6 Extraction). The first one is shown as a 📋 banner above the stem. The stem sets a concrete production situation inside that scenario.
  - **Pinning.** Every bank item carries `points=("<ts>:<K|S><n>", …)`, the exact guide bullet(s) it tests. `Question.__post_init__` validates them through `guide_index.point_ref`, so a wrong pin, or a bank item missing a pin or scenario, fails at import. The page shows "⭐ What this tests: TS x · Skill n · p.N" after answering.
  - **Style.** Judgment, not recall; the qualifier is hidden the way real stems do it (most effective, first, root cause). Four plausible options of similar length, with distractors from the guide's anti-patterns and the docs' pitfalls. The correct position varies (keep A/B/C/D roughly even). The explanation says why the tempting option fails.
  - **Docs-basis items** (`basis="docs", in_bank=False`) are scenario-framed too, and never "Per the docs, what…" recall.
  - **Exam-style bar (user, 2026-09-27: "the quality of questions are good" after D1.6 was redone to it).** Write like the guide's own §9 Sample Questions (12 items, PDF pp.27–33 — the official benchmark):
    - **Stem:** 3–5 sentences — a production symptom with numbers (%, counts, minutes, tokens) and, where it fits, a log detail that reveals the cause.
    - **Qualifier:** hidden (most effective · most likely root cause · first step · how should you evaluate · best enables).
    - **Wrong options:** each is a real engineering move that fails for a nameable reason — prompt instead of code, over-engineered (classifier, routing layer), solves a different problem, blames a downstream component that is working, over-provisions tools, bigger context window / model, self-reported confidence, misreads a parameter, or a feature that doesn't exist.
    - **Explanation:** says why each wrong option fails.
    - **Length tell:** the correct option must NOT be the longest (check with a script).
  - **Question-style sources (read 2026-09-27; also in `docs/SOURCES.md`, community rows 2–3):**

    | # | Source | Status | Used for |
    |---|---|---|---|
    | 1 | Official exam guide §9 Sample Questions (local PDF, pp.27–33) | official | the style benchmark |
    | 2 | github.com/OlivierAlter/Claude-Certified-Architect-Foundations-Certification-Exam | community, unverified | style only — nothing copied |
    | 3 | github.com/hamzafarooq/claude-certified-architect | community, unverified | style only — nothing copied |
    | 4 | claudecertifiedarchitects.com/cca-practice-questions | community, unverified | style only — nothing copied |
    | 5 | certsafari.com/anthropic/claude-certified-architect-foundations | community, unverified | style only — nothing copied |
  - **Coverage.** `docs/QUESTION_MAP.md`, generated by `question_bank.render_question_map_markdown()`, lists every guide bullet with its questions and flags gaps. On 2026-09-28 all 206 bullets of the task statements the built concepts cover were covered (138 bank items). Gaps remain only in TS 3.6, 5.3, 5.5 and 5.6, which have no built concept yet; add their questions when those concepts are built.
- **Built so far:** D1.1 Agentic Loops · D1.2 Subagents (guide TS 1.2 + 1.3 — 16 exam points, 8 distractors, 10 playground tabs incl. a session-fork demo) · D1.3 Stop Reason (TS 1.1 K1/S1/S3; a `decide()` handler lab over 10 single-call scenarios — 7 stop reasons + empty end_turn + API error; 8 distractors; a stop-reason inspector playground) · D1.4 Session State & Persistence (TS 1.7 + 5.4 — 17 exam points; a simulated session layer with named sessions, resume/continue/fork, a changing fake codebase, context degradation, scratchpad, manifest; 6 distractors × 5 scenarios; 5 playground tabs) · D1.5 Human-in-the-Loop Escalation (TS 5.2 + 1.4 — 15 exam points; a keyword-driven simulated support agent with scripted customers; code gate vs prompt; structured handoff; 7 distractors × 7 scenarios; 7 playground tabs) · D1.6 Subagent State Handoff (TS 1.3 / 5.4 / 1.4 — what goes in the prompt between agents; 6 distractors × 4 scenarios) · D1.7 Agent Instruction Files (TS 3.1 + docs-only AGENTS.md — a simulated CLAUDE.md loader with /memory views; 6 distractors × 4 scenarios) · D1.8 Task Decomposition (TS 1.6 — prompt chaining vs dynamic decomposition; 5 distractors × 3 scenarios) · D2.1 Tool Calling (TS 2.1 + 1.1 — a word-overlap simulated tool router; 5 distractors × 4 scenarios) · D2.2 Tool Choice (TS 2.3 + 4.3 — tool_choice auto/any/forced/none, strict schemas, nullable/other/unclear, scoped tools per agent, models that reject forcing; 8 distractors × 6 scenarios) · D2.3 MCP (TS 2.4 + 2.2 — .mcp.json vs ~/.claude.json with a simulated teammate, ${VAR}, community vs custom, descriptions vs Grep, resources; isError + errorCategory/isRetryable, empty vs access failure, local recovery; 12 distractors × 8 scenarios) · D2.4 SDK Hooks (TS 1.5 — a simulated Agent SDK hook runner implementing the docs' matcher rules, deny precedence, updatedToolOutput, async and PostToolUse-can't-undo; 7 distractors × 3 scenarios; 6 playground tabs) · D2.5 Tool Evaluation (partial: guide §7 p.24 + TS 2.1 — an eval harness around the D2.1 router that decides ship/block and is judged against unseen production traffic; 5 distractors × 3 scenarios) · D2.6 Built-in Tools vs Skills vs MCP (TS 2.5 + 3.2 S5 + 2.4 S3 — Grep/Glob/Read/Edit/Write on a simulated repo; 6 distractors × 5 scenarios; a “which surface?” tab from the docs' feature comparison) · D3.1 CLAUDE.md Hierarchy (TS 3.1 + 3.3 — path-scoped rules with docs-correct glob semantics; 5 distractors × 3 scenarios) · D3.2 Plan Mode (TS 3.4 — plan vs direct, Explore, plan → execute; 5 distractors × 4 scenarios) · D3.3 Skills (TS 3.2 — commands/skills scopes, context: fork, allowed-tools vs disallowed-tools, argument-hint; 6 distractors × 6 scenarios) · D3.4 Checkpoints (partial: TS 1.7 + 5.4 S5 — /rewind options, Bash changes not tracked, summarize vs /clear, branch, resume then rewind; 5 distractors × 5 scenarios) · D4.1 System Prompts (TS 4.1 — explicit criteria vs “be conservative”, severity examples, disabling a noisy category; 4 distractors × 4 scenarios) · D4.3 Batch API (TS 4.5 — batch vs sync by latency, custom_id matching, resubmit only failures, SLA windows, no mid-request tool loop, sample first; 7 distractors × 7 scenarios; mandatory Batches-vs-sync table) · D4.4 Structured Outputs (TS 4.3 + 4.4 — schema-valid ≠ correct, nullable fields, conflict fields, normalisation rules, detected_pattern; 6 distractors × 5 scenarios) · D4.7 Attention Engineering (TS 5.1 + docs long-context tips — lost in the middle, query at the end, summary drift, trimming tool output; 4 distractors × 4 scenarios) · D4.9 Prompt Engineering Techniques (TS 4.2 + 3.5 — few-shot count/variety/format, test-driven iteration, fix interacting issues together; 6 distractors × 5 scenarios) · D4.10 Multi-Pass Review (TS 4.6 — independent reviewer vs self-review/extended thinking, per-file + integration passes, confidence routing; 5 distractors × 5 scenarios). D4.2 Prompt Caching is an **ℹ️ awareness page** (user request, 2026-09-28): `AWARENESS = AwarenessContent(...)` instead of `CONTENT`, rendered by `concept_page._render_awareness`. It covers what caching is, what it does NOT fix (wrong answers that reach for it), caching vs batch, and 3 practice items kept out of the bank. It has no lab, no playground and no implementation detail; the guide's out-of-scope bullet is §17 Appendix · Out-of-Scope Topics · p.39. D4.5 Vision and D4.6 Streaming (out of scope) and D4.8 4D Framework (ungroundable) are deliberately not built. · D5.1 Context Window Management (TS 5.1 + 5.4 — stateless API/full history, exploration in a subagent vs 400 “prompt is too long”, /compact vs /clear with persistent rules in CLAUDE.md, structured upstream output for a limited downstream budget; 5 distractors × 4 scenarios) · D5.2 Case Facts Block (TS 5.1 K1/S1/S2 + docs state management — block outside the summarised history in every prompt, JSON not prose, per issue, kept current, customer-stated expectations; 5 distractors × 4 scenarios). The concept list has NO concept for TS 5.3 (error propagation) or TS 5.6 (provenance); TS 5.5 and TS 3.6 exist only as unnumbered cross-cutting concepts. Multi-agent labs use the ROLE-dispatching simulated model; the playground `PlayTab.engine` is `support` | `research` | `stop` | `session` | `escalation` | `handoff` | `memory` | `decomp` | `toolsel` | `toolchoice` | `mcp` | `hooks` | `evaltools` | `builtin` | `rules` | `plan` | `skills` | `checkpoint` | `review` | `batch` | `extract` | `attention` | `fewshot` | `mpreview` | `ctxwin` | `casefacts` | `fork`. Knob names must not be `send`, `clear`, `msg` or `history` (they collide with the tab's own widget keys — asserted).
- **D2.3.1 and D2.3.2 — the two LIVE MCP pages (user requests, 2026-10-03/04; ➕ extras, not on the exam).** Hand-written pages listed in the sidebar straight after D2.3 but NOT `concepts_map` entries, so the 71-concept counts are unchanged. Both are thin files over one renderer, `utils/mcp_page.py`; the engine is `utils/mcp_live.py`. **D2.3.1 `pages/c231_mcp_hosted.py` — MCP client → a server hosted separately:** the community `sec-edgar-mcp` server (AGPL-3.0; its README says it is not affiliated with or endorsed by the SEC, and the SEC pages read mention data APIs and files, not an MCP server — the page says exactly that, nothing stronger) runs as its own service over **Streamable HTTP** at `http://127.0.0.1:9870/mcp`, bound to loopback only; the client connects by URL and never starts it (a Start/Stop box on the page plays the provider). **D2.3.2 `pages/c232_mcp_local.py` — my own MCP server, local:** `mcp_servers/laptop_server.py` over **stdio**, started by the client as a child process. Each page connects to ONE server and opens with tabs — **🗺️ Where each part runs** (a matplotlib schematic with explicit boundaries: this machine · `localhost` (loopback) · somewhere else across the internet · the SEC's servers; its zone title names the machine honestly — "your laptop" only when the app is on Windows — plus a table giving each part's machine and address or evidence), **🔀 Sequence**, and **⚖️ Hosted vs local** (the same numbered comparison table). The hosted page adds **🌐 What sec.gov exposes** (endpoint and rules tables) and **🧮 From a question to an SEC request** (the four hops from a sentence to a request, then per-tool pseudo code beside the requests actually observed, and a "run it yourself" button that calls the tool with chosen arguments and lists the requests the server really made). User request, 2026-10-04: "don't guess and make it factual and grounded" — every fact in `utils/mcp_edgar_facts.py` is tagged 📘 SEC page / 📦 package source / 👁 observed (with the date and package versions), and anything not checked is said to be unchecked; re-observe it before changing a row. The matplotlib schematic replaced Graphviz because no `dot` binary is installed here, so Graphviz layouts could not be looked at. Then the comparison table — the user asked for the two setups on separate pages with the difference shown (2026-10-04). Then, kept simple at the user's request ("too much info"): a question box, the answer, "What happened, step by step" as ONE table in time order (model calls, MCP requests with their transport, tool calls, and the web requests each server made, read from the server's own log), and "What each tool returned" as readable tables, never JSON; tokens, the run's own sequence diagram and raw JSON sit in one collapsed Details expander; pressing Ask wipes the previous result and nothing is remembered between questions. Do not add concept expanders, exam tables or traps back. **Every MCP server feature is shown on both pages (user request, 2026-10-04: "we should learn all features").** A "What this server offers" section tabulates what the server lists: Tools (with read-only / outside-world annotations), Resources and resource templates (with a Read button), Prompts, and an "All MCP features" table with the docs' control model — **tools: the model decides; resources: the application decides; prompts: the user decides**. The question form can attach resources (`resources/read`, added to the model's context) and use a server prompt (`prompts/get`, blanks filled as `name=value; …`). The local server (`laptop_server.py`: 9 tools, 3 resources + 1 template, 3 prompts) also sends progress and log notifications and uses **elicitation**: its one write tool, `save_note`, asks the user before writing — the page's Decline / Approve choice is the pre-set answer, because a web form cannot pause mid-call (say so). The hosted server is `mcp_servers/edgar_hosted_server.py`: the community package's 21 tools registered unchanged, plus resources and prompts added by this workbench (`edgar://tickers` is 40 real rows from sec.gov; the folder catalogue and clean-up policy on the local server are MOCK and labelled so). `mcp_servers/data/my_notes.txt` is personal and gitignored. **Two agents:** a *research agent* chooses and calls the MCP tools; a *synthesis agent* (`mcp_live.synthesise` — own prompt, no tools, input = the question + the tool results only) writes the curated answer and **chooses the chart type** (bar / grouped bar / line / stacked bar, with a reason) as schema-constrained JSON; `utils/mcp_charts.py` draws it and every plotted value is looked up in the tool result it cites (hatched if not found; charts with fewer than two numbers are dropped). Gemini's thinking is off on these pages (`thinking_budget=0`) because it produced empty replies. **Server rules (`laptop_server.py`):** descriptions say what a tool returns, its input, and when to use a different tool; failures are raised so the SDK sets `isError: true`, with `errorCategory` / `isRetryable` / `message`; an empty search is a valid result; it never returns the computer name, user name, serial numbers, network addresses or file contents, because every tool result is sent to the model. **Rules:** the packages (`mcp<2`, `sec-edgar-mcp`, `ddgs`) are in `requirements.txt` — user decision, 2026-10-04: both pages must also run on the hosted copy (Streamlit Cloud), reversing the earlier "optional packages" rule; on a hosted copy the keys come from Streamlit's Secrets via `utils/secrets_env.py` (copied into environment variables at app start; `.env` on the PC is unchanged), and the local page warns that "this computer" is then the hosted Linux machine, not the user's laptop (`laptop_server.py` has Linux code paths for that); `SEC_EDGAR_USER_AGENT` lives only in `.env`; no credential-looking env var is passed to a server; nothing from these pages enters the question bank; "deploying or hosting MCP servers" stays out of exam scope.
- **D2.3.3 Financial-data vendors (user request, 2026-10-04; ➕ extra, not on the exam).** `pages/c233_data_vendors.py` over `utils/vendor_facts.py`: a reference table for an investment-banking agent — per vendor, the MCP server and API it publishes, what it sells (high level) and how a client gets access. Vendors: Crunchbase, ZoomInfo, FactSet, FactSet SharkRepellent, Moody's, S&P Global Market Intelligence (Kensho), S&P Global Ratings, Fitch, Bloomberg, LSEG, with SEC EDGAR for comparison; the user's "DealInfo" and "Contexa" could not be identified and are shown as such — never guess a vendor. Rules: facts only from the vendors' own pages, each row labelled ✅ read / 🔎 search snippet of the page / 📰 republished press release / ❓ unknown; say "not stated" for anything a page did not say and list what could not be checked; no prices (none published) and no e-mail addresses are copied; the page makes no network call and needs no key, so it works on the hosted copy. Vendor pages change: re-read before building on a row.
- **Reference implementation:** D1.1 Agentic Loops (re-grounded 2026-09-26: the canonical loop handles all seven stop reasons; 9 distractors — 5 from the guide, 4 from the docs). Current counts: `docs/CONCEPTS_MAP.md`.

## Structure
```
app.py                    # Streamlit entry point — run this
pages/                    # One page per task statement / capstone / readiness page
                          #   concepts_index.py = the CONCEPTS index (domain tabs + card grid)
                          #   c231_mcp_hosted.py · c232_mcp_local.py = D2.3.1 / D2.3.2, the two LIVE MCP pages (➕ extras)
                          #   c233_data_vendors.py = D2.3.3, financial-data vendors' MCP/API reference table (➕ extra, static)
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
  secrets_env.py          # NEW: copies GEMINI_API_KEY / ANTHROPIC_API_KEY / SEC_EDGAR_USER_AGENT from Streamlit's Secrets
                          #   into environment variables (hosted copy); called once from app.py
  course_map.py           # NEW: structured mirror of the Phase Status tables below — drives app.py's
                          #   sidebar nav and (from page 2) the Home page's 30-cell coverage map. Keep
                          #   in sync with this file's Phase Status tables (docs-sync checklist item 5).
  placeholder.py          # NEW: shared "coming soon" page for every 🔜 entry in course_map.py — see
                          #   its docstring for the 3-step checklist when a placeholder becomes real
  concepts_map.py         # NEW (CONCEPTS): the 71-concept taxonomy + each concept's scope status vs the guide
  concept_page.py         # NEW (CONCEPTS): generic concept-page renderer (flowchart, code lab, distractors…)
  flow_style.py           # NEW (CONCEPTS): readable() — 18pt charts, max 2 nodes per row (FLOWCHART RULE); used by D1.3+ flow_dot / DECISION_DOT
  concept_types.py        # NEW (CONCEPTS): ConceptContent / Variant / Question / ExamPoint dataclasses
  agent_playground.py     # NEW (CONCEPTS): the playground's agent loop + developer-side knobs (SIMULATED model)
  playground_ui.py        # NEW (CONCEPTS): one message box + knobs + transcript per sub-concept tab
  guide_index.py          # NEW (CONCEPTS): exact guide-PDF positions (section, page, bullet counts) — positions only, no text
  concepts_content/       # NEW (CONCEPTS): one module per built concept (template: agentic_loops.py)
  lab_runner.py           # NEW (CONCEPTS): runs learner code in a separate process (timeout, no keys)
  lab_harness.py          # NEW (CONCEPTS): the child-process side of lab_runner — not run by hand
  lab_trace.py            # NEW (CONCEPTS): event log the lab reads back to colour the flowchart
  mock_claude.py          # NEW (CONCEPTS): SIMULATED Claude-shaped client + scripted scenarios (incl. multi-agent ROLE dispatch)
  research_backend.py     # NEW (CONCEPTS): fake research backend for the multi-agent labs (web_search, Task tool schema)
  session_lab.py          # NEW (CONCEPTS): simulated session layer for D1.4 (resume / continue / fork, fake repo, manifest)
  session_play.py         # NEW (CONCEPTS): D1.4 playground engine
  support_lab.py          # NEW (CONCEPTS): fake support backend + scripted customers for D1.5 (refund ledger, handoffs)
  escalation_play.py      # NEW (CONCEPTS): D1.5 playground engine (system prompt built from knobs, code gate)
  handoff_lab.py · handoff_play.py   # NEW (CONCEPTS): D1.6 simulated downstream agents + playground
  memory_lab.py · memory_play.py     # NEW (CONCEPTS): D1.7 simulated CLAUDE.md/AGENTS.md loader (memory docs rules) + playground
  decomp_lab.py · decomp_play.py     # NEW (CONCEPTS): D1.8 simulated reviewer / legacy codebase + playground
  tool_select_lab.py · toolsel_play.py   # NEW (CONCEPTS): D2.1 simulated tool router + playground
  toolchoice_lab.py · toolchoice_play.py # NEW (CONCEPTS): D2.2 simulated tool_choice / extraction / tool distribution + playground
  mcp_lab.py · mcp_play.py           # NEW (CONCEPTS): D2.3 simulated MCP config (you + a teammate), agent, error backends + playground
  hooks_lab.py · hooks_play.py       # NEW (CONCEPTS): D2.4 simulated Agent SDK hook runner (matchers, Pre/PostToolUse) + playground
  eval_lab.py · eval_play.py         # NEW (CONCEPTS): D2.5 eval harness + release gate on the D2.1 router + playground
  builtin_lab.py · builtin_play.py   # NEW (CONCEPTS): D2.6 simulated repo + Grep/Glob/Read/Edit/Write + surface chooser
  rules_lab.py · rules_play.py       # NEW (CONCEPTS): D3.1 sessions on memory_lab (path-scoped rules, /memory view)
  plan_lab.py · plan_play.py         # NEW (CONCEPTS): D3.2 simulated plan-mode / direct / Explore session
  skills_lab.py · skills_play.py     # NEW (CONCEPTS): D3.3 simulated command/skill loader (scopes, frontmatter)
  checkpoint_lab.py · checkpoint_play.py # NEW (CONCEPTS): D3.4 simulated session with checkpoints, /rewind, git, branch
  review_lab.py · review_play.py     # NEW (CONCEPTS): D4.1 simulated code reviewer reading a system prompt's criteria
  batch_lab.py · batch_play.py       # NEW (CONCEPTS): D4.3 simulated Message Batches (custom_id, failures, windows)
  extract_lab.py · extract_play.py   # NEW (CONCEPTS): D4.4 simulated schema extraction + semantic checks
  attention_lab.py · attention_play.py # NEW (CONCEPTS): D4.7 simulated long-context reader (position effects, trimming)
  fewshot_lab.py · fewshot_play.py   # NEW (CONCEPTS): D4.9 simulated few-shot extractor + iteration loop
  mpreview_lab.py · mpreview_play.py # NEW (CONCEPTS): D4.10 simulated generator + reviewers (instances, passes, routing)
  ctxwin_lab.py · ctxwin_play.py     # NEW (CONCEPTS): D5.1 simulated context window (stateless chat, explorer subagent, session compaction, report budget)
  casefacts_lab.py · casefacts_play.py # NEW (CONCEPTS): D5.2 simulated long support session with summarisation + case-facts block
  stop_lab.py             # NEW (CONCEPTS): stop-reason lab request/actions/expected-action table + reference handler policies
  stop_inspector.py       # NEW (CONCEPTS): the stop-reason inspector playground engine
  research_playground.py  # NEW (CONCEPTS): the multi-agent playground engine (coordinator + subagents, developer-side knobs)
  mcp_live.py · mcp_seq.py # NEW (D2.3.1/2): LIVE MCP client (stdio + Streamable HTTP), research + synthesis agents; sequence diagrams
  mcp_page.py             # NEW (D2.3.1/2): the shared renderer for both live MCP pages (schematic, comparison, steps table, results)
  mcp_charts.py           # NEW (D2.3.1/2): draws the charts the synthesis agent chooses; unverified values are hatched
  vendor_facts.py         # NEW (D2.3.3): sourced facts on financial-data vendors' MCP servers, APIs, content and access
  mcp_edgar_facts.py      # NEW (D2.3.1): sourced facts for the hosted page — SEC endpoints and rules, the four hops, per-tool pseudo code + observed requests
mcp_servers/
  laptop_server.py        # NEW (D2.3.2): the workbench's OWN MCP server (stdio): 9 tools, resources + a template, prompts,
                          #   progress/log notifications, elicitation (save_note), tool annotations; structured errors
  edgar_hosted_server.py  # NEW (D2.3.1): sec-edgar-mcp's 21 tools + workbench resources and prompts, over Streamable HTTP
  data/                   # tickers.csv (real, from sec.gov) · sec_forms.csv · folder_catalog.csv + cleanup_policy.md (MOCK)
  # tools.py (above) is now real: fake support backend used by the labs
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
  QUESTION_MAP.md         # auto-generated from utils/question_bank.py — every guide bullet → the questions that test it (gaps flagged)
  CONCEPTS_MAP.md         # auto-generated from utils/concepts_map.py — every concept vs the guide, with
                          #   its scope status and evidence. Regenerate, don't hand-edit.
  SESSION_LOG.md          # append-only record of every session — Claude adds an entry before stopping
.claude/
  skills/arch-diagram/    # HTML architecture-diagram generator (from agents101)
  commands/next-page.md   # /next-page — builds the next pending page
  commands/next-concept.md # /next-concept — builds the next CONCEPTS page (one per session)
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
| 9 | Subagent spawning | Task tool, `allowedTools` includes `"Task"` (exam wording; current docs name the tool **`Agent`** — `"Task"` is a legacy alias, match both) | no equivalent — `st.code()` + built for real in `sandbox_project/` |

### C. Claude API facts (exam ground truth — taught with `st.code()`, not executed)
- **Agentic loop** *(docs: platform.claude.com/docs/en/build-with-claude/handling-stop-reasons and …/refusals-and-fallback; guide TS 1.1)*: read `stop_reason`. Keep looping **while it is `"tool_use"`**. **Any other value exits the loop and MUST be handled** — `end_turn` = the model finished (check the answer isn't empty); `max_tokens` = truncated (raise it / continue; an incomplete `tool_use` is retried with a higher limit); `stop_sequence` = a custom stop sequence hit; `pause_turn` = server-tool loop paused, send the response back as-is; `refusal` = a normal **HTTP 200** response (not an error) — retry on a **different** model and stay on it; `model_context_window_exceeded` = context full (beta per docs). The exam guide names only `tool_use` and `end_turn`. Do not parse assistant text to decide termination; an iteration cap must not be the *primary* stop condition — the Agent SDK's `max_turns` / `max_budget_usd` are optional guards that surface as error results (`error_max_turns`, `error_max_budget_usd`), never as success.
- **`tool_result` formatting** *(docs: …/tool-use/handle-tool-calls)*: results follow the assistant `tool_use` turn immediately, all in ONE user message, `tool_result` blocks FIRST (text before them → 400 error); text added after results can lead to empty `end_turn` responses. Failures use `is_error: true`.
- **Tool results** go back in a **user** message as `tool_result` blocks, matched to the `tool_use` id. Append them to the history so the model can reason about the next step.
- **Three `tool_choice` modes (guide):** `auto` (may answer in text), `any` (must call some tool), forced `{"type": "tool", "name": "..."}` (must call that tool). The docs add a fourth, `none` (no tools).
- **Forced tool use is not supported everywhere (docs-verified 2026-09-27, define-tools):** `any`/`tool` return a 400 with manual extended thinking and on Claude Opus 5.5, Fable 5.1 and Mythos 5.1 — use `auto` + strict tools or structured outputs there. With `any`/`tool` no text precedes the `tool_use` block.
- Schema-conformant tool output removes JSON *syntax* errors but not *semantic* errors (totals that don't add up, values in the wrong field).
- Batch API facts from the guide: 50% cost saving, up to 24 h window, no latency SLA, no multi-turn tool calling inside one request, correlate with `custom_id`.
- Subagents do **not** inherit the coordinator's history — pass context explicitly in the prompt. *(docs: agent-sdk/subagents § What subagents inherit — a non-fork subagent's only channel from the parent is the spawn tool's prompt string; only its FINAL message returns; the spawn tool is `Agent` in current docs, `Task` in the exam guide; nested subagents allowed by the docs, default depth 3, at most 20 concurrent — past the limit the spawn is refused with "Concurrent subagent limit reached".)*

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
- [ ] Every new question is scenario-framed and pinned (`scenarios=`, `points=`); regenerate `docs/QUESTION_MAP.md` and check no new gaps

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
- [ ] A CONCEPTS page was built → its `docs_refs` / `docs_verified_on` / `grounding` come from docs actually fetched that session (grounding rule), then regenerate `docs/CONCEPTS_MAP.md` (see `utils/concepts_map.py`'s `render_concepts_map_markdown()`)

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
| 9 | (no agents101 equivalent) | **CONCEPTS section** (user request, 2026-09-26): a concept-by-concept learning surface with runnable code labs, added alongside the phases without changing them. Scope follows the guide, not the community list its layout mirrors; every concept is grounded in the official docs (platform.claude.com + code.claude.com); ➕ extras allowed only when docs-grounded. See the CONCEPTS section above. |

## Deferred Work
*(empty)*

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- **This repo's safety rules (added 2026-10-05):** rebuild with `graphify extract . --code-only` then `graphify cluster-only . --no-label` — no model calls, nothing leaves the machine (this is how the current graph was built: 116 code files, docs skipped). Never pass `--no-gitignore` (it would pull in `docs/source/` — the copyrighted guide PDF — and `.env`). Don't run `/graphify .` semantic extraction or `graphify label` here without asking: they send docs to a model and can pick up the Gemini key from the environment. `graphify-out/` is gitignored; the PreToolUse hooks live in the gitignored `.claude/settings.json` (local only). Undo everything with `graphify uninstall --project`.
