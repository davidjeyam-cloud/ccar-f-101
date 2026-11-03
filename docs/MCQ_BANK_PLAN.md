# Plan: exam MCQ bank

Status: IN BUILD. Decisions made by the owner on 2026-11-01. Progress table at the end.

## Decisions
| # | Decision | Choice |
|---|---|---|
| 1 | Organisation | By task statement, every question tagged to a scenario and pinned to guide bullets |
| 2 | Size | max(20, 3 per bullet) per task statement: 734 questions |
| 3 | No repeats | Strict: same wording, same situation with changed details, or same situation and trap. Checked against the 150 bank items, the 40 section 10 items, the 12 guide samples and the bank itself |
| 4 | Variety | Five question types (diagnose, fix, choose, configure, evaluate), three levels |
| 5 | Format | Single answer only, no multiple-response |
| 6 | Source text | Original questions only (default taken; owner did not pick otherwise). Community repos: topics and traps only. Recalled real exam questions excluded (guide sections 13, 14) |
| 7 | Existing questions | Stay where they are, separate from this bank |

## Theme
The exam tests judgment on production tradeoffs. Every question names the one principle it tests (`utils/mcq_bank/principles.py`) and the page shows it after answering.

## Size by task statement
| Bullets | Task statements | Each | Total |
|---|---|---|---|
| 6 | 1.1 1.4 1.5 1.6 3.3 4.1 4.6 | 20 | 140 |
| 8 | 1.2 1.3 1.7 2.1 2.2 3.1 3.4 4.4 4.5 5.3 5.5 | 24 | 264 |
| 9 | 2.3 2.4 2.5 3.2 3.5 3.6 4.2 5.2 5.4 5.6 | 27 | 270 |
| 10 | 4.3 5.1 | 30 | 60 |

## Pipeline
1. Corpus: official pages, guide text, study repos (read only, kept outside the repo).
2. Writer agents, one domain each, one task statement at a time, to the brief.
3. `python -m utils.mcq_bank_verify`: structure, quotes found word for word, no repeat, no copy, scope.
4. Independent review agents: answer each question blind, then audit facts against the official pages. Disagreements resolved against the quotes.
5. Shown on the Phase 1 to 5 placeholder pages, grouped by bullet. `built` stays False.
6. Then Phase 6 (scenario view plus exercise-based questions) and Phase 7 (timed mock). Not started.

## Limits
- No source can prove a question matches the real exam. The benchmark is the guide's 12 samples.
- Some guide conventions have no official page. Those items are marked guide-only.
- Levels are the writer's judgment, not measured difficulty.

## Progress
| Domain | Target | Written | Verified | Reviewed |
|---|---|---|---|---|
| D1 | 152 | 152 | 152 | 152 (blind 151/152; fact audit done, all findings fixed) |
| D2 | 129 | 129 | 129 | 129 (blind + fact audit, findings fixed) |
| D3 | 149 | 149 | 149 | 149 (blind + fact audit, findings fixed) |
| D4 | 145 | 145 | 145 | 145 (blind + fact audit, findings fixed) |
| D5 | 159 | 159 | 159 | fact audit + arithmetic audit done, findings fixed; blind test not re-run on rewritten 5.4-5.6 items |

Total 734, all pass `utils.mcq_bank_verify` (2026-11-03). 284 are guide-only (no official docs page supports the judgment; heaviest in 4.1, 4.4, 5.2, 5.5, 5.6). None is owner-signed-off.
