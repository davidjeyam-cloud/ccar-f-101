---
description: Build the next CONCEPTS page (first buildable concept without a content module), with a flowchart, a runnable code lab and its exam distractors, then stop.
---

You are extending the **CONCEPTS** section. Build **exactly one concept page**, then stop. This is separate from
`/next-page` (the 46 phase pages) — **do not change the phase structure, `utils/course_map.py`, or any existing
page.**

## 1. Pick the concept
1. Read `utils/concepts_map.py`. Candidates are concepts with `cm.kind(c)` of `exam` (status `in_guide` /
   `partial`) and, once every exam concept is built, `extra` (a not-in-the-guide concept with an entry in
   `EXTRA_DOCS`) — that have **no** file `utils/concepts_content/<slug_with_underscores>.py`. Take the first in list
   order (D1.1 → D5.2, then the cross-cutting ones), unless the user names one.
2. Never build `out_of_scope` / `awareness` concepts (CLAUDE.md out-of-scope rule) or `ungroundable` ones (no
   official docs basis — grounding rule). If the user insists, say so plainly and ask; do not build silently.
3. Say which concept you picked and why, in one or two lines.

## 2. Ground it before writing — 100% grounded in the official docs (CLAUDE.md grounding rule)
- **Fetch and read the official docs first** (WebFetch): `platform.claude.com/docs/en/...` for API / prompting /
  tool-use topics and `code.claude.com/docs/en/...` for Claude Code / Agent SDK topics (`.../llms.txt` on each site is
  the index; `EXTRA_DOCS` in `concepts_map.py` lists candidates for extras). Do not write from memory. Record every
  page you read in `docs_refs` and today's date in `docs_verified_on`.
- **Exam concepts:** also read the guide's text for every task statement in `guide_refs` (extract `docs/source/*.pdf`
  with `pdftotext -layout`). The guide decides scope; the docs decide technical facts; if they differ, show both and
  follow the docs on facts (note it in `docs/SOURCES.md`).
- **Extras** (not in the guide) are labelled "not on the CCAR-F exam" on screen and must be fully docs-grounded; their
  practice questions are `in_bank=False`. If the docs don't support enough to build a page, stop and say so.
- Fill `grounding` with every substantive claim tagged `docs` / `guide` / `recommendation` / `simulated` and where it
  comes from. Anything you can't ground: label it or leave it out. Paraphrase; never copy passages; never reproduce a
  real exam question.
- **Distractors** come from the guide's anti-pattern lists AND the docs' own pitfall/warning lists; each carries its
  `source` ("guide" | "docs"). Anything else is labelled as your addition.

## 3. Build it (template: `utils/concepts_content/agentic_loops.py`)
Create `utils/concepts_content/<slug_with_underscores>.py` exposing `CONTENT = ConceptContent(...)`
(`utils/concept_types.py`). The page renderer (`utils/concept_page.py`) needs nothing else. Required parts:
- `docs_refs`, `docs_verified_on`, `grounding` (step 2), and a `source` on every distractor (`Variant.source` + the 5th distractor column).
- **Flowchart** (`flow_dot`, Graphviz DOT) and `node_states(trace)` so the chart lights up along the path the
  learner's run took (green = correct, red = where it went wrong, missing = not reached).
- **Code lab**: a `✅ correct` variant plus one runnable variant per distractor, each with a scenario that makes the
  failure visible, `observe` / `why` / `fix` text, and `check_outcome(scenario, trace)`.
- **Agent playground (CLAUDE.md AGENT PLAYGROUND RULE):** a `PlayTab` per sub-concept (message box + developer-side knobs + transcript) in `playground=` / `playground_intro=`; extend `utils/agent_playground.py` / `mock_claude.py` additively if the concept needs a new condition or knob. Run every tab with default and changed knobs and see each "try this" happen before writing it.
- **Exam highlighting (CLAUDE.md EXAM HIGHLIGHT RULE):** `exam_points` (one `ExamPoint` per guide bullet under the task statement's Knowledge of / Skills in, paraphrased, with `lab` saying where the page exercises it); every guide-derived distractor gets `source="guide:<ts>:<K|S><n>"`; ⭐ on exam-named nodes/rows/variant labels; guide claims in `grounding` cite `TS x.y · Knowledge/Skill n · p.N`. Read the task statement in the PDF first and count its bullets; `utils/guide_index.py` must already list the task statement.
- **Mental models (CLAUDE.md MENTAL MODEL RULE):** a `mental_model` for the concept, plus a one-line 🧭 mental model for every sub-concept the page teaches (each stop-reason-like branch, term or mode) — true to the docs, short, and naming the failure it prevents. Do not hand over a page missing any.
- Distractors table, side-by-side table (numbered rows), decision tree, 3+ **original** practice questions (with
  `scenarios=` tags; `basis="docs", in_bank=False` for items beyond the guide's wording), 3+ FAQ items, related-concept slugs, experiments.
- If the concept needs behaviour the simulated model or fake backend can't produce, **extend** `utils/mock_claude.py`
  / `utils/tools.py` additively (new scenario, new tool) — do not break existing scenarios. The model is always
  **SIMULATED** and labelled so; never present it as real Claude; pin no real model id from memory.

## 4. Verify — do not skip (this is where the last concept caught real bugs)
1. `py_compile` on `app.py`, `pages/*.py`, `utils/*.py`, `utils/concepts_content/*.py`.
2. **Run every variant against every scenario** through `utils.lab_runner.run_lab` and confirm each distractor really
   fails the way its `observe` text claims (and the correct variant passes). Fix the code or the claim — never ship a
   claim you did not see happen. Also compare each factual sentence on the page with the docs you fetched.
3. Validate every generated DOT graph (`uv run --no-project --with pydot ...`).
4. `AppTest.from_function` the concept page: render, press Run, switch variant, run again, practice question.
   (`switch_page` cannot target callable pages.) Assert on the **right** graphviz element index — the lab's
   highlighted chart sits between the two static ones.
5. Existing pages still render (default, Home, Exam Blueprint, Concepts index).
6. Regenerate `docs/CONCEPTS_MAP.md`; sandbox secret scan through `push.ps1` (see CLAUDE.md).

## 5. Hand over
Tell the user what was built, what you verified (and what you could not, e.g. no browser to screenshot the layout),
and the commit message (`feat: concept D#.# — <title>`). **Do not `git push`. Do not stage or commit unless asked.**
Do not start the next concept.
