"""
storage.py — DuckDB persistence layer.

Schema: jobs(id, titulo, empresa, url, fonte, categoria, descritivo,
data_encontrada, status). Deduplicated on url via ON CONFLICT DO NOTHING.
Status values: novo | aplicado | descartado | entrevista.
"""
import hashlib
from datetime import date

import duckdb

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id              VARCHAR PRIMARY KEY,
    titulo          VARCHAR,
    empresa         VARCHAR,
    url             VARCHAR UNIQUE,
    fonte           VARCHAR,
    categoria       VARCHAR,
    descritivo      VARCHAR,
    data_encontrada DATE,
    status          VARCHAR DEFAULT 'novo'
)
"""


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def init_db() -> None:
    con = _connect()
    con.execute(SCHEMA)
    con.close()


def save_jobs(jobs: list[dict]) -> int:
    con = _connect()
    before = con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    for job in jobs:
        job_id = hashlib.sha256(job["url"].encode()).hexdigest()[:16]
        con.execute(
            """
            INSERT INTO jobs (id, titulo, empresa, url, fonte, categoria, descritivo, data_encontrada)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (url) DO NOTHING
            """,
            [
                job_id,
                job.get("titulo", ""),
                job.get("empresa", ""),
                job["url"],
                job.get("fonte", ""),
                job.get("categoria", ""),
                job.get("descritivo", job.get("snippet", "")),
                date.today(),
            ],
        )
    after = con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    con.close()
    return after - before


def update_status(url: str, status: str) -> None:
    con = _connect()
    con.execute("UPDATE jobs SET status = ? WHERE url = ?", [status, url])
    con.close()


def get_jobs(status: str = None) -> list[dict]:
    con = _connect()
    if status:
        rows = con.execute("SELECT * FROM jobs WHERE status = ? ORDER BY data_encontrada DESC", [status]).fetchall()
    else:
        rows = con.execute("SELECT * FROM jobs ORDER BY data_encontrada DESC").fetchall()
    cols = [c[0] for c in con.description]
    con.close()
    return [dict(zip(cols, row)) for row in rows]


def get_stats() -> dict:
    con = _connect()
    total = con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    by_status = dict(con.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall())
    by_categoria = dict(con.execute("SELECT categoria, COUNT(*) FROM jobs GROUP BY categoria").fetchall())
    by_fonte = dict(con.execute("SELECT fonte, COUNT(*) FROM jobs GROUP BY fonte").fetchall())
    con.close()
    return {"total": total, "por_status": by_status, "por_categoria": by_categoria, "por_fonte": by_fonte}
