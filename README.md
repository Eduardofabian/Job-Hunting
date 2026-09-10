# job-hunting 🎯

> Automated job search CLI for data roles in Brazil.
> Searches 7 sources, deduplicates results, stores in DuckDB and exports a Markdown report — ready to apply.

---

## The Problem

Finding remote data jobs in Brazil means checking Gupy, Indeed, InHire, Remotar and more — all manually, with no history and no stack-based filtering. Most job boards only let you search by title, not by the actual technologies required.

job-hunting automates this: run one command, get a curated report of relevant openings across all sources, filtered by your stack.

---

## Vision

Today it is a **radar** — it finds the openings. The goal is a full job-hunting
assistant that carries a role from discovery to offer:

| Stage | Now | Next |
|-------|-----|------|
| **Discover** | Multi-source search + noise filtering | Playwright for sources search engines don't index |
| **Evaluate** | Manual review of the Markdown report | LLM fit score (0–10) per opening against your profile |
| **Apply** | Copy link, tailor CV by hand | Draft a per-job CV + cover letter from a base profile |
| **Track** | `--status` flag in the CLI | Timeline per application, follow-up reminders |
| **Run** | Manual `python main.py --export` | GitHub Actions cron + Telegram alerts for high-fit jobs |

The CLI and DuckDB schema are built to absorb these without a rewrite — each
stage is a column on the existing `jobs` table and a new command.

---

## How It Works

```bash
python main.py --export
```

1. **Search** — queries DuckDuckGo across 7 job platforms, filtered to the last 30 days (falls back to no date filter when a narrow query returns nothing)
2. **Extract** — fetches each job page and parses the description with BeautifulSoup4
3. **Filter** — removes noise (DBT therapy listings, index pages, ad redirects) and deduplicates
4. **Store** — saves to local DuckDB with deduplication by URL
5. **Export** — generates `data/exports/vagas_YYYY-MM-DD.md` grouped by category

---

## CLI

```bash
python main.py                        # search and store
python main.py --export               # search + export markdown
python main.py --export-only          # export from existing database
python main.py --status aplicado URL  # update job status
python main.py --list novo            # list jobs by status
python main.py --stats                # database summary
```

Status values: `novo`, `aplicado`, `descartado`, `entrevista`.

---

## Stack

| Layer | Tool |
|-------|------|
| Search | DuckDuckGo Search (`ddgs`) |
| Scraping | `requests` + BeautifulSoup4 |
| Database | DuckDB |
| Config | `python-dotenv` |
| User-Agent | `fake-useragent` |

---

## Sources Searched

| Source | Type | Coverage |
|--------|------|----------|
| Gupy (`gupy.io`) | ATS | Largest BR job platform |
| Remotar (`remotar.com.br`) | Aggregator | 100% remote, curated |
| InHire (`inhire.app`) | ATS | BR tech startups |
| Indeed BR (`br.indeed.com`) | Aggregator | High volume |
| Revelo (`jobs.revelo.com.br`) | Platform | Tech, company invites you |
| Greenhouse (`boards.greenhouse.io`) | ATS | International / LATAM USD |
| Lever (`jobs.lever.co`) | ATS | International / LATAM USD |

LinkedIn and Glassdoor are intentionally excluded — their ToS forbids automated querying and they block it aggressively.

---

## Setup

```bash
git clone https://github.com/Eduardofabian/Job-Hunting.git
cd Job-Hunting
pip install -r requirements.txt
```

No API key required — the tool uses DuckDuckGo by default.

A `.env` file is optional, only for the Google Custom Search API backend:

```ini
GOOGLE_API_KEY=your_key_here
GOOGLE_CSE_ID=your_cx_here
```

---

## Status — v1

- [x] Multi-source search via DuckDuckGo
- [x] Job description extraction per domain
- [x] DuckDB storage with deduplication
- [x] Markdown export grouped by category
- [x] CLI with status tracking

Next steps are in [Vision](#vision) above.

---

## Why DuckDuckGo and Not Google?

Google Custom Search API was the first approach — blocked by a GCP propagation bug (403 on every request despite the API being enabled and billing linked). That code path is still in `scraper.py`; set `USE_GOOGLE_API = True` in `config.py` to use it once resolved.

Direct platform scraping (Playwright) is more robust but heavier — planned for v2.

---

## Project Structure

```text
job-hunting/
├── main.py         # CLI entry point
├── scraper.py      # DuckDuckGo search + URL parsing + filters
├── parser.py       # Job description extractor
├── storage.py      # DuckDB persistence layer
├── exporter.py     # Markdown report generator
├── config.py       # Queries, sources, settings
├── requirements.txt
├── .env.example    # Template — never commit .env
└── data/
    ├── jobs.duckdb     # Local database (gitignored)
    └── exports/        # Generated reports (gitignored)
```

---

*Built by [Eduardo Fabian de Oliveira](https://linkedin.com/in/eduardofabianoliveira) — Data Engineer*
