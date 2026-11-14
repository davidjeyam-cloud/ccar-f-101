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
cd web
npm install                            # first time
npm run dev                            # http://localhost:5173
npm run build                          # type-check + production build to web/dist
npx vite preview --port 9100           # serve the build locally
```

Port 9000 stays with Streamlit.

## Deployed 2026-11-14: Cloudflare Worker with static assets

Live at https://ccar-f-web.ccar-f-web.workers.dev (checked: `/`, `/practice` and both data files return 200).

This is a Worker serving the built files, not a Pages project. Wrangler 4.162 auto-configured it when `wrangler pages project create` ran: it added `web/wrangler.jsonc` (single-page-app fallback), the `@cloudflare/vite-plugin` and `wrangler` dev dependencies, and `deploy` and `preview` scripts. The Cloudflare account is `davidjeyam@gmail.com`, logged in with `npx wrangler login`.

Redeploy after any change (from your PC, while logged in):

```powershell
cd web
npm run deploy                         # builds, then wrangler deploy
```

Since 2026-11-14 `push.ps1` runs `scripts\deploy_web.ps1` after every push (build, deploy, then a check that the live course.json matches), and Claude Code does the same after its own pushes. There is no GitHub-side auto-deploy. Connecting one is optional (dashboard, Workers & Pages, the Worker, Settings, Builds).

### Still to do by hand: lock it with Cloudflare Access (about 3 minutes)

The wrangler login cannot create Access rules, so this is a dashboard step. Until it is done the URL is public. The site holds only original questions: no guide text and no keys.

1. Cloudflare dashboard, Zero Trust. Choose the Free plan if asked (it asks for a team name).
2. Workers & Pages, the `ccar-f-web` Worker, Settings, Domains & Routes. Under `workers.dev`, turn on Cloudflare Access. This also covers the preview URLs.
3. Edit the policy it created: Allow, Include, Emails, `davidjeyam@gmail.com`. Login method: One-time PIN.
4. Open the link on your phone, enter the email, type the PIN from your inbox, then add the page to the home screen.

## What is in the React app, and what is not

In (2026-11-14): Home, the Concepts tab with the course map, a full page for every built concept (28 of them: summary and mental model, the gold "what the exam demands" box, flowchart and decision tree drawn in the browser, the code variants shown read-only with what each does when run, the distractor table, side-by-side, interactive practice questions, FAQ, docs and claim sources), Practice by task statement, and the timed Mock exam.

Not in (needs Python): the **Run** button of each code lab, and the agent playground's message boxes. Those stay in Streamlit. The only way to run them on the phone without a server would be Pyodide (Python in the browser); that is untested here. The 44 concepts that are not built (cross-cutting and out-of-scope stubs) are cards only. Next candidates: the error log and readiness gates, a Tool-Use Primer page.

The content is edited in place: `web/public/data/` (questions, course map, one JSON file per concept) is the source of truth, and the lab Python is in `web/pylab/`. The old exporters in `scripts/` are a frozen legacy bridge and refuse to run without `--overwrite-from-python`.

## Sources

- Cloudflare Pages limits (official changelog on the file limit): https://developers.cloudflare.com/changelog/post/2026-01-23-pages-file-limit-increase/index.md
- Cloudflare Pages free tier 2026 (third-party): https://temps.sh/blog/cloudflare-pages-free-tier-limits-2026
- Cloudflare Access product page: https://www.cloudflare.com/en-au/products/cloudflare-access
- Cloudflare Zero Trust for small business (Cloudflare blog): https://blog.cloudflare.com/zero-trust-week-setting-up-cloudflare-one-as-a-small-business/
- Hugging Face Spaces overview (official): https://huggingface.co/docs/hub/en/spaces-overview
- Hugging Face Spaces hardware (official): https://huggingface.co/docs/hub/main/spaces-gpus
- Hugging Face forum, CPU Basic restrictions (community): https://discuss.huggingface.co/t/official-community-complaint-revert-free-cpu-basic-spaces-and-remove-anti-developer-sdk-restrictions/177703
