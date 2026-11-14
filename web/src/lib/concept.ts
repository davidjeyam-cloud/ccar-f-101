import { useData } from './data'

export type Claim = { text: string; kind: string; ref: string }
export type Distractor = { name: string; looks: string; fails: string; instead: string; source: string; exam: boolean }
export type ConceptQuestion = {
  q: string; opts: string[]; ans: number; explain: string; scenarios: number[]; docs: boolean; tests: string[]
}
export type Variant = {
  key: string; label: string; kind: 'correct' | 'distractor'; code: string; scenario: string
  observe: string; why: string; fix: string; source: string; exam: boolean
}
export type PlayTab = {
  key: string; label: string; mentalModel: string; exam: string; meaning: string; docs: string
  examples: string[]; tryThis: string[]
}
export type ConceptPage = {
  slug: string; code: string | null; title: string; kind: string; domain: number | null; guide: string
  awareness: boolean
  tldr: string; mentalModel: string; whatItIs: string; guideNote: string
  docsRefs: { title: string; url: string }[]; docsVerifiedOn: string; grounding: Claim[]
  distractors: Distractor[]
  sideBySide: { headers: string[]; rows: string[][] }
  questions: ConceptQuestion[]
  faq: { q: string; a: string }[]
  related: { slug: string; title: string; built: boolean }[]
  // full pages only
  howItWorks?: string; whereSeen?: string
  examPoints?: { ref: string; text: string; lab: string }[]
  flowDot?: string; decisionDot?: string
  labIntro?: string; labScenarios?: { id: string; title: string; description: string }[]
  variants?: Variant[]; experiments?: string[]
  playgroundIntro?: string; playground?: PlayTab[]
  // awareness pages only
  examNote?: string; notExaminable?: string
}

export const useConcept = (slug: string) => useData<ConceptPage>(`concepts/${slug}.json`)

export const CLAIM_KIND: Record<string, string> = {
  docs: '📘 official docs', guide: '🎓 exam guide', recommendation: '💡 my recommendation', simulated: '🧪 simulated',
}
