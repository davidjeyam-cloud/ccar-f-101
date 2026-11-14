# Hosting the React app (web/) for free, private, phone-friendly

Checked 2026-11-14 by web search. Several figures come from third-party sites, so confirm them on the provider pages before relying on them. Sources are listed at the end.

## What was found

| # | Item | Finding | Confidence |
|---|---|---|---|
| 1 | Cloudflare Pages, static hosting | Free; static assets free and unlimited; 500 builds per month; 20,000 files per site | Builds figure is third-party (the official limits page did not render in the search) |
| 2 | Cloudflare Access, free plan | Free for teams under 50 users; sign-in by email one-time PIN or an identity provider | Cloudflare pricing page, consistent across sources |
| 3 | Pages Functions | Billed as Workers; free cap about 100,000 requests per day | Third-party; CPU limit reported as 10 ms or 30 ms, so check |
| 4 | Hugging Face Spaces, Static | Free for everyone | Official Hub docs |
| 5 | Hugging Face Spaces, Docker | The Hub docs say Docker and Gradio Spaces need a paid plan to create (PRO or Team) | Official docs; forum posts in 2026 say free CPU access has also been tightened |
| 6 | Hugging Face free CPU Basic | 2 vCPU, 16 GB, sleeps after 48 hours idle; private Spaces return 404 to others | Official docs |

An earlier suggestion in this project (a free Python backend on Hugging Face) does not hold up: item 5 says Docker needs a paid plan. Treat Hugging Face as optional.

## Plan

| # | Part of the app | Where it runs | Cost |
|---|---|---|---|
| 1 | React front end, question bank, course map, practice, timed mock | Cloudflare Pages, as static files plus JSON | Free |
| 2 | Private access from your phone | Cloudflare Access in front of the Pages site (one-time PIN to your email) | Free |
| 3 | Progress and mock history | The browser's localStorage, per device | Free |
| 4 | Gemini demos, live MCP pages, runnable code labs | Stay in the Streamlit app for now (local, or Streamlit Cloud) | Free |
| 5 | Optional later: a small API for the demos | Cloudflare Workers free tier, or a paid Hugging Face Docker Space | Free / paid |

The mock grades in the browser, so a sleeping backend can never interrupt a 120-minute exam.

## Local commands

```powershell
python scripts/export_web_data.py      # regenerate web/public/data/*.json from the Python sources
cd web
npm install                            # first time
npm run dev                            # http://localhost:5173
npm run build                          # type-check + production build to web/dist
npx vite preview --port 9100           # serve the build locally
```

Port 9000 stays with Streamlit.

## Deploy to Cloudflare Pages (you do these steps; they need your login)

Connecting the GitHub repo gives the same behaviour as Streamlit Cloud: a push to `master` redeploys.

1. Cloudflare dashboard, Workers & Pages, Create, Pages, Connect to Git, pick `ccar-f-101`.
2. Build settings: framework Vite; build command `cd web && npm ci && npm run build`; output directory `web/dist`; root directory empty.
3. Deploy once. You get `https://<project>.pages.dev`.
4. Before sharing the link, protect it: Zero Trust, Access, Applications, Add an application, Self-hosted. Add the domain `<project>.pages.dev` and also `*.<project>.pages.dev` so preview deployments are covered. Policy: Allow, emails equal to your own address. Login method: One-time PIN.
5. Open the link on your phone, enter your email, type the PIN. Add it to the home screen.

Until step 4 is done the site is public. It contains only original questions, no guide text and no keys, but do not skip the step.

## What is not in the React app yet

The runnable code labs, the Agent playground, the live MCP pages and the Gemini demos. Those need Python, so they remain in Streamlit. Next candidates for the React app: concept summary pages as static content, the error log and readiness gates.

## Sources

- Cloudflare Pages limits (official changelog on the file limit): https://developers.cloudflare.com/changelog/post/2026-01-23-pages-file-limit-increase/index.md
- Cloudflare Pages free tier 2026 (third-party): https://temps.sh/blog/cloudflare-pages-free-tier-limits-2026
- Cloudflare Access product page: https://www.cloudflare.com/en-au/products/cloudflare-access
- Cloudflare Zero Trust for small business (Cloudflare blog): https://blog.cloudflare.com/zero-trust-week-setting-up-cloudflare-one-as-a-small-business/
- Hugging Face Spaces overview (official): https://huggingface.co/docs/hub/en/spaces-overview
- Hugging Face Spaces hardware (official): https://huggingface.co/docs/hub/main/spaces-gpus
- Hugging Face forum, CPU Basic restrictions (community): https://discuss.huggingface.co/t/official-community-complaint-revert-free-cpu-basic-spaces-and-remove-anti-developer-sdk-restrictions/177703
