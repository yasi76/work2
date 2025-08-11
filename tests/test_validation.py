from ultimate_discovery.models import UrlRecord, normalize_url, is_valid_http_url, deduplicate_records


def test_normalize_url_basic():
    assert normalize_url("example.com") == "https://example.com/"
    assert normalize_url("HTTP://Example.COM/path/") == "http://example.com/path"


def test_is_valid_http_url():
    assert is_valid_http_url("https://example.com/")
    assert not is_valid_http_url("ftp://example.com/")
    assert not is_valid_http_url("https://not a host/")


def test_deduplicate_records():
    a = UrlRecord(
        url="https://Example.com/",
        source="s",
        confidence=5,
        category="c",
        country="de",
        method="m",
    )
    b = UrlRecord(
        url="https://example.com",
        source="s",
        confidence=7,
        category="c",
        country="de",
        method="m",
    )
    unique, dup = deduplicate_records([a, b])
    assert len(unique) == 1
    assert dup == 1