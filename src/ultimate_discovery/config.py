from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import sys

try:  # Python 3.11+
    import tomllib as _toml
except Exception:  # pragma: no cover
    try:
        import tomli as _toml  # type: ignore
    except Exception:  # pragma: no cover
        _toml = None  # type: ignore


DEFAULT_METHOD_PRIORITY: Dict[str, int] = {
    "Hardcoded": 5,
    "Manual Curation": 4,
    "Google Search": 3,
    "Enhanced Discovery": 2,
    "Generated": 1,
}


@dataclass(slots=True)
class Config:
    output_dir: str
    country_filters: List[str] = field(default_factory=list)
    category_filters: List[str] = field(default_factory=list)
    min_confidence: int = 0

    rate_limit_per_sec: float = 1.0
    max_retries: int = 2
    timeout_s: float = 15.0

    include_curated: bool = True
    include_hardcoded: bool = True

    use_enhanced: bool = True
    use_google: bool = True

    optional_module_paths: Dict[str, str] = field(default_factory=dict)

    allow_domains: List[str] = field(default_factory=list)
    block_domains: List[str] = field(default_factory=list)

    method_priority: Dict[str, int] = field(default_factory=lambda: dict(DEFAULT_METHOD_PRIORITY))

    log_level: str = "INFO"
    json_logs: bool = False

    run_id: Optional[str] = None


def load_config(path: str) -> Config:
    if _toml is None:
        print(
            "tomllib/tomli not available. Please install 'tomli' on Python 3.10 or upgrade to Python 3.11.",
            file=sys.stderr,
        )
        raise RuntimeError("Missing TOML parser")

    with open(path, "rb") as f:
        data = _toml.load(f)

    cfg = Config(
        output_dir=str(data.get("output_dir", "./out")),
        country_filters=list(data.get("country_filters", []) or []),
        category_filters=list(data.get("category_filters", []) or []),
        min_confidence=int(data.get("min_confidence", 0)),
        rate_limit_per_sec=float(data.get("rate_limit_per_sec", 1.0)),
        max_retries=int(data.get("max_retries", 2)),
        timeout_s=float(data.get("timeout_s", 15.0)),
        include_curated=bool(data.get("include_curated", True)),
        include_hardcoded=bool(data.get("include_hardcoded", True)),
        use_enhanced=bool(data.get("use_enhanced", True)),
        use_google=bool(data.get("use_google", True)),
        optional_module_paths=dict(data.get("optional_module_paths", {}) or {}),
        allow_domains=list(data.get("allow_domains", []) or []),
        block_domains=list(data.get("block_domains", []) or []),
        method_priority=dict(data.get("method_priority", DEFAULT_METHOD_PRIORITY) or DEFAULT_METHOD_PRIORITY),
        log_level=str(data.get("log_level", "INFO")),
        json_logs=bool(data.get("json_logs", False)),
        run_id=(str(data.get("run_id")) if data.get("run_id") is not None else None),
    )

    # Env override: allow USE_GOOGLE=false to disable Google source
    env_use_google = os.getenv("USE_GOOGLE")
    if env_use_google is not None:
        cfg.use_google = env_use_google.strip().lower() not in {"0", "false", "no", "off"}

    # Ensure output directory exists
    os.makedirs(cfg.output_dir, exist_ok=True)
    return cfg