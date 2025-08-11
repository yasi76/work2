from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from urllib.parse import urlparse, urlunparse
import re


HTTP_SCHEMES = {"http", "https"}


@dataclass(slots=True)
class UrlRecord:
    url: str
    source: str
    confidence: int
    category: str
    country: str
    method: str
    notes: Optional[str] = None

    normalized_url: str = field(init=False)

    def __post_init__(self) -> None:
        self.normalized_url = normalize_url(self.url)


@dataclass(slots=True)
class DiscoveryResult:
    records: List[UrlRecord]
    meta: Dict[str, object]


def normalize_url(raw_url: str) -> str:
    if not raw_url:
        return ""

    url = raw_url.strip()

    # Prepend scheme if missing
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = f"https://{url}"

    parsed = urlparse(url)

    # Lowercase scheme and host
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Remove userinfo and port if default
    if "@" in netloc:
        netloc = netloc.split("@", 1)[-1]

    # Strip query and fragment
    path = parsed.path or "/"
    query = ""
    fragment = ""

    # Remove trailing slash except for root
    if path != "/":
        path = path.rstrip("/")
        if not path:
            path = "/"

    normalized = urlunparse((scheme, netloc, path, "", query, fragment))
    return normalized


def looks_like_domain(host: str) -> bool:
    if not host or host.count(".") < 1:
        return False
    if re.search(r"\s", host):
        return False
    # Basic TLD check
    if not re.search(r"\.[a-zA-Z]{2,}$", host):
        return False
    return True


def is_valid_http_url(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in HTTP_SCHEMES:
        return False
    if not looks_like_domain(parsed.netloc.lower()):
        return False
    return True


def deduplicate_records(records: List[UrlRecord]) -> Tuple[List[UrlRecord], int]:
    seen: set[str] = set()
    unique: List[UrlRecord] = []
    duplicates = 0
    for rec in records:
        if rec.normalized_url in seen:
            duplicates += 1
            continue
        seen.add(rec.normalized_url)
        unique.append(rec)
    return unique, duplicates