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
| 1 | A newer model may reject a forced `tool_choice` | `CLAUDE.md` Critical SDK Notes; D2.2 Tool Choice | **VERIFIED 2026-09-27** (define-tools § Forcing tool use: 400 on Opus 5.5 / Fable 5.1 / Mythos 5.1 and with manual extended thinking) |
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
| 1 | platform.claude.com/docs/en/build-with-claude/handling-stop-reasons | 2026-09-26 (re-read for D1.3) | The seven stop_reason values, per-reason handling, empty end_turn pitfall, stop reasons vs errors, stop sequence text NOT in content, pause_turn default limit 10 — D1.1 Agentic Loops, D1.3 Stop Reason |
| 2 | platform.claude.com/docs/en/build-with-claude/refusals-and-fallback | 2026-09-26 (re-read for D1.3) | refusal = HTTP 200, stop_details (type/category/explanation, nullable), categories, retry on a different model, pitfalls — D1.1, D1.3 |
| 3 | platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works | 2026-09-26 | The client-tool agentic loop, server-side loop / pause_turn — D1.1 |
| 4 | platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls | 2026-09-26 | tool_result formatting rules, is_error, parallel results — D1.1 |
| 5 | platform.claude.com/docs/en/agents-and-tools/tool-use/overview and …/build-a-tool-using-agent | 2026-09-26 | Tool Runner, tutorial loop — D1.1 |
| 6 | code.claude.com/docs/en/agent-sdk/agent-loop (platform `/agent-sdk/*` redirects here) | 2026-09-26 | SDK loop, max_turns / max_budget_usd, ResultMessage subtypes, hooks — D1.1 |
| 7 | code.claude.com/docs/en/agent-sdk/subagents | 2026-09-26 | Subagent context isolation, AgentDefinition fields, spawn tool name (Agent/Task), depth/concurrency/spend limits — D1.2 Subagents |
| 8 | code.claude.com/docs/en/sub-agents | 2026-09-26 | Claude Code subagents: context received, forks, best practices/limitations, Task-vs-Agent note — D1.2 |
| 9 | code.claude.com/docs/en/agent-sdk/sessions | 2026-09-26 | continue / resume / fork sessions — D1.2 (guide TS 1.3 Knowledge 4) |
| 10 | code.claude.com/docs/en/sessions | 2026-09-27 | --continue vs --resume <name>, naming (-n, /rename), what a resumed session restores, --fork-session and /branch, /compact, /clear — D1.4 |
| 11 | code.claude.com/docs/en/best-practices | 2026-09-27 | performance degrades as context fills; /clear, /compact <instructions>; hooks deterministic vs instructions advisory — D1.4, D1.5 |
| 12 | code.claude.com/docs/en/agent-sdk/sessions (re-read) | 2026-09-27 | SDK resume takes a session ID; fork_session; forks don't branch files; fresh session + captured state — D1.4 |
| 13 | platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat | 2026-09-27 | sample good interactions in the prompt; escalation-accuracy metric — D1.5 |
| 14 | platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | 2026-09-27 | examples: relevant, diverse, <example> tags, 3–5 of them; explain why — D1.5 |
| 15 | code.claude.com/docs/en/agent-sdk/hooks | 2026-09-27 | PreToolUse permissionDecision deny + reason; deny priority — D1.5 |
| 16 | code.claude.com/docs/en/memory | 2026-09-27 | CLAUDE.md scopes and load order, subdirectory on-demand loading, @import rules (relative to the importing file, 4 hops), .claude/rules/ and `paths`, /memory, 200-line target, AGENTS.md rules — D1.7 |
| 17 | code.claude.com/docs/en/common-workflows | 2026-09-27 | codebase exploration and test recipes — D1.8 |
| 18 | platform.claude.com prompting best practices (re-read) | 2026-09-27 | chain complex prompts; subagent orchestration; state tracking; structured state formats — D1.6, D1.8 |
| 19 | platform.claude.com/docs/llms.txt (index, 637 English pages) | 2026-09-26 | Finding docs for concepts and candidate pages for extras (`EXTRA_DOCS`) |
| 20 | platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools | 2026-09-27 | Tool definition fields, name regex, input_examples, detailed descriptions, consolidating/namespacing tools, tool_choice auto/any/tool/none, no text before a forced call, models that reject forcing — D2.1, D2.2 |
| 21 | platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use and …/build-with-claude/structured-outputs | 2026-09-27 | strict: true (schema-valid inputs, additionalProperties: false); schema compliance ≠ semantic correctness — D2.2 |
| 22 | code.claude.com/docs/en/mcp | 2026-09-27 | local/project/user scopes and storage, approval prompt, precedence, ${VAR} / ${VAR:-default} expansion and missing-variable warning, credential variables empty in remote url/headers, tool search, output limits — D2.3 |
| 23 | code.claude.com/docs/en/common-workflows (re-read) | 2026-09-27 | @server:resource references to MCP resources — D2.3 |
| 24 | code.claude.com/docs/en/agent-sdk/custom-tools | 2026-09-27 | isError / is_error, uncaught exceptions become error results, tools vs allowedTools — D2.2, D2.3 |
| 25 | code.claude.com/docs/en/agent-sdk/hooks | 2026-09-27 | Hook events (Python vs TS), HookMatcher, callback inputs/outputs, PreToolUse decisions, PostToolUse updatedToolOutput / additionalContext, deny > defer > ask > allow, parallel hooks, async output, timeouts, troubleshooting — D2.4 |
| 26 | code.claude.com/docs/en/hooks and …/hooks-guide | 2026-09-27 | Matcher patterns (exact vs regex, mcp__server__.*); deterministic control; PostToolUse can't undo — D2.4 |
| 27 | code.claude.com/docs/en/agent-sdk/permissions | 2026-09-27 | Evaluation order: hooks → deny → ask → mode → allow → canUseTool; hook deny applies even in bypassPermissions — D2.4 |

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
| 3 | Name of the spawn tool | TS 1.3: the **Task** tool; `allowedTools` must include "Task" | The tool is **Agent** (appears as "Task" only in the init tool list; `tool_use` blocks said "Task" before Claude Code v2.1.63); docs examples put "Agent" in allowed_tools | The guide's term for exam answers; the page teaches both and advises matching both in real code |
| 4 | Who routes communication | TS 1.2: hub-and-spoke — the coordinator manages ALL inter-subagent communication | Subagents can spawn their own subagents (default depth 3), capped by depth / concurrency / spend limits | The guide's hub-and-spoke for design and exam answers (observability, consistent error handling); the docs' nesting is noted as a real capability |
| 5 | Resuming by name | TS 1.7: `--resume <session-name>` and `fork_session` | CLI: `claude --resume <name>` (or an ID; an ambiguous name opens the picker); Agent SDK: `resume` takes a session ID, `fork_session=True` | Consistent; the page shows which control belongs to the CLI and which to the SDK |
| 6 | Escalation rules | TS 5.2 defines the triggers (human request, policy gap/ambiguity, no progress) and the unreliable proxies (sentiment, self-reported confidence) | The docs define no escalation rules; they supply mechanisms (examples in prompts, deterministic hooks / PreToolUse deny, an escalation-accuracy metric) | The guide for the rules, the docs for the mechanisms — tagged as such on the page |
| 7 | AGENTS.md | Not mentioned in guide v1.0 (TS 3.1 covers CLAUDE.md only) | Claude Code reads AGENTS.md when no CLAUDE.md / .claude/CLAUDE.md / CLAUDE.local.md is present above; otherwise import it (@AGENTS.md) or change the setting (v2.1.277+) | Taught on D1.7 as 📘 docs-only, never gold; its question is `in_bank=False` |
| 8 | tool_choice options | TS 2.3 K4 / TS 4.3 K2: auto, any, forced | Four options (+ `none`); forcing rejected on some models and with manual extended thinking | Guide's three for exam answers; the page teaches `none` and the restriction as 📘 docs-only |
| 9 | Split vs consolidate tools | TS 2.1: split generic tools into purpose-specific ones with defined contracts | Best practices also suggest consolidating related operations behind an `action` parameter | Compatible: both aim at unambiguous selection; D2.1 teaches the guide's split and notes the docs' option |
| 10 | MCP scopes | TS 2.4: project (.mcp.json) vs user (~/.claude.json) | Three scopes; local (in ~/.claude.json per project) is the default | Guide's two for exam answers; local shown as 📘 docs-only |
| 11 | MCP tool discovery | TS 2.4 K3: all servers' tools discovered at connection, available together | Tool search and cached tool lists can defer connecting a server until first use | Guide for exam answers; the docs' refinement in the D2.3 FAQ |
| 12 | MCP error fields | TS 2.2: isError plus errorCategory / isRetryable / description | The protocol/SDK flag is isError (is_error in Python); the content is yours to structure | Consistent: errorCategory/isRetryable are the guide's convention for the content |
| 13 | Hook names | TS 1.5: PostToolUse and "tool call interception" hooks | The interception event is PreToolUse (allow/deny/ask/defer, updatedInput); PostToolUse can't undo an action | Consistent; the page names PreToolUse and teaches the docs' mechanics as 📘 docs-only |

## Out-of-scope (from the guide — never build on these)
Fine-tuning / training models · API auth, billing, account management · language/framework specifics beyond tool and schema config · deploying or hosting MCP servers · Claude internals, training, weights · Constitutional AI / RLHF / safety training · embedding models and vector DBs · computer use · vision / image analysis · streaming / SSE · rate limits, quotas, pricing calculations · OAuth / key rotation / auth protocol details · cloud-provider configuration · benchmarking / model comparison metrics · prompt-caching implementation details (know it exists) · token counting / tokenisation.

## Reference material (not a source of exam truth)
| # | File | Purpose |
|---|---|---|
| 1 | `docs/reference/agents101_CLAUDE.md` | Copy of the agents101 `CLAUDE.md` — the structure and conventions this repo mirrors. Says nothing about the exam. |
