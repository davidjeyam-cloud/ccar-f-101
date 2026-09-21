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
