import { useState } from 'react'
import { useLibrary } from '../../lib/library'
import { store, save } from '../../lib/data'

type Section = { title: string; columns: string[]; rows: string[][]; warning?: string }
type ExamDayData = { title: string; caption: string; sections: Section[]; checklist: string[]; contacts: string }

export default function ExamDay() {
  const { data, error } = useLibrary<ExamDayData>('exam-day')
  const [done, setDone] = useState<string[]>(() => {
    const v = store<unknown>('examday', [])
    return Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : []
  })

  if (error) return <p className="err" role="alert">{String(error)}</p>
  if (!data) return <p className="muted">Loading…</p>

  const toggle = (c: string) => {
    const next = done.includes(c) ? done.filter(x => x !== c) : [...done, c]
    setDone(next)
    save('examday', next)
  }

  return (
    <>
      <h1>🗓️ {data.title}</h1>
      <p className="muted small">{data.caption}</p>

      {data.sections.map(s => (
        <section key={s.title}>
          <h2>{s.title}</h2>
          <div className="scroll">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  {s.columns.map(c => <th key={c}>{c}</th>)}
                </tr>
              </thead>
              <tbody>
                {s.rows.map((r, i) => (
                  <tr key={i}>
                    <td>{i + 1}</td>
                    {r.map((cell, j) => <td key={j}>{cell}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {s.warning && <p className="warn">{s.warning}</p>}
        </section>
      ))}

      <h2>Your checklist</h2>
      <div>
        {data.checklist.map(c => (
          <label key={c} style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', minHeight: 44, cursor: 'pointer' }}>
            <input type="checkbox" checked={done.includes(c)} onChange={() => toggle(c)} style={{ width: 22, height: 22, flexShrink: 0 }} />
            <span>{c}</span>
          </label>
        ))}
      </div>
      <p className="muted small">{done.length} of {data.checklist.length} done. {data.contacts}</p>
    </>
  )
}
