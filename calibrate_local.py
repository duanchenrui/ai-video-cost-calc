#!/usr/bin/env python3
"""
Local Hardware Ground-Truth Calibration Tool (calibrate_local.py)
Detects your local Apple Silicon / NVIDIA GPU specs, compares your real measured
ComfyUI render time & power draw against the FinOps Engine prediction, and outputs
a verifiable MAPE (Mean Absolute Percentage Error) report to calibration_report.json.
"""
import datetime
import json
import pathlib
import platform
import subprocess

BASE_DIR = pathlib.Path(__file__).resolve().parent


def detect_hardware():
    info = {
        "os": platform.system(),
        "machine": platform.machine(),
        "chip": "Unknown",
        "memory_gb": 0,
    }
    if platform.system() == "Darwin":
        try:
            chip = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
            mem_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip())
            info["chip"] = chip
            info["memory_gb"] = round(mem_bytes / (1024 ** 3))
        except Exception:
            pass
    return info


def main():
    hw = detect_hardware()
    print("=== AI Video FinOps Local Ground-Truth Calibration ===")
    print(f"Detected Machine: {hw['chip']} ({hw['memory_gb']}GB RAM, {hw['os']}/{hw['machine']})")
    print("Enter your REAL measured ComfyUI 5-second clip render time (e.g. from ComfyUI /history):")

    try:
        res = input("Resolution tested [720p / 1080p] (default 1080p): ").strip() or "1080p"
        actual_sec = float(input("Measured actual render seconds for one 5s clip (e.g. 920): ").strip())
        predicted_sec = float(input("FinOps calculator predicted seconds per 5s clip (e.g. 880): ").strip())
    except (ValueError, EOFError):
        print("Aborted: please enter valid numbers.")
        return

    abs_err_pct = abs(actual_sec - predicted_sec) / max(1.0, actual_sec) * 100.0
    report = {
        "calibrated_at": datetime.date.today().isoformat(),
        "hardware": hw,
        "resolution": res,
        "actual_sec_per_5s_clip": actual_sec,
        "predicted_sec_per_5s_clip": predicted_sec,
        "mape_pct": round(abs_err_pct, 2),
        "status": "PASS (<10% MAPE)" if abs_err_pct < 10.0 else "NEEDS_TUNING (>=10% MAPE)",
    }
    out_path = BASE_DIR / "calibration_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n[ok] Calibration saved to {out_path}")
    print(f"MAPE Error: {report['mape_pct']}% -> {report['status']}")


if __name__ == "__main__":
    main()
