# Sources

## Ground truth

| # | Source | Status | Notes |
|---|---|---|---|
| 1 | **Claude Certified Architect – Foundations Exam Guide**, v1.0, effective July 2026, exam code CCAR-F (Anthropic) | **GROUND TRUTH** | Local copy in `docs/source/` — **gitignored, never committed** (copyrighted). Wins over every other source. If anything disagrees with it, follow the guide and record the disagreement below. |

Everything in this repo is a **paraphrase** of the guide. No long passages are copied. No real exam questions are reproduced or recalled; every question we write is original.

## What the guide itself covers (official — no "verify" label needed)
- Exam format, timing, passing score (720 scaled), validity (12 months), fee, retake waiting periods, registration, rules of conduct (guide sections 3, 10–15)
- Domains, weights, the 6 scenarios, all 30 task statements (sections 4–6)
- The in-scope and out-of-scope lists (appendix)
- CLI facts it names: `-p` / `--print`, `--output-format json`, `--json-schema`; `--resume`, `fork_session`, `/memory`, `/compact`

## Unverified community claims

Anything below is labelled **"community claim, verify in current docs"** wherever it appears in the repo. No page, question or demo may rely on one of these until it is verified against the guide or current official docs.

| # | Claim | Where it is used | Status |
|---|---|---|---|
| 1 | A newer model may reject a forced `tool_choice` | `CLAUDE.md` Critical SDK Notes; page 2.3 | UNVERIFIED — check current docs before teaching |
| 2 | Real exam scores land roughly 40–190 points below practice-exam scores, so treat 900 as a floor | Readiness gate 3; `docs/STUDY_PLAN.md` | UNVERIFIED — candidate reports only |
| 3 | CLI flags beyond `-p`, `--output-format json`, `--json-schema` | Page 3.6; `sandbox_project/` | UNVERIFIED — verify each flag with `claude --help` / current docs before use |
| 4 | Model-specific behaviour (any claim of the form "model X does Y") | Any page | UNVERIFIED |
| 5 | Exam-policy details **not** in the guide (e.g. the size of partner-tier discounts, unofficial retake or scheduling tips) | `07c_Exam_Day` | UNVERIFIED — the guide's own section 11–12 wording is the reference |
| 6 | Gemini function-calling mode names and `usage_metadata` fields used in the Claude-to-Gemini mapping table | `CLAUDE.md` Critical SDK Notes B | UNVERIFIED — check current Google docs before a page relies on them |
| 7 | The community concept list's taxonomy (71 concepts, D-numbering, section layout) | CONCEPTS section (`utils/concepts_map.py`) | UNVERIFIED third-party structure; each concept's scope status is Claude's judgment vs guide v1.0 (2026-09-26) |
| 8 | Exact error wording and the deterministic empty-`end_turn` in the simulated Messages API | `utils/mock_claude.py` | The RULES are now docs-verified (2026-09-26: tool_result ordering and pairing, empty end_turn after text-after-results, refusal shape, max_tokens, pause_turn); the exact wording is an approximation and is marked SIMULATED |

> **Origin of these claims:** they were relayed in the CCAR-F build prompt without named URLs. No specific community repo, blog or forum is recorded here yet. When you consult one, add a row to the table below.

## Official Claude docs consulted (technical truth — CLAUDE.md source-of-truth rule 5)

| # | Page (all fetched and read) | Date | Used for |
|---|---|---|---|
| 1 | platform.claude.com/docs/en/build-with-claude/handling-stop-reasons | 2026-09-26 | The seven stop_reason values, per-reason handling, empty end_turn pitfall, stop reasons vs errors — D1.1 Agentic Loops |
| 2 | platform.claude.com/docs/en/build-with-claude/refusals-and-fallback | 2026-09-26 | refusal = HTTP 200, stop_details, retry on a different model, pitfalls — D1.1 |
| 3 | platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works | 2026-09-26 | The client-tool agentic loop, server-side loop / pause_turn — D1.1 |
| 4 | platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls | 2026-09-26 | tool_result formatting rules, is_error, parallel results — D1.1 |
| 5 | platform.claude.com/docs/en/agents-and-tools/tool-use/overview and …/build-a-tool-using-agent | 2026-09-26 | Tool Runner, tutorial loop — D1.1 |
| 6 | code.claude.com/docs/en/agent-sdk/agent-loop (platform `/agent-sdk/*` redirects here) | 2026-09-26 | SDK loop, max_turns / max_budget_usd, ResultMessage subtypes, hooks — D1.1 |
| 7 | platform.claude.com/docs/llms.txt (index, 637 English pages) | 2026-09-26 | Finding docs for concepts and candidate pages for extras (`EXTRA_DOCS`) |

## Community sources consulted

| # | Source (name + URL) | Date read | What we took from it | Agrees with guide? |
|---|---|---|---|---|
| 1 | claudearchitectcertification.com — `/concepts` and `/concepts/agentic-loops` (third-party site) | 2026-09-26 | Concept list, domain grouping and page-section layout — structure only, no text copied | Partly: the 30 numbered concepts fit the guide's 5 domains; the 41 unnumbered ones mostly have no matching guide content (`docs/CONCEPTS_MAP.md`) |

## Disagreements between community sources and the guide

| # | Topic | Community says | Guide says | What we follow |
|---|---|---|---|---|
| 1 | Scope of what is worth studying | The concept list includes Vision & Multimodal, Streaming, Prompt Caching and Auth & Access Control as concepts | Guide Appendix: vision and streaming are out of scope, prompt caching is "know it exists" only, API authentication is out of scope | The guide — those concepts are listed but not built |

## Where the official docs refine the guide

| # | Topic | Guide says | Docs say | What we follow |
|---|---|---|---|---|
| 1 | Loop stop reasons | TS 1.1 names `tool_use` (continue) and `end_turn` (stop) | Seven values; the loop exits on any non-`tool_use` reason and the app must handle each (`max_tokens`, `refusal`, `pause_turn`, …) | Docs for behaviour; the guide for what the exam expects — the page teaches both and marks which is which |
| 2 | Iteration caps | Anti-pattern when used as the PRIMARY stop mechanism | The Agent SDK offers `max_turns` / `max_budget_usd` as optional guards that return an error result when hit | Both are compatible: a limit is a loud guard, never the way a healthy loop ends |

## Out-of-scope (from the guide — never build on these)
Fine-tuning / training models · API auth, billing, account management · language/framework specifics beyond tool and schema config · deploying or hosting MCP servers · Claude internals, training, weights · Constitutional AI / RLHF / safety training · embedding models and vector DBs · computer use · vision / image analysis · streaming / SSE · rate limits, quotas, pricing calculations · OAuth / key rotation / auth protocol details · cloud-provider configuration · benchmarking / model comparison metrics · prompt-caching implementation details (know it exists) · token counting / tokenisation.

## Reference material (not a source of exam truth)
| # | File | Purpose |
|---|---|---|
| 1 | `docs/reference/agents101_CLAUDE.md` | Copy of the agents101 `CLAUDE.md` — the structure and conventions this repo mirrors. Says nothing about the exam. |
