# Session Log — ccar-f-101

> Append-only. One entry per session, newest at the bottom. Written by Claude at the end of each session so nothing is missed.
> The global one-file checkpoint `C:\Users\abc\.claude\session_resume.md` is overwritten each time; this log is the permanent record.

---

## 2026-09-21 — Recover lost session, finish Stage A

**Recovered:** the earlier chat was session `4cfeb919-853d-4225-918e-0d481b914f1a` (22:38), filed under `C:\Users\abc`. Its transcript was copied into the ccar-f-101 project session folder (original untouched). Resume with `claude --resume 4cfeb919-853d-4225-918e-0d481b914f1a`.

**Done:**
- Resumed the CCAR-F golden-prompt build, Stage A only (docs + config, no app pages).
- Written: `CLAUDE.md`, `AGENTS.md`, `push.ps1`, `docs/ARCHITECTURE.md`, `docs/SOURCES.md`, `docs/STUDY_PLAN.md`, `docs/APPROACH_SCORECARD.md` (stub), `.claude/commands/next-page.md`.
- Earlier the same day (previous session): repo created and cloned, inputs copied, `.gitignore`, `.env.example`, `requirements.txt`, `.streamlit/config.toml`.
- Verified: nothing staged; `docs/source/` gitignored; `push.ps1` tested in throwaway repos (blocks secrets and `docs/source/`, prompts before first push); real files pass the scan.

**Decisions:**
- Scenario numbers follow the official guide (1 Support, 2 CodeGen, 3 Research, 4 DevProd, 5 CI, 6 Extraction).
- `push.ps1` follows the prompt's staging list literally; stages only paths that exist.
- No model ID chosen; no community sources named.

**Open questions (waiting on user):**
1. What is `APPROACH_SCORECARD.md` / page `00d` meant to be? (stub, not guessed)
2. Default model ID for `utils/llm.py`?
3. Add `.gitignore`, `requirements.txt`, `.streamlit/`, `.env.example`, `.claude/commands/`, `push.ps1` to the `push.ps1` staging list?
4. Branch: local `master` vs global note "pushes to main".
5. Named community sources for `docs/SOURCES.md`?
6. Page filename slugs for phases 1–6.

**Next step:** user reviews Stage A and answers the questions; then `/next-page` to start Stage B.

**Commit status:** nothing committed, nothing staged.

---

## 2026-09-21 (later) — Switch the app to Gemini (same setup as agents101)

**Trigger:** typed `/next-page`; Claude picked `00_Hello_Claude` and asked which model to pin. The user answered: use Gemini, same model, setup and API key as agents101.

**Decision (user):** LLM = Google Gemini `gemini-2.5-flash`, SDK `google-genai`, key `GEMINI_API_KEY`. This **reverses** the build prompt's `anthropic` SDK / `ANTHROPIC_API_KEY`. Resolves open question 2 (model ID).

**Done:**
- `.env` (local, gitignored): `GEMINI_API_KEY` copied from agents101's `.env` (value never printed).
- `.env.example`, `requirements.txt`: switched to Gemini (`google-genai>=2.7.0`; `anthropic` removed). `.venv` updated (`google-genai` 2.24.0).
- `push.ps1`: secret scan gained an `AIza` (Google key) rule; tested with a fake key in a throwaway repo — aborts and unstages.
- Docs updated to match: `CLAUDE.md` (guardrails, stack, model rules, new Claude↔Gemini mapping table, trace standard, checklist, deviation row 8), `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/SOURCES.md` (row 6: Gemini mapping unverified), `.claude/commands/next-page.md`.
- Live check: `gemini-2.5-flash` answered "OK" with the copied key; `usage_metadata` returned token counts.

**Trade-off to remember:** the exam tests *Claude* behaviour (`stop_reason`, `tool_choice`, `tool_result`, Message Batches). Gemini demos show the pattern, not Claude's fields. Mitigation in the docs: Claude term shown beside the Gemini one in every trace, Claude API facts taught via `st.code()`, real Claude behaviour learned in `sandbox_project/` with Claude Code, quiz/bank stay Claude-specific. The Gemini mode names / `usage_metadata` fields in the mapping table are unverified.

**Not started:** `00_Hello_Claude` — paused on naming (see below). No app code exists yet.

**Open questions (waiting on user):**
1. Page name: keep `00_Hello_Claude.py` (prompt's name) or rename to `00_Hello_Gemini.py` (agents101's name, and what the page actually verifies)?
2. `APPROACH_SCORECARD` purpose (still open).
3. Add `.gitignore`, `requirements.txt`, `.streamlit/`, `.env.example`, `.claude/commands/`, `push.ps1` to the push.ps1 staging list?
4. Branch: `master` vs "pushes to main".
5. Named community sources; page slugs for phases 1–6.

**Next step:** answer question 1, then re-run `/next-page` to build the Phase 0 foundation (`app.py`, `utils/llm.py`, styles/trace/progress helpers, the first page).

**Commit status:** nothing committed, nothing staged.

---

## 2026-09-21 (later still) — Claude API key reminder rule (🔑 pages)

**Decision (user):** it is an exam, so a small cost must not compromise preparation. Wherever the Claude API key gives a real advantage, the app must show a **big, flashing "BUY THE CLAUDE API KEY" reminder**. Gemini stays the default elsewhere.

**Basis (checked 2026-09-21 on the official pricing pages):** Claude Haiku 4.5 is $1 in / $5 out per million tokens (Batch 50% off); Gemini 2.5 Flash is $0.30 in / $2.50 out with a free tier; the Claude API has no ongoing free tier, only a small amount of free credits for new users. The subscription (Claude Code) covers `sandbox_project/` builds but not running the Claude API from Python.

**Done (docs only — no app code exists yet):**
- `CLAUDE.md`: new **Claude API Key Reminder Standard** section (when a page gets 🔑, banner spec, accessibility, Home status card, hand-over reminder, `anthropic` SDK + `CLAUDE_MODEL` plan, purchase timing); 🔑 flags in Phase Status (1.1, 2.3, 4.3, 4.4, 4.5, 06c, 06d, 06e; 1.3 to confirm); new-page checklist item; deviation row 8 exception.
- `AGENTS.md`, `.claude/commands/next-page.md`, `docs/STUDY_PLAN.md` ("Before Day 1: buy the Claude API key"), `.env.example` (commented `ANTHROPIC_API_KEY` line).

**Still to do (Stage B):** build `claude_key_banner()` in `utils/styles.py` with the first 🔑 page; add `anthropic` to `requirements.txt` then; confirm the Haiku 4.5 model ID against current docs.

**Reminder for the user:** buy the Claude API key in the Claude Console (https://platform.claude.com/) with a low spend limit **before Day 1 / page 1.1**.

**Commit status:** nothing committed, nothing staged.

---

## 2026-09-21 — End of day

User called it off for the day. State: **Stage A complete, Stage B not started** (no app code). Nothing committed, nothing staged; `.env` (Gemini key) and `.venv` are local and gitignored.

**Resume with:** answer the page-name question (`00_Hello_Claude.py` vs `00_Hello_Gemini.py`), then run `/next-page`.

**Reminders for the user:**
1. Buy the Claude API key (Claude Console, https://platform.claude.com/, low spend limit) before Day 1 / page 1.1.
2. Still-open questions: `APPROACH_SCORECARD` purpose; whether `push.ps1` should also stage `.gitignore`, `requirements.txt`, `.streamlit/`, `.env.example`, `.claude/commands/`, `push.ps1`; branch `master` vs "pushes to main"; named community sources; page slugs for phases 1–6.
3. Nothing has been pushed. When ready for a first commit, run `.\push.ps1 "docs: Stage A setup"` yourself (it asks before the first push).

---

## 2026-09-22 — First commit (local) and push.ps1 fixes

**Question from user:** "is the code committed to GitHub? I want it committed before I exit each time." Answer: it was not — no commits, GitHub repo empty.

**Done:**
- Added `.gitignore`, `requirements.txt`, `.env.example`, `.streamlit`, `.claude` (commands + arch-diagram skill) and `push.ps1` itself to the `push.ps1` staging list (resolves the earlier open question 3). `.env`, `.venv`, `docs/source/`, `progress.json`, `output/` stay excluded.
- The secret scan now skips only `push.ps1`'s own rule-definition lines (they contain the patterns as text); a secret anywhere else in `push.ps1` is still caught (tested).
- `push.ps1` now also **pushes already-committed but unpushed work**: it scans the unpushed commits, blocks `docs/source/`, then goes to push. Before this fix, running it with nothing staged would have exited without pushing. Tested: clean unpushed commit, unpushed commit with a leak (aborts), already up to date.
- Set repo-local git identity `davidjeyam-cloud <davidjeyam@gmail.com>` (same as agents101).
- **Committed locally:** `55e6d5a docs: Stage A setup - project docs, config, push script` (16 files; staged tree was byte-identical to the tree that passed the scan). A follow-up commit holds the push.ps1 fixes and this log entry.

**NOT pushed.** GitHub is still empty. The user runs `.\push.ps1` (it asks before the first push).

**Standing rule (user, 2026-09-22):** before the user exits a session, check `git status` / `git log` / remote heads and say plainly whether everything is committed and pushed; commit outstanding work (Claude may commit, never push).

---

## 2026-09-22 — Stage B: first page built (00_Hello_Claude)

**Page name confirmed by user:** keep `00_Hello_Claude.py` (not renamed to Hello_Gemini).

**Built (checklist passed):**
- `app.py` — entry point, `st.navigation`, Phase 0 group with one page so far.
- `utils/styles.py`, `utils/llm.py`, `utils/trace.py`, `utils/diagrams.py`, `utils/quiz.py`, `utils/question_bank.py`, `utils/progress.py` — all new, mirroring agents101's patterns where one exists (styles/llm/trace/quiz), original for `progress.py`/`question_bank.py` (no agents101 equivalent).
- `pages/00_Hello_Claude.py` — explains the three-key architecture (Claude Code subscription / GEMINI_API_KEY now / ANTHROPIC_API_KEY later), live Gemini call with an Execution Trace that maps the finish reason to the Claude term, a 4-row key-comparison table, a 4-row traps table, sandbox_project/ build step, progress ticks.
- `docs/images/00_hello.png` exported.
- `PHASE_SEEDS["0"]` (9 concepts, 3 snippets) added to `utils/quiz.py`. No `question_bank.py` entries — Phase 0 has no task-statement number, documented in that module's docstring.
- Verified: `py_compile` clean; `streamlit.testing.v1.AppTest` run against `app.py` with zero exceptions, both with and without `GEMINI_API_KEY` (`.env` moved aside and restored — restore confirmed by byte count).
- Docs synced: `CLAUDE.md` Phase Status row -> ✅, `AGENTS.md` page count 0->1 and Phase Map, `docs/ARCHITECTURE.md` status line and Phase 0 row.

**Bugs found and fixed while building:**
1. matplotlib + DejaVu Sans has no emoji glyphs (same lesson agents101 already learned for wkhtmltoimage) - a 🔑 in `diagrams.py` produced a missing-glyph warning; replaced with plain text ("KEY pages"). Diagram layout also needed rework (arrow labels were overlapping boxes) - fixed with an opaque background patch behind each label.
2. `st.image(..., use_container_width=True)` is deprecated - switched to `width="stretch"`.
3. **push.ps1 false positives:** the "KEY= assignment" secret-scan rule flagged ordinary code (`Client(api_key=GEMINI_API_KEY)`, `Client(api_key=gemini_key)`) and a page-identifier constant (`PAGE_KEY = "00_Hello_Claude"`) as possible secrets. Fixed two ways: (a) the rule now exempts a captured value that itself contains the word "key" (a real secret token never spells "key" in its own content - only a variable/constant *name* does), tested against 4 cases including two negative controls (a real AIza key and a real unquoted `_KEY=` literal must still be caught, and both still are); (b) renamed the page constant from `PAGE_KEY` to `PAGE_SLUG` and added a naming note to `utils/progress.py` so no future page reintroduces the collision.

**Security near-miss, investigated and closed:**
A byte-identical stray copy of the copyrighted exam guide PDF was found at `docs/Claude_Certified_Architect_Foundations_Exam_Guide.pdf` (628,815 bytes, matches `docs/source/instructor_...pdf` exactly) - outside `docs/source/`, so neither `.gitignore` nor `push.ps1`'s old `docs/source/*`-only guard would have caught it. Origin unknown - nothing run this session referenced that path or filename, and `git log --all` confirms it was never staged or committed. Deleted the stray copy; confirmed no other stray PDFs exist in the repo (only matplotlib's own bundled PDFs under the gitignored `.venv/`). Hardened `push.ps1` with a second, repo-wide guard that blocks staging or committing **any** `.pdf` file, in both the normal-commit and unpushed-commit code paths - tested, catches a stray `docs/stray.pdf`. **The user should keep an eye out for this file reappearing** - if it does, that would identify the source (some tool/hook writing it), which is not yet known.

**Verification before hand-off:** full sandbox clone of the real working tree committed cleanly (26 files, 0 secret-scan hits) with all three fixes in place; four negative-control tests confirmed the scan still catches a real AIza key, a real unquoted password, a real unquoted `_KEY=` literal, and now a stray PDF.

**Not committed.** Per `/next-page` protocol, Claude does not stage or commit mid-build - only hands over the commit message. The user runs `.\push.ps1 "<message>"` when ready.

**Next step:** user builds the `sandbox_project/CLAUDE.md` step from this page's "Build it in VS Code with Claude Code" box, then types `/next-page` again for `00a_Home`.

---

## 2026-09-22 (continued) — Page 2: Home, plus a guide-traceability layer

**Trigger:** user asked (1) whether the study plan and sidebar are grounded against the guide PDF, (2) for a mapping between sidebar names/sub-topics and the guide, then (3) to update Home's project intent (grounded) and add a visual table for the blueprint sub-topics.

**Grounding audit (before building):** re-extracted `docs/source/*.pdf` fresh with `pdftotext`, confirmed byte-identical to the extraction used on 2026-09-21, and cross-checked all 30 task statements, all 5 domain names/weights (27/18/20/20/15%), and all 6 scenarios (numbering + exact primary domains) against that fresh text. All match `CLAUDE.md`. Caveat surfaced to the user: the *day-by-day schedule* in `docs/STUDY_PLAN.md` is not guide content (the guide has no calendar) - it came from the build prompt, using the guide's task-statement order as its backbone.

**Traceability layer added (utils/course_map.py):**
- `DOMAINS` dict: official domain name + weight + guide section, verified against guide §4/§6.
- `SCENARIOS` dict: guide scenario number + title + primary domains, verified against guide §5.
- `PageEntry.guide_ref()`: one-line citation for any page (domain+weight+task-statement, or scenario+primary-domains).
- `render_guide_map_markdown()`: generates `docs/GUIDE_MAP.md` (new, committed) - a standalone, off-app traceability table for all 46 pages, regenerable, not hand-maintained.
- `utils/placeholder.py` updated to show each unbuilt page's guide reference inline.

**Page built: `00a_Home`** (Phase 0, dashboard - not a lesson page, so it skips the concept/demo/quiz steps, matching agents101's own Home page precedent):
- "What this project is for" section, paraphrased from guide §1 (About This Certification) and §2 (Intended Audience), explicitly citing both.
- Visual blueprint table: 5 domain rows × task-statement badge cells (30 cells total, verified via markdown inspection, not just eyeballed), colour-coded by build status, ★/🔑 markers, driven live from `course_map.py` - can't go stale the way agents101's own hand-typed Home page did (its CLAUDE.md admits 4 stale CSS/count bugs).
- Scenario table (6 rows, guide-numbered, primary domains, status).
- Built with this app's own light theme tokens (`utils/styles.py`), not copied from agents101's dark-neon Home page, which is a different, inconsistent palette.

**Verified:**
- `py_compile` clean across app.py + all pages + all utils.
- `AppTest` on the default page (Hello Claude): 0 exceptions.
- `AppTest.switch_page("pages/00a_Home.py")` (direct `from_file` on a page fails outside app.py's navigation context - `sys.path` doesn't include the repo root; this is a test-harness artifact, not an app bug): 0 exceptions.
- Regex-verified the rendered blueprint table has exactly 30 task-statement cells in the right order/markers, and exactly 6 scenario rows.
- **No headless browser available in this environment** to screenshot the live CSS render - structural correctness verified, visual layout was not eyeballed by Claude. Asked the user to confirm it looks right.
- Sandbox secret scan: clean, 30 files.

**Docs synced:** `CLAUDE.md` (both Phase Status rows -> ✅), `AGENTS.md` (2/46, Phase Map), `docs/ARCHITECTURE.md`, `docs/GUIDE_MAP.md` regenerated.

**Not committed** - handing over the commit message per `/next-page` protocol norms (this was a direct content request, not a `/next-page` run, but the same "don't commit unless asked" convention was kept).

**Next step:** user reviews Home's visual layout in the browser; then either more direction, or `/next-page` for `00b_Exam_Blueprint`.

---

## 2026-09-22 (continued) — Page 3: Exam Blueprint

**Trigger:** user clicked the Exam Blueprint placeholder and asked "is it empty?" - confirmed it was working as designed (unbuilt placeholder), then user asked to build it.

**Content split decided:** the original CLAUDE.md description for this page ("domains, weights, scenarios, out-of-scope") would have duplicated Home's new blueprint table. Repurposed: Home = *what* is tested (domains/task-statements/scenarios, built earlier today); Exam Blueprint = *how the exam itself works* (format, timing, scoring, policies, out-of-scope). Documented the split in both pages and in CLAUDE.md's Phase Status row.

**Refactor:** extracted the card/table/stat CSS Home had defined locally into `utils/styles.py` (`DASHBOARD_CSS` / `apply_dashboard_css()`), since Exam Blueprint needed the identical pattern. Updated Home to use the shared classes (`wb-card`, `wb-table`, `wb-stat*`, `wb-cite`) instead of its own duplicate `cf-*` copies, keeping only the blueprint-grid-specific classes (`cf-cell`, `cf-domain-name`, `cf-weight-badge`) local to Home.

**Page built: `00b_Exam_Blueprint`** - three tables, all grounded and cross-checked against the fresh guide extraction:
- Exam details at a glance (10 rows) - guide §3.
- How it's scored (criterion-referenced, not curved) - guide §10.
- Policies worth planning around (8 rows: ID, accommodations, retake waits/limits, no-show, exam-day conduct, misconduct, recertification) - guide §12, §13, §15.
- Out-of-scope topics (16 rows, matches the guide's Appendix count exactly) - guide Appendix.

**Verified:** `py_compile` clean; `AppTest` via real navigation on all 3 built pages (default/Hello Claude, Home, Exam Blueprint) - 0 exceptions each; regex-counted Exam Blueprint's rendered output: 3 tables, 34 data rows (10+8+16, matches exactly what was written); sandbox secret scan clean, 31 files.

**Docs synced:** `CLAUDE.md` (row -> ✅, description updated), `AGENTS.md` (3/46, Phase Map), `docs/ARCHITECTURE.md`, `docs/GUIDE_MAP.md` regenerated.

**Not committed** - same pending commit as the rest of today's Stage B work.

**Next step:** user reviews the live app (still no headless browser available to screenshot); then more direction, or `/next-page` for `00c_Study_Plan`.

---

## 2026-09-22/23 — End of day

**Committed on the user's behalf** (per the commit-before-exit rule), not pushed: `2c9f7bc "feat: Stage B pages 1-3 - Hello Claude, Home, Exam Blueprint"`. Working tree clean. GitHub still shows no commits pushed (`git ls-remote --heads origin` returned empty at start of exit check). Local Streamlit server (PID 25860) stopped.

**State:** 3 of 46 pages built (Hello Claude, Home, Exam Blueprint), all following the Page Structure Standard variant for dashboard pages. Sidebar shows the full 46-page roadmap via placeholders. `docs/GUIDE_MAP.md` traces every page to the guide.

**Resume with:** run `.\push.ps1` to push everything (3 local commits) to GitHub, then either give direction for the next page or type `/next-page` for `00c_Study_Plan`.

---

## 2026-09-26 — New CONCEPTS section (concept-by-concept learning with runnable code labs)

**Request (user):** add a section called CONCEPTS, structured like claudearchitectcertification.com/concepts (concepts + sub-concepts), without modifying any other structure. Intent: learn each concept one at a time with code snippets and flowcharts, and be able to *edit the code and press Run in Streamlit* to see how each flow works and where it fails or hallucinates (exam distractors). Example given: Agentic Loops.

**What was checked first:** fetched the site's concept index and its Agentic Loops page (structure only). It lists 71 concepts: 30 numbered D1.1–D5.2 plus 41 unnumbered "cross-cutting" ones; each concept page has Summary, What it is, How it works, Where you'll see it, Code examples, Looks right isn't, Side-by-side, Decision tree, Question patterns, FAQ. It has no runnable code and no execution flow, exactly as the user said.

**Decision taken (flag to the user):** the site is a **community** source. Mirrored its layout and taxonomy, but **scope follows the official guide**. Keyword-searched guide v1.0: zero hits for guardrails, prompt injection, GDPR/HIPAA, bias, stakeholders, governance, Projects, connectors, Artifacts, Managed Agents, Client SDK, "4D". Result of tagging all 71: 22 in the guide, 15 partial, 1 awareness (prompt caching), 3 explicitly out of scope (Vision, Streaming, Auth & access control), 30 not in the guide. Only in-guide/partial concepts get built; the rest get an honest stub. This respects CLAUDE.md's out-of-scope rule; the user can override any of it. Statuses are Claude's judgment — verify in `docs/CONCEPTS_MAP.md`.

**Built (additive — no existing page, `course_map.py`, Home counts or phase structure changed):**
- `utils/concepts_map.py` (taxonomy + scope status), `utils/concept_page.py` (generic renderer), `utils/concept_types.py`, `pages/concepts_index.py` (domain tabs + card grid), additive block in `app.py` (sidebar sections "CONCEPTS" and "CONCEPTS · D1…D5"; the 41 cross-cutting pages are registered but hidden).
- **Code lab engine:** `utils/lab_runner.py` + `lab_harness.py` (learner code runs in a **separate process**: 10 s timeout, temp cwd, **no API keys in env**, secrets redacted), `utils/mock_claude.py` (**SIMULATED** Claude Messages-API-shaped client, stateless — decides only from the messages it is sent, and enforces tool_use/tool_result pairing), `utils/tools.py` (fake support backend — the planned tools.py; deliberately permissive so bugs show as visible consequences), `utils/lab_trace.py`.
- **D1.1 Agentic Loops** (reference implementation, `utils/concepts_content/agentic_loops.py`): flowchart that lights up along the path the run took; 6 runnable variants (correct loop + 5 exam distractors taken from the guide's Task Statement 1.1 anti-patterns and skills); 5 scenarios; result checker; distractors table; side-by-side; decision tree; 3 original practice questions (also registered in `utils/question_bank.py`, `reviewed_by_user: False`); FAQ; experiments.
- `/next-concept` command (`.claude/commands/next-concept.md`) so remaining concepts are built one at a time to the same template and the same verify-before-claiming discipline.
- Docs: CLAUDE.md (new CONCEPTS section, structure, checklist, deviation 9), AGENTS.md, docs/ARCHITECTURE.md, docs/SOURCES.md (community source consulted, 2 new unverified-claim rows, 1 disagreement row), docs/CONCEPTS_MAP.md (generated).

**Verification (this is what caught real problems):**
- Ran every variant × every scenario through the real subprocess runner. Confirmed each distractor fails as its text claims, and that the correct loop passes all 5 scenarios. Notable: distractors A, C and E *pass* on easy scenarios and only break on the right trigger — which is exactly why they are exam traps.
- Edge cases: busy loop killed at the timeout; syntax error surfaced; missing assistant turn → simulated API error and the SEND node goes red; loop with no backstop trips the simulated spend guard; a key placed in the parent env is absent in the child and redacted if printed; oversize code rejected; relative `.env` read finds nothing.
- Validated all 32 generated Graphviz graphs with an independent parser (pydot, isolated `uv run --no-project`; project venv untouched).
- `AppTest`: existing pages unaffected (default, Home, Exam Blueprint); index renders with 7 tabs; concept page renders all 11 sections; Run → success/failed result check + highlighted chart; switching to distractor A loads its code and scenario and its run marks exactly the ABANDON node red; edited code runs; Reset restores; practice question right/wrong feedback; 7 stub statuses render.
- Two of my own test mistakes caught along the way (wrong graphviz element index made a "green nodes" assertion pass vacuously; a scenario expectation that wrongly failed a hard-coded sequence on the happy path) — both fixed and re-verified.
- Sandbox secret scan via `push.ps1`: clean, 43 files; no stray PDFs.
- **Not verified:** the visual layout (Graphviz rendering, CSS, monospace editor) — no headless browser in this environment; the user must look.

**Limits stated to the user:** the lab is not a security sandbox (runs with the user's permissions); the simulated model is not real Claude and its API error wording is an approximation (marked SIMULATED, listed in SOURCES.md as unverified); the 🔑 phase page for TS 1.1 will check the same mechanics against the real API once the key is bought.

**Not committed.** Work is uncommitted on top of commit `bcd6e44`.

**Next step:** user reviews the CONCEPTS section in the browser (http://localhost:8501/concepts) and says what to change; then `/next-concept` builds D1.2 Subagents (first buildable concept without a content module) — or names another. Open questions for the user: keep CONCEPTS at the bottom of the sidebar or move it to the top? Build any of the "not in guide" concepts anyway as clearly-labelled extras?


## 2026-09-26 (later) — CONCEPTS to the top, extras, and 100% official-docs grounding

**Request (user):** (1) move CONCEPTS to the top of the sidebar; (2) "yes" to building the not-in-the-guide concepts as extras; (3) the Agentic Loops concept is not fully aligned with the official platform docs (handling-stop-reasons, refusals-and-fallback) — as a rule ALL concepts must be 100% grounded against the Claude platform docs; (4) update CLAUDE.md and any interim memory snapshot.

**What was wrong:** my D1.1 page taught two stop reasons (`tool_use`, `end_turn`) and raised a generic error on anything else, and called the iteration cap "my recommendation". The docs list seven stop reasons and require each to be handled; a refusal is an HTTP 200 (retry on a different model); `max_tokens` is truncation; `pause_turn` means send the response back; tool_result blocks must come first in one user message; text after results can cause an empty `end_turn`; the Agent SDK's `max_turns` / `max_budget_usd` return error subtypes. (The guide itself names only two — recorded in docs/SOURCES.md as a refinement.)

**Docs read (2026-09-26):** platform: handling-stop-reasons, refusals-and-fallback, how-tool-use-works, handle-tool-calls, tool-use overview, build-a-tool-using-agent, llms.txt index; code.claude.com: agent-sdk/agent-loop (platform `/agent-sdk/*` 307-redirects there — so "platform docs" was read as both sites).

**Done:**
- `utils/mock_claude.py` rewritten docs-aligned (refusal HTTP-200 shape, max_tokens truncation, pause_turn, empty end_turn after text-after-results, tool_result ordering/pairing rules, model + max_tokens in trace); scenarios now 8.
- `utils/concept_types.py`: DocRef / Claim provenance / Variant.source / Question.basis + in_bank.
- `utils/concepts_content/agentic_loops.py` rewritten docs-first: canonical loop handles all seven stop reasons; 9 distractors (A–E from the guide, F–I from the docs' pitfalls); flowchart with TRUNC/REFUSAL/PAUSE; docs list + provenance table (21 tagged claims); 2 docs-based questions (`in_bank=False`).
- `utils/concept_page.py`: "Grounded in the official docs" section, provenance expander, Source column, ➕ extra badge/stubs; `pages/concepts_index.py` counts by kind; `utils/question_bank.py` skips `in_bank=False`.
- `utils/concepts_map.py`: `EXTRA_DOCS` (9 candidate extras), `kind()` → exam 37 · extra 9 · ungroundable 21 · excluded 4; nav markers ➕ / ⚪ / ⛔ / ℹ️; CONCEPTS_MAP.md gains Kind + Candidate-docs columns.
- `app.py`: CONCEPTS sections first in the sidebar; Hello Claude still default (`default=True`).
- Rules/memory: CLAUDE.md (source-of-truth rule 5 = official docs technical truth, grounding rule + extras policy in the CONCEPTS section, corrected Critical SDK Notes C, checklist, deviation 9), `.claude/commands/next-concept.md` (fetch docs first), AGENTS.md, docs/ARCHITECTURE.md, docs/SOURCES.md (docs consulted + "where docs refine the guide"), memory (`feedback_ground-concepts-in-platform-docs.md`, project memory, index), `session_resume.md`.

**Verified by running:** all 10 variants × 8 scenarios through the real subprocess runner; every "observe" claim seen happening (F: half-sentence / empty answer / abandoned pause; G: 3 refusals; H: empty end_turn; I: 400; C with a cap of 8 works, i.e. the trap); edge cases (timeout, syntax error, missing assistant append, no backstop, env-leak, oversize, relative .env); 82 DOT graphs (pydot); AppTest (default, Home, Exam Blueprint, index, concept page Run/variant/reset/practice, extra + ungroundable + excluded stubs); py_compile. One check bug found and fixed: the `runaway` check counted a simulated API error as a "loud failure".
**Not verified:** visual layout (no browser). Docs-derived claims reflect the pages as fetched today.

**Not committed.** Work is uncommitted on top of bcd6e44; 4 local commits + this work are unpushed — run `.\push.ps1`.

**Next step:** user reviews http://localhost:8501/concepts; then `/next-concept` (D1.2 Subagents — needs code.claude.com sub-agents docs fetched first).


## 2026-09-26 (later) — Trace tables wrap; first push; D1.2 Subagents built

**User feedback fixed:** D1.1's "Execution Trace" tables truncated long cells (e.g. "Response content") because they were `st.dataframe`. They are now the wrapped HTML table used elsewhere (wrap CSS added); verified with AppTest (0 dataframes, full cell text present).

**Pushed (user asked explicitly):** commit `7c28e32` (CONCEPTS + D1.1 + rules) — first push, whole history scanned first (no keys / PDFs / .env); `origin/master` now tracks. `push.ps1`'s first-push confirmation prompt can't run non-interactively, so the push itself was `git push -u origin master` after the scan.

**Built D1.2 Subagents** (guide TS 1.2 pp.5–6 + TS 1.3 pp.6–7; `utils/concepts_content/subagents.py`):
- Docs read (2026-09-26): code.claude.com agent-sdk/subagents, sub-agents, agent-sdk/sessions. **Two guide-vs-docs differences recorded in SOURCES.md:** the guide says the spawn tool is `Task`, the docs say `Agent` (Task = legacy alias, renamed v2.1.63); the guide's hub-and-spoke vs the docs allowing nested subagents.
- 16 ⭐ exam points (every Knowledge/Skill bullet of both task statements) with exact refs; 24 grounding claims; 9 lab variants (correct + A–G from the guide, H from the docs' warning), 3 scenarios (broad_topic, simple_question, source_fails); left-to-right colour-keyed flowchart whose red bug nodes light only for the bug a run shows; decision tree; side-by-side; 6 questions (4 guide-based in the bank tagged by their own TS — 1.2:1, 1.3:3 — plus 2 docs-based); FAQ.
- Agent playground: 10 tabs (Spawn tool, Isolated context, AgentDefinition tools, Structured findings, Parallel spawning + concurrency limit, Dynamic selection, Goals not procedures, Decomposition, Review & refinement, Session fork) with per-tab knobs; new engines `research_playground.py` (coordinator + subagents, prompt built from knobs, each subagent's received prompt shown) and a no-model fork demo.
- Infra (additive): `mock_claude.py` ROLE dispatch (coordinator/searcher/analyst/synthesizer, parallel tool_use blocks, stop_sequences/context-window earlier), `research_backend.py`, `PlayTab.engine`, `ConceptContent.scenarios/show_ledger`, `Question.ts`, harness records scenario id.
- Matrix verified by running: correct passes all 3 scenarios; A,C,F fail all; B,D,E,H fail broad+source_fails; G fails only source_fails (hides until a source fails). Two design fixes came from running it: F ("route around the coordinator") originally passed because only search hops were hidden — now measured as results the coordinator received but couldn't use ("blind"); some chart states were misleading (fixed).
- Tests: 28 flow graphs + decision tree parse (pydot); AppTest — page, Run, variant switch, all playground tabs with changed knobs, fork demo, practice question; D1.1 regression (matrix, edges, page, playground, DOT), Home/Blueprint/index/default page all clean.
- Not verified: visual layout (no browser). Simulated coordinator is keyword-driven — stated on the page.

**Uncommitted** after `7c28e32`. Not pushed. Next: `/next-concept` → D1.3 Stop Reason (or whichever the map lists next).

## 2026-09-26 (later still) — D1.3 Stop Reason built

**Picked** D1.3 (`stop-reason`, guide TS 1.1) as the first unbuilt exam concept. It overlaps D1.1's loop, so it is framed as the *decision at the top of each iteration*: one response → which value → which action.

**Docs re-read (2026-09-26):** handling-stop-reasons, refusals-and-fallback. New verified facts: the stop-sequence text is NOT in the content (corrected D1.1's playground text + grounding claim that had said "not verified"); pause_turn default iteration limit 10 and the same tools must be resent; refusal `category`/`explanation` are nullable and named categories are cyber/bio/frontier_llm/reasoning_extraction/general_harms; a context-window stop still returns valid partial content.

**Built** (`utils/concepts_content/stop_reason.py`): 3 ⭐ exam points (TS 1.1 K1/S1/S3 — the guide names only tool_use/end_turn); lab where the learner writes `decide(response)` across 10 single-call scenarios (each stop reason, incomplete tool call at max_tokens, empty end_turn, API error); 8 distractors (A,B guide S3; C–H docs: tool_use blocks vs stop_reason, else-branch, same-model refusal retry, blind empty retry, no try/except, decide-from-explanation); LR colour-keyed chart showing your handler's branch vs the docs' branch; 9 playground tabs (`engine="stop"`: raw response + chosen vs expected action); 6 questions (2 guide → bank TS 1.1, 4 docs-based); mental model on every sub-concept.
Infra (additive): mock `Turn.special` (max_tokens mid tool call, context full), `STOP_SCENARIOS`, `utils/stop_lab.py`, `utils/stop_inspector.py`, harness `stop_lab.configure`.

**Verified by running:** every variant × 10 scenarios (correct passes all; A only tool_use; B six; C only max_tokens_tool; D seven; E,H only refusal; F only empty; G only API error); lab variants and playground policies agree on all 90 combinations; 91 DOT graphs parse; AppTest (page, Run, variant switch, all 9 tabs, changed handlers/knobs, practice); D1.1, D1.2, Home, Blueprint, index regressions clean. Not verified: visual layout (no browser).

**Uncommitted** (D1.2 + D1.3 on top of pushed 7c28e32).


## 2026-09-27 — D1.4 Session State & Persistence and D1.5 Human-in-the-Loop Escalation built

**Request (user):** build D1.4 and D1.5 without asking; apply all earlier feedback and CLAUDE.md rules; ground in the exam guide; no guesses.

**Grounding.** Guide text read from the PDF for TS 1.7 (pp.8–9), TS 5.4 (pp.21–22), TS 5.2 (pp.20–21), TS 1.4 (p.7), and the §5 scenario descriptions (used for the practice questions' scenario tags). Docs fetched 2026-09-27: code.claude.com sessions, best-practices, agent-sdk/sessions, agent-sdk/hooks; platform customer-support-chat, claude-prompting-best-practices. Recorded in SOURCES.md, with two guide-vs-docs rows (CLI `--resume <name>` vs SDK `resume=<id>`; escalation rules are the guide's, the docs give mechanisms).

**D1.4** (`utils/concepts_content/session_state.py`): all 17 TS 1.7 + 5.4 bullets as ⭐ exam points (5.4 K3/S1 point to D1.2); simulated session layer `utils/session_lab.py` (named sessions, --continue picking the most recent, resume, fork, a fake codebase that changes overnight, simulated degradation threshold, scratchpad, crash manifest); 6 guide distractors (silent resume, fresh without summary, always resume, no fork, restart after crash, --continue) × 5 scenarios; 5 playground tabs (`utils/session_play.py`).
**D1.5** (`utils/concepts_content/escalation.py`): all 15 TS 5.2 + 1.4 bullets (1.4 S2 points to D1.2); fake support backend + scripted customers `utils/support_lab.py`; keyword-driven simulated support agent in mock_claude; code gate vs prompt-only; structured vs free-text handoff; 7 guide distractors (sentiment, confidence, investigate-first, heuristic pick, prompt-only verification, free-text handoff, "complex cases") × 7 scenarios; 7 playground tabs (`utils/escalation_play.py`).

**Verified by running:** both matrices (D1.4: correct passes 5/5, each distractor fails exactly its scenarios; D1.5: correct 7/7, A 2 fails, B 4, C 1, D 1, E 1, F 4, G 5); every observe text matched to observed output (fixed one false claim in D1.4 A before writing; found and fixed a simulator realism bug — the support agent ignored refund_allowed=false; fixed two playground verdicts that missed failures); 95 new DOT graphs parse; AppTest on both pages (render, Run, variant switch, every playground tab, knob changes, all practice questions); full regression of D1.1–D1.3, Home, Blueprint, index, stubs. Not verified: visual layout (no browser).

**Uncommitted** (D1.2–D1.5 on top of pushed 7c28e32). Next: `/next-concept` → D1.6 Subagent State Handoff.


## 2026-09-27 (later) — D1.6, D1.7, D1.8 built; all flowcharts top-down; committed + pushed

**Request (user):** build D1.6–D1.8 without asking; ground in the exam guide and cross-check the Claude Code docs; mental models where they help; commit to GitHub when done. Mid-turn: all flowcharts must be top-down (LR charts illegible); then continue with D2.1–D2.3.

**Grounding.** Guide PDF: TS 1.6 (p.8), TS 3.1 (pp.12–13); TS 1.3/1.4/5.4 re-used. Docs fetched 2026-09-27: code.claude.com memory (CLAUDE.md scopes, loading, @import, rules, /memory, AGENTS.md), common-workflows; platform prompting best practices (chaining, subagent orchestration, state tracking). SOURCES.md row 7: AGENTS.md is docs-only.

**D1.6 Subagent State Handoff** (`subagent_state_handoff.py`, `handoff_lab.py`, `handoff_play.py`): 7 exam points; 6 distractors (pointer, prose, transcripts[docs], top-2 only, no phase summary, no saved state) × 4 scenarios; 5 playground tabs.
**D1.7 Agent Instruction Files** (`agent_instruction_files.py`, `memory_lab.py`, `memory_play.py`): a simulated loader implementing the memory docs' rules, printing /memory views per persona; 8 TS 3.1 exam points; 6 distractors (user-level team rule, root-level imports, monolith — guide; no @AGENTS.md, CLAUDE.local.md team rule, root-relative import path — docs) × 4 scenarios; 5 tabs. Bug found by running: path normalisation stripped the dot from `.claude/`.
**D1.8 Task Decomposition** (`task_decomposition.py`, `decomp_lab.py`, `decomp_play.py`): 6 exam points; 5 guide distractors (single pass, no integration pass, fixed plan, non-adaptive plan, adaptive picking for a review) × 3 scenarios; 3 tabs. Two texts corrected after running (single pass finds 0/4, not 1/4; the picked-file list).

**Top-down charts:** every flow_dot and decision tree now `rankdir=TB`, bug nodes in one bottom row, 12pt font — FLOWCHART RULE added to CLAUDE.md. A knob named `send` collided with the Send button's widget key (renamed; now asserted).

**Verified:** all 8 concepts' matrices by running; AppTest on every page (render, Run, variant, every tab, all practice questions); 310 DOT graphs parse and are top-down; D1.1–D1.5 regressions and Home/Blueprint/index clean. Not verified: visual layout (no browser).

**Committed and pushed** at the user's explicit request. Next: D2.1–D2.3.


## 2026-09-27 (evening) — D2.1 Tool Calling, D2.2 Tool Choice, D2.3 MCP built; committed + pushed

**Request (user):** continue into Domain 2 with D2.1–D2.3 ("key concepts — utmost care, detail, exam-centric"), top-down flowcharts, commit to GitHub when done.

**Grounding.** Guide PDF: TS 2.1 (p.9), TS 2.2 (pp.9–10), TS 2.3 (pp.10–11), TS 2.4 (p.11), TS 4.3 (pp.17–18); TS 1.1 re-used. Docs fetched 2026-09-27: platform define-tools, strict-tool-use, structured-outputs; code.claude.com mcp, common-workflows (@server:resource), agent-sdk/custom-tools (isError). SOURCES.md: docs rows 20–24; guide-vs-docs rows 8–12 (tool_choice 3 vs 4 options + forcing restriction; split vs consolidate; MCP scopes 2 vs 3; tool search vs "all at connection"; isError vs errorCategory/isRetryable). Unverified-claim row 1 (models rejecting forced tool_choice) is now VERIFIED; CLAUDE.md Critical SDK Notes C updated.

**D2.1 Tool Calling** (`tool_calling.py`, `tool_select_lab.py`, `toolsel_play.py`): 9 exam points; a word-overlap simulated router; 5 distractors × 4 scenarios; 5 playground tabs.
**D2.2 Tool Choice** (`tool_choice.py`, `toolchoice_lab.py`, `toolchoice_play.py`): 19 exam points (TS 2.3 + 4.3); simulated API enforcing the documented rules (no text before a forced call, 400 where forcing isn't supported); 8 distractors × 6 scenarios; 6 tabs.
**D2.3 MCP** (`mcp.py`, `mcp_lab.py`, `mcp_play.py`): 17 exam points (TS 2.4 + 2.2); config part simulates your session AND a teammate's fresh clone; error part runs your MCP tool handlers and orders subagent through a simulated coordinator; 12 guide distractors × 8 scenarios; 6 tabs.

**Verified by running:** all three matrices (every distractor fails exactly the scenarios its observe text names; correct passes all); every playground tab with default and changed knobs; AppTest on each page (render, Run, variant switch, every tab, all practice questions — 7/7 and 8/8); 162 new DOT graphs parse and are top-down; full regression of D1.1–D1.8, D2.1, Home, Blueprint, Concepts index. Bugs found by running: a quoting slip in the playground renderer; the "strict ≠ correct" tab used the wrong invoice. Not verified: visual layout (no browser).

**Committed and pushed** at the user's explicit request. Next: D2.4 SDK Hooks (`/next-concept`).


## 2026-09-27 (night) — D2.4 SDK Hooks built (uncommitted)

**Request (user):** `/next-concept` → D2.4 SDK Hooks (Pre/PostToolUse), guide TS 1.5.

**Grounding.** Guide PDF: TS 1.5 (p.7 — 3 Knowledge, 3 Skills). Docs fetched 2026-09-27: code.claude.com agent-sdk/hooks, hooks (matcher patterns), hooks-guide (deterministic control; PostToolUse can't undo), agent-sdk/permissions (hooks first in the evaluation order). SOURCES.md docs rows 25–27, guide-vs-docs row 13 (the guide's "tool call interception" = the docs' PreToolUse).

**D2.4** (`utils/concepts_content/hooks.py`, `utils/hooks_lab.py`, `utils/hooks_play.py`): 6 exam points; a simulated Agent SDK hook runner implementing the docs' matcher rules (exact vs regex), deny > defer > ask > allow, updatedToolOutput / additionalContext, async outputs that can't block, and PostToolUse after execution; a simulated support agent whose prompt-only rule slips under "my manager approved it" and which misreads raw Unix timestamps / status codes. 7 distractors (prompt-only, missing reason/redirect, blocking the whole tool, normalising by prompt — guide; PostToolUse policy, exact-name matcher, async policy — docs) × 3 scenarios; 6 playground tabs (hook vs prompt, block & redirect, normalise, matchers, several hooks, Pre vs Post).

**Verified by running:** matrix (correct 3/3; each distractor fails exactly its scenario, for the named reason — the diagnosis for the matcher variant was fixed after the first run); 22 playground knob combinations + 4 through AppTest; AppTest on the page (render, Run, variant, 6 tabs, 6/6 practice); 26 DOT graphs parse, top-down; regressions of D1.5, D2.1–D2.3, Home, Blueprint, index. Not verified: visual layout (no browser).

**Committed** (not pushed) at the user's request: `feat: concept D2.4 — SDK Hooks (Pre/PostToolUse)`. Next: D2.5 Tool Evaluation & Testing (partial) or D2.6.


## 2026-09-28 — Readable flowcharts (D1.2 by hand, D1.3–D2.4 via utils/flow_style.py)

**Request (user):** D1.2's flowchart text was too small — make it readable even if it needs scrolling; then ("this is good size, keep it in memory") apply the same size to every flowchart from D1.3 onwards.

**Cause:** st.graphviz_chart scales a chart to the column width; D1.2 had 8 distractor nodes in one row, so the whole chart shrank.
**D1.2** (`subagents.py`): node 18pt, edge labels 16pt, key 16pt, distractors stacked 2 per row. Approved by the user.
**D1.3–D2.4** (10 modules): new `utils/flow_style.py::readable()` post-processes flow_dot and DECISION_DOT — same sizes; any row (or fan-out of >2 children) re-cut into rows of at most 2 nodes, or 1 when a pair is estimated wider than 720 px; stacked with invisible edges. Estimated widest rows now ~630–710 px (D1.2 ≈ 615 px). Rule saved in CLAUDE.md FLOWCHART RULE and memory.

**Verified:** every variant × scenario re-run for all 10 concepts — results identical to before; 481 DOT graphs parse, all 18pt and ≤ 2 nodes per row; AppTest renders each page and its lab (no exceptions). Not verified: the rendered pixel width (no Graphviz binary or browser here) — widths are estimates from label length. Not changed: D1.1's charts and D1.2's decision tree (outside the request).

**Uncommitted.**


## 2026-09-28 — D1.2 tools grid; D2.5, D2.6 and all of D3 (D3.1–D3.4) built

**Requests (user):** (1) D1.2: explain `tools` / `allowedTools` / `disallowedTools` and what a subagent inherits "as a simple table, separate section … grid type explanation". (2) "continue from D2.5, D2.6 and all sections of D3".

**D1.2 tools & permissions section** (`subagents.py` WHAT_IT_IS): three grids — each setting (where set, controls, if blank, reaches the subagent?), what a non-fork subagent inherits (✅/❌/⚠️), and 8 worked examples. Grounded in agent-sdk/subagents, sub-agents (Available tools, tools vs disallowedTools order, permission modes, hooks), agent-sdk/permissions, agent-sdk/hooks — all fetched 2026-09-28.

**Built** (each: guide TS text read from the PDF, docs fetched 2026-09-28, lab + distractors verified by running, playground tabs run with default and changed knobs, AppTest page test, 18pt charts):
- **D2.5 Tool Evaluation** (◐; guide §7 p.24 + TS 2.1; docs develop-tests, troubleshooting-tool-use) — `evaluation.py`, `eval_lab.py`, `eval_play.py`; 5 distractors × 3 scenarios; 5 tabs.
- **D2.6 Built-in vs Custom vs Skills vs MCP** (TS 2.5 + 3.2 S5 + 2.4 S3; docs tools-reference, features-overview) — `agentic_tool_surface_selection.py`, `builtin_lab.py`, `builtin_play.py`; 6 × 5; 5 tabs.
- **D3.1 CLAUDE.md Hierarchy** (TS 3.1 + 3.3; memory docs re-read) — `claude_md_hierarchy.py`, `rules_lab.py`, `rules_play.py`; 5 × 3; 4 tabs. Fixed `memory_lab.py` to the docs' glob semantics (`*` = one directory, `**` = any depth, braces) and to read only the `paths` field; D1.7's matrix re-run — unchanged.
- **D3.2 Plan Mode** (TS 3.4; permission-modes, sub-agents built-ins) — `plan_mode.py`, `plan_lab.py`, `plan_play.py`; 5 × 4; 3 tabs.
- **D3.3 Skills** (TS 3.2; skills docs) — `skills.py`, `skills_lab.py`, `skills_play.py`; 6 × 6; 5 tabs. Guide says allowed-tools restricts; docs say it pre-approves and disallowed-tools restricts — both taught (SOURCES row 14).
- **D3.4 Checkpoints** (◐; TS 1.7 + 5.4 S5; checkpointing docs) — `checkpoints.py`, `checkpoint_lab.py`, `checkpoint_play.py`; 5 × 5; 5 tabs.

**SOURCES.md:** docs rows 28–36; guide-vs-docs rows 14–19 (allowed-tools, argument-hint, rules trigger on read, Grep/Glob absent by default, checkpoints docs-only, evaluation partial).

**Bugs found by running:** the wiring script skipped three lookup tables for the second concept (fixed; it now asserts every edit); two playground tabs had an empty first example so Send did nothing; memory_lab's fnmatch let `*` cross directories (contradicting the docs' `*.md` = root only).

**Not verified:** rendered chart width and layout (no Graphviz binary or browser here). **Uncommitted.**


## 2026-09-28 — CONCEPTS D4: D4.1, D4.3, D4.4, D4.7, D4.9, D4.10

**Built (docs-grounded, verified by running):**

| # | Concept | Guide | Distractors × scenarios | Playground engine |
|---|---|---|---|---|
| 1 | D4.1 System Prompts | TS 4.1 | 4 × 4 | review |
| 2 | D4.3 Batch API | TS 4.5 | 7 × 7 | batch |
| 3 | D4.4 Structured Outputs | TS 4.3 + 4.4 | 6 × 5 | extract |
| 4 | D4.7 Attention Engineering | TS 5.1 + docs | 4 × 4 | attention |
| 5 | D4.9 Prompt Engineering Techniques | TS 4.2 + 3.5 | 6 × 5 | fewshot |
| 6 | D4.10 Multi-Pass Review | TS 4.6 | 5 × 5 | mpreview |

**Not built, by rule:** D4.2 Prompt Caching (awareness only), D4.5 Vision and D4.6 Streaming (out of scope), D4.8 4D Framework (no official docs basis).

**Verified:** every variant × scenario matrix matches its `observe` text. All 24 built concepts pass the regression with earlier matrices unchanged, and all 979 DOT graphs parse. AppTest renders every page with its tabs, and every practice answer is accepted. The default page, Home, Exam Blueprint and the Concepts index show no exceptions.

**Bugs found by running:**
- The knob name `prompt_style` clashed with an existing one; it was renamed to `instruction_style`.
- The D4.1 prompt splitter didn't split severity lines; the regex is fixed.
- The D4.4 due date was ambiguous in both conventions; it was changed so the day/month rule matters.
- D4.7 had a headers knob the simulation didn't model; it was removed.

**SOURCES.md:** docs rows 37–39; guide-vs-docs rows 20–23 (batch and tools, few-shot count, long-context placement, confidence for routing vs escalation).

**Not verified:** rendered chart width and layout (no browser here). **Uncommitted.**

### 2026-09-28 (later) — D4.2 Prompt Caching as an awareness page

The user asked not to skip D4.2. **Guide check:** no task statement mentions prompt caching. Its only appearance is the Appendix's out-of-scope list: implementation details are out of scope beyond knowing it exists (p.39).

**Built:** an ℹ️ awareness page with no lab, no playground and no implementation detail. It covers:

- the summary, a mental model, and the exam box;
- what it is and isn't, with 5 sub-concepts, each with a 🧭 line;
- 5 wrong answers that reach for caching to fix quality, stale-context or agent-context problems (labelled 💡 my recommendation, derived from the docs);
- a caching vs Batch API table;
- 3 practice items, kept out of the bank;
- a FAQ and the grounding list.

**Code changes:**

- New `AwarenessContent` dataclass.
- New `concept_page._render_awareness`.
- `load_content` falls back to `AWARENESS`.
- The sidebar marker is `ℹ️📘` and the index card shows "📘 awareness page".

**Verified:** py_compile passes. The page renders in AppTest with 0 exceptions, and 3/3 practice answers are accepted. The index, Home, Exam Blueprint and the full concept regression are unchanged. **Uncommitted.**

### 2026-09-28 (later) — Practice questions grounded in guide scenarios and pinned to guide bullets

The user asked that every quiz question be grounded in the guide's scenarios and linked to what the exam tests, starting at D1.3 and filling gaps in the earlier ones.

**Audit before:**
- 129 questions, 98 of them bank items.
- Scenario tags existed but weren't shown on the page.
- No question was pinned to a guide bullet.
- 29 docs items had no scenario, and several were recall ("Per the docs, what…").
- Many correct answers sat in position B, and all of D1.1's did.

**Done:**
- `Question.points` added and validated at import. A bank item without a pin or scenario is rejected.
- Pages show a 📋 scenario banner above each question and a "⭐ What this tests" reference after answering.
- Question sets rewritten for D1.2–D4.10: 22 concepts, in exam style.
- D1.1 pinned, with its answer positions rebalanced.
- Docs items reframed into scenarios, as judgment rather than recall.
- New `docs/QUESTION_MAP.md` coverage map.

**Result:**
- 173 questions: 138 bank items and 35 docs/awareness items.
- All 206 bullets of the covered task statements are pinned by at least one question.
- Answer positions: A 34 · B 31 · C 36 · D 37.
- Primary scenarios: S1 33 · S2 30 · S3 24 · S4 20 · S5 14 · S6 17.
- Gaps: only TS 3.6, 5.3, 5.5 and 5.6 (no built concept yet).

**Verified:**
- AppTest on all 25 built concept pages: 0 exceptions, every correct answer accepted, and a banner on every question.
- A wrong answer shows the pin caption.
- Index, Home and Blueprint render cleanly.
- Full regression: matrices unchanged, 979 DOT graphs.

**Uncommitted.**

### 2026-09-28 (later) — Domain 5 concepts: D5.1 Context Window Management, D5.2 Case Facts Block

The user asked to "run all of D5". The concept list has two numbered D5 concepts, and both are now built, docs-grounded and verified by running.

| # | Concept | Guide | Distractors × scenarios | Engine |
|---|---|---|---|---|
| 1 | D5.1 Context Window Management | TS 5.1 (K3, K4, S6) + TS 5.4 (K1, K3, S1, S5) | 5 × 4 | ctxwin |
| 2 | D5.2 Case Facts Block | TS 5.1 (K1, S1, S2) + docs state management | 5 × 4 | casefacts |

**Docs read:** Context windows; Context editing; Compaction; Claude Code "How Claude Code works"; prompting best practices (state management).

**Bugs found by running:**
- The "last 2 messages" knob would have started a request with an assistant turn. It's now "last 3 messages".
- D5.2 labelled variant E's refund_promise failure as "no block". It's now "customer expectations left out".

**Verified:**
- Both matrices through the real runner.
- AppTest: every tab and every practice answer.
- Full regression: 27 concept pages; all earlier matrices unchanged; 1,031 DOT graphs parse.
- Question map: 147 bank questions, 206/206 bullets of the covered task statements.

**Gap flagged to the user:** the concept list has no concept for TS 5.3 (error propagation) or 5.6 (provenance). TS 5.5 (human review) and 3.6 (CI/CD) exist only as unnumbered cross-cutting concepts.

**Uncommitted.**

## 2026-09-27 (late) — Every practice question rewritten to exam style

**Why:** the user found the questions "pretty straightforward" and asked for items "as close as the exam style questions".

**Research — for style only, nothing copied:**
- The official benchmark is the guide's own §9 Sample Questions (12 items, PDF pp.27–33).
- Four community banks were also read (OlivierAlter, hamzafarooq, claudecertifiedarchitects.com, certsafari). They are unverified and were used for style only.
- The sources are recorded in CLAUDE.md (QUESTION RULE → exam-style bar) and in `docs/SOURCES.md` (community rows 2–3).

**The style bar:**
- A 3–5 sentence production symptom with numbers or log evidence.
- A hidden qualifier.
- Wrong options that are real engineering moves failing for a nameable reason.
- An explanation that covers every option.
- The correct option is never the longest.

**What was done:**
- D1.6 was redone first. The user approved it ("the quality of questions are good"), then all 27 pages were redone: 187 items, of which 150 are in the bank.
- Pins were kept, so coverage is unchanged: 208/215 bullets of the covered task statements.
- The D1.6 items add TS 5.6 K1 and S4.
- Items that closely echoed official samples were reframed with different situations and distractors: the batch pre-merge/overnight item (Q11), the per-file review item (Q12), the verify_fact item (Q9) and the test-file rules item (Q6).
- Answer positions: A 41 / B 50 / C 53 / D 43.

**Checks:**
- `chkq.py`: no length tells.
- `test_questions.py`: 0 problems on every page.
- `test_all_pages.py`: 0 exceptions.

**Uncommitted.**


---

## 2026-10-03 — D2.3.0: a live MCP client page over SEC EDGAR (➕ extra)

**Request:** a small project inside the app: an MCP client first, using the SEC EDGAR MCP server; a chat box where a company question leads to the right tool being chosen; lineage and trace; a sequence diagram of the flow.

**Research first:**
- Free finance MCP servers were listed for the user (World Bank Data360 is official; SEC EDGAR, FRED, ECB, IMF are community servers over official data). Bloomberg, S&P Global and Moody's need paid subscriptions.
- Read modelcontextprotocol.io (*Architecture overview*, *Server → Tools*) and the server's repo page. Recorded in `docs/SOURCES.md` (community row 4).

**Built:**
- `utils/mcp_live.py`: the client and agent loop. One session per question (start the server → `initialize` → `tools/list` → loop → close). Gemini chooses the tool; results are normalised into ok / `isError=true` / soft error (`success:false` with `isError=false`). It extracts CIK, forms, dates and accession numbers for lineage and digit-matches the answer's figures against the tool results.
- `utils/mcp_seq.py`: sequence diagrams drawn from the run's own event log.
- `pages/c23_mcp_sec_edgar.py`: setup checks, the flow diagram, concept and code-pattern expanders, the gold "what IS on the exam" table, tool discovery with a "tools offered" selector, the chat, a manual mode (you choose the tool; works with no model key), traps, and a what-runs-where note.
- `app.py`: the page is listed after D2.3 in the sidebar. `concepts_map` is untouched.
- `requirements-mcp.txt` (optional): `mcp>=1.30,<2` and `sec-edgar-mcp`. `sec-edgar-mcp` 1.0.8 does not start on `mcp` 2.x.
- `.env.example`: a commented `SEC_EDGAR_USER_AGENT` line. The real value is in the local `.env` only.

**Seen in live runs (2026-10-03), used as the page's traps:**
- `search_companies` returned an empty success for Apple, Microsoft, Tesla and Berkshire Hathaway.
- `get_cik_by_ticker("ZZZZZZ")` returned `success:false` with `isError=false`; only a missing required argument gave `isError=true`.
- After an empty search the model used tickers it already knew, despite the system prompt.
- 21 tool definitions cost about 3,700 input tokens per model call; 3 tools about 475.

**Checks:**
- Page test (AppTest): connect, an example question, a restricted-tools question through the chat box, manual mode — 0 exceptions.
- Missing SEC contact, missing model key and missing packages each show a clear message.
- `app.py` starts with 0 exceptions; `py_compile` is clean.

**Not done:** not viewed in a real browser by Claude. The MCP server build is the next step. **Uncommitted.**


### 2026-10-04 — D2.3.0 simplified

**Feedback:** "there is too much info… all I need is a simple view of the flow, when tools are used, what tool is used, when the SEC website is hit and what is the actual result (printed on the page, not a JSON message)."

**Changed:**
- The page is now a question box, the answer, and "What happened, step by step": one card per tool call showing the tool, what it says it does, what was sent, the sec.gov requests made during that call, and the result as readable tables.
- The sec.gov requests are real, not inferred: the server is started through a one-line launcher that turns on `urllib3` debug logging, and `utils/mcp_live.py` reads the request lines the server logs during each `tools/call` (httpx and requests).
- Removed from the page: the concept and code-pattern expanders, the exam table, the tool list and "tools offered" selector, manual mode, the lineage tab, the traps table, progress ticks. The diagram, tokens and raw JSON are in one collapsed Details expander.
- An empty model reply (seen once live) is retried once and reported as a failure if it repeats.
- Fixed earlier the same day: `No module named pywintypes` (the app had to be restarted after the packages were installed), and answers appearing off-screen (the question box now sits above the answer).

**Seen live:** `search_companies` returns an empty list without contacting sec.gov; `get_cik_by_ticker` fetches `company_tickers_exchange.json`; `get_financials` and `get_recent_filings` fetch the company's submissions JSON and the filing text.

**Checks:** page test with four question types (figures, a list of filings, insider transactions, an unknown company): 0 exceptions. **Uncommitted.**

**Later the same day (user request):**
- "What happened, step by step" is now one table in time order: step, request type (model request, MCP `initialize` + `tools/list`, MCP `tools/call`, HTTP GET to sec.gov), what was sent or fetched, outcome, time. The readable results follow under "What each tool returned".
- Pressing Ask clears the previous result at once. Only the latest question is shown, and questions no longer carry memory of earlier ones.
- Empty model replies: one question got an empty reply (thinking tokens, no text, no function call) in about half of 5 runs. With `thinking_budget=0` the same question answered 5 out of 5, and 3 other questions answered too. An empty reply is still retried (twice) and then reported as a failure.

**Checks:** page test with two questions in a row (the second replaces the first), app start, and the three missing-setup messages: 0 exceptions. **Uncommitted.**

**Synthesis agent and charts (user request, same day):** "a synthesis agent which will curate the responses from all the tools… include capabilities to draw comparison charts… what type of chart will be chosen by the LLM."
- `mcp_live.synthesise()`: a second model call with its own system prompt and no tools. Its input is the question plus every tool result; nothing is inherited from the research agent. It returns schema-constrained JSON: headline, summary, key points, caveats and up to 3 chart specs (type, title, reason, series, points with `source_call`).
- Chart types offered to the model: bar, grouped bar, line, stacked bar. Pie was left out on purpose (part-to-whole reads better as a stacked bar).
- `utils/mcp_charts.py` draws them. Each plotted value is searched for in the tool result it cites: found, found in another call (the source is corrected), or not found (drawn hatched, flagged in the table beside the chart).
- The research agent's prompt now tells it to gather the same data for every company and to reply briefly; `MAX_TURNS` is 12.
- Chart colours follow the dataviz skill's reference palette (first four slots). Its validator script needs Node, which is not installed here, so it was not run; the palette is used unchanged.

**Seen live:**
- "Compare the revenue and net income of Apple, Microsoft and Alphabet": three `get_financials` calls in one model turn; the synthesis agent chose two bar charts (one per measure) and warned that Microsoft's figures come from a 10-K and the others from 10-Qs, with different period ends. All 6 plotted values were found in the tool results.
- "How has Apple's revenue changed from 2021 to 2024?": the server's `compare_periods` tool fails with an internal error, so there is no data, no synthesis and no line chart. The page shows the failure.

**Checks:** engine runs for 5 question types; page test for comparison, failing-tool and out-of-scope questions; app start: 0 exceptions. Charts of all four types were rendered and looked at. **Uncommitted.**

**Own MCP server (user request, same day):** "create my own mcp server component… tools to get details from my laptop like hardware spec, file storage… also a tool to search the web."
- `mcp_servers/laptop_server.py` (FastMCP, stdio): `get_hardware_spec`, `get_storage`, `get_folder_sizes(path)` (home folder only, 8-second budget, reports `complete: false` when cut short), `web_search(query, max_results)` (the `ddgs` package, no key).
- Failures use `ToolError` with `errorCategory`, `isRetryable` and a message: a path outside home is a `permission` error, a missing folder or empty query is a `validation` error, an unreachable search service is `transient` and retryable. An empty search returns `count: 0`.
- Nothing identifying is returned: no computer name, user name, serial numbers, network addresses or file contents.
- `utils/mcp_live.py` now connects to several servers (one `ClientSession` each, `AsyncExitStack`), merges their tool lists and routes each call to the owning server. The page has a server picker; the steps table shows a Connect row per server and which server each tool call went to.
- Web rows: the laptop server logs a `NET …` line per search; the client reads it the same way it reads sec-edgar's HTTP log lines.
- The synthesis agent drops any chart with fewer than two numbers (it once drew a one-bar chart).

**Seen live:**
- With 25 tools from 2 servers offered, the model chose `get_hardware_spec` for "what laptop is this", `get_storage` for "how full are my drives" (the synthesis agent chose a stacked bar: used + free), `get_financials` for an Apple question, and chained `get_hardware_spec` → `web_search("<processor name> release date")` for a processor question.
- Asked about C:\Windows, the model declined without calling the tool, quoting the tool description's home-folder limit. Called directly, the server refuses with a `permission` error.
- Connecting takes about 2 s for my-laptop and 4 s for sec-edgar; the first model call carries about 4,600 input tokens of tool definitions.

**Checks:** the server on its own (8 calls incl. 3 failure cases); the engine on 5 question types; the page on 2; app start: 0 exceptions. **Uncommitted.**

**Split into two pages (user correction, same day):** "one for EDGAR which only helps to understand the MCP client process with the MCP server hosted separately… another subtopic which will host the server at my end… both should have a simple schematic and a sequence diagram showing the difference… on separate webpages."
- The combined page is gone. `utils/mcp_page.py` renders both; `pages/c231_mcp_hosted.py` (D2.3.1) and `pages/c232_mcp_local.py` (D2.3.2) are one-line files. Each page connects to one server only.
- **The SEC does not host an MCP server**, and the user was told so. To give a real "hosted separately" setup, `sec-edgar-mcp` now runs as its own service over Streamable HTTP at `http://127.0.0.1:9870/mcp` (loopback only). The client connects by URL and refuses to run when nothing is listening. A Start/Stop box on the page stands in for the provider (`mcp_live.start_service` / `stop_service`).
- D2.3.2 keeps stdio: the client launches `mcp_servers/laptop_server.py` as a child process.
- Each page opens with a Graphviz schematic, a sequence diagram of that setup, and an 8-row hosted-vs-local comparison table with a link to the other page. The steps table names the transport on each MCP row.
- Seen live: connecting over HTTP to the running service took about 0.1 s; starting the service took about 5 s; starting the stdio server took about 2 s per question.

**Checks:** both pages end to end (local: ask; hosted: stopped → start → ask → stop); both schematics parse; app start and missing-setup messages: 0 exceptions. **Uncommitted.**

**All MCP server features, on both pages (user request, same day):** "add more tools… a list of tools available should be tabulated… add additional features of the MCP like the resources and other key components… for both local and the remote one."
- Read modelcontextprotocol.io *Understanding MCP servers* for the control model: tools are model-controlled, resources application-controlled, prompts user-controlled.
- `mcp_servers/laptop_server.py` now has 9 tools (new: `summarize_file_types`, `get_top_processes`, `estimate_disk_runway`, `check_internet`, `save_note`), 3 resources and 1 template (`laptop://catalog/folders` and `laptop://policy/cleanup` are MOCK data; `laptop://notes`; `laptop://drive/{letter}`), 3 prompts (`health_check`, `cleanup_plan`, `can_it_run`), progress and log notifications from the two folder-walking tools, an elicitation in `save_note` (the only tool that writes), and read-only / open-world annotations on every tool.
- `mcp_servers/edgar_hosted_server.py` is the hosted stand-in: the community package's 21 tools registered unchanged, plus `edgar://tickers` (40 rows fetched from sec.gov's `company_tickers_exchange.json` on 2026-10-04), `edgar://forms`, the template `edgar://company/{ticker}`, and 3 prompts.
- Client (`utils/mcp_live.py`): `catalog()`, `read_resource()`, `get_prompt()`; `ask()` takes `attach` (resources read by the application and put in the model's context) and `confirm` (the pre-set answer to an elicitation); progress and log notifications are collected per tool call.
- Pages (`utils/mcp_page.py`): a "What this server offers" section with four tabs (Tools, Resources, Prompts, All MCP features); the question form can attach resources, use a server prompt and, on the local page, choose Decline / Approve; the steps table shows prompt, resource, notification and "the server asked you" rows.

**Seen live:**
- With `edgar://tickers` attached, "Berkshire Hathaway" was resolved to `BRK-B` from the list; earlier runs guessed `BRK.A` from memory.
- Attaching the ticker list added about 870 input tokens to the first model call; for Nvidia and Broadcom the result was the same with or without it.
- `save_note` with Decline returned `saved: false` and wrote nothing; with Approve it wrote one line, readable at `laptop://notes`.
- `get_folder_sizes` on a 235-entry folder sent 235 progress notifications and one log message; none of them reach the model.
- The community package sets no tool annotations, so its tools table reads "not stated".

**Checks:** the local server on its own (all features); the engine on both servers; both pages (tables, read a resource, prompt with a missing blank, prompt + attachments, save_note declined and approved, hosted start → ask → stop): 0 exceptions. Test notes were deleted afterwards. **Uncommitted.**

**Hang fixed (same day):** the user reported the page stuck on "The model is choosing a tool…". A stack dump of the running app (`py-spy`) showed the script thread waiting on the synthesis agent's Gemini request, which had no timeout. The MCP server had already finished and closed.
- Both model requests now carry a 45-second timeout (`MODEL_TIMEOUT_MS`), and the synthesis reply is capped at 4,000 output tokens (`SYNTH_MAX_TOKENS`).
- If the synthesis agent times out or errors, the tool results and steps table are still shown, with a warning and the research agent's own reply.
- If the research agent's request times out, the page shows "The model did not answer within 45 seconds" instead of an `ExceptionGroup`.
- Tested by forcing each timeout. The cause of the stall itself (Gemini's side or the network) is not known. **Uncommitted.**

**Both MCP pages on the hosted copy (user decision, same day):** opening `https://ccar-f.streamlit.app/concept-mcp-local` showed "The MCP package is not installed". Asked how the pages should behave on Streamlit Cloud, the user chose "Both pages on Cloud".
- `requirements.txt` now includes `mcp>=1.30,<2`, `sec-edgar-mcp>=1.0.8` and `ddgs>=9.0` (this reverses the earlier "optional packages" rule). `requirements-mcp.txt` just points at it.
- `utils/secrets_env.py` copies `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` and `SEC_EDGAR_USER_AGENT` from Streamlit's Secrets into environment variables at app start. This also makes the Gemini demos work on the hosted copy once the key is entered there.
- `mcp_servers/laptop_server.py` has Linux code paths (`/proc/meminfo`, `/proc/cpuinfo`, `ps`, the `/` drive), and the local page warns that on the hosted copy "this computer" is the hosted Linux machine.
- AGENTS.md and docs/ARCHITECTURE.md stack tables updated.

**Checks:** the Linux parsers were tested with sample `/proc` and `ps` text, and the tools with the platform faked as Linux. They were NOT run on a real Linux machine (no WSL or Docker here), so the hosted copy is the first real run. The secrets loader was tested with and without secrets. Both pages and the all-pages regression pass on Windows.

**Hosted page made concrete (user request, 2026-10-04):** "in the sec-edgar page it is not clear where the MCP server is hosted and running… draw boundaries between my laptop, localhost, somewhere else and sec.gov… outline what sec.gov exposes — REST endpoints or what… it is too abstract how the tools translate a chat question into a query… a pseudo code snippet in the app… don't guess, make it factual and grounded."

**Research (all of it read, not recalled):**
- The SEC's *EDGAR APIs* and *Developer resources* pages: four REST endpoints on `data.sec.gov` (submissions, companyconcept, companyfacts, frames), bulk zips on `www.sec.gov`, no authentication or key, a limit of 10 requests per second, no CORS on `data.sec.gov`, and no SQL or query interface mentioned.
- The installed source of `sec-edgar-mcp` 1.0.8 (the tools, the ticker cache) and `edgartools` 5.60.0 (sets the `User-Agent` header from the identity; throttles itself to 8 requests per second).
- 8 tools called twice each on a freshly started service: 44 requests, every one a GET to `data.sec.gov` or `www.sec.gov`, answered 200, none with a query string. The first request in a fresh process is the ticker list; the ticker cache then lives in memory, so a second `get_cik_by_ticker` made no request.

**Built:**
- `utils/mcp_seq.py::schematic_png`: a matplotlib schematic with explicit zones — this machine (named "your laptop" only when the app is on Windows), `localhost` (loopback), "somewhere else across the internet", and the SEC's servers. Matplotlib because there is no Graphviz binary here to look at a layout. Both pages use it.
- `utils/mcp_edgar_facts.py`: the sourced facts (endpoints, rules, the four hops, five tools with pseudo code and the requests observed).
- `utils/mcp_page.py`: the setup section is now tabs. Hosted: Where each part runs · Sequence · What sec.gov exposes · From a question to an SEC request · Hosted vs local. Local: Where each part runs · Sequence · Hosted vs local. The explorer has a "Call this tool now" button (`mcp_live.call_tool`, no model) that lists the requests the server really makes.

**Findings worth keeping (from reading the code and running it):**
- `get_recent_filings` accepts a `days` argument and never uses it: it appears only in the function's signature.
- `get_company_facts` and `get_key_metrics` fetch the companyfacts file (HTTP 200) but return `"metrics": {}` with `success: true`, because the tool reads `facts.data` and the installed edgartools returns an `EntityFacts` object that has no `.data`.
- `get_financials` takes the later of the latest 10-K and the latest 10-Q, so "latest" can be a quarterly report.

**Correction:** an earlier entry and some page text said "the SEC hosts no MCP server". What was actually checked: the project's README says it is not affiliated with the SEC, and the SEC pages read list data APIs and files, not an MCP server. The page text now says exactly that.

**Checks:** both schematics (3 variants) rendered and looked at; both pages tested end to end (tabs, tables, each explorer tool, the live call with a changed ticker, invalid JSON, service stopped and running); local page unchanged apart from the new tabs. **Uncommitted.**

**New page D2.3.3 — financial-data vendors (user request, 2026-10-04):** "a simple table, like the MCP server outline in 2.3.1, with Crunchbase, ZoomInfo, FactSet, SharkRepellent, rating agencies (Moody's, S&P, Fitch), DealInfo, Contexa… list the key MCP or API endpoints, what they commercially sell (high level), how a client accesses the service. Ground it in their official pages. I'm building an investment-banking agent. Add Bloomberg and LSEG."

**Research (vendor pages fetched and read, 2026-10-04):**
- MCP servers found with a published endpoint: Crunchbase (`https://mcp.crunchbase.com`, 14 tools), ZoomInfo (`https://mcp.zoominfo.com/mcp`, 6 tools), Moody's (`https://api.moodys.com/genai-ready-data/m1/mcp`, 5 tools). Described without a URL: FactSet (8 content APIs behind it), S&P/Kensho (remote MCP server for the LLM-ready API), Bloomberg (Enterprise MCP in Data License Plus, 100M+ securities and 30,000+ fields), LSEG (managed MCP server with Microsoft Copilot Studio and in Databricks Marketplace, phased), Fitch (Fitch Nexus).
- REST or library APIs: Crunchbase (`api.crunchbase.com/v4/data/`, 200 calls per minute), ZoomInfo (Search, Enrich, Lookup, Usage; OAuth 2.0), Bloomberg (BLPAPI, Server API, B-PIPE, Data License over REST/SFTP/cloud), LSEG (Data Library, Datastream Web Service).
- SharkRepellent is a FactSet product (takeover-defence and governance data). No MCP server or API for it was found on the pages read.
- "DealInfo": no vendor found. "Contexa": matched a WooCommerce search product, a document-extraction API and an MCP developer platform, none a financial-data vendor. Both are shown as unidentified; the user was asked for the exact names.
- Blocked or unreadable to my tools: Fitch's own domains and the business-wire copy of its release (so Fitch rests on a republished press release); S&P RatingsDirect, S&P's AI-for-developers page and S&P marketplace API page; FactSet's developer-portal pages (script-built, title only); ZoomInfo's REST base URL and rate-limit values.
- No page states a price. No e-mail address is copied into the repo.

**Built:** `utils/vendor_facts.py` (the facts, with a basis label per row), `pages/c233_data_vendors.py` (tabs: At a glance · Vendor details and sources · For an investment-banking agent · What I could not check), `app.py` (sidebar entry after D2.3.2). The page makes no network call and works without keys, so it also works on the hosted copy.

**Checks:** page test (13 rows, 4 basis labels, 11 detail sections, no e-mail or price strings), `app.py` start: 0 exceptions. **Uncommitted.**

**D2.3.3 tools and APIs tab (user request, 2026-10-04):** new tab "Tools and APIs" with a count table, an MCP tools table (vendor, tool, description, MCP inputs, MCP outputs) and a separate REST/library API table. Read for this: Crunchbase tool reference (14 tools), ZoomInfo docs.gtm.ai available tools (19, which corrects the 6 shown earlier), Moody's MCP page (5), Crunchbase using-the-api, LSEG common-APIs summary. FactSet, S&P, Fitch, Bloomberg, LSEG publish no readable tool list; inputs/outputs the pages omit say "not stated". Uncommitted.
