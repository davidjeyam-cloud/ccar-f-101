import { Link } from 'react-router-dom'
import { Inline } from '../../components/Md'
import { useLibrary } from '../../lib/library'

/** A reading document converted from a .docx into simple blocks (see web/public/data/library/reading-*.json). */
type Block =
  | { type: 'h'; level: 1 | 2; text: string }
  | { type: 'p'; md: string }
  | { type: 'ul'; items: string[] }
  | { type: 'table'; headers: string[]; rows: string[][] }
  | { type: 'img'; src: string; alt: string }
type Doc = { title: string; sub: string; blocks: Block[] }

export default function ReadingDoc({ name, docx }: { name: string; docx: string }) {
  const { data, error } = useLibrary<Doc>(name)
  if (error) return <p className="err" role="alert">{String(error)}</p>
  if (!data) return <p className="muted">Loading…</p>

  return (
    <>
      <p className="small"><Link to="/library/reading">← Reading</Link></p>
      <h1>{data.title}</h1>
      <p className="muted small">{data.sub}</p>
      <div className="actions">
        <a className="btn ghost" href={docx} download>Download .docx</a>
      </div>
      {data.blocks.map((b, i) => {
        switch (b.type) {
          case 'h':
            return <h2 key={i}>{b.text}</h2>
          case 'p':
            return <p key={i}><Inline>{b.md}</Inline></p>
          case 'ul':
            return <ul key={i}>{b.items.map((t, j) => <li key={j}><Inline>{t}</Inline></li>)}</ul>
          case 'img':
            return (
              <div className="diagram" key={i}>
                <a href={b.src} target="_blank" rel="noreferrer">
                  <img src={b.src} alt={b.alt} style={{ width: '100%', height: 'auto', display: 'block' }} />
                </a>
              </div>
            )
          case 'table':
            return (
              <div className="scroll" key={i}>
                <table className={b.headers.length >= 4 ? 'rtable' : undefined}>
                  <thead><tr>{b.headers.map((h, j) => <th key={j}>{h}</th>)}</tr></thead>
                  <tbody>
                    {b.rows.map((r, j) => (
                      <tr key={j}>
                        {r.map((c, k) => (
                          <td key={k} data-label={b.headers[k]}>{k === 0 ? <b><Inline>{c}</Inline></b> : <Inline>{c}</Inline>}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
        }
      })}
      <p className="small muted">Tap a diagram to open it full size.</p>
    </>
  )
}
