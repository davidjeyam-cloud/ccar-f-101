import { Link } from 'react-router-dom'
import { useLibrary } from '../../lib/library'

type File = { label: string; href: string; size: string }
type Item = { id: string; title: string; kind: string; text: string; read: string; readLabel?: string; files: File[]; caveat: string }
type Reading = { intro: string; items: Item[] }

export default function Reading() {
  const { data, error } = useLibrary<Reading>('reading')
  if (error) return <p className="err" role="alert">{String(error)}</p>
  if (!data) return <p className="muted">Loading…</p>

  return (
    <>
      <h1>📎 Reading: cheatsheets</h1>
      <p className="lead">{data.intro}</p>
      <div className="grid">
        {data.items.map((it) => {
          const inApp = it.read.startsWith('/library/')
          return (
            <div className="card" key={it.id}>
              <b>{it.title}</b>
              <div className="chips"><span className="chip">{it.kind}</span></div>
              <div className="small">{it.text}</div>
              <div className="actions">
                {inApp
                  ? <Link className="btn" to={it.read}>Read here</Link>
                  : <a className="btn" href={it.read} target="_blank" rel="noreferrer">{it.readLabel ?? 'Open'}</a>}
                {it.files.map((f) => (
                  <a className="btn ghost" key={f.href} href={f.href} download>{f.label} ({f.size})</a>
                ))}
              </div>
              <div className="small muted">{it.caveat}</div>
            </div>
          )
        })}
      </div>
      <p className="small muted">
        Reading these is a supplement. The practice questions and the concept pages remain the way to check you can apply it.
      </p>
    </>
  )
}
