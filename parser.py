"""
parser.py — Job description extractor.

Fetches the job posting page and extracts the description text using
domain-specific CSS selectors, falling back to plain body text, then to the
search snippet if the request fails. Rotates User-Agent via fake-useragent
and sleeps DELAY_BETWEEN_REQUESTS seconds between calls.
"""
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from config import DELAY_BETWEEN_REQUESTS

_ua = UserAgent()

SELECTORS = {
    "greenhouse.io": ["div.content", "div#content"],
    "lever.co": ["div.section-wrapper", "div.posting-description"],
    "smartrecruiters.com": ["div.job-description"],
    "indeed.com": ["div#jobDescriptionText"],
    "remotar.com.br": ["div.job-description", "div.content", "main"],
    "revelo.com.br": ["div.job-description", "div.description", "main"],
    "inhire.app": ["div.job-description", "div.content", "main"],
}


def fetch_description(url: str, snippet: str = "") -> str:
    try:
        resp = requests.get(url, headers={"User-Agent": _ua.random}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        node = None
        for domain, selectors in SELECTORS.items():
            if domain in url:
                for selector in selectors:
                    node = soup.select_one(selector)
                    if node:
                        break
                break

        if node:
            return node.get_text(" ", strip=True)[:1000] or snippet
        if soup.body:
            return soup.body.get_text(" ", strip=True)[:500] or snippet
        return snippet
    except Exception:
        return snippet
    finally:
        time.sleep(DELAY_BETWEEN_REQUESTS)
