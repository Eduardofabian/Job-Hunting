"""
scraper.py — Job search via DuckDuckGo Search (ddgs).

Runs each query from config.QUERIES. Uses the Google Custom Search API instead
when config.USE_GOOGLE_API is True. Extracts source (Greenhouse, Lever, Indeed,
etc.) and company name from the URL via regex. Callers filter index pages
(is_index_page) and noise terms (is_noise) before storing results.
"""
import re

import requests
from ddgs import DDGS
from ddgs.exceptions import DDGSException

from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, MAX_RESULTS_PER_QUERY, SEARCH_TIMELIMIT, USE_GOOGLE_API

SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# ponytail: order matters — greenhouse/lever/smartrecruiters checked before generic fallback
SOURCE_PATTERNS = [
    (re.compile(r"boards\.greenhouse\.io/([^/]+)"), "Greenhouse"),
    (re.compile(r"jobs\.lever\.co/([^/]+)"), "Lever"),
    (re.compile(r"jobs\.smartrecruiters\.com/([^/]+)"), "SmartRecruiters"),
]


NOISE_TERMS = [
    # dbt terapêutico (confundido com dbt data tool)
    "therapist", "psychologist", "clinical", "dbt therapy", "dbt skills",
    "dialectical", "licensed", "mental health", "counselor", "behavioral therapy",
    # cargos fora do target
    "hvac", "drafter", "autocad designer", "mechanical engineer",
    "child", "adolescent", "nurse", "physician",
    # páginas de índice (não são vagas)
    "jobs available on indeed", "job openings at", "vagas abertas no momento",
    "browse", "search results", "job listings",
    # links de anúncio/redirecionamento
    "bing.com/aclick", "jobleads.com", "latam remote jobs - work from home",
]

def is_noise(job: dict) -> bool:
    text = (job.get("titulo", "") + " " + job.get("descritivo", job.get("snippet", ""))).lower()
    return any(term.lower() in text for term in NOISE_TERMS)


# ponytail: sites indexam páginas de busca/listagem junto com vagas reais — descartar
BLOCKED_URL_PATTERNS = [
    "/q-", "/l-", "/job-search", "/jobs?", "/jobs/search",
    "-vagas.html", "bing.com/aclick", "jobleads.com", "/jobs.html", "?from=",
    "/skills/", "/recrutadores-form", "/parceiros/",
]


def is_index_page(url: str) -> bool:
    return any(pattern in url for pattern in BLOCKED_URL_PATTERNS)


def parse_url(url: str) -> dict:
    for pattern, fonte in SOURCE_PATTERNS:
        m = pattern.search(url)
        if m:
            return {"fonte": fonte, "empresa": m.group(1)}
    if "indeed.com" in url:
        return {"fonte": "Indeed", "empresa": "?"}
    return {"fonte": "Outro", "empresa": "?"}


def _search_google_api(query: str, categoria: str) -> list[dict]:
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": MAX_RESULTS_PER_QUERY,
    }
    resp = requests.get(SEARCH_URL, params=params, timeout=15)
    resp.raise_for_status()
    items = resp.json().get("items", [])

    jobs = []
    for item in items:
        url = item["link"]
        source_info = parse_url(url)
        jobs.append({
            "titulo": item.get("title", ""),
            "url": url,
            "snippet": item.get("snippet", ""),
            "categoria": categoria,
            "fonte": source_info["fonte"],
            "empresa": source_info["empresa"],
        })
    return jobs


def _search_free(query: str, categoria: str) -> list[dict]:
    # ponytail: DuckDuckGo, no API key needed — googlesearch-python gets rate-limited/blocked by Google
    try:
        results = DDGS().text(query, max_results=MAX_RESULTS_PER_QUERY, timelimit=SEARCH_TIMELIMIT)
    except DDGSException:
        # site: + termos entre aspas + timelimit combinados costumam voltar índice vazio no DDG —
        # cai pra busca sem filtro de data em vez de perder a categoria inteira
        results = DDGS().text(query, max_results=MAX_RESULTS_PER_QUERY)
    jobs = []
    for item in results:
        url = item["href"]
        source_info = parse_url(url)
        jobs.append({
            "titulo": item.get("title", ""),
            "url": url,
            "snippet": item.get("body", ""),
            "categoria": categoria,
            "fonte": source_info["fonte"],
            "empresa": source_info["empresa"],
        })
    return jobs


def search(query: str, categoria: str) -> list[dict]:
    if USE_GOOGLE_API:
        return _search_google_api(query, categoria)
    return _search_free(query, categoria)
