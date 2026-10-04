"""
Facts for page D2.3.3 — what financial-data vendors expose over MCP and APIs, what they sell, and how a client gets it.

Written for an investment-banking agent that would need several of these sources. Every row was read from the
vendor's own pages on READ_ON unless its BASIS says otherwise. Nothing is filled in from memory: what a page did not
say is written as "not stated", and what could not be read at all is written as such.

BASIS (shown on every row):
  ✅ read      the vendor's own page, fetched and read
  🔎 snippet   a search-result summary of the vendor's page; the page itself could not be fetched (blocked or script-built)
  📰 press     a vendor press release as republished on a news site; the vendor's own domain was blocked to my tools
  ❓ unknown   not found / not identified

No price appears anywhere: none of the pages read states one. No e-mail address is copied: each page names a sales contact.
"""

READ_ON = "2026-10-04"

BASIS = {
    "✅": "Read on the vendor's own page",
    "🔎": "From a search summary of the vendor's page; the page itself could not be fetched",
    "📰": "Vendor press release as republished on a news site; the vendor's own domain was blocked to my tools",
    "❓": "Not found, or not identified",
}

# Short cells for the "at a glance" table.
# (vendor, group, mcp, api, sells, access, basis)
GLANCE = (
    ("Crunchbase", "Private companies",
     "`https://mcp.crunchbase.com` · 14 tools: natural-language answers, structured search, entity profiles, saved lists",
     "REST `https://api.crunchbase.com/v4/data/` · JSON · API key in a header · 200 calls per minute",
     "Private-company data: company profiles, funding rounds, people, investors, acquisitions, plus predictions",
     "MCP: sign in with your Crunchbase account. MCP is bought per workspace and assigned to each user as a seat; ask Crunchbase sales. API: an API key",
     "✅"),
    ("ZoomInfo", "Contacts and accounts",
     "`https://mcp.zoominfo.com/mcp` · 6 tools: find, enrich and research accounts; find, enrich and research contacts",
     "REST groups Search, Enrich, Lookup, Usage · OAuth 2.0 · base URL not on the page I read",
     "B2B company and contact data: firmographics, technographics, funding, business signals, contact details",
     "A ZoomInfo licence (self-serve or enterprise); OAuth sign-in; plan limits and credits apply; a free trial is offered",
     "✅"),
    ("FactSet", "Market and deal data",
     "FactSet's own MCP server. Its article lists 8 content APIs behind it: Fundamentals, Estimates, Ownership, M&A, Pricing, People, Events, Supply Chain. Endpoint URL not verified",
     "REST content APIs on `developer.factset.com` (the catalogue page is script-built; I could not read it)",
     "Financial data and analytics: fundamentals, estimates, ownership, M&A, prices, events, supply chain",
     "Through a FactSet relationship; a search summary says an MCP trial is requested from FactSet",
     "🔎"),
    ("FactSet SharkRepellent", "Takeover defence and governance",
     "None found on the pages I read",
     "None found on the pages I read",
     "Takeover-defence and corporate-governance data on thousands of US companies: poison pills, charter and bylaw provisions, state takeover laws, a “Bullet Proof” defence rating",
     "Not stated on the page I read. It describes a software platform with custom reports and company defence profiles",
     "✅"),
    ("Moody's", "Credit ratings",
     "`https://api.moodys.com/genai-ready-data/m1/mcp` · 5 tools: find entity, get ratings, rating drivers, scorecard, search research",
     "“Smart APIs” are named on Moody's page; no endpoints are stated there",
     "Credit ratings and research; company data on more than 600 million entities",
     "Request credentials and the endpoint from Moody's; OAuth sign-in through a Moody's login page",
     "✅"),
    ("S&P Global Market Intelligence (Kensho)", "Financial data",
     "A remote MCP server for the Kensho LLM-ready API. URL not stated",
     "Kensho LLM-ready API (details not read). A search summary also names XpressAPI and Capital IQ API",
     "Capital IQ financials, market prices, segment financials, company intelligence, competitors, M&A transactions, earnings-call transcripts",
     "Ask Kensho for testing; in Claude, add the S&P Global connector and log in to your authorised account. Licence terms not stated",
     "✅"),
    ("S&P Global Ratings (RatingsDirect)", "Credit ratings",
     "None found",
     "Data feeds, cloud and API solutions, per a search summary of S&P's pages",
     "Credit ratings and research; a search summary gives 9,500 issuers and 79,000 securities",
     "A search summary says customers with an S&P Global Market Intelligence subscription register for access; RatingsDirect sits inside Capital IQ",
     "🔎"),
    ("Fitch (Fitch Solutions)", "Credit ratings",
     "A “Fitch Nexus” MCP connector. Endpoint not stated",
     "None found",
     "Credit research, current and historical ratings and outlooks, financials and forecasts, rating factors and sensitivities; CreditSights, BMI and Sustainable Fitch “coming”",
     "Licence terms not stated. The release says clients need “a one-time only connection”",
     "📰"),
    ("Bloomberg", "Market data and terminal",
     "Bloomberg Enterprise MCP, part of Data License Plus: more than 100 million securities and over 30,000 fields",
     "BLPAPI (C++, Java, .NET), Desktop API, Server API, B-PIPE; Data License over REST, SFTP, web services or cloud",
     "Reference, pricing, fundamentals, estimates, ESG, risk, regulation and historical data",
     "Data License: a self-service catalogue at `data.bloomberg.com`. Data License Plus: request a demo. Terminal and server APIs: a Bloomberg subscription (not detailed on the page)",
     "✅"),
    ("LSEG", "Market and deal data",
     "A managed MCP server: for Microsoft Copilot Studio, and in Databricks Marketplace (Financial Analytics, Lipper). Phased rollout. URL not stated",
     "LSEG Data Library (Python, TypeScript, .NET); Datastream Web Service",
     "Market data and analytics, Lipper funds, and Deals data: M&A, private equity, capital raising (4.4 million deals, since 1960)",
     "Through LSEG product licences. The Data Library needs an app key (plus login for a platform session, or the Workspace app running for a desktop session). Deals: Workspace, SDC, DBI or an SFTP feed",
     "✅"),
    ("DealInfo", "—",
     "Not identified",
     "Not identified",
     "Not identified: my searches found no company with this name",
     "—",
     "❓"),
    ("Contexa", "—",
     "Not identified",
     "Not identified",
     "Not identified as a financial-data vendor: my searches found a WooCommerce search plugin, a document-extraction API and an MCP developer platform with this name",
     "—",
     "❓"),
    ("SEC EDGAR (free, for comparison)", "Public filings",
     "No SEC MCP server found on the SEC pages I read. The community `sec-edgar-mcp` is used on page D2.3.1",
     "REST on `data.sec.gov` plus files on `www.sec.gov` · JSON · no key · 10 requests per second",
     "Public company filings and the XBRL facts in them",
     "Nothing to buy: send a User-Agent that identifies you",
     "✅"),
)

# Per-vendor detail: (vendor, [(topic, text), ...], [(label, url), ...])
DETAILS = (
    ("Crunchbase", (
        ("MCP tools (14 on its Tool Reference page)",
         "Expert: `cb_expert_query_answer`, `cb_expert_build_search`, `cb_expert_query_domain`, `cb_expert_resolve_entity`, `cb_expert_submit_feedback`. "
         "Structured: `cb_reference`, `cb_entity_autocomplete`, `cb_entity_get`, `cb_search_query`. "
         "Lists: `cb_list_query`, `cb_list_create`, `cb_list_add_entities`, `cb_list_get`. Utility: `cb_metering_get_state`"),
        ("Clients named", "Claude, ChatGPT, VS Code with GitHub Copilot, Perplexity, Mistral Vibe, and any client that implements the current MCP specification"),
        ("REST API", "Entity lookup, search and autocomplete families; example path `/entities/organizations/crunchbase`; HTTPS only; key as the `user_key` parameter or the `X-cb-user-key` header"),
        ("Product-page figures", "790 data fields per company; 15 million+ private-company predictions refreshed weekly (as stated on the product page)"),
    ), (("MCP overview", "https://data.crunchbase.com/docs/mcp-overview"),
        ("Getting started with MCP", "https://data.crunchbase.com/docs/getting-started-with-mcp"),
        ("Tool reference", "https://data.crunchbase.com/docs/tool-reference"),
        ("Using the API", "https://data.crunchbase.com/docs/using-the-api"),
        ("Crunchbase MCP product page", "https://about.crunchbase.com/products/crunchbase-mcp"))),
    ("ZoomInfo", (
        ("MCP", "OAuth 2.0 sign-in through a browser, with ZoomInfo credentials or company single sign-on. Clients named: Claude Code, OpenAI Codex, Cursor, VS Code Copilot, Claude, ChatGPT, Perplexity. "
                "The docs say model training should be turned off in the AI client"),
        ("REST groups", "Search: contacts, companies, intent, news, scoops. Enrich: contacts, companies, corporate hierarchy, intent, news, org charts, scoops, technologies, hashtags. Lookup. Usage"),
        ("Licence note", "Intent endpoints need “the Intent SKU” in your package"),
        ("Not found", "The REST base URL and the rate-limit numbers were not on the pages I fetched. The old API documentation is marked “Legacy”"),
    ), (("ZoomInfo MCP solution page", "https://www.zoominfo.com/solutions/zoominfo-mcp"),
        ("Connect to ZoomInfo MCP", "https://docs.gtm.ai/docs/connect-to-zoominfo-mcp"),
        ("API documentation", "https://docs.gtm.ai/"))),
    ("FactSet", (
        ("What FactSet itself says", "Its “Enterprise MCP” article lists “eight content APIs”: Fundamentals, Estimates, Ownership, M&A, Pricing (FGP), People, Events and Supply Chain. "
                                     "The same article discusses OAuth and scoped access for MCP in general; it does not describe FactSet's own enforcement"),
        ("Not verified", "The MCP endpoint URL appeared only in a third-party listing, so it is not shown. The developer-portal pages are script-built and returned only a title to my fetch. "
                         "A search summary mentions 24 tools and a trial by contacting FactSet; I could not confirm either on FactSet's page"),
    ), (("FactSet developer portal — MCP", "https://developer.factset.com/mcp"),
        ("FactSet Enterprise MCP, part 3 (security and governance)", "https://insight.factset.com/enterprise-mcp-part-3-security-and-governance"))),
    ("FactSet SharkRepellent", (
        ("What the page says", "“FactSet's corporate governance database, SharkRepellent, provides takeover defense and corporate governance data for thousands of US companies.” "
                               "It compiles board structure and shareholder-rights data from articles of incorporation, bylaws, state takeover laws and shareholder rights plans, tracks poison pills, and scores defences with a “Bullet Proof Rating System”"),
        ("Delivery", "Not stated. The page mentions custom reports and company defence profiles. A FactSet marketplace page for “FactSet Corporate Governance” returned only its title"),
        ("For an agent", "I found no MCP server or API for SharkRepellent on the pages I read, and none of FactSet's MCP content areas is governance data"),
    ), (("FactSet Insight — SharkRepellent", "https://insight.factset.com/takeover-defense-and-corporate-governance-data-is-available-through-factsets-sharkrepellent-database"),)),
    ("Moody's", (
        ("MCP tools (5)", "`findEntity`, `searchEntityDocuments`, `getEntityRatings`, `getEntityRatingDrivers`, `getEntityScorecard`"),
        ("Access", "“Request credentials and endpoint URL from Moody's”; OAuth through a Moody's login page. Works with any LLM that supports the MCP standard, including Claude and OpenAI APIs"),
        ("Pathways", "Moody's names three: “Smart APIs”, MCP servers, and integrations through Databricks Marketplace and Claude for Financial Services"),
        ("Scale stated", "600 million entities and 2 billion ownership links (Moody's press release); 600 million+ public and private entities (Moody's blog)"),
    ), (("Moody's — Model Context Protocol", "https://www.moodys.com/web/en/us/genai/model-context-protocol.html"),
        ("Moody's — GenAI-ready data pathways", "https://www.moodys.com/web/en/us/creditview/blog/gen-ai-ready-data-powered-for-adoption.html"),
        ("Moody's press release — Claude", "https://www.moodys.com/web/en/us/media-relations/press-releases/moodys-brings-credit-and-compliance-workflows-directly-into-anthropics-claude.html"))),
    ("S&P Global Market Intelligence (Kensho)", (
        ("Datasets named", "Financial statements and line items; market prices and price charts; segment financials, market capitalisation, total enterprise value; company intelligence; competitors; M&A transactions; earnings-call transcripts. "
                           "Private-company financials were “coming soon” and Capital IQ consensus estimates “in development” when the post was written"),
        ("Built by", "Kensho, S&P Global's AI hub, for the Kensho LLM-ready API. S&P's press release says it works with any large language model"),
        ("Not found", "The MCP endpoint URL, the tool names and the licence terms. S&P's own “AI for partners and developers” page returned an access error"),
    ), (("S&P Global and Anthropic press release", "https://press.spglobal.com/2025-07-15-S-P-Global-and-Anthropic-Announce-Integration-of-S-P-Globals-Trusted-Financial-Data-into-Claude"),
        ("Kensho — LLM-ready API and MCP server access", "https://kensho.com/news/kensho-llm-ready-api-expands-mcp-server-access-dataset-support-integrations"))),
    ("S&P Global Ratings (RatingsDirect)", (
        ("What I have", "Only search summaries of S&P's pages: RatingsDirect covers credit ratings and research, is integrated into the Capital IQ platform, and S&P offers data feeds, cloud and API solutions (XpressAPI, Capital IQ API)"),
        ("Not found", "RatingsDirect and the S&P marketplace pages returned access errors or only a title when fetched, so no endpoint, protocol or licence detail is shown"),
    ), (("RatingsDirect", "https://www.spglobal.com/marketintelligence/en/solutions/ratingsdirect"),
        ("S&P Global Marketplace — API solutions", "https://www.marketplace.spglobal.com/en/solutions/api-solutions-(61953ac7-ea64-4fac-926a-feb7f846c2be)"))),
    ("Fitch (Fitch Solutions)", (
        ("What the release says", "Fitch Nexus gives access to Fitch Ratings credit research, current and historical ratings, outlooks and watch changes, company financials, forecasts and key ratios, and rating factors and sensitivities. "
                                  "CreditSights insights are “available soon”; BMI and Sustainable Fitch follow “in the following months”. It is described as built for “enterprise and regulated environments”"),
        ("Why 📰", "Fitch's own domains (fitchratings.com, fitchsolutions.com) were blocked to my tools, and the business-wire copy returned an access error. This row rests on a republished press release"),
        ("Not found", "Endpoint, tool names, API and licence terms"),
    ), (("Fitch Nexus MCP — press release as republished", "https://ffnews.com/newsarticle/fitch-solutions-launches-fitch-nexus-mcp-to-deliver-greater-speed-to-credit-insights/"),)),
    ("Bloomberg", (
        ("APIs on its API library page", "BLPAPI (core API: C++, Java, C#/.NET), Desktop API (for terminal users), Server API and B-PIPE (server-side data feed), Data License"),
        ("Data License", "“100B+ data points published daily”, “100M+ financial instruments”, “47k+ data fields”, “8k+ datasets”: reference, ESG, pricing, risk, regulation, fundamentals, estimates, historical. Delivered by REST API, SFTP, web services or cloud. A self-service portal lets clients browse, test and customise datasets"),
        ("Data License Plus and Enterprise MCP", "Adds cloud data sharing, Bloomberg Enterprise MCP and the Qube Datastore with Python access. The MCP covers “more than 100 million securities and over 30,000 fields”, structured by issuer, portfolio and hierarchy. How agents authenticate is not stated on that page"),
        ("Note", "The two pages give different field counts (47k+ for Data License, 30,000+ for the MCP). I did not check why"),
    ), (("Bloomberg — API library", "https://professional.bloomberg.com/support/api-library/"),
        ("Bloomberg — Data License", "https://professional.bloomberg.com/products/data/data-license/"),
        ("Bloomberg — Data License Plus", "https://professional.bloomberg.com/products/data/data-license/dl-plus/"))),
    ("LSEG", (
        ("MCP", "A managed MCP server announced with Microsoft, to connect Copilot Studio to LSEG APIs; and a first phase in Databricks Marketplace through Agent Bricks and Delta Sharing: LSEG Financial Analytics, Lipper Fund Data and Analytics, Historical Analytics. "
                "“AI-ready content will continue to roll out in phases through MCP”"),
        ("APIs", "LSEG Data Library (Python, TypeScript, .NET): a desktop session needs the Workspace or Eikon app running locally plus an app key; a platform session needs an app key and user credentials. Datastream Web Service for time-series data. Eikon Data API is described as “very unlikely” to be needed"),
        ("Deals data", "“M&A, private equity, capital raising, infrastructure, company events”; 4.4 million+ deals, 1.5 million+ M&A transactions, back to 1960. Desktop access through Workspace, SDC and DBI; an SFTP feed per dataset; the LSEG data catalogue"),
    ), (("LSEG and Microsoft — MCP", "https://www.lseg.com/en/media-centre/press-releases/2025/lseg-and-microsoft-transform-access-to-ai-ready-financial-data-in-customer-workflows"),
        ("LSEG MCP in Databricks Marketplace", "https://www.lseg.com/en/solutions/ai-finance-solutions/updates/lseg-launches-mcp-server-databricks-marketplace-ai-ready-access"),
        ("LSEG APIs summary", "https://developers.lseg.com/en/article-catalog/article/summary-of-common-lseg-apis"),
        ("LSEG Deals data", "https://www.lseg.com/en/data-catalogue/deals"))),
    ("DealInfo and Contexa", (
        ("What I found", "No vendor called “DealInfo”. “Contexa” matched three unrelated things: a WooCommerce search product (contexa.co), a document-extraction API (contexa.works) and an MCP developer platform (contexaai.com). None is a financial-data vendor, so I did not guess"),
        ("Needed from you", "The exact vendor names or websites"),
    ), ()),
)

# What an investment-banking agent asks, and which sources above cover it. This is MY reading of the facts, not a vendor claim.
AGENT_MAP = (
    ("Public-company filings and reported financials", "SEC EDGAR (free) · FactSet Fundamentals · S&P Capital IQ financials (Kensho) · Bloomberg Data License (fundamentals)"),
    ("Private companies, funding rounds, investors", "Crunchbase"),
    ("Who to contact at a company", "ZoomInfo"),
    ("Credit ratings, outlooks, rating drivers", "Moody's (MCP) · Fitch Nexus (MCP) · S&P Global Ratings (no MCP found)"),
    ("M&A deals and comparables", "LSEG Deals · FactSet M&A · S&P (M&A transactions, Kensho) · Crunchbase (acquisitions of private companies)"),
    ("Takeover defences and activism", "FactSet SharkRepellent. No MCP or API found for it"),
    ("Prices and estimates", "FactSet · Bloomberg · S&P (market prices; Capital IQ consensus estimates were “in development”)"),
    ("Ownership, events, transcripts, supply chain", "FactSet (ownership, events, supply chain) · S&P (earnings-call transcripts)"),
    ("Macro and time-series data", "LSEG Datastream Web Service"),
)

# What the vendors have in common, from the rows above.
PATTERNS = (
    ("The user signs in", "Crunchbase, ZoomInfo, Moody's and S&P/Kensho all have the person sign in with their own vendor account (OAuth or a vendor login)"),
    ("An account or licence comes first", "Crunchbase needs an MCP seat, ZoomInfo a licence (a trial is offered), Moody's credentials issued by Moody's, LSEG an LSEG product licence, and Bloomberg Data License Plus is requested through a demo form"),
    ("An API usually exists beside the MCP", "Crunchbase, ZoomInfo, Bloomberg and LSEG each also publish REST or library APIs. For Moody's and S&P Kensho the page names APIs but gives no endpoints"),
    ("Not every dataset is reachable by an agent", "SharkRepellent, S&P ratings and Fitch have no endpoint on the pages I could read"),
    ("No prices are published", "None of the pages read states a price; every vendor sends you to sales or a demo"),
)

# Things I could not check.
GAPS = (
    "Fitch's own domains and the business-wire copy of its release were blocked to my tools; the Fitch row rests on a republished press release.",
    "S&P Global's RatingsDirect, its marketplace API page and its “AI for partners and developers” page returned access errors or only a title.",
    "FactSet's developer-portal pages are script-built and returned only a title; the MCP endpoint and tool count are unconfirmed.",
    "ZoomInfo's REST base URL and rate-limit numbers were not on the pages I fetched.",
    "No page states a price, a contract term or a licence tier for any vendor.",
    "“DealInfo” and “Contexa” could not be identified as financial-data vendors.",
    "Vendor pages change. Re-read a vendor's page before building on a row.",
)
