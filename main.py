"""
job-radar — CLI entry point.

Commands:
  python main.py               search and store jobs
  python main.py --export      search + export markdown report
  python main.py --export-only  export from existing database
  python main.py --status aplicado <url>  update job status
  python main.py --list novo   list jobs by status
  python main.py --stats       show database summary
"""
import argparse
import sys

from config import FETCH_DESCRIPTION, QUERIES, VALID_STATUSES
from exporter import export_md
from parser import fetch_description
from scraper import is_index_page, is_noise, search
from storage import get_jobs, get_stats, init_db, save_jobs, update_status


def run_search():
    all_jobs = []
    descartadas_indice = 0
    for categoria, queries in QUERIES.items():
        for q in queries:
            try:
                results = search(q, categoria)
            except Exception as e:
                print(f"  ! erro na busca '{q}': {e}")
                continue
            bruto = len(results)
            results = [j for j in results if not is_index_page(j["url"])]
            descartadas_indice += bruto - len(results)
            if FETCH_DESCRIPTION:
                for job in results:
                    job["descritivo"] = fetch_description(job["url"], job.get("snippet", ""))
            all_jobs.extend(results)
            print(f"  {categoria} :: {q} -> {len(results)} resultado(s)")

    print(f"  ⨯ {descartadas_indice} vagas descartadas por URL de índice")

    limpo = [j for j in all_jobs if not is_noise(j)]
    descartadas_ruido = len(all_jobs) - len(limpo)
    print(f"  ⨯ {descartadas_ruido} vagas descartadas por ruído")

    novas = save_jobs(limpo)
    print(f"✔ {len(limpo)} vagas encontradas, {novas} novas")


def print_jobs(jobs: list[dict]):
    if not jobs:
        print("Nenhuma vaga encontrada.")
        return
    for job in jobs:
        print(f"[{job['status']}] {job['titulo']} — {job['empresa']} ({job['fonte']})")
        print(f"  {job['url']}")


def print_stats(stats: dict):
    print(f"✔ Total de vagas: {stats['total']}")
    print("📌 Por status:")
    print("   " + " | ".join(f"{k}: {v}" for k, v in stats["por_status"].items()))
    print("📊 Por categoria:")
    for categoria, count in sorted(stats["por_categoria"].items(), key=lambda x: -x[1]):
        print(f"   {categoria}: {count}")
    print("🔗 Por fonte:")
    for fonte, count in sorted(stats["por_fonte"].items(), key=lambda x: -x[1]):
        print(f"   {fonte}: {count}")


def main():
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="job-radar — busca vagas remotas")
    parser.add_argument("--export", action="store_true", help="busca + exporta .md")
    parser.add_argument("--export-only", action="store_true", help="só exporta, sem buscar")
    parser.add_argument("--status", nargs=2, metavar=("STATUS", "URL"), help="atualiza status de uma vaga")
    parser.add_argument("--list", metavar="STATUS", help="lista vagas por status")
    parser.add_argument("--stats", action="store_true", help="resumo do banco")
    args = parser.parse_args()

    init_db()

    if args.status:
        status, url = args.status
        if status not in VALID_STATUSES:
            print(f"! status inválido. Use um de: {', '.join(VALID_STATUSES)}")
            return
        update_status(url, status)
        print(f"✔ Status atualizado → {status}")

    elif args.list:
        print_jobs(get_jobs(status=args.list))

    elif args.stats:
        print_stats(get_stats())

    elif args.export_only:
        path = export_md(get_jobs())
        print(f"✔ Exportado → {path}")

    elif args.export:
        run_search()
        path = export_md(get_jobs())
        print(f"✔ Exportado → {path}")

    else:
        run_search()


if __name__ == "__main__":
    main()
