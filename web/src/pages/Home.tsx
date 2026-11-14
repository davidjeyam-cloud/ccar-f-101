import { Link } from 'react-router-dom'
import { useBank, useCourse } from '../lib/data'

export default function Home() {
  const { data: course, error } = useCourse()
  const { data: bank } = useBank()
  if (error) return <p className="err" role="alert">{error}</p>
  if (!course) return <p className="muted">Loading…</p>
  const labs = course.concepts.filter((c) => c.built && c.kind === 'exam').length
  const covered = course.taskStatements.filter((t) => t.labs.length).length
  return (
    <>
      <h1>CCAR-F Study Workbench</h1>
      <p className="lead">
        Study for the Claude Certified Architect – Foundations exam: concept labs, scenario-based practice and a timed mock.
        Questions test judgment and trade-offs, not recall.
      </p>
      <div className="stats">
        <div className="stat"><b>{labs}</b><span>Exam concept labs built</span></div>
        <div className="stat"><b>{covered} / {course.taskStatements.length}</b><span>Task statements with a lab</span></div>
        <div className="stat"><b>{bank?.questions.length ?? '…'}</b><span>Exam-style questions</span></div>
        <div className="stat"><b>4 of 6</b><span>Scenarios drawn per sitting</span></div>
      </div>
      <div className="actions">
        <Link className="btn" to="/practice">Practice by task statement</Link>
        <Link className="btn ghost" to="/mock">Start a timed mock</Link>
      </div>
      <h2>The blueprint — 30 task statements</h2>
      <p className="muted small">Green = a concept lab covers it. Tap a cell to practise that task statement.</p>
      <div className="blueprint">
        {course.domains.map((d) => (
          <div className="bp-row" key={d.n}>
            <div className="bp-name"><b>Domain {d.n} — {d.name}</b><span className="badge">{d.weight} of the exam</span></div>
            <div className="cells">
              {course.taskStatements.filter((t) => t.domain === d.n).map((t) => (
                <Link key={t.ts} to={`/practice?ts=${t.ts}`} className={'cell' + (t.labs.length ? ' on' : '')}
                  title={`${t.title} · ${t.questions} questions`}>{t.ts}</Link>
              ))}
            </div>
          </div>
        ))}
      </div>
      <h2>The 6 exam scenarios</h2>
      <ul className="plain">
        {course.scenarios.map((s) => {
          const n = bank?.questions.filter((q) => q.scenarios[0] === s.n).length
          return <li key={s.n}><b>{s.n}.</b> {s.name} <span className="muted">· {n ?? '…'} questions</span></li>
        })}
      </ul>
    </>
  )
}
