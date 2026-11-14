import { useState } from 'react'
import { Inline } from '../../components/Md'
import { useLibrary } from '../../lib/library'
import './Vendors.css'

type Link = { label: string; url: string }
type Glance = { vendor: string; group: string; mcp: string; api: string; sells: string; access: string; basis: string }
type Detail = { vendor: string; facts: { topic: string; text: string }[]; sources: Link[] }
type Tool = { vendor: string; tool: string; description: string; inputs: string; outputs: string }
type Rest = { vendor: string; api: string; description: string; inputs: string; outputs: string }
type Data = {
  title: string; readOn: string; caption: string; noPriceNote: string; glanceNote: string; toolsNote: string; nextStep: string
  basis: { label: string; meaning: string }[]
  glance: Glance[]; details: Detail[]
  agentMap: { question: string; sources: string }[]
  patterns: { pattern: string; text: string }[]
  gaps: string[]
  toolCounts: { vendor: string; tools: string; url: string; note: string }[]
  mcpTools: Tool[]; restApis: Rest[]
  dbx: {
    types: { type: string; note: string }[]
    mcp: { provider: string; product: string; offers: string; access: string; basis: string }[]
    sources: Link[]; gaps: string[]
  }
}

const TABS = ['At a glance', 'Tools and APIs', 'Databricks', 'Details and sources', 'For an agent', 'Not checked'] as const

const Links = ({ items }: { items: Link[] }) => (
  <p className="small vd-links"><strong>Pages read:</strong>{' '}
    {items.map((l, i) => (
      <span key={l.url}>{i > 0 && ' · '}<a href={l.url} target="_blank" rel="noreferrer">{l.label}</a></span>
    ))}
  </p>
)

const Field = ({ name, text }: { name: string; text: string }) => (
  <div className="vd-field"><div className="vd-name">{name}</div><div><Inline>{text}</Inline></div></div>
)

export default function Vendors() {
  const { data, error } = useLibrary<Data>('vendors')
  const [tab, setTab] = useState<(typeof TABS)[number]>('At a glance')
  const [filter, setFilter] = useState('all')
  if (error) return <p className="err" role="alert">{error}</p>
  if (!data) return <p className="muted">Loading…</p>

  const shown = data.glance.filter((g) => filter === 'all' || g.basis === filter)
  return (
    <>
      <h1>{data.title}</h1>
      <p className="muted small">{data.caption}</p>

      <p><strong>Basis of each row</strong></p>
      <div className="scroll"><table>
        <thead><tr><th></th><th>Meaning</th></tr></thead>
        <tbody>{data.basis.map((b) => <tr key={b.label}><td>{b.label}</td><td>{b.meaning}</td></tr>)}</tbody>
      </table></div>
      <p className="muted small">{data.noPriceNote}</p>

      <div className="vd-tabs" role="tablist">
        {TABS.map((t) => (
          <button key={t} role="tab" aria-selected={tab === t} className={'btn ghost' + (tab === t ? ' vd-on' : '')} onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>

      {tab === 'At a glance' && (
        <>
          <div className="vd-filter">
            <span className="small muted">Show basis:</span>
            {['all', ...data.basis.map((b) => b.label)].map((f) => (
              <button key={f} className={'btn ghost' + (filter === f ? ' vd-on' : '')} onClick={() => setFilter(f)}>{f}</button>
            ))}
          </div>
          <div className="grid">
            {shown.map((g) => (
              <div className="card vd-card" key={g.vendor}>
                <h3>{g.vendor}{g.group !== '—' && <span className="muted small"> — {g.group}</span>} <span className="chip">{g.basis}</span></h3>
                <Field name="MCP server" text={g.mcp} />
                <Field name="API" text={g.api} />
                <Field name="What they sell (high level)" text={g.sells} />
                <Field name="How a client gets access" text={g.access} />
                {data.details.find((d) => d.vendor === g.vendor || g.vendor.startsWith(d.vendor))?.sources.slice(0, 1).map((s) => (
                  <p className="small" key={s.url}><a href={s.url} target="_blank" rel="noreferrer">{s.label}</a></p>
                ))}
              </div>
            ))}
          </div>
          <p className="muted small">{data.glanceNote}</p>
        </>
      )}

      {tab === 'Tools and APIs' && (
        <>
          <p><strong>MCP tools listed by name on the vendors' pages: {data.mcpTools.length} in total, from 4 vendors (the 11 FactSet names are from a search summary, marked 🔎).</strong></p>
          <div className="scroll"><table>
            <thead><tr><th>#</th><th>Vendor</th><th>Tools listed</th><th>Page</th><th>Note</th></tr></thead>
            <tbody>{data.toolCounts.map((t, i) => (
              <tr key={t.vendor}><td>{i + 1}</td><td>{t.vendor}</td><td>{t.tools}</td>
                <td>{t.url ? <a href={t.url} target="_blank" rel="noreferrer">page</a> : '—'}</td><td>{t.note}</td></tr>
            ))}</tbody>
          </table></div>
          <p><strong>MCP tools</strong> — inputs and outputs as the page states them</p>
          <div className="scroll"><table>
            <thead><tr><th>#</th><th>Vendor</th><th>Tool</th><th>Short description</th><th>MCP inputs</th><th>MCP outputs</th></tr></thead>
            <tbody>{data.mcpTools.map((t, i) => (
              <tr key={i}><td>{i + 1}</td><td>{t.vendor}</td><td><code>{t.tool}</code></td><td>{t.description}</td><td>{t.inputs}</td><td>{t.outputs}</td></tr>
            ))}</tbody>
          </table></div>
          <p><strong>REST and library APIs</strong> — the same columns, kept apart because the API calls are not one-to-one with the MCP tools</p>
          <div className="scroll"><table>
            <thead><tr><th>#</th><th>Vendor</th><th>API or endpoint</th><th>Short description</th><th>REST inputs</th><th>REST outputs</th></tr></thead>
            <tbody>{data.restApis.map((t, i) => (
              <tr key={i}><td>{i + 1}</td><td>{t.vendor}</td><td><Inline>{t.api}</Inline></td><td>{t.description}</td><td>{t.inputs}</td><td>{t.outputs}</td></tr>
            ))}</tbody>
          </table></div>
          <p className="muted small">{data.toolsNote}</p>
        </>
      )}

      {tab === 'Databricks' && (
        <>
          <p><strong>What Databricks Marketplace lists</strong> — per its product page</p>
          <div className="scroll"><table>
            <thead><tr><th>#</th><th>Type</th><th>Note</th></tr></thead>
            <tbody>{data.dbx.types.map((t, i) => <tr key={t.type}><td>{i + 1}</td><td>{t.type}</td><td>{t.note}</td></tr>)}</tbody>
          </table></div>
          <p><strong>MCP servers named on Databricks' own blog posts: {data.dbx.mcp.length}</strong></p>
          <div className="scroll"><table>
            <thead><tr><th>#</th><th>Provider</th><th>Product</th><th>What it offers</th><th>Access method</th><th>Basis</th></tr></thead>
            <tbody>{data.dbx.mcp.map((m, i) => (
              <tr key={i}><td>{i + 1}</td><td>{m.provider}</td><td>{m.product}</td><td>{m.offers}</td><td>{m.access}</td><td>{m.basis}</td></tr>
            ))}</tbody>
          </table></div>
          <Links items={data.dbx.sources} />
          <p><strong>What I could not check</strong></p>
          <ul>{data.dbx.gaps.map((g) => <li key={g}>{g}</li>)}</ul>
        </>
      )}

      {tab === 'Details and sources' && (
        <>
          <p>One section per vendor: the details behind the table, and the pages each row was read from.</p>
          {data.details.map((d) => (
            <details className="variant" key={d.vendor}>
              <summary>{d.vendor}</summary>
              {d.facts.map((f) => <Field key={f.topic} name={f.topic} text={f.text} />)}
              {d.sources.length > 0 && <Links items={d.sources} />}
            </details>
          ))}
        </>
      )}

      {tab === 'For an agent' && (
        <>
          <p><strong>Which source answers which question</strong> — my reading of the table, not a claim by any vendor.</p>
          <div className="scroll"><table>
            <thead><tr><th>#</th><th>A question the agent asks</th><th>Sources that cover it</th></tr></thead>
            <tbody>{data.agentMap.map((a, i) => <tr key={i}><td>{i + 1}</td><td>{a.question}</td><td>{a.sources}</td></tr>)}</tbody>
          </table></div>
          <p><strong>What the vendors have in common</strong></p>
          <div className="scroll"><table>
            <thead><tr><th>#</th><th>Pattern</th><th>What the rows show</th></tr></thead>
            <tbody>{data.patterns.map((p, i) => <tr key={i}><td>{i + 1}</td><td>{p.pattern}</td><td>{p.text}</td></tr>)}</tbody>
          </table></div>
          <p><Inline>{data.nextStep}</Inline></p>
        </>
      )}

      {tab === 'Not checked' && (
        <>
          <p>Things I could not verify, so you can decide what to chase before building on this table:</p>
          <ul>{data.gaps.map((g) => <li key={g}>{g}</li>)}</ul>
        </>
      )}
    </>
  )
}
