# Concepts Map — the CONCEPTS section vs the official guide

> Auto-generated from `utils/concepts_map.py` — do not hand-edit. The taxonomy mirrors a community concept list (claudearchitectcertification.com/concepts, a third-party site: unverified, structure only, no content copied). **Scope statuses are Claude's judgment from a keyword search and reading of guide v1.0 on 2026-09-26 — verify them.**

**71 concepts · 1 built.** 🎯 In the guide: 22 · ◐ Partly in the guide: 15 · ℹ️ Awareness only: 1 · ⛔ Out of scope: 3 · ⚪ Not in the guide: 30

**Kinds:** exam = in the guide (built with docs + guide) · ➕ extra = not on the exam but an official docs page covers it (built only if grounded, labelled *not on the exam*) · ungroundable = no official docs basis found, stays a stub · excluded = out of scope / awareness, never built. Candidate docs are fetched and read when the concept is built.

| # | Code | Concept | Status | Kind | Guide alignment | Candidate official docs | Evidence / note | Built |
|---|---|---|---|---|---|---|---|---|
| 1 | D1.1 | Agentic Loops | 🎯 In the guide | exam | TS 1.1 — Agentic loops (p.5) | — | — | 🧪 |
| 2 | D1.2 | Subagents | 🎯 In the guide | exam | TS 1.2 — Coordinator-subagent (pp.5–6) · TS 1.3 — Subagent invocation (pp.6–7) | — | — | — |
| 3 | D1.3 | Stop Reason | 🎯 In the guide | exam | TS 1.1 — Agentic loops (p.5) | — | stop_reason inspection is part of TS 1.1; the guide's appendix lists stop_reason handling. | — |
| 4 | D1.4 | Session State & Persistence | 🎯 In the guide | exam | TS 1.7 — Session state (pp.8–9) · TS 5.4 — Codebase exploration (pp.21–22) | — | — | — |
| 5 | D1.5 | Human-in-the-Loop Escalation | 🎯 In the guide | exam | TS 5.2 — Escalation (pp.20–21) · TS 1.4 — Enforcement & handoff (p.7) | — | — | — |
| 6 | D1.6 | Subagent State Handoff | 🎯 In the guide | exam | TS 1.3 — Subagent invocation (pp.6–7) · TS 1.4 — Enforcement & handoff (p.7) · TS 5.4 — Codebase exploration (pp.21–22) | — | — | — |
| 7 | D1.7 | Agent Instruction Files (CLAUDE.md / AGENTS.md) | ◐ Partly in the guide | exam | TS 3.1 — CLAUDE.md hierarchy (pp.12–13) | — | CLAUDE.md is in the guide (TS 3.1); AGENTS.md does not appear anywhere in it. | — |
| 8 | D1.8 | Task Decomposition Strategies | 🎯 In the guide | exam | TS 1.6 — Task decomposition (p.8) | — | — | — |
| 9 | D2.1 | Tool Calling | 🎯 In the guide | exam | TS 2.1 — Tool descriptions (p.9) · TS 1.1 — Agentic loops (p.5) | — | — | — |
| 10 | D2.2 | Tool Choice | 🎯 In the guide | exam | TS 2.3 — Tool choice (pp.10–11) · TS 4.3 — Structured output (pp.17–18) | — | — | — |
| 11 | D2.3 | Model Context Protocol | 🎯 In the guide | exam | TS 2.4 — MCP config (p.11) · TS 2.2 — Structured errors (pp.9–10) | — | — | — |
| 12 | D2.4 | SDK Hooks (Pre/PostToolUse) | 🎯 In the guide | exam | TS 1.5 — Hooks (pp.7–8) | — | — | — |
| 13 | D2.5 | Tool Evaluation & Testing | ◐ Partly in the guide | exam | TS 2.1 — Tool descriptions (p.9) | — | Guide §7/§8 asks you to test tool-selection reliability with ambiguous requests; there is no dedicated task statement. | — |
| 14 | D2.6 | Built-In Tools vs Custom Tools vs Skills vs MCP | 🎯 In the guide | exam | TS 2.5 — Built-in tools (pp.11–12) · TS 3.2 — Commands and skills (p.13) · TS 2.4 — MCP config (p.11) | — | — | — |
| 15 | D3.1 | CLAUDE.md Hierarchy | 🎯 In the guide | exam | TS 3.1 — CLAUDE.md hierarchy (pp.12–13) · TS 3.3 — Path-specific rules (pp.13–14) | — | — | — |
| 16 | D3.2 | Plan Mode | 🎯 In the guide | exam | TS 3.4 — Plan vs direct (p.14) | — | — | — |
| 17 | D3.3 | Skills | 🎯 In the guide | exam | TS 3.2 — Commands and skills (p.13) | — | — | — |
| 18 | D3.4 | Checkpoints & Session Management | ◐ Partly in the guide | exam | TS 1.7 — Session state (pp.8–9) · TS 5.4 — Codebase exploration (pp.21–22) | — | The guide covers --resume, fork_session and /compact; the word “checkpoints” does not appear. | — |
| 19 | D4.1 | System Prompts & Instructions | 🎯 In the guide | exam | TS 4.1 — Explicit criteria (p.16) | — | — | — |
| 20 | D4.2 | Prompt Caching | ℹ️ Awareness only | excluded | — | — | Guide Appendix: prompt-caching implementation details are out of scope “beyond knowing it exists”. | — |
| 21 | D4.3 | Batch API | 🎯 In the guide | exam | TS 4.5 — Batch (pp.18–19) | — | — | — |
| 22 | D4.4 | Structured Outputs | 🎯 In the guide | exam | TS 4.3 — Structured output (pp.17–18) · TS 4.4 — Validation-retry (p.18) | — | — | — |
| 23 | D4.5 | Vision & Multimodal | ⛔ Out of scope | excluded | — | — | Guide Appendix: vision / image-analysis capabilities will not appear on the exam. | — |
| 24 | D4.6 | Streaming | ⛔ Out of scope | excluded | — | — | Guide Appendix: streaming API implementation and server-sent events will not appear on the exam. | — |
| 25 | D4.7 | Attention Engineering | ◐ Partly in the guide | exam | TS 5.1 — Context preservation (pp.19–20) · TS 1.6 — Task decomposition (p.8) | — | The guide names the lost-in-the-middle effect (5.1) and attention dilution (1.6, 4.6); no dedicated task statement. | — |
| 26 | D4.8 | 4D Framework | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 27 | D4.9 | Prompt Engineering Techniques | 🎯 In the guide | exam | TS 4.1 — Explicit criteria (p.16) · TS 4.2 — Few-shot (pp.16–17) · TS 3.5 — Iterative refinement (pp.14–15) | — | — | — |
| 28 | D4.10 | Multi-Instance & Multi-Pass Review Architectures | 🎯 In the guide | exam | TS 4.6 — Multi-pass review (p.19) | — | — | — |
| 29 | D5.1 | Context Window Management | 🎯 In the guide | exam | TS 5.1 — Context preservation (pp.19–20) · TS 5.4 — Codebase exploration (pp.21–22) | — | — | — |
| 30 | D5.2 | Case Facts Block | 🎯 In the guide | exam | TS 5.1 — Context preservation (pp.19–20) | — | — | — |
| 31 | — | Translating Business Requirements into Claude Solutions | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 32 | — | End-to-End Architecture Design (Input to Feedback Loop) | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 33 | — | Workflow vs Agent: Choosing the Right Architecture | ◐ Partly in the guide | exam | TS 1.6 — Task decomposition (p.8) · TS 1.1 — Agentic loops (p.5) | — | Fixed pipelines vs dynamic decomposition (1.6) and model-driven vs pre-set sequences (1.1). | — |
| 34 | — | Aligning Solutions to Business Value Pillars | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 35 | — | Claude Model Selection & Tradeoffs | ⚪ Not in the guide | extra | — | https://platform.claude.com/docs/en/about-claude/models/overview<br>https://platform.claude.com/docs/en/about-claude/models/choosing-a-model | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). Adjacent exclusion: performance benchmarking / model-comparison metrics. | — |
| 36 | — | Authentication & Access Control for Agent Systems | ⛔ Out of scope | excluded | — | — | Guide Appendix excludes API authentication / account management and OAuth / key-rotation / auth-protocol details. | — |
| 37 | — | Accuracy-Latency-Cost Tradeoff Analysis | ◐ Partly in the guide | exam | TS 4.5 — Batch (pp.18–19) | — | Only the batch-vs-synchronous latency/cost trade-off is covered. | — |
| 38 | — | Observability & Monitoring for Agents at Scale | ◐ Partly in the guide | exam | TS 1.2 — Coordinator-subagent (pp.5–6) | — | The guide mentions observability only as a reason to route subagent communication through the coordinator. | — |
| 39 | — | Progressive Discovery vs Monolithic Context Strategy | ◐ Partly in the guide | exam | TS 2.5 — Built-in tools (pp.11–12) · TS 5.4 — Codebase exploration (pp.21–22) | — | Incremental codebase exploration (Grep, then Read) and scratchpad files. | — |
| 40 | — | Debugging LLM System Failures | ⚪ Not in the guide | extra | — | https://code.claude.com/docs/en/agent-sdk/observability | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). (Root-cause diagnosis is exercised throughout the §9 sample questions, but there is no dedicated task statement.) | — |
| 41 | — | Guardrails & Safe Deployment Practices | ◐ Partly in the guide | exam | TS 1.4 — Enforcement & handoff (p.7) · TS 1.5 — Hooks (pp.7–8) | — | The word “guardrails” never appears; programmatic enforcement via hooks / prerequisite gates does (1.4, 1.5). | — |
| 42 | — | LLM System Risks & Failure Modes | ⚪ Not in the guide | extra | — | https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations<br>https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 43 | — | Regulatory Compliance for AI Systems (GDPR, HIPAA, FedRAMP) | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 44 | — | Ethical AI Considerations (Bias, Fairness, Transparency) | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 45 | — | Structured Stakeholder Discovery | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 46 | — | Communicating AI Decisions & Value to Stakeholders | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 47 | — | Stakeholder Feedback Loops & SLA Alignment | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 48 | — | Architecture Documentation & Implementation Handoff | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 49 | — | AI Solution Lifecycle Management | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 50 | — | Building Agents: Client SDK vs Agent SDK vs Managed Agents | ◐ Partly in the guide | exam | TS 1.1 — Agentic loops (p.5) · TS 1.2 — Coordinator-subagent (pp.5–6) · TS 1.3 — Subagent invocation (pp.6–7) · TS 1.5 — Hooks (pp.7–8) · TS 1.7 — Session state (pp.8–9) | — | The guide covers the Claude Agent SDK; “Client SDK” and “Managed Agents” do not appear. | — |
| 51 | — | Agent Design Patterns: Memory, Context Management & Third-Party Frameworks | ◐ Partly in the guide | exam | TS 5.1 — Context preservation (pp.19–20) · TS 5.4 — Codebase exploration (pp.21–22) | — | Context management is in scope; specific third-party frameworks are excluded by the Appendix. | — |
| 52 | — | Systems Life Cycle Management for Claude Applications | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 53 | — | Software Engineering Foundations for Claude Applications | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). Adjacent exclusion: language/framework detail beyond tool and schema configuration. | — |
| 54 | — | Claude Application Design Across Interfaces | ⚪ Not in the guide | extra | — | https://code.claude.com/docs/en/agent-sdk/overview<br>https://platform.claude.com/docs/en/managed-agents/overview | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 55 | — | LLM Fundamentals: Tokens, Sampling & Non-Determinism | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). Adjacent exclusion: token-counting algorithms and tokenisation specifics. | — |
| 56 | — | Technical Fundamentals: SDKs, REST, and WebSockets | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). Adjacent exclusion: streaming / server-sent-events implementation. | — |
| 57 | — | AI Application Security: Prompt Injection & Untrusted Input | ⚪ Not in the guide | extra | — | https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks<br>https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 58 | — | Prompting Strategy by Task Type: Analysis, Research, Drafting, Brainstorming | ⚪ Not in the guide | extra | — | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 59 | — | Evaluating Claude Output for Accuracy & Completeness | ◐ Partly in the guide | exam | TS 5.5 — Human review (pp.22–23) · TS 4.4 — Validation-retry (p.18) | — | — | — |
| 60 | — | Identifying Hallucinations, Inconsistencies & Bias in AI Output | ◐ Partly in the guide | exam | TS 4.4 — Validation-retry (p.18) · TS 4.2 — Few-shot (pp.16–17) · TS 5.5 — Human review (pp.22–23) | — | “Hallucination” appears only for extraction (fabricated values); “bias” does not appear. | — |
| 61 | — | Editing & Adapting Outputs for the Intended Audience | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 62 | — | Choosing Output Formats: Artifacts vs Inline vs Structured Data | ⚪ Not in the guide | extra | — | https://platform.claude.com/docs/en/build-with-claude/structured-outputs | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 63 | — | Selecting the Right Claude Product Feature | ⚪ Not in the guide | extra | — | https://code.claude.com/docs/en/features-overview | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 64 | — | Using Claude for Research, Planning & Solution Development | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 65 | — | Integrating Claude into Existing Workflows | ◐ Partly in the guide | exam | TS 3.6 — CI/CD (pp.15–16) | — | — | — |
| 66 | — | Configuring & Maintaining Claude Projects | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 67 | — | Managing Uploaded Knowledge & Connectors | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 68 | — | Identifying Appropriate vs Inappropriate AI Use Cases | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 69 | — | Following Organizational AI Governance Policy | ⚪ Not in the guide | ungroundable | — | — | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
| 70 | — | Adjusting Approach Based on Feedback & Results | ◐ Partly in the guide | exam | TS 3.5 — Iterative refinement (pp.14–15) | — | — | — |
| 71 | — | Optimizing AI Workflows for Efficiency | ⚪ Not in the guide | extra | — | https://platform.claude.com/docs/en/build-with-claude/batch-processing<br>https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency | No matching task statement or knowledge item in guide v1.0 (keyword search, 2026-09-26). | — |
