from __future__ import annotations

from typing import List
from ..models import UrlRecord
from ..logging_utils import get_logger

logger = get_logger(__name__)


class GoogleSearchWrapperSource:
    def discover(self) -> List[UrlRecord]:
        try:
            from google_search_scraper import GoogleSearchStartupFinder  # type: ignore
        except Exception as exc:  # pragma: no cover
            logger.warning("Google search module not available: %s", exc)
            return []

        try:
            instance = GoogleSearchStartupFinder()
            result = instance.discover_all_startups()
        except Exception as exc:
            logger.error("Google search discovery failed: %s", exc, exc_info=True)
            return []

        records: List[UrlRecord] = []
        for item in result.get("urls", []):
            records.append(
                UrlRecord(
                    url=item.get("url", ""),
                    source=str(item.get("source", "Google")),
                    confidence=int(item.get("confidence", 0)),
                    category=str(item.get("category", "")),
                    country=str(item.get("country", "")),
                    method="Google Search",
                )
            )
        return records