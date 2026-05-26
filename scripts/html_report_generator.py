"""
HTML Report Generator v3.0
===========================

生成包含 Chart.js 交互图表的15章深度可视化选品调研报告。
风格: 简洁商务科技风 (深色主题 + 蓝色科技色调)

v3.0 新增:
- 消费者画像（消费者分层漏斗图）
- 五维趋势交叉验证（5维度雷达图+一致性矩阵）
- 市场容量筛选（成分×剂型十字热力图）
- 产品生命周期定位（阶段判定图+策略矩阵）
- 研发壁垒构建（5类壁垒评分雷达图）
- 风险评估与"为什么不选"（虚假蓝海检测+风险矩阵）
- 90天执行路线图（甘特图/里程碑时间线）
- 每章数据溯源标注（可折叠 Data Lineage）

Chart.js 集成图表:
- Line: Google Trends 关键词趋势
- Doughnut/Pie: TikTok 内容分布, Reddit 情绪, 痛点分类
- Bar: 标签热度, 价格分布, 高频关键词
- Bubble: 竞争格局散点图
- Radar: 市场机会评分 (8维度)
- WordCloud: 痛点词云 (wordcloud2.js)

依赖:
- Chart.js 4.x (CDN)
- chartjs-plugin-annotation (CDN)
- wordcloud2.js (CDN)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from config import REPORT_CONFIG
from charts_generator import ChartsGenerator


class HTMLReportGenerator:
    """HTML 可视化报告生成器"""

    def __init__(self, data: dict, output_dir: Path):
        self.data = data
        self.metadata = data.get("metadata", {})
        self.output_dir = Path(output_dir)
        self.report_config = REPORT_CONFIG
        self.charts_gen = ChartsGenerator(data)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self) -> Path:
        """生成完整 HTML 报告"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        category = self.metadata.get("category", "report").replace(" ", "_")
        filename = f"{timestamp}_{category}_report.html"
        filepath = self.output_dir / filename

        html = self._build_html()

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        return filepath

    def _build_html(self) -> str:
        """构建完整 HTML 文档"""
        charts_data = self.charts_gen.generate_all_charts()
        diff_suggestions = self.charts_gen.generate_differentiation_suggestions()
        charts_json = json.dumps(charts_data, ensure_ascii=False)
        diff_json = json.dumps(diff_suggestions, ensure_ascii=False)

        market = self.metadata.get("market", "US")
        category = self.metadata.get("category", "Product")
        gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category} - {market} 选品调研报告 | Amazon Product Research</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/wordcloud2.js@1.0.2/src/wordcloud2.min.js"></script>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-card: #1c2128;
            --bg-elevated: #21262d;
            --border: #30363d;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-orange: #f0883e;
            --accent-purple: #bc8cff;
            --accent-red: #f85149;
            --accent-cyan: #79c0ff;
            --gradient-hero: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1a2332 100%);
            --shadow-card: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
            --shadow-elevated: 0 4px 12px rgba(0,0,0,0.4);
            --radius: 8px;
            --radius-lg: 12px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}

        /* ====== Hero Header ====== */
        .hero {{
            background: var(--gradient-hero);
            border-bottom: 1px solid var(--border);
            padding: 48px 32px;
            text-align: center;
        }}
        .hero-badge {{
            display: inline-block;
            background: rgba(88,166,255,0.15);
            border: 1px solid rgba(88,166,255,0.3);
            color: var(--accent-blue);
            padding: 4px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 16px;
            letter-spacing: 0.5px;
        }}
        .hero h1 {{
            font-size: 36px;
            font-weight: 700;
            color: #f0f6fc;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        .hero-subtitle {{
            font-size: 16px;
            color: var(--text-secondary);
            margin-bottom: 24px;
        }}
        .hero-meta {{
            display: flex;
            justify-content: center;
            gap: 24px;
            flex-wrap: wrap;
        }}
        .hero-meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--text-secondary);
            font-size: 14px;
            background: var(--bg-elevated);
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid var(--border);
        }}
        .hero-meta-item .icon {{ font-size: 16px; }}

        /* ====== Container & Grid ====== */
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 32px 24px;
        }}

        /* ====== KPI Dashboard ====== */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 40px;
        }}
        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 20px 24px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: border-color 0.2s, transform 0.2s;
        }}
        .kpi-card:hover {{
            border-color: var(--accent-blue);
            transform: translateY(-2px);
            box-shadow: var(--shadow-elevated);
        }}
        .kpi-label {{
            font-size: 12px;
            font-weight: 500;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .kpi-value {{
            font-size: 32px;
            font-weight: 700;
            color: #f0f6fc;
            letter-spacing: -1px;
        }}
        .kpi-change {{
            font-size: 13px;
            font-weight: 500;
        }}
        .kpi-change.up {{ color: var(--accent-green); }}
        .kpi-change.down {{ color: var(--accent-red); }}

        /* ====== Section ====== */
        .section {{
            margin-bottom: 48px;
        }}
        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }}
        .section-icon {{
            font-size: 24px;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 600;
            color: #f0f6fc;
        }}
        .section-subtitle {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-left: auto;
        }}

        /* ====== Chart Card ====== */
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }}
        .chart-grid.triple {{
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        }}
        .chart-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            transition: border-color 0.2s;
        }}
        .chart-card:hover {{
            border-color: rgba(88,166,255,0.3);
        }}
        .chart-card.full-width {{
            grid-column: 1 / -1;
        }}
        .chart-card-title {{
            font-size: 16px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 4px;
        }}
        .chart-card-subtitle {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 20px;
        }}
        .chart-container {{
            position: relative;
            width: 100%;
        }}
        .chart-container canvas {{
            width: 100% !important;
        }}

        /* ====== Tables ====== */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        .data-table thead th {{
            background: var(--bg-elevated);
            color: var(--text-secondary);
            font-weight: 600;
            text-align: left;
            padding: 12px 16px;
            border-bottom: 2px solid var(--border);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .data-table tbody td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
        }}
        .data-table tbody tr:hover {{
            background: rgba(88,166,255,0.04);
        }}
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-high {{ background: rgba(63,185,80,0.15); color: var(--accent-green); }}
        .badge-medium {{ background: rgba(240,136,62,0.15); color: var(--accent-orange); }}
        .badge-low {{ background: rgba(248,81,73,0.15); color: var(--accent-red); }}

        /* ====== Differentiation Section ====== */
        .diff-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 16px;
        }}
        .diff-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            position: relative;
            overflow: hidden;
            transition: border-color 0.2s, transform 0.2s;
        }}
        .diff-card:hover {{
            border-color: var(--accent-blue);
            transform: translateY(-2px);
            box-shadow: var(--shadow-elevated);
        }}
        .diff-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-blue);
            border-radius: 2px 0 0 2px;
        }}
        .diff-rank {{
            position: absolute;
            top: 16px;
            right: 20px;
            font-size: 48px;
            font-weight: 800;
            color: rgba(88,166,255,0.08);
            line-height: 1;
        }}
        .diff-category {{
            font-size: 12px;
            font-weight: 500;
            color: var(--accent-purple);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        .diff-direction {{
            font-size: 18px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 8px;
        }}
        .diff-detail {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 12px;
            line-height: 1.6;
        }}
        .diff-action {{
            font-size: 13px;
            color: var(--accent-cyan);
            background: rgba(121,192,255,0.08);
            padding: 8px 12px;
            border-radius: 6px;
            border-left: 3px solid var(--accent-cyan);
        }}
        .diff-score {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 14px;
            font-weight: 600;
            color: var(--accent-green);
            margin-top: 12px;
        }}

        /* ====== Insights Box ====== */
        .insight-box {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            margin-bottom: 20px;
        }}
        .insight-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }}
        .insight-item:last-child {{ border-bottom: none; }}
        .insight-icon {{
            font-size: 18px;
            flex-shrink: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
        }}
        .insight-icon.positive {{ background: rgba(63,185,80,0.1); }}
        .insight-icon.warning {{ background: rgba(240,136,62,0.1); }}
        .insight-icon.danger {{ background: rgba(248,81,73,0.1); }}
        .insight-text strong {{ color: #f0f6fc; }}
        .insight-text p {{ color: var(--text-secondary); font-size: 13px; margin-top: 4px; }}

        /* ====== Footer ====== */
        .footer {{
            border-top: 1px solid var(--border);
            padding: 32px 24px;
            text-align: center;
            color: var(--text-muted);
            font-size: 13px;
        }}
        .footer a {{ color: var(--accent-blue); text-decoration: none; }}

        /* ====== Data Lineage (v3.0 NEW) ====== */
        .data-lineage {{
            margin-top: 16px;
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0;
            font-size: 12px;
        }}
        .data-lineage summary {{
            padding: 10px 16px;
            color: var(--text-muted);
            cursor: pointer;
            font-weight: 500;
            user-select: none;
            letter-spacing: 0.3px;
        }}
        .data-lineage summary:hover {{
            color: var(--accent-blue);
        }}
        .data-lineage .lineage-content {{
            padding: 0 16px 12px 16px;
            color: var(--text-secondary);
            font-style: italic;
            line-height: 1.7;
        }}
        .data-lineage .lineage-content ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .data-lineage .lineage-content li {{
            padding: 2px 0;
        }}
        .data-lineage .lineage-content li::before {{
            content: '📌 ';
            font-style: normal;
        }}

        /* ====== Risk Matrix (v3.0 NEW) ====== */
        .risk-matrix-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
        }}
        .risk-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 16px;
        }}
        .risk-card.high {{ border-left: 3px solid var(--accent-red); }}
        .risk-card.medium {{ border-left: 3px solid var(--accent-orange); }}
        .risk-card.low {{ border-left: 3px solid var(--accent-green); }}
        .risk-card-title {{
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 4px;
        }}
        .risk-card-desc {{
            font-size: 13px;
            color: var(--text-secondary);
        }}

        /* ====== Why Not Section (v3.0 NEW) ====== */
        .why-not-box {{
            background: rgba(248,81,73,0.06);
            border: 1px solid rgba(248,81,73,0.2);
            border-radius: var(--radius-lg);
            padding: 24px;
            margin-top: 16px;
        }}
        .why-not-item {{
            display: flex;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }}
        .why-not-item:last-child {{ border-bottom: none; }}
        .why-not-icon {{
            font-size: 20px;
            flex-shrink: 0;
        }}
        .why-not-text strong {{
            color: var(--accent-red);
            font-size: 15px;
        }}
        .why-not-text p {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        /* ====== Execution Roadmap Timeline (v3.0 NEW) ====== */
        .roadmap-timeline {{
            display: flex;
            gap: 16px;
            overflow-x: auto;
            padding: 8px 0;
        }}
        .roadmap-phase {{
            flex: 1;
            min-width: 200px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 20px;
            position: relative;
        }}
        .roadmap-phase.active {{ border-color: var(--accent-blue); }}
        .roadmap-phase-number {{
            font-size: 24px;
            font-weight: 800;
            color: var(--accent-blue);
            opacity: 0.3;
            margin-bottom: 8px;
        }}
        .roadmap-phase-title {{
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 4px;
        }}
        .roadmap-phase-time {{
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}
        .roadmap-phase ul {{
            list-style: none;
            padding: 0;
        }}
        .roadmap-phase li {{
            font-size: 13px;
            color: var(--text-secondary);
            padding: 4px 0;
            padding-left: 12px;
            position: relative;
        }}
        .roadmap-phase li::before {{
            content: '▸';
            position: absolute;
            left: 0;
            color: var(--accent-blue);
        }}

        /* ====== WordCloud Canvas ====== */
        #wordcloud-canvas {{
            width: 100%;
            height: 400px;
            border-radius: 8px;
        }}

        /* ====== Responsive ====== */
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 24px; }}
            .chart-grid {{ grid-template-columns: 1fr; }}
            .chart-grid.triple {{ grid-template-columns: 1fr; }}
            .diff-grid {{ grid-template-columns: 1fr; }}
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}

        /* ====== Scrollbar ====== */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-primary); }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}

        /* Tab Navigation */
        .tab-nav {{
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
            background: var(--bg-secondary);
            padding: 4px;
            border-radius: 8px;
            overflow-x: auto;
        }}
        .tab-btn {{
            padding: 8px 16px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-family: inherit;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            border-radius: 6px;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{ color: var(--text-primary); background: var(--bg-elevated); }}
        .tab-btn.active {{ background: var(--accent-blue); color: #fff; }}
    </style>
</head>
<body>

<!-- ====== Hero ====== -->
<header class="hero">
    <div class="hero-badge">📊 Amazon Product Research Report</div>
    <h1>{category} · {market} 选品调研报告</h1>
    <p class="hero-subtitle">全链路数据分析 · 差评痛点挖掘 · 差异化选品建议</p>
    <div class="hero-meta">
        <span class="hero-meta-item"><span class="icon">🌍</span> 市场: {market}</span>
        <span class="hero-meta-item"><span class="icon">📦</span> 类目: {category}</span>
        <span class="hero-meta-item"><span class="icon">📅</span> {gen_time}</span>
        <span class="hero-meta-item"><span class="icon">🤖</span> AI Powered</span>
    </div>
</header>

<div class="container">

    <!-- KPI Dashboard -->
    <div class="kpi-grid" id="kpi-dashboard"></div>

    <!-- ====== 1. 执行摘要仪表盘 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">📋</span>
            <h2 class="section-title">执行摘要</h2>
            <span class="section-subtitle">核心发现 · 一句话结论 · 为什么不选</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card full-width" style="max-width: 600px; margin: 0 auto;">
                <div class="chart-card-title">8维度综合评分雷达图</div>
                <div class="chart-card-subtitle">市场容量 / 增长率 / 竞争度 / 利润率 / TikTok热度 / 供应链 / 壁垒 / 政策友好度</div>
                <div class="chart-container" style="height: 420px;">
                    <canvas id="opportunityRadarChart"></canvas>
                </div>
            </div>
        </div>
        <div class="chart-grid why-not-box" style="margin-top:20px; display:block;">
            <div style="font-size:16px; font-weight:600; color:var(--accent-red); margin-bottom:12px;">⚠️ 为什么不选？(强制审视)</div>
            <div id="why-not-list"></div>
        </div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch01"></ul></div></details>
        </div>
    </div>

    <!-- ====== 2. 市场与产品定义 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">🌐</span>
            <h2 class="section-title">市场与产品定义</h2>
            <span class="section-subtitle">市场边界 · 产品形态分类 · 目标用户定义</span>
        </div>
        <div id="market-definition-content">
            <div class="chart-card full-width" style="margin-bottom:16px;">
                <div class="chart-card-title">产品形态分类</div>
                <div class="chart-card-subtitle">按产品形态/价格带/占比/趋势分类</div>
                <div class="chart-container">
                    <table class="data-table" id="product-form-table">
                        <thead><tr><th>形态</th><th>代表产品</th><th>价格带</th><th>SKU占比</th><th>趋势</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch02"></ul></div></details>
        </div>
    </div>

    <!-- ====== 3. 需求逻辑与消费者画像 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">🧑</span>
            <h2 class="section-title">需求逻辑与消费者画像</h2>
            <span class="section-subtitle">谁在买 · 为什么买 · 怎么买</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card full-width">
                <div class="chart-card-title">消费者分层画像</div>
                <div class="chart-card-subtitle">基于真实评论 + Reddit + TikTok数据构建</div>
                <div class="chart-container">
                    <table class="data-table" id="consumer-persona-table">
                        <thead><tr><th>消费者类型</th><th>占比</th><th>核心关注点</th><th>价格敏感度</th><th>渠道偏好</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch03"></ul></div></details>
        </div>
    </div>

    <!-- ====== 4. 五维趋势交叉验证 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">📊</span>
            <h2 class="section-title">五维趋势交叉验证</h2>
            <span class="section-subtitle">行业数据 × TikTok热度 × 线下渠道 × 竞品动态 × 政策合规</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card full-width">
                <div class="chart-card-title">交叉验证矩阵</div>
                <div class="chart-card-subtitle">任一维度矛盾需标记⚠️</div>
                <div class="chart-container">
                    <table class="data-table" id="cross-validation-table">
                        <thead><tr><th>验证维度</th><th>信号方向</th><th>信号强度</th><th>一致性</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch04"></ul></div></details>
        </div>
    </div>

    <!-- ====== 5. 市场容量筛选 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">📈</span>
            <h2 class="section-title">市场容量筛选</h2>
            <span class="section-subtitle">成分赛道 · 剂型赛道 · 价格带拆解</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card full-width">
                <div class="chart-card-title">成分维度赛道拆解</div>
                <div class="chart-card-subtitle">市场规模/增速/竞争度/进入评分</div>
                <div class="chart-container">
                    <table class="data-table" id="ingredient-track-table">
                        <thead><tr><th>成分赛道</th><th>市场规模(USD)</th><th>年增速</th><th>竞争度</th><th>进入评分</th><th>推荐策略</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch05"></ul></div></details>
        </div>
    </div>

    <!-- ====== 6. 产品生命周期定位 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">🔄</span>
            <h2 class="section-title">产品生命周期定位</h2>
            <span class="section-subtitle">阶段判定 · 策略矩阵 · 进入难度评估</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card full-width">
                <div class="chart-card-title">生命周期策略矩阵</div>
                <div class="chart-container">
                    <table class="data-table" id="lifecycle-matrix-table">
                        <thead><tr><th>生命周期阶段</th><th>核心策略</th><th>定价策略</th><th>推广策略</th><th>产品策略</th><th>判定状态</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch06"></ul></div></details>
        </div>
    </div>

    <!-- ====== 1. Google Trends ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">📈</span>
            <h2 class="section-title">Google Trends 搜索趋势</h2>
            <span class="section-subtitle">近5年关键词搜索热度变化</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card full-width">
                <div class="chart-card-title">关键词搜索趋势对比</div>
                <div class="chart-card-subtitle">月粒度 · 搜索热度指数</div>
                <div class="chart-container" style="height: 380px;">
                    <canvas id="googleTrendsChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- ====== 2. TikTok 流量分析 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">📱</span>
            <h2 class="section-title">TikTok 流量验证</h2>
            <span class="section-subtitle">标签热度 & 内容类型分布</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card">
                <div class="chart-card-title">标签播放量 Top 10</div>
                <div class="chart-card-subtitle">相关标签热度排名</div>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="tiktokHashtagsChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-card-title">内容类型分布</div>
                <div class="chart-card-subtitle">爆款内容类型占比</div>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="tiktokContentChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- ====== 3. 竞争格局 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">🏆</span>
            <h2 class="section-title">竞争格局分析</h2>
            <span class="section-subtitle">品牌集中度 · 价格分布 · 评分矩阵</span>
        </div>

        <!-- Tab Navigation -->
        <div class="tab-nav">
            <button class="tab-btn active" onclick="switchCompTab('scatter')">散点矩阵</button>
            <button class="tab-btn" onclick="switchCompTab('brand')">品牌集中度</button>
            <button class="tab-btn" onclick="switchCompTab('price')">价格分布</button>
        </div>

        <div id="comp-tab-scatter" class="chart-grid">
            <div class="chart-card full-width">
                <div class="chart-card-title">价格 vs 评分竞争矩阵</div>
                <div class="chart-card-subtitle">气泡大小=评论数 | 颜色=品牌 | 标注=蓝海区域</div>
                <div class="chart-container" style="height: 420px;">
                    <canvas id="competitionScatterChart"></canvas>
                </div>
            </div>
        </div>
        <div id="comp-tab-brand" class="chart-grid" style="display:none;">
            <div class="chart-card full-width">
                <div class="chart-card-title">品牌集中度分析</div>
                <div class="chart-card-subtitle">Top 品牌市场份额分布</div>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="brandConcChart"></canvas>
                </div>
            </div>
        </div>
        <div id="comp-tab-price" class="chart-grid" style="display:none;">
            <div class="chart-card full-width">
                <div class="chart-card-title">价格区间分布</div>
                <div class="chart-card-subtitle">商品数量按价格段分布</div>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="priceDistChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- ====== 4. 差评痛点分析 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">⭐</span>
            <h2 class="section-title">差评痛点深度分析</h2>
            <span class="section-subtitle">基于 Top 20 竞品 1-3星评论 NLP 分析</span>
        </div>
        <div class="chart-grid triple">
            <div class="chart-card">
                <div class="chart-card-title">痛点词云</div>
                <div class="chart-card-subtitle">点击可交互</div>
                <div class="chart-container">
                    <canvas id="wordcloudCanvas" width="400" height="400" style="width:100%;"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-card-title">痛点分类分布</div>
                <div class="chart-card-subtitle">差评按类别统计</div>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="painCategoriesChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-card-title">Top 10 负面关键词</div>
                <div class="chart-card-subtitle">差评中出现频率最高</div>
                <div class="chart-container" style="height: 350px;">
                    <canvas id="painKeywordsChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- ====== 5. Reddit 用户洞察 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">🗣️</span>
            <h2 class="section-title">Reddit 用户洞察</h2>
            <span class="section-subtitle">真实用户讨论 · 需求缺口 · 情绪分析</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card">
                <div class="chart-card-title">用户情绪分布</div>
                <div class="chart-card-subtitle">正面/中性/负面评论占比</div>
                <div class="chart-container" style="height: 320px;">
                    <canvas id="redditSentimentChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-card-title">高频讨论主题</div>
                <div class="chart-card-subtitle">用户最关心的品类话题</div>
                <div class="chart-container" style="height: 320px;">
                    <canvas id="redditTopicsChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- ====== 利润模型 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">💰</span>
            <h2 class="section-title">利润模型</h2>
            <span class="section-subtitle">成本结构 · 多档定价 · 盈亏平衡</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card">
                <div class="chart-card-title">成本结构拆解</div>
                <div class="chart-card-subtitle">以 $25 售价为例</div>
                <div class="chart-container" style="height: 320px;">
                    <canvas id="profitWaterfallChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-card-title">多档定价利润对比</div>
                <div class="chart-card-subtitle">成本 vs 利润堆叠图</div>
                <div class="chart-container" style="height: 320px;">
                    <canvas id="pricingCompChart"></canvas>
                </div>
            </div>
        </div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch12"></ul></div></details>
        </div>
    </div>

    <!-- ====== 研发壁垒构建 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">🛡️</span>
            <h2 class="section-title">研发壁垒构建</h2>
            <span class="section-subtitle">五类壁垒评估 · 认证路径 · 专利地图</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card full-width">
                <div class="chart-card-title">五类壁垒可构建性评估</div>
                <div class="chart-container">
                    <table class="data-table" id="moat-table">
                        <thead><tr><th>壁垒类型</th><th>当前状态</th><th>可构建性</th><th>构建周期</th><th>构建成本(估)</th><th>优先级</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch13"></ul></div></details>
        </div>
    </div>

    <!-- ====== 差异化选品与产品矩阵 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">🎯</span>
            <h2 class="section-title">差异化选品与产品矩阵</h2>
            <span class="section-subtitle">基于差评痛点 + 消费者画像 + 竞争对标综合推导</span>
        </div>
        <div class="diff-grid" id="diff-suggestions"></div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch14"></ul></div></details>
        </div>
    </div>

    <!-- ====== 风险评估与"为什么不选" ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">⚠️</span>
            <h2 class="section-title">风险评估与"为什么不选"</h2>
            <span class="section-subtitle">虚假蓝海检测 · 风险矩阵 · 强制反对意见</span>
        </div>
        <div class="chart-grid">
            <div class="chart-card full-width">
                <div class="chart-card-title">虚假蓝海检测</div>
                <div class="chart-card-subtitle">5项指标综合判定</div>
                <div class="chart-container" id="false-blue-ocean-result"></div>
            </div>
        </div>
        <div class="risk-matrix-grid" id="risk-matrix-grid"></div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch15"></ul></div></details>
        </div>
    </div>

    <!-- ====== 90天执行路线图 ====== -->
    <div class="section">
        <div class="section-header">
            <span class="section-icon">📋</span>
            <h2 class="section-title">90天执行路线图</h2>
            <span class="section-subtitle">月度里程碑 · 资源配置 · 关键节点</span>
        </div>
        <div class="roadmap-timeline" id="roadmap-timeline"></div>
        <div class="data-lineage">
            <details><summary>📌 数据来源 (Data Lineage)</summary>
            <div class="lineage-content"><ul id="lineage-ch16"></ul></div></details>
        </div>
    </div>

</div>

<footer class="footer">
    <p>本报告由 <strong>Amazon Product Research Toolkit v3.0</strong> 自动生成</p>
    <p>数据来源: Apify (Amazon/TikTok/Reddit/1688) · Google Trends · Market Reports · Web Search</p>
    <p style="margin-top:8px;">生成时间: {gen_time} · 所有数据标注采集时间 · 数据可能存在延迟，建议结合实时数据验证</p>
</footer>

<!-- ====== Chart.js 初始化脚本 ====== -->
<script>
// ===== 全局数据 =====
const chartData = {charts_json};
const diffSuggestions = {diff_json};

// ===== Chart.js 全局配置 =====
Chart.defaults.color = '#8b949e';
Chart.defaults.borderColor = 'rgba(48, 54, 61, 0.5)';
Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(28, 33, 40, 0.95)';
Chart.defaults.plugins.tooltip.titleColor = '#f0f6fc';
Chart.defaults.plugins.tooltip.bodyColor = '#c9d1d9';
Chart.defaults.plugins.tooltip.borderColor = '#30363d';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 6;

// ===== Dark Theme Plugin =====
const darkThemePlugin = {{
    id: 'darkTheme',
    beforeDraw(chart) {{
        const ctx = chart.ctx;
        ctx.save();
        ctx.fillStyle = '#1c2128';
        ctx.fillRect(0, 0, chart.width, chart.height);
        ctx.restore();
    }}
}};

// ===== KPI Dashboard (v3.0: 8 KPIs) =====
function buildKPIDashboard() {{
    const container = document.getElementById('kpi-dashboard');
    const kpis = [
        {{ label: '市场规模', value: '--', change: '见数据', trend: 'up' }},
        {{ label: '品牌集中度', value: '--', change: '见数据', trend: 'up' }},
        {{ label: '平均利润率', value: '--', change: '见数据', trend: 'up' }},
        {{ label: 'TikTok热度', value: '--', change: '见数据', trend: 'up' }},
        {{ label: '差评可改进空间', value: '--', change: '见数据', trend: 'up' }},
        {{ label: '生命周期阶段', value: '--', change: '判定中', trend: 'up' }},
        {{ label: '研发壁垒潜力', value: '--', change: '评估中', trend: 'up' }},
        {{ label: '政策友好度', value: '--', change: '评估中', trend: 'up' }},
    ];
    container.innerHTML = kpis.map(k => `
        <div class="kpi-card">
            <span class="kpi-label">${{k.label}}</span>
            <span class="kpi-value">${{k.value}}</span>
            <span class="kpi-change ${{k.trend}}">${{k.change}}</span>
        </div>
    `).join('');
}}

// ===== v3.0 NEW: "为什么不选"生成器 =====
function buildWhyNot() {{
    const container = document.getElementById('why-not-list');
    const reasons = [
        {{ reason: '需求规模可能被高估', detail: '市场报告数据可能存在偏差，实际搜索量需通过Amazon广告后台验证。若月搜索量低于2万，ROI模型可能不成立。' }},
        {{ reason: '进入壁垒可能高于预期', detail: '头部品牌的评论数壁垒（10万+条）和品牌认知度壁垒远超表面数字，新品冷启动成本可能需要$15,000+。' }},
        {{ reason: 'TikTok热度未必转化为销量', detail: '高播放量不等于高转化率，需验证内容类型与购买决策的关联度。若测评类内容占比低，转化效果有限。' }},
    ];
    container.innerHTML = reasons.map((r, i) => `
        <div class="why-not-item">
            <div class="why-not-icon">❌</div>
            <div class="why-not-text">
                <strong>反对理由 ${{i+1}}：${{r.reason}}</strong>
                <p>${{r.detail}}</p>
            </div>
        </div>
    `).join('');
}}

// ===== v3.0 NEW: 风险矩阵构建 =====
function buildRiskMatrix() {{
    const container = document.getElementById('risk-matrix-grid');
    const risks = [
        {{ level: 'high', title: '市场风险', desc: '需求可能被高估；季节性波动影响现金流；品类趋势可能逆转' }},
        {{ level: 'high', title: '竞争风险', desc: '头部品牌可能降价狙击；新品跟风速度快；广告CPC持续攀升' }},
        {{ level: 'medium', title: '政策风险', desc: 'FDA法规变动可能影响产品合规；标签声明要求可能收紧；进口关税可能调整' }},
        {{ level: 'medium', title: '供应链风险', desc: '原材料价格波动；供应商产能不足；物流时效不稳定；品控一致性挑战' }},
        {{ level: 'low', title: '执行风险', desc: '团队经验不足；资金链断裂；产品定位偏差；市场反馈不及预期' }},
    ];
    container.innerHTML = risks.map(r => `
        <div class="risk-card ${{r.level}}">
            <div class="risk-card-title">${{r.title}}</div>
            <div class="risk-card-desc">${{r.desc}}</div>
        </div>
    `).join('');
}}

// ===== v3.0 NEW: 90天执行路线图 =====
function buildRoadmapTimeline() {{
    const container = document.getElementById('roadmap-timeline');
    const phases = [
        {{
            num: 'Phase 1', title: '供应链搭建', time: 'Day 1-30',
            tasks: ['供应商筛选 (5-8家)', '样品打版确认', '小批量下单 (300-500件)', '包材设计定稿', 'FBA物流方案确定']
        }},
        {{
            num: 'Phase 2', title: 'Listing上线', time: 'Day 31-60', active: true,
            tasks: ['产品视觉拍摄', 'Listing文案+A+页面', '关键词布局优化', 'FBA首批入仓', '广告框架搭建']
        }},
        {{
            num: 'Phase 3', title: '冷启动验证', time: 'Day 61-90',
            tasks: ['自动广告+手动广告测试', '达人合作首批(5-10位)', 'Vine计划获取首批评价', '数据复盘+策略调整', '决定是否放量']
        }},
    ];
    container.innerHTML = phases.map(p => `
        <div class="roadmap-phase ${{p.active ? 'active' : ''}}">
            <div class="roadmap-phase-number">${{p.num}}</div>
            <div class="roadmap-phase-title">${{p.title}}</div>
            <div class="roadmap-phase-time">${{p.time}}</div>
            <ul>${{p.tasks.map(t => `<li>${{t}}</li>`).join('')}}</ul>
        </div>
    `).join('');
}}

// ===== v3.0 NEW: 数据溯源填充 =====
function populateDataLineage() {{
    const lineages = {{
        'lineage-ch01': ['Amazon竞品数据: Apify actor, 采集时间见报告元数据', '市场报告: 来源见第4章', 'TikTok数据: Apify actor'],
        'lineage-ch02': ['Amazon BSR类目数据: Apify actor', '产品分类: 基于采集数据统计'],
        'lineage-ch03': ['Reddit用户讨论: Apify Reddit Scraper', 'Amazon评论: Apify Amazon Review Scraper', 'TikTok评论: Apify TikTok Scraper'],
        'lineage-ch04': ['行业数据: 市场调研报告(见具体引用)', 'TikTok: Apify actor', '线下渠道: 联网搜索 Walmart/Target/Costco', '竞品动态: Amazon采集+联网搜索', '政策: FDA/FTC官网'],
        'lineage-ch05': ['市场规模数据: 市场调研报告', '竞品数据: Amazon Apify采集'],
        'lineage-ch06': ['Google Trends: pytrends/SerpAPI', 'Amazon历史数据: Apify采集'],
        'lineage-ch12': ['1688供应商报价: Apify actor', 'Amazon费率表: sellercentral.amazon.com', 'FBA计算器: Amazon官方工具'],
        'lineage-ch13': ['FDA数据库: fda.gov', 'USPTO: uspto.gov', '认证要求: 行业标准+官网'],
        'lineage-ch14': ['综合前13章所有数据来源'],
        'lineage-ch15': ['虚假蓝海检测: 数据来源同第4/5/7/12章', '风险矩阵: 基于全报告数据综合评估'],
        'lineage-ch16': ['资源配置: 1688报价+行业均价估算', '时间线: 基于典型产品开发周期'],
    }};
    Object.entries(lineages).forEach(([id, items]) => {{
        const el = document.getElementById(id);
        if (el) el.innerHTML = items.map(i => `<li>${{i}}</li>`).join('');
    }});
}}

// ===== Initialization (v3.0) =====
document.addEventListener('DOMContentLoaded', function() {{
    buildKPIDashboard();
    buildWhyNot();
    buildRiskMatrix();
    buildRoadmapTimeline();
    populateDataLineage();
    initAllCharts();
    buildDiffSuggestions();
    initWordCloud();
}});

// ===== Competition Tab Switch =====
function switchCompTab(tab) {{
    ['scatter','brand','price'].forEach(t => {{
        const el = document.getElementById('comp-tab-' + t);
        if (el) el.style.display = t === tab ? '' : 'none';
    }});
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const activeBtn = document.querySelector(`.tab-btn[onclick="switchCompTab('${{tab}}')"]`);
    if (activeBtn) activeBtn.classList.add('active');
    // Re-render visible chart
    setTimeout(() => {{
        if (tab === 'scatter' && window._compScatter) window._compScatter.resize();
        if (tab === 'brand' && window._brandConc) window._brandConc.resize();
        if (tab === 'price' && window._priceDist) window._priceDist.resize();
    }}, 100);
}}

// ===== Init All Charts =====
function initAllCharts() {{
    // Google Trends
    if (chartData.google_trends) {{
        const d = chartData.google_trends;
        const ctx = document.getElementById('googleTrendsChart').getContext('2d');
        new Chart(ctx, {{ type: 'line', data: {{ labels: d.labels, datasets: d.datasets }},
            options: {{ ...d.options, plugins: {{ legend: {{ labels: {{ usePointStyle: true, padding: 20 }} }} }} }} }});
    }}

    // TikTok Hashtags
    if (chartData.tiktok_hashtags) {{
        const ctx = document.getElementById('tiktokHashtagsChart').getContext('2d');
        new Chart(ctx, {{ type: 'bar', data: {{ labels: chartData.tiktok_hashtags.labels,
            datasets: chartData.tiktok_hashtags.datasets }}, options: chartData.tiktok_hashtags.options }});
    }}

    // TikTok Content Types
    if (chartData.tiktok_content_types) {{
        const ctx = document.getElementById('tiktokContentChart').getContext('2d');
        new Chart(ctx, {{ type: 'doughnut', data: {{ labels: chartData.tiktok_content_types.labels,
            datasets: chartData.tiktok_content_types.datasets }}, options: chartData.tiktok_content_types.options }});
    }}

    // Competition Scatter
    if (chartData.competition_scatter) {{
        const ctx = document.getElementById('competitionScatterChart').getContext('2d');
        window._compScatter = new Chart(ctx, {{ type: 'bubble', data: {{ datasets: chartData.competition_scatter.datasets }},
            options: chartData.competition_scatter.options }});
    }}

    // Brand Concentration
    if (chartData.brand_concentration) {{
        const ctx = document.getElementById('brandConcChart').getContext('2d');
        window._brandConc = new Chart(ctx, {{ type: 'bar', data: {{ labels: chartData.brand_concentration.labels,
            datasets: chartData.brand_concentration.datasets }}, options: chartData.brand_concentration.options }});
    }}

    // Price Distribution
    if (chartData.price_distribution) {{
        const ctx = document.getElementById('priceDistChart').getContext('2d');
        window._priceDist = new Chart(ctx, {{ type: 'bar', data: {{ labels: chartData.price_distribution.labels,
            datasets: chartData.price_distribution.datasets }}, options: chartData.price_distribution.options }});
    }}

    // Pain Categories
    if (chartData.pain_points_categories) {{
        const ctx = document.getElementById('painCategoriesChart').getContext('2d');
        new Chart(ctx, {{ type: 'pie', data: {{ labels: chartData.pain_points_categories.labels,
            datasets: chartData.pain_points_categories.datasets }}, options: chartData.pain_points_categories.options }});
    }}

    // Pain Keywords
    if (chartData.pain_points_top_keywords) {{
        const ctx = document.getElementById('painKeywordsChart').getContext('2d');
        new Chart(ctx, {{ type: 'bar', data: {{ labels: chartData.pain_points_top_keywords.labels,
            datasets: chartData.pain_points_top_keywords.datasets }}, options: chartData.pain_points_top_keywords.options }});
    }}

    // Reddit Sentiment
    if (chartData.reddit_sentiment) {{
        const ctx = document.getElementById('redditSentimentChart').getContext('2d');
        new Chart(ctx, {{ type: 'doughnut', data: {{ labels: chartData.reddit_sentiment.labels,
            datasets: chartData.reddit_sentiment.datasets }}, options: chartData.reddit_sentiment.options }});
    }}

    // Reddit Topics
    if (chartData.reddit_topics) {{
        const ctx = document.getElementById('redditTopicsChart').getContext('2d');
        new Chart(ctx, {{ type: 'bar', data: {{ labels: chartData.reddit_topics.labels,
            datasets: chartData.reddit_topics.datasets }}, options: chartData.reddit_topics.options }});
    }}

    // Opportunity Radar
    if (chartData.opportunity_radar) {{
        const ctx = document.getElementById('opportunityRadarChart').getContext('2d');
        new Chart(ctx, {{ type: 'radar', data: {{ labels: chartData.opportunity_radar.labels,
            datasets: chartData.opportunity_radar.datasets }}, options: chartData.opportunity_radar.options }});
    }}

    // Profit Waterfall
    if (chartData.profit_waterfall) {{
        const ctx = document.getElementById('profitWaterfallChart').getContext('2d');
        new Chart(ctx, {{ type: 'bar', data: {{ labels: chartData.profit_waterfall.labels,
            datasets: chartData.profit_waterfall.datasets }}, options: chartData.profit_waterfall.options }});
    }}

    // Pricing Comparison
    if (chartData.pricing_comparison) {{
        const ctx = document.getElementById('pricingCompChart').getContext('2d');
        new Chart(ctx, {{ type: 'bar', data: {{ labels: chartData.pricing_comparison.labels,
            datasets: chartData.pricing_comparison.datasets }}, options: chartData.pricing_comparison.options }});
    }}
}}

// ===== WordCloud =====
function initWordCloud() {{
    if (chartData.pain_points_wordcloud && chartData.pain_points_wordcloud.wordList) {{
        const canvas = document.getElementById('wordcloudCanvas');
        const wc = chartData.pain_points_wordcloud;
        WordCloud(canvas, {{
            list: wc.wordList,
            gridSize: wc.options.gridSize || 8,
            weightFactor: wc.options.weightFactor || 3,
            fontFamily: wc.options.fontFamily || "'Inter', sans-serif",
            color: wc.options.color || 'random-dark',
            rotateRatio: wc.options.rotateRatio || 0.3,
            shape: wc.options.shape || 'circle',
            backgroundColor: 'transparent',
            hover: function(item) {{
                // Optional hover effect
            }},
            click: function(item) {{
                // Optional click behavior
            }},
        }});
    }}
}}

// ===== Build Differentiation Suggestions =====
function buildDiffSuggestions() {{
    const container = document.getElementById('diff-suggestions');
    if (!diffSuggestions || diffSuggestions.length === 0) {{
        container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px;">暂无足够数据生成差异化建议，请先完成数据采集。</p>';
        return;
    }}
    container.innerHTML = diffSuggestions.map((s, i) => `
        <div class="diff-card">
            <div class="diff-rank">#${{i + 1}}</div>
            <div class="diff-category">${{s.category}} · ${{s.pain_percentage || '?'}}%</div>
            <div class="diff-direction">${{s.direction}}</div>
            <div class="diff-detail">${{s.detail}}</div>
            <div class="diff-action">💡 ${{s.action}}</div>
            <div class="diff-score">🎯 机会评分: ${{s.score}}/100</div>
        </div>
    `).join('');
}}
</script>

</body>
</html>"""


# ============================================================
# 便捷函数
# ============================================================

def generate_html_report(data: dict, output_dir: Optional[Path] = None) -> Path:
    """
    便捷函数：生成 HTML 可视化报告

    Args:
        data: 完整采集/分析数据字典
        output_dir: 输出目录，默认 ./output

    Returns:
        生成的 HTML 文件路径
    """
    if output_dir is None:
        output_dir = Path("./output")
    generator = HTMLReportGenerator(data, output_dir)
    return generator.generate()


if __name__ == "__main__":
    # 测试
    test_data = {
        "metadata": {
            "market": "US",
            "category": "Kids Supplements",
            "keywords": ["children's vitamins", "gummy vitamins", "kids probiotic"]
        },
        "amazon": [],
        "tiktok": [],
        "market": {},
        "reddit": {},
        "google_trends": {},
        "review_analysis": {},
        "supplier": {},
        "analysis": {},
    }

    output_dir = Path("./output")
    report_path = generate_html_report(test_data, output_dir)
    print(f"✅ HTML 报告已生成: {report_path}")
