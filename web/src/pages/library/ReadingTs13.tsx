import { Link } from 'react-router-dom'
import { Inline } from '../../components/Md'
import { useLibrary } from '../../lib/library'

type Table = { headers: string[]; rows: string[][] }
type Doc = {
  ts13: {
    title: string; sub: string; picture: string
    flowAlt: string; toolsAlt: string; perspectiveAlt: string
    questions: Table; receives: Table; wrong: Table; wrongNote: string
    sides: { coordinator: string[]; subagent: string[]; habit: string }
    plan: string[]
  }
}

function DataTable({ t }: { t: Table }) {
  return (
    <div className="scroll">
      <table>
        <thead><tr>{t.headers.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
        <tbody>
          {t.rows.map((r, i) => (
            <tr key={i}>{r.map((c, j) => <td key={j}>{j === 0 || j === 1 ? <b>{c}</b> : c}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Pic({ src, alt }: { src: string; alt: string }) {
  return (
    <>
      <div className="diagram">
        <a href={src} target="_blank" rel="noreferrer">
          <img src={src} alt={alt} style={{ width: '100%', height: 'auto', minWidth: 0, display: 'block' }} />
        </a>
      </div>
      <p className="small muted">Tap the diagram to open it full size.</p>
    </>
  )
}

export default function ReadingTs13() {
  const { data, error } = useLibrary<Doc>('reading')
  if (error) return <p className="err" role="alert">{String(error)}</p>
  if (!data) return <p className="muted">Loading…</p>
  const d = data.ts13

  return (
    <>
      <p className="small"><Link to="/library/reading">← Reading</Link></p>
      <h1>{d.title}</h1>
      <p className="muted small">{d.sub}</p>
      <div className="actions">
        <a className="btn ghost" href="/reading/TS_1.3_cheatsheet.docx" download>Download .docx (540 KB)</a>
        <Link className="btn ghost" to="/practice">Practice TS 1.3</Link>
      </div>

      <div className="mental"><b>🧭 The one-line picture</b><p>{d.picture}</p></div>

      <h2>1. The flow, start to finish</h2>
      <Pic src="/reading/ts-1-3/flow.png" alt={d.flowAlt} />

      <h2>2. Seven questions, seven answers</h2>
      <DataTable t={d.questions} />

      <h2>3. tools vs allowedTools: a worked example</h2>
      <Pic src="/reading/ts-1-3/tools.png" alt={d.toolsAlt} />

      <h2>3b. The same example, from each side</h2>
      <p><b>The coordinator (the agent)</b> holds the permission list.</p>
      <ul>{d.sides.coordinator.map((s, i) => <li key={i}><Inline>{s}</Inline></li>)}</ul>
      <p><b>The subagent</b> holds the toolbox.</p>
      <ul>{d.sides.subagent.map((s, i) => <li key={i}><Inline>{s}</Inline></li>)}</ul>
      <Pic src="/reading/ts-1-3/perspective.png" alt={d.perspectiveAlt} />
      <div className="gold-box"><b>Exam habit:</b> {d.sides.habit}</div>

      <h2>4. What a subagent receives</h2>
      <DataTable t={d.receives} />

      <h2>5. The eight wrong answers the exam tempts you with</h2>
      <DataTable t={d.wrong} />
      <p className="small muted">{d.wrongNote}</p>

      <h2>6. Study plan (about 90 minutes)</h2>
      <ul>{d.plan.map((s, i) => <li key={i}><Inline>{s}</Inline></li>)}</ul>
      <p className="small muted">
        Source: this workbench's Subagents concept page, built from the official guide and the Claude docs. Task is the exam's
        name for the spawn tool; current docs call it Agent.
      </p>
    </>
  )
}
