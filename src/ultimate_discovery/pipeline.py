from __future__ import annotations

import time
from typing import List, Callable
from .config import Config
from .models import UrlRecord, is_valid_http_url, deduplicate_records
from .ranking import rank_records
from .analysis import analyze
from .io_utils import determine_run_id, make_output_paths, write_outputs
from .logging_utils import get_logger

logger = get_logger(__name__)


class RateLimiter:
    def __init__(self, rate_per_sec: float) -> None:
        self.min_interval = 1.0 / max(rate_per_sec, 0.0001)
        self._last_time = 0.0

    def wait(self) -> None:
        now = time.time()
        elapsed = now - self._last_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_time = time.time()


def with_retry(fn: Callable[[], List[UrlRecord]], max_retries: int, delay_s: float = 1.0) -> List[UrlRecord]:
    attempt = 0
    while True:
        try:
            return fn()
        except Exception as exc:
            attempt += 1
            logger.error("Discoverer failed on attempt %s: %s", attempt, exc, exc_info=True)
            if attempt > max_retries:
                return []
            time.sleep(delay_s * attempt)


def build_sources(cfg: Config) -> List[Callable[[], List[UrlRecord]]]:
    from .discovery.hardcoded import HardcodedSource
    from .discovery.curated import CuratedSource

    sources: List[Callable[[], List[UrlRecord]]] = []

    if cfg.include_hardcoded:
        sources.append(HardcodedSource().discover)
    if cfg.include_curated:
        sources.append(CuratedSource().discover)

    if cfg.use_enhanced:
        from .discovery.enhanced import EnhancedWrapperSource

        sources.append(EnhancedWrapperSource().discover)
    if cfg.use_google:
        from .discovery.google_search import GoogleSearchWrapperSource

        sources.append(GoogleSearchWrapperSource().discover)

    return sources


def run_pipeline(cfg: Config) -> dict:
    limiter = RateLimiter(cfg.rate_limit_per_sec)

    # Run discoverers
    all_records: List[UrlRecord] = []
    for discover in build_sources(cfg):
        limiter.wait()
        records = with_retry(discover, max_retries=cfg.max_retries)
        logger.info("Source yielded %d records", len(records))
        all_records.extend(records)

    # Validate
    invalid = 0
    validated: List[UrlRecord] = []
    for rec in all_records:
        if not is_valid_http_url(rec.normalized_url):
            invalid += 1
            continue
        if cfg.allow_domains and not any(ad in rec.normalized_url for ad in cfg.allow_domains):
            # Skip if allowlist configured and not matched
            continue
        if cfg.block_domains and any(bd in rec.normalized_url for bd in cfg.block_domains):
            continue
        if rec.confidence < cfg.min_confidence:
            continue
        # Apply category/country filters if set
        if cfg.category_filters and rec.category not in cfg.category_filters:
            continue
        if cfg.country_filters and rec.country not in cfg.country_filters:
            continue
        validated.append(rec)

    # Dedupe
    deduped, duplicates = deduplicate_records(validated)

    # Rank
    ranked = rank_records(deduped, cfg.method_priority)

    # Analysis
    analysis = analyze(ranked, duplicates_removed=duplicates, invalid_skipped=invalid)

    # Outputs
    run_id = determine_run_id(cfg.run_id)
    out_paths = make_output_paths(cfg.output_dir, run_id)
    csv_path, json_path, report_path = write_outputs(ranked, analysis, out_paths)

    summary = {
        "total_urls": len(ranked),
        "analysis": analysis,
        "files": {"csv": csv_path, "json": json_path, "report": report_path},
    }
    return summary