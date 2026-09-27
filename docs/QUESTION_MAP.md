# Question Map — every bank question pinned to the exam guide

Auto-generated from `utils/question_bank.py` (which collects each built concept page's practice items). Regenerate, don't hand-edit. Every bank question is set in one of the guide's six scenarios (§5, pp.3–4) and pinned to the exact Knowledge/Skill bullet(s) it tests (§6). A wrong pin fails at import (`Question.__post_init__` → `guide_index.point_ref`). Questions are original — never real exam items — and `reviewed_by_user: False` until the owner signs them off.

**150 bank questions.** Guide bullets covered in the task statements built so far: **208 / 215**. Whole guide: 208 / 240 (task statements with no built concept yet are listed as gaps below).

| # | Scenario (primary) | Questions |
|---|---|---|
| 1 | Customer Support Resolution Agent | 40 |
| 2 | Code Generation with Claude Code | 31 |
| 3 | Multi-Agent Research System | 25 |
| 4 | Developer Productivity with Claude | 23 |
| 5 | Claude Code for Continuous Integration | 13 |
| 6 | Structured Data Extraction | 18 |

**Correct-answer position** (should be roughly even): A 34 · B 40 · C 42 · D 34


## TS 1.1 — Agentic loops (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.1 · Knowledge 1 · p.5 | stop-reason · S1 — Your support agent returns a response with stop_reason tool_use. Its content is a text blo…<br>stop-reason · S4 — A codebase-exploration agent requests Grep for “refund_policy”. Your code runs it, stores … |
| K2 | TS 1.1 · Knowledge 2 · p.5 | agentic-loops · S1 — After each tool call, your loop runs the tool, writes the result to your monitoring system…<br>stop-reason · S4 — A codebase-exploration agent requests Grep for “refund_policy”. Your code runs it, stores … |
| K3 | TS 1.1 · Knowledge 3 · p.5 | stop-reason · S1 — To make the support agent “predictable”, a team hard-codes every request to run get_custom… |
| S1 | TS 1.1 · Skill 1 · p.5 | agentic-loops · S4 — A code-migration agent needs between 2 and 15 tool calls, depending on the repository. Its…<br>stop-reason · S1 — Your support agent returns a response with stop_reason tool_use. Its content is a text blo… |
| S2 | TS 1.1 · Skill 2 · p.5 | agentic-loops · S1 — After each tool call, your loop runs the tool, writes the result to your monitoring system… |
| S3 | TS 1.1 · Skill 3 · p.5 | agentic-loops · S1 — Your support agent's loop ends the conversation when the assistant's text contains “resolv…<br>agentic-loops · S4 — A code-migration agent needs between 2 and 15 tool calls, depending on the repository. Its…<br>stop-reason · S1 — A team's loop treats any response that contains a text block as the agent's final answer. … |

## TS 1.2 — Coordinator-subagent (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.2 · Knowledge 1 · pp.5–6 | subagents · S3 — To save a round trip, a developer lets the synthesis subagent call the web-search subagent… |
| K2 | TS 1.2 · Knowledge 2 · pp.5–6 | subagents · S3 — The coordinator prompts each search subagent with a numbered procedure: search site A, the… |
| K3 | TS 1.2 · Knowledge 3 · pp.5–6 | subagents · S3 — Users ask everything from “What year was the EU ETS launched?” to “Compare carbon-pricing … |
| K4 | TS 1.2 · Knowledge 4 · pp.5–6 | subagents · S3 — Asked to research “renewable energy adoption in Europe”, the system returns a well-cited r… |
| S1 | TS 1.2 · Skill 1 · pp.5–6 | subagents · S3 — Users ask everything from “What year was the EU ETS launched?” to “Compare carbon-pricing … |
| S2 | TS 1.2 · Skill 2 · pp.5–6 | subagents · S3 — Two search subagents receive the same brief: “find recent evidence on battery recycling”. … |
| S3 | TS 1.2 · Skill 3 · pp.5–6 | subagents · S3 — A user asked for a report on “the EV market: regulation, market size and supply chains”. T… |
| S4 | TS 1.2 · Skill 4 · pp.5–6 | subagents · S3 — To save a round trip, a developer lets the synthesis subagent call the web-search subagent… |

## TS 1.3 — Subagent invocation (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.3 · Knowledge 1 · pp.6–7 | subagents · S3 — A coordinator built with the Agent SDK has three well-described subagent definitions, and … |
| K2 | TS 1.3 · Knowledge 2 · pp.6–7 | subagent-state-handoff · S3 — Reviewers flag that 70% of the research system's final reports contain only generic statem… |
| K3 | TS 1.3 · Knowledge 3 · pp.6–7 | subagents · S3 — The coordinator sends document-analysis work to the web-search subagent in about 25% of ru… |
| K4 | TS 1.3 · Knowledge 4 · pp.6–7 | session-state · S2 — After a 90-minute shared analysis of a legacy billing module, the team wants to compare tw… |
| S1 | TS 1.3 · Skill 1 · pp.6–7 | subagent-state-handoff · S3 — Reviewers flag that 70% of the research system's final reports contain only generic statem…<br>subagent-state-handoff · S3 — To cut cost, a teammate proposes that the coordinator pass only the 5 highest-relevance fi… |
| S2 | TS 1.3 · Skill 2 · pp.6–7 | subagent-state-handoff · S3 — The synthesis subagent now receives all 40 findings, and the reports read well. However, a…<br>subagent-state-handoff · S3 — The synthesis subagent has a 6,000-token input budget. Four document-analysis subagents ea… |
| S3 | TS 1.3 · Skill 3 · pp.6–7 | subagents · S3 — To research three independent regions, the coordinator spawns one search subagent, waits f… |
| S4 | TS 1.3 · Skill 4 · pp.6–7 | subagents · S3 — The coordinator prompts each search subagent with a numbered procedure: search site A, the… |

## TS 1.4 — Enforcement & handoff (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.4 · Knowledge 1 · p.7 | stop-reason · S1 — To make the support agent “predictable”, a team hard-codes every request to run get_custom…<br>escalation · S1 — The system prompt says “always verify the customer with get_customer before issuing a refu… |
| K2 | TS 1.4 · Knowledge 2 · p.7 | escalation · S1 — The system prompt says “always verify the customer with get_customer before issuing a refu… |
| K3 | TS 1.4 · Knowledge 3 · p.7 | escalation · S1 — Human agents say escalated tickets from the support agent arrive as free-text notes averag…<br>subagent-state-handoff · S1 — Your support agent escalates policy-exception refunds by calling escalate_to_human with th… |
| S1 | TS 1.4 · Skill 1 · p.7 | escalation · S1 — The system prompt says “always verify the customer with get_customer before issuing a refu… |
| S2 | TS 1.4 · Skill 2 · p.7 | escalation · S1 — One message from a customer covers three things: a damaged blender, a double charge on las… |
| S3 | TS 1.4 · Skill 3 · p.7 | escalation · S1 — Human agents say escalated tickets from the support agent arrive as free-text notes averag…<br>subagent-state-handoff · S1 — Your support agent escalates policy-exception refunds by calling escalate_to_human with th… |

## TS 1.5 — Hooks (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.5 · Knowledge 1 · pp.7–8 | hooks · S1 — Two third-party MCP tools return dates differently, one as Unix seconds and one as ISO 860…<br>hooks · S1 — get_customer returns full card numbers and dates of birth, which the model never needs and… |
| K2 | TS 1.5 · Knowledge 2 · pp.7–8 | hooks · S1 — Company policy says refunds above $500 must go to a human. The support agent's system prom… |
| K3 | TS 1.5 · Knowledge 3 · pp.7–8 | hooks · S1 — Company policy says refunds above $500 must go to a human. The support agent's system prom…<br>hooks · S1 — A support team is converting its rule list into hooks after a hook fixed its refund-limit …<br>hooks · S1 — get_customer returns full card numbers and dates of birth, which the model never needs and… |
| S1 | TS 1.5 · Skill 1 · pp.7–8 | hooks · S1 — Two third-party MCP tools return dates differently, one as Unix seconds and one as ISO 860… |
| S2 | TS 1.5 · Skill 2 · pp.7–8 | hooks · S1 — Company policy says refunds above $500 must go to a human. The support agent's system prom…<br>hooks · S1 — A PreToolUse hook now blocks refunds over $500. But when a refund is blocked, the agent re… |
| S3 | TS 1.5 · Skill 3 · pp.7–8 | hooks · S1 — Company policy says refunds above $500 must go to a human. The support agent's system prom…<br>hooks · S1 — A support team is converting its rule list into hooks after a hook fixed its refund-limit … |

## TS 1.6 — Task decomposition (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.6 · Knowledge 1 · p.8 | task-decomposition · S5 — A team has two workflows. Workflow 1 runs the same security, style and test-coverage check… |
| K2 | TS 1.6 · Knowledge 2 · p.8 | task-decomposition · S5 — Your CI review already reviews each of a pull request's changed files in its own pass, whi… |
| K3 | TS 1.6 · Knowledge 3 · p.8 | task-decomposition · S4 — An engineer asks the agent to “add comprehensive tests to our legacy billing codebase”: 18…<br>task-decomposition · S4 — An agent investigating a production memory leak was given a fixed plan: profile service A,… |
| S1 | TS 1.6 · Skill 1 · p.8 | task-decomposition · S5 — A team has two workflows. Workflow 1 runs the same security, style and test-coverage check… |
| S2 | TS 1.6 · Skill 2 · p.8 | task-decomposition · S5 — Your CI review already reviews each of a pull request's changed files in its own pass, whi… |
| S3 | TS 1.6 · Skill 3 · p.8 | task-decomposition · S4 — An engineer asks the agent to “add comprehensive tests to our legacy billing codebase”: 18… |

## TS 1.7 — Session state (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.7 · Knowledge 1 · pp.8–9 | session-state · S2 — On Monday a developer ran a 3-hour Claude Code investigation of the payments service, in a… |
| K2 | TS 1.7 · Knowledge 2 · pp.8–9 | session-state · S2 — After a 90-minute shared analysis of a legacy billing module, the team wants to compare tw…<br>checkpoints · S2 — After a shared 40-minute analysis, a developer tried refactoring approach A, rewound, then… |
| K3 | TS 1.7 · Knowledge 3 · pp.8–9 | session-state · S4 — A developer resumes yesterday's analysis session of an order service. Overnight a teammate… |
| K4 | TS 1.7 · Knowledge 4 · pp.8–9 | session-state · S2 — Three weeks after an architecture investigation, a large refactor has rewritten about 70% … |
| S1 | TS 1.7 · Skill 1 · pp.8–9 | session-state · S2 — On Monday a developer ran a 3-hour Claude Code investigation of the payments service, in a… |
| S2 | TS 1.7 · Skill 2 · pp.8–9 | session-state · S2 — After a 90-minute shared analysis of a legacy billing module, the team wants to compare tw…<br>checkpoints · S2 — After a shared 40-minute analysis, a developer tried refactoring approach A, rewound, then… |
| S3 | TS 1.7 · Skill 3 · pp.8–9 | session-state · S2 — Three weeks after an architecture investigation, a large refactor has rewritten about 70% … |
| S4 | TS 1.7 · Skill 4 · pp.8–9 | session-state · S4 — A developer resumes yesterday's analysis session of an order service. Overnight a teammate… |

## TS 2.1 — Tool descriptions (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.1 · Knowledge 1 · p.9 | tool-calling · S3 — A research agent has two tools, analyze_content and analyze_document, both described as “A… |
| K2 | TS 2.1 · Knowledge 2 · p.9 | tool-calling · S1 — Customers say things like “order 1001”, but lookup_order accepts only IDs like ORD-1001. I… |
| K3 | TS 2.1 · Knowledge 3 · p.9 | tool-calling · S3 — A research agent has two tools, analyze_content and analyze_document, both described as “A…<br>evaluation · S3 — A team's tool-selection eval scores 100% on 200 requests, yet in production the agent rout… |
| K4 | TS 2.1 · Knowledge 4 · p.9 | tool-calling · S3 — After the team carefully rewrote every tool description, misrouting fell from 30% to 8%. T…<br>evaluation · S1 — A support agent's eval shows it picks get_customer instead of lookup_order on 48% of reque… |
| S1 | TS 2.1 · Skill 1 · p.9 | tool-calling · S1 — Customers say things like “order 1001”, but lookup_order accepts only IDs like ORD-1001. I…<br>evaluation · S1 — A support agent's eval shows it picks get_customer instead of lookup_order on 48% of reque… |
| S2 | TS 2.1 · Skill 2 · p.9 | tool-calling · S3 — In the same system, analyze_content is meant only for processing web search results, and a… |
| S3 | TS 2.1 · Skill 3 · p.9 | tool-calling · S3 — A single analyze_document tool is used to pull out figures, write summaries and check clai… |
| S4 | TS 2.1 · Skill 4 · p.9 | tool-calling · S3 — After the team carefully rewrote every tool description, misrouting fell from 30% to 8%. T… |

## TS 2.2 — Structured errors (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.2 · Knowledge 1 · pp.9–10 | mcp · S1 — A customer gives the date “next Tuesday”, and lookup_order rejects it because it expects Y… |
| K2 | TS 2.2 · Knowledge 2 · pp.9–10 | mcp · S1 — A customer gives the date “next Tuesday”, and lookup_order rejects it because it expects Y… |
| K3 | TS 2.2 · Knowledge 3 · pp.9–10 | mcp · S1 — process_refund returns isError with the text “Operation failed” for every failure. When a … |
| K4 | TS 2.2 · Knowledge 4 · pp.9–10 | mcp · S1 — process_refund returns isError with the text “Operation failed” for every failure. When a … |
| S1 | TS 2.2 · Skill 1 · pp.9–10 | mcp · S1 — A customer gives the date “next Tuesday”, and lookup_order rejects it because it expects Y… |
| S2 | TS 2.2 · Skill 2 · pp.9–10 | mcp · S1 — process_refund returns isError with the text “Operation failed” for every failure. When a … |
| S3 | TS 2.2 · Skill 3 · pp.9–10 | mcp · S3 — A research subagent's source API times out on about 5% of calls, and most timeouts succeed… |
| S4 | TS 2.2 · Skill 4 · pp.9–10 | mcp · S1 — An order-lookup tool catches every exception and returns an empty list. During a 25-minute… |

## TS 2.3 — Tool choice (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.3 · Knowledge 1 · pp.10–11 | tool-choice · S1 — A single support agent has been given 18 tools as features were added: refunds, shipping, … |
| K2 | TS 2.3 · Knowledge 2 · pp.10–11 | tool-choice · S3 — In the research system, every agent is given all 18 tools. The synthesis agent runs its ow… |
| K3 | TS 2.3 · Knowledge 3 · pp.10–11 | tool-choice · S6 — In an extraction pipeline, a validation agent checks each invoice's totals. For 90% of inv…<br>tool-choice · S1 — A single support agent has been given 18 tools as features were added: refunds, shipping, … |
| K4 | TS 2.3 · Knowledge 4 · pp.10–11 | tool-choice · S6 — An invoice-extraction pipeline defines one extraction tool, with tool_choice set to “auto”… |
| S1 | TS 2.3 · Skill 1 · pp.10–11 | tool-choice · S3 — In the research system, every agent is given all 18 tools. The synthesis agent runs its ow… |
| S2 | TS 2.3 · Skill 2 · pp.10–11 | tool-choice · S3 — A document-analysis subagent has a generic fetch_url tool. In about 1 run in 12, it fetche… |
| S3 | TS 2.3 · Skill 3 · pp.10–11 | tool-choice · S6 — In an extraction pipeline, a validation agent checks each invoice's totals. For 90% of inv… |
| S4 | TS 2.3 · Skill 4 · pp.10–11 | tool-choice · S6 — In an extraction workflow, extract_metadata must run before anything else, because later t… |
| S5 | TS 2.3 · Skill 5 · pp.10–11 | tool-choice · S6 — An invoice-extraction pipeline defines one extraction tool, with tool_choice set to “auto”… |

## TS 2.4 — MCP config (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.4 · Knowledge 1 · p.11 | mcp · S4 — The team wants all 25 developers to get the same GitHub MCP server as soon as they clone t…<br>mcp · S4 — A developer wants to try an experimental MCP server that nobody else uses and that may be … |
| K2 | TS 2.4 · Knowledge 2 · p.11 | mcp · S4 — The team wants all 25 developers to get the same GitHub MCP server as soon as they clone t… |
| K3 | TS 2.4 · Knowledge 3 · p.11 | mcp · S4 — A developer has both a GitHub MCP server and a Jira MCP server configured. To “let Claude … |
| K4 | TS 2.4 · Knowledge 4 · p.11 | mcp · S4 — Before answering any question about the analytics database, the agent makes about 12 descr… |
| S1 | TS 2.4 · Skill 1 · p.11 | mcp · S4 — The team wants all 25 developers to get the same GitHub MCP server as soon as they clone t… |
| S2 | TS 2.4 · Skill 2 · p.11 | mcp · S4 — A developer wants to try an experimental MCP server that nobody else uses and that may be … |
| S3 | TS 2.4 · Skill 3 · p.11 | mcp · S4 — Your MCP server offers find_references, which searches all 30 service repositories and ret… |
| S4 | TS 2.4 · Skill 4 · p.11 | mcp · S4 — The team needs Claude to read and update Jira tickets, and separately to run the company's… |
| S5 | TS 2.4 · Skill 5 · p.11 | mcp · S4 — Before answering any question about the analytics database, the agent makes about 12 descr… |

## TS 2.5 — Built-in tools (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.5 · Knowledge 1 · pp.11–12 | agentic-tool-surface-selection · S4 — Before removing the deprecated function legacy_price(), a developer asks the agent to find… |
| K2 | TS 2.5 · Knowledge 2 · pp.11–12 | agentic-tool-surface-selection · S4 — Before a testing-framework migration, the agent must list every React test file. They foll… |
| K3 | TS 2.5 · Knowledge 3 · pp.11–12 | agentic-tool-surface-selection · S2 — The agent must change timeout = 30 to timeout = 60 only in the [payments] section of a con… |
| K4 | TS 2.5 · Knowledge 4 · pp.11–12 | agentic-tool-surface-selection · S2 — The agent must change timeout = 30 to timeout = 60 only in the [payments] section of a con… |
| S1 | TS 2.5 · Skill 1 · pp.11–12 | agentic-tool-surface-selection · S4 — Before removing the deprecated function legacy_price(), a developer asks the agent to find… |
| S2 | TS 2.5 · Skill 2 · pp.11–12 | agentic-tool-surface-selection · S4 — Before a testing-framework migration, the agent must list every React test file. They foll… |
| S3 | TS 2.5 · Skill 3 · pp.11–12 | agentic-tool-surface-selection · S2 — The agent must change timeout = 30 to timeout = 60 only in the [payments] section of a con… |
| S4 | TS 2.5 · Skill 4 · pp.11–12 | agentic-tool-surface-selection · S4 — A new engineer asks how an order moves from checkout to fulfilment in an unfamiliar 3,000-… |
| S5 | TS 2.5 · Skill 5 · pp.11–12 | agentic-tool-surface-selection · S4 — A utils/index.ts file re-exports helpers from five internal modules. To find usages of one… |

## TS 3.1 — CLAUDE.md hierarchy (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.1 · Knowledge 1 · pp.12–13 | agent-instruction-files · S2 — In a 40-service repository, only services/payments needs extra instructions: amounts are s… |
| K2 | TS 3.1 · Knowledge 2 · pp.12–13 | agent-instruction-files · S2 — A new developer says Claude Code ignores the team's conventions (always run the linter, al… |
| K3 | TS 3.1 · Knowledge 3 · pp.12–13 | agent-instruction-files · S2 — A monorepo holds a payments package and a frontend package, maintained by different teams … |
| K4 | TS 3.1 · Knowledge 4 · pp.12–13 | claude-md-hierarchy · S2 — A project's CLAUDE.md has grown to 700 lines covering testing, API conventions and deploym… |
| S1 | TS 3.1 · Skill 1 · pp.12–13 | agent-instruction-files · S2 — A new developer says Claude Code ignores the team's conventions (always run the linter, al…<br>claude-md-hierarchy · S4 — Two engineers say Claude behaves differently on the same monorepo: in one of their session… |
| S2 | TS 3.1 · Skill 2 · pp.12–13 | agent-instruction-files · S2 — A monorepo holds a payments package and a frontend package, maintained by different teams … |
| S3 | TS 3.1 · Skill 3 · pp.12–13 | claude-md-hierarchy · S2 — A project's CLAUDE.md has grown to 700 lines covering testing, API conventions and deploym… |
| S4 | TS 3.1 · Skill 4 · pp.12–13 | agent-instruction-files · S2 — Two developers on the same repository get different behaviour on the same task: one sessio…<br>claude-md-hierarchy · S4 — Two engineers say Claude behaves differently on the same monorepo: in one of their session… |

## TS 3.2 — Commands and skills (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.2 · Knowledge 1 · p.13 | skills · S2 — A team lead created a /release-notes command in ~/.claude/commands/ and told the 12-person… |
| K2 | TS 3.2 · Knowledge 2 · p.13 | skills · S2 — A /map-dependencies skill prints about 4,000 lines of analysis into the conversation, crow… |
| K3 | TS 3.2 · Knowledge 3 · p.13 | skills · S2 — A /map-dependencies skill prints about 4,000 lines of analysis into the conversation, crow… |
| K4 | TS 3.2 · Knowledge 4 · p.13 | skills · S2 — A developer wants a terser version of the team's shared /review-pr skill for their own use… |
| S1 | TS 3.2 · Skill 1 · p.13 | skills · S2 — A team lead created a /release-notes command in ~/.claude/commands/ and told the 12-person… |
| S2 | TS 3.2 · Skill 2 · p.13 | skills · S2 — A /map-dependencies skill prints about 4,000 lines of analysis into the conversation, crow… |
| S3 | TS 3.2 · Skill 3 · p.13 | skills · S2 — A /generate-docs skill should only write documentation files, but in 3 of its last 20 runs… |
| S4 | TS 3.2 · Skill 4 · p.13 | skills · S2 — Developers keep invoking /fix-issue without the issue number. In 30% of runs Claude fixes … |
| S5 | TS 3.2 · Skill 5 · p.13 | agentic-tool-surface-selection · S2 — A team wants Claude to always use their package manager's commands (pnpm, never npm) in ev… |

## TS 3.3 — Path-specific rules (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.3 · Knowledge 1 · pp.13–14 | claude-md-hierarchy · S2 — Infrastructure conventions (tagging, naming, no hard-coded regions) apply to every Terrafo… |
| K2 | TS 3.3 · Knowledge 2 · pp.13–14 | claude-md-hierarchy · S2 — Infrastructure conventions (tagging, naming, no hard-coded regions) apply to every Terrafo… |
| K3 | TS 3.3 · Knowledge 3 · pp.13–14 | claude-md-hierarchy · S2 — A team created .claude/rules/testing.md with paths: ["tests/**/*"]. But their test files l… |
| S1 | TS 3.3 · Skill 1 · pp.13–14 | claude-md-hierarchy · S2 — Infrastructure conventions (tagging, naming, no hard-coded regions) apply to every Terrafo… |
| S2 | TS 3.3 · Skill 2 · pp.13–14 | claude-md-hierarchy · S2 — A team created .claude/rules/testing.md with paths: ["tests/**/*"]. But their test files l… |
| S3 | TS 3.3 · Skill 3 · pp.13–14 | claude-md-hierarchy · S2 — A team created .claude/rules/testing.md with paths: ["tests/**/*"]. But their test files l… |

## TS 3.4 — Plan vs direct (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.4 · Knowledge 1 · p.14 | plan-mode · S2 — A developer asks Claude Code to move a service from one ORM to another. About 60 files are… |
| K2 | TS 3.4 · Knowledge 2 · p.14 | plan-mode · S2 — A stack trace points to a missing null check on one line of one function, and the fix is o… |
| K3 | TS 3.4 · Knowledge 3 · p.14 | plan-mode · S2 — A developer asks Claude Code to move a service from one ORM to another. About 60 files are…<br>plan-mode · S2 — A team used plan mode to design a 45-file library migration and approved the plan. They ar… |
| K4 | TS 3.4 · Knowledge 4 · p.14 | plan-mode · S2 — During a multi-phase task, the main session's context fills with search output from about … |
| S1 | TS 3.4 · Skill 1 · p.14 | plan-mode · S2 — A developer asks Claude Code to move a service from one ORM to another. About 60 files are…<br>plan-mode · S2 — A team must add payments using either a hosted checkout page or an embedded card form. Eac… |
| S2 | TS 3.4 · Skill 2 · p.14 | plan-mode · S2 — A stack trace points to a missing null check on one line of one function, and the fix is o… |
| S3 | TS 3.4 · Skill 3 · p.14 | plan-mode · S2 — During a multi-phase task, the main session's context fills with search output from about … |
| S4 | TS 3.4 · Skill 4 · p.14 | plan-mode · S2 — A team used plan mode to design a 45-file library migration and approved the plan. They ar… |

## TS 3.5 — Iterative refinement (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.5 · Knowledge 1 · pp.14–15 | prompt-engineering-techniques · S2 — A developer describes in prose how Claude Code should convert API field names: snake_case … |
| K2 | TS 3.5 · Knowledge 2 · pp.14–15 | prompt-engineering-techniques · S2 — A developer asks Claude Code to fix a data migration script and replies “still broken” aft… |
| K3 | TS 3.5 · Knowledge 3 · pp.14–15 | prompt-engineering-techniques · S2 — A developer who has never built a caching layer asks Claude Code to add one to an API serv… |
| K4 | TS 3.5 · Knowledge 4 · pp.14–15 | prompt-engineering-techniques · S2 — Three bugs are open: the tax calculation depends on how the order total is rounded, and bo… |
| S1 | TS 3.5 · Skill 1 · pp.14–15 | prompt-engineering-techniques · S2 — A developer describes in prose how Claude Code should convert API field names: snake_case … |
| S2 | TS 3.5 · Skill 2 · pp.14–15 | prompt-engineering-techniques · S2 — A developer asks Claude Code to fix a data migration script and replies “still broken” aft… |
| S3 | TS 3.5 · Skill 3 · pp.14–15 | prompt-engineering-techniques · S2 — A developer who has never built a caching layer asks Claude Code to add one to an API serv… |
| S4 | TS 3.5 · Skill 4 · pp.14–15 | prompt-engineering-techniques · S2 — A migration script generated by Claude Code crashes on rows where middle_name is null, abo… |
| S5 | TS 3.5 · Skill 5 · pp.14–15 | prompt-engineering-techniques · S2 — Three bugs are open: the tax calculation depends on how the order total is rounded, and bo… |

## TS 3.6 — CI/CD (0/9 bullets) — *no built concept yet*

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.6 · Knowledge 1 · pp.15–16 | ⚠️ **gap** |
| K2 | TS 3.6 · Knowledge 2 · pp.15–16 | ⚠️ **gap** |
| K3 | TS 3.6 · Knowledge 3 · pp.15–16 | ⚠️ **gap** |
| K4 | TS 3.6 · Knowledge 4 · pp.15–16 | ⚠️ **gap** |
| S1 | TS 3.6 · Skill 1 · pp.15–16 | ⚠️ **gap** |
| S2 | TS 3.6 · Skill 2 · pp.15–16 | ⚠️ **gap** |
| S3 | TS 3.6 · Skill 3 · pp.15–16 | ⚠️ **gap** |
| S4 | TS 3.6 · Skill 4 · pp.15–16 | ⚠️ **gap** |
| S5 | TS 3.6 · Skill 5 · pp.15–16 | ⚠️ **gap** |

## TS 4.1 — Explicit criteria (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.1 · Knowledge 1 · p.16 | system-prompts · S5 — Your CI reviewer flags about 40 code comments a week as “inaccurate” when they are merely … |
| K2 | TS 4.1 · Knowledge 2 · p.16 | system-prompts · S5 — A reviewer's prompt says “be conservative and only report issues you're highly confident a… |
| K3 | TS 4.1 · Knowledge 3 · p.16 | system-prompts · S5 — Developers dismiss about 80% of the reviewer's “performance” findings. A survey shows they… |
| S1 | TS 4.1 · Skill 1 · p.16 | system-prompts · S5 — Your CI reviewer flags about 40 code comments a week as “inaccurate” when they are merely …<br>system-prompts · S5 — A reviewer's prompt says “be conservative and only report issues you're highly confident a…<br>system-prompts · S5 — The team deliberately catches broad exceptions in its plugin loader, a documented local pa… |
| S2 | TS 4.1 · Skill 2 · p.16 | system-prompts · S5 — Developers dismiss about 80% of the reviewer's “performance” findings. A survey shows they… |
| S3 | TS 4.1 · Skill 3 · p.16 | system-prompts · S5 — Two identical unchecked-null bugs in different files come back as “critical” in one review… |

## TS 4.2 — Few-shot (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.2 · Knowledge 1 · pp.16–17 | prompt-engineering-techniques · S5 — A CI review prompt lists the four fields every finding needs (location, issue, severity, s… |
| K2 | TS 4.2 · Knowledge 2 · pp.16–17 | prompt-engineering-techniques · S1 — A support agent hesitates between get_customer and lookup_order on requests like “it's abo… |
| K3 | TS 4.2 · Knowledge 3 · pp.16–17 | prompt-engineering-techniques · S1 — Every time the agent mishandles a new kind of ambiguous request, the team adds another rul… |
| K4 | TS 4.2 · Knowledge 4 · pp.16–17 | prompt-engineering-techniques · S6 — Extracting product dimensions, the pipeline returns null for required measurements in abou… |
| S1 | TS 4.2 · Skill 1 · pp.16–17 | prompt-engineering-techniques · S1 — A support agent hesitates between get_customer and lookup_order on requests like “it's abo… |
| S2 | TS 4.2 · Skill 2 · pp.16–17 | prompt-engineering-techniques · S5 — A CI review prompt lists the four fields every finding needs (location, issue, severity, s… |
| S3 | TS 4.2 · Skill 3 · pp.16–17 | prompt-engineering-techniques · S5 — The CI reviewer flags the team's standard retry decorator as “unsafe error handling” on ab… |
| S4 | TS 4.2 · Skill 4 · pp.16–17 | prompt-engineering-techniques · S6 — A citation extractor works on papers with a bibliography at the end, but misses or duplica… |
| S5 | TS 4.2 · Skill 5 · pp.16–17 | prompt-engineering-techniques · S6 — Extracting product dimensions, the pipeline returns null for required measurements in abou… |

## TS 4.3 — Structured output (10/10 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.3 · Knowledge 1 · pp.17–18 | structured-outputs · S6 — An extraction service asks Claude to “reply with JSON only” and parses the text. About 2% … |
| K2 | TS 4.3 · Knowledge 2 · pp.17–18 | tool-choice · S6 — An invoice-extraction pipeline defines one extraction tool, with tool_choice set to “auto”…<br>tool-choice · S6 — Incoming documents may be invoices, receipts or contracts, each with its own extraction to… |
| K3 | TS 4.3 · Knowledge 3 · pp.17–18 | structured-outputs · S6 — The pipeline now uses strict tool use, and every invoice extraction is valid JSON that mat… |
| K4 | TS 4.3 · Knowledge 4 · pp.17–18 | tool-choice · S6 — An extraction schema marks tax_id as a required string. An audit of 500 invoices finds pla…<br>tool-choice · S6 — A document_type enum lists invoice, receipt and contract. New document kinds, such as cred… |
| S1 | TS 4.3 · Skill 1 · pp.17–18 | structured-outputs · S6 — An extraction service asks Claude to “reply with JSON only” and parses the text. About 2% … |
| S2 | TS 4.3 · Skill 2 · pp.17–18 | tool-choice · S6 — Incoming documents may be invoices, receipts or contracts, each with its own extraction to… |
| S3 | TS 4.3 · Skill 3 · pp.17–18 | tool-choice · S6 — In an extraction workflow, extract_metadata must run before anything else, because later t… |
| S4 | TS 4.3 · Skill 4 · pp.17–18 | tool-choice · S6 — An extraction schema marks tax_id as a required string. An audit of 500 invoices finds pla… |
| S5 | TS 4.3 · Skill 5 · pp.17–18 | tool-choice · S6 — A document_type enum lists invoice, receipt and contract. New document kinds, such as cred… |
| S6 | TS 4.3 · Skill 6 · pp.17–18 | structured-outputs · S6 — Due dates arrive as “05/04/2026” (UK invoices), “April 5th” and “2026-04-05”, and about 6%… |

## TS 4.4 — Validation-retry (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.4 · Knowledge 1 · p.18 | structured-outputs · S6 — When validation fails, the pipeline retries with “The previous output was invalid, please … |
| K2 | TS 4.4 · Knowledge 2 · p.18 | structured-outputs · S6 — Invoices often say “PO: see attached purchase order”, but the attachment is never sent to … |
| K3 | TS 4.4 · Knowledge 3 · p.18 | structured-outputs · S5 — Developers dismiss about 35% of the CI reviewer's findings, but the team can't tell which … |
| K4 | TS 4.4 · Knowledge 4 · p.18 | structured-outputs · S6 — The pipeline now uses strict tool use, and every invoice extraction is valid JSON that mat… |
| S1 | TS 4.4 · Skill 1 · p.18 | structured-outputs · S6 — When validation fails, the pipeline retries with “The previous output was invalid, please … |
| S2 | TS 4.4 · Skill 2 · p.18 | structured-outputs · S6 — Invoices often say “PO: see attached purchase order”, but the attachment is never sent to … |
| S3 | TS 4.4 · Skill 3 · p.18 | structured-outputs · S5 — Developers dismiss about 35% of the CI reviewer's findings, but the team can't tell which … |
| S4 | TS 4.4 · Skill 4 · p.18 | structured-outputs · S6 — Some invoices contain their own arithmetic errors, and some list a summary total that diff… |

## TS 4.5 — Batch (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.5 · Knowledge 1 · pp.18–19 | batch-api · S1 — Finance asks to move a weekly compliance audit of about 20,000 support transcripts to the … |
| K2 | TS 4.5 · Knowledge 2 · pp.18–19 | batch-api · S1 — A support team runs two Claude workloads: a live refund-eligibility check that the agent c…<br>batch-api · S1 — Finance asks to move a weekly compliance audit of about 20,000 support transcripts to the … |
| K3 | TS 4.5 · Knowledge 3 · pp.18–19 | batch-api · S1 — A nightly refund-review job needs the model to call lookup_order, see the result, then dec… |
| K4 | TS 4.5 · Knowledge 4 · pp.18–19 | batch-api · S6 — A batch of 500 document extractions comes back, and the team pairs each result with its in… |
| S1 | TS 4.5 · Skill 1 · pp.18–19 | batch-api · S1 — A support team runs two Claude workloads: a live refund-eligibility check that the agent c… |
| S2 | TS 4.5 · Skill 2 · pp.18–19 | batch-api · S6 — Documents arrive throughout the day, and each must be extracted within 30 hours of arrivin… |
| S3 | TS 4.5 · Skill 3 · pp.18–19 | batch-api · S6 — In a nightly batch of 2,000 extractions, 40 requests failed, 12 of them because their docu… |
| S4 | TS 4.5 · Skill 4 · pp.18–19 | batch-api · S6 — A team is about to batch-process 100,000 archived contracts with a brand-new extraction pr… |

## TS 4.6 — Multi-pass review (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.6 · Knowledge 1 · p.19 | multi-pass-review-architectures · S2 — Claude Code generates a pagination feature, and in the same session the developer asks it … |
| K2 | TS 4.6 · Knowledge 2 · p.19 | multi-pass-review-architectures · S2 — Claude Code generates a pagination feature, and in the same session the developer asks it … |
| K3 | TS 4.6 · Knowledge 3 · p.19 | multi-pass-review-architectures · S5 — A single review pass over a 30-file pull request misses issues in the middle files, and in… |
| S1 | TS 4.6 · Skill 1 · p.19 | multi-pass-review-architectures · S2 — Claude Code generates a pagination feature, and in the same session the developer asks it … |
| S2 | TS 4.6 · Skill 2 · p.19 | multi-pass-review-architectures · S5 — A single review pass over a 30-file pull request misses issues in the middle files, and in…<br>multi-pass-review-architectures · S5 — Per-file review passes now find every local bug in a PR. But file_04 renames total to amou… |
| S3 | TS 4.6 · Skill 3 · p.19 | multi-pass-review-architectures · S5 — A CI reviewer posts every finding as a PR comment, about 25 per PR, and developers now ign… |

## TS 5.1 — Context preservation (10/10 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.1 · Knowledge 1 · pp.19–20 | attention-engineering · S1 — To save space, a long support conversation is summarised every ten turns. After three summ…<br>case-facts-block · S1 — A support agent summarises the conversation every ten turns and keeps a case-facts block o… |
| K2 | TS 5.1 · Knowledge 2 · pp.19–20 | attention-engineering · S3 — A research coordinator concatenates nine subagents' reports (about 60,000 tokens) and asks… |
| K3 | TS 5.1 · Knowledge 3 · pp.19–20 | attention-engineering · S1 — Each lookup_order call returns 40+ fields (warehouse codes, carrier events, internal flags…<br>context-window · S4 — A log-investigation agent reads entire 2,000-line log files at every step, although it onl… |
| K4 | TS 5.1 · Knowledge 4 · pp.19–20 | attention-engineering · S1 — A developer builds a support chat on the Messages API and, to save tokens, sends only the …<br>context-window · S1 — To save tokens, a support chat built on the Messages API sends only the last three message… |
| S1 | TS 5.1 · Skill 1 · pp.19–20 | attention-engineering · S1 — To save space, a long support conversation is summarised every ten turns. After three summ…<br>case-facts-block · S1 — A support agent summarises the conversation every ten turns and keeps a case-facts block o…<br>case-facts-block · S1 — A team adds a “case facts” message at the start of each support conversation. Once a conve…<br>case-facts-block · S1 — An agent records a refund as “pending” in its case-facts block. Twenty minutes later a loo… |
| S2 | TS 5.1 · Skill 2 · pp.19–20 | attention-engineering · S1 — In one session a customer raises problems with three orders. In about 1 of 8 such conversa…<br>case-facts-block · S1 — A customer raises a billing dispute and two returns in one conversation. The agent's case-… |
| S3 | TS 5.1 · Skill 3 · pp.19–20 | attention-engineering · S1 — Each lookup_order call returns 40+ fields (warehouse codes, carrier events, internal flags…<br>context-window · S4 — A log-investigation agent reads entire 2,000-line log files at every step, although it onl… |
| S4 | TS 5.1 · Skill 4 · pp.19–20 | attention-engineering · S3 — A research coordinator concatenates nine subagents' reports (about 60,000 tokens) and asks… |
| S5 | TS 5.1 · Skill 5 · pp.19–20 | subagent-state-handoff · S3 — A report on remote-work productivity says “studies disagree sharply”, presenting a 38% gai… |
| S6 | TS 5.1 · Skill 6 · pp.19–20 | subagent-state-handoff · S3 — The synthesis subagent has a 6,000-token input budget. Four document-analysis subagents ea…<br>context-window · S3 — A report agent can fit about 6,000 tokens of input. Four document-analysis subagents each … |

## TS 5.2 — Escalation (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.2 · Knowledge 1 · pp.20–21 | escalation · S1 — Your support agent escalates about 30% of conversations. A review of 200 escalations finds… |
| K2 | TS 5.2 · Knowledge 2 · pp.20–21 | escalation · S1 — A customer opens with: “I don't want a bot. Put me through to a person now.” The issue loo… |
| K3 | TS 5.2 · Knowledge 3 · pp.20–21 | escalation · S1 — To cut unnecessary escalations, a team proposes escalating only when the model's self-repo… |
| K4 | TS 5.2 · Knowledge 4 · pp.20–21 | escalation · S1 — get_customer returns two accounts for the name “Customer A”: one in Leeds and one in Leice… |
| S1 | TS 5.2 · Skill 1 · pp.20–21 | escalation · S1 — Your support agent escalates about 30% of conversations. A review of 200 escalations finds… |
| S2 | TS 5.2 · Skill 2 · pp.20–21 | escalation · S1 — A customer opens with: “I don't want a bot. Put me through to a person now.” The issue loo… |
| S3 | TS 5.2 · Skill 3 · pp.20–21 | escalation · S1 — A customer is clearly frustrated after a delivery arrived 5 days late, but hasn't asked fo… |
| S4 | TS 5.2 · Skill 4 · pp.20–21 | escalation · S1 — A customer asks the agent to match a competitor's price that is £40 lower. Your refund pol… |
| S5 | TS 5.2 · Skill 5 · pp.20–21 | escalation · S1 — get_customer returns two accounts for the name “Customer A”: one in Leeds and one in Leice… |

## TS 5.3 — Error propagation (0/8 bullets) — *no built concept yet*

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.3 · Knowledge 1 · p.21 | ⚠️ **gap** |
| K2 | TS 5.3 · Knowledge 2 · p.21 | ⚠️ **gap** |
| K3 | TS 5.3 · Knowledge 3 · p.21 | ⚠️ **gap** |
| K4 | TS 5.3 · Knowledge 4 · p.21 | ⚠️ **gap** |
| S1 | TS 5.3 · Skill 1 · p.21 | ⚠️ **gap** |
| S2 | TS 5.3 · Skill 2 · p.21 | ⚠️ **gap** |
| S3 | TS 5.3 · Skill 3 · p.21 | ⚠️ **gap** |
| S4 | TS 5.3 · Skill 4 · p.21 | ⚠️ **gap** |

## TS 5.4 — Codebase exploration (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.4 · Knowledge 1 · pp.21–22 | session-state · S4 — Two hours into a codebase exploration, the agent's answers start contradicting answers it …<br>context-window · S2 — Two hours into a refactor in Claude Code, the context is 95% full of search output, and an… |
| K2 | TS 5.4 · Knowledge 2 · pp.21–22 | checkpoints · S4 — A developer plans to /clear the session before the next part of a long investigation. The … |
| K3 | TS 5.4 · Knowledge 3 · pp.21–22 | context-window · S4 — An onboarding agent answering “how does billing work?” reads file after file of a 5,000-fi… |
| K4 | TS 5.4 · Knowledge 4 · pp.21–22 | session-state · S3 — A research coordinator runs three analysis agents over a 400-document corpus. After a cras…<br>subagent-state-handoff · S4 — A nightly job runs four exploration subagents over a large monorepo, and each takes about … |
| S1 | TS 5.4 · Skill 1 · pp.21–22 | context-window · S4 — An onboarding agent answering “how does billing work?” reads file after file of a 5,000-fi… |
| S2 | TS 5.4 · Skill 2 · pp.21–22 | session-state · S4 — Two hours into a codebase exploration, the agent's answers start contradicting answers it …<br>checkpoints · S4 — A developer plans to /clear the session before the next part of a long investigation. The … |
| S3 | TS 5.4 · Skill 3 · pp.21–22 | session-state · S4 — A migration investigation has three phases: map dependencies, find risky call sites, then …<br>subagent-state-handoff · S4 — A coordinator agent migrates a legacy billing module in two phases. Phase 1 subagents mapp… |
| S4 | TS 5.4 · Skill 4 · pp.21–22 | session-state · S3 — A research coordinator runs three analysis agents over a 400-document corpus. After a cras…<br>subagent-state-handoff · S4 — A nightly job runs four exploration subagents over a large monorepo, and each takes about … |
| S5 | TS 5.4 · Skill 5 · pp.21–22 | checkpoints · S2 — Two hours into exploring a legacy codebase, the session is full of verbose search and file…<br>context-window · S2 — Two hours into a refactor in Claude Code, the context is 95% full of search output, and an… |

## TS 5.5 — Human review (0/8 bullets) — *no built concept yet*

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.5 · Knowledge 1 · pp.22–23 | ⚠️ **gap** |
| K2 | TS 5.5 · Knowledge 2 · pp.22–23 | ⚠️ **gap** |
| K3 | TS 5.5 · Knowledge 3 · pp.22–23 | ⚠️ **gap** |
| K4 | TS 5.5 · Knowledge 4 · pp.22–23 | ⚠️ **gap** |
| S1 | TS 5.5 · Skill 1 · pp.22–23 | ⚠️ **gap** |
| S2 | TS 5.5 · Skill 2 · pp.22–23 | ⚠️ **gap** |
| S3 | TS 5.5 · Skill 3 · pp.22–23 | ⚠️ **gap** |
| S4 | TS 5.5 · Skill 4 · pp.22–23 | ⚠️ **gap** |

## TS 5.6 — Provenance (2/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.6 · Knowledge 1 · p.23 | subagent-state-handoff · S3 — The synthesis subagent now receives all 40 findings, and the reports read well. However, a… |
| K2 | TS 5.6 · Knowledge 2 · p.23 | ⚠️ **gap** |
| K3 | TS 5.6 · Knowledge 3 · p.23 | ⚠️ **gap** |
| K4 | TS 5.6 · Knowledge 4 · p.23 | ⚠️ **gap** |
| S1 | TS 5.6 · Skill 1 · p.23 | ⚠️ **gap** |
| S2 | TS 5.6 · Skill 2 · p.23 | ⚠️ **gap** |
| S3 | TS 5.6 · Skill 3 · p.23 | ⚠️ **gap** |
| S4 | TS 5.6 · Skill 4 · p.23 | subagent-state-handoff · S3 — A report on remote-work productivity says “studies disagree sharply”, presenting a 38% gai… |
| S5 | TS 5.6 · Skill 5 · p.23 | ⚠️ **gap** |
