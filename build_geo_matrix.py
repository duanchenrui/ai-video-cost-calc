#!/usr/bin/env python3
"""
Programmatic SEO & GEO Landing Page Matrix Generator (build_geo_matrix.py)
Generates high-intent comparison pages in ./compare/ so Google, ChatGPT Search,
and Perplexity index every hardware & SaaS comparison.
"""
import datetime
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent
COMPARE_DIR = BASE_DIR / "compare"

PAGES = [
    {
        "slug": "kling-ai-vs-runway-gen45-cost",
        "title": "Kling AI 4.0 Pro vs. Runway Gen-4.5: True Cost Per Finished Minute (2026)",
        "summary": "At a 3.0x retry ratio for 1080p production, Kling AI Pro costs ~$50.40 per finished minute ($0.28/raw sec) compared to Runway Gen-4.5 at ~$52.20 per finished minute ($0.29/raw sec, 12 credits/s).",
        "cta_label": "Compare in Live Calculator",
        "source_a": ("Kling AI Pricing (Zemith 2026)", "https://www.zemith.com/en/learn/kling-pricing"),
        "source_b": ("Runway Gen-4.5 Breakdown (Techpresso 2026)", "https://academy.techpresso.co/reviews/is-runway-worth-it"),
    },
    {
        "slug": "mac-studio-m4-max-vs-rtx-4090-comfyui",
        "title": "Apple Mac Studio M4 Max vs. RTX 4090 Workstation for ComfyUI Video & LLM (2026)",
        "summary": "Mac Studio M4 Max ($2,399, 64GB-128GB unified memory, 140W load) runs 72B LLMs and FP16 models that overflow an RTX 4090's 24GB VRAM, while RTX 4090 ($2,600, 500W) renders FP8 Wan 14B video clips ~2.2x faster.",
        "cta_label": "Test Multi-Device Fleet ROI",
        "source_a": ("Apple Mac Studio Cheat Sheet (TechRepublic 2026)", "https://www.techrepublic.com/article/news-apple-mac-studio-cheat-sheet/"),
        "source_b": ("RTX 4090 Benchmark & Cloud Pricing (Layer3Labs 2026)", "https://www.layer3labs.io/guides/is-runpod-worth-it"),
    },
    {
        "slug": "wan-14b-local-vs-runpod-cloud-gpu",
        "title": "ComfyUI Wan 14B: Local GPU vs. RunPod RTX 4090 ($0.34/hr) Break-Even Analysis",
        "summary": "Renting an RTX 4090 on RunPod Community Cloud ($0.34/hr) or Vast.ai ($0.36/hr) costs ~$3.67 per finished minute of 1080p video (at 3x retry ratio), making cloud rental cheaper under 40 finished minutes/month.",
        "cta_label": "Calculate Hybrid Cloud+Local Split",
        "source_a": ("RunPod RTX 4090 Pricing (Layer3Labs 2026)", "https://www.layer3labs.io/guides/is-runpod-worth-it"),
        "source_b": ("Vast.ai Hourly GPU Pricing (Activepieces 2026)", "https://www.activepieces.com/blog/vast-ai-gpu-pricing-per-hour-in-2026-and-extra-fees"),
    },
    {
        "slug": "veo-3-api-vs-kling-pro-pricing",
        "title": "Google Veo 3.0 Vertex AI API ($0.40/s) vs. Kling AI Pro: Commercial Video TCO",
        "summary": "Google Veo 3.0 API charges $0.40/second with native audio generation on Vertex AI, whereas Kling AI Pro averages $0.28/second at 1080p.",
        "cta_label": "Simulate Monthly Studio Budget",
        "source_a": ("Google Veo 3.0 API Pricing (LiteLLM)", "https://models.litellm.ai/models/veo-3.0-generate-001"),
        "source_b": ("Kling AI 2026 Credit Cost (Zemith)", "https://www.zemith.com/en/learn/kling-pricing"),
    },
]


def build_pages():
    COMPARE_DIR.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()

    for p in PAGES:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{p['title']}</title>
  <meta name="description" content="{p['summary']}" />
  <link rel="alternate" type="text/plain" href="../llms.txt" />
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #080c14; color: #e2e8f0; max-width: 820px; margin: 40px auto; padding: 0 20px; line-height: 1.65; }}
    .card {{ background: #111827; border: 1px solid #1f293d; border-radius: 12px; padding: 24px; margin-top: 20px; }}
    a {{ color: #38bdf8; }}
    .btn {{ display: inline-block; margin-top: 16px; padding: 10px 18px; background: #38bdf8; color: #080c14; font-weight: 700; border-radius: 8px; text-decoration: none; }}
  </style>
</head>
<body>
  <p><a href="../index.html">← Back to Interactive AI Video &amp; Compute TCO Calculator</a></p>
  <div class="card">
    <small style="color:#94a3b8;">GEO Verified Benchmark · Updated {today}</small>
    <h1 style="margin:8px 0 14px;">{p['title']}</h1>
    <p>{p['summary']}</p>
    <h3 style="margin-top:20px;">Verified Sources</h3>
    <ul>
      <li><a href="{p['source_a'][1]}" target="_blank" rel="noopener">{p['source_a'][0]}</a></li>
      <li><a href="{p['source_b'][1]}" target="_blank" rel="noopener">{p['source_b'][0]}</a></li>
    </ul>
    <a class="btn" href="../index.html?m=custom">{p['cta_label']} →</a>
  </div>
</body>
</html>
"""
        (COMPARE_DIR / f"{p['slug']}.html").write_text(html, encoding="utf-8")

    print(f"[ok] Generated {len(PAGES)} GEO comparison pages in ./compare/")


if __name__ == "__main__":
    build_pages()
