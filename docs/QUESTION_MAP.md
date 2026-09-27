# Question Map — every bank question pinned to the exam guide

Auto-generated from `utils/question_bank.py` (which collects each built concept page's practice items). Regenerate, don't hand-edit. Every bank question is set in one of the guide's six scenarios (§5, pp.3–4) and pinned to the exact Knowledge/Skill bullet(s) it tests (§6). A wrong pin fails at import (`Question.__post_init__` → `guide_index.point_ref`). Questions are original — never real exam items — and `reviewed_by_user: False` until the owner signs them off.

**147 bank questions.** Guide bullets covered in the task statements built so far: **206 / 206**. Whole guide: 206 / 240 (task statements with no built concept yet are listed as gaps below).

| # | Scenario (primary) | Questions |
|---|---|---|
| 1 | Customer Support Resolution Agent | 38 |
| 2 | Code Generation with Claude Code | 31 |
| 3 | Multi-Agent Research System | 25 |
| 4 | Developer Productivity with Claude | 22 |
| 5 | Claude Code for Continuous Integration | 14 |
| 6 | Structured Data Extraction | 17 |

**Correct-answer position** (should be roughly even): A 36 · B 33 · C 39 · D 39


## TS 1.1 — Agentic loops (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.1 · Knowledge 1 · p.5 | stop-reason · S1 — Mid-conversation, your support agent returns a response with stop_reason “tool_use”. Its c…<br>stop-reason · S4 — A codebase-exploration agent requests Grep, your code runs it, and then you send the next … |
| K2 | TS 1.1 · Knowledge 2 · p.5 | agentic-loops · S1 — After each tool call your loop executes the tool and prints the result, then sends the nex…<br>stop-reason · S4 — A codebase-exploration agent requests Grep, your code runs it, and then you send the next … |
| K3 | TS 1.1 · Knowledge 3 · p.5 | stop-reason · S1 — To make the support agent “predictable”, a team hard-codes every request to run get_custom… |
| S1 | TS 1.1 · Skill 1 · p.5 | agentic-loops · S4 — A migration agent needs anywhere from 2 to 15 tool calls depending on the repository. The …<br>stop-reason · S1 — Mid-conversation, your support agent returns a response with stop_reason “tool_use”. Its c… |
| S2 | TS 1.1 · Skill 2 · p.5 | agentic-loops · S1 — After each tool call your loop executes the tool and prints the result, then sends the nex… |
| S3 | TS 1.1 · Skill 3 · p.5 | agentic-loops · S1 — Your support agent's loop exits as soon as the assistant's reply contains the word “resolv…<br>agentic-loops · S4 — A migration agent needs anywhere from 2 to 15 tool calls depending on the repository. The …<br>stop-reason · S1 — A team's loop decides the agent is finished whenever a response contains a text block. Ord… |

## TS 1.2 — Coordinator-subagent (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.2 · Knowledge 1 · pp.5–6 | subagents · S3 — Your research system has a coordinator and four subagents. To save a round trip, a develop… |
| K2 | TS 1.2 · Knowledge 2 · pp.5–6 | subagents · S3 — The coordinator's prompt to each search subagent is a numbered procedure: search site A, t… |
| K3 | TS 1.2 · Knowledge 3 · pp.5–6 | subagents · S3 — Users ask everything from “What year was the EU ETS launched?” to “Compare carbon-pricing … |
| K4 | TS 1.2 · Knowledge 4 · pp.5–6 | subagents · S3 — Asked to research “renewable energy adoption in Europe”, the system returns a well-cited r… |
| S1 | TS 1.2 · Skill 1 · pp.5–6 | subagents · S3 — Users ask everything from “What year was the EU ETS launched?” to “Compare carbon-pricing … |
| S2 | TS 1.2 · Skill 2 · pp.5–6 | subagents · S3 — Two search subagents are given the same topic brief. Their results overlap by about 70%, a… |
| S3 | TS 1.2 · Skill 3 · pp.5–6 | subagents · S3 — A first draft of a report covers regulation and market size well but has almost nothing on… |
| S4 | TS 1.2 · Skill 4 · pp.5–6 | subagents · S3 — Your research system has a coordinator and four subagents. To save a round trip, a develop… |

## TS 1.3 — Subagent invocation (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.3 · Knowledge 1 · pp.6–7 | subagents · S3 — A coordinator built with the Agent SDK has three well-described subagents configured, yet … |
| K2 | TS 1.3 · Knowledge 2 · pp.6–7 | subagent-state-handoff · S3 — The coordinator spawns the synthesis subagent with the prompt “Using the research results … |
| K3 | TS 1.3 · Knowledge 3 · pp.6–7 | subagents · S3 — The coordinator keeps sending document-analysis work to the web-search subagent. The team … |
| K4 | TS 1.3 · Knowledge 4 · pp.6–7 | session-state · S2 — After a shared analysis of a legacy billing module, the team wants to try two refactoring … |
| S1 | TS 1.3 · Skill 1 · pp.6–7 | subagent-state-handoff · S3 — The coordinator spawns the synthesis subagent with the prompt “Using the research results … |
| S2 | TS 1.3 · Skill 2 · pp.6–7 | subagent-state-handoff · S3 — The synthesis subagent writes a fluent report, but none of its claims can be traced to a s… |
| S3 | TS 1.3 · Skill 3 · pp.6–7 | subagents · S3 — To research three independent regions, the coordinator requests one search subagent, waits… |
| S4 | TS 1.3 · Skill 4 · pp.6–7 | subagents · S3 — The coordinator's prompt to each search subagent is a numbered procedure: search site A, t… |

## TS 1.4 — Enforcement & handoff (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.4 · Knowledge 1 · p.7 | stop-reason · S1 — To make the support agent “predictable”, a team hard-codes every request to run get_custom…<br>escalation · S1 — The system prompt says “always verify the customer with get_customer before issuing a refu… |
| K2 | TS 1.4 · Knowledge 2 · p.7 | escalation · S1 — The system prompt says “always verify the customer with get_customer before issuing a refu… |
| K3 | TS 1.4 · Knowledge 3 · p.7 | escalation · S1 — Human agents complain that escalated tickets arrive as “Customer needs help, see chat”, an… |
| S1 | TS 1.4 · Skill 1 · p.7 | escalation · S1 — The system prompt says “always verify the customer with get_customer before issuing a refu… |
| S2 | TS 1.4 · Skill 2 · p.7 | escalation · S1 — One message from a customer covers three things: a damaged blender, a double charge on las… |
| S3 | TS 1.4 · Skill 3 · p.7 | escalation · S1 — Human agents complain that escalated tickets arrive as “Customer needs help, see chat”, an… |

## TS 1.5 — Hooks (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.5 · Knowledge 1 · pp.7–8 | hooks · S1 — Two MCP tools return dates differently, one as Unix seconds and one as ISO 8601, and a thi…<br>hooks · S1 — get_customer returns full card numbers and dates of birth, which the model never needs and… |
| K2 | TS 1.5 · Knowledge 2 · pp.7–8 | hooks · S1 — Company policy says refunds above $500 must go to a human. The support agent's system prom… |
| K3 | TS 1.5 · Knowledge 3 · pp.7–8 | hooks · S1 — Company policy says refunds above $500 must go to a human. The support agent's system prom…<br>hooks · S1 — Which of these support-agent requirements is best handled by a prompt instruction rather t…<br>hooks · S1 — get_customer returns full card numbers and dates of birth, which the model never needs and… |
| S1 | TS 1.5 · Skill 1 · pp.7–8 | hooks · S1 — Two MCP tools return dates differently, one as Unix seconds and one as ISO 8601, and a thi… |
| S2 | TS 1.5 · Skill 2 · pp.7–8 | hooks · S1 — Company policy says refunds above $500 must go to a human. The support agent's system prom…<br>hooks · S1 — A PreToolUse hook now blocks refunds over $500. But when blocked, the agent retries the sa… |
| S3 | TS 1.5 · Skill 3 · pp.7–8 | hooks · S1 — Company policy says refunds above $500 must go to a human. The support agent's system prom…<br>hooks · S1 — Which of these support-agent requirements is best handled by a prompt instruction rather t… |

## TS 1.6 — Task decomposition (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.6 · Knowledge 1 · p.8 | task-decomposition · S5 — A team has two workflows. Workflow 1: every pull request gets the same security, style and… |
| K2 | TS 1.6 · Knowledge 2 · p.8 | task-decomposition · S5 — Your CI review step sends one prompt with all 20 changed files of a pull request. It catch… |
| K3 | TS 1.6 · Knowledge 3 · p.8 | task-decomposition · S4 — An engineer asks the agent to “add comprehensive tests to our legacy billing codebase”. No…<br>task-decomposition · S4 — An agent investigating a production memory leak was given a fixed plan: profile service A,… |
| S1 | TS 1.6 · Skill 1 · p.8 | task-decomposition · S5 — A team has two workflows. Workflow 1: every pull request gets the same security, style and… |
| S2 | TS 1.6 · Skill 2 · p.8 | task-decomposition · S5 — Your CI review step sends one prompt with all 20 changed files of a pull request. It catch… |
| S3 | TS 1.6 · Skill 3 · p.8 | task-decomposition · S4 — An engineer asks the agent to “add comprehensive tests to our legacy billing codebase”. No… |

## TS 1.7 — Session state (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 1.7 · Knowledge 1 · pp.8–9 | session-state · S2 — On Monday a developer ran a long Claude Code investigation of the payments service, in a s… |
| K2 | TS 1.7 · Knowledge 2 · pp.8–9 | session-state · S2 — After a shared analysis of a legacy billing module, the team wants to try two refactoring …<br>checkpoints · S2 — After a shared analysis, a developer tries refactoring approach A, rewinds, tries approach… |
| K3 | TS 1.7 · Knowledge 3 · pp.8–9 | session-state · S4 — A developer resumes yesterday's analysis session of an order service. Overnight a teammate… |
| K4 | TS 1.7 · Knowledge 4 · pp.8–9 | session-state · S2 — Three weeks after an architecture investigation, a large refactor has rewritten most of th… |
| S1 | TS 1.7 · Skill 1 · pp.8–9 | session-state · S2 — On Monday a developer ran a long Claude Code investigation of the payments service, in a s… |
| S2 | TS 1.7 · Skill 2 · pp.8–9 | session-state · S2 — After a shared analysis of a legacy billing module, the team wants to try two refactoring …<br>checkpoints · S2 — After a shared analysis, a developer tries refactoring approach A, rewinds, tries approach… |
| S3 | TS 1.7 · Skill 3 · pp.8–9 | session-state · S2 — Three weeks after an architecture investigation, a large refactor has rewritten most of th… |
| S4 | TS 1.7 · Skill 4 · pp.8–9 | session-state · S4 — A developer resumes yesterday's analysis session of an order service. Overnight a teammate… |

## TS 2.1 — Tool descriptions (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.1 · Knowledge 1 · p.9 | tool-calling · S3 — A research agent has two tools, analyze_content and analyze_document, both described as “A… |
| K2 | TS 2.1 · Knowledge 2 · p.9 | tool-calling · S1 — Customers say things like “order 1001”, but lookup_order only accepts ids like ORD-1001. L… |
| K3 | TS 2.1 · Knowledge 3 · p.9 | tool-calling · S3 — A research agent has two tools, analyze_content and analyze_document, both described as “A…<br>evaluation · S3 — A team's tool-selection eval scores 100% on 200 requests, yet in production the agent keep… |
| K4 | TS 2.1 · Knowledge 4 · p.9 | tool-calling · S3 — Tool descriptions were carefully rewritten, yet any request mentioning a “report”, such as…<br>evaluation · S1 — A support agent's eval shows it picks get_customer instead of lookup_order on about half t… |
| S1 | TS 2.1 · Skill 1 · p.9 | tool-calling · S1 — Customers say things like “order 1001”, but lookup_order only accepts ids like ORD-1001. L…<br>evaluation · S1 — A support agent's eval shows it picks get_customer instead of lookup_order on about half t… |
| S2 | TS 2.1 · Skill 2 · p.9 | tool-calling · S3 — In the same system, analyze_content is actually only for processing web search results, an… |
| S3 | TS 2.1 · Skill 3 · p.9 | tool-calling · S3 — A single analyze_document tool is used to pull out figures, write summaries and check clai… |
| S4 | TS 2.1 · Skill 4 · p.9 | tool-calling · S3 — Tool descriptions were carefully rewritten, yet any request mentioning a “report”, such as… |

## TS 2.2 — Structured errors (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.2 · Knowledge 1 · pp.9–10 | mcp · S1 — A customer gives the date “next Tuesday”, and lookup_order rejects it because it expects Y… |
| K2 | TS 2.2 · Knowledge 2 · pp.9–10 | mcp · S1 — A customer gives the date “next Tuesday”, and lookup_order rejects it because it expects Y… |
| K3 | TS 2.2 · Knowledge 3 · pp.9–10 | mcp · S1 — process_refund returns isError with the text “Operation failed” for every failure. When a … |
| K4 | TS 2.2 · Knowledge 4 · pp.9–10 | mcp · S1 — process_refund returns isError with the text “Operation failed” for every failure. When a … |
| S1 | TS 2.2 · Skill 1 · pp.9–10 | mcp · S1 — A customer gives the date “next Tuesday”, and lookup_order rejects it because it expects Y… |
| S2 | TS 2.2 · Skill 2 · pp.9–10 | mcp · S1 — process_refund returns isError with the text “Operation failed” for every failure. When a … |
| S3 | TS 2.2 · Skill 3 · pp.9–10 | mcp · S3 — A research subagent's source API times out now and then. Currently every timeout is passed… |
| S4 | TS 2.2 · Skill 4 · pp.9–10 | mcp · S1 — An order-lookup tool catches every exception and returns an empty list. When the order dat… |

## TS 2.3 — Tool choice (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.3 · Knowledge 1 · pp.10–11 | tool-choice · S1 — A single support agent was given 18 tools as features were added: refunds, shipping, loyal… |
| K2 | TS 2.3 · Knowledge 2 · pp.10–11 | tool-choice · S3 — In the research system, every agent gets all 18 tools. The synthesis agent keeps running w… |
| K3 | TS 2.3 · Knowledge 3 · pp.10–11 | tool-choice · S3 — After scoping, the synthesis agent often needs to check a single fact (a date, a figure) a…<br>tool-choice · S1 — A single support agent was given 18 tools as features were added: refunds, shipping, loyal… |
| K4 | TS 2.3 · Knowledge 4 · pp.10–11 | tool-choice · S6 — An invoice-extraction pipeline defines one extraction tool, but on short or odd documents … |
| S1 | TS 2.3 · Skill 1 · pp.10–11 | tool-choice · S3 — In the research system, every agent gets all 18 tools. The synthesis agent keeps running w… |
| S2 | TS 2.3 · Skill 2 · pp.10–11 | tool-choice · S3 — A document-analysis subagent has a generic fetch_url tool. It sometimes fetches unrelated … |
| S3 | TS 2.3 · Skill 3 · pp.10–11 | tool-choice · S3 — After scoping, the synthesis agent often needs to check a single fact (a date, a figure) a… |
| S4 | TS 2.3 · Skill 4 · pp.10–11 | tool-choice · S6 — In an extraction workflow, extract_metadata must always run first. After that, the model s… |
| S5 | TS 2.3 · Skill 5 · pp.10–11 | tool-choice · S6 — An invoice-extraction pipeline defines one extraction tool, but on short or odd documents … |

## TS 2.4 — MCP config (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.4 · Knowledge 1 · p.11 | mcp · S4 — The team wants every developer to get the same GitHub MCP server as soon as they clone the…<br>mcp · S4 — A developer wants to try an experimental MCP server that nobody else uses yet and that mig… |
| K2 | TS 2.4 · Knowledge 2 · p.11 | mcp · S4 — The team wants every developer to get the same GitHub MCP server as soon as they clone the… |
| K3 | TS 2.4 · Knowledge 3 · p.11 | mcp · S4 — A developer has both a GitHub MCP server and a Jira MCP server configured. To “let Claude … |
| K4 | TS 2.4 · Knowledge 4 · p.11 | mcp · S4 — Before answering any question about the analytics database, the agent makes a dozen descri… |
| S1 | TS 2.4 · Skill 1 · p.11 | mcp · S4 — The team wants every developer to get the same GitHub MCP server as soon as they clone the… |
| S2 | TS 2.4 · Skill 2 · p.11 | mcp · S4 — A developer wants to try an experimental MCP server that nobody else uses yet and that mig… |
| S3 | TS 2.4 · Skill 3 · p.11 | mcp · S4 — Your MCP server has find_references, which searches across all service repositories and re… |
| S4 | TS 2.4 · Skill 4 · p.11 | mcp · S4 — The team needs Claude to read and update Jira tickets, and separately to run the company's… |
| S5 | TS 2.4 · Skill 5 · p.11 | mcp · S4 — Before answering any question about the analytics database, the agent makes a dozen descri… |

## TS 2.5 — Built-in tools (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 2.5 · Knowledge 1 · pp.11–12 | agentic-tool-surface-selection · S4 — A developer asks the agent to find every place the deprecated function legacy_price() is c… |
| K2 | TS 2.5 · Knowledge 2 · pp.11–12 | agentic-tool-surface-selection · S4 — Before a testing-framework migration, the agent must list every React test file (they foll… |
| K3 | TS 2.5 · Knowledge 3 · pp.11–12 | agentic-tool-surface-selection · S2 — The agent tries to change timeout = 30 to timeout = 60 in one section of a config file, bu… |
| K4 | TS 2.5 · Knowledge 4 · pp.11–12 | agentic-tool-surface-selection · S2 — The agent tries to change timeout = 30 to timeout = 60 in one section of a config file, bu… |
| S1 | TS 2.5 · Skill 1 · pp.11–12 | agentic-tool-surface-selection · S4 — A developer asks the agent to find every place the deprecated function legacy_price() is c… |
| S2 | TS 2.5 · Skill 2 · pp.11–12 | agentic-tool-surface-selection · S4 — Before a testing-framework migration, the agent must list every React test file (they foll… |
| S3 | TS 2.5 · Skill 3 · pp.11–12 | agentic-tool-surface-selection · S2 — The agent tries to change timeout = 30 to timeout = 60 in one section of a config file, bu… |
| S4 | TS 2.5 · Skill 4 · pp.11–12 | agentic-tool-surface-selection · S4 — A new engineer asks how an order moves from checkout to fulfilment in an unfamiliar codeba… |
| S5 | TS 2.5 · Skill 5 · pp.11–12 | agentic-tool-surface-selection · S4 — A utils/index.ts file re-exports helpers from five internal modules. The agent searched fo… |

## TS 3.1 — CLAUDE.md hierarchy (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.1 · Knowledge 1 · pp.12–13 | agent-instruction-files · S2 — In a repository, only the services/payments directory needs extra instructions: money is s… |
| K2 | TS 3.1 · Knowledge 2 · pp.12–13 | agent-instruction-files · S2 — A new developer says Claude Code ignores the team's conventions: always run the linter, al… |
| K3 | TS 3.1 · Knowledge 3 · pp.12–13 | agent-instruction-files · S2 — A monorepo holds a payments package and a frontend package, maintained by different teams … |
| K4 | TS 3.1 · Knowledge 4 · pp.12–13 | claude-md-hierarchy · S2 — A project's CLAUDE.md has grown to 700 lines covering testing, API conventions and deploym… |
| S1 | TS 3.1 · Skill 1 · pp.12–13 | agent-instruction-files · S2 — A new developer says Claude Code ignores the team's conventions: always run the linter, al…<br>claude-md-hierarchy · S4 — Two engineers say Claude behaves differently in their sessions on the same monorepo. One s… |
| S2 | TS 3.1 · Skill 2 · pp.12–13 | agent-instruction-files · S2 — A monorepo holds a payments package and a frontend package, maintained by different teams … |
| S3 | TS 3.1 · Skill 3 · pp.12–13 | claude-md-hierarchy · S2 — A project's CLAUDE.md has grown to 700 lines covering testing, API conventions and deploym… |
| S4 | TS 3.1 · Skill 4 · pp.12–13 | agent-instruction-files · S2 — Two developers on the same repository get different behaviour on the same task: one's sess…<br>claude-md-hierarchy · S4 — Two engineers say Claude behaves differently in their sessions on the same monorepo. One s… |

## TS 3.2 — Commands and skills (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.2 · Knowledge 1 · p.13 | skills · S2 — A team lead created a /release-notes command in ~/.claude/commands/ and told the team to u… |
| K2 | TS 3.2 · Knowledge 2 · p.13 | skills · S2 — A /map-dependencies skill prints thousands of lines of analysis into the conversation, cro… |
| K3 | TS 3.2 · Knowledge 3 · p.13 | skills · S2 — A /map-dependencies skill prints thousands of lines of analysis into the conversation, cro… |
| K4 | TS 3.2 · Knowledge 4 · p.13 | skills · S2 — A developer wants a terser version of the team's shared /review-pr skill for their own use… |
| S1 | TS 3.2 · Skill 1 · p.13 | skills · S2 — A team lead created a /release-notes command in ~/.claude/commands/ and told the team to u… |
| S2 | TS 3.2 · Skill 2 · p.13 | skills · S2 — A /map-dependencies skill prints thousands of lines of analysis into the conversation, cro… |
| S3 | TS 3.2 · Skill 3 · p.13 | skills · S2 — A /generate-docs skill should only ever write documentation files, never run shell command… |
| S4 | TS 3.2 · Skill 4 · p.13 | skills · S2 — Developers keep invoking /fix-issue without the issue number, and Claude ends up fixing wh… |
| S5 | TS 3.2 · Skill 5 · p.13 | agentic-tool-surface-selection · S2 — A team wants Claude to always use their package manager's commands in every session. Separ… |

## TS 3.3 — Path-specific rules (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.3 · Knowledge 1 · pp.13–14 | claude-md-hierarchy · S2 — Infrastructure conventions (tagging, naming, no hard-coded regions) should apply only when… |
| K2 | TS 3.3 · Knowledge 2 · pp.13–14 | claude-md-hierarchy · S2 — Infrastructure conventions (tagging, naming, no hard-coded regions) should apply only when… |
| K3 | TS 3.3 · Knowledge 3 · pp.13–14 | claude-md-hierarchy · S2 — Test files live next to their components across 40 directories (Button.test.tsx beside But… |
| S1 | TS 3.3 · Skill 1 · pp.13–14 | claude-md-hierarchy · S2 — Infrastructure conventions (tagging, naming, no hard-coded regions) should apply only when… |
| S2 | TS 3.3 · Skill 2 · pp.13–14 | claude-md-hierarchy · S2 — Test files live next to their components across 40 directories (Button.test.tsx beside But… |
| S3 | TS 3.3 · Skill 3 · pp.13–14 | claude-md-hierarchy · S2 — Test files live next to their components across 40 directories (Button.test.tsx beside But… |

## TS 3.4 — Plan vs direct (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.4 · Knowledge 1 · p.14 | plan-mode · S2 — A developer asks Claude Code to move a service from one ORM to another. About 60 files are… |
| K2 | TS 3.4 · Knowledge 2 · p.14 | plan-mode · S2 — A stack trace points to a missing null check on one line of one function, and the fix is o… |
| K3 | TS 3.4 · Knowledge 3 · p.14 | plan-mode · S2 — A developer asks Claude Code to move a service from one ORM to another. About 60 files are…<br>plan-mode · S2 — A team used plan mode to design a 45-file library migration and approved the plan. They're… |
| K4 | TS 3.4 · Knowledge 4 · p.14 | plan-mode · S2 — During a multi-phase task, the main session's context keeps filling with search output fro… |
| S1 | TS 3.4 · Skill 1 · p.14 | plan-mode · S2 — A developer asks Claude Code to move a service from one ORM to another. About 60 files are…<br>plan-mode · S2 — A team must add payments using either a hosted checkout page or an embedded card form. Eac… |
| S2 | TS 3.4 · Skill 2 · p.14 | plan-mode · S2 — A stack trace points to a missing null check on one line of one function, and the fix is o… |
| S3 | TS 3.4 · Skill 3 · p.14 | plan-mode · S2 — During a multi-phase task, the main session's context keeps filling with search output fro… |
| S4 | TS 3.4 · Skill 4 · p.14 | plan-mode · S2 — A team used plan mode to design a 45-file library migration and approved the plan. They're… |

## TS 3.5 — Iterative refinement (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 3.5 · Knowledge 1 · pp.14–15 | prompt-engineering-techniques · S2 — A developer describes in prose how Claude Code should convert API field names (snake_case … |
| K2 | TS 3.5 · Knowledge 2 · pp.14–15 | prompt-engineering-techniques · S2 — A developer asks Claude Code to fix a data migration script and replies “still broken” aft… |
| K3 | TS 3.5 · Knowledge 3 · pp.14–15 | prompt-engineering-techniques · S2 — A developer who has never built a caching layer asks Claude Code to add one to a busy API.… |
| K4 | TS 3.5 · Knowledge 4 · pp.14–15 | prompt-engineering-techniques · S2 — Two bugs interact: the tax calculation depends on how the order total is rounded, and both… |
| S1 | TS 3.5 · Skill 1 · pp.14–15 | prompt-engineering-techniques · S2 — A developer describes in prose how Claude Code should convert API field names (snake_case … |
| S2 | TS 3.5 · Skill 2 · pp.14–15 | prompt-engineering-techniques · S2 — A developer asks Claude Code to fix a data migration script and replies “still broken” aft… |
| S3 | TS 3.5 · Skill 3 · pp.14–15 | prompt-engineering-techniques · S2 — A developer who has never built a caching layer asks Claude Code to add one to a busy API.… |
| S4 | TS 3.5 · Skill 4 · pp.14–15 | prompt-engineering-techniques · S2 — A migration script generated by Claude Code crashes on rows where middle_name is null, and… |
| S5 | TS 3.5 · Skill 5 · pp.14–15 | prompt-engineering-techniques · S2 — Two bugs interact: the tax calculation depends on how the order total is rounded, and both… |

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
| K1 | TS 4.1 · Knowledge 1 · p.16 | system-prompts · S5 — Your CI reviewer flags many code comments as “inaccurate” when they're merely old-fashione… |
| K2 | TS 4.1 · Knowledge 2 · p.16 | system-prompts · S5 — A reviewer's prompt says “be conservative and only report issues you're highly confident a… |
| K3 | TS 4.1 · Knowledge 3 · p.16 | system-prompts · S5 — Developers dismiss about 80% of the reviewer's “performance” findings, and have begun igno… |
| S1 | TS 4.1 · Skill 1 · p.16 | system-prompts · S5 — Your CI reviewer flags many code comments as “inaccurate” when they're merely old-fashione…<br>system-prompts · S5 — A reviewer's prompt says “be conservative and only report issues you're highly confident a…<br>system-prompts · S5 — The team deliberately catches broad exceptions in its plugin loader, a documented local pa… |
| S2 | TS 4.1 · Skill 2 · p.16 | system-prompts · S5 — Developers dismiss about 80% of the reviewer's “performance” findings, and have begun igno… |
| S3 | TS 4.1 · Skill 3 · p.16 | system-prompts · S5 — Two identical unchecked-null bugs in different files come back as “critical” in one and “m… |

## TS 4.2 — Few-shot (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.2 · Knowledge 1 · pp.16–17 | prompt-engineering-techniques · S5 — A CI review prompt lists the fields every finding needs (location, issue, severity, sugges… |
| K2 | TS 4.2 · Knowledge 2 · pp.16–17 | prompt-engineering-techniques · S1 — A support agent hesitates between get_customer and lookup_order on requests like “it's abo… |
| K3 | TS 4.2 · Knowledge 3 · pp.16–17 | prompt-engineering-techniques · S1 — Every time the agent mishandles a new kind of ambiguous request, the team adds another rul… |
| K4 | TS 4.2 · Knowledge 4 · pp.16–17 | prompt-engineering-techniques · S6 — Extracting product dimensions, the pipeline returns null for required measurements wheneve… |
| S1 | TS 4.2 · Skill 1 · pp.16–17 | prompt-engineering-techniques · S1 — A support agent hesitates between get_customer and lookup_order on requests like “it's abo… |
| S2 | TS 4.2 · Skill 2 · pp.16–17 | prompt-engineering-techniques · S5 — A CI review prompt lists the fields every finding needs (location, issue, severity, sugges… |
| S3 | TS 4.2 · Skill 3 · pp.16–17 | prompt-engineering-techniques · S5 — The CI reviewer keeps flagging the team's standard retry decorator as “unsafe error handli… |
| S4 | TS 4.2 · Skill 4 · pp.16–17 | prompt-engineering-techniques · S6 — A citation extractor works on papers with a bibliography at the end, but misses or duplica… |
| S5 | TS 4.2 · Skill 5 · pp.16–17 | prompt-engineering-techniques · S6 — Extracting product dimensions, the pipeline returns null for required measurements wheneve… |

## TS 4.3 — Structured output (10/10 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.3 · Knowledge 1 · pp.17–18 | structured-outputs · S6 — An extraction service asks Claude to “reply with JSON only” and parses the text. About 2% … |
| K2 | TS 4.3 · Knowledge 2 · pp.17–18 | tool-choice · S6 — An invoice-extraction pipeline defines one extraction tool, but on short or odd documents …<br>tool-choice · S6 — Incoming documents may be invoices, receipts or contracts, each with its own extraction to… |
| K3 | TS 4.3 · Knowledge 3 · pp.17–18 | structured-outputs · S6 — The pipeline now uses strict tool use, so every invoice extraction is valid JSON. Audits s… |
| K4 | TS 4.3 · Knowledge 4 · pp.17–18 | tool-choice · S6 — An extraction schema marks tax_id as a required string. Audits find plausible-looking but …<br>tool-choice · S6 — A document_type enum lists invoice, receipt and contract. New kinds, such as credit notes … |
| S1 | TS 4.3 · Skill 1 · pp.17–18 | structured-outputs · S6 — An extraction service asks Claude to “reply with JSON only” and parses the text. About 2% … |
| S2 | TS 4.3 · Skill 2 · pp.17–18 | tool-choice · S6 — Incoming documents may be invoices, receipts or contracts, each with its own extraction to… |
| S3 | TS 4.3 · Skill 3 · pp.17–18 | tool-choice · S6 — In an extraction workflow, extract_metadata must always run first. After that, the model s… |
| S4 | TS 4.3 · Skill 4 · pp.17–18 | tool-choice · S6 — An extraction schema marks tax_id as a required string. Audits find plausible-looking but … |
| S5 | TS 4.3 · Skill 5 · pp.17–18 | tool-choice · S6 — A document_type enum lists invoice, receipt and contract. New kinds, such as credit notes … |
| S6 | TS 4.3 · Skill 6 · pp.17–18 | structured-outputs · S6 — Due dates arrive as “05/04/2026” (UK invoices), “April 5th” and “2026-04-05”, and extracti… |

## TS 4.4 — Validation-retry (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.4 · Knowledge 1 · p.18 | structured-outputs · S6 — When validation fails, the pipeline retries with “The previous output was invalid, please … |
| K2 | TS 4.4 · Knowledge 2 · p.18 | structured-outputs · S6 — Invoices often say “PO: see attached purchase order”, but the attachment isn't sent to the… |
| K3 | TS 4.4 · Knowledge 3 · p.18 | structured-outputs · S5 — Developers dismiss many of the CI reviewer's findings, but the team can't tell which kinds… |
| K4 | TS 4.4 · Knowledge 4 · p.18 | structured-outputs · S6 — The pipeline now uses strict tool use, so every invoice extraction is valid JSON. Audits s… |
| S1 | TS 4.4 · Skill 1 · p.18 | structured-outputs · S6 — When validation fails, the pipeline retries with “The previous output was invalid, please … |
| S2 | TS 4.4 · Skill 2 · p.18 | structured-outputs · S6 — Invoices often say “PO: see attached purchase order”, but the attachment isn't sent to the… |
| S3 | TS 4.4 · Skill 3 · p.18 | structured-outputs · S5 — Developers dismiss many of the CI reviewer's findings, but the team can't tell which kinds… |
| S4 | TS 4.4 · Skill 4 · p.18 | structured-outputs · S6 — Some invoices contain their own arithmetic errors, and some list a total in the summary th… |

## TS 4.5 — Batch (8/8 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.5 · Knowledge 1 · pp.18–19 | batch-api · S1 — Finance asks to move a weekly compliance audit of support transcripts to the Message Batch… |
| K2 | TS 4.5 · Knowledge 2 · pp.18–19 | batch-api · S5 — To cut costs, a team wants to move two workloads to the Message Batches API: the automated…<br>batch-api · S1 — Finance asks to move a weekly compliance audit of support transcripts to the Message Batch… |
| K3 | TS 4.5 · Knowledge 3 · pp.18–19 | batch-api · S1 — A refund-review job needs the model to call lookup_order, see the result, then decide on t… |
| K4 | TS 4.5 · Knowledge 4 · pp.18–19 | batch-api · S6 — A batch of 500 document extractions comes back, and the team pairs each result with its in… |
| S1 | TS 4.5 · Skill 1 · pp.18–19 | batch-api · S5 — To cut costs, a team wants to move two workloads to the Message Batches API: the automated… |
| S2 | TS 4.5 · Skill 2 · pp.18–19 | batch-api · S6 — Documents arrive all day, and each must be extracted within 30 hours of arriving. Batches … |
| S3 | TS 4.5 · Skill 3 · pp.18–19 | batch-api · S6 — In a nightly batch of 2,000 extractions, 40 requests failed. Twelve failed because their d… |
| S4 | TS 4.5 · Skill 4 · pp.18–19 | batch-api · S6 — A team is about to batch-process 100,000 archived contracts with a brand-new extraction pr… |

## TS 4.6 — Multi-pass review (6/6 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 4.6 · Knowledge 1 · p.19 | multi-pass-review-architectures · S2 — Claude Code generates a pagination feature. In the same session, the developer asks it to … |
| K2 | TS 4.6 · Knowledge 2 · p.19 | multi-pass-review-architectures · S2 — Claude Code generates a pagination feature. In the same session, the developer asks it to … |
| K3 | TS 4.6 · Knowledge 3 · p.19 | multi-pass-review-architectures · S5 — A single review pass over a 30-file pull request misses issues in the middle files and say… |
| S1 | TS 4.6 · Skill 1 · p.19 | multi-pass-review-architectures · S2 — Claude Code generates a pagination feature. In the same session, the developer asks it to … |
| S2 | TS 4.6 · Skill 2 · p.19 | multi-pass-review-architectures · S5 — A single review pass over a 30-file pull request misses issues in the middle files and say…<br>multi-pass-review-architectures · S5 — Per-file review passes find every local bug in a PR. But file_04 renames total to amount, … |
| S3 | TS 4.6 · Skill 3 · p.19 | multi-pass-review-architectures · S5 — A CI reviewer posts every finding as a PR comment, and developers are drowning in low-valu… |

## TS 5.1 — Context preservation (10/10 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.1 · Knowledge 1 · pp.19–20 | attention-engineering · S1 — To save space, a long support conversation is summarised every ten turns. After a few roun…<br>case-facts-block · S1 — A support agent summarises the conversation every ten turns. Early on, a customer explaine… |
| K2 | TS 5.1 · Knowledge 2 · pp.19–20 | attention-engineering · S3 — A research coordinator concatenates nine subagents' reports and asks for the single bigges… |
| K3 | TS 5.1 · Knowledge 3 · pp.19–20 | attention-engineering · S1 — Each lookup_order call returns 40+ fields: warehouse codes, carrier events, internal flags…<br>context-window · S4 — A log-investigation agent reads entire 2,000-line log files at every step, although it onl… |
| K4 | TS 5.1 · Knowledge 4 · pp.19–20 | attention-engineering · S1 — A developer builds a support chat on the Messages API and, to save tokens, sends only the …<br>context-window · S1 — To save tokens, a support chat built on the Messages API keeps only the last three message… |
| S1 | TS 5.1 · Skill 1 · pp.19–20 | attention-engineering · S1 — To save space, a long support conversation is summarised every ten turns. After a few roun…<br>case-facts-block · S1 — A support agent summarises the conversation every ten turns. Early on, a customer explaine…<br>case-facts-block · S1 — A team adds a “case facts” message at the start of each support conversation. Once the con…<br>case-facts-block · S1 — An agent records a refund as “pending” in its case-facts block. Twenty minutes later a loo… |
| S2 | TS 5.1 · Skill 2 · pp.19–20 | attention-engineering · S1 — In one session a customer raises problems with three orders. By the end, the agent quotes …<br>case-facts-block · S1 — A customer raises a billing dispute and two returns in one conversation. The agent keeps o… |
| S3 | TS 5.1 · Skill 3 · pp.19–20 | attention-engineering · S1 — Each lookup_order call returns 40+ fields: warehouse codes, carrier events, internal flags…<br>context-window · S4 — A log-investigation agent reads entire 2,000-line log files at every step, although it onl… |
| S4 | TS 5.1 · Skill 4 · pp.19–20 | attention-engineering · S3 — A research coordinator concatenates nine subagents' reports and asks for the single bigges… |
| S5 | TS 5.1 · Skill 5 · pp.19–20 | subagent-state-handoff · S3 — A research report presents a 2016 survey as current evidence and mixes up findings from a … |
| S6 | TS 5.1 · Skill 6 · pp.19–20 | subagent-state-handoff · S3 — The report subagent runs with a tight context budget. Document-analysis subagents send it …<br>context-window · S3 — A report agent can only fit about 6,000 tokens of input. Four document-analysis subagents … |

## TS 5.2 — Escalation (9/9 bullets)

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.2 · Knowledge 1 · pp.20–21 | escalation · S1 — Your support agent escalates about 30% of conversations. Reviews show most were routine, i… |
| K2 | TS 5.2 · Knowledge 2 · pp.20–21 | escalation · S1 — A customer opens with: “I don't want a bot. Put me through to a person now.” The issue loo… |
| K3 | TS 5.2 · Knowledge 3 · pp.20–21 | escalation · S1 — To cut unnecessary escalations, a team proposes escalating whenever the model's self-repor… |
| K4 | TS 5.2 · Knowledge 4 · pp.20–21 | escalation · S1 — get_customer returns two accounts for the name “Customer A”, one in Leeds and one in Leice… |
| S1 | TS 5.2 · Skill 1 · pp.20–21 | escalation · S1 — Your support agent escalates about 30% of conversations. Reviews show most were routine, i… |
| S2 | TS 5.2 · Skill 2 · pp.20–21 | escalation · S1 — A customer opens with: “I don't want a bot. Put me through to a person now.” The issue loo… |
| S3 | TS 5.2 · Skill 3 · pp.20–21 | escalation · S1 — A customer is clearly frustrated after a late delivery but hasn't asked for a person. The … |
| S4 | TS 5.2 · Skill 4 · pp.20–21 | escalation · S1 — A customer asks you to match a competitor's lower price. Your refund policy covers price a… |
| S5 | TS 5.2 · Skill 5 · pp.20–21 | escalation · S1 — get_customer returns two accounts for the name “Customer A”, one in Leeds and one in Leice… |

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
| K1 | TS 5.4 · Knowledge 1 · pp.21–22 | session-state · S4 — Deep into a long codebase exploration, the agent's answers start contradicting earlier one…<br>context-window · S2 — Two hours into a refactor in Claude Code, the context is 95% full of search output, and an… |
| K2 | TS 5.4 · Knowledge 2 · pp.21–22 | checkpoints · S4 — A developer plans to /clear the session before starting the next part of a long investigat… |
| K3 | TS 5.4 · Knowledge 3 · pp.21–22 | subagent-state-handoff · S4 — While onboarding a developer to a legacy monolith, the main agent's context fills with raw…<br>context-window · S4 — An onboarding agent answering “how does billing work?” reads file after file of a large le… |
| K4 | TS 5.4 · Knowledge 4 · pp.21–22 | session-state · S3 — A coordinator and three exploration agents crash after two of the agents have finished. Re… |
| S1 | TS 5.4 · Skill 1 · pp.21–22 | subagent-state-handoff · S4 — While onboarding a developer to a legacy monolith, the main agent's context fills with raw…<br>context-window · S4 — An onboarding agent answering “how does billing work?” reads file after file of a large le… |
| S2 | TS 5.4 · Skill 2 · pp.21–22 | session-state · S4 — Deep into a long codebase exploration, the agent's answers start contradicting earlier one…<br>checkpoints · S4 — A developer plans to /clear the session before starting the next part of a long investigat… |
| S3 | TS 5.4 · Skill 3 · pp.21–22 | session-state · S4 — A migration investigation has three phases: map dependencies, identify risky call sites, t… |
| S4 | TS 5.4 · Skill 4 · pp.21–22 | session-state · S3 — A coordinator and three exploration agents crash after two of the agents have finished. Re… |
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

## TS 5.6 — Provenance (0/9 bullets) — *no built concept yet*

| Bullet | Guide reference | Questions (concept · scenario) |
|---|---|---|
| K1 | TS 5.6 · Knowledge 1 · p.23 | ⚠️ **gap** |
| K2 | TS 5.6 · Knowledge 2 · p.23 | ⚠️ **gap** |
| K3 | TS 5.6 · Knowledge 3 · p.23 | ⚠️ **gap** |
| K4 | TS 5.6 · Knowledge 4 · p.23 | ⚠️ **gap** |
| S1 | TS 5.6 · Skill 1 · p.23 | ⚠️ **gap** |
| S2 | TS 5.6 · Skill 2 · p.23 | ⚠️ **gap** |
| S3 | TS 5.6 · Skill 3 · p.23 | ⚠️ **gap** |
| S4 | TS 5.6 · Skill 4 · p.23 | ⚠️ **gap** |
| S5 | TS 5.6 · Skill 5 · p.23 | ⚠️ **gap** |
