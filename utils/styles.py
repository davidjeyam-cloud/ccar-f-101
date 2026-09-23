"""
Shared design tokens and theme utilities.
apply_theme() is called from app.py before pg.run() — applies to every page.
Base theme is controlled by .streamlit/config.toml (light, #F5F7FA background).

Mirrors agents101's utils/styles.py so the two apps look related.

NOTE: claude_key_banner() is NOT defined here yet. Per CLAUDE.md's
"Claude API Key Reminder Standard", it is added when the first 🔑 page
(1.1 Agentic loops) is built, together with the `anthropic` SDK dependency.
"""

import streamlit as st

# ── Brand colour tokens (identical to agents101) ────────────────────────────────
C = {
    "bg":         "#F5F7FA",   # page background (matches config.toml)
    "bg_surface": "#FFFFFF",   # card / panel surface
    "bg_overlay": "#EDF2F7",   # sidebar / secondary surface
    "border":     "#CBD5E0",   # standard border
    "border_sub": "#E2E8F0",   # subtle border
    "text_prim":  "#1A202C",   # primary text
    "text_sec":   "#2D3748",   # secondary text
    "text_muted": "#718096",   # muted / caption text
    "green":      "#059669",   # success / complete
    "blue":       "#0066CC",   # primary action
    "purple":     "#6B46C1",   # accent
    "orange":     "#D97706",   # warning / in-progress
    "red":        "#DC2626",   # error / danger
}

# Accessible chart palette — distinct, colourblind-safe, readable on white
CHART_COLORS = ["#0066CC", "#059669", "#D97706", "#6B46C1", "#DC2626",
                "#0891B2", "#65A30D", "#EA580C"]

# Phase-status accent colours used in phase_header()
ACCENT_COMPLETE = "#059669"   # green-600  — fully built page
ACCENT_CURRENT  = "#D97706"   # amber-600  — page in progress
ACCENT_COMING   = "#9CA3AF"   # gray-400   — not yet started

# ── Minimal global CSS (config.toml handles the base theme) ────────────────────
_GLOBAL_CSS = """
<style>
/* Sidebar */
section[data-testid="stSidebar"] { background-color: #EDF2F7 !important; }
section[data-testid="stSidebar"] * { color: #2D3748 !important; }
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {
    border-color: #CBD5E0 !important;
}
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] a { color: #2D3748 !important; }

/* Notification boxes — let Streamlit control their own text colour */
[data-testid="stNotification"] p { color: inherit !important; }

/* Active tab indicator */
button[data-baseweb="tab"][aria-selected="true"] {
    color: #0066CC !important;
    border-bottom: 2px solid #0066CC !important;
}

/* Typography scale */
.stApp h1 { font-size: 2rem    !important; font-weight: 800 !important; line-height: 1.25 !important; }
.stApp h2 { font-size: 1.5rem  !important; font-weight: 700 !important; line-height: 1.3  !important; }
.stApp h3 { font-size: 1.25rem !important; font-weight: 600 !important; line-height: 1.4  !important; }
.stApp h4 { font-size: 1.1rem  !important; font-weight: 600 !important; }
.stMarkdown p,
[data-testid="stMarkdownContainer"] p { line-height: 1.65 !important; }
[data-testid="stCaptionContainer"] p { font-size: 0.875rem !important; line-height: 1.5 !important; }
.stCodeBlock code { font-size: 0.875rem !important; }
</style>
"""


def apply_theme() -> None:
    """Inject minimal CSS that complements the light base theme in config.toml.
    Called once from app.py before pg.run()."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


# ── Shared dashboard chrome (cards, tables, stat tiles) ─────────────────────────
# Used by Phase 0's dashboard-style pages (Home, Exam Blueprint, Study Plan, ...) -
# pages that present information rather than teach+demo a task statement, so they
# skip the Page Structure Standard. Call apply_dashboard_css() once per such page,
# after apply_theme() has already run globally from app.py.
DASHBOARD_CSS = f"""
<style>
.wb-card {{
    background:{C['bg_surface']}; border:1px solid {C['border_sub']}; border-radius:12px;
    padding:20px 24px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,0.06);
}}
.wb-card h4 {{ margin-top:0; }}
.wb-cite {{ color:{C['text_muted']}; font-size:0.75rem; font-style:italic; }}
.wb-table {{ width:100%; border-collapse:collapse; }}
.wb-table th {{
    text-align:left; font-size:0.72rem; letter-spacing:1px; text-transform:uppercase;
    color:{C['text_muted']}; border-bottom:2px solid {C['border_sub']}; padding:8px 10px;
}}
.wb-table td {{
    vertical-align:top; padding:10px; border-bottom:1px solid {C['border_sub']}; font-size:0.88rem;
}}
.wb-stats {{ display:flex; gap:16px; margin: 4px 0 24px 0; flex-wrap:wrap; }}
.wb-stat {{
    background:{C['bg_surface']}; border:1px solid {C['border_sub']}; border-radius:12px;
    padding:16px 22px; flex:1; min-width:130px; text-align:center;
    box-shadow:0 1px 3px rgba(0,0,0,0.06);
}}
.wb-stat-num {{ font-size:1.9rem; font-weight:800; line-height:1; }}
.wb-stat-label {{ color:{C['text_muted']}; font-size:0.72rem; letter-spacing:1px; text-transform:uppercase; margin-top:4px; }}
</style>
"""


def apply_dashboard_css() -> None:
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)


def phase_header(phase_label: str, title: str, subtitle: str,
                 accent: str = ACCENT_COMPLETE) -> str:
    """
    Return a clean white card phase-header banner for a light-background app.

    accent — pass one of the module constants:
        ACCENT_COMPLETE  (#059669 green)  — page fully built
        ACCENT_CURRENT   (#D97706 amber)  — page in progress
        ACCENT_COMING    (#9CA3AF grey)   — not yet started
    """
    return (
        f"<div style='background:#FFFFFF;border-left:4px solid {accent};"
        f"border-radius:8px;padding:16px 22px;margin-bottom:20px;"
        f"box-shadow:0 1px 3px rgba(0,0,0,0.07),0 1px 2px rgba(0,0,0,0.04)'>"
        f"<div style='font-size:0.65rem;font-weight:700;letter-spacing:2px;"
        f"text-transform:uppercase;color:{accent};margin-bottom:5px'>"
        f"{phase_label}</div>"
        f"<div style='font-size:1.6rem;font-weight:800;color:#1A202C;line-height:1.2'>"
        f"{title}</div>"
        f"<div style='font-size:0.875rem;color:#718096;margin-top:5px'>"
        f"{subtitle}</div>"
        f"</div>"
    )
