#!/usr/bin/env python3
import argparse, csv, json, re, time
from html import unescape
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

# ---------- HTTP session with retries ----------
def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en"})
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD","GET","OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=50)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

# ---------- Text cleanup ----------
SEP_REGEX = re.compile(r"\s*[\|\-–—>]+\s*")
WS_REGEX = re.compile(r"\s+")
def clean_text(t: str) -> str:
    if not t: return ""
    t = unescape(t).strip()
    # Prefer the first chunk before separators like " | " or " – "
    parts = SEP_REGEX.split(t, maxsplit=1)
    t = parts[0].strip()
    t = WS_REGEX.sub(" ", t)
    # Trim very long titles
    return t[:200].strip()

# ---------- Domain → nice name fallback ----------
def name_from_domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    # Drop common subdomains
    for sub in ("www.", "m.", "app.", "en.", "de."):
        if host.startswith(sub):
            host = host[len(sub):]
    # Take second-level label
    bits = host.split(".")
    core = ""
    if len(bits) >= 2:
        core = bits[-2]
    else:
        core = bits[0]
    core = core.replace("-", " ").replace("_", " ").strip()
    core = WS_REGEX.sub(" ", core)
    return core.title() if core else ""

# ---------- JSON-LD extraction ----------
ORG_TYPES = {
    "Organization","LocalBusiness","Corporation","Company","NGO",
    "MedicalOrganization","Hospital","MedicalClinic","SoftwareApplication","WebSite"
}
def extract_from_jsonld(soup: BeautifulSoup) -> str:
    scripts = soup.find_all("script", {"type":"application/ld+json"})
    for tag in scripts:
        try:
            data = json.loads(tag.string or tag.text or "")
        except Exception:
            continue
        # Normalize to list
        items = data if isinstance(data, list) else [data]
        for it in items:
            if not isinstance(it, dict):
                continue
            t = it.get("@type")
            # @type may be string or list
            types = {t} if isinstance(t, str) else set(t or [])
            if types & ORG_TYPES:
                name = it.get("name") or it.get("legalName") or it.get("alternateName")
                if name:
                    return clean_text(str(name))
    return ""

# ---------- Meta tags / H1 / Title ----------
def extract_from_meta_h1_title(soup: BeautifulSoup) -> str:
    # og:site_name
    tag = soup.find("meta", property="og:site_name")
    if tag and tag.get("content"):
        return clean_text(tag["content"])
    # application-name
    tag = soup.find("meta", attrs={"name":"application-name"})
    if tag and tag.get("content"):
        return clean_text(tag["content"])
    # First H1 (skip very long slogans)
    h1 = soup.find("h1")
    if h1:
        h1_text = clean_text(h1.get_text(" ", strip=True))
        if h1_text and len(h1_text.split()) <= 8:
            return h1_text
    # Title
    if soup.title and soup.title.string:
        return clean_text(soup.title.string)
    return ""

# ---------- Main extractor ----------

def extract_company_name(url: str, session: requests.Session, timeout: float = 12.0) -> str:
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        # Some sites send 403 to bots; try homepage if deep URL
        if resp.status_code >= 400:
            # retry bare origin
            parsed = urlparse(url)
            origin = f"{parsed.scheme}://{parsed.netloc}/"
            resp = session.get(origin, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
    except Exception:
        # last-ditch: name from domain
        return name_from_domain(url)

    soup = BeautifulSoup(resp.content, "html.parser")

    # 1) JSON-LD Organization.name
    name = extract_from_jsonld(soup)
    if name:
        return name

    # 2) og:site_name / app name / h1 / title
    name = extract_from_meta_h1_title(soup)
    if name:
        return name

    # 3) Fallback from domain
    return name_from_domain(resp.url or url)

# ---------- CSV I/O ----------

def enrich_csv(input_csv: str, output_csv: str, limit: int | None, delay: float):
    session = make_session()
    rows = []
    with open(input_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "url" not in reader.fieldnames:
            raise SystemExit("Input CSV must have a 'url' column.")
        fieldnames = list(reader.fieldnames)
        if "company_name" not in fieldnames:
            fieldnames.append("company_name")

        with open(output_csv, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=fieldnames)
            writer.writeheader()

            for i, row in enumerate(reader, start=1):
                if limit and i > limit:
                    break
                url = (row.get("url") or "").strip()
                if not url:
                    row["company_name"] = ""
                    writer.writerow(row); continue

                try:
                    name = extract_company_name(url, session)
                except Exception:
                    name = name_from_domain(url)

                row["company_name"] = name
                writer.writerow(row)

                if delay > 0:
                    time.sleep(delay)

def main():
    ap = argparse.ArgumentParser(description="Enrich a CSV of URLs with company_name")
    ap.add_argument("input_csv", help="Path to input CSV (must include 'url' column)")
    ap.add_argument("-o", "--output", help="Output CSV path (default: add _with_names)")
    ap.add_argument("--limit", type=int, default=None, help="Max rows to process (for testing)")
    ap.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    args = ap.parse_args()

    out = args.output
    if not out:
        if args.input_csv.lower().endswith(".csv"):
            out = args.input_csv[:-4] + "_with_names.csv"
        else:
            out = args.input_csv + "_with_names.csv"

    enrich_csv(args.input_csv, out, args.limit, args.delay)
    print(f"✅ Done. Wrote: {out}")

if __name__ == "__main__":
    main()