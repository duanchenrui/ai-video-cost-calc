#!/usr/bin/env python3
"""
Daily Timestamp & Benchmark Refresher for ComputeVideoCost.ai
Updates the last_updated date in data.json, llms.txt, and index.html.
"""
import datetime
import json
import pathlib
import re

BASE_DIR = pathlib.Path(__file__).resolve().parent

def main():
    today = datetime.date.today().isoformat()

    data_path = BASE_DIR / "data.json"
    if data_path.exists():
        data = json.loads(data_path.read_text(encoding="utf-8"))
        data["last_updated"] = today
        data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for filename in ("llms.txt", "index.html"):
        fpath = BASE_DIR / filename
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8")
            updated = re.sub(r"Updated:? \d{4}-\d{2}-\d{2}", f"Updated {today}", content)
            fpath.write_text(updated, encoding="utf-8")

    print(f"[ok] Refreshed GEO timestamps to {today}")

if __name__ == "__main__":
    main()
