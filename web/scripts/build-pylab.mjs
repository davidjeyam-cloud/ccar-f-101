// Packs web/pylab/** into public/pylab/utils.zip for Pyodide (runs automatically before `npm run build`).
import { zipSync } from 'fflate'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const src = path.join(root, 'pylab')
const out = path.join(root, 'public', 'pylab', 'utils.zip')
const files = {}
const walk = (dir) => {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) walk(p)
    else if (e.name.endsWith('.py')) files[path.relative(src, p).split(path.sep).join('/')] = new Uint8Array(fs.readFileSync(p))
  }
}
walk(src)
fs.mkdirSync(path.dirname(out), { recursive: true })
fs.writeFileSync(out, zipSync(files, { level: 6 }))
console.log(`pylab/utils.zip: ${Object.keys(files).length} modules, ${Math.round(fs.statSync(out).size / 1024)} KB`)
