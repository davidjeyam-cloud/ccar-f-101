import { Inline } from '../../components/Md'
import { useLibrary } from '../../lib/library'

type Repo = { repo: string; stars: number | null; licence: string; lastPush: string; what: string; read: string }
type Site = { name: string; url: string; note: string }
type Diff = { source: string; says: string; docsSay: string; agrees: string; usedIn: string }
type Sources = { foundOn: string; github: Repo[]; gitlab: string; websites: Site[]; disagreements: Diff[] }

export default function McqSources() {
  const { data, error } = useLibrary<Sources>('mcq-sources')
  if (error) return <p className="err" role="alert">{String(error)}</p>
  if (!data) return <p className="muted">Loading…</p>

  return (
    <>
      <h1>📚 10 · MCQs: Study sources</h1>
      <p className="muted small">
        ➕ Extra · found {data.foundOn} · community material is unofficial: the exam guide decides scope, the official docs
        decide facts · used for topics and traps only, nothing copied
      </p>

      <h2>GitHub: {data.github.length} repositories</h2>
      <p className="small muted">Stars, licence and last push as GitHub reported them on {data.foundOn}.</p>
      <div className="grid">
        {data.github.map((r) => (
          <div className="card" key={r.repo}>
            <b><a href={`https://github.com/${r.repo}`} target="_blank" rel="noreferrer">{r.repo}</a></b>
            <div className="chips">
              <span className="chip">★ {r.stars === null ? '—' : r.stars.toLocaleString('en-GB')}</span>
              <span className="chip">licence: {r.licence}</span>
              <span className="chip">last push {r.lastPush}</span>
            </div>
            <div className="small"><b>What it is:</b> {r.what}</div>
            <div className="small"><b>What I read:</b> {r.read}</div>
          </div>
        ))}
      </div>
      <p className="small muted">
        “none” = GitHub shows no licence, so the text stays all-rights-reserved: it can be read, not reused. That is why every
        question here is original and carries a quote from an official page instead.
      </p>

      <h2>GitLab</h2>
      <p>{data.gitlab}</p>

      <h2>Websites</h2>
      <p className="small muted">
        From web search results only; I did not open them, so no claim is made about their quality.
      </p>
      <div className="scroll">
        <table>
          <thead><tr><th>Site</th><th>What the search result says</th></tr></thead>
          <tbody>
            {data.websites.map((w) => (
              <tr key={w.url}>
                <td><a href={w.url} target="_blank" rel="noreferrer">{w.name}</a></td>
                <td>{w.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Where a community source differs from the official docs</h2>
      <p className="small muted">Found while checking the questions.</p>
      <div className="grid">
        {data.disagreements.map((d, i) => (
          <div className="card" key={i}>
            <b>{d.source}</b>
            <div className="small"><b>It says:</b> <Inline>{d.says}</Inline></div>
            <div className="small"><b>The official docs say:</b> <Inline>{d.docsSay}</Inline></div>
            <div className="small"><b>Who agrees with the docs:</b> {d.agrees}</div>
            <div className="small muted">Used in: {d.usedIn}</div>
          </div>
        ))}
      </div>
      <p className="small muted">
        Recorded on {data.foundOn}. The Streamlit app could re-check these claims against the raw repository files with a
        verifier script; that script is legacy and was not run for this port.
      </p>
    </>
  )
}
