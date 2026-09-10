"""
config.py — Queries, sources and settings.

QUERIES: search strings grouped by category, one stack focus per category.
Toggle USE_GOOGLE_API to switch the search backend (DuckDuckGo <-> Google CSE).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "jobs.duckdb"
EXPORT_DIR = DATA_DIR / "exports"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
MAX_RESULTS_PER_QUERY = 10
# ponytail: GCP Custom Search API blocked on billing/project config (403). Using the DuckDuckGo
# (ddgs) backend until that's sorted — flip to True once curl against SEARCH_URL returns 200.
USE_GOOGLE_API = False

DELAY_BETWEEN_REQUESTS = 2
FETCH_DESCRIPTION = True
SEARCH_TIMELIMIT = "m"  # "d"=dia, "w"=semana, "m"=mês, None=sem filtro

VALID_STATUSES = ("novo", "aplicado", "descartado", "entrevista")

QUERIES = {
    # ─── REMOTAR (curadoria 100% remoto — prioridade alta) ────────
    "Remotar — SQL / Dados": [
        'site:remotar.com.br "sql" "dados"',
        'site:remotar.com.br "analista de dados"',
        'site:remotar.com.br "engenheiro de dados"',
    ],
    "Remotar — Power BI / BI": [
        'site:remotar.com.br "power bi"',
        'site:remotar.com.br "analista de bi"',
        'site:remotar.com.br "business intelligence"',
    ],
    "Remotar — Analytics / dbt": [
        'site:remotar.com.br "analytics engineer"',
        'site:remotar.com.br "dbt"',
        'site:remotar.com.br "python" "dados"',
    ],

    # ─── GUPY (maior ATS BR) ───────────────────────────────────────
    "Gupy — SQL": [
        'site:gupy.io "sql" "remoto"',
        'site:gupy.io "sql" "home office"',
    ],
    "Gupy — Power BI": [
        'site:gupy.io "power bi" "remoto"',
        'site:gupy.io "power bi" "home office"',
    ],
    "Gupy — Python + Dados": [
        'site:gupy.io "python" "dados" "remoto"',
        'site:gupy.io "python" "analista" "remoto"',
    ],
    "Gupy — dbt / Analytics Engineer": [
        'site:gupy.io "dbt" "remoto"',
        'site:gupy.io "analytics engineer" "remoto"',
    ],
    "Gupy — Excel + BI": [
        'site:gupy.io "excel" "bi" "remoto"',
        'site:gupy.io "excel" "analista de dados" "remoto"',
    ],

    # ─── INHIRE (startups e scale-ups BR) ──────────────────────────
    "InHire — Dados / BI": [
        'site:inhire.app "engenheiro de dados"',
        'site:inhire.app "analista de dados"',
        'site:inhire.app "power bi"',
        'site:inhire.app "sql"',
    ],

    # ─── INDEED BR (volume alto) ────────────────────────────────────
    "Indeed BR — SQL": [
        'site:br.indeed.com "sql" "analista" "remoto"',
        'site:br.indeed.com "sql" "engenheiro de dados" "remoto"',
    ],
    "Indeed BR — Power BI": [
        'site:br.indeed.com "power bi" "remoto"',
        'site:br.indeed.com "power bi" "analista" "remoto"',
    ],

    # ─── REVELO (tech BR) ─────────────────────────────────────────
    # ponytail: GeekHunter removido — site:geekhunter.com.br não indexa vagas individuais no
    # DuckDuckGo (só páginas de suporte/blog), testado com várias queries, 0 resultado sempre.
    "Revelo — Dados / BI": [
        'site:jobs.revelo.com.br "analista de dados"',
        'site:jobs.revelo.com.br "power bi"',
        'site:jobs.revelo.com.br "engenheiro de dados"',
        'site:jobs.revelo.com.br "sql" "dados"',
    ],

    # ─── INTERNACIONAIS LATAM (USD) ─────────────────────────────────
    "LATAM USD — Analytics Engineer": [
        'site:boards.greenhouse.io "analytics engineer" "latam" "remote"',
        'site:jobs.lever.co "analytics engineer" "latam"',
        'site:jobs.lever.co "dbt" "latam"',
    ],
    "LATAM USD — Data Engineer": [
        'site:jobs.lever.co "data engineer" "brazil" "remote"',
        'site:boards.greenhouse.io "data engineer" "brazil" "remote"',
    ],
}
