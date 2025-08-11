from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Tuple
import csv
import json
import os

from .models import UrlRecord


def determine_run_id(run_id: str | None) -> str:
    return run_id or datetime.now().strftime("%Y%m%d_%H%M%S")


def make_output_paths(output_dir: str, run_id: str) -> Dict[str, str]:
    run_dir = os.path.join(output_dir, run_id)
    os.makedirs(run_dir, exist_ok=True)
    return {
        "csv": os.path.join(run_dir, f"ultimate_discovery_{run_id}.csv"),
        "json": os.path.join(run_dir, f"ultimate_discovery_{run_id}.json"),
        "report": os.path.join(run_dir, f"discovery_report_{run_id}.txt"),
        "manifest": os.path.join(run_dir, f"MANIFEST.json"),
    }


def write_outputs(records: List[UrlRecord], analysis: Dict[str, object], out_paths: Dict[str, str]) -> Tuple[str, str, str]:
    # CSV
    with open(out_paths["csv"], "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "url",
                "source",
                "confidence",
                "category",
                "country",
                "method",
                "notes",
            ],
        )
        writer.writeheader()
        for r in records:
            writer.writerow(
                {
                    "url": r.normalized_url or r.url,
                    "source": r.source,
                    "confidence": r.confidence,
                    "category": r.category,
                    "country": r.country,
                    "method": r.method,
                    "notes": r.notes or "",
                }
            )

    # JSON
    payload = {
        "discovery_timestamp": out_paths["json"].split("_")[-1].split(".")[0],
        "total_urls_discovered": len(records),
        "analysis": analysis,
        "urls": [
            {
                "url": r.normalized_url or r.url,
                "source": r.source,
                "confidence": r.confidence,
                "category": r.category,
                "country": r.country,
                "method": r.method,
                "notes": r.notes,
            }
            for r in records
        ],
    }
    with open(out_paths["json"], "w", encoding="utf-8") as jf:
        json.dump(payload, jf, indent=2, ensure_ascii=False)

    # Report
    with open(out_paths["report"], "w", encoding="utf-8") as rf:
        rf.write("🚀 ULTIMATE STARTUP DISCOVERY REPORT\n")
        rf.write("=" * 60 + "\n\n")
        rf.write(f"Discovery Run ID: {os.path.basename(os.path.dirname(out_paths['report']))}\n")
        rf.write(f"Total URLs Discovered: {len(records)}\n\n")

        rf.write("📊 DISCOVERY METHODS:\n")
        for method, count in (analysis.get("method_counts") or {}).items():
            rf.write(f"  • {method}: {count} URLs\n")

        qm = analysis.get("quality_metrics", {})
        rf.write("\n🎯 QUALITY METRICS:\n")
        rf.write(f"  • High Confidence (8-10): {qm.get('high_confidence', 0)} URLs\n")
        rf.write(f"  • Medium Confidence (5-7): {qm.get('medium_confidence', 0)} URLs\n")
        rf.write(f"  • Low Confidence (1-4): {qm.get('low_confidence', 0)} URLs\n")
        rf.write(f"  • Overall Quality Score: {qm.get('quality_score', 0):.2f}/3.0\n")

        rf.write("\n🏷️ CATEGORIES:\n")
        for category, count in (analysis.get("category_counts") or {}).items():
            rf.write(f"  • {category}: {count} URLs\n")

        rf.write("\n🌍 GEOGRAPHIC DISTRIBUTION:\n")
        for country, count in (analysis.get("country_counts") or {}).items():
            rf.write(f"  • {country}: {count} URLs\n")

        rf.write("\n🧹 DATA HYGIENE:\n")
        rf.write(f"  • Duplicates removed: {analysis.get('duplicates_removed', 0)}\n")
        rf.write(f"  • Invalid URLs skipped: {analysis.get('invalid_urls_skipped', 0)}\n")

        rf.write("\n🔝 TOP 20 HIGHEST CONFIDENCE URLs:\n")
        top = sorted(records, key=lambda r: r.confidence, reverse=True)[:20]
        for idx, r in enumerate(top, 1):
            rf.write(f"  {idx:2d}. {r.normalized_url or r.url} (confidence: {r.confidence})\n")

    # Manifest
    manifest = {
        "files": {k: os.path.relpath(v, start=os.path.dirname(out_paths["manifest"])) for k, v in out_paths.items()},
        "total": len(records),
    }
    with open(out_paths["manifest"], "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)

    return out_paths["csv"], out_paths["json"], out_paths["report"]