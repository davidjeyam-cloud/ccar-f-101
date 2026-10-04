"""
sec-edgar (hosted stand-in) — the server behind page D2.3.1 (➕ extra — not on the CCAR-F exam).

It runs as its OWN service over Streamable HTTP; an MCP client reaches it by URL and never starts it:
    .venv\\Scripts\\python.exe mcp_servers\\edgar_hosted_server.py --host 127.0.0.1 --port 9870

What is whose:
- The 21 TOOLS are the community `sec-edgar-mcp` package's, registered unchanged (AGPL-3.0, not written
  or endorsed by the SEC; the SEC itself hosts no MCP server). They fetch from sec.gov.
- The RESOURCES and PROMPTS below were added by this workbench, so the hosted page can show every MCP
  server feature. The upstream package ships none.

    RESOURCES    the APPLICATION decides which to read and attach as context
        edgar://tickers            CSV: ticker, company, CIK, exchange for 40 large US-listed companies
        edgar://forms              CSV: what each common SEC form is
        edgar://company/{ticker}   a resource TEMPLATE: one row of the ticker list
    PROMPTS      the USER picks one — ready-made questions with blanks to fill in
        compare_companies · latest_filing · insider_activity

Why the ticker list matters (guide TS 2.4: a resource is a catalogue that saves exploratory tool calls):
in live runs the package's `search_companies` tool returned nothing for well-known names, so the model
fell back on tickers it remembered. With edgar://tickers attached, the name → ticker → CIK step is read
from data instead of guessed.

`data/tickers.csv` is the first 40 rows of https://www.sec.gov/files/company_tickers_exchange.json,
fetched on 2026-10-04. `data/sec_forms.csv` holds this workbench's own one-line descriptions.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from sec_edgar_mcp.server import register_tools          # needs SEC_EDGAR_USER_AGENT in the environment

DATA = Path(__file__).resolve().parent / "data"
TICKERS_AS_OF = "2026-10-04"


def build(host: str, port: int) -> FastMCP:
    mcp = FastMCP("sec-edgar (hosted stand-in)", host=host, port=port)
    register_tools(mcp)                                  # the community package's 21 tools, unchanged

    # ── resources ────────────────────────────────────────────────────────────
    @mcp.resource("edgar://tickers", name="tickers", title="Ticker list", mime_type="text/csv",
                  description="Ticker, company name, CIK and exchange for 40 large US-listed companies. Use it to turn "
                              f"a company name into a ticker or CIK without a search. From sec.gov, fetched {TICKERS_AS_OF}.")
    def tickers() -> str:
        return (DATA / "tickers.csv").read_text(encoding="utf-8")

    @mcp.resource("edgar://forms", name="forms", title="SEC form types", mime_type="text/csv",
                  description="What each common SEC form is (10-K, 10-Q, 8-K, 4 …) and how often it is filed. "
                              "Short descriptions written for this workbench.")
    def forms() -> str:
        return (DATA / "sec_forms.csv").read_text(encoding="utf-8")

    @mcp.resource("edgar://company/{ticker}", name="company", title="One company from the ticker list",
                  mime_type="application/json",
                  description="One row of the ticker list as JSON. Put the ticker in the URI, e.g. edgar://company/AAPL. "
                              "A resource TEMPLATE: one definition, many URIs.")
    def company(ticker: str) -> str:
        rows = csv.DictReader(io.StringIO((DATA / "tickers.csv").read_text(encoding="utf-8")))
        row = next((r for r in rows if r["ticker"].upper() == ticker.upper()), None)
        return json.dumps(row or {"ticker": ticker.upper(), "error": "not in the 40-company ticker list"}, indent=2)

    # ── prompts ──────────────────────────────────────────────────────────────
    @mcp.prompt(title="Compare companies", description="Compare one measure across several companies from their latest filings.")
    def compare_companies(tickers: str, measure: str = "revenue and net income") -> str:
        return (f"Compare the {measure} of {tickers} in their latest filings. Gather the same data for every company, "
                f"state the period and form type of each figure, and say plainly if the periods are not like-for-like.")

    @mcp.prompt(title="Latest filing", description="Find a company's most recent filing of one form type.")
    def latest_filing(ticker: str, form_type: str = "10-K") -> str:
        return (f"Find the most recent {form_type} filing for {ticker}. Give its filing date, the period it covers and "
                f"its accession number.")

    @mcp.prompt(title="Insider activity", description="Summarise recent insider transactions at a company.")
    def insider_activity(ticker: str, days: str = "90") -> str:
        return (f"Summarise insider transactions at {ticker} over the last {days} days: how many filings, their dates "
                f"and form types. Say so if the transaction details are not available.")

    return mcp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="sec-edgar tools + workbench resources and prompts, over Streamable HTTP")
    parser.add_argument("--host", default="127.0.0.1", help="address to listen on (keep it on loopback)")
    parser.add_argument("--port", type=int, default=9870)
    args = parser.parse_args()
    build(args.host, args.port).run(transport="streamable-http")
