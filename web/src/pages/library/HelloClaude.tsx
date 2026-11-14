import Md, { Inline } from '../../components/Md'
import Mermaid from '../../components/Mermaid'
import { useLibrary } from '../../lib/library'

type Table = { headers: string[]; rows: string[][] }
type Doc = {
  retired: string
  mermaid: string
  mermaidTitle: string
  mermaidCaption: string
  whatIs: string[]
  keys: Table
  keyNotes: string[]
  costFacts: string[]
  firstCall: {
    intro: string; code1Label: string; code1: string; wrapper: string
    traceLabel: string; trace: string; whatHappened: string
  }
  principles: string[]
  traps: Table
  build: { prompt: string; done: string[] }
}

function DataTable({ t }: { t: Table }) {
  return (
    <div className="scroll">
      <table>
        <thead><tr>{t.headers.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
        <tbody>
          {t.rows.map((r, i) => (
            <tr key={i}>{r.map((c, j) => (j === 0 ? <th key={j} scope="row"><Inline>{c}</Inline></th> : <td key={j}><Inline>{c}</Inline></td>))}</tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function HelloClaude() {
  const { data, error } = useLibrary<Doc>('hello-claude')
  if (error) return <p className="err" role="alert">{error}</p>
  if (!data) return <p className="muted">Loading…</p>
  return (
    <>
      <h1>Hello Claude</h1>
      <p className="lead">Read-only write-up of the first Streamlit page: three keys, three jobs.</p>
      <div className="warn" role="note"><Inline>{data.retired}</Inline></div>

      <h2>{data.mermaidTitle}</h2>
      <Mermaid source={data.mermaid} label={data.mermaidTitle} />
      <p className="muted small">{data.mermaidCaption}</p>

      <h2>What is CCAR-F, and why Gemini?</h2>
      {data.whatIs.map((p, i) => <Md key={i}>{p}</Md>)}

      <h2>The three keys at a glance</h2>
      <DataTable t={data.keys} />
      {data.keyNotes.map((p, i) => <Md key={i}>{p}</Md>)}
      <h3>Cost notes (dated facts, not updated)</h3>
      <ul>{data.costFacts.map((c, i) => <li key={i}><Inline>{c}</Inline></li>)}</ul>

      <h2>The first live call</h2>
      <p><Inline>{data.firstCall.intro}</Inline></p>
      <p className="small"><strong>{data.firstCall.code1Label}</strong></p>
      <pre><code>{data.firstCall.code1}</code></pre>
      <Md>{data.firstCall.wrapper}</Md>
      <p className="small"><strong>{data.firstCall.traceLabel}</strong></p>
      <pre><code>{data.firstCall.trace}</code></pre>
      <Md>{data.firstCall.whatHappened}</Md>

      <h2>Principles the page followed</h2>
      <ul>{data.principles.map((p, i) => <li key={i}><Inline>{p}</Inline></li>)}</ul>

      <h2>Common traps</h2>
      <DataTable t={data.traps} />

      <h2>Build it in VS Code with Claude Code</h2>
      <p className="small">Prompt to try in the Claude Code panel:</p>
      <blockquote><Inline>{data.build.prompt}</Inline></blockquote>
      <p className="small"><strong>Done when:</strong></p>
      <ul>{data.build.done.map((d, i) => <li key={i}><Inline>{d}</Inline></li>)}</ul>
    </>
  )
}
