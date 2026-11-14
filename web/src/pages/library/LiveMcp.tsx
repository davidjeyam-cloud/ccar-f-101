import { useState } from 'react'
import Md, { Inline } from '../../components/Md'
import Mermaid from '../../components/Mermaid'
import { useLibrary } from '../../lib/library'
import './LiveMcp.css'

type Tool = { name: string; summary: string; inputs: string[]; readOnly: boolean | null; openWorld: boolean | null; full: string | null }
type Res = { uri?: string; name: string; mime: string | null; description: string | null }
type Tpl = { uri?: string; name: string; mime: string | null; description: string | null }
type Prompt = { name: string; description: string | null; args: { name: string; required: boolean }[] }
type Extra = { kind: 'csv' | 'text'; note: string; rows?: string[][]; text?: string }
type Setup = {
  num: string; title: string; caption: string; whereMermaid: string; whereLegend: string; whereRows: string[][]; whereNote: string
  seqTitle: string; seqMermaid: string; offersNote: string; examples: string[]; aboutNotes: string[]
  offers: { tools: Tool[]; resources: (Res & { uri: string })[]; templates: (Tpl & { uri: string })[]; prompts: Prompt[] }
  resourceExtras: Record<string, Extra>
}
type SecTool = { tool: string; question: string; args: Record<string, unknown>; code: string; first: string[]; second: string[]; note: string }
type Doc = {
  retired: string; readOn: string; versions: string
  compare: { row: string; hosted: string; local: string }[]; compareNote: string
  features: { feature: string; control: string; calls: string; local: string; hosted: string }[]; featuresNote: string
  setups: { hosted: Setup; local: Setup }
  serverRules: { heading: string; rules: string[]; hostedWho: string; hostedWhy: string }
  sec: {
    sources: { name: string; url: string }[]; legend: string; observedNote: string
    endpoints: { host: string; path: string; what: string; how: string; used: string }[]
    rules: { topic: string; fact: string; source: string }[]
    hops: { n: string; what: string; over: string; sent: string }[]
    tools: SecTool[]
  }
}

function Table({ head, rows }: { head: string[]; rows: string[][] }) {
  return (
    <div className="scroll">
      <table className="lm-tbl">
        <thead><tr>{head.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
        <tbody>
          {rows.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j}><Inline>{c}</Inline></td>)}</tr>)}
        </tbody>
      </table>
    </div>
  )
}

const num = (rows: string[][]) => rows.map((r, i) => [String(i + 1), ...r])
const yn = (v: boolean | null, yes: string, no: string) => (v === null ? 'not stated' : v ? yes : no)

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="lm-sec"><h2>{title}</h2>{children}</section>
}

function SecEndpoints({ d }: { d: Doc }) {
  const s = d.sec
  return (
    <Section title="What sec.gov exposes">
      <p><Inline>{s.legend}</Inline></p>
      <h3>Addresses</h3>
      <Table head={['#', 'Host', 'Address', 'What comes back', 'How I know', 'Used by this server?']}
        rows={num(s.endpoints.map((e) => [`\`${e.host}\``, `\`${e.path}\``, e.what, e.how, e.used]))} />
      <h3>Rules</h3>
      <Table head={['#', 'Topic', 'Fact', 'Source']} rows={num(s.rules.map((r) => [r.topic, r.fact, r.source]))} />
      <p className="muted small">Sources: {s.sources.map((x, i) => (
        <span key={x.url}>{i > 0 && ' · '}<a href={x.url} target="_blank" rel="noreferrer">{x.name}</a></span>
      ))}</p>
    </Section>
  )
}

function SecTranslate({ d }: { d: Doc }) {
  const s = d.sec
  const [i, setI] = useState(0)
  const t = s.tools[i]
  const call = JSON.stringify({ name: t.tool, args: t.args }, null, 2)
  const rpc = JSON.stringify({ jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: t.tool, arguments: t.args } }, null, 2)
  return (
    <Section title="From a question to an SEC request">
      <p>There is no SQL and no query language on the way: the model picks a tool and its arguments, and the tool is ordinary Python that builds web addresses and reads what comes back.</p>
      <Table head={['#', 'What happens', 'Over what', 'What is sent']} rows={s.hops.map((h) => [h.n, h.what, h.over, h.sent])} />
      <h3>Pick a tool and see the whole path</h3>
      <label>
        <span className="muted small">Tool</span>
        <select className="lm-select" value={i} onChange={(e) => setI(Number(e.target.value))}>
          {s.tools.map((x, k) => <option key={x.tool} value={k}>{x.tool}</option>)}
        </select>
      </label>
      <p><b>1. You ask:</b> <i>{t.question}</i></p>
      <p><b>2. Gemini answers with a function call</b>, a tool and its arguments, not a query</p>
      <pre className="lm-pre"><code>{call}</code></pre>
      <p><b>3. The client sends it to the server</b> (HTTP POST to the server's address; rebuilt from the call, not captured)</p>
      <pre className="lm-pre"><code>{rpc}</code></pre>
      <p><b>4. The tool runs on the server.</b> Pseudo code, simplified from the package source ({d.versions}). Lines starting with <code>GET</code> are requests to the SEC.</p>
      <pre className="lm-pre"><code>{t.code}</code></pre>
      <p><b>The requests it made</b>: 👁 observed {d.readOn} for Apple, on a freshly started service</p>
      <Table head={['#', 'Method', 'Address', 'Answered']} rows={t.first.map((u, k) => [String(k + 1), 'GET', `\`${u}\``, '200'])} />
      <p className="muted small">First call: {t.first.length} request{t.first.length !== 1 ? 's' : ''}. Called again straight after: {t.second.length}. <Inline>{t.note}</Inline></p>
      {t.second.length > 0 && (
        <details className="lm-details">
          <summary>The requests of the second call</summary>
          <Table head={['#', 'Method', 'Address', 'Answered']} rows={t.second.map((u, k) => [String(k + 1), 'GET', `\`${u}\``, '200'])} />
        </details>
      )}
      <p className="muted small"><Inline>{s.observedNote}</Inline></p>
    </Section>
  )
}

function Offers({ d, kind }: { d: Doc; kind: 'hosted' | 'local' }) {
  const s = d.setups[kind]
  const o = s.offers
  const rows = [...o.resources.map((r) => ({ ...r, tpl: false })), ...o.templates.map((r) => ({ ...r, tpl: true }))]
  const mine = kind === 'local' ? 'On this server (local)' : 'On this server (hosted)'
  const theirs = kind === 'local' ? 'On the hosted server' : 'On the local server'
  return (
    <Section title="What this server offers">
      <p className="muted small">The live page asked the server for these lists with <code>tools/list</code>, <code>resources/list</code> and <code>prompts/list</code>. Recorded from the server code, nothing was run.</p>
      <h3>🛠️ Tools ({o.tools.length})</h3>
      <p className="muted small"><b>The model decides</b> when to call a tool. All it reads is the name and description.</p>
      <Table head={['#', 'Tool', 'What it does', 'Inputs', 'Changes anything?', 'Reaches outside this PC?']}
        rows={num(o.tools.map((t) => [`\`${t.name}\``, t.summary, t.inputs.map((a) => `\`${a}\``).join(', ') || 'none',
          yn(t.readOnly, 'No, read-only', '**Yes**'), yn(t.openWorld, 'Yes', 'No')]))} />
      {s.offersNote && <p className="muted small"><Inline>{s.offersNote}</Inline></p>}
      {kind === 'local' && (
        <details className="lm-details">
          <summary>The full description of each tool (what the model reads)</summary>
          {o.tools.map((t) => <div key={t.name}><h4><code>{t.name}</code></h4><pre className="lm-pre">{t.full}</pre></div>)}
        </details>
      )}
      <h3>📚 Resources ({rows.length})</h3>
      <p className="muted small"><b>The application decides</b> which resources to read and hand to the model. A resource is data to read; it never acts.</p>
      <Table head={['#', 'URI', 'Name', 'Type', 'What it holds']}
        rows={num(rows.map((r) => [`\`${r.uri}\``, r.name + (r.tpl ? ' *(template)*' : ''), r.mime || '—', r.description || '—']))} />
      {Object.entries(s.resourceExtras).map(([uri, x]) => (
        <details className="lm-details" key={uri}>
          <summary><code>{uri}</code>: content</summary>
          <p className="muted small"><Inline>{x.note}</Inline></p>
          {x.kind === 'csv' && x.rows ? <Table head={['#', ...x.rows[0]]} rows={x.rows.slice(1).map((r, i) => [String(i + 1), ...r])} /> : <pre className="lm-pre">{x.text}</pre>}
        </details>
      ))}
      <h3>📝 Prompts ({o.prompts.length})</h3>
      <p className="muted small"><b>The user decides</b> to use a prompt: a ready-made question written by the server's author, with blanks to fill in.</p>
      <Table head={['#', 'Prompt', 'What it asks for', 'Blanks to fill']}
        rows={num(o.prompts.map((p) => [`\`${p.name}\``, p.description || '—',
          p.args.map((a) => `\`${a.name}\`${a.required ? '' : ' (optional)'}`).join(', ') || 'none']))} />
      <h3>🧩 All MCP features</h3>
      <Table head={['#', 'MCP feature', 'Who controls it', 'Protocol calls', mine, theirs]}
        rows={num(d.features.map((f) => [`**${f.feature}**`, f.control, f.calls, kind === 'local' ? f.local : f.hosted, kind === 'local' ? f.hosted : f.local]))} />
      <p className="muted small">{d.featuresNote}</p>
    </Section>
  )
}

function Compare({ d, kind }: { d: Doc; kind: 'hosted' | 'local' }) {
  const [mine, theirs] = kind === 'hosted'
    ? ['Hosted separately (D2.3.1)', 'Local, my own (D2.3.2)'] : ['Local, my own (D2.3.2)', 'Hosted separately (D2.3.1)']
  return (
    <Section title="Hosted vs local">
      <Table head={['#', '', mine, theirs]}
        rows={num(d.compare.map((c) => [`**${c.row}**`, kind === 'hosted' ? c.hosted : c.local, kind === 'hosted' ? c.local : c.hosted]))} />
      <p className="muted small">{d.compareNote}</p>
    </Section>
  )
}

export default function LiveMcp() {
  const { data: d, error } = useLibrary<Doc>('live-mcp')
  const [kind, setKind] = useState<'hosted' | 'local'>('hosted')
  if (error) return <p className="err" role="alert">{error}</p>
  if (!d) return <p className="muted">Loading…</p>
  const s = d.setups[kind]
  return (
    <>
      <h1>Live MCP pages, as a write-up</h1>
      <p className="muted small">➕ Extra: not on the CCAR-F exam · live data was not investment advice</p>
      <div className="warn" role="note"><Inline>{d.retired}</Inline></div>
      <div className="lm-switch" role="group" aria-label="Choose a setup">
        <button type="button" className={kind === 'hosted' ? 'btn' : 'btn ghost'} aria-pressed={kind === 'hosted'} onClick={() => setKind('hosted')}>Hosted (D2.3.1)</button>
        <button type="button" className={kind === 'local' ? 'btn' : 'btn ghost'} aria-pressed={kind === 'local'} onClick={() => setKind('local')}>Local (D2.3.2)</button>
      </div>

      <h2>{s.num} · {s.title}</h2>
      <p className="lead">{s.caption}</p>

      <Section title="Where each part runs">
        <div className="lm-diagram"><Mermaid source={s.whereMermaid} label={`Where each part runs, ${s.num}`} /></div>
        <p className="muted small">{s.whereLegend}</p>
        <Table head={['#', 'Part', 'Runs on', 'Address or evidence']} rows={num(s.whereRows)} />
        <Md>{s.whereNote}</Md>
      </Section>

      <Section title="Sequence of a request">
        <p className="muted small">{s.seqTitle}. The textbook flow; solid arrows are requests, dashed arrows are replies.</p>
        <div className="lm-diagram"><Mermaid source={s.seqMermaid} label={`Sequence diagram, ${s.num}`} /></div>
      </Section>

      {kind === 'hosted' && <SecEndpoints d={d} />}
      {kind === 'hosted' && <SecTranslate d={d} />}

      <Offers d={d} kind={kind} />

      <Section title="What is whose, and what the author controls">
        {kind === 'hosted' ? (
          <>
            <Md>{d.serverRules.hostedWho}</Md>
            <Md>{d.serverRules.hostedWhy}</Md>
          </>
        ) : (
          <>
            <p className="muted small">{d.serverRules.heading}</p>
            <ul className="lm-list">{d.serverRules.rules.map((r, i) => <li key={i}><Inline>{r}</Inline></li>)}</ul>
          </>
        )}
      </Section>

      <Compare d={d} kind={kind} />

      <Section title="Questions the live page offered">
        <p className="muted small">Examples from the retired Ask form. They cannot be run here.</p>
        <ul className="lm-list">{s.examples.map((e) => <li key={e}>{e}</li>)}</ul>
      </Section>

      <Section title="About this page">
        <ul className="lm-list">{s.aboutNotes.map((n, i) => <li key={i}><Inline>{n}</Inline></li>)}</ul>
      </Section>
    </>
  )
}
