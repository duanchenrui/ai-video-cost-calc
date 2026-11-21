#!/usr/bin/env python3
"""
Automated FinOps Mathematical & Data Schema Golden Regression Tests
Run via `python3 -m unittest tests/test_finops_math.py` or in GitHub Actions CI.
Blocks deployment if any pricing anomaly or financial invariant breaks.
"""
import json
import math
import pathlib
import unittest

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data.json"

RES_COMPUTE_MULT = {"720p": 1.0, "1080p": 2.35, "4k": 5.4}
RES_ACT_VRAM_GB = {"720p": 2.5, "1080p": 5.5, "4k": 13.5}
VAE_TEXT_ENC_GB = 2.8


def optimize_kling_plan(raw_sec: float, res: str = "1080p"):
    cr_per_sec = {"720p": 14, "1080p": 22, "4k": 42}[res]
    req_cr = math.ceil(raw_sec * cr_per_sec)
    plans = [
        ("Standard", 10.0, 660),
        ("Pro", 37.0, 3000),
        ("Premier", 92.0, 8000),
    ]
    topup_per_1k = 15.0
    best_cost = float("inf")
    best_bought = 0
    for _, price, credits in plans:
        deficit = max(0, req_cr - credits)
        packs = math.ceil(deficit / 1000)
        cost_a = price + packs * topup_per_1k
        if cost_a < best_cost:
            best_cost = cost_a
            best_bought = credits + packs * 1000
        seats = max(1, math.ceil(req_cr / credits))
        cost_b = seats * price
        if cost_b < best_cost:
            best_cost = cost_b
            best_bought = seats * credits
    waste_pct = (max(0, best_bought - req_cr) / best_bought) * 100 if best_bought else 0.0
    return best_cost, waste_pct


def calc_cloud_gpu_tco(hourly_rate: float, speed_mult: float, vram_gb: float,
                       weight_vram_gb: float, num_5s_clips: float, res: str = "1080p",
                       is_spot: bool = True):
    peak_vram = weight_vram_gb + VAE_TEXT_ENC_GB + RES_ACT_VRAM_GB[res]
    cliff = 1.0
    if peak_vram > vram_gb:
        cliff = 5.5 if peak_vram <= vram_gb * 1.25 else 99.0
    clip_sec = (160.0 * RES_COMPUTE_MULT[res] * cliff) / speed_mult
    active_h = (num_5s_clips * clip_sec) / 3600.0
    cold_h = (20 * 4.0) / 60.0
    idle_h = active_h * 0.15
    preempt_h = active_h * (0.08 if is_spot else 0.0)
    storage_cost = 120 * 0.07
    total = (active_h + cold_h + idle_h + preempt_h) * hourly_rate + storage_cost
    return total, active_h, peak_vram, cliff


class TestFinOpsInvariants(unittest.TestCase):
    def test_data_json_schema_and_sanity_bounds(self):
        self.assertTrue(DATA_PATH.exists(), "data.json must exist")
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        self.assertIn("video_saas", data)
        self.assertIn("cloud_gpu", data)
        self.assertIn("local_hardware", data)
        for gpu in data["cloud_gpu"]:
            self.assertGreater(gpu["hourly_rate"], 0.05, f"Suspicious low GPU rate: {gpu['id']}")
            self.assertLess(gpu["hourly_rate"], 25.0, f"Suspicious high GPU rate: {gpu['id']}")
            self.assertGreaterEqual(gpu["vram_gb"], 8)
        for hw in data["local_hardware"]:
            self.assertGreater(hw["capex_usd"], 200)
            self.assertGreater(hw["watts_load"], 10)

    def test_saas_step_function_floor_and_waste(self):
        cost_small, waste_small = optimize_kling_plan(10, "1080p")
        self.assertGreaterEqual(cost_small, 10.0, "Cannot pay less than entry plan")
        self.assertGreater(waste_small, 50.0, "Small usage on discrete plan must show waste")
        self.assertLess(waste_small, 100.0)

        cost_med, _ = optimize_kling_plan(120, "1080p")
        cost_large, _ = optimize_kling_plan(600, "1080p")
        self.assertGreaterEqual(cost_med, cost_small)
        self.assertGreater(cost_large, cost_med)

    def test_cloud_gpu_hidden_tax_strictly_positive(self):
        total, active_h, _, _ = calc_cloud_gpu_tco(0.34, 1.0, 24, 15, 500, "1080p", is_spot=True)
        naive_cost = active_h * 0.34
        self.assertGreater(total, naive_cost * 1.20, "Hidden taxes (storage/cold/idle/spot) must exceed naive compute")

    def test_vram_swap_cliff_triggers_sharply(self):
        _, active_ok, _, cliff_ok = calc_cloud_gpu_tco(0.34, 1.0, 24, 15, 100, "1080p")
        _, active_cliff, _, cliff_hit = calc_cloud_gpu_tco(0.34, 1.0, 24, 15, 100, "4k")
        self.assertEqual(cliff_ok, 1.0)
        self.assertGreater(cliff_hit, 4.0, "4K on 24GB GPU with 15GB weights must trigger offload/OOM cliff")
        self.assertGreater(active_cliff, active_ok * 5.0)

    def test_nonlinear_resolution_scaling(self):
        self.assertGreater(RES_COMPUTE_MULT["1080p"], 2.0 * RES_COMPUTE_MULT["720p"])
        self.assertGreater(RES_COMPUTE_MULT["4k"], 2.0 * RES_COMPUTE_MULT["1080p"])


if __name__ == "__main__":
    unittest.main()
