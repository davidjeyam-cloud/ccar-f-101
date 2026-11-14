import type { Course, Question } from './data'

const shuffle = <T,>(a: T[]): T[] => {
  const b = [...a]
  for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]] }
  return b
}

/** Largest-remainder split of `items` by the domain weights (60 -> 16/11/12/12/9). */
export function quotas(weights: Record<string, number>, items: number): Record<number, number> {
  const raw = Object.entries(weights).map(([d, w]) => ({ d: +d, v: (items * w) / 100 }))
  const out: Record<number, number> = Object.fromEntries(raw.map((r) => [r.d, Math.floor(r.v)]))
  let left = items - Object.values(out).reduce((a, b) => a + b, 0)
  for (const r of [...raw].sort((a, b) => (b.v % 1) - (a.v % 1))) { if (left-- > 0) out[r.d]++ }
  return out
}

/** 4 of the 6 guide scenarios at random; domain quotas by weight; falls back to other scenarios only if a domain is short. */
export function draw(all: Question[], course: Course): { ids: string[]; scenarios: number[]; short: number[] } {
  const need = quotas(course.mock.weights, course.mock.items)
  const byDom = (scs: number[]) => {
    const o: Record<number, Question[]> = {}
    for (const d of Object.keys(need)) o[+d] = all.filter((q) => q.domain === +d && scs.includes(q.scenarios[0]))
    return o
  }
  let scs: number[] = [1, 2, 3, 4]
  for (let i = 0; i < 300; i++) {
    const t = shuffle([1, 2, 3, 4, 5, 6]).slice(0, 4).sort()
    const p = byDom(t)
    if (Object.keys(need).every((d) => p[+d].length >= need[+d])) { scs = t; break }
  }
  const pool = byDom(scs), picked: Question[] = [], short: number[] = []
  for (const d of Object.keys(need).map(Number)) {
    let have = shuffle(pool[d]).slice(0, need[d])
    if (have.length < need[d]) {
      short.push(d)
      const rest = all.filter((q) => q.domain === d && !have.includes(q))
      have = have.concat(shuffle(rest).slice(0, need[d] - have.length))
    }
    picked.push(...have)
  }
  return { ids: shuffle(picked).map((q) => q.id), scenarios: scs, short }
}

export type Result = {
  correct: number; total: number; pct: number; scaled: number
  byDomain: Record<number, { right: number; total: number }>; missed: string[]
}
/** Estimated scaled score: a straight line 100-1000. The guide gives the 720 pass mark, not the conversion. */
export function grade(qs: Question[], answers: Record<string, number>): Result {
  const byDomain: Result['byDomain'] = {}
  const missed: string[] = []
  let correct = 0
  for (const q of qs) {
    const d = (byDomain[q.domain] ??= { right: 0, total: 0 })
    d.total++
    if (answers[q.id] === q.ans) { correct++; d.right++ } else missed.push(q.id)
  }
  const pct = qs.length ? correct / qs.length : 0
  return { correct, total: qs.length, pct, scaled: Math.round(100 + 900 * pct), byDomain, missed }
}
