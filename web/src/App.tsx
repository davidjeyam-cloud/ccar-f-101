import { NavLink, Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import Concepts from './pages/Concepts'
import Concept from './pages/Concept'
import Practice from './pages/Practice'
import Mock from './pages/Mock'
import Library from './pages/Library'
import Blueprint from './pages/library/Blueprint'
import ExamDay from './pages/library/ExamDay'
import McqSources from './pages/library/McqSources'
import Mcqs from './pages/library/Mcqs'
import Vendors from './pages/library/Vendors'
import Oracle from './pages/library/Oracle'
import LiveMcp from './pages/library/LiveMcp'
import HelloClaude from './pages/library/HelloClaude'
import Reading from './pages/library/Reading'
import ReadingTs13 from './pages/library/ReadingTs13'
import ReadingDoc from './pages/library/ReadingDoc'

const links = [
  { to: '/', label: 'Home', d: 'M3 11l9-8 9 8v10a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z' },
  { to: '/concepts', label: 'Concepts', d: 'M12 3l9 4.5-9 4.5-9-4.5zM3 12l9 4.5 9-4.5M3 16.5L12 21l9-4.5' },
  { to: '/practice', label: 'Practice', d: 'M9 11l3 3 8-8M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h9' },
  { to: '/library', label: 'Library', d: 'M4 19.5V5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2zM8 7h7M8 11h7' },
  { to: '/mock', label: 'Mock exam', d: 'M12 8v5l3 2M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z' },
]

export default function App() {
  return (
    <div className="shell">
      <nav className="nav" aria-label="Main">
        <div className="brand">CCAR-F <span>Workbench</span></div>
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.to === '/'} className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d={l.d} /></svg>
            <span>{l.label}</span>
          </NavLink>
        ))}
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/concepts" element={<Concepts />} />
          <Route path="/concepts/:slug" element={<Concept />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/mock" element={<Mock />} />
          <Route path="/library" element={<Library />} />
          <Route path="/library/blueprint" element={<Blueprint />} />
          <Route path="/library/exam-day" element={<ExamDay />} />
          <Route path="/library/mcq-sources" element={<McqSources />} />
          <Route path="/library/mcqs/:set" element={<Mcqs />} />
          <Route path="/library/vendors" element={<Vendors />} />
          <Route path="/library/oracle" element={<Oracle />} />
          <Route path="/library/live-mcp" element={<LiveMcp />} />
          <Route path="/library/hello-claude" element={<HelloClaude />} />
          <Route path="/library/reading" element={<Reading />} />
          <Route path="/library/reading/ts-1-3" element={<ReadingTs13 />} />
          <Route path="/library/reading/claude-api" element={<ReadingDoc name="reading-claude-api" docx="/reading/Claude_Messages_API_cheatsheet.docx" />} />
          <Route path="*" element={<p>Page not found.</p>} />
        </Routes>
      </main>
    </div>
  )
}
