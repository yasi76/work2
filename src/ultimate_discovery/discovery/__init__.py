from __future__ import annotations

from typing import Protocol, List
from ..models import UrlRecord


class DiscoverySource(Protocol):
    def discover(self) -> List[UrlRecord]:
        ...