import { useEffect, useState } from 'react'

/** Draws a Graphviz DOT graph in the browser (viz-js, WebAssembly, loaded only when a diagram is on screen). */
export default function Dot({ dot, label }: { dot: string; label: string }) {
  const [svg, setSvg] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  useEffect(() => {
    let live = true
    setSvg(null); setErr(null)
    import('@viz-js/viz')
      .then((m) => m.instance())
      .then((viz) => { if (live) setSvg(viz.renderString(dot, { format: 'svg' })) })
      .catch((e: Error) => { if (live) setErr(`Could not draw the diagram: ${e.message}`) })
    return () => { live = false }
  }, [dot])
  if (err) return <p className="err" role="alert">{err}</p>
  if (!svg) return <p className="muted small">Drawing diagram…</p>
  // The DOT comes from this project's own content modules, not from user input.
  return <div className="diagram" role="img" aria-label={label} dangerouslySetInnerHTML={{ __html: svg }} />
}
