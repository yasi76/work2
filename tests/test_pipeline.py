from types import SimpleNamespace
from ultimate_discovery.config import Config
from ultimate_discovery.pipeline import run_pipeline
from ultimate_discovery.models import UrlRecord


def test_pipeline_happy_path(monkeypatch, tmp_path):
    cfg = Config(
        output_dir=str(tmp_path),
        include_curated=False,
        include_hardcoded=False,
        use_enhanced=False,
        use_google=False,
        rate_limit_per_sec=1000.0,
    )

    # Inject mock sources
    def fake_build_sources(_cfg):
        def s1():
            return [
                UrlRecord(
                    url="https://a.com",
                    source="S1",
                    confidence=9,
                    category="cat",
                    country="de",
                    method="Hardcoded",
                ),
                UrlRecord(
                    url="https://b.com",
                    source="S1",
                    confidence=6,
                    category="cat",
                    country="de",
                    method="Enhanced Discovery",
                ),
            ]

        def s2():
            return [
                UrlRecord(
                    url="https://b.com/",
                    source="S2",
                    confidence=7,
                    category="cat",
                    country="de",
                    method="Google Search",
                ),
                UrlRecord(
                    url="https://invalid host",
                    source="S2",
                    confidence=10,
                    category="cat",
                    country="de",
                    method="Google Search",
                ),
            ]

        return [s1, s2]

    monkeypatch.setattr("ultimate_discovery.pipeline.build_sources", fake_build_sources)

    summary = run_pipeline(cfg)
    assert summary["total_urls"] == 2  # a.com and b.com deduped
    files = summary["files"]
    assert files["csv"].endswith(".csv")
    assert files["json"].endswith(".json")
    assert files["report"].endswith(".txt")