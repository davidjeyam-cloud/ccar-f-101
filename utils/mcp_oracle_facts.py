"""
Facts and diagrams for page D2.3.4 — how a chat question becomes SQL on an Oracle database through MCP.
(➕ extra — not on the CCAR-F exam.)  Kept short on purpose: the diagrams carry the story.

One MAIN diagram (the whole path, kept simple) plus two small ZOOM diagrams that expand one part each.

Basis: 📘 = MCP documentation (modelcontextprotocol.io) · 🏛 = Oracle's own pages · 🧪 = my illustration (schema and SQL:
NOT from Oracle, NOT run — there is no Oracle database in this workbench) · ❓ = the pages did not say.
"""

READ_ON = "2026-10-08"

# ── MAIN diagram: top to bottom. Layers are boxes; solid arrows go down to the database, dotted arrows bring the answer up.
# The numbers match the step cards beside it on the page (CARDS below).
MERMAID = """flowchart TB
    subgraph L1["① YOU"]
        U["💬 Chat box"]
    end
    subgraph L2["② APP — the chat window and the LLM"]
        LLM["🧠 LLM<br/><b>writes the SQL</b><br/>(MCP does not)"]
    end
    subgraph L3["③ MCP CLIENT — a part of the app"]
        CL["🔌 MCP client<br/>speaks MCP to one server"]
    end
    subgraph L4["④ MCP SERVER — Oracle"]
        direction LR
        T["🛠 TOOLS — the model decides<br/><b>run-sql</b> runs a SQL statement<br/><b>connect</b> opens a connection<br/><b>list-connections</b> lists saved ones"]
        R["📄 RESOURCES* — the app decides<br/><b>schema notes</b>: tables + columns<br/><b>glossary</b>: spend = qty x price"]
        PR["✍️ PROMPTS* — the user decides<br/><b>top-customers</b>(year)<br/>a ready-made question"]
    end
    subgraph L5["⑤ ORACLE DATABASE"]
        DB[("🗄 Runs the SQL as one limited user<br/><b>CUSTOMERS ⟷ ORDERS ⟷ ORDER_ITEMS</b>")]
    end

    U -->|"1 question"| LLM
    LLM -->|"2 tool call + SQL"| CL
    CL -->|"3 tools/call (JSON-RPC)"| T
    T -->|"4 run the SQL"| DB
    DB -.->|"5 rows"| T
    T -.-> CL
    CL -.-> LLM
    LLM -.->|"6 answer in words"| U

    style L1 fill:#f4f8ff,stroke:#3b6fd4,stroke-width:2px
    style L2 fill:#fffaf0,stroke:#c98a00,stroke-width:2px
    style L3 fill:#fff4e0,stroke:#d9822b,stroke-width:2px
    style L4 fill:#f3fbf5,stroke:#2f9e57,stroke-width:2px
    style L5 fill:#fff5f5,stroke:#c0392b,stroke-width:2px
    classDef user fill:#e8f1ff,stroke:#3b6fd4,color:#12305e
    classDef app fill:#fff3d6,stroke:#c98a00,color:#5a3d00
    classDef client fill:#ffe9c7,stroke:#d9822b,color:#5a2f00
    classDef server fill:#e3f6e8,stroke:#2f9e57,color:#0e4a26
    classDef db fill:#fde8e8,stroke:#c0392b,color:#5e1510
    class U user
    class LLM app
    class CL client
    class T,R,PR server
    class DB db
"""

# ── The same run, as cards beside the diagram. All data is invented ("Customer A…"); nothing here was run.
# Basis: the chat, rows and answer are 🧪 illustration. The tools/call envelope is the MCP message shape 📘; the argument
# name "sql" is 🧪 my example because Oracle's page does not state run-sql's inputs.
CHAT_QUESTION = "Which 5 customers spent the most in 2025?"
ROWS = (
    ("Customer A", "48,210.00"),
    ("Customer B", "41,875.50"),
    ("Customer C", "39,002.25"),
    ("Customer D", "35,560.00"),
    ("Customer E", "31,944.80"),
)
ANSWER = ("Your top 5 customers by 2025 spend were Customer A (48,210.00), Customer B (41,875.50), "
          "Customer C (39,002.25), Customer D (35,560.00) and Customer E (31,944.80).")
WIRE_SQL_SHORT = "SELECT c.name, SUM(…) … FETCH FIRST 5 ROWS ONLY"

# ── ZOOM 1: to write a three-table join the LLM must know the table and column names. Three ways it can learn them.
ZOOM_SCHEMA = """\
flowchart TB
    subgraph W["Where do the table and column names come from?"]
        direction LR
        A["📄 <b>A resource</b><br/>the app attaches schema notes<br/>before the question<br/><i>📘 MCP docs name database<br/>schemas as a resource example</i>"]
        B["🛠 <b>A tool</b><br/>returns the schema<br/>when the LLM asks<br/><i>❓ Oracle's server: not stated</i>"]
        C["🔎 <b>A catalogue query</b><br/>LLM runs run-sql on<br/>USER_TAB_COLUMNS first<br/><i>🏛 the view exists<br/>🧪 using it this way is my example</i>"]
    end
    LLM["🧠 LLM now knows the tables<br/>and how they join"]
    SQL["writes: SELECT … FROM customers<br/>JOIN orders JOIN order_items …"]
    A --> LLM
    B --> LLM
    C --> LLM
    LLM --> SQL

    style W fill:#f3fbf5,stroke:#2f9e57,stroke-width:2px
    classDef src fill:#e3f6e8,stroke:#2f9e57,color:#0e4a26
    classDef host fill:#fff3d6,stroke:#c98a00,color:#5a3d00
    classDef out fill:#eeeeee,stroke:#777,color:#222
    class A,B,C src
    class LLM host
    class SQL out
"""

# ── ZOOM 2: one host, two servers. Server B (web search) is an invented second server, drawn dashed.
ZOOM_SERVERS = """\
flowchart TB
    LLM["🧠 LLM — shown the tools of BOTH servers<br/>and picks which to call"]
    subgraph H["MCP HOST — one client per server"]
        direction LR
        CA["🔌 client A"]
        CB["🔌 client B"]
    end
    subgraph SA["SERVER A — Oracle"]
        TA["🛠 run-sql · connect …"]
    end
    subgraph SB["SERVER B — web (example)"]
        TB["🛠 search"]
    end
    DB[("🗄 Oracle Database")]
    WEB[("🌐 public web")]
    LLM -->|"question needs the data"| CA
    LLM -->|"question needs the web"| CB
    CA --> TA --> DB
    CB --> TB --> WEB

    style H fill:#fffaf0,stroke:#c98a00,stroke-width:2px
    style SA fill:#f3fbf5,stroke:#2f9e57,stroke-width:2px
    style SB fill:#f1f5fb,stroke:#5b7db1,stroke-width:2px,stroke-dasharray:5 4
    classDef host fill:#fff3d6,stroke:#c98a00,color:#5a3d00
    classDef server fill:#e3f6e8,stroke:#2f9e57,color:#0e4a26
    classDef serverb fill:#e4ecf8,stroke:#5b7db1,color:#1d3557
    classDef db fill:#fde8e8,stroke:#c0392b,color:#5e1510
    class LLM,CA,CB host
    class TA server
    class TB serverb
    class DB,WEB db
"""

KEY_IDEA = ("MCP does not turn English into SQL. The **LLM** writes the SQL and passes it as a tool argument; "
            "the **MCP server** only carries it to the database and the rows back. The database user's privileges "
            "decide what the SQL may touch.")

TWO_SERVERS = ("A host can connect to several servers at once, one client each. The LLM is shown the tools of all of "
               "them and picks. 📘")

# 🧪 My example — never presented as Oracle output.
EXAMPLE_SQL = """\
SELECT c.name, SUM(oi.quantity * oi.unit_price) AS total_spent
FROM   customers c
JOIN   orders o       ON o.customer_id = c.id
JOIN   order_items oi ON oi.order_id   = o.id
WHERE  o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
GROUP  BY c.name
ORDER  BY total_spent DESC
FETCH FIRST 5 ROWS ONLY"""

ORACLE_LINE = ("Oracle's SQLcl MCP server lists 5 tools (`list-connections`, `connect`, `disconnect`, `run-sql`, "
               "`run-sqlcl`) and advises a least-privilege database user and no direct access to production. 🏛")
NOT_STATED = ("Not stated on the pages I read: the tools' inputs and outputs, the transport, any read-only or approval "
              "mode, and whether it offers resources or prompts. The * boxes show what an MCP server can offer, "
              "not what Oracle's does. The second server is an invented example.")
SOURCES = (
    ("Oracle: SQLcl MCP tools", "https://docs.oracle.com/en/database/oracle/sql-developer-command-line/25.3/sqcug/sqlcl-mcp-server-tools.html"),
    ("Oracle: using the SQLcl MCP server", "https://docs.oracle.com/en/database/oracle/sql-developer-command-line/25.2/sqcug/using-oracle-sqlcl-mcp-server.html"),
    ("Oracle: USER_TAB_COLUMNS", "https://docs.oracle.com/en/database/oracle/oracle-database/23/refrn/USER_TAB_COLUMNS.html"),
    ("MCP: understanding servers", "https://modelcontextprotocol.io/docs/learn/server-concepts"),
)
NEXT_STEPS = "failure paths (a SQL error coming back) · asking the user to approve a tool call"
