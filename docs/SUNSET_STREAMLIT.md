# Sunsetting Streamlit - parity checklist

Decision (user, 2026-11-14): retire the Streamlit app. The React app (`web/`, on Cloudflare) takes over, nothing is left behind, and all future code changes happen in `web/` only.

**Nothing is deleted until every row below is either ✅ in React or explicitly dropped by the user, and the user approves the removal.** Everything stays recoverable from git: the final Streamlit commit is tagged `streamlit-final` before any deletion.

Inventory taken 2026-11-14: 15 Streamlit pages, 90 `utils/` modules, 28 concept content modules, 49 lab and playground modules, 2 MCP servers.

## Parity matrix

| # | Streamlit piece | In React today? | What it takes | Needs a decision? |
|---|---|---|---|---|
| 1 | Home dashboard | ✅ | done | |
| 2 | Concepts index, course map | ✅ | done | |
| 3 | 28 concept pages: reading content, flowcharts, exam box, distractors, FAQ, practice | ✅ | done; the JSON in `web/public/data/concepts/` is now the source | |
| 4 | Concept code labs: the **Run** button, editable Python, flowchart lit up by the run | ❌ | The lab runtime is pure standard-library Python (checked). It could run unchanged in the browser via Pyodide (untested here), or be rewritten in TypeScript, or dropped | **Yes** |
| 5 | Agent playground: message box and knobs per sub-concept (47 engine modules) | ❌ | Same choice as row 4 | **Yes** |
| 6 | Timed Mock | ✅ | done | |
| 7 | Practice by task statement (replaces the 46 phase placeholder pages) | ✅ | done | |
| 8 | 07b Error Log and the four readiness gates | ❌ | Port. Needs storage: this device only (localStorage), or a Cloudflare D1 database to sync phone and laptop | Storage choice |
| 9 | 07c Exam Day (paraphrased guide §11-16 plus a saved checklist) | ✅ | Ported 2026-11-14 to `/library/exam-day`; the checklist is saved per device | |
| 10 | 00b Exam Blueprint (format, timing, scoring, policies, out-of-scope list) | ✅ | Ported 2026-11-14 to `/library/blueprint` | |
| 11 | 00 Hello Claude (three keys, first live call) | ✅ write-up | Ported as a read-only write-up at `/library/hello-claude`; the live call is dropped (decision 2) | **Yes** |
| 12 | Section 10 MCQs: 40 evidence-backed questions (10.1 MCP, 10.2 Skills, 10.3 D2) and 10.0 study sources | ✅ | Ported 2026-11-14: `/library/mcqs/{mcp,skills,d2}` (40 questions with word-for-word evidence) and `/library/mcq-sources`. The verifier script stays in git history only | Where the verifier lives |
| 13 | D2.3.3 financial-data vendors table | ✅ | Ported 2026-11-14 to `/library/vendors` | |
| 14 | D2.3.4 Oracle chat-to-SQL Mermaid page | ✅ | Ported 2026-11-14 to `/library/oracle` (Mermaid) | |
| 15 | D2.3.1 / D2.3.2 **live MCP pages** (a real client talking to a hosted and a local MCP server) | ✅ write-up | Ported as a read-only write-up at `/library/live-mcp` (hosted and local); the live clients are dropped (decision 2) | **Yes** |
| 16 | The two MCP servers (`mcp_servers/`) | dropped | The two servers stay in git history (`streamlit-final`); the write-up records what they offer | **Yes** |
| 17 | Gemini demos and the LLM quiz generator (`utils/llm.py`, `utils/quiz.py`) | dropped | Gemini demos and the LLM quiz generator are dropped (decision 2); the project needs no API key any more | **Yes** |
| 18 | Personal progress (`progress.json`): ticks, mock history, error log | partly | React keeps its own per-device copy; the old file holds only 2 concept entries | |
| 19 | Python content modules as the **source of truth** for questions and concepts | ❌ | "Changes in React only" means moving the content into `web/` as the source of truth (JSON/TS), instead of generating it from Python | **Yes** |
| 20 | The Streamlit Cloud app (https://ccar-f.streamlit.app/), `.streamlit/`, `requirements*.txt`, `push.ps1` Streamlit parts, port 9000 / Tailscale serve | n/a | Switch off after parity | |

## Decisions (user, 2026-11-14)

| # | Question | Decision |
|---|---|---|
| 1 | Code labs and agent playgrounds (rows 4, 5) | **Run the existing Python in the browser (Pyodide).** To be proven on real labs first; fall back to the user if it fails |
| 2 | Live MCP pages, MCP servers, Gemini demos, Hello Claude live call (rows 11, 15-17) | **Drop the live parts, keep read-only write-ups** so the information is preserved |
| 3 | Error log, mock history, gates (row 8) | **Cloudflare D1, synced.** The API must sit behind Cloudflare Access: do not expose study data from a public Worker, so this waits for the Access lock |
| 4 | Source of truth (row 19) | **Switch now:** content lives in `web/` as the source; no more generating it from Python |

## Order of work

1. **Freeze** (done): no new features or fixes in Streamlit; `CLAUDE.md` says so.
2. **Prove Pyodide** on real labs (a spike; result below).
3. **Tag `streamlit-final`**, which needs the pending work committed first.
4. **Flip the source of truth** (done 2026-11-14): `web/public/data/` is the source; the lab Python (88 modules, the closure the labs need) was copied to `web/pylab/` and is packed by `web/scripts/build-pylab.mjs` at build time; the export step is gone from `scripts/deploy_web.ps1` and `push.ps1`; the old exporters refuse to run without `--overwrite-from-python`. The final comparison with the archive built from `web/pylab` was again 937 of 937 identical.
5. **Port the static pieces** (done 2026-11-14, by eight parallel agents plus an integrated check): Exam Blueprint, Exam Day, section 10 MCQs and sources, vendors, Oracle, and read-only write-ups for the live MCP pages and Hello Claude, all under `/library/*` with a Library hub. Found and fixed in the phone-width check: the sources tables squeezed into unreadable columns (now cards), unreadable vendor labels (a background tint used as text colour), and diagrams wider than a phone (a swipe hint was added). Not checked: dark mode, and a real phone.
6. **Run buttons and playgrounds in the browser** (Pyodide, in a Web Worker with a 10-second timeout, as the Streamlit runner has).
7. **D1 sync** for the error log, mock history and gates, once the Access lock is on.
8. **Remove:** delete the Streamlit code and Python content, switch off the Streamlit Cloud app and the local service, rewrite `CLAUDE.md` for a React-only project.

## Pyodide spike result (2026-11-14, Node, not yet a browser)

Question: can the existing lab Python run unchanged in the browser? Method: every variant of every built concept's code lab, run against each scenario it is meant for (937 runs), once with the native runner (`utils/lab_runner.py`) and once inside Pyodide through `web/public/pylab/runner.py` (a copy of the harness logic for a long-lived interpreter), comparing stdout, trace events and the raised error.

| Step | Result |
|---|---|
| First run | 896 of 937 identical. The 41 differences were two causes, not a general problem |
| Cause 1 | The evaluation lab imports a concept module that was not in the archive. Fixed: the archive now also packs `concepts_content/` |
| Cause 2 | The hooks lab calls `asyncio.run`, which cannot block in Pyodide's synchronous entry point. Fixed: the runner drives simple `async def` callbacks to the end directly; it fails with a clear message if a program really waits on a timer or the network |
| Final run | **937 of 937 identical.** Pyodide reports Python 3.14.2, the same as the native runner. No run was slower than 2 s; the average was about 0.4 s |

What this does and does not prove:
- It proves the lab runtime is portable: standard library only, same Python version, identical results.
- It does **not** yet prove the browser experience. Still to test: loading Pyodide in a Web Worker in a real browser (including a phone), the first-load download (Pyodide's own files are several MB, plus the 744 KB lab archive), self-hosting versus the jsdelivr CDN, and terminating a runaway program at 10 s.
- The playground engines (`*_play.py`) are in the same archive and use the same runtime, but they were not part of this comparison; they get their own check when they are wired up.
