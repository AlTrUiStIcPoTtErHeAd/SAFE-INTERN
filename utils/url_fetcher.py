# utils/url_fetcher.py
"""
URL content fetcher for SAFE-INTERN.

Purpose:
- Fetch readable website text
- Used in intake BEFORE analysis
"""

import requests
from bs4 import BeautifulSoup


def fetch_text_from_url(url: str, timeout: int = 10) -> str:
    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    response = requests.get(url, timeout=timeout, headers={
        "User-Agent": "SAFE-INTERN/1.0"
    })

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts & styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
