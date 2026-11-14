import { Link, useParams } from 'react-router-dom'
import Md, { Inline } from '../components/Md'
import Dot from '../components/Dot'
import QuestionCard from '../components/QuestionCard'
import { CLAIM_KIND, useConcept, type Distractor } from '../lib/concept'
import { useCourse } from '../lib/data'

const KIND: Record<string, string> = {
  exam: '⭐ EXAM TOPIC', extra: '➕ Extra — not on the exam', excluded: 'ℹ️ Awareness only', ungroundable: 'No docs basis',
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="csec"><h2>{title}</h2>{children}</section>
}

function Table({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="scroll">
      <table>
        <thead><tr>{headers.map((h) => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j}><Inline>{c}</Inline></td>)}</tr>)}</tbody>
      </table>
    </div>
  )
}

function Distractors({ rows }: { rows: Distractor[] }) {
  return (
    <div className="scroll">
      <table>
        <thead><tr><th>Tempting answer</th><th>Why it looks right</th><th>Why it fails</th><th>Do this instead</th><th>Source</th></tr></thead>
        <tbody>
          {rows.map((d) => (
            <tr key={d.name}>
              <td><b>{d.name}</b></td><td><Inline>{d.looks}</Inline></td><td><Inline>{d.fails}</Inline></td><td><Inline>{d.instead}</Inline></td>
              <td>{d.source ? <span className={d.exam ? 'exam-chip' : 'src-chip'}>{d.source}</span> : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Concept() {
  const { slug = '' } = useParams()
  const { data: c, error } = useConcept(slug)
  const { data: course } = useCourse()
  if (error) return <><p className="err" role="alert">{error}</p><p><Link to="/concepts">Back to Concepts</Link></p></>
  if (!c) return <p className="muted">Loading…</p>
  const scName = (n: number[]) => course?.scenarios.find((s) => s.n === n[0])
  return (
    <>
      <p className="small"><Link to="/concepts">← All concepts</Link></p>
      <div className="chips">
        {c.code && <span className="chip">{c.code}</span>}
        <span className={c.kind === 'exam' ? 'exam-chip' : 'chip'}>{KIND[c.kind] ?? c.kind}</span>
      </div>
      <h1>{c.title}</h1>
      {c.guide && <p className="muted small">{c.guide}</p>}

      <Section title="Summary"><Md>{c.tldr}</Md></Section>
      <div className="mental"><b>🧭 Mental model</b><p><Inline>{c.mentalModel}</Inline></p></div>

      {c.awareness && (
        <>
          <div className="gold-box"><b>⭐ What the exam says</b><Md>{c.examNote ?? ''}</Md></div>
          <Section title="What it is"><Md>{c.whatItIs}</Md></Section>
          <Section title="What is deliberately left out"><Md>{c.notExaminable ?? ''}</Md></Section>
        </>
      )}

      {!c.awareness && (
        <>
          {c.examPoints && c.examPoints.length > 0 && (
            <div className="gold-box">
              <b>⭐ What the exam demands</b>
              <p className="small muted">One row per guide bullet, paraphrased. The bullets are counted in order, because the guide doesn't number them.</p>
              <div className="scroll">
                <table>
                  <thead><tr><th>Guide reference</th><th>What the exam expects</th><th>Where this page exercises it</th></tr></thead>
                  <tbody>{c.examPoints.map((p, i) => <tr key={i}><td><span className="exam-chip">{p.ref}</span></td><td><Inline>{p.text}</Inline></td><td><Inline>{p.lab}</Inline></td></tr>)}</tbody>
                </table>
              </div>
            </div>
          )}
          <Section title="What it is"><Md>{c.whatItIs}</Md></Section>
          <Section title="How it works">
            <Md>{c.howItWorks ?? ''}</Md>
            {c.flowDot && <Dot dot={c.flowDot} label={`Flowchart of ${c.title}`} />}
          </Section>
          <Section title="Where you'll see it"><Md>{c.whereSeen ?? ''}</Md></Section>

          {c.variants && c.variants.length > 0 && (
            <Section title="The code lab, read-only">
              <p className="warn">The ▶ Run button needs Python, so it lives in the Streamlit app (localhost:9000). Here you can read each version of the code and what it does when run.</p>
              <Md>{c.labIntro ?? ''}</Md>
              {c.variants.map((v) => (
                <details key={v.key} className="variant">
                  <summary><span className={v.kind === 'correct' ? 'ok-dot' : 'bad-dot'} />{v.label}</summary>
                  {v.source && <p><span className={v.exam ? 'exam-chip' : 'src-chip'}>{v.source}</span></p>}
                  <pre><code>{v.code}</code></pre>
                  <p className="small muted">Scenario: {c.labScenarios?.find((s) => s.id === v.scenario)?.title ?? v.scenario}</p>
                  <p><b>What you see when it runs:</b> <Inline>{v.observe}</Inline></p>
                  <p><b>{v.kind === 'correct' ? 'Why it works:' : 'Why it fails:'}</b> <Inline>{v.why}</Inline></p>
                  {v.fix && <p><b>Do this instead:</b> <Inline>{v.fix}</Inline></p>}
                </details>
              ))}
            </Section>
          )}

          {c.playground && c.playground.length > 0 && (
            <Section title="Sub-concepts (the agent playground)">
              <Md>{c.playgroundIntro ?? ''}</Md>
              <p className="muted small">The interactive message boxes are in Streamlit; the picture to hold for each is here.</p>
              {c.playground.map((t) => (
                <details key={t.key} className="variant">
                  <summary>{t.label}</summary>
                  {t.exam && <p><span className="exam-chip">{t.exam}</span></p>}
                  <p><b>🧭</b> <Inline>{t.mentalModel}</Inline></p>
                  <p><Inline>{t.meaning}</Inline></p>
                  {t.tryThis.length > 0 && <ul>{t.tryThis.map((x, i) => <li key={i}><Inline>{x}</Inline></li>)}</ul>}
                  <p className="small muted">Grounded in: {t.docs}</p>
                </details>
              ))}
            </Section>
          )}
        </>
      )}

      {c.distractors.length > 0 && <Section title="Looks right, isn't"><Distractors rows={c.distractors} /></Section>}
      {c.sideBySide.rows.length > 0 && <Section title="Side by side"><Table headers={c.sideBySide.headers} rows={c.sideBySide.rows} /></Section>}
      {!c.awareness && c.decisionDot && <Section title="Decision tree"><Dot dot={c.decisionDot} label={`Decision tree for ${c.title}`} /></Section>}

      {c.questions.length > 0 && (
        <Section title="Practice">
          <p className="muted small">Original questions, not real exam questions.</p>
          {c.questions.map((q, i) => <QuestionCard key={i} q={q} n={i + 1} scenarioName={scName(q.scenarios)?.name} />)}
        </Section>
      )}

      {!c.awareness && c.experiments && c.experiments.length > 0 && (
        <Section title="Try this in the lab"><ul>{c.experiments.map((x, i) => <li key={i}><Inline>{x}</Inline></li>)}</ul></Section>
      )}
      {c.faq.length > 0 && (
        <Section title="FAQ">
          {c.faq.map((f) => <details key={f.q} className="variant"><summary><Inline>{f.q}</Inline></summary><p><Inline>{f.a}</Inline></p></details>)}
        </Section>
      )}
      {c.related.length > 0 && (
        <Section title="Related concepts">
          <ul>{c.related.map((r) => <li key={r.slug}>{r.built ? <Link to={`/concepts/${r.slug}`}>{r.title}</Link> : r.title}</li>)}</ul>
        </Section>
      )}

      <Section title="Where this page comes from">
        <p className="small muted">{c.guideNote}</p>
        <p className="small"><b>Official docs read</b> (verified {c.docsVerifiedOn}):</p>
        <ul className="small">{c.docsRefs.map((d) => <li key={d.url}><a href={d.url} target="_blank" rel="noreferrer">{d.title}</a></li>)}</ul>
        <details className="variant">
          <summary>Every claim and its source ({c.grounding.length})</summary>
          <div className="scroll">
            <table>
              <thead><tr><th>Claim</th><th>Source type</th><th>Where</th></tr></thead>
              <tbody>{c.grounding.map((g, i) => <tr key={i}><td><Inline>{g.text}</Inline></td><td>{CLAIM_KIND[g.kind] ?? g.kind}</td><td className="small">{g.ref}</td></tr>)}</tbody>
            </table>
          </div>
        </details>
      </Section>
    </>
  )
}
