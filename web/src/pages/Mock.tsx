import { useEffect, useMemo, useState } from 'react'
import { store, save, useBank, useCourse, type Question } from '../lib/data'
import { draw, grade, type Result } from '../lib/mock'

type History = { when: string; scaled: number; pct: number; scenarios: number[]; byDomain: Result['byDomain'] }[]
const GATE = 0.8

const clock = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

export default function Mock() {
  const { data: course, error } = useCourse()
  const { data: bank, error: e2 } = useBank()
  const [run, setRun] = useState<{ qs: Question[]; scenarios: number[]; short: number[]; deadline: number } | null>(null)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [i, setI] = useState(0)
  const [left, setLeft] = useState(0)
  const [result, setResult] = useState<Result | null>(null)
  const [history, setHistory] = useState<History>(() => store<History>('mock', []))

  const finish = (qs: Question[], ans: Record<string, number>, scenarios: number[]) => {
    const r = grade(qs, ans)
    setResult(r)
    setRun(null)
    const next = [...history, { when: new Date().toISOString(), scaled: r.scaled, pct: r.pct, scenarios, byDomain: r.byDomain }]
    setHistory(next)
    save('mock', next)
  }

  useEffect(() => {
    if (!run) return
    const tick = () => {
      const s = Math.max(0, Math.round((run.deadline - Date.now()) / 1000))
      setLeft(s)
      if (s === 0) finish(run.qs, answers, run.scenarios)
    }
    tick()
    const t = setInterval(tick, 1000)
    return () => clearInterval(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run])

  const byId = useMemo(() => new Map((bank?.questions ?? []).map((q) => [q.id, q])), [bank])
  if (error || e2) return <p className="err" role="alert">{error ?? e2}</p>
  if (!course || !bank) return <p className="muted">Loading…</p>

  const start = () => {
    const d = draw(bank.questions, course)
    setAnswers({}); setI(0); setResult(null)
    setRun({
      qs: d.ids.map((id) => byId.get(id)!), scenarios: d.scenarios, short: d.short,
      deadline: Date.now() + course.mock.minutes * 60 * 1000,
    })
  }

  if (run) {
    const q = run.qs[i]
    const answered = Object.keys(answers).length
    return (
      <>
        <div className="mock-bar">
          <b className={left < 600 ? 'warn-text' : ''} aria-live="off">{clock(left)}</b>
          <span className="muted small">{answered} / {run.qs.length} answered</span>
          <button className="btn ghost" onClick={() => { if (confirm('Finish and grade the exam now?')) finish(run.qs, answers, run.scenarios) }}>Finish</button>
        </div>
        <article className="qcard">
          <div className="small muted">Question {i + 1} of {run.qs.length} · Scenario {q.scenarios[0]}</div>
          <p className="stem">{q.q}</p>
          <div className="opts" role="radiogroup" aria-label="Answers">
            {q.opts.map((o, n) => (
              <button key={n} role="radio" aria-checked={answers[q.id] === n} className={'opt' + (answers[q.id] === n ? ' picked' : '')}
                onClick={() => setAnswers({ ...answers, [q.id]: n })}>
                <b>{'ABCD'[n]}</b><span>{o}</span>
              </button>
            ))}
          </div>
          <div className="actions">
            <button className="btn ghost" disabled={i === 0} onClick={() => setI(i - 1)}>Previous</button>
            <button className="btn" disabled={i === run.qs.length - 1} onClick={() => setI(i + 1)}>Next</button>
          </div>
        </article>
        <div className="qgrid" aria-label="Jump to question">
          {run.qs.map((x, n) => (
            <button key={x.id} className={'qn' + (answers[x.id] !== undefined ? ' done' : '') + (n === i ? ' here' : '')}
              onClick={() => setI(n)} aria-label={`Question ${n + 1}`}>{n + 1}</button>
          ))}
        </div>
      </>
    )
  }

  if (result) {
    const missed = result.missed.map((id) => byId.get(id)!).filter(Boolean)
    return (
      <>
        <h1>Mock result</h1>
        <div className="stats">
          <div className="stat"><b>{result.correct} / {result.total}</b><span>Correct ({Math.round(result.pct * 100)}%)</span></div>
          <div className="stat"><b>{result.scaled}</b><span>Estimated scaled score (pass mark {course.mock.passScaled})</span></div>
        </div>
        <p className="muted small">{course.mock.scaleNote}</p>
        <div className="scroll">
          <table>
            <thead><tr><th>Domain</th><th>Score</th><th>80% gate</th></tr></thead>
            <tbody>
              {course.domains.map((d) => {
                const r = result.byDomain[d.n]
                const p = r ? r.right / r.total : 0
                return <tr key={d.n}><td>D{d.n} {d.name}</td><td>{r ? `${r.right} / ${r.total}` : '—'}</td><td>{r ? (p >= GATE ? 'Met' : 'Below') : '—'}</td></tr>
              })}
            </tbody>
          </table>
        </div>
        <h2>Missed questions ({missed.length})</h2>
        {missed.map((q) => (
          <details key={q.id} className="miss">
            <summary>{q.id} · TS {q.ts}</summary>
            <p className="stem">{q.q}</p>
            <p><b>Answer {'ABCD'[q.ans]}.</b> {q.opts[q.ans]}</p>
            <p className="small">{q.explain}</p>
          </details>
        ))}
        <div className="actions"><button className="btn" onClick={start}>Take another mock</button></div>
      </>
    )
  }

  return (
    <>
      <h1>Timed mock exam</h1>
      <p className="lead">
        {course.mock.items} questions in {course.mock.minutes} minutes, drawn from 4 of the 6 scenarios at random, with the domain
        mix set by the exam weights. Single answer each; the real exam also has multiple-response items. Your answers are graded at the end.
      </p>
      <div className="actions"><button className="btn" onClick={start}>Start the mock</button></div>
      {history.length > 0 && (
        <>
          <h2>Your earlier mocks (this device)</h2>
          <div className="scroll">
            <table>
              <thead><tr><th>When</th><th>Score</th><th>Estimated scaled</th><th>Scenarios</th></tr></thead>
              <tbody>
                {[...history].reverse().slice(0, 10).map((h) => (
                  <tr key={h.when}><td>{new Date(h.when).toLocaleString()}</td><td>{Math.round(h.pct * 100)}%</td><td>{h.scaled}</td><td>{h.scenarios.join(', ')}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  )
}
