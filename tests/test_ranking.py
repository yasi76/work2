from ultimate_discovery.models import UrlRecord
from ultimate_discovery.ranking import rank_records


METHOD_PRIORITY = {
    "Hardcoded": 5,
    "Manual Curation": 4,
    "Google Search": 3,
    "Enhanced Discovery": 2,
    "Generated": 1,
}


def make(url: str, conf: int, method: str, source: str) -> UrlRecord:
    return UrlRecord(
        url=url,
        source=source,
        confidence=conf,
        category="cat",
        country="country",
        method=method,
    )


def test_ranking_confidence_first_then_method():
    recs = [
        make("https://a.com", 7, "Google Search", "A"),
        make("https://b.com", 7, "Enhanced Discovery", "B"),
        make("https://c.com", 8, "Enhanced Discovery", "C"),
    ]
    ranked = rank_records(recs, METHOD_PRIORITY)
    assert [r.normalized_url for r in ranked] == [
        "https://c.com/",
        "https://a.com/",
        "https://b.com/",
    ]


def test_tie_breaker_by_source_name():
    recs = [
        make("https://a.com", 7, "Google Search", "Zzz"),
        make("https://b.com", 7, "Google Search", "Aaa"),
    ]
    ranked = rank_records(recs, METHOD_PRIORITY)
    assert [r.source for r in ranked] == ["Zzz", "Aaa"]  # reverse sort overall