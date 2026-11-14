import { useLibrary } from '../../lib/library'
import Mermaid from '../../components/Mermaid'
import { Inline } from '../../components/Md'
import './oracle.css'

type Pair = string[]
type Oracle = {
  readOn: string
  keyIdea: string
  main: { mermaid: string; chat: string; sql: string; call: unknown; rowHeads: string[]; rows: Pair[]; answer: string }
  zoom1: { mermaid: string; uri: string; notes: string; toolCall: unknown; catalogueSql: string; catalogueRows: Pair[] }
  zoom2: { mermaid: string; intro: string; question: string; toolsSeen: Pair[]; searchCall: unknown; answer: string }
  oracleLine: string
  notStated: string
  sources: Pair[]
  nextSteps: string
}

const json = (o: unknown) => JSON.stringify(o, null, 2)

function Table({ heads, rows }: { heads: string[]; rows: Pair[] }) {
  return (
    <div className="scroll">
      <table>
        <thead><tr>{heads.map((h) => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j}>{c}</td>)}</tr>)}</tbody>
      </table>
    </div>
  )
}

function Step({ title, sub, children }: { title: string; sub?: string; children: React.ReactNode }) {
  return (
    <div className="card orc-card">
      <strong>{title}</strong>
      {sub && <span className="muted small">{sub}</span>}
      {children}
    </div>
  )
}

const Bubble = ({ who, children }: { who: string; children: string }) => (
  <p className="orc-bubble"><span className="muted small">{who}</span><br />{children}</p>
)

export default function Oracle() {
  const { data, error } = useLibrary<Oracle>('oracle')
  if (error) return <p className="err" role="alert">{error}</p>
  if (!data) return <p className="muted">Loading…</p>
  const { main, zoom1, zoom2 } = data

  return (
    <>
      <h1>Chat question → SQL on Oracle, through MCP</h1>
      <p className="muted small">➕ Extra: not on the CCAR-F exam · the diagram and the cards show the same run, with the same step numbers</p>
      <p className="lead"><Inline>{data.keyIdea}</Inline></p>

      <div className="orc-split">
        <Mermaid source={main.mermaid} label="Layers from you down to the Oracle database: chat, app with the LLM, MCP client, MCP server, database" />
        <div className="orc-cards">
          <Step title="1 · You ask" sub="① chat"><Bubble who="You">{main.chat}</Bubble></Step>
          <Step title="2 · The LLM writes the SQL" sub="② app → ③ client">
            <p className="muted small">A tool call: tool <code>run-sql</code>, with this SQL as its argument 🧪</p>
            <pre><code>{main.sql}</code></pre>
          </Step>
          <Step title="3 · The client sends it" sub="③ client → ④ server"><pre><code>{json(main.call)}</code></pre></Step>
          <Step title="4 · Oracle runs it · 5 · rows come back" sub="④ server ⇄ ⑤ database">
            <Table heads={main.rowHeads} rows={main.rows} />
          </Step>
          <Step title="6 · The LLM answers in words" sub="② app → ① you"><Bubble who="Assistant">{main.answer}</Bubble></Step>
          <p className="muted small">
            🧪 The chat, SQL, names and numbers are my invented example, never run. The <code>tools/call</code> envelope is the MCP message
            shape 📘; the argument name <code>sql</code> is my example, because Oracle's page does not state <code>run-sql</code>'s inputs.
            The SQL is shortened in step 3.
          </p>
        </div>
      </div>

      <h2>Zoom 1 — how does the LLM know the table names?</h2>
      <p className="muted small">To write the three-table join it must know which tables and columns exist. Three routes, A, B and C.</p>
      <div className="orc-split">
        <Mermaid source={zoom1.mermaid} label="Three routes by which the LLM learns the schema: resource, describe-schema tool, catalogue query" />
        <div className="orc-cards">
          <Step title={`A · a resource — ${zoom1.uri} 🧪`}>
            <pre><code>{zoom1.notes}</code></pre>
            <p className="muted small">The app reads it and puts it in the LLM's context before the question. 📘 MCP's docs name database schemas as a resource example.</p>
          </Step>
          <Step title="B · a tool — describe-schema 🧪">
            <pre><code>{json(zoom1.toolCall)}</code></pre>
            <p className="muted small">An invented tool. Whether Oracle's server has one: not stated. ❓</p>
          </Step>
          <Step title="C · a catalogue query — through run-sql">
            <pre><code>{zoom1.catalogueSql}</code></pre>
            <Table heads={['table_name', 'column_name']} rows={zoom1.catalogueRows} />
            <p className="muted small">🏛 Oracle: <code>USER_TAB_COLUMNS</code> describes the columns of the tables you own. That the LLM queries it through <code>run-sql</code> is my example. 🧪</p>
          </Step>
        </div>
      </div>

      <h2>Zoom 2 — a second server</h2>
      <p className="muted small">{data.zoom2.intro}</p>
      <div className="orc-split">
        <Mermaid source={zoom2.mermaid} label="One app with two MCP clients and two servers: Oracle and an example web-search server" />
        <div className="orc-cards">
          <Step title="1 · You ask" sub="① chat"><Bubble who="You">{zoom2.question}</Bubble></Step>
          <Step title="What the LLM is shown" sub="② app"><Table heads={['Server', 'Tools']} rows={zoom2.toolsSeen} /></Step>
          <Step title="2 · Needs the data" sub="③ client A → ④ server A">
            <p className="muted small"><code>run-sql</code> with the SQL from the main example. Result: Customer A, 48,210.00 🧪</p>
          </Step>
          <Step title="3 · Needs the web" sub="③ client B → ④ server B">
            <pre><code>{json(zoom2.searchCall)}</code></pre>
            <p className="muted small">An invented tool and argument. 🧪</p>
          </Step>
          <Step title="4 · One answer" sub="② app → ① you"><Bubble who="Assistant">{zoom2.answer}</Bubble></Step>
        </div>
      </div>

      <hr />
      <p><strong>Oracle's own server</strong> 🏛 — <Inline>{data.oracleLine}</Inline></p>
      <p className="muted small">{data.notStated}</p>
      <p className="small">
        {data.sources.map(([label, url], i) => (
          <span key={url}>{i > 0 && ' · '}<a href={url} target="_blank" rel="noreferrer">{label}</a></span>
        ))}
      </p>
      <p><strong>Expand next:</strong> {data.nextSteps}</p>
      <p className="muted small">Oracle pages read on {data.readOn}.</p>
    </>
  )
}
