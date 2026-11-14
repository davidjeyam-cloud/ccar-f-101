import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useCourse } from '../lib/data'

const KIND: Record<string, string> = {
  exam: 'Exam topic', extra: 'Extra – not on the exam', ungroundable: 'No docs basis', excluded: 'Out of scope / awareness',
}

export default function Concepts() {
  const { data: course, error } = useCourse()
  const [tab, setTab] = useState<string>('map')
  const list = useMemo(() => {
    if (!course) return []
    if (tab === 'all') return course.concepts
    if (tab === 'cross') return course.concepts.filter((c) => !c.code)
    return course.concepts.filter((c) => String(c.domain) === tab && c.code)
  }, [course, tab])
  if (error) return <p className="err" role="alert">{error}</p>
  if (!course) return <p className="muted">Loading…</p>
  const gaps = course.taskStatements.filter((t) => !t.labs.length)
  const tabs: [string, string][] = [
    ['map', 'Course map'], ['all', 'All'], ...course.domains.map((d): [string, string] => [String(d.n), `D${d.n}`]), ['cross', 'Cross-cutting'],
  ]
  return (
    <>
      <h1>Concepts</h1>
      <p className="lead">
        The course map shows every guide task statement against the labs and questions that cover it. The runnable code labs
        still live in the Streamlit app; this app starts with the map, practice and the mock exam.
      </p>
      <div className="tabs" role="tablist">
        {tabs.map(([k, l]) => (
          <button key={k} role="tab" aria-selected={tab === k} className={tab === k ? 'tab on' : 'tab'} onClick={() => setTab(k)}>{l}</button>
        ))}
      </div>
      {tab === 'map' ? (
        <>
          {gaps.length > 0 && (
            <p className="warn">No built lab yet for: {gaps.map((g) => `TS ${g.ts} ${g.title}`).join(' · ')}. Their questions exist.</p>
          )}
          <div className="scroll">
            <table>
              <thead><tr><th>TS</th><th>Task statement</th><th>Domain</th><th>Labs</th><th>Still to build</th><th>Qs</th></tr></thead>
              <tbody>
                {course.taskStatements.map((t) => (
                  <tr key={t.ts}>
                    <td><Link to={`/practice?ts=${t.ts}`}>{t.ts}</Link></td><td>{t.title}</td><td>D{t.domain}</td>
                    <td>{t.labs.length ? t.labs.map((code, i) => {
                      const hit = course.concepts.find((c) => c.code === code)
                      return <span key={code}>{i > 0 && ', '}{hit ? <Link to={`/concepts/${hit.slug}`}>{code}</Link> : code}</span>
                    }) : '—'}</td><td className="small">{t.pending.join('; ') || '—'}</td><td>{t.questions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <div className="grid">
          {list.map((c) => (
            <div className="card" key={c.slug}>
              <div className="small muted">{c.code ?? 'Cross-cutting'} · {KIND[c.kind]}{c.built ? ' · page built' : ''}</div>
              <b>{c.built ? <Link to={`/concepts/${c.slug}`}>{c.title}</Link> : c.title}</b>
              <div className="small muted">{c.guide || 'No guide task statement'}</div>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
