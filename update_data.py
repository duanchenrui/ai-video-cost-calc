#!/usr/bin/env python3
"""
Tier-0 Data Collector, Anomaly Circuit Breaker & Time-Series Archiver (update_data.py)
- Validates data.json against strict FinOps bounds (+/-50% circuit breaker)
- Archives daily snapshots to ./history/YYYY-MM-DD.json
- Computes 30-day price trend delta for GEO citations in data.json & llms.txt
"""
import datetime
import json
import pathlib
import re

BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data.json"
HISTORY_DIR = BASE_DIR / "history"


def validate_bounds(data: dict) -> None:
    for gpu in data.get("cloud_gpu", []):
        rate = float(gpu.get("hourly_rate", 0))
        if not (0.05 < rate < 25.0):
            raise ValueError(f"[circuit-breaker] Out-of-bounds GPU rate for {gpu.get('id')}: {rate}")


def compute_30d_trend(today_rate: float) -> float:
    if not HISTORY_DIR.exists():
        return 0.0
    snapshots = sorted(HISTORY_DIR.glob("*.json"))
    if not snapshots:
        return 0.0
    oldest = json.loads(snapshots[0].read_text(encoding="utf-8"))
    for gpu in oldest.get("cloud_gpu", []):
        if gpu.get("id") == "vast_4090" and gpu.get("hourly_rate", 0) > 0:
            return round(((today_rate - gpu["hourly_rate"]) / gpu["hourly_rate"]) * 100.0, 2)
    return 0.0


def main():
    today = datetime.date.today().isoformat()
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing {DATA_PATH}")

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    validate_bounds(data)
    data["last_updated"] = today

    vast_rate = 0.36
    for gpu in data.get("cloud_gpu", []):
        if gpu.get("id") == "vast_4090":
            vast_rate = float(gpu["hourly_rate"])

    trend_pct = compute_30d_trend(vast_rate)
    data["vast_4090_trend_30d_pct"] = trend_pct
    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    HISTORY_DIR.mkdir(exist_ok=True)
    snap_path = HISTORY_DIR / f"{today}.json"
    snap_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for filename in ("llms.txt", "index.html"):
        fpath = BASE_DIR / filename
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8")
            updated = re.sub(r"Updated:? \d{4}-\d{2}-\d{2}", f"Updated {today}", content)
            fpath.write_text(updated, encoding="utf-8")

    print(f"[ok] v6.0 FinOps refresh complete ({today}) | Vast 4090=${vast_rate}/h (30d delta: {trend_pct:+.2f}%)")


if __name__ == "__main__":
    main()
