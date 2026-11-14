# Lab Python (the browser runtime)

These files are the SOURCE of the code labs and agent playgrounds that run in the browser through Pyodide. They are a copy of the
`utils/` modules the labs need, taken on 2026-11-14 when the Streamlit app was frozen (see docs/SUNSET_STREAMLIT.md). From now on edit
them HERE, not in the repo-root `utils/`.

- `npm run build` packs this folder into `public/pylab/utils.zip` (`scripts/build-pylab.mjs`); `public/pylab/runner.py` runs one program.
- Standard library only. Do not add third-party imports: Pyodide would need them downloaded.
- Text that appears on the concept pages (summaries, exam points, questions) lives in `public/data/concepts/*.json`. The `concepts_content/*.py`
  files here are kept only because the labs call their check functions (`check_outcome`, `node_states`) and some import their constants.
