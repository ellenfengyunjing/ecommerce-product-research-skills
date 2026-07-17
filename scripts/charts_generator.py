"""
Charts Generator Module (NEW)
==============================

为 HTML 可视化报告生成 Chart.js 所需的 JavaScript 数据结构。

支持的图表类型:
- Line: Google Trends 关键词趋势
- Doughnut/Pie: TikTok 内容类型分布, Reddit 情绪分布
- Bar/HorizontalBar: 标签播放量排名, 供应商报价对比
- Scatter: 竞争格局 (价格 vs 评分)
- Radar: 市场机会综合评分
- Waterfall: 利润成本结构 (Chart.js 插件)
- WordCloud: 差评痛点词云 (wordcloud2.js)

配色方案: 简洁商务科技风 (深色背景 + 蓝色调)
"""

import json
import math
from collections import Counter
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

from image_prompt_builder import attach_image_prompts


# ============================================================
# 配色方案
# ============================================================

CHART_COLORS = {
    "primary": [
        "#58a6ff", "#3fb950", "#f0883e", "#bc8cff",
        "#f85149", "#79c0ff", "#d2a8ff", "#ffa657",
        "#56d364", "#e5534b", "#db6d28", "#8b949e"
    ],
    "blue_gradient": [
        "rgba(88, 166, 255, 0.9)",
        "rgba(88, 166, 255, 0.7)",
        "rgba(88, 166, 255, 0.5)",
        "rgba(88, 166, 255, 0.3)",
        "rgba(88, 166, 255, 0.15)",
    ],
    "sentiment": {
        "positive": "#3fb950",
        "neutral": "#8b949e",
        "negative": "#f85149"
    },
    "warning": "#f0883e",
    "success": "#3fb950",
    "danger": "#f85149",
    "info": "#58a6ff",
    "purple": "#bc8cff",
}


class ChartsGenerator:
    """图表数据生成器"""

    def __init__(self, data: dict):
        """
        Args:
            data: 完整的采集数据字典
        """
        self.data = data
        self.metadata = data.get("metadata", {})
        self.amazon_data = data.get("amazon", [])
        self.tiktok_data = data.get("tiktok", [])
        self.market_data = data.get("market", {})
        self.reddit_data = data.get("reddit", {})
        self.google_trends = data.get("google_trends", {})
        self.review_analysis = data.get("review_analysis", {})
        self.supplier_data = data.get("supplier", {})
        self.analysis = data.get("analysis", {})

    def generate_all_charts(self) -> Dict[str, dict]:
        """生成所有图表数据结构"""
        charts = {
            # Google Trends
            "google_trends": self.generate_google_trends_chart(),
            # TikTok 品类分布
            "tiktok_hashtags": self.generate_tiktok_hashtags_chart(),
            "tiktok_content_types": self.generate_tiktok_content_chart(),
            # 竞争格局
            "competition_scatter": self.generate_competition_scatter(),
            "brand_concentration": self.generate_brand_concentration_chart(),
            "price_distribution": self.generate_price_distribution_chart(),
            # 差评痛点
            "pain_points_wordcloud": self.generate_pain_points_wordcloud(),
            "pain_points_categories": self.generate_pain_points_categories(),
            "pain_points_top_keywords": self.generate_pain_points_keywords(),
            # Reddit 洞察
            "reddit_sentiment": self.generate_reddit_sentiment(),
            "reddit_topics": self.generate_reddit_topics(),
            # 市场机会
            "opportunity_radar": self.generate_opportunity_radar(),
            # 利润模型
            "profit_waterfall": self.generate_profit_waterfall(),
            "pricing_comparison": self.generate_pricing_comparison(),
            # 供应商
            "supplier_comparison": self.generate_supplier_comparison(),
        }
        return {name: chart for name, chart in charts.items() if chart}

    # ============================================================
    # Google Trends 折线图
    # ============================================================

    def generate_google_trends_chart(self) -> dict:
        """生成 Google Trends 关键词趋势折线图"""
        trends = self.google_trends

        if not trends or not trends.get("keywords"):
            return {}

        keywords_data = trends.get("keywords", {})
        timeline = trends.get("timeline", [])

        datasets = []
        for i, (keyword, values) in enumerate(keywords_data.items()):
            datasets.append({
                "label": keyword,
                "data": values,
                "borderColor": CHART_COLORS["primary"][i % len(CHART_COLORS["primary"])],
                "backgroundColor": "transparent",
                "borderWidth": 2,
                "pointRadius": 0,
                "pointHoverRadius": 5,
                "tension": 0.4,
                "fill": False,
            })

        return {
            "type": "line",
            "title": "Google Trends 关键词搜索趋势",
            "subtitle": f"{self.metadata.get('category', '')} - 近5年搜索热度变化",
            "labels": timeline,
            "datasets": datasets,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "y": {
                        "title": {"display": True, "text": "搜索热度指数"},
                        "grid": {"color": "rgba(48, 54, 61, 0.5)"},
                    },
                    "x": {
                        "grid": {"display": False},
                    }
                }
            }
        }

    # ============================================================
    # TikTok 柱状图/环形图
    # ============================================================

    def generate_tiktok_hashtags_chart(self) -> dict:
        """生成 TikTok 标签播放量排名柱状图"""
        tiktok = self.tiktok_data

        if not tiktok:
            return {}

        # 按播放量排序取 Top 10
        sorted_tags = sorted(tiktok, key=lambda x: x.get("views", 0), reverse=True)[:10]

        labels = [t.get("hashtag", f"#tag{i}") for i, t in enumerate(sorted_tags)]
        values = [t.get("views", 0) for t in sorted_tags]

        return {
            "type": "bar",
            "title": "TikTok 标签播放量 Top 10",
            "subtitle": f"{self.metadata.get('category', '')} 相关标签热度排名",
            "labels": labels,
            "datasets": [{
                "label": "播放量",
                "data": values,
                "backgroundColor": CHART_COLORS["blue_gradient"],
                "borderColor": "#58a6ff",
                "borderWidth": 1,
                "borderRadius": 4,
            }],
            "options": {
                "indexAxis": "y",
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "播放量"},
                        "grid": {"color": "rgba(48, 54, 61, 0.5)"},
                        "ticks": {
                            "callback": "function(value) { if (value >= 1e8) return (value/1e8).toFixed(1)+'亿'; if (value >= 1e4) return (value/1e4).toFixed(1)+'万'; return value; }"
                        }
                    }
                }
            }
        }

    def generate_tiktok_content_chart(self) -> dict:
        """生成 TikTok 内容类型分布环形图"""
        content_types = self.analysis.get("tiktok", {}).get("content_types", {})

        if not content_types:
            return {}

        return {
            "type": "doughnut",
            "title": "TikTok 内容类型分布",
            "subtitle": "爆款内容类型占比分析",
            "labels": list(content_types.keys()),
            "datasets": [{
                "data": list(content_types.values()),
                "backgroundColor": CHART_COLORS["primary"][:len(content_types)],
                "borderColor": "rgba(13, 17, 23, 0.8)",
                "borderWidth": 2,
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": True,
                "plugins": {
                    "legend": {"position": "right"}
                }
            }
        }

    # ============================================================
    # 竞争格局散点图
    # ============================================================

    def generate_competition_scatter(self) -> dict:
        """生成竞争格局价格-评分散点图"""
        products = self.amazon_data

        if not products:
            return {}

        # 按品牌分组
        brand_groups = {}
        for p in products:
            brand = p.get("brand", "Unknown")
            if brand not in brand_groups:
                brand_groups[brand] = []
            brand_groups[brand].append(p)

        datasets = []
        colors = CHART_COLORS["primary"]
        for i, (brand, items) in enumerate(brand_groups.items()):
            datasets.append({
                "label": brand,
                "data": [
                    {
                        "x": item.get("price", 0),
                        "y": item.get("rating", 0),
                        "r": min(max(item.get("review_count", 100) / 100, 5), 25),
                        "title": item.get("title", "")[:30],
                    }
                    for item in items
                ],
                "backgroundColor": colors[i % len(colors)] + "99",
                "borderColor": colors[i % len(colors)],
                "borderWidth": 1,
            })

        return {
            "type": "bubble",
            "title": "竞争格局：价格 vs 评分",
            "subtitle": "气泡大小 = 评论数量 | 颜色 = 品牌",
            "datasets": datasets,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "价格 (USD)"},
                        "grid": {"color": "rgba(48, 54, 61, 0.5)"},
                    },
                    "y": {
                        "title": {"display": True, "text": "评分"},
                        "min": 3.0,
                        "max": 5.0,
                        "grid": {"color": "rgba(48, 54, 61, 0.5)"},
                    }
                },
                "plugins": {
                    "tooltip": {
                        "callbacks": {
                            "label": "function(ctx) { return ctx.raw.title + ': $' + ctx.raw.x + ' / ' + ctx.raw.y + '⭐'; }"
                        }
                    },
                    "annotation": {
                        "annotations": {
                            "blueOcean": {
                                "type": "box",
                                "xMin": 15, "xMax": 35,
                                "yMin": 3.8, "yMax": 4.3,
                                "backgroundColor": "rgba(88, 166, 255, 0.1)",
                                "borderColor": "rgba(88, 166, 255, 0.3)",
                                "borderWidth": 1,
                                "label": {
                                    "display": True,
                                    "content": "蓝海区域",
                                    "position": "center",
                                }
                            }
                        }
                    }
                }
            }
        }

    def generate_brand_concentration_chart(self) -> dict:
        """生成品牌集中度柱状图"""
        brand_conc = self.analysis.get("market", {}).get("brand_concentration", {})
        brand_shares = brand_conc.get("brand_shares", {})

        if not brand_shares:
            brands = {}
            for p in self.amazon_data:
                brand = p.get("brand", "Unknown")
                brands[brand] = brands.get(brand, 0) + 1
            sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]
            brand_shares = {k: v for k, v in sorted_brands}
        if not brand_shares:
            return {}

        return {
            "type": "bar",
            "title": "品牌集中度分析",
            "subtitle": f"Top {len(brand_shares)} 品牌市场份额分布",
            "labels": list(brand_shares.keys()),
            "datasets": [{
                "label": "商品数量",
                "data": list(brand_shares.values()),
                "backgroundColor": CHART_COLORS["blue_gradient"][:len(brand_shares)],
                "borderRadius": 4,
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
            }
        }

    def generate_price_distribution_chart(self) -> dict:
        """生成价格分布直方图"""
        prices = [p.get("price", 0) for p in self.amazon_data if p.get("price")]

        if not prices:
            return {}

        # 按 $5 区间分组
        bins = {}
        for p in prices:
            bin_key = f"${int(p//5)*5}-{int(p//5)*5+5}"
            bins[bin_key] = bins.get(bin_key, 0) + 1

        sorted_bins = sorted(bins.items(), key=lambda x: int(x[0].split("$")[1].split("-")[0]))

        return {
            "type": "bar",
            "title": "价格区间分布",
            "subtitle": "商品数量按价格段分布",
            "labels": [b[0] for b in sorted_bins],
            "datasets": [{
                "label": "商品数",
                "data": [b[1] for b in sorted_bins],
                "backgroundColor": "#58a6ff99",
                "borderColor": "#58a6ff",
                "borderWidth": 1,
                "borderRadius": 4,
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
            }
        }

    # ============================================================
    # 差评痛点词云 & 分类
    # ============================================================

    def generate_pain_points_wordcloud(self) -> dict:
        """生成差评痛点词云数据"""
        review_analysis = self.review_analysis
        pain_points = review_analysis.get("pain_points", [])

        if not pain_points:
            return {}

        # wordcloud2.js 格式: [["word", weight], ...]
        word_list = [[pp["word"], pp["weight"]] for pp in pain_points[:80]]

        return {
            "type": "wordcloud",
            "title": "竞品差评痛点词云",
            "subtitle": "基于 Top 20 竞品 1-3星评论 NLP 分析",
            "wordList": word_list,
            "colors": CHART_COLORS["primary"],
            "options": {
                "gridSize": 8,
                "weightFactor": 3,
                "fontFamily": "'Inter', -apple-system, sans-serif",
                "color": "function(word, weight) { return weight > 30 ? '#f85149' : weight > 15 ? '#f0883e' : '#58a6ff'; }",
                "rotateRatio": 0.3,
                "shape": "circle",
                "backgroundColor": "transparent",
            }
        }

    def generate_pain_points_categories(self) -> dict:
        """生成痛点分类占比饼图"""
        review_analysis = self.review_analysis
        categories = review_analysis.get("pain_categories", {})

        if not categories:
            return {}

        return {
            "type": "pie",
            "title": "差评痛点分类分布",
            "subtitle": "Top 20 竞品负评按类别统计",
            "labels": list(categories.keys()),
            "datasets": [{
                "data": list(categories.values()),
                "backgroundColor": CHART_COLORS["primary"][:len(categories)],
                "borderColor": "rgba(13, 17, 23, 0.9)",
                "borderWidth": 2,
                "hoverOffset": 8,
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": True,
                "plugins": {
                    "legend": {"position": "bottom"}
                }
            }
        }

    def generate_pain_points_keywords(self) -> dict:
        """生成 Top 10 高频负面关键词"""
        pain_points = self.review_analysis.get("pain_points", [])

        if not pain_points:
            return {}

        top10 = sorted(pain_points, key=lambda x: x.get("weight", 0), reverse=True)[:10]

        return {
            "type": "bar",
            "title": "Top 10 高频负面关键词",
            "subtitle": "竞品差评中出现频率最高的词汇",
            "labels": [pp["word"] for pp in top10],
            "datasets": [{
                "label": "出现频次",
                "data": [pp["weight"] for pp in top10],
                "backgroundColor": [
                    "rgba(248, 81, 73, 0.8)",
                    "rgba(248, 81, 73, 0.7)",
                    "rgba(240, 136, 62, 0.8)",
                    "rgba(240, 136, 62, 0.7)",
                    "rgba(240, 136, 62, 0.6)",
                ] + ["rgba(88, 166, 255, 0.7)"] * 5,
                "borderRadius": 4,
            }],
            "options": {
                "indexAxis": "y",
                "responsive": True,
                "maintainAspectRatio": False,
            }
        }

    # ============================================================
    # Reddit 情绪分析
    # ============================================================

    def generate_reddit_sentiment(self) -> dict:
        """生成 Reddit 用户情绪分布饼图"""
        reddit = self.reddit_data
        sentiment = reddit.get("sentiment", {})

        if not sentiment:
            return {}

        return {
            "type": "doughnut",
            "title": "Reddit 用户情绪分析",
            "subtitle": "相关子版块讨论情绪分布",
            "labels": list(sentiment.keys()),
            "datasets": [{
                "data": list(sentiment.values()),
                "backgroundColor": [
                    CHART_COLORS["sentiment"]["positive"],
                    CHART_COLORS["sentiment"]["neutral"],
                    CHART_COLORS["sentiment"]["negative"],
                ],
                "borderColor": "rgba(13, 17, 23, 0.9)",
                "borderWidth": 2,
                "hoverOffset": 8,
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": True,
            }
        }

    def generate_reddit_topics(self) -> dict:
        """生成 Reddit 高频讨论主题柱状图"""
        reddit = self.reddit_data
        topics = reddit.get("top_topics", {})

        if not topics:
            return {}

        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)

        return {
            "type": "bar",
            "title": "Reddit 高频讨论主题",
            "subtitle": "用户最关心的品类话题",
            "labels": [t[0] for t in sorted_topics],
            "datasets": [{
                "label": "讨论热度",
                "data": [t[1] for t in sorted_topics],
                "backgroundColor": CHART_COLORS["blue_gradient"][:len(topics)],
                "borderRadius": 4,
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "x": {
                        "ticks": {"maxRotation": 45, "minRotation": 0}
                    }
                }
            }
        }

    # ============================================================
    # 市场机会雷达图
    # ============================================================

    def generate_opportunity_radar(self) -> dict:
        """生成市场机会综合评分雷达图"""
        scores = self.analysis.get("market", {}).get("scores", {})

        if not scores:
            return {}

        return {
            "type": "radar",
            "title": "市场机会综合评分",
            "subtitle": "6维度雷达图 | 分数越高机会越大",
            "labels": list(scores.keys()),
            "datasets": [{
                "label": self.metadata.get("category", "目标品类"),
                "data": list(scores.values()),
                "backgroundColor": "rgba(88, 166, 255, 0.2)",
                "borderColor": "#58a6ff",
                "borderWidth": 2,
                "pointBackgroundColor": "#58a6ff",
                "pointBorderColor": "#fff",
                "pointRadius": 4,
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": True,
                "scales": {
                    "r": {
                        "min": 0,
                        "max": 100,
                        "ticks": {
                            "stepSize": 20,
                            "backdropColor": "transparent",
                            "color": "#8b949e",
                        },
                        "grid": {"color": "rgba(48, 54, 61, 0.8)"},
                        "pointLabels": {"color": "#c9d1d9", "font": {"size": 12}},
                    }
                }
            }
        }

    # ============================================================
    # 利润模型
    # ============================================================

    def generate_profit_waterfall(self) -> dict:
        """生成成本结构瀑布图"""
        profit = self.analysis.get("profit", {})
        cost_structure = profit.get("cost_structure", {})

        if not cost_structure:
            return {}

        return {
            "type": "bar",
            "title": "成本结构与利润分析",
            "subtitle": "以 $25 售价为例的成本拆解",
            "labels": list(cost_structure.keys()),
            "datasets": [{
                "label": "金额 (USD)",
                "data": list(cost_structure.values()),
                "backgroundColor": [
                    "#58a6ff", "#58a6ff", "#58a6ff",
                    "#58a6ff", "#58a6ff", "#58a6ff",
                    "#3fb950",
                ],
                "borderRadius": 4,
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "x": {
                        "ticks": {"maxRotation": 45, "minRotation": 0}
                    }
                }
            }
        }

    def generate_pricing_comparison(self) -> dict:
        """生成多档定价对比图"""
        tiers = self.analysis.get("profit", {}).get("pricing_tiers", [])

        if not tiers:
            return {}

        return {
            "type": "bar",
            "title": "多档定价利润对比",
            "subtitle": "各档位成本/利润/毛利率",
            "labels": [t.get("name", "") for t in tiers],
            "datasets": [
                {
                    "label": "成本",
                    "data": [t.get("cost", 0) for t in tiers],
                    "backgroundColor": "rgba(248, 81, 73, 0.7)",
                    "borderRadius": 4,
                },
                {
                    "label": "利润",
                    "data": [t.get("profit", 0) for t in tiers],
                    "backgroundColor": "rgba(63, 185, 80, 0.7)",
                    "borderRadius": 4,
                },
            ],
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "x": {"stacked": True},
                    "y": {"stacked": True},
                }
            }
        }

    # ============================================================
    # 供应商对比
    # ============================================================

    def generate_supplier_comparison(self) -> dict:
        """生成供应商报价区间图"""
        suppliers = self.supplier_data.get("suppliers", [])

        if not suppliers:
            return {}

        labels = [s.get("name", f"供应商{i}") for i, s in enumerate(suppliers)]
        costs = [s.get("unit_cost", 0) for s in suppliers]
        mos = [s.get("moq", 0) for s in suppliers]

        return {
            "type": "bar",
            "title": "1688 供应商报价与MOQ对比",
            "subtitle": "单位成本 (¥) vs 起订量",
            "labels": labels,
            "datasets": [{
                "label": "单价 (¥)",
                "data": costs,
                "backgroundColor": "#58a6ff99",
                "borderColor": "#58a6ff",
                "borderWidth": 1,
                "borderRadius": 4,
                "yAxisID": "y",
            }],
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "y": {
                        "title": {"display": True, "text": "单价 (¥)"},
                        "position": "left",
                    },
                }
            }
        }

    # ============================================================
    # Mock 数据生成器
    # ============================================================
    # 差异化建议生成
    # ============================================================

    def generate_differentiation_suggestions(self) -> List[dict]:
        """
        基于差评分析和 Reddit 洞察生成差异化建议

        Returns:
            差异化建议列表，每条包含方向、依据、机会评分
        """
        suggestions = []

        # 从差评痛点生成改进建议
        pain_categories = self.review_analysis.get("pain_categories", {})
        pain_points = self.review_analysis.get("pain_points", [])

        category_suggestions = {
            "产品质量": {
                "direction": "品质升级策略",
                "detail": "采用更高标准材料/工艺，将产品质量提升至超出消费者预期",
                "action": "对比竞品材质规格，升级到工业级/医疗级标准",
                "score": 90,
            },
            "功能问题": {
                "direction": "功能创新策略",
                "detail": "针对竞品功能缺陷，设计更符合用户场景的解决方案",
                "action": "通过 Reddit 用户需求分析，定位被忽略的使用场景",
                "score": 85,
            },
            "包装问题": {
                "direction": "包装体验优化",
                "detail": "从开箱体验、环保材料、防损设计三方面重构包装",
                "action": "引入易开设计、可回收材料、防泄漏密封",
                "score": 75,
            },
            "服务问题": {
                "direction": "服务差异化",
                "detail": "建立超越行业标准的售前售后服务体验",
                "action": "30天无条件退货 + 24小时客服 + 产品使用指南视频",
                "score": 70,
            },
            "期望落差": {
                "direction": "真实营销策略",
                "detail": "用真实用户场景和使用效果代替夸大宣传",
                "action": "Listing 中使用真实场景图 + 详细规格说明 + 使用对比",
                "score": 80,
            },
        }

        for cat, percentage in sorted(pain_categories.items(), key=lambda x: x[1], reverse=True):
            if cat in category_suggestions:
                info = category_suggestions[cat]
                suggestions.append({
                    "category": cat,
                    "pain_percentage": percentage,
                    "direction": info["direction"],
                    "detail": info["detail"],
                    "action": info["action"],
                    "score": info["score"],
                })

        # 从 Reddit 需求缺口生成建议
        reddit_topics = self.reddit_data.get("top_topics", {})
        if reddit_topics:
            gaps = self.reddit_data.get("demand_gaps", [])
            for gap in gaps[:3]:
                suggestions.append({
                    "category": "Reddit需求缺口",
                    "pain_percentage": gap.get("frequency", 0),
                    "direction": gap.get("opportunity", "市场空白"),
                    "detail": gap.get("description", ""),
                    "action": gap.get("action", ""),
                    "score": gap.get("score", 75),
                })

        # 如果没有足够数据，生成默认建议
        if not suggestions:
            suggestions = [
                {
                    "category": "产品质量",
                    "pain_percentage": 30,
                    "direction": "品质升级策略",
                    "detail": "竞品普遍存在材质和质量问题，提升品质是最直接的差异化路径",
                    "action": "调研竞品差评中高频质量问题，针对性地升级材料和工艺",
                    "score": 90,
                },
                {
                    "category": "期望落差",
                    "pain_percentage": 25,
                    "direction": "超预期体验设计",
                    "detail": "Reddit 用户多次提到'期望vs现实'的落差，超预期体验能迅速积累好评",
                    "action": "在产品中增加一个意外惊喜的小配件/功能，并在包装中体现品牌温度",
                    "score": 85,
                },
                {
                    "category": "功能问题",
                    "pain_percentage": 20,
                    "direction": "场景化功能创新",
                    "detail": "大部分竞品功能设计停留在基础层面，缺少对细分场景的深度优化",
                    "action": "分析 Reddit 用户实际使用场景，设计针对性功能模块",
                    "score": 82,
                },
            ]

        suggestions = sorted(suggestions, key=lambda x: x["score"], reverse=True)
        return attach_image_prompts(
            suggestions,
            category=self.metadata.get("category", ""),
            market=self.metadata.get("market", ""),
        )


# ============================================================
# 便捷函数
# ============================================================

def generate_chart_json(data: dict) -> str:
    """生成所有图表的 JSON 字符串，供 HTML 模板使用"""
    generator = ChartsGenerator(data)
    charts = generator.generate_all_charts()
    suggestions = generator.generate_differentiation_suggestions()

    result = {
        "charts": charts,
        "differentiation_suggestions": suggestions,
        "generated_at": datetime.now().isoformat(),
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 测试
    test_data = {
        "metadata": {
            "market": "US",
            "category": "kids supplements",
            "keywords": ["children's vitamins", "gummy vitamins"]
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
    charts = ChartsGenerator(test_data)
    data = charts.generate_all_charts()
    print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
    print("\n...")
    print(f"\n✅ 共生成 {len(data)} 个图表数据结构")
