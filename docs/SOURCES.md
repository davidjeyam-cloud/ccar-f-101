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
| 28 | platform.claude.com/docs/en/test-and-evaluate/develop-tests | 2026-09-28 | Success criteria (specific, measurable), eval design (task-specific, edge cases, automate, volume over quality), grading methods — D2.5 |
| 29 | platform.claude.com/docs/en/agents-and-tools/tool-use/troubleshooting-tool-use | 2026-09-28 | Wrong tool → sharpen descriptions (WHEN to use); wrong parameters → strict / input_examples — D2.5 |
| 30 | code.claude.com/docs/en/tools-reference | 2026-09-28 | Read/Write/Edit/Grep/Glob/Bash behaviour; Edit needs a unique old_string (or replace_all); Grep/Glob absent by default on macOS/Linux/WSL — D2.6 |
| 31 | code.claude.com/docs/en/features-overview | 2026-09-28 | CLAUDE.md vs rules vs skills vs subagents vs hooks vs MCP; context cost by feature; guardrails belong in hooks — D2.6, D3.3 |
| 32 | code.claude.com/docs/en/memory (re-read) | 2026-09-28 | Locations, on-demand subdirectory loading, path-scoped rules trigger on READ, glob examples (*.md = root only), `paths` the only field read — D3.1 |
| 33 | code.claude.com/docs/en/permission-modes | 2026-09-28 | Plan mode (read-only until approved; Shift+Tab, /plan, --permission-mode plan; approval options) — D3.2 |
| 34 | code.claude.com/docs/en/sub-agents (re-read) | 2026-09-28 | Built-in Explore / Plan subagents; available tools and inheritance; tools vs disallowedTools — D1.2 tools grid, D3.2 |
| 35 | code.claude.com/docs/en/skills | 2026-09-28 | Skill locations and precedence, frontmatter (context: fork, agent, allowed-tools, disallowed-tools, argument-hint, disable-model-invocation), arguments — D3.3 |
| 36 | code.claude.com/docs/en/checkpointing | 2026-09-28 | Checkpoints per prompt, /rewind options, summarize, limitations (Bash, subagents, external), not a replacement for git — D3.4 |
| 37 | platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | 2026-09-28 | Be clear and direct, add context, role, use examples (3–5, relevant/diverse/structured), long-context prompting (documents at the top, query at the end), XML tags, chain complex prompts / self-correction — D4.1, D4.7, D4.9, D4.10 |
| 38 | platform.claude.com/docs/en/build-with-claude/batch-processing | 2026-09-28 | Message Batches: up to 24 h, 50% cost, results in any order → match by custom_id, result types (succeeded/errored/canceled/expired), tool use supported per request — D4.3 |
| 39 | platform.claude.com/docs/en/build-with-claude/structured-outputs + …/tool-use/strict-tool-use | 2026-09-28 | Schema-guaranteed output; what it doesn't guarantee (semantic correctness); strict tools — D4.4 |
| 40 | platform.claude.com/docs/en/build-with-claude/prompt-caching (+ batch-processing § Using prompt caching with Message Batches) | 2026-09-28 | What caching reuses (identical prefix, tools → system → messages), uses, output unchanged, batch + caching (discounts stack, hits best-effort) — D4.2 awareness page; implementation detail deliberately not taught |
| 41 | platform.claude.com/docs/en/build-with-claude/context-windows | 2026-09-28 | What counts toward the window; turns accumulate; context rot; overflow (400 prompt is too long / model_context_window_exceeded); caching doesn't free window space; compaction + context editing pointers — D5.1 |
| 42 | platform.claude.com/docs/en/build-with-claude/context-editing + …/compaction | 2026-09-28 | Tool result clearing (beta), thinking block clearing; compaction on demand vs at a threshold; custom summarisation prompt — D5.1, D5.2 |
| 43 | code.claude.com/docs/en/how-claude-code-works | 2026-09-28 | Context window in Claude Code: auto-compaction, early instructions may be lost → CLAUDE.md, /compact focus, /context, subagents' own windows — D5.1 |
| 44 | platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices (§ State management, multi-context-window workflows) | 2026-09-28 | Structured formats (JSON) for state data, free text for progress notes, git for state — D5.2 |

## Community sources consulted

| # | Source (name + URL) | Date read | What we took from it | Agrees with guide? |
|---|---|---|---|---|
| 1 | claudearchitectcertification.com — `/concepts` and `/concepts/agentic-loops` (third-party site) | 2026-09-26 | Concept list, domain grouping and page-section layout — structure only, no text copied | Partly: the 30 numbered concepts fit the guide's 5 domains; the 41 unnumbered ones mostly have no matching guide content (`docs/CONCEPTS_MAP.md`) |
| 2 | Official guide §9 Sample Questions (12 items, pp.27–33 of the local PDF) — official, listed here because it set the question STYLE | 2026-09-27 | Style benchmark for D1.6's rewritten questions: 3–5 sentence production symptom with numbers and log evidence; hidden qualifier (most effective / most likely root cause / first step / how should you evaluate); four equal-length options; wrong options that are prompt-instead-of-code, over-engineered, solve a different problem, blame a working downstream agent, over-provision tools, or misread a parameter. No sample question reused. | Yes (official) |
| 3 | Community question banks: github.com/OlivierAlter/Claude-Certified-Architect-Foundations-Certification-Exam, github.com/hamzafarooq/claude-certified-architect, claudecertifiedarchitects.com/cca-practice-questions, certsafari.com (CCAR-F page) | 2026-09-27 | Style only (stem length, numeric symptoms, distractor patterns) — community claim, unverified; no question, stem or option copied or adapted | Style matches the guide's §9 samples; content not verified |
| 4 | MCP for the live pages D2.3.1 / D2.3.2: modelcontextprotocol.io (*Architecture overview*; *Understanding MCP servers* — read 2026-10-04 for who controls tools / resources / prompts; *Specification 2025-06-18 → Server → Tools*) and the server github.com/stefanoamorelli/sec-edgar-mcp (v1.0.8, AGPL-3.0, community, not SEC-affiliated) | 2026-10-03 | modelcontextprotocol.io is the protocol's own documentation (not Anthropic exam material): host/client/server, transports, tools/list, tools/call, isError. The server is run as an optional local subprocess, never vendored into this repo | Behaviour on the page was observed in live runs on 2026-10-03 (21 tools, protocol 2025-11-25, `search_companies` returning empty successes, `success:false` with `isError=false`). ➕ extra — building a client is not on the exam |
| 5 | SEC pages for the hosted MCP page D2.3.1: sec.gov — *EDGAR Application Programming Interfaces* and *Developer resources* (read 2026-10-04); the source code of `sec-edgar-mcp` 1.0.8 and `edgartools` 5.60.0 (read from the installed packages); the MCP server's own request log for 8 tools × 2 calls (44 requests, AAPL, 2026-10-04) | 2026-10-04 | Endpoint URL patterns, no API key, 10 requests per second, no CORS on data.sec.gov, no SQL or query interface mentioned; what each tool fetches and how | SEC pages are the SEC's own wording (not Anthropic exam material). A row marked 👁 comes from the log and can change when the package or the SEC changes. ➕ extra — not on the exam |
| 6 | Vendor pages for D2.3.3 (financial-data vendors), read 2026-10-04: Crunchbase (data.crunchbase.com docs, product page); ZoomInfo (zoominfo.com MCP page, docs.gtm.ai); Moody's (MCP page, GenAI-ready-data blog, press release); S&P Global / Kensho (press release, Kensho news); FactSet (insight.factset.com articles); Bloomberg (professional.bloomberg.com API library, Data License, Data License Plus); LSEG (press releases, developers.lseg.com, data catalogue); Fitch (a republished press release on ffnews.com) | 2026-10-04 | MCP endpoints and tool names, REST/library APIs, content sold (high level) and how a client gets access | Each vendor's wording, not Anthropic exam material. Pages that were blocked, script-built or returned only a title are listed on the page under "What I could not check" (Fitch's own domains, S&P RatingsDirect and marketplace pages, FactSet's developer portal). No prices were published on any page read. ➕ extra — not on the exam |

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
| 14 | `allowed-tools` in skills | TS 3.2 S3: allowed-tools restricts tool access during a skill | allowed-tools PRE-APPROVES tools for the turn and “does not restrict which tools are available”; `disallowed-tools` removes tools | Exam answers: allowed-tools (the guide's wording). Real skills: disallowed-tools to take tools away. D3.3 teaches both; its lab follows the docs |
| 15 | `argument-hint` | TS 3.2 S4: prompts developers for required parameters | A hint shown during autocomplete (e.g. `[issue-number]`) | Consistent in intent; the page quotes the docs' mechanism |
| 16 | Path-scoped rules trigger | TS 3.3 K2: rules load “when editing matching files” | Rules trigger when Claude READS a matching file, not on every tool use | Docs for behaviour (reading precedes editing, so both hold in practice) — D3.1 |
| 17 | Grep / Glob tools | TS 2.5 assumes Grep and Glob tools | Absent by default on macOS, Linux and WSL; Claude runs grep / find through Bash | Same choice either way (content vs path search) — D2.6 |
| 18 | Checkpoints | Not in guide v1.0 (TS 1.7 covers --resume and fork_session; TS 5.4 /compact) | Checkpoints per prompt, /rewind menu, Bash changes not tracked | Taught as 📘 docs-only on D3.4 |
| 19 | Tool evaluation | No task statement; §7 p.24 says to test tool selection with ambiguous requests | develop-tests gives the method (criteria, edge cases, grading) | D2.5 is ◐ partial: guide sets what to test, docs how |
| 20 | Batch and tools | TS 4.5: no multi-turn tool calling within a single batch request | Tool use is supported inside batch requests | Consistent: a request can include tools, but there's no round trip mid-request to run them — D4.3 teaches the guide's point |
| 21 | Few-shot count | TS 4.2: 2–4 targeted examples | 3–5 examples | Exam answers: the guide's range; D4.9 shows both |
| 22 | Long-context placement | TS 5.1: key findings summary at the start, section headers | Put long documents at the top and the query at the end (up to 30% better) | Complementary; D4.7 teaches both, tagged by source |
| 23 | Self-reported confidence | TS 5.2: unreliable proxy for escalation | TS 4.6 S3 / 5.5: per-finding confidence routes review findings once calibrated | Guide-internal distinction (different decisions); D4.10 FAQ explains it |
| 24 | Prompt caching | Only in the out-of-scope list: implementation details out of scope beyond knowing it exists (§17 Appendix · p.39 — the Appendix starts p.36, the Out-of-Scope list p.38) | Docs cover it in full (breakpoints, lifetimes, minimums, usage fields) | D4.2 is an awareness page: what it is / is not, no implementation detail |
| 25 | Managing a full context | TS 5.4 S5 names /compact (Claude Code) | The API adds server-side compaction and context editing (beta); Claude Code auto-compacts and may lose early instructions (put persistent rules in CLAUDE.md) | D5.1 teaches /compact as ⭐ and the rest as 📘 docs-only |

## Out-of-scope (from the guide — never build on these)
Fine-tuning / training models · API auth, billing, account management · language/framework specifics beyond tool and schema config · deploying or hosting MCP servers · Claude internals, training, weights · Constitutional AI / RLHF / safety training · embedding models and vector DBs · computer use · vision / image analysis · streaming / SSE · rate limits, quotas, pricing calculations · OAuth / key rotation / auth protocol details · cloud-provider configuration · benchmarking / model comparison metrics · prompt-caching implementation details (know it exists) · token counting / tokenisation.

## Reference material (not a source of exam truth)
| # | File | Purpose |
|---|---|---|
| 1 | `docs/reference/agents101_CLAUDE.md` | Copy of the agents101 `CLAUDE.md` — the structure and conventions this repo mirrors. Says nothing about the exam. |
