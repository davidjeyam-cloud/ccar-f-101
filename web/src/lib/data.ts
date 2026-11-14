import { useEffect, useState } from 'react'

export type Question = {
  id: string; ts: string; domain: number; scenarios: number[]
  q: string; opts: string[]; ans: number; explain: string
  tests: string[]; bullets: string[]; principle: string; level: string; docs: boolean
}
export type TaskStatement = {
  ts: string; title: string; domain: number; pages: string
  labs: string[]; pending: string[]; questions: number
}
export type Concept = {
  slug: string; code: string | null; title: string; domain: number | null
  kind: 'exam' | 'extra' | 'ungroundable' | 'excluded'; status: string; built: boolean; guide: string
}
export type Course = {
  domains: { n: number; name: string; weight: string }[]
  taskStatements: TaskStatement[]
  scenarios: { n: number; name: string }[]
  concepts: Concept[]
  mock: { items: number; minutes: number; weights: Record<string, number>; passScaled: number; scaleNote: string }
}

const cache = new Map<string, Promise<unknown>>()
function load<T>(name: string): Promise<T> {
  if (!cache.has(name)) {
    cache.set(name, fetch(`/data/${name}`).then((r) => {
      if (!r.ok) throw new Error(`Could not load ${name} (HTTP ${r.status})`)
      return r.json()
    }))
  }
  return cache.get(name) as Promise<T>
}

/** Loads a static JSON file; the error is returned so the page can show it, never swallowed. */
export function useData<T>(name: string): { data: T | null; error: string | null } {
  const [state, setState] = useState<{ data: T | null; error: string | null }>({ data: null, error: null })
  useEffect(() => {
    let live = true
    load<T>(name).then((d) => live && setState({ data: d, error: null }),
      (e: Error) => live && setState({ data: null, error: e.message }))
    return () => { live = false }
  }, [name])
  return state
}
export const useCourse = () => useData<Course>('course.json')
export const useBank = () => useData<{ questions: Question[] }>('bank.json')

/** Per-device progress. Cleared if the browser data is cleared, so the page works without it. */
export function store<T>(key: string, fallback: T): T {
  try { const v = localStorage.getItem('ccarf:' + key); return v ? (JSON.parse(v) as T) : fallback } catch { return fallback }
}
export function save(key: string, value: unknown): void {
  try { localStorage.setItem('ccarf:' + key, JSON.stringify(value)) } catch { /* private mode: progress just is not kept */ }
}
