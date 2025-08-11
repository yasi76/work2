from __future__ import annotations

import json
import sys
from pathlib import Path
import typer

from .config import load_config, Config
from .logging_utils import setup_logging
from .pipeline import run_pipeline

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def run(
    config: Path = typer.Option(..., exists=True, readable=True, help="Path to config TOML"),
    output_dir: Path = typer.Option(None, help="Override output directory"),
    run_id: str = typer.Option(None, help="Deterministic run ID (default: timestamp)"),
    log_level: str = typer.Option("INFO", help="Log level"),
    json_logs: bool = typer.Option(False, help="Emit JSON logs"),
):
    cfg = load_config(str(config))
    if output_dir is not None:
        cfg.output_dir = str(output_dir)
    if run_id is not None:
        cfg.run_id = run_id
    if log_level is not None:
        cfg.log_level = log_level
    cfg.json_logs = json_logs

    setup_logging(cfg.log_level, cfg.json_logs)
    summary = run_pipeline(cfg)

    typer.echo(
        f"Completed. URLs: {summary['total_urls']} | CSV: {summary['files']['csv']} | JSON: {summary['files']['json']} | Report: {summary['files']['report']}"
    )


@app.command()
def validate(input: Path = typer.Option(..., exists=True, readable=True, help="Saved JSON of prior run")):
    data = json.loads(Path(input).read_text(encoding="utf-8"))
    urls = data.get("urls", [])
    # Basic schema check
    required = {"url", "source", "confidence", "category", "country", "method"}
    missing = []
    for idx, item in enumerate(urls):
        keys = set(item.keys())
        if not required.issubset(keys):
            missing.append(idx)
    if missing:
        typer.echo(f"Invalid records at positions: {missing}")
        raise typer.Exit(code=1)
    typer.echo(f"Validation OK. {len(urls)} records.")


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    main()