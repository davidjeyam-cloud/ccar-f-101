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

