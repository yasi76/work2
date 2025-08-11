from __future__ import annotations

from typing import List
from ..models import UrlRecord
from ..logging_utils import get_logger

logger = get_logger(__name__)


class EnhancedWrapperSource:
    def discover(self) -> List[UrlRecord]:
        try:
            from enhanced_startup_discovery import EnhancedStartupDiscovery  # type: ignore
        except Exception as exc:  # pragma: no cover - optional module
            logger.warning("Enhanced module not available: %s", exc)
            return []

        try:
            instance = EnhancedStartupDiscovery()
            result = instance.discover_all_startups()
        except Exception as exc:
            logger.error("Enhanced discovery failed: %s", exc, exc_info=True)
            return []

        records: List[UrlRecord] = []
        for item in result.get("urls", []):
            records.append(
                UrlRecord(
                    url=item.get("url", ""),
                    source=str(item.get("source", "Enhanced")),
                    confidence=int(item.get("confidence", 0)),
                    category=str(item.get("category", "")),
                    country=str(item.get("country", "")),
                    method="Enhanced Discovery",
                )
            )
        return records