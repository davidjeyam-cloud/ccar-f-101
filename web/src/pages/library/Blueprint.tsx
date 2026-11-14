import Md, { Inline } from '../../components/Md'
import { useLibrary } from '../../lib/library'

type Rows = { title: string; source: string; rows: string[][] }
type Data = {
  title: string; lead: string; kicker: string
  glance: Rows
  scoring: { title: string; paragraphs: string[]; source: string }
  policies: Rows
  outOfScope: { title: string; source: string; items: string[] }
  next: string
}

export default function Blueprint() {
  const { data, error } = useLibrary<Data>('blueprint')
  if (error) return <p className="err" role="alert">{String(error)}</p>
  if (!data) return <p className="muted">Loading…</p>
  const table = (t: Rows, heads: [string, string]) => (
    <section className="csec">
      <h2>{t.title}</h2>
      <div className="scroll"><table>
        <thead><tr><th>{heads[0]}</th><th>{heads[1]}</th></tr></thead>
        <tbody>{t.rows.map((r, i) => <tr key={i}><td>{r[0]}</td><td><Inline>{r[1]}</Inline></td></tr>)}</tbody>
      </table></div>
      <p className="muted small"><Inline>{t.source}</Inline></p>
    </section>
  )
  return (
    <>
      <p className="muted small">{data.kicker}</p>
      <h1>{data.title}</h1>
      <p className="lead">{data.lead}</p>
      {table(data.glance, ['Item', 'Value'])}
      <section className="csec">
        <h2>{data.scoring.title}</h2>
        {data.scoring.paragraphs.map((p, i) => <Md key={i}>{p}</Md>)}
        <p className="muted small">{data.scoring.source}</p>
      </section>
      {table(data.policies, ['Situation', 'What the guide says'])}
      <section className="csec">
        <h2>{data.outOfScope.title}</h2>
        <div className="scroll"><table>
          <thead><tr><th>#</th><th>Not tested</th></tr></thead>
          <tbody>{data.outOfScope.items.map((t, i) => <tr key={i}><td>{i + 1}</td><td>{t}</td></tr>)}</tbody>
        </table></div>
        <p className="muted small"><Inline>{data.outOfScope.source}</Inline></p>
      </section>
      <section className="csec">
        <h2>What's next</h2>
        <Md>{data.next}</Md>
      </section>
    </>
  )
}
