import { useState } from 'react'
import type { ConceptQuestion } from '../lib/concept'
import { Inline } from './Md'

/** One practice question with its own state: pick an option, then see the explanation. */
export default function QuestionCard({ q, n, scenarioName }: { q: ConceptQuestion; n: number; scenarioName?: string }) {
  const [picked, setPicked] = useState<number | null>(null)
  return (
    <article className="qcard">
      <div className="small muted">
        Question {n}{scenarioName ? ` · ${scenarioName}` : ''}{q.docs ? ' · 📘 docs-based (beyond the guide)' : ''}
      </div>
      <p className="stem"><Inline>{q.q}</Inline></p>
      <div className="opts" role="radiogroup" aria-label="Answers">
        {q.opts.map((o, i) => {
          const state = picked === null ? '' : i === q.ans ? ' right' : i === picked ? ' wrong' : ''
          return (
            <button key={i} role="radio" aria-checked={picked === i} className={'opt' + state}
              onClick={() => picked === null && setPicked(i)}>
              <b>{'ABCD'[i]}</b><span><Inline>{o}</Inline></span>
            </button>
          )
        })}
      </div>
      {picked !== null && (
        <div className="explain" role="status">
          <p><b>{picked === q.ans ? 'Correct.' : `Not quite — the answer is ${'ABCD'[q.ans]}.`}</b> <Inline>{q.explain}</Inline></p>
          {q.tests.length > 0 && <p className="small"><span className="exam-chip">⭐ What this tests</span> {q.tests.join(' · ')}</p>}
        </div>
      )}
    </article>
  )
}
