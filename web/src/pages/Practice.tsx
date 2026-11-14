import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Inline } from '../components/Md'
import { store, save, useBank, useCourse, type Question } from '../lib/data'

type Picks = Record<string, number>

export default function Practice() {
  const { data: course, error } = useCourse()
  const { data: bank, error: e2 } = useBank()
  const [params, setParams] = useSearchParams()
  const ts = params.get('ts') ?? '1.1'
  const [picks, setPicks] = useState<Picks>(() => store<Picks>('practice', {}))
  const [i, setI] = useState(0)
  if (error || e2) return <p className="err" role="alert">{error ?? e2}</p>
  if (!course || !bank) return <p className="muted">Loading…</p>
  const qs: Question[] = bank.questions.filter((x) => x.ts === ts)
  const q = qs[i]
  const done = qs.filter((x) => picks[x.id] !== undefined)
  const right = done.filter((x) => picks[x.id] === x.ans).length
  const choose = (n: number) => {
    if (picks[q.id] !== undefined) return
    const next = { ...picks, [q.id]: n }
    setPicks(next)
    save('practice', next)
  }
  const picked = q ? picks[q.id] : undefined
  return (
    <>
      <h1>Practice</h1>
      <label className="field">Task statement
        <select value={ts} onChange={(e) => { setParams({ ts: e.target.value }); setI(0) }}>
          {course.taskStatements.map((t) => <option key={t.ts} value={t.ts}>{t.ts} — {t.title} ({t.questions})</option>)}
        </select>
      </label>
      <p className="muted small">Score on this task statement: {right} / {done.length} answered (of {qs.length}).</p>
      {q && (
        <article className="qcard">
          <div className="small muted">{q.id} · Scenario {q.scenarios[0]}: {course.scenarios.find((s) => s.n === q.scenarios[0])?.name}</div>
          <p className="stem"><Inline>{q.q}</Inline></p>
          <div className="opts" role="radiogroup" aria-label="Answers">
            {q.opts.map((o, n) => {
              const state = picked === undefined ? '' : n === q.ans ? ' right' : n === picked ? ' wrong' : ''
              return (
                <button key={n} role="radio" aria-checked={picked === n} className={'opt' + state} onClick={() => choose(n)}>
                  <b>{'ABCD'[n]}</b><span><Inline>{o}</Inline></span>
                </button>
              )
            })}
          </div>
          {picked !== undefined && (
            <div className="explain" role="status">
              <p><b>{picked === q.ans ? 'Correct.' : `Not quite — the answer is ${'ABCD'[q.ans]}.`}</b> <Inline>{q.explain}</Inline></p>
              {q.principle && <p className="small"><b>Principle:</b> {q.principle}</p>}
              <p className="small muted">Tests: {q.tests.join(' · ')}</p>
            </div>
          )}
          <div className="actions">
            <button className="btn ghost" disabled={i === 0} onClick={() => setI(i - 1)}>Previous</button>
            <span className="muted small">{i + 1} / {qs.length}</span>
            <button className="btn" disabled={i === qs.length - 1} onClick={() => setI(i + 1)}>Next</button>
          </div>
        </article>
      )}
    </>
  )
}
