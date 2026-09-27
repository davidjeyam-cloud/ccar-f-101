"""
Generic renderer for a CONCEPTS page. A built concept supplies a ConceptContent
(utils/concepts_content/<slug>.py); this module turns it into the page:

    Summary → What it is → How it works (flowchart) → Where you'll see it →
    Code lab (edit + Run) → Looks right, isn't → Side-by-side → Decision tree →
    Practice → FAQ → Related

Section order follows the community concept list's layout; the runnable code
lab and the flowchart that lights up along the path your run took are what that
list does not have. Concepts that are not built yet (or that the guide excludes)
get an honest stub instead of a blank page.

Everything the lab's "model" says is SIMULATED and labelled that way on screen.
"""

import html
import importlib
import re

import streamlit as st

from utils import concepts_map as cm
from utils.concept_types import CLAIM_KINDS, ConceptContent
from utils.course_map import DOMAINS
from utils.guide_index import point_ref, resolve_source, scenario_ref, ts_ref
from utils.lab_runner import run_lab
from utils.playground_ui import render_playground
from utils.mock_claude import SCENARIO_ORDER, SCENARIOS
from utils.progress import render_progress_ticks
from utils.styles import ACCENT_COMING, ACCENT_COMPLETE, ACCENT_CURRENT, C, apply_dashboard_css, phase_header
from utils.trace import render_trace

LAB_TIMEOUT_SECONDS = 10


def load_content(slug: str) -> ConceptContent | None:
    if not cm.is_built(slug):
        return None
    module = importlib.import_module(f"utils.concepts_content.{cm.content_module_name(slug)}")
    return module.CONTENT


def _inline(text: str) -> str:
    """Escape HTML, then turn `code` and **bold** into tags (for table cells)."""
    out = html.escape(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)


def _table(headers, rows) -> str:
    head = "".join(f"<th>{_inline(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="wb-card"><table class="wb-table"><tr>{head}</tr>{body}</table></div>'


def _chips(concept: cm.Concept) -> str:
    chips = []
    if concept.domain:
        name, weight, _ = DOMAINS[concept.domain]
        chips.append(f"Domain {concept.domain} · {name} ({weight})")
    if cm.kind(concept) == "extra":
        chips.append("➕ EXTRA — not on the CCAR-F exam")
    elif cm.kind(concept) == "exam":
        chips.append("⭐ EXAM TOPIC — " + " · ".join(ts_ref(t).replace("Guide ", "Guide ") for t in concept.guide_refs))
    else:
        chips.append(f"{cm.STATUS_ICON[concept.status]} {cm.STATUS_LABEL[concept.status]}")
    if concept.guide_refs:
        chips.append("Guide: " + ", ".join(f"TS {t}" for t in concept.guide_refs))
    spans = "".join(f'<span class="cc-chip{" cc-chip-exam" if c.startswith("⭐") else ""}">{html.escape(c)}</span>'
                    for c in chips)
    return f'<div class="cc-chips">{spans}</div>'


def _page_css(code_key: str) -> None:
    st.markdown(f"""
<style>
.cc-chips {{ display:flex; flex-wrap:wrap; gap:8px; margin:-8px 0 18px 0; }}
.cc-chip {{ background:{C['bg_overlay']}; border:1px solid {C['border_sub']}; color:{C['text_sec']};
           border-radius:20px; padding:3px 12px; font-size:0.78rem; font-weight:600; }}
.cc-chip-exam {{ background:#FEF3C7; border:1.5px solid #D97706; color:#92400E; }}
.cc-exam {{ background:#FFFBEB; border:2px solid #D97706; border-left:8px solid #D97706; border-radius:10px;
           padding:12px 16px; margin:6px 0 14px 0; color:{C['text_prim']}; }}
.cc-exam h4 {{ margin:0 0 6px 0; color:#92400E; }}
.wb-table td, .wb-table th {{ white-space: normal !important; overflow-wrap: anywhere; word-break: break-word; vertical-align: top; }}
.cc-sim {{ background:rgba(217,119,6,0.10); border:1px solid {C['orange']}; color:{C['text_prim']};
          border-radius:10px; padding:10px 14px; font-size:0.88rem; margin-bottom:12px; }}
.st-key-{code_key} textarea {{ font-family: Consolas, 'Courier New', monospace !important;
                               font-size: 0.85rem !important; line-height: 1.45 !important; tab-size: 4; }}
</style>""", unsafe_allow_html=True)


# ── Lab ────────────────────────────────────────────────────────────────────────


def _api_call_rows(trace: dict) -> list:
    rows = []
    for e in trace["events"]:
        if e["kind"] != "api_call":
            continue
        parts = []
        for b in e["blocks"]:
            if b["type"] == "text":
                parts.append(f'text: "{b["text"]}"')
            else:
                parts.append(f'tool_use: {b["name"]}({b["input"]})')
        row = {"call #": e["call"]}
        if e.get("role") or any(x.get("role") for x in trace["events"] if x["kind"] == "api_call"):
            row["agent role"] = e.get("role") or "coordinator"
        row.update({"stop_reason": e["stop_reason"], "messages sent": e["n_messages"],
                    "in tokens (simulated)": e["input_tokens"], "out tokens (simulated)": e["output_tokens"],
                    "response content": "  +  ".join(parts)})
        rows.append(row)
    return rows


def _tool_rows(trace: dict) -> list:
    return [{"#": i, "tool": e["name"], "arguments": str(e["args"]), "result": e["result"][:140]}
            for i, e in enumerate((e for e in trace["events"] if e["kind"] == "tool_exec"), 1)]


def _render_result(content: ConceptContent, stored: dict) -> None:
    res, scenario = stored["res"], stored["scenario"]

    if res.error:
        st.error(res.error)
        return
    if res.timed_out:
        st.error(f"⏱ Timed out after {LAB_TIMEOUT_SECONDS} s and was stopped. That is usually an infinite loop — "
                 "the exact failure a loop with no correct stop condition produces.")
        if res.stdout:
            st.code(res.stdout, language="text")
        return

    trace = res.trace
    raised = trace["status"]["raised"] if trace else None
    if raised:
        st.warning(f"Your code raised: `{raised[:300]}`")
    else:
        st.success(f"Run finished in {res.seconds:.1f} s.")

    st.markdown("**Output** (what your code printed)")
    st.code(res.stdout or "(no output)", language="text")
    if res.stderr.strip():
        with st.expander("stderr / traceback"):
            st.code(res.stderr, language="text")
    if not trace:
        st.info("The run produced no trace, so the flowchart and checks are unavailable.")
        return

    ok, expected, observed = content.check_outcome(scenario, trace)
    box = st.success if ok else st.error
    box(f"**Result check — {'meets' if ok else 'does NOT meet'} this scenario's expected outcome.**  \n"
        f"Expected: {expected}.  \nYour run: {observed}")
    st.caption("A learning aid, not a grader: it reads the fake backend's ledger and the simulated model's "
               "stop reasons.")

    st.markdown("**Your run, traced on the flowchart** — 🟩 executed correctly · 🟥 where it went wrong · ⬜ not reached")
    st.graphviz_chart(content.flow_dot(content.node_states(trace)))

    def _show(rows: list, empty_text: str) -> None:
        if rows:
            # HTML table, not st.dataframe: dataframe cells truncate long text instead of wrapping it
            headers = list(rows[0])
            st.markdown(_table(headers, [[str(r.get(h, "")) for h in headers] for r in rows]), unsafe_allow_html=True)
        else:
            st.write(empty_text)

    def _tab_calls():
        st.caption("SIMULATED model — every response below was scripted by utils/mock_claude.py, not generated by Claude.")
        _show(_api_call_rows(trace), "No model calls.")

    def _tab_tools():
        _show(_tool_rows(trace), "No tools ran.")

    def _tab_ledger():
        ledger = trace["ledger"]
        st.markdown("**Refunds issued** (`duplicate: True` = the backend refunded an already-refunded order)")
        _show(ledger["refunds"], "None.")
        st.markdown("**Confirmations sent**")
        _show(ledger["confirmations"], "None.")

    tabs = [("Model calls", _tab_calls), ("Tool runs", _tab_tools)]
    if content.show_ledger:
        tabs.append(("Backend ledger", _tab_ledger))
    render_trace(*tabs)


def _render_lab(slug: str, content: ConceptContent) -> None:
    p = "lab_" + slug.replace("-", "_")
    vkey, skey, ckey, rkey = f"{p}_variant", f"{p}_scenario", f"{p}_code", f"{p}_result"
    variants = {v.key: v for v in content.variants}
    scenario_ids = list(content.scenarios) or SCENARIO_ORDER

    if ckey not in st.session_state:
        first = content.variants[0]
        st.session_state[vkey], st.session_state[skey], st.session_state[ckey] = first.key, first.scenario, first.code

    def _load_variant() -> None:
        v = variants[st.session_state[vkey]]
        st.session_state[ckey], st.session_state[skey] = v.code, v.scenario
        st.session_state.pop(rkey, None)

    _page_css(ckey)
    st.subheader("🧪 Code lab — edit it, run it, break it")
    st.markdown(content.lab_intro)
    st.markdown(
        '<div class="cc-sim"><strong>SIMULATED.</strong> The “model” here is a scripted stand-in '
        '(<code>utils/mock_claude.py</code>) that speaks the Claude Messages-API shape — no API call, no key, '
        'no cost, and not real Claude. It exists so failures are reproducible. Your code runs in a separate '
        f'Python process on this machine ({LAB_TIMEOUT_SECONDS} s timeout, no API keys in its environment); '
        'only run code you understand.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])
    with c1:
        st.selectbox("Start from", list(variants), key=vkey, on_change=_load_variant,
                     format_func=lambda k: variants[k].label)
    with c2:
        st.selectbox("Scenario (simulated model + fake backend)", scenario_ids, key=skey,
                     format_func=lambda k: SCENARIOS[k].title)
    st.caption(SCENARIOS[st.session_state[skey]].description)

    v = variants[st.session_state[vkey]]
    with st.expander("What to observe · why · what to do instead", expanded=True):
        st.markdown(f"**Observe:** {v.observe}")
        st.markdown(f"**{'Why it works' if v.kind == 'correct' else 'Why it fails'}:** {v.why}")
        if v.fix:
            st.markdown(f"**Do this instead:** {v.fix}")

    st.text_area("Python — edit freely", key=ckey, height=470, label_visibility="collapsed")

    b1, b2, _ = st.columns([1, 1, 4])
    run = b1.button("▶ Run", type="primary", key=f"{p}_run")
    b2.button("↺ Reset code", key=f"{p}_reset", on_click=_load_variant)

    if run:
        code = st.session_state[ckey]
        if not code.strip():
            st.warning("The editor is empty.")
        else:
            with st.spinner("Running in a separate Python process…"):
                res = run_lab(code, st.session_state[skey], timeout=LAB_TIMEOUT_SECONDS)
            st.session_state[rkey] = {"res": res, "scenario": st.session_state[skey]}

    if rkey in st.session_state:
        _render_result(content, st.session_state[rkey])

    with st.expander("Try this next — experiments"):
        for i, text in enumerate(content.experiments, 1):
            st.markdown(f"{i}. {text}")


# ── Page ───────────────────────────────────────────────────────────────────────


def _render_exam_points(concept: cm.Concept, content: ConceptContent) -> None:
    """The gold box: exactly what the guide demands, with exact references (TS, bullet, page)."""
    if not content.exam_points:
        return
    st.markdown(
        '<div class="cc-exam"><h4>⭐ What the exam demands — from the official guide</h4>'
        "The candidate is expected to know or do these. Each row is paraphrased and pinned to its exact place in the "
        "guide PDF. <em>Bullet numbers count the bullets in the order they appear (the guide itself does not number "
        "them).</em></div>", unsafe_allow_html=True)
    rows = [(str(i), "⭐ " + point_ref(p.ts, p.kind, p.n), p.text, p.lab or "—")
            for i, p in enumerate(content.exam_points, 1)]
    st.markdown(_table(("#", "Guide reference", "What the exam expects", "Where this page exercises it"), rows),
                unsafe_allow_html=True)
    where = " · ".join(ts_ref(t) for t in concept.guide_refs)
    st.caption(f"Source: official exam guide v1.0 (local PDF, not redistributed) — {where}. Everything not marked ⭐ is "
               "beyond the guide's wording (official docs or my recommendation).")


def _render_questions(slug: str, content: ConceptContent) -> None:
    st.caption("Original practice items written for this workbench — not real exam questions. Items marked 📘 test "
               "official-docs behaviour beyond the guide's task-statement text; they are not in the question bank.")
    for i, q in enumerate(content.questions, 1):
        with st.container(border=True):
            if q.basis == "docs":
                st.caption("📘 docs-based item (beyond the guide's wording)")
            choice = st.radio(f"**Q{i}.** {q.q}", q.opts, index=None, key=f"q_{slug.replace('-', '_')}_{i}")
            if st.button("Check answer", key=f"qc_{slug.replace('-', '_')}_{i}"):
                if choice is None:
                    st.warning("Pick an option first.")
                elif q.opts.index(choice) == q.ans:
                    st.success(f"Correct. {q.explain}")
                else:
                    st.error(f"Not quite. The best answer is: **{q.opts[q.ans]}**  \n{q.explain}")


def _render_full(concept: cm.Concept, content: ConceptContent) -> None:
    domain_label = f"CONCEPTS · D{concept.domain} · {cm.DOMAIN_SHORT[concept.domain]}" if concept.domain else "CONCEPTS"
    st.markdown(phase_header(domain_label, f"🧪 {concept.code} {concept.title}" if concept.code else f"🧪 {concept.title}",
                             "Learn it, run the code, break it, then check yourself.", accent=ACCENT_COMPLETE),
                unsafe_allow_html=True)
    st.markdown(_chips(concept), unsafe_allow_html=True)

    st.subheader("Summary")
    st.markdown(content.tldr)
    st.info(f"🧭 **Mental model.** {content.mental_model}")
    _render_exam_points(concept, content)

    st.subheader("What it is")
    st.markdown(content.what_it_is)

    st.subheader("How it works")
    st.markdown(content.how_it_works)
    st.graphviz_chart(content.flow_dot({}))
    st.caption("The same flowchart lights up along the path your own run takes in the code lab below.")

    st.subheader("Where you'll see it")
    st.markdown(content.where_seen)

    st.divider()
    _render_lab(concept.slug, content)
    if content.playground:
        st.divider()
        render_playground(concept.slug, content)
    st.divider()

    st.subheader("Looks right, isn't")
    st.caption("The exam distractors for this concept. Each one is a variant you can load and run in the lab above.")
    st.markdown(_table(("#", "Tempting approach", "Why it looks right", "Why it fails", "Do this instead", "Source"),
                       [(str(i), *row[:4], resolve_source(row[4])) for i, row in enumerate(content.distractors, 1)]),
                unsafe_allow_html=True)
    st.caption("⭐ = an anti-pattern the exam guide itself names (exact bullet shown). 📘 = a pitfall from the official "
               "docs that the guide does not name — worth knowing, less likely to be tested verbatim.")

    st.subheader("Side-by-side")
    st.markdown(_table(content.side_by_side_headers, content.side_by_side_rows), unsafe_allow_html=True)

    st.subheader("Decision tree")
    st.graphviz_chart(content.decision_dot)

    st.subheader("Practice")
    _render_questions(concept.slug, content)

    st.subheader("Frequently asked")
    for q, a in content.faq:
        with st.expander(q):
            st.markdown(a)

    st.subheader("Related concepts")
    pages = st.session_state.get("_concept_pages", {})
    related = [cm.get(s) for s in content.related if cm.get(s)]
    cols = st.columns(max(1, len(related)))
    for col, rel in zip(cols, related):
        with col:
            label = f"{rel.code} {rel.title}" if rel.code else rel.title
            if rel.slug in pages:
                st.page_link(pages[rel.slug], label=label, icon="🔗")
            else:
                st.write(label)

    st.subheader("Grounded in the official docs")
    st.caption(f"Rule: every concept is grounded in the official Claude documentation. These pages were fetched and "
               f"read on {content.docs_verified_on}; if a page has changed since, the docs win — tell me and I will fix this one.")
    for ref in content.docs_refs:
        st.markdown(f"- 📘 [{ref.title}]({ref.url})")
    with st.expander("Where each claim on this page comes from (provenance)"):
        st.markdown(_table(("#", "Claim", "Source type", "Where"),
                           [(str(i), c.text, ("⭐ " if c.kind == "guide" else "") + CLAIM_KINDS[c.kind], c.ref)
                            for i, c in enumerate(content.grounding, 1)]), unsafe_allow_html=True)

    st.caption(content.guide_note)
    render_progress_ticks(f"concept-{concept.slug}")


_STUB_TEXT = {
    "in_guide": ("🔜 Planned",
                 "This concept is covered by the official guide, so it will be built with the same template as "
                 "Agentic Loops (flowchart, runnable code lab, exam distractors, practice). Concepts are built one "
                 "at a time — type **`/next-concept`** in the Claude Code panel."),
    "partial": ("🔜 Planned (partly in the guide)",
                "Only part of this concept is in the official guide, so the page will cover just that part with the "
                "same template as Agentic Loops. Concepts are built one at a time — type **`/next-concept`**."),
    "awareness": ("ℹ️ Awareness only",
                  "The guide expects you to know this exists, nothing more. No lab will be built — implementation "
                  "detail is explicitly out of scope."),
    "out_of_scope": ("⛔ Out of scope for CCAR-F",
                     "The guide's Appendix says this will not appear on the exam, and this workbench never builds "
                     "pages or questions on out-of-scope topics (CLAUDE.md). If you want it for your own learning "
                     "anyway, ask — it would be added as a clearly-labelled extra, outside the exam plan."),
    "not_in_guide": ("⚪ Not in the CCAR-F guide",
                     "The community concept list includes this, but guide v1.0 has no matching task statement."),
}

_EXTRA_TEXT = ("➕ Extra — not on the CCAR-F exam",
               "Guide v1.0 has no task statement for this, but an official Claude docs page covers it, so it can be built "
               "as an **extra** (clearly labelled as not on the exam) — grounded in those docs, fetched and read at build "
               "time. Type **`/next-concept`** to build extras one at a time, after the exam concepts.")
_UNGROUNDABLE_TEXT = ("⚪ Not built — no official docs basis found",
                      "This concept is not in the exam guide and I found no official Claude docs page for it (checked the "
                      "docs indexes, 2026-09-26). Rule: every concept is 100% grounded in the official docs — so it is not "
                      "built rather than filled with unverified material. If you know of an official page that covers it, "
                      "tell me and it becomes an extra.")


def _render_stub(concept: cm.Concept) -> None:
    k = cm.kind(concept)
    title, body = {"extra": _EXTRA_TEXT, "ungroundable": _UNGROUNDABLE_TEXT}.get(k, _STUB_TEXT[concept.status])
    accent = ACCENT_CURRENT if cm.buildable(concept) else ACCENT_COMING
    domain_label = f"CONCEPTS · D{concept.domain} · {cm.DOMAIN_SHORT[concept.domain]}" if concept.domain else "CONCEPTS · Cross-cutting"
    st.markdown(phase_header(domain_label, f"{concept.code} {concept.title}" if concept.code else concept.title,
                             title, accent=accent), unsafe_allow_html=True)
    st.markdown(_chips(concept), unsafe_allow_html=True)
    st.info(body)
    if k == "extra":
        st.markdown("**Candidate official docs (to be fetched and read when built):**")
        for url in cm.EXTRA_DOCS[concept.slug]:
            st.markdown(f"- {url}")
    if concept.guide_refs:
        st.markdown("**⭐ Where the exam guide covers this (Claude's mapping — verify):**")
        for t in concept.guide_refs:
            st.markdown(f"- {ts_ref(t)} — {cm.ts_title(t)}")
    if concept.note:
        st.markdown(f"**Evidence:** {concept.note}")
    st.caption("Taxonomy from a community concept list (claudearchitectcertification.com — unverified). "
               "Full mapping: `docs/CONCEPTS_MAP.md`.")


def render_concept(slug: str) -> None:
    """Callable target for every concept page registered in app.py."""
    concept = cm.get(slug)
    st.set_page_config(page_title=f"{concept.code + ' ' if concept.code else ''}{concept.title} — Concepts",
                       page_icon="🧪", layout="wide")
    apply_dashboard_css()
    content = load_content(slug)
    if content is None:
        _render_stub(concept)
    else:
        _render_full(concept, content)
