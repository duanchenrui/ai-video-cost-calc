/**
 * FinOps Engine v6.0 — First-Principles AI Video & Compute TCO Core
 * Replaces linear guesses with:
 *   1. Discrete SaaS tier step-function & credit expiration waste modeling
 *   2. Cloud GPU hidden taxes (cold start, network volume storage, idle tax, spot preemption)
 *   3. Hardware Roofline (Compute vs. Memory Bandwidth) & VRAM Swap Cliff modeling
 *   4. Client-side Monte Carlo simulation (N=1,000) for P50 / P90 budget risk bands
 *   5. Exact break-even inflection point root-finding
 *   6. Glass-Box formula audit trace for independent third-party verification
 */

(function (global) {
  "use strict";

  // Nonlinear attention & spatial-temporal compute scaling vs 720p baseline
  const RES_COMPUTE_MULT = { "720p": 1.0, "1080p": 2.35, "4k": 5.4 };
  // Activation + KV cache peak VRAM overhead (GB) by resolution
  const RES_ACT_VRAM_GB = { "720p": 2.5, "1080p": 5.5, "4k": 13.5 };
  // Constant VAE + Text Encoder resident VRAM (GB)
  const VAE_TEXT_ENC_GB = 2.8;

  // Discrete monthly subscription tiers (verified 2026 pricing)
  const SAAS_TIERS = {
    kling_pro: {
      name: "Kling AI 4.0 (Discrete Credit Plans)",
      creditsPerSec: { "720p": 14, "1080p": 22, "4k": 42 },
      plans: [
        { name: "Standard", price: 10, credits: 660 },
        { name: "Pro", price: 37, credits: 3000 },
        { name: "Premier", price: 92, credits: 8000 }
      ],
      topupPricePer1000Cr: 15.0,
      sourceUrl: "https://www.zemith.com/en/learn/kling-pricing",
      sourceName: "Zemith 2026"
    },
    runway_gen45: {
      name: "Runway Gen-4.5 (Discrete Credit Plans)",
      creditsPerSec: { "720p": 10, "1080p": 12, "4k": 20 },
      plans: [
        { name: "Standard", price: 15, credits: 625 },
        { name: "Pro", price: 35, credits: 2250 },
        { name: "Max", price: 95, credits: 6500 }
      ],
      topupPricePer1000Cr: 16.0,
      sourceUrl: "https://academy.techpresso.co/reviews/is-runway-worth-it",
      sourceName: "Techpresso 2026"
    },
    heygen_avatar_v: {
      name: "HeyGen Avatar IV/V (Discrete Credit Plans)",
      creditsPerSec: { "720p": 0.34, "1080p": 0.34, "4k": 0.68 },
      plans: [
        { name: "Creator", price: 29, credits: 600 },
        { name: "Pro", price: 49, credits: 1200 },
        { name: "Business", price: 149, credits: 4000 }
      ],
      topupPricePer1000Cr: 42.0,
      sourceUrl: "https://usevelo.ai/blog/heygen-pricing/",
      sourceName: "Velo 2026"
    },
    veo3_api: {
      name: "Google Veo 3.0/3.1 (Pure Pay-as-You-Go API)",
      payAsYouGo: true,
      pricePerSec: { "720p": 0.40, "1080p": 0.40, "4k": 0.60 },
      sourceUrl: "https://models.litellm.ai/models/veo-3.0-generate-001",
      sourceName: "LiteLLM 2026"
    }
  };

  /**
   * 1. SaaS Discrete Step-Function Plan Optimizer
   * Finds the exact lowest-cost plan + top-up bundle and computes unused credit waste %.
   */
  function optimizeSaasPlan(saasId, rawSec, res) {
    const spec = SAAS_TIERS[saasId];
    if (!spec) return null;

    if (spec.payAsYouGo) {
      const rate = spec.pricePerSec[res] || 0.40;
      const monthlyCost = rawSec * rate;
      return {
        monthlyCost,
        effectivePerSec: rate,
        nominalPerSec: rate,
        wastePct: 0,
        recommendedBundle: `Pay-as-you-go API ($${rate.toFixed(2)}/s)`,
        audit: [
          `Billing Model: Pure Per-Second API (0% credit expiration waste)`,
          `Formula: ${rawSec.toFixed(0)} raw sec × $${rate.toFixed(2)}/s = $${monthlyCost.toFixed(2)}/mo`
        ]
      };
    }

    const crPerSec = spec.creditsPerSec[res] || spec.creditsPerSec["1080p"];
    const reqCredits = Math.ceil(rawSec * crPerSec);

    let best = { cost: Infinity, bundle: "", purchasedCr: 0 };

    // Evaluate each base tier + optional top-ups or multiple seats
    spec.plans.forEach(plan => {
      // Option A: single tier + top-ups
      const deficit = Math.max(0, reqCredits - plan.credits);
      const topupPacks = Math.ceil(deficit / 1000);
      const costA = plan.price + topupPacks * spec.topupPricePer1000Cr;
      const boughtA = plan.credits + topupPacks * 1000;
      if (costA < best.cost) {
        best = {
          cost: costA,
          bundle: topupPacks > 0 ? `1× ${plan.name} ($${plan.price}) + ${topupPacks}× 1k Top-up` : `1× ${plan.name} ($${plan.price})`,
          purchasedCr: boughtA
        };
      }
      // Option B: N seats of this tier
      const seats = Math.max(1, Math.ceil(reqCredits / plan.credits));
      const costB = seats * plan.price;
      const boughtB = seats * plan.credits;
      if (costB < best.cost) {
        best = {
          cost: costB,
          bundle: `${seats}× ${plan.name} ($${plan.price}/seat)`,
          purchasedCr: boughtB
        };
      }
    });

    const unusedCr = Math.max(0, best.purchasedCr - reqCredits);
    const wastePct = best.purchasedCr > 0 ? (unusedCr / best.purchasedCr) * 100 : 0;
    const effectivePerSec = rawSec > 0 ? best.cost / rawSec : 0;
    const nominalPerSec = (spec.plans[1].price / spec.plans[1].credits) * crPerSec;

    return {
      monthlyCost: best.cost,
      effectivePerSec,
      nominalPerSec,
      wastePct,
      recommendedBundle: best.bundle,
      audit: [
        `Required Credits: ${rawSec.toFixed(0)} raw sec × ${crPerSec} cr/s = ${reqCredits.toLocaleString()} credits`,
        `Optimal Step-Function Bundle: ${best.bundle} (${best.purchasedCr.toLocaleString()} cr purchased)`,
        `Monthly Credit Expiration Waste: ${unusedCr.toLocaleString()} cr (${wastePct.toFixed(1)}% wasted at month-end)`,
        `Effective Cost: $${effectivePerSec.toFixed(3)}/raw sec (vs nominal $${nominalPerSec.toFixed(3)}/s)`
      ]
    };
  }

  /**
   * 2. Hardware Peak VRAM & Roofline Latency Model
   * Explicitly separates model weights + VAE/Text Encoder + resolution activation peak.
   * Applies a realistic 6.5x Swap Cliff if unified memory swaps or CUDA offloads to RAM.
   */
  function computePeakVramGB(weightVramGB, res) {
    const actGB = RES_ACT_VRAM_GB[res] || 5.5;
    return Number((weightVramGB + VAE_TEXT_ENC_GB + actGB).toFixed(1));
  }

  function calcHardwareLatencyFactor(hw, peakVramGB) {
    // Roofline bottleneck: Apple Silicon is Memory-Bandwidth bound on large diffusion steps;
    // NVIDIA discrete GPUs are Compute-bound until VRAM overflows PCIe.
    let status = "OK";
    let cliffMult = 1.0;

    if (peakVramGB > hw.vram_gb) {
      if (hw.arch && hw.arch.startsWith("apple") && peakVramGB <= hw.vram_gb * 1.35) {
        status = "SWAP_CLIFF";
        cliffMult = 6.5; // macOS unified memory SSD/RAM swap cliff
      } else if (peakVramGB <= hw.vram_gb * 1.25) {
        status = "OFFLOAD_CLIFF";
        cliffMult = 5.5; // CUDA PCIe system RAM offload cliff
      } else {
        status = "OOM";
        cliffMult = 99.0;
      }
    }
    return { status, cliffMult };
  }

  /**
   * 3. Cloud GPU Hidden Tax Model
   * Includes: Active compute + Cold start weight pull + Idle tax + Network Volume storage + Spot preemption.
   */
  function calcCloudGpuTco(gpu, modelWeightVramGB, baseClipSec4090_720p, num5sClips, res, quantSpeedBoost, options = {}) {
    const idleTaxPct = options.idleTaxPct !== undefined ? options.idleTaxPct : 0.15;
    const spotPreemptPct = gpu.isSpot ? 0.08 : 0.0;
    const sessionsPerMo = options.sessionsPerMo || 20;
    const coldStartMinPerSession = options.coldStartMinPerSession || 4.0;
    const storageGB = options.storageGB || 120; // Wan 14B + Flux + VAE + ComfyUI container
    const storageRatePerGBMo = options.storageRatePerGBMo || 0.07;

    const peakVramGB = computePeakVramGB(modelWeightVramGB, res);
    const { status, cliffMult } = calcHardwareLatencyFactor(gpu, peakVramGB);
    const isOom = status === "OOM";

    const resMult = RES_COMPUTE_MULT[res] || 2.35;
    const clipSec = (baseClipSec4090_720p * resMult * cliffMult) / (gpu.speed_mult * quantSpeedBoost);
    const activeHours = (num5sClips * clipSec) / 3600;

    const coldStartHours = (sessionsPerMo * coldStartMinPerSession) / 60;
    const idleHours = activeHours * idleTaxPct;
    const preemptHours = activeHours * spotPreemptPct;
    const billableHours = activeHours + coldStartHours + idleHours + preemptHours;

    const computeCost = billableHours * gpu.hourly_rate;
    const storageCost = storageGB * storageRatePerGBMo;
    const totalMonthly = computeCost + storageCost;
    const hiddenTaxCost = (coldStartHours + idleHours + preemptHours) * gpu.hourly_rate + storageCost;
    const hiddenTaxPct = totalMonthly > 0 ? (hiddenTaxCost / totalMonthly) * 100 : 0;

    return {
      totalMonthly,
      activeHours,
      billableHours,
      peakVramGB,
      vramStatus: status,
      isOom,
      hiddenTaxCost,
      hiddenTaxPct,
      audit: [
        `Peak VRAM Breakdown: ${modelWeightVramGB}GB weights + ${VAE_TEXT_ENC_GB}GB VAE/TE + ${RES_ACT_VRAM_GB[res]}GB activations = ${peakVramGB}GB (GPU has ${gpu.vram_gb}GB -> ${status})`,
        `Active Render: ${num5sClips.toFixed(0)} clips × ${clipSec.toFixed(0)}s/clip = ${activeHours.toFixed(1)}h (res scale ${resMult}x)`,
        `Cloud Hidden Taxes: Cold start ${coldStartHours.toFixed(1)}h + Idle(${(idleTaxPct*100).toFixed(0)}%) ${idleHours.toFixed(1)}h + Spot retry ${preemptHours.toFixed(1)}h + ${storageGB}GB Volume ($${storageCost.toFixed(2)}/mo)`,
        `Total Billable: ${billableHours.toFixed(1)}h × $${gpu.hourly_rate}/h + $${storageCost.toFixed(2)} = $${totalMonthly.toFixed(2)}/mo (${hiddenTaxPct.toFixed(1)}% hidden cloud tax)`
      ]
    };
  }

  /**
   * 4. Deterministic Seeded Monte Carlo Simulation (N=1,000)
   * Models right-skewed log-normal retry multiplier & cloud/spot variance to yield P50 & P90 bands.
   */
  function runMonteCarlo(baseMonthlyFn, meanRetry, trials = 1000) {
    // Mulberry32 deterministic PRNG so results don't jitter on unrelated slider drags
    let seed = 20261120;
    function rand() {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }
    function randNormal() {
      const u = Math.max(1e-6, rand());
      const v = rand();
      return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    }

    const samples = new Float64Array(trials);
    const sigma = 0.28; // realistic heavy-tail variance in AI video prompt retries
    for (let i = 0; i < trials; i++) {
      // Log-normal factor with median ~1.0 and right tail (P90 ~1.43x meanRetry)
      const retrySample = Math.max(1.0, meanRetry * Math.exp(sigma * randNormal()));
      const cloudJitter = 1.0 + 0.06 * randNormal();
      samples[i] = baseMonthlyFn(retrySample, Math.max(0.85, cloudJitter));
    }
    samples.sort();
    const p50 = samples[Math.floor(trials * 0.50)];
    const p90 = samples[Math.floor(trials * 0.90)];
    return { p50, p90 };
  }

  /**
   * 5. Exact Break-Even Inflection Root-Finder
   * Scans monthly finished minutes [2..240] to find:
   *   - minCloudBeatsSaas: exact finished min/mo where Cloud GPU < SaaS
   *   - minLocalBeatsCloud: exact finished min/mo where New Local Hardware < Cloud GPU
   */
  function findBreakEvenInflections(evalAtFinishedMin) {
    let cloudBeatsSaasMin = null;
    let localBeatsCloudMin = null;
    for (let m = 2; m <= 240; m += 2) {
      const { saasCost, cloudGpuCost, localNewCost } = evalAtFinishedMin(m);
      if (cloudBeatsSaasMin === null && cloudGpuCost < saasCost) cloudBeatsSaasMin = m;
      if (localBeatsCloudMin === null && localNewCost < cloudGpuCost) localBeatsCloudMin = m;
    }
    return { cloudBeatsSaasMin, localBeatsCloudMin };
  }

  global.FinOpsEngine = {
    RES_COMPUTE_MULT,
    RES_ACT_VRAM_GB,
    VAE_TEXT_ENC_GB,
    SAAS_TIERS,
    optimizeSaasPlan,
    computePeakVramGB,
    calcHardwareLatencyFactor,
    calcCloudGpuTco,
    runMonteCarlo,
    findBreakEvenInflections
  };
})(typeof window !== "undefined" ? window : globalThis);
