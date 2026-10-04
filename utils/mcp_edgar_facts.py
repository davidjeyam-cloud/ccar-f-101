"""
Facts shown on the hosted MCP page (D2.3.1): what sec.gov exposes, and how one tool call turns into requests to it.

Every row says where it comes from, so nothing here rests on memory:
  📘 SEC       the SEC's own pages, read on READ_ON (SEC_SOURCES)
  📦 code      the source of the installed packages: sec-edgar-mcp 1.0.8 and edgartools 5.60.0
  👁 observed  seen in the MCP server's own request log, AAPL, on READ_ON — each tool called twice on a freshly
               started service (8 tools, 44 requests in all: every one a GET, to two hosts, answered 200, and none
               carried a query string)
The pseudo code is simplified from the code it names; comments marked "observed" are log lines, not code.
Re-run `ask` on the page and read the web rows of the steps table to check any row yourself.
"""

READ_ON = "2026-10-04"
VERSIONS = "sec-edgar-mcp 1.0.8 · edgartools 5.60.0"
SEC_SOURCES = (
    ("SEC — EDGAR Application Programming Interfaces", "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"),
    ("SEC — Developer resources and fair access", "https://www.sec.gov/about/developer-resources"),
)

# (host, path, what it returns, how I know, does this server use it?)
ENDPOINTS = (
    ("data.sec.gov", "/submissions/CIK##########.json",
     "One company: its details and its filing history (JSON). Long histories continue in extra files such as "
     "`CIK##########-submissions-001.json`", "📘 SEC · 👁 observed", "Yes — every company tool"),
    ("data.sec.gov", "/api/xbrl/companyfacts/CIK##########.json",
     "Every XBRL fact one company has ever reported, in one JSON file", "📘 SEC · 👁 observed",
     "Yes — `get_company_facts`, `get_key_metrics`"),
    ("data.sec.gov", "/api/xbrl/companyconcept/CIK##########/us-gaap/{concept}.json",
     "One company's values for one concept (for example `NetIncomeLoss`)", "📘 SEC", "Not seen in my runs"),
    ("data.sec.gov", "/api/xbrl/frames/us-gaap/{concept}/USD/{period}.json",
     "One concept across all companies for one period", "📘 SEC", "Not seen in my runs"),
    ("www.sec.gov", "/files/company_tickers_exchange.json",
     "The list of ticker, company name, CIK and exchange (JSON)", "👁 observed (not on the API page I read)",
     "Yes — turns a ticker into a CIK"),
    ("www.sec.gov", "/Archives/edgar/data/{cik}/{accession without dashes}/{accession}.txt",
     "One complete filing as a single text file, including its XBRL data", "👁 observed (not on the API page I read)",
     "Yes — `get_financials`, filings, insider tools"),
    ("www.sec.gov", "companyfacts.zip · submissions.zip",
     "Bulk downloads of the two data sets above, refreshed nightly", "📘 SEC", "Not used"),
)

# (rule, fact, source)
RULES = (
    ("API key or login", "None. The SEC page states: “These APIs do not require any authentication or API keys to access.”",
     "📘 SEC API page"),
    ("How often", "The SEC asks for no more than 10 requests per second per user. The library this server uses "
                  "throttles itself to 8 per second (`max_requests_per_second = 8`).",
     "📘 SEC developer page · 📦 edgar/httprequests.py"),
    ("Who is asking", "Each request carries a `User-Agent` header with the text of `SEC_EDGAR_USER_AGENT` "
                      "(`headers[\"User-Agent\"] = identity`). The SEC developer page says it does not allow automated "
                      "tools that identify themselves as unclassified bots.",
     "📦 edgar/httprequests.py · 📘 SEC developer page"),
    ("A query language", "None described. The SEC pages list RESTful JSON APIs, RSS feeds, index files, daily archives and "
                         "an HTTPS file system; no SQL or query interface is mentioned. In my 44 logged requests, none had a "
                         "query string (nothing after a `?`).",
     "📘 SEC developer page · 👁 observed"),
    ("From a web page", "`data.sec.gov` does not support CORS, so a browser page cannot call it directly. A program on a "
                        "server — like this MCP server — makes the call instead.",
     "📘 SEC API page"),
    ("What comes back", "The data APIs return JSON. A filing is a text file.", "📘 SEC API page · 👁 observed"),
)

# The four hops from a sentence to an SEC request.
HOPS = (
    ("1", "You type a question", "Plain English", "—"),
    ("2", "The agent sends the question and all the tools' names, descriptions and input schemas to Gemini",
     "HTTPS to Google (`generativelanguage.googleapis.com`)",
     "Gemini answers with a **function call**: a tool name plus arguments, as JSON. It is a choice of tool, not a query"),
    ("3", "The MCP client sends that call to the MCP server",
     "HTTP POST to `http://127.0.0.1:9870/mcp` — a JSON-RPC message with `method: tools/call`; it never leaves this machine",
     "`name` and `arguments`, copied from the function call"),
    ("4", "The tool runs. It is an ordinary Python function in the server process",
     "HTTPS GET to `data.sec.gov` and `www.sec.gov` — the only step that goes to the SEC",
     "It builds URLs from the CIK or accession number. Filtering and parsing happen in Python, on the JSON or text that came back"),
)

# One entry per tool shown in the explorer.
TOOLS = (
    {
        "tool": "get_cik_by_ticker",
        "question": "What is Apple's CIK?",
        "args": {"ticker": "AAPL"},
        "code": """def get_cik_by_ticker(ticker="AAPL"):                 # sec_edgar_mcp/utils/cache.py
    if ticker_cache is empty:                         # only the FIRST call in a server process
        GET https://www.sec.gov/files/company_tickers_exchange.json
            # a static JSON file: a list of [cik, name, ticker, exchange]
        ticker_cache = { ticker: cik  for each row in the file }
    cik = ticker_cache.get("AAPL")                    # a dictionary lookup in memory: no SEC call
    return {"success": True, "cik": zero_pad(cik, 10), "ticker": "AAPL"}""",
        "first": ("https://www.sec.gov/files/company_tickers_exchange.json",),
        "second": (),
        "note": "The second call made no request at all: the ticker list is kept in memory for the life of the server process.",
    },
    {
        "tool": "get_recent_filings",
        "question": "List the two most recent 10-K filings for Apple.",
        "args": {"identifier": "AAPL", "form_type": "10-K", "limit": 2},
        "code": """def get_recent_filings(identifier="AAPL", form_type="10-K", days=30, limit=2):
    company = get_company(identifier)                 # ticker -> CIK (see get_cik_by_ticker), then edgartools Company(cik)
    filings = company.get_filings(form="10-K")
        GET https://data.sec.gov/submissions/CIK0000320193.json
            # REST: the company's details and its recent filings, as JSON
        GET https://data.sec.gov/submissions/CIK0000320193-submissions-001.json
            # older filings; the first file names these extra files (edgartools entity/data.py)
        # "10-K only" is applied in Python on the downloaded list: no query string is sent
    rows = []
    for filing in filings:                            # newest first
        if len(rows) >= limit: break
        rows.append({accession_number, filing_date, form, company, cik, period_of_report})
        # observed: one more GET of  /Archives/edgar/data/320193/<accession>.txt  per filing returned
        # (why edgartools fetches that file was not checked)
    return {"success": True, "filings": rows, "count": len(rows)}""",
        "first": ("https://www.sec.gov/files/company_tickers_exchange.json",
                  "https://data.sec.gov/submissions/CIK0000320193.json",
                  "https://data.sec.gov/submissions/CIK0000320193-submissions-001.json",
                  "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/0000320193-25-000079.txt",
                  "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/0000320193-24-000123.txt"),
        "second": ("https://data.sec.gov/submissions/CIK0000320193.json",
                   "https://data.sec.gov/submissions/CIK0000320193-submissions-001.json",
                   "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/0000320193-25-000079.txt",
                   "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/0000320193-24-000123.txt"),
        "note": "The `days` argument is accepted but never used: in the code it appears only in the function's signature.",
    },
    {
        "tool": "get_financials",
        "question": "What was Apple's revenue and net income in its latest filing?",
        "args": {"identifier": "AAPL", "statement_type": "income"},
        "code": """def get_financials(identifier="AAPL", statement_type="income"):    # sec_edgar_mcp/tools/financial.py
    company = get_company(identifier)
    latest_10k = company.get_filings(form="10-K").latest()    # the two submissions files, as above
    latest_10q = company.get_filings(form="10-Q").latest()
    latest = whichever has the LATER filing_date              # so "latest" can be a quarterly 10-Q
    financials = Financials.extract(latest)
        GET https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/0000320193-26-000020.txt
            # the whole filing as one text file; it contains the XBRL data
            # (the folder name is the accession number without its dashes)
            # observed: this file was fetched twice
    income = financials.income_statement()                    # parsed from that XBRL, in Python
    return {"success": True, "statements": {"income_statement": income},
            "filing_reference": {accession_number, filing_date, form_type, sec_url}}""",
        "first": ("https://www.sec.gov/files/company_tickers_exchange.json",
                  "https://data.sec.gov/submissions/CIK0000320193.json",
                  "https://data.sec.gov/submissions/CIK0000320193-submissions-001.json",
                  "https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/0000320193-26-000020.txt",
                  "https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/0000320193-26-000020.txt"),
        "second": ("https://data.sec.gov/submissions/CIK0000320193.json",
                   "https://data.sec.gov/submissions/CIK0000320193-submissions-001.json",
                   "https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/0000320193-26-000020.txt",
                   "https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/0000320193-26-000020.txt"),
        "note": "No XBRL query was sent to the SEC: the numbers were read out of the filing text after it arrived.",
    },
    {
        "tool": "get_insider_transactions",
        "question": "Any insider transactions at Apple in the last 30 days?",
        "args": {"identifier": "AAPL", "days": 30, "limit": 3},
        "code": """def get_insider_transactions(identifier="AAPL", form_types=None, days=30, limit=3):   # tools/insider.py
    company = get_company(identifier)
    filings = company.get_filings(form=["3", "4", "5"])      # the same two submissions files; form filter in Python
    for filing in filings:                                   # newest first
        if count >= limit: break
        if filing_date is older than `days` days: continue   # the date check is Python too
        row = {filing_date, form_type, accession_number, url, sec_url}
        owner = filing.obj()                                 # edgartools reads the filing
            GET https://www.sec.gov/Archives/edgar/data/320193/<accession>.txt     # the Form 4 itself
            # observed: also GET https://data.sec.gov/submissions/CIK<another filer>.json
            # (a different CIK from Apple's; why it is fetched was not checked)
    return {"success": True, "transactions": rows, ...}""",
        "first": ("https://www.sec.gov/files/company_tickers_exchange.json",
                  "https://data.sec.gov/submissions/CIK0000320193.json",
                  "https://data.sec.gov/submissions/CIK0000320193-submissions-001.json",
                  "https://www.sec.gov/Archives/edgar/data/320193/<accession of a Form 4>.txt",
                  "https://data.sec.gov/submissions/CIK<another filer>.json",
                  "https://www.sec.gov/Archives/edgar/data/320193/<accession of a Form 4>.txt",
                  "https://data.sec.gov/submissions/CIK<another filer>.json",
                  "https://www.sec.gov/Archives/edgar/data/320193/<accession of a Form 4>.txt",
                  "https://data.sec.gov/submissions/CIK<another filer>.json"),
        "second": ("https://data.sec.gov/submissions/CIK0000320193.json",
                   "https://data.sec.gov/submissions/CIK0000320193-submissions-001.json",
                   "https://data.sec.gov/submissions/CIK<another filer>.json",
                   "https://data.sec.gov/submissions/CIK<another filer>.json",
                   "https://data.sec.gov/submissions/CIK<another filer>.json"),
        "note": "One Form 4 file and one more submissions file per filing: nine requests for three transactions.",
    },
    {
        "tool": "get_company_facts",
        "question": "Give me Apple's key figures from its company facts.",
        "args": {"identifier": "AAPL"},
        "code": """def get_company_facts(identifier="AAPL"):                 # tools/company.py
    company = get_company(identifier)
    facts = company.get_facts()
        GET https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json
            # REST: every XBRL fact the company has reported, as one JSON file
    metrics = {}
    if hasattr(facts, "data"):                            # <- the tool only looks inside facts.data
        for name in [Assets, Liabilities, StockholdersEquity, Revenues, NetIncomeLoss,
                     EarningsPerShareBasic, CashAndCashEquivalents, CommonStockSharesOutstanding]:
            if name in facts.data["us-gaap"]: metrics[name] = the latest value
    return {"success": True, "metrics": metrics, "has_facts": True}""",
        "first": ("https://www.sec.gov/files/company_tickers_exchange.json",
                  "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
                  "https://data.sec.gov/submissions/CIK0000320193.json"),
        "second": ("https://data.sec.gov/submissions/CIK0000320193.json",),
        "note": "This one returned `\"metrics\": {}` with `success: true` for Apple. The SEC file arrived (HTTP 200), but the "
                "installed edgartools returns an `EntityFacts` object that has no `.data` attribute, so the tool's loop never "
                "ran. An empty result that looks like success: the case the exam asks you to tell apart from a failure (TS 2.2).",
    },
)
