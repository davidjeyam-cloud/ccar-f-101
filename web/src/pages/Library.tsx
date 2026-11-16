import { Link } from 'react-router-dom'

const CORE = [
  { to: '/library/blueprint', title: 'Exam Blueprint', text: 'Format, timing, scoring, policies and the out-of-scope list.' },
  { to: '/library/exam-day', title: 'Exam Day', text: 'Registration, ID, rules of conduct, retakes, plus a checklist.' },
  { to: '/library/reading', title: 'Reading: cheatsheets', text: 'TS 1.3 subagents and the Claude Messages API: read here or download (.docx, .pdf).' },
]
const EXTRA = [
  { to: '/library/mcqs/mcp', title: '10.1 MCQs: MCP', text: '10 questions, each backed by word-for-word official quotes.' },
  { to: '/library/mcqs/skills', title: '10.2 MCQs: Claude Skills', text: '10 questions with evidence.' },
  { to: '/library/mcqs/d2', title: '10.3 MCQs: Tool Design and MCP', text: '20 questions covering every Domain 2 bullet.' },
  { to: '/library/mcq-sources', title: '10.0 Study sources', text: 'The GitHub repos and websites collated, and what was found.' },
  { to: '/library/vendors', title: 'D2.3.3 Financial-data vendors', text: 'Who publishes an MCP server or API, and how to get access.' },
  { to: '/library/oracle', title: 'D2.3.4 Chat to SQL on Oracle', text: 'How MCP lets a chat question reach a database.' },
  { to: '/library/live-mcp', title: 'D2.3.1 and D2.3.2 Live MCP', text: 'Hosted vs local MCP servers (read-only write-up).' },
  { to: '/library/hello-claude', title: 'Hello Claude', text: 'The three keys and the first call (read-only write-up).' },
]

export default function Library() {
  return (
    <>
      <h1>Library</h1>
      <p className="lead">Reference pages and extras that are not concept labs. The first three are on the exam path; the rest are extras (not on the exam).</p>
      <h2>Exam path</h2>
      <div className="grid">
        {CORE.map((c) => <div className="card" key={c.to}><b><Link to={c.to}>{c.title}</Link></b><div className="small muted">{c.text}</div></div>)}
      </div>
      <h2>Extras (not on the exam)</h2>
      <div className="grid">
        {EXTRA.map((c) => <div className="card" key={c.to}><b><Link to={c.to}>{c.title}</Link></b><div className="small muted">{c.text}</div></div>)}
      </div>
    </>
  )
}
