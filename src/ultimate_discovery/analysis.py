from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List
from .models import UrlRecord


def analyze(records: List[UrlRecord], duplicates_removed: int, invalid_skipped: int) -> Dict[str, object]:
    method_counts: Counter[str] = Counter(r.method for r in records)
    confidence_distribution: Counter[int] = Counter(r.confidence for r in records)
    category_counts: Counter[str] = Counter(r.category for r in records)
    country_counts: Counter[str] = Counter(r.country for r in records)

    total = len(records)
    high = sum(1 for r in records if r.confidence >= 8)
    medium = sum(1 for r in records if 5 <= r.confidence < 8)
    low = sum(1 for r in records if r.confidence < 5)

    per_method_precision_proxy: Dict[str, float] = {}
    for method, count in method_counts.items():
        if count == 0:
            per_method_precision_proxy[method] = 0.0
        else:
            per_method_precision_proxy[method] = (
                sum(1 for r in records if r.method == method and r.confidence >= 8) / count
            )

    return {
        "total_urls": total,
        "method_counts": dict(method_counts),
        "confidence_distribution": dict(confidence_distribution),
        "category_counts": dict(category_counts),
        "country_counts": dict(country_counts),
        "quality_metrics": {
            "high_confidence": high,
            "medium_confidence": medium,
            "low_confidence": low,
            "quality_score": (high * 3 + medium * 2 + low) / total if total else 0.0,
            "per_method_precision_proxy": per_method_precision_proxy,
        },
        "duplicates_removed": duplicates_removed,
        "invalid_urls_skipped": invalid_skipped,
    }