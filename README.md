# AI Video & Local Compute TCO Engine (v3.0 天花板版)

这个目录包含 **A（多机异构硬件/云算力测算）+ C（全模态 AI 视频生成真实单分钟成本）** 的终极版 GEO 交互工具站。

## 核心功能矩阵（v3.0 已全部实装）
1. **双模式切换**：
   - **⚡ 快速设置模式**：10 秒标准预设（个人带货 / 漫剧工作室 / MCN 矩阵量产）。
   - **🛠️ 专家全矩阵模式**：支持多机异构集群（Mac Studio + Mac mini + RTX 显卡混搭，区分「已有 0 折旧」与「新购算折旧」）、二手残值率抵扣（默认 45%）、ComfyUI 队列并联 vs Exo 跨机内存池化。
2. **⚡ 智能云地混合路由（Hybrid Cloud+Local） & AI 一键寻优**：
   - 支持按百分比切分「本地主力挂机 + 云端 RunPod / Kling / Veo 3 弹性削峰」。
   - 点击顶部 **「✨ AI 一键寻优」**，系统自动根据你设定的「日均最大允许挂机时长（SLA）」算出不爆显存、不延期的最低成本混合配比。
3. **全模态前后期成本叠加（Full Pipeline Stack）**：
   - 一键勾选叠加 `LLM 剧本/分镜` + `Flux 角色首帧` + `AI 配音/音效` + `4K 超分插帧`。
4. **📈 24 个月累计现金流回本曲线（SVG 动态折线图）**：
   - 直观对比 0~24 个月内「纯 SaaS 订阅 vs 云 GPU 租赁 vs 本地硬件（扣二手残值后首付+月电费）」的资金交叉回本点。
5. **💱 USD / CNY 双币种切换 + 🔗 URL 状态持久分享 + 📋 一键生成立项书与 ComfyUI 分布式启动脚本**。
6. **🤖 Programmatic GEO 页面裂变脚本（`build_geo_matrix.py`）**：
   - 运行 `python3 build_geo_matrix.py` 自动生成 `./compare/*.html` 长尾对比落地页矩阵与 `sitemap.xml`。
