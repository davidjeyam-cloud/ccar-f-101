import { useParams, Link } from 'react-router-dom'
import { useState } from 'react'
import { useLibrary } from '../../lib/library'
import { store, save } from '../../lib/data'
import { Inline } from '../../components/Md'

type Evidence = { label: string; url: string; quote: string; guideOnly: boolean }
type MQ = {
  id: string; ts: string; tsRef: string; scenario: number; scenarioName: string; scenarios: number[]
  q: string; opts: string[]; ans: number; explain: string; points: string[]; basis: string
  evidence: Evidence[]; community: string; live: string
}
type MSet = { title: string; scope: string; count: number; questions: MQ[] }
type Mcqs = { checked_on: string; sets: Record<string, MSet> }

const L = 'ABCD'

function Card({ q, picked, onPick }: { q: MQ; picked: number | null; onPick: (i: number) => void }) {
  const real = q.evidence.filter((e) => !e.guideOnly)
  return (
    <div className="qcard">
      <p className="small">
        <b>{q.id}</b> · 📋 Scenario {q.scenario}: {q.scenarioName}
        {q.basis === 'docs' && <> · <span className="chip">📘 docs-based</span></>}
      </p>
      <p><Inline>{q.q}</Inline></p>
      <div className="opts">
        {q.opts.map((o, i) => {
          const cls = picked === null ? '' : i === q.ans ? ' right' : i === picked ? ' wrong' : ''
          return (
            <button key={i} className={'opt' + cls} disabled={picked !== null} onClick={() => onPick(i)}>
              <b>{L[i]}</b><span><Inline>{o}</Inline></span>
            </button>
          )
        })}
      </div>
      {picked !== null && (
        <>
          <div className="explain">
            <p>
              <b>{picked === q.ans ? 'Correct. ' : `Not quite. The best answer is ${L[q.ans]}. `}</b>
              <Inline>{q.explain}</Inline>
            </p>
          </div>
          <details className="variant">
            <summary>How this answer was checked</summary>
            {real.length > 0 ? (
              <p className="small"><b>Official wording</b> (word for word; checked on the date shown at the top)</p>
            ) : (
              <p className="small"><b>Exam guide only:</b> no official docs page covers this judgment, so the guide's task statement is the basis.</p>
            )}
            {real.map((e, i) => (
              <blockquote key={i}>
                <p>{e.quote}</p>
                <p className="small">— <a href={e.url} target="_blank" rel="noreferrer">{e.label}</a></p>
              </blockquote>
            ))}
            {q.live && <p><b>Seen on the real CLI.</b> <Inline>{q.live}</Inline></p>}
            {q.community && <p><b>Community cross-check</b> (study repositories, read for coverage only). <Inline>{q.community}</Inline></p>}
            <p className="small">
              <span className="exam-chip">⭐ What this tests</span>{' '}
              {q.points.join(' · ')}
            </p>
          </details>
        </>
      )}
    </div>
  )
}

export default function Mcqs() {
  const { set = '' } = useParams()
  const { data, error } = useLibrary<Mcqs>('mcqs')
  const key = `mcqs-${set}`
  const [picks, setPicks] = useState<Record<string, number>>(() => store<Record<string, number>>(key, {}))
  const [lastSet, setLastSet] = useState(set)
  if (lastSet !== set) { setLastSet(set); setPicks(store<Record<string, number>>(key, {})) }

  if (error) return <p className="err" role="alert">{error}</p>
  if (!data) return <p className="muted">Loading…</p>
  const s = data.sets[set]
  if (!s) {
    return (
      <>
        <h1>Evidence-backed MCQs</h1>
        <p className="warn">Unknown set "{set}". Choose one: {Object.keys(data.sets).map((k) => (
          <span key={k}><Link to={`/library/mcqs/${k}`}>{k}</Link>{' '}</span>
        ))}</p>
      </>
    )
  }
  const pick = (id: string, i: number) => {
    const next = { ...picks, [id]: i }
    setPicks(next); save(key, next)
  }
  const done = s.questions.filter((q) => picks[q.id] !== undefined)
  const right = done.filter((q) => picks[q.id] === q.ans).length
  let lastTs = ''
  return (
    <>
      <h1>10 · MCQs: {s.title}</h1>
      <p className="muted">
        ➕ Own section, not in the exam question bank · {s.count} original questions · answers checked against official pages on {data.checked_on} · not real exam questions
      </p>
      <p><b>Score: {right} / {done.length} answered</b> (of {s.count})</p>
      {done.length > 0 && (
        <button className="btn ghost" onClick={() => { setPicks({}); save(key, {}) }}>Reset answers</button>
      )}
      <details className="variant">
        <summary>How these questions were built and checked</summary>
        <ol>
          <li><b>Scope:</b> the official exam guide (task statements {s.scope}).</li>
          <li><b>Topics and traps:</b> the community study repositories collated on the Study sources page, read for what they test. Nothing is copied.</li>
          <li><b>Facts:</b> every correct answer has a word-for-word quote from an official page, shown under the answer.</li>
          <li><b>Back-test:</b> the Streamlit app's verifier downloaded those pages again and checked every quote, the answer positions and the option lengths. A corrupted quote was rejected.</li>
          <li><b>Live:</b> where the real Claude Code CLI could show the behaviour safely, it was run in an isolated config folder.</li>
        </ol>
        <p className="small">📘 = the behaviour comes from the official docs and goes beyond the guide's wording. Where the guide and the docs word something differently, the explanation says so.</p>
      </details>
      {s.questions.map((q) => {
        const head = set === 'd2' && q.ts !== lastTs ? (lastTs = q.ts, <h2 key={'h' + q.ts}>{q.tsRef}</h2>) : null
        return (
          <div key={q.id}>
            {head}
            <Card q={q} picked={picks[q.id] ?? null} onPick={(i) => pick(q.id, i)} />
          </div>
        )
      })}
    </>
  )
}
