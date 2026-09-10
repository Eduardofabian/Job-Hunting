"""
exporter.py — Markdown report generator.

Groups jobs by category into data/exports/vagas_YYYY-MM-DD.md
(utf-8-sig for Windows compatibility).
"""
from datetime import date
from pathlib import Path

from config import EXPORT_DIR

CATEGORY_EMOJI = {
    "Analytics Engineer / dbt": "🔵",
    "Engenheiro de Dados": "🟢",
    "Analista de Dados": "🟢",
    "Analista de BI / Desenvolvedor Power BI": "🟡",
    "Stack SQL + Power BI": "🟡",
    "Stack SQL + Excel (analista generalista)": "🟡",
    "Analista de Produto (tech)": "🟠",
    "Analista de Growth": "🟠",
    "Analista de Operações / Inteligência Operacional": "🟠",
    "Analista Financeiro (dados)": "🟠",
    "Analytics Engineer LATAM (USD)": "🔴",
    "Data Engineer LATAM (USD)": "🔴",
}


def export_md(jobs: list[dict]) -> Path:
    today = date.today().isoformat()
    lines = [f"# Job Radar — {today}", f"_{len(jobs)} vagas encontradas_", "", "---", ""]

    by_categoria: dict[str, list[dict]] = {}
    for job in jobs:
        by_categoria.setdefault(job["categoria"], []).append(job)

    for categoria, itens in by_categoria.items():
        emoji = CATEGORY_EMOJI.get(categoria, "⚪")
        lines.append(f"## {emoji} {categoria}")
        lines.append("")
        for job in itens:
            lines.append(f"### {job['titulo']} — {job['empresa']}")
            lines.append(f"- **Link:** {job['url']}")
            lines.append(f"- **Fonte:** {job['fonte']}")
            lines.append(f"- **Encontrada em:** {job['data_encontrada']}")
            lines.append(f"- **Status:** {job['status']}")
            if job.get("descritivo"):
                lines.append("- **Descritivo:**")
                lines.append(f"  > {job['descritivo']}")
            lines.append("")
        lines.append("---")
        lines.append("")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EXPORT_DIR / f"vagas_{today}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8-sig")
    return out_path
