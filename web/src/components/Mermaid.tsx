import { useEffect, useId, useState } from 'react'

/** Draws a Mermaid diagram in the browser (mermaid, loaded only when one is on screen). If it cannot draw, the source is shown. */
export default function Mermaid({ source, label }: { source: string; label: string }) {
  const id = 'mmd' + useId().replace(/[^a-zA-Z0-9]/g, '')
  const [svg, setSvg] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  useEffect(() => {
    let live = true
    setSvg(null); setErr(null)
    import('mermaid')
      .then(async (m) => {
        m.default.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'neutral' })
        const out = await m.default.render(id, source)
        if (live) setSvg(out.svg)
      })
      .catch((e: Error) => { if (live) setErr(e.message) })
    return () => { live = false }
  }, [source, id])
  if (err) return <><p className="err" role="alert">Could not draw the diagram: {err}</p><pre><code>{source}</code></pre></>
  if (!svg) return <p className="muted small">Drawing diagram…</p>
  // The source comes from this project's own data files; mermaid sanitises its output (securityLevel strict).
  return (
    <>
      <div className="diagram" role="img" aria-label={label} dangerouslySetInnerHTML={{ __html: svg }} />
      <p className="small muted diagram-hint">Swipe sideways to see the whole diagram.</p>
    </>
  )
}
