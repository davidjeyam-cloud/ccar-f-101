---
description: Build the next pending page (first 🔜 in CLAUDE.md whose prerequisites are done), then run the commit checklist and stop.
---

You are in Stage B of the ccar-f-101 build. Build **exactly one page**, then stop.

## 1. Pick the page
1. Read the **Phase Status** tables in `CLAUDE.md`.
2. Choose the first page marked 🔜 whose prerequisites are done:
   - Phases are worked in order (0 → 7), except that a capstone unlocks only after the phase listed in the **Capstone Protocol** table (06e also needs 06d; 06f is last).
   - `04d` shares the `04c` demo — build `04c` first.
   - Honour the study plan's baseline shortcut only if the user has told you a domain scored ≥ 80%.
3. If nothing qualifies, say so and stop. Do not pick a page yourself if it is ambiguous — ask.
4. Tell the user which page you picked and why, in one or two lines.

## 2. Read before writing
- `docs/source/*.pdf` — the guide's task statement for this page (ground truth). Extract text locally if needed.
- `CLAUDE.md` — Page Structure Standard, Comparison Standard, Execution Trace Standard, Critical SDK Notes.
- The previous built page, to match style.
If the guide is missing, say so and stop.

## 3. Build the page to the standards
- Follow the **Page Structure Standard** in order (diagram → 📖 concept → 📐 Core Code Pattern → demo → 🔍 What just happened → traps table → 🛠️ Build it in VS Code with Claude Code → four progress ticks → What's next).
- ★ pages get a real interactive demo. All other pages are **concept + build**: no live demo, mark them so in the status table.
- Every comparison is a numbered table. Include any mandatory table this page owns (see CLAUDE.md).
- Every model call gets a `🔬 Execution Trace` (finish reason with the Claude term beside it, function_call/response blocks, function-calling mode, token counts). Demos run on Gemini (`gemini-2.5-flash` via `utils/llm.py`); Claude-specific mechanics go in `st.code()` snippets.
- No key must not break the page. Label any simulated output **SIMULATED**.
- **🔑 pages** (see CLAUDE.md → Claude API Key Reminder Standard): put `claude_key_banner(...)` at the top, use the real Claude API for the flagged mechanic, and in your hand-over message remind the user in one line to buy the Claude API key. If you think a page qualifies for 🔑 and it is not flagged, say so and ask.
- Paraphrase the guide. No long copied passages. No real exam questions. Nothing out of scope.
- Add community-sourced claims only with the label "community claim, verify in current docs", and record them in `docs/SOURCES.md`.
- Never state a claim about the exam or Claude Code you have not verified. Say "I'm not sure" or ask.

## 4. Run the commit checklist (CLAUDE.md → Commit Baseline)
1. `py_compile` on `app.py`, `pages/*.py`, `utils/*.py`
2. App starts clean (with and without `GEMINI_API_KEY`)
3. New-page checklist — every box
3b. Sidebar: add this page's slug -> file path to `app.py`'s `_REAL_PAGES` dict, and flip its `PageEntry.built` to `True` in `utils/course_map.py` (see `utils/placeholder.py`'s docstring) — otherwise it stays a placeholder in the sidebar even though it's built
4. Quiz sync: `PHASE_SEEDS` entry (8–12 concepts, 3 snippets) **and** original bank questions tagged by task statement in `utils/question_bank.py`
5. Docs sync: Phase Status table, `pages/00a_Home.py` count/coverage map, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/images/` for new diagrams, `docs/SOURCES.md`
6. Secret scan of what would be staged (see `push.ps1`)

**Never mark the page ✅ until the whole checklist passes.** If something fails, leave 🔜, report what failed, and stop.

## 5. Stop and hand over
1. Tell the user what to build in `sandbox_project/` for this page, with the prompt and the done-when checklist. Then wait — they will do that build with you in this same panel.
2. When the checklist passes, give the commit message (`feat:` / `fix:` / `chore:` / `docs:` style) and remind the user to run `.\push.ps1 "message"`.
3. **Do not run `git push`.** Do not stage or commit unless asked. Do not create or delete GitHub repos.
4. Do not start the next page.
