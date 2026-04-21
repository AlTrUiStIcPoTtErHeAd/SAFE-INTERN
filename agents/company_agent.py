"""
Company agent (rule-based).

NO LLM
NO CrewAI
"""

from urllib.parse import urlparse
import requests
import re
from bs4 import BeautifulSoup

from database.company_repository import record_company_check

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "icloud.com", "aol.com", "protonmail.com"
}


def _domain(value: str | None) -> str | None:
    if not value:
        return None
    if "@" in value:
        return value.split("@")[-1].lower()
    parsed = urlparse(value if value.startswith("http") else "https://" + value)
    return parsed.netloc.replace("www.", "").lower() or None


def analyze_website_content(html_content: str, expected_domain: str | None) -> list[str]:
    issues = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Look for emails
        text_content = soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content)
        emails = list(set([e.lower() for e in emails if len(e) < 50]))
        
        if expected_domain and emails:
            # Check if any email matches the expected domain
            domain_match = any(expected_domain in email for email in emails)
            
            if not domain_match:
                 issues.append(f"Website lists emails but none match domain @{expected_domain}")
        
        # 2. Check for contact page
        contact_links = soup.find_all('a', href=True)
        has_contact_page = any('contact' in link['href'].lower() or 'contact' in link.text.lower() for link in contact_links)
        
        if not has_contact_page and not emails:
             issues.append("Website has no clear 'Contact' section or visible emails")

    except Exception:
        pass
        
    return issues


def run_company_agent(intake: dict) -> dict:
    observations = []

    website = intake.get("website")
    email = intake.get("email")

    website_domain = _domain(website)
    email_domain = _domain(email)

    if website:
        try:
            url = website if website.startswith("http") else f"https://{website}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code != 200:
                observations.append("Company website not reachable")
            else:
                # Website is reachable, analyze content
                content_issues = analyze_website_content(r.text, website_domain)
                observations.extend(content_issues)

            if not r.url.startswith("https"):
                observations.append("Website does not use HTTPS")
                
        except Exception:
            observations.append("Company website not reachable")

    if email_domain:
        if email_domain in FREE_EMAIL_DOMAINS:
            observations.append("Free email domain used")
        if website_domain and email_domain != website_domain:
            observations.append("Email domain does not match website domain")

    record_company_check(
        domain=website_domain,
        email_domain=email_domain,
        issues=observations
    )

    if not observations:
        observations.append("No major company issues detected")

    return {"observations": observations}
