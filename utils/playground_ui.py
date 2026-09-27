"""
Streamlit UI for the agent playground: one tab per sub-concept, each with its own message box, its own knobs
(the developer-side constraints that sub-concept is about) and a transcript of how the agent handled it.
Engine: utils/agent_playground.py. Content (tabs, blurbs, mental models): the concept's `playground` tuple.

Everything the "model" does is SIMULATED and labelled so on screen.
"""

import html

import streamlit as st

from utils.agent_playground import IN_RATE_PER_1K, OUT_RATE_PER_1K, PlayConfig, run_agent
from utils.research_playground import ResearchConfig, run_research
from utils.stop_inspector import StopConfig, run_stop
from utils.session_play import SessionConfig, run_play
from utils.escalation_play import EscalationConfig, run_escalation
from utils.handoff_play import HandoffConfig, run_handoff
from utils.memory_play import MemoryConfig, run_memory
from utils.decomp_play import DecompConfig, run_decomp
from utils.toolsel_play import ToolSelConfig, run_toolsel
from utils.toolchoice_play import ToolChoiceConfig, run_toolchoice
from utils.mcp_play import McpConfig, run_mcp
from utils.hooks_play import HooksConfig, run_hooks
from utils.casefacts_play import CaseFactsConfig, run_casefacts
from utils.ctxwin_play import CtxWinConfig, run_ctxwin
from utils.mpreview_play import MPReviewConfig, run_mpreview
from utils.fewshot_play import FewshotConfig, run_fewshot
from utils.attention_play import AttentionConfig, run_attention
from utils.extract_play import ExtractConfig, run_extract
from utils.batch_play import BatchConfig, run_batch
from utils.review_play import ReviewConfig, run_review
from utils.checkpoint_play import CheckpointConfig, run_checkpoint
from utils.skills_play import SkillsConfig, run_skills
from utils.plan_play import PlanConfig, run_plan
from utils.rules_play import RulesConfig, run_rules
from utils.builtin_play import BuiltinConfig, run_builtin
from utils.eval_play import EvalConfig, run_eval
from utils.stop_lab import POLICIES
from utils.guide_index import resolve_source

HISTORY_KEEP = 3   # runs kept per tab

# what each knob is, for the widgets: key -> (label, kind, extra)
_KNOBS = {
    "max_tokens": ("max_tokens (per request)", "int", {"min_value": 20, "max_value": 2048, "step": 10,
                   "help": "The API parameter: the most output tokens one response may use."}),
    "max_tokens_policy": ("When stop_reason is max_tokens…", "choice",
                          {"options": {"raise": "raise max_tokens and ask again (handled)",
                                       "surface": "report it as a result (don't show it as an answer)"}}),
    "refusal_policy": ("When stop_reason is refusal…", "choice",
                       {"options": {"different_model": "retry on a DIFFERENT model (docs)",
                                    "same_model": "retry the SAME model (up to 3×)",
                                    "stop": "stop, no retry"}}),
    "pause_policy": ("When stop_reason is pause_turn…", "choice",
                     {"options": {"resume": "send the response back as-is (docs)",
                                  "treat_as_final": "treat it as the final answer (bug)"}}),
    "stop_sequences": ("Stop sequence (your tripwire text)", "text",
                       {"help": "If the reply would contain this text, generation halts there. Leave empty for none."}),
    "context_window": ("Context window (SIMULATED tokens)", "int", {"min_value": 0, "max_value": 2000, "step": 10,
                       "help": "0 = unlimited. Each request re-sends the whole conversation, so input tokens grow every turn."}),
    "max_turns": ("max_turns (tool-use turns)", "int", {"min_value": 0, "max_value": 30, "step": 1,
                  "help": "0 = no limit (the SDK default). Counts tool-use turns only."}),
    "handler": ("Your handler decides…", "choice", {"options": {k: v[0] for k, v in POLICIES.items()}}),
    "mid_tool_call": ("Is the limit hit mid tool call?", "choice", {"options": {
        "no": "no — the cut is in the text", "yes": "yes — inside a tool_use block (incomplete tool call)"}}),
    "choice": ("tool_choice", "choice", {"options": {"auto": "auto", "any": "any", "tool:extract_invoice": "tool: extract_invoice",
                                                     "tool:extract_contract": "tool: extract_contract", "none": "none"}}),
    "doc": ("Document", "choice", {"options": {"invoice": "a chatty invoice email", "contract": "a services contract"}}),
    "first": ("First call's tool_choice", "choice", {"options": {"forced": "tool: extract_metadata", "any": "any", "auto": "auto"}}),
    "release": ("Release to auto after the first call?", "choice", {"options": {"yes": "yes", "no": "no — keep it"}}),
    "nullable": ("tax_id nullable?", "choice", {"options": {"yes": "yes", "no": "no — required string"}}),
    "other": ("category enum has other + detail?", "choice", {"options": {"yes": "yes", "no": "no — closed list"}}),
    "strict": ("strict: true?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "validate": ("Your own semantic check (line items = total)?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "searcher_tools": ("Searcher's tools", "choice", {"options": {
        "scoped": "web_search + load_document", "fetch_url": "web_search + fetch_url", "all": "all 18"}}),
    "synth_tools": ("Synthesizer's tools", "choice", {"options": {
        "verify_fact": "verify_fact", "web_search": "web_search", "none": "none", "all": "all 18"}}),
    "model": ("Model", "choice", {"options": {"mock-opus-5.5": "mock-opus-5.5 (rejects forcing, per the docs' list)", "mock-claude": "mock-claude"}}),
    "thinking": ("Manual extended thinking", "choice", {"options": {"off": "off", "enabled": "enabled"}}),
    "github_scope": ("Where the team's GitHub server is configured", "choice", {"options": {
        "project": ".mcp.json (project)", "user": "~/.claude.json (user)", "local": "~/.claude.json for this project (local)"}}),
    "token_style": ("GitHub token in the config", "choice", {"options": {"var": "${GITHUB_TOKEN}", "literal": "a literal token (fake)"}}),
    "teammate_env": ("Teammate has GITHUB_TOKEN set?", "choice", {"options": {"set": "yes", "unset": "no"}}),
    "jira_source": ("Jira server", "choice", {"options": {"community": "community server", "custom": "our own custom server"}}),
    "notes_scope": ("Your experimental scratch-notes server", "choice", {"options": {"user": "~/.claude.json (user)", "project": ".mcp.json (project)"}}),
    "tool_desc": ("find_references description", "choice", {"options": {"detailed": "detailed (what, returns, when vs Grep)", "vague": "“Finds references.”"}}),
    "resources": ("Expose the schema catalog as a resource?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "error_style": ("How your tools report errors", "choice", {"options": {
        "structured": "isError + category + isRetryable + readable text", "generic": "“Operation failed”", "code_only": "structured, but a code instead of words"}}),
    "err_case": ("Situation", "choice", {"options": {"policy": "refund over the limit", "timeout": "timeout (recovers)",
                                                     "permission": "no access", "empty": "no orders"}}),
    "orders_state": ("Order service", "choice", {"options": {"empty": "customer has no orders", "permission": "refuses access (permission)",
                                                             "timeout_twice": "times out twice, then answers"}}),
    "empty_handling": ("lookup_orders handling", "choice", {"options": {"success": "empty = success; failures = isError",
                                                                       "error": "empty → isError “not found”", "swallow": "any exception → []"}}),
    "local_retry": ("Subagent retries retryable errors locally?", "choice", {"options": {"yes": "yes (up to 3)", "no": "no"}}),
    "partial_info": ("Propagates error + attempts + partial results?", "choice", {"options": {"yes": "yes", "no": "no — just “failed”"}}),
    "enforcement": ("Where the $500 refund limit is enforced", "choice", {"options": {
        "hook": "PreToolUse hook only", "prompt": "system prompt only", "both": "hook + prompt"}}),
    "deny_reason": ("What the hook tells the model when it denies", "choice", {"options": {
        "redirect": "reason + “call escalate_to_human instead”", "reason_only": "“not allowed” only", "none": "no reason"}}),
    "normalize": ("How mixed formats are handled", "choice", {"options": {
        "hook": "PostToolUse hook (updatedToolOutput)", "prompt": "explained in the prompt", "none": "not at all"}}),
    "pre_matcher": ("PreToolUse matcher", "choice", {"options": {
        "mcp__billing__process_refund": "mcp__billing__process_refund", "process_refund": "process_refund",
        "mcp__billing": "mcp__billing", "mcp__billing__.*": "mcp__billing__.*", ".*refund.*": ".*refund.*", "": "(none - every tool)"}}),
    "logger": ("Also register an audit logger that returns allow?", "choice", {"options": {"allow": "yes", "none": "no"}}),
    "policy_mode": ("Policy hook output", "choice", {"options": {"sync": "synchronous decision", "async": "async (agent doesn't wait)"}}),
    "policy_event": ("Register the policy hook on", "choice", {"options": {"PreToolUse": "PreToolUse", "PostToolUse": "PostToolUse"}}),
    "candidate": ("Candidate tool set", "choice", {"options": {"v1": "v1 — vague web tool", "v2": "v2 — sharpened descriptions", "v3": "v3 — sharpened, lost ORD- formatting"}}),
    "cover_ambiguous": ("Test set includes ambiguous requests?", "choice", {"options": {"yes": "yes", "no": "no — clear + edge only"}}),
    "criteria_style": ("Success criteria", "choice", {"options": {"per_category": "a bar per category", "overall_80": "overall ≥ 80%"}}),
    "grader": ("Grader", "choice", {"options": {"exact": "exact job + input", "job_only": "job only", "any_tool": "“a tool was called”"}}),
    "rerun": ("After a change, re-run", "choice", {"options": {"full": "the whole suite", "failures_only": "only last time's failures"}}),
    "search_tool": ("Tool", "choice", {"options": {"grep": "Grep (contents)", "glob": "Glob (paths)"}}),
    "edit_strategy": ("How to change the [payments] timeout", "choice", {"options": {"short_anchor": "Edit “timeout = 30”", "longer_anchor": "Edit with “[payments]” in the anchor", "replace_all": "Edit with replace_all", "read_write": "Edit, falling back to Read + Write"}}),
    "explore": ("How to explore", "choice", {"options": {"incremental": "Grep the entry point, Read along imports", "read_all": "Read every file first"}}),
    "wrapper_names": ("Names to search for", "choice", {"options": {"exported": "the wrapper's exported names", "original": "the functions' original names"}}),
    "need": ("The need", "choice", {"options": {"always_rule": "“Use pnpm, not npm” every session", "deploy_workflow": "a /deploy checklist run sometimes", "guardrail": "never edit .env", "external_data": "read the issue tracker", "verbose_research": "scan 200 files, report findings"}}),
    "surface": ("Surface", "choice", {"options": {"claude_md": "CLAUDE.md", "skill": "skill", "hook": "hook", "mcp": "MCP server", "subagent": "subagent"}}),
    "who": ("Session", "choice", {"options": {"teammate": "a teammate (fresh clone)", "you": "you"}}),
    "api_rule_where": ("Where the API rule lives", "choice", {"options": {"project_rule": "project .claude/rules/api.md (paths: src/api/**)", "root_claude_md": "project root CLAUDE.md", "user_rule": "your ~/.claude/rules/api.md", "local_md": "CLAUDE.local.md (gitignored)"}}),
    "tf_paths": ("Terraform rule frontmatter", "choice", {"options": {"scoped": "paths: terraform/**/*", "none": "no frontmatter", "misspelled": "path: terraform/**/* (typo)"}}),
    "test_rule_as": ("Test convention lives in", "choice", {"options": {"glob_rule": ".claude/rules/testing.md, paths **/*.test.tsx", "dir_claude_md": "src/web/CLAUDE.md", "root_glob": ".claude/rules/testing.md, paths *.test.tsx"}}),
    "task_pick": ("Task", "choice", {"options": {"library_migration": "45-file library migration (2 approaches)", "single_bug": "one-line bug with a stack trace", "choose_integration": "hosted vs embedded payments (2 files)", "big_discovery": "search 300 files, change 12"}}),
    "mode_pick": ("Mode", "choice", {"options": {"plan": "plan mode", "direct": "direct execution"}}),
    "discovery": ("Files to discover", "choice", {"options": {"50": "50", "300": "300", "1000": "1,000"}}),
    "use_explore": ("Use the Explore subagent?", "choice", {"options": {"yes": "yes", "no": "no — discover in the main conversation"}}),
    "approval": ("At the plan-approval prompt", "choice", {"options": {"acceptEdits": "Yes — auto-accept edits", "default": "Yes — manually approve edits", "auto": "Yes — use auto mode", "keep_planning": "No — keep planning"}}),
    "cmd_where": ("Where /review-pr is stored", "choice", {"options": {"project_commands": ".claude/commands/review-pr.md", "project_skills": ".claude/skills/review-pr/SKILL.md", "user_commands": "~/.claude/commands/review-pr.md"}}),
    "fork_on": ("context: fork?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "fork_agent": ("agent (when forked)", "choice", {"options": {"Explore": "Explore (read-only)", "general-purpose": "general-purpose"}}),
    "allowed_list": ("allowed-tools", "choice", {"options": {"write_edit": "Write Edit", "none": "(none)"}}),
    "disallowed_list": ("disallowed-tools", "choice", {"options": {"bash": "Bash", "none": "(none)"}}),
    "session_mode": ("Session permission mode", "choice", {"options": {"acceptEdits": "acceptEdits", "default": "default"}}),
    "hint_on": ("argument-hint: [issue-number]?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "std_where": ("The “use pnpm” standard lives in", "choice", {"options": {"claude_md": "CLAUDE.md", "skill": "a skill (package-manager)"}}),
    "rw_action": ("Rewind option", "choice", {"options": {"code": "Restore code", "conversation": "Restore conversation", "code_and_conversation": "Restore code and conversation"}}),
    "git_too": ("Also git restore config.json?", "choice", {"options": {"yes": "yes", "no": "no — rely on /rewind"}}),
    "ctx_action": ("To free the context", "choice", {"options": {"summarize_from_here": "Summarize from prompt 2", "summarize_up_to_here": "Summarize up to prompt 2", "compact": "/compact", "clear": "/clear"}}),
    "alt_action": ("To try approach B", "choice", {"options": {"branch": "/branch (fork the session)", "rewind": "rewind to prompt 2 (code + conversation)"}}),
    "resume_first": ("Resume cart-pence first?", "choice", {"options": {"yes": "yes — claude --resume cart-pence", "no": "no — rewind in today's session"}}),
    "instruction_style": ("Instruction", "choice", {"options": {"explicit": "Report / Skip categories", "accurate": "“check that comments are accurate”", "conservative": "“be conservative, high-confidence only”"}}),
    "sev_examples": ("Severity levels have concrete examples?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "perf_off": ("Performance category switched off?", "choice", {"options": {"yes": "yes (for now)", "no": "no"}}),
    "job_pick": ("Job", "choice", {"options": {"premerge": "pre-merge check (blocking)", "nightly": "nightly test generation", "tool_loop": "investigations that call tools", "results_order": "weekly audit summaries"}}),
    "api_pick": ("API", "choice", {"options": {"sync": "synchronous Messages API", "batch": "Message Batches API"}}),
    "match_by": ("Match results by", "choice", {"options": {"custom_id": "custom_id", "position": "position in the list"}}),
    "retry_mode": ("Resubmit", "choice", {"options": {"failed_chunked": "failed only, chunking the too-long ones", "failed_only": "failed only, unchanged", "all": "the whole batch"}}),
    "window_hours": ("Submit every", "choice", {"options": {"1": "1 h", "4": "4 h", "6": "6 h", "12": "12 h", "24": "24 h"}}),
    "sample_on": ("Refine the prompt on a sample first?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "sem_check": ("Semantic check (calculated vs stated total)?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "absent_policy": ("When information isn't in the document", "choice", {"options": {"flag": "store null + flag", "retry": "retry twice"}}),
    "po_nullable": ("po_number nullable?", "choice", {"options": {"yes": "yes", "no": "no - required string"}}),
    "conflict_field": ("conflict_detected field?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "norm_rules": ("Normalisation rules in the prompt", "choice", {"options": {"iso_uk": "ISO 8601 + UK day/month", "iso_only": "ISO 8601 only", "none": "none"}}),
    "pattern_field": ("detected_pattern on findings?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "lead_summary": ("Key-findings summary at the start?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "q_position": ("Question position", "choice", {"options": {"end": "at the end", "start": "at the start"}}),
    "keep_facts": ("Case-facts block?", "choice", {"options": {"yes": "yes", "no": "no - rely on the summary"}}),
    "trim_fields": ("Fields kept per lookup", "choice", {"options": {"5": "5 relevant fields", "12": "12 fields", "all": "all 40"}}),
    "n_examples": ("Complete format examples", "choice", {"options": {"0": "0", "1": "1", "2": "2", "3": "3"}}),
    "ex_style": ("Routing examples", "choice", {"options": {"reasoned": "varied, with “why X over Y”", "answers_only": "varied, answers only", "all_same": "all the same outcome"}}),
    "ex_formats": ("Extraction examples", "choice", {"options": {"varied": "approximate, imperial and metric", "one": "metric only"}}),
    "fix_mode": ("Raise the two bugs", "choice", {"options": {"together": "together, one message", "sequential": "one at a time"}}),
    "reviewer_kind": ("Reviewer", "choice", {"options": {"new_instance": "a new, independent instance", "same_session": "the generator's own session", "same_session_thinking": "same session + extended thinking"}}),
    "pass_plan": ("Review plan", "choice", {"options": {"per_file_integration": "per-file passes + integration pass", "per_file_only": "per-file passes only", "one_pass": "one pass over all 14 files"}}),
    "auto_threshold": ("Auto-post findings with confidence ≥", "choice", {"options": {"0.8": "0.8", "0.5": "0.5", "none": "(no confidence - post all)"}}),
    "cw_history": ("What each API call sends", "choice", {"options": {"full": "the whole conversation", "latest": "only the newest message", "recent3": "the last 3 messages (sliding window)"}}),
    "cw_explore": ("Where the exploration happens", "choice", {"options": {"subagent": "in a subagent's own window", "main": "in the main conversation"}}),
    "cw_rule": ("Where the persistent rule lives", "choice", {"options": {"claude_md": "CLAUDE.md", "chat": "said once in the conversation"}}),
    "cw_full": ("When the window is 95% full", "choice", {"options": {"compact": "/compact with a focus", "clear": "/clear"}}),
    "cw_upstream": ("What the analysis subagents return", "choice", {"options": {"structured": "key facts + citations + relevance", "verbose": "full reasoning chains"}}),
    "cw_budget": ("Report agent's input budget (tokens)", "choice", {"options": {"6000": "6,000", "12000": "12,000", "24000": "24,000"}}),
    "cf_block": ("Case-facts block", "choice", {"options": {"every_prompt": "in every prompt, outside the summary", "none": "none (facts only in the history)"}}),
    "cf_format": ("Block format", "choice", {"options": {"json": "structured (JSON)", "prose": "a prose note"}}),
    "cf_per_issue": ("One record per issue?", "choice", {"options": {"yes": "yes, keyed by order id", "flat": "no, one flat record"}}),
    "cf_updates": ("When a newer value arrives", "choice", {"options": {"overwrite": "overwrite (newest wins)", "set_once": "keep the first value"}}),
    "cf_customer": ("Capture customer-stated facts?", "choice", {"options": {"yes": "yes (deadlines, needs)", "tools_only": "no, tool data only"}}),
    "quality": ("Tool descriptions", "choice", {"options": {"detailed": "detailed (the docs' checklist)", "minimal": "one line each"}}),
    "web_tool": ("The web-results tool", "choice", {"options": {
        "renamed": "extract_web_results (renamed, web-only)", "overlapping": "analyze_content + a near-identical analyze_document"}}),
    "doc_tools": ("Document tools", "choice", {"options": {"split": "three purpose-specific tools", "generic": "one generic analyze_document"}}),
    "keyword_rule": ("System-prompt keyword rule", "choice", {"options": {
        "off": "none", "on": "“whenever the user mentions a document, use summarize_content”"}}),
    "formats": ("Formats & boundaries in lookup_order / get_customer", "choice", {"options": {"with": "stated", "without": "left out"}}),
    "payload": ("What the handoff carries", "choice", {"options": {
        "all": "ALL the findings", "first_two": "only the first two (“keep it short”)", "pointer": "a pointer: “the findings from earlier”"}}),
    "fmt": ("Shape of the findings", "choice", {"options": {
        "structured": "structured: claim + url, document, page", "prose": "prose: the claims in one paragraph"}}),
    "crossing": ("What crosses to the next agent", "choice", {"options": {
        "final": "the findings (final messages)", "raw": "the search agents' whole transcripts"}}),
    "n_findings": ("Number of findings", "int", {"min_value": 6, "max_value": 24, "step": 18}),
    "summary": ("Inject the phase-1 summary?", "choice", {"options": {"yes": "yes", "no": "no"}}),
    "state": ("Inject the saved state?", "choice", {"options": {"yes": "yes", "no": "no — just “continue”"}}),
    "team_rule_in": ("Where does the team rule (pnpm test) live?", "choice", {"options": {
        "project": "./CLAUDE.md (project, committed)", "user": "~/.claude/CLAUDE.md (user)", "local": "./CLAUDE.local.md (local, gitignored)"}}),
    "persona": ("Who is running Claude Code?", "choice", {"options": {"you": "you (the author)", "teammate": "a teammate on a fresh clone"}}),
    "import_at": ("Where are the standards imported?", "choice", {"options": {
        "package": "in each package's CLAUDE.md", "root": "all of them in the root CLAUDE.md"}}),
    "import_path": ("How is the package import path written?", "choice", {"options": {
        "relative_to_file": "relative to the importing file (../../standards/…)", "relative_to_root": "relative to the repo root (standards/…)"}}),
    "layout": ("Instruction layout", "choice", {"options": {"rules": "topic files in .claude/rules/", "monolith": "one monolithic CLAUDE.md"}}),
    "api_paths": ("API rule has paths: src/api/**?", "choice", {"options": {"yes": "yes (path-scoped)", "no": "no (always loaded)"}}),
    "claude_md": ("The repo's CLAUDE.md…", "choice", {"options": {
        "imports": "exists and imports @AGENTS.md", "no_import": "exists, no import", "none": "doesn't exist (AGENTS.md only)"}}),
    "strategy": ("Review strategy", "choice", {"options": {
        "chain": "per-file passes + integration pass", "per_file": "per-file passes only", "single": "one pass over everything"}}),
    "n_files": ("Files in the change", "int", {"min_value": 3, "max_value": 14, "step": 11}),
    "plan": ("Plan", "choice", {"options": {
        "adaptive": "map → prioritise → adapt", "mapped": "map → prioritise, never adapt", "fixed": "fixed alphabetical plan"}}),
    "budget": ("Action budget", "int", {"min_value": 3, "max_value": 12, "step": 1}),
    "pattern": ("Decomposition pattern", "choice", {"options": {"chaining": "prompt chaining (fixed steps)", "dynamic": "dynamic decomposition"}}),
    "triggers": ("Escalation criteria in the system prompt", "choice", {"options": {
        "explicit": "explicit triggers + few-shot examples (correct)", "sentiment": "escalate when the customer is upset",
        "confidence": "escalate when self-reported confidence < 0.7", "complex": "“escalate complex cases”"}}),
    "human_request": ("When the customer asks for a human…", "choice", {"options": {
        "immediate": "escalate immediately (correct)", "investigate_first": "investigate first, then escalate"}}),
    "matches": ("When a lookup returns several customers…", "choice", {"options": {
        "ask": "ask for another identifier (correct)", "pick_recent": "pick the one with the most recent order"}}),
    "gate": ("Verification before a refund is…", "choice", {"options": {
        "code": "a CODE gate around process_refund (correct)", "prompt_only": "only a line in the prompt"}}),
    "handoff": ("Handoff format", "choice", {"options": {
        "structured": "structured: customer id, root cause, refund amount, recommended action", "free_text": "one free-text message"}}),
    "how": ("How do you return to yesterday's work?", "choice", {"options": {
        "resume_name": "claude --resume refund-investigation (by name)", "continue": "claude --continue (most recent)",
        "fresh_nosummary": "a brand-new session, no summary"}}),
    "changed": ("What changed since the analysis?", "choice", {"options": {
        "none": "nothing", "one": "one file (the refund limit)", "most": "most files (a refactor; the limit moved)"}}),
    "approach": ("How do you continue?", "choice", {"options": {
        "resume_tell": "resume + name the changed files", "resume_silent": "resume, say nothing about changes",
        "fresh_summary": "new session + structured summary", "fresh_nosummary": "new session, no summary"}}),
    "fork": ("Branch with fork_session?", "choice", {"options": {
        "yes": "yes — fork the baseline for each approach", "no": "no — resume the same baseline for both"}}),
    "explored": ("Files read in the long session", "int", {"min_value": 1, "max_value": 30, "step": 1,
                 "help": "Each read adds ~800 simulated tokens to the context."}),
    "compact": ("Run /compact before asking?", "choice", {"options": {"no": "no", "yes": "yes"}}),
    "scratchpad": ("Keep a scratchpad of key findings?", "choice", {"options": {"no": "no", "yes": "yes — notes/refund-findings.md"}}),
    "manifest": ("Did agents export state before the crash?", "choice", {"options": {
        "yes": "yes — a manifest at a known location", "no": "no"}}),
    "allow_task": ("Spawn tool in allowedTools?", "choice", {"options": {
        "yes": "yes — \"Task\" (docs: \"Agent\") is allowed", "no": "no — the coordinator cannot spawn subagents"}}),
    "context_mode": ("What does each subagent receive?", "choice", {"options": {
        "full_prompt": "the complete findings, in its prompt (correct)",
        "assume_inherited": "just a short label — assume it inherits context (wrong)"}}),
    "parallel": ("Delegation style", "choice", {"options": {
        "yes": "parallel — all Task calls in ONE response", "no": "one subagent per turn"}}),
    "max_concurrent": ("Concurrent-subagent limit", "int", {"min_value": 1, "max_value": 20, "step": 1,
                       "help": "Docs default: 20 running at once. Extra spawns are refused, not queued."}),
    "decomposition": ("How is the topic split?", "choice", {"options": {
        "distinct": "distinct areas, no overlap (correct)", "overlapping": "overlapping areas (duplicated work)",
        "narrow": "only the single most prominent area (too narrow)"}}),
    "review_gaps": ("Coordinator reviews the draft for gaps?", "choice", {"options": {
        "yes": "yes — re-delegate targeted searches", "no": "no — accept the first draft"}}),
    "fail_source": ("A source fails?", "choice", {"options": {
        "no": "no — every search works", "yes": "yes — the first film search times out"}}),
    "findings_format": ("Findings passed between agents", "choice", {"options": {
        "structured": "structured: claim + source url/document/page", "claims_only": "claims only — metadata dropped"}}),
    "prompt_style": ("How is the coordinator prompted?", "choice", {"options": {
        "goal": "goals + quality criteria (correct)", "procedural": "fixed step-by-step procedure"}}),
    "searcher_has_search": ("Searcher's tools (AgentDefinition.tools)", "choice", {"options": {
        "yes": "includes web_search", "no": "web_search left out"}}),
    "max_budget_usd": ("max_budget_usd (SIMULATED $)", "float", {"min_value": 0.0, "max_value": 0.05, "step": 0.0005,
                       "format": "%.4f", "help": "0 = no limit (the SDK default). Illustrative rates, not real pricing."}),
}


def _bubble(text: str, role: str = "assistant", avatar: str | None = None) -> None:
    with st.chat_message(role, avatar=avatar):
        st.markdown(text)


def _render_run(run: dict) -> None:
    for ev in run["events"]:
        t = ev["type"]
        if t == "user":
            _bubble(ev["text"], "user")
            if not ev["intent"]:
                st.caption("No order mentioned → the simulated model answers without tools (a model-driven decision).")
        elif t == "api":
            parts = []
            for b in ev["blocks"]:
                if b["type"] == "text":
                    parts.append(b["text"] or "*(empty text)*")
                else:
                    parts.append(f"`{b['type']}: {b['name']}({b['input']})`")
            body = "  \n".join(parts) if parts else "*(empty content — the response has no blocks)*"
            _bubble(body)
            det = f" · stop_details = `{ev['stop_details']}`" if ev["stop_details"] else ""
            seq = f" · stop_sequence = `{ev['stop_sequence']}`" if ev["stop_sequence"] else ""
            st.caption(f"call #{ev['call']} · {ev['model']} · max_tokens {ev['max_tokens']} · in {ev['in']} / out {ev['out']} "
                       f"tokens · ${ev['cost']:.4f} (running ${ev['spent']:.4f})")
            st.markdown(f"**`stop_reason = {ev['stop_reason']}`**{det}{seq}  \n➡️ *{ev['action']}*")
        elif t == "tool":
            _bubble(f"ran `{ev['name']}({ev['args']})` → `{ev['result'][:110]}`", avatar="🛠️")

    res = run["result"]
    lines = (f"**Result: `{res['subtype']}`**  \n{res['why']}  \n"
             f"API calls {res['api_calls']} · tool turns {res['tool_turns']} · simulated spend ${res['spent']:.4f}")
    if res["text"]:
        lines += f"  \nText returned: “{res['text']}”"
    tag = ("SDK result subtype" if res["source"] == "sdk" else
           "this playground's label — not an SDK subtype")
    if res["ok"]:
        st.success(lines)
    elif res["subtype"].startswith("error_"):
        st.error(lines)
    else:
        st.warning(lines)
    st.caption(f"Label type: {tag}.")


def _render_research(run: dict) -> None:
    ev0 = run["events"][0]
    with st.expander("Coordinator system prompt (built from your settings) and its tools"):
        st.code(ev0["system"], language="text")
        st.caption(f"Tools offered to the coordinator: {ev0['tools'] or 'none — it cannot spawn subagents'}")
    for ev in run["events"][1:]:
        t = ev["type"]
        if t == "coord":
            parts = [ev["text"]] if ev["text"] else []
            for c in ev["calls"]:
                parts.append(f"`Task({c['kind']})` — {c['desc']}")
            _bubble("  \n".join(parts) if parts else "*(final answer)*", avatar="🧭")
            st.caption(f"coordinator call #{ev['turn']} · in {ev['in']} tokens · **stop_reason = {ev['stop_reason']}** · "
                       f"{len(ev['calls'])} Task call(s) in this response · it has seen {ev['seen_chars']} chars of subagent output")
            for c in ev["calls"]:
                with st.expander(f"Prompt the coordinator wrote for {c['kind']} — the ONLY context that subagent can get"):
                    st.code(c["prompt"], language="text")
        elif t == "subagent":
            with st.expander(f"🤖 {ev['kind']} subagent ran (simulated {ev['seconds']} s) → result"):
                st.markdown(f"**It received:** `{ev['received'][:300]}`")
                st.markdown(f"**Its tools:** {ev['tools'] or 'none'}")
                for line in ev["tool_log"]:
                    st.markdown(f"- 🛠️ `{line}`")
                st.markdown("**Only this final message goes back to the coordinator:**")
                st.code(ev["result"], language="text")
        elif t == "limit":
            st.warning(ev["text"])
        elif t == "error":
            st.error(ev["text"])
    res = run["result"]
    body = res["report"] or "*(no final answer)*"
    box = st.success if res["ok"] else st.warning
    box(f"**Final answer**  \n{body}")
    c = st.columns(5)
    c[0].metric("Subagent runs", res["runs"])
    c[1].metric("Coordinator turns", res["turns"])
    c[2].metric("Simulated time", f"{res['seconds']} s")
    c[3].metric("Areas covered", f"{len(res['covered'])}/3")
    c[4].metric("Citations", res["cited"])
    for n in res["notes"]:
        st.markdown(f"⚠️ {n}")
    if res["ok"]:
        st.caption("No problems detected in this run.")
    st.caption("Simulated time = per response, the slowest subagent (calls in ONE response run concurrently), summed over "
               "responses. The keyword-driven coordinator is a stand-in for real instruction-following.")


def _render_stop(run: dict) -> None:
    req = run["request"]
    st.markdown("**Request sent to the simulated model**")
    st.json({k: v for k, v in req.items()}, expanded=False)
    st.caption(f"HTTP status: {run['http']}")
    if run["response"]:
        st.markdown("**Response — read `stop_reason` first**")
        r = run["response"]
        st.markdown(f"**`stop_reason = {r['stop_reason']}`** · `stop_details = {r['stop_details']}` · "
                    f"`stop_sequence = {r['stop_sequence']!r}` · in {r['usage']['input_tokens']} / out {r['usage']['output_tokens']} tokens")
        st.json(r["content"] if r["content"] else [], expanded=True)
        if not r["content"]:
            st.caption("content is an EMPTY list — no text, no tool call.")
    else:
        st.error(run["raised"])
    box = st.success if run["ok"] else st.error
    box(f"**Your handler chose:** `{run['action']}` — {run['chosen_meaning']}  \n"
        f"**The docs call for:** `{run['expected']}` — {run['expected_meaning']}  \n"
        + ("✅ Correct." if run["ok"] else "❌ Mishandled."))
    st.markdown(f"**Why it matters:** {run['consequence']}")


def _render_session(run: dict) -> None:
    for line in run["lines"]:
        st.markdown(f"- {line}")
    _bubble(run["answer"])
    (st.success if run["ok"] else st.error)(("✅ " if run["ok"] else "❌ ") + run["why"])
    cols = st.columns(max(1, len(run["metrics"])))
    for col, (k, v) in zip(cols, run["metrics"].items()):
        col.metric(k, str(v))


def _render_escalation(run: dict) -> None:
    with st.expander("System prompt built from your settings"):
        st.code(run["system"], language="text")
    for kind, text in run["steps"]:
        if kind == "customer":
            _bubble(text, "user")
        elif kind in ("agent", "agent_note"):
            _bubble(text or "*(no text)*")
        elif kind == "blocked":
            st.warning(f"🛡️ gate: {text}")
        else:
            st.caption(f"🛠️ {text}")
    if run["handoffs"]:
        st.markdown("**Handoff the human receives** (they can't see the conversation):")
        st.json(run["handoffs"][-1])
    if run["refunds"]:
        st.markdown("**Refunds issued:**")
        st.json(run["refunds"])
    outcome = ("Escalated to a human" + (f" after {run['tools_before']} tool call(s)" if run["tools_before"] is not None else "")
               if run["escalated"] else ("Resolved by the agent" if run["refunds"] else "No escalation, no refund"))
    (st.error if run["notes"] else st.success)(f"**{outcome}.**" + ("".join(f"  \n⚠️ {n}" for n in run["notes"])))


def _render_handoff(run: dict) -> None:
    with st.expander(f"The exact prompt the downstream agent received ({run['metrics'].get('prompt tokens', '?')} tokens) — its ONLY context"):
        p = run["prompt"]
        st.code(p if len(p) < 4000 else p[:4000] + f"\n… [{len(p) - 4000} more characters]", language="text")
    _bubble(run["output"])
    (st.success if run["ok"] else st.error)(("✅ " if run["ok"] else "❌ ") + run["why"])
    cols = st.columns(len(run["metrics"]))
    for col, (k, v) in zip(cols, run["metrics"].items()):
        col.metric(k, str(v))


def _render_memory(run: dict) -> None:
    st.markdown(f"**/memory — {run['persona']}, with `{run['opened']}` open**")
    for x in run["loaded"]:
        st.markdown(("- ⚠️ " if x.get("missing") else "- ") + f"`{x['path']}` — {x['why']}")
    st.markdown("**Instructions in context:** " + (", ".join(run["received"]) or "none"))
    if run["notes"]:
        st.error("  \n".join("⚠️ " + n for n in run["notes"]))
    else:
        st.success("✅ Everyone gets what they should, and only where it applies.")
    with st.expander("The instruction files in this layout"):
        for k, v in run["files"].items():
            st.markdown(f"`{k}` ({len(v.splitlines())} lines)")
            st.code(v if len(v) < 600 else v[:600] + "\n…", language="markdown")


def _render_decomp(run: dict) -> None:
    for line in run["lines"]:
        st.markdown(f"- {line}")
    (st.success if run["ok"] else st.error)(("✅ " if run["ok"] else "❌ ") + run["score"]
                                           + (f"  \nMissed: {run['missed']}" if run["missed"] else ""))


def _html_table(rows: list) -> str:
    import html as _h
    if not rows:
        return ""
    heads = list(rows[0])
    head = "".join(f"<th>{_h.escape(str(h))}</th>" for h in heads)
    body = "".join("<tr>" + "".join(f"<td>{_h.escape(str(r.get(h, '')))}</td>" for h in heads) + "</tr>" for r in rows)
    return f'<div class="wb-card"><table class="wb-table"><tr>{head}</tr>{body}</table></div>'


def _render_toolsel(run: dict) -> None:
    verdict = "" if run["ok"] is None else (" ✅ right kind of tool" if run["ok"] else f" ❌ this request needs a “{run['expected']}” tool")
    st.markdown(f"**Picked:** `{run['tool']}` ({run['kind']}) · **input:** `{run['input'] or {}}`{verdict}")
    st.caption(run["why"])
    st.markdown(_html_table(run["rows"]), unsafe_allow_html=True)
    with st.expander("System prompt used"):
        st.code(run["system"], language="text")


def _render_toolchoice(run: dict) -> None:
    if run["request"]:
        st.markdown("**Request**")
        st.json(run["request"], expanded=False)
    if run["error"]:
        st.error(run["error"])
    if run["response"]:
        st.markdown(f"**Response** — `stop_reason = {run['response']['stop_reason']}`")
        st.json(run["response"]["content"], expanded=True)
    for line in run["lines"]:
        st.markdown(f"- {line}")
    if run["notes"]:
        st.error("  \n".join("⚠️ " + n for n in run["notes"]))
    else:
        st.success("✅ The guarantee you needed held.")


def _render_mcp(run: dict) -> None:
    for name, content in run.get("files", {}).items():
        st.markdown(f"**{name}**")
        st.json(content, expanded=False)
    for line in run["lines"]:
        st.markdown(f"- {line}")
    if run["notes"]:
        st.error("  \n".join("⚠️ " + n for n in run["notes"]))
    else:
        st.success("✅ Works for everyone, and the agent recovers correctly.")


def _render_hooks(run: dict) -> None:
    for line in run["lines"]:
        st.markdown(f"- {line}")
    if run["notes"]:
        st.error("  \n".join("⚠️ " + n for n in run["notes"]))
    else:
        st.success("✅ The rule held and the agent did the right thing.")


def _render_lines(run: dict) -> None:
    for line in run["lines"]:
        st.markdown(f"- {line}")
    if run["notes"]:
        st.error("  \n".join("⚠️ " + n for n in run["notes"]))
    else:
        st.success("✅ That worked the way it should.")


def _render_fork(slug: str, spec) -> None:
    """Session fork demo (docs: agent-sdk/sessions § Fork) — no model involved; it shows what a fork is."""
    base = f"pg_{slug.replace('-', '_')}_{spec.key}"
    key = f"{base}_sessions"
    if key not in st.session_state:
        st.session_state[key] = {"S1": {"parent": None, "history": [
            "user: Analyze the auth module and suggest improvements",
            "assistant: (reads 12 files) Found: session tokens never expire; passwords hashed with a weak scheme; ...",
            "user: Summarise the risks in three bullets",
            "assistant: 1) no token expiry  2) weak hashing  3) no rate limiting"]}}
    sessions = st.session_state[key]
    st.markdown("**The shared analysis baseline is session `S1`.** Fork it to try a different direction without losing it.")
    c1, c2, c3 = st.columns([2, 2, 2])
    parent = c1.selectbox("Fork from", list(sessions), key=f"{base}_parent")
    if c2.button("🍴 Fork this session", key=f"{base}_fork"):
        new_id = f"S{len(sessions) + 1}"
        sessions[new_id] = {"parent": parent, "history": list(sessions[parent]["history"])}
        st.session_state[f"{base}_target"] = new_id
    target = c3.selectbox("Add a message to", list(sessions), key=f"{base}_target")
    msg = st.text_input("Message", value="Instead of JWT, outline how OAuth2 would work", key=f"{base}_msg")
    if st.button("▶ Send to that session", key=f"{base}_send"):
        sessions[target]["history"] += [f"user: {msg}", "assistant: (works on it… simulated reply)"]
    cols = st.columns(len(sessions))
    for col, (sid, data) in zip(cols, sessions.items()):
        with col:
            st.markdown(f"**`{sid}`**" + (f" — forked from `{data['parent']}`" if data["parent"] else " — original"))
            st.caption(f"{len(data['history'])} messages")
            for line in data["history"]:
                st.markdown(f"- {line}")
    if st.button("🗑 Reset sessions", key=f"{base}_reset"):
        del st.session_state[key]
        st.rerun()
    st.caption("Per the docs: a fork is a NEW session that starts with a copy of the original's history; the original stays "
               "unchanged and both can be resumed separately. Forking branches the conversation, not the filesystem — file "
               "edits a forked agent makes are real. (This demo is a simulation of the session bookkeeping; no model runs.)")


def _knob_widget(base: str, knob: str, default):
    label, kind, extra = _KNOBS[knob]
    key = f"{base}_{knob}"
    if kind == "int":
        return st.number_input(label, value=int(default), key=key, **extra)
    if kind == "float":
        return st.number_input(label, value=float(default), key=key, **extra)
    if kind == "text":
        return st.text_input(label, value=str(default), key=key, **extra)
    options = list(extra["options"])
    return st.selectbox(label, options, index=options.index(default), key=key,
                        format_func=lambda o: extra["options"][o])


def _render_tab(slug: str, spec) -> None:
    base = f"pg_{slug.replace('-', '_')}_{spec.key}"
    hist_key = f"{base}_history"

    if spec.exam_source:
        st.markdown(f"**{resolve_source(spec.exam_source)}**")
    else:
        st.markdown("**📘 Official docs — beyond the guide's wording (not gold)**")
    st.info(f"🧭 **Mental model.** {spec.mental_model}")
    st.markdown(spec.meaning)
    st.caption(f"Docs: {spec.docs}")

    if spec.engine == "fork":
        _render_fork(slug, spec)
        if spec.try_this:
            with st.expander("Try this next"):
                for i, t in enumerate(spec.try_this, 1):
                    st.markdown(f"{i}. {t}")
        return

    st.markdown("**Constraints you control (the developer side)**")
    clash = set(spec.knobs) & {"send", "clear", "msg", "history"}   # these names are taken by the tab's own widget keys
    assert not clash, f"knob name(s) {clash} collide with playground widget keys"
    values = {}
    if spec.knobs:
        cols = st.columns(min(3, len(spec.knobs)))
        for i, knob in enumerate(spec.knobs):
            with cols[i % len(cols)]:
                fallback = {"research": ResearchConfig, "stop": StopConfig, "session": SessionConfig, "escalation": EscalationConfig, "handoff": HandoffConfig,
                 "memory": MemoryConfig, "decomp": DecompConfig, "toolsel": ToolSelConfig,
                 "toolchoice": ToolChoiceConfig, "mcp": McpConfig,
                 "hooks": HooksConfig, "evaltools": EvalConfig, "builtin": BuiltinConfig, "rules": RulesConfig, "plan": PlanConfig, "skills": SkillsConfig, "checkpoint": CheckpointConfig, "review": ReviewConfig, "batch": BatchConfig, "extract": ExtractConfig, "attention": AttentionConfig, "fewshot": FewshotConfig, "mpreview": MPReviewConfig, "ctxwin": CtxWinConfig, "casefacts": CaseFactsConfig}.get(
                    spec.engine, PlayConfig).__dataclass_fields__.get(knob)
                values[knob] = _knob_widget(base, knob, spec.defaults.get(knob, fallback.default if fallback else 0))
    else:
        st.caption("No knobs on this tab — it shows the normal loop. Try different messages.")

    st.markdown("**Say something to the agent** (each message starts a fresh run)")
    msg = st.text_input("Your message", value=spec.examples[0], key=f"{base}_msg", label_visibility="collapsed")
    st.caption("Try: " + "  ·  ".join(f"`{e}`" for e in spec.examples))
    c1, c2, _ = st.columns([1, 1, 4])
    send = c1.button("▶ Send", type="primary", key=f"{base}_send")
    if c2.button("🗑 Clear", key=f"{base}_clear"):
        st.session_state[hist_key] = []

    if send:
        if not msg.strip():
            st.warning("Type a message first.")
        else:
            with st.spinner("Running the simulated agent…"):
                if spec.engine == "research":
                    cfg = ResearchConfig(**values)
                    run = run_research(msg.strip(), cfg)
                elif spec.engine in ("handoff", "memory", "decomp", "toolsel", "toolchoice", "mcp", "hooks", "builtin", "evaltools", "rules", "plan", "skills", "checkpoint", "review", "batch", "extract", "attention", "fewshot", "mpreview", "ctxwin", "casefacts"):
                    cls, fn = {"handoff": (HandoffConfig, run_handoff), "memory": (MemoryConfig, run_memory),
                               "decomp": (DecompConfig, run_decomp), "toolsel": (ToolSelConfig, run_toolsel),
                               "toolchoice": (ToolChoiceConfig, run_toolchoice), "mcp": (McpConfig, run_mcp),
                               "hooks": (HooksConfig, run_hooks), "evaltools": (EvalConfig, run_eval), "builtin": (BuiltinConfig, run_builtin), "rules": (RulesConfig, run_rules), "plan": (PlanConfig, run_plan), "skills": (SkillsConfig, run_skills), "checkpoint": (CheckpointConfig, run_checkpoint), "review": (ReviewConfig, run_review), "batch": (BatchConfig, run_batch), "extract": (ExtractConfig, run_extract), "attention": (AttentionConfig, run_attention), "fewshot": (FewshotConfig, run_fewshot), "mpreview": (MPReviewConfig, run_mpreview), "ctxwin": (CtxWinConfig, run_ctxwin), "casefacts": (CaseFactsConfig, run_casefacts)}[spec.engine]
                    cfg = cls(mode=spec.condition, **values)
                    run = fn(msg.strip(), cfg)
                elif spec.engine == "escalation":
                    cfg = EscalationConfig(scenario=spec.condition, **values)
                    run = run_escalation(msg.strip(), cfg)
                elif spec.engine == "session":
                    cfg = SessionConfig(mode=spec.condition, **values)
                    run = run_play(msg.strip(), cfg)
                elif spec.engine == "stop":
                    cfg = StopConfig(condition=spec.condition, **values)
                    run = run_stop(msg.strip(), cfg)
                else:
                    cfg = PlayConfig(condition=spec.condition,
                                     **{**({"max_tokens": 1024} if "max_tokens" not in values else {}),
                                        **{k: (tuple(s for s in [v] if s) if k == "stop_sequences" else v)
                                           for k, v in values.items()}})
                    run = run_agent(msg.strip(), cfg)
            hist = st.session_state.setdefault(hist_key, [])
            hist.insert(0, {"cfg": cfg, "run": run})
            del hist[HISTORY_KEEP:]

    for i, item in enumerate(st.session_state.get(hist_key, [])):
        with st.container(border=(i == 0)):
            if i == 0:
                st.markdown("**Latest run**")
            else:
                st.markdown(f"*Earlier run #{i}*")
            {"research": _render_research, "stop": _render_stop, "session": _render_session, "escalation": _render_escalation,
             "handoff": _render_handoff, "memory": _render_memory, "decomp": _render_decomp,
             "toolsel": _render_toolsel, "toolchoice": _render_toolchoice, "mcp": _render_mcp, "hooks": _render_hooks, "evaltools": _render_lines, "builtin": _render_lines, "rules": _render_lines, "plan": _render_lines, "skills": _render_lines, "checkpoint": _render_lines, "review": _render_lines, "batch": _render_lines, "extract": _render_lines, "attention": _render_lines, "fewshot": _render_lines, "mpreview": _render_lines, "ctxwin": _render_lines, "casefacts": _render_lines}.get(spec.engine, _render_run)(item["run"])

    if spec.try_this:
        with st.expander("Try this next"):
            for i, t in enumerate(spec.try_this, 1):
                st.markdown(f"{i}. {t}")


def render_playground(slug: str, content) -> None:
    st.subheader("💬 Agent playground — type a message, watch how the agent handles it")
    st.markdown(content.playground_intro)
    st.markdown(
        '<div class="cc-sim"><strong>SIMULATED.</strong> The agent loop is real workbench code, but the “model” is a '
        f'scripted stand-in (<code>utils/mock_claude.py</code>) — not Claude. Token sizes are invented and dollars use '
        f'illustrative rates (${IN_RATE_PER_1K}/1K in, ${OUT_RATE_PER_1K}/1K out), <em>not real pricing</em>. It runs '
        "in this app's process; no API key, no cost.</div>", unsafe_allow_html=True)
    tabs = st.tabs([t.label for t in content.playground])
    for tab, spec in zip(tabs, content.playground):
        with tab:
            _render_tab(slug, spec)
