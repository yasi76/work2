from __future__ import annotations

from typing import Dict, List, Tuple
from .models import UrlRecord


def sort_key_for_record(record: UrlRecord, method_priority: Dict[str, int]) -> Tuple[int, int, str]:
    method_score = method_priority.get(record.method, 0)
    # Higher confidence first, then method priority, then source name to stabilize
    return (
        record.confidence,
        method_score,
        record.source.lower(),
    )


def rank_records(records: List[UrlRecord], method_priority: Dict[str, int]) -> List[UrlRecord]:
    return sorted(records, key=lambda r: sort_key_for_record(r, method_priority), reverse=True)