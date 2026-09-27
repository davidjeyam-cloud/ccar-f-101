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
                 "memory": MemoryConfig, "decomp": DecompConfig}.get(
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
                elif spec.engine in ("handoff", "memory", "decomp"):
                    cls, fn = {"handoff": (HandoffConfig, run_handoff), "memory": (MemoryConfig, run_memory),
                               "decomp": (DecompConfig, run_decomp)}[spec.engine]
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
             "handoff": _render_handoff, "memory": _render_memory, "decomp": _render_decomp}.get(spec.engine, _render_run)(item["run"])

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
