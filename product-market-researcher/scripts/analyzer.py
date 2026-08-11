"""
Analyzers Module
================

数据分析和建模模块：
- MarketAnalyzer: 市场分析
- TikTokAnalyzer: TikTok 传播分析
- ProfitModelBuilder: 利润模型构建
"""

from typing import Dict, List
from config import SELECTION_CRITERIA, PROFIT_CONFIG
from image_prompt_builder import attach_image_prompts


class MarketAnalyzer:
    """市场分析器"""

    def __init__(self, data: dict):
        self.data = data
        self.amazon_data = data.get("amazon", [])
        self.market_data = data.get("market", {})

    def analyze(self) -> Dict:
        """
        执行市场分析

        Returns:
            市场分析结果
        """
        return {
            "market_size": self._analyze_market_size(),
            "brand_concentration": self._analyze_brand_concentration(),
            "price_distribution": self._analyze_price_distribution(),
            "rating_distribution": self._analyze_rating_distribution(),
            "blue_ocean_opportunities": self._identify_blue_ocean(),
            "scores": self._calculate_market_scores(),
        }

    def _analyze_market_size(self) -> Dict:
        """分析市场规模"""
        return {
            "estimated_size": self.market_data.get("market_size", "Unknown"),
            "cagr": self.market_data.get("cagr", 0),
            "total_products": len(self.amazon_data),
        }

    def _analyze_brand_concentration(self) -> Dict:
        """分析品牌集中度"""
        brands = {}
        for product in self.amazon_data:
            brand = product.get("brand", "Unknown")
            brands[brand] = brands.get(brand, 0) + 1

        total = len(self.amazon_data)
        brand_shares = {b: c / total for b, c in brands.items()}

        # Top 10 品牌集中度
        top10_share = sum(sorted(brand_shares.values(), reverse=True)[:10])

        return {
            "unique_brands": len(brands),
            "top10_concentration": top10_share,
            "is_concentrated": top10_share > 0.5,
            "recommendation": "推荐进入" if top10_share < 0.3 else "需要差异化",
        }

    def _analyze_price_distribution(self) -> Dict:
        """分析价格分布"""
        prices = [p.get("price", 0) for p in self.amazon_data if p.get("price")]

        if not prices:
            return {}

        return {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices),
            "median": sorted(prices)[len(prices) // 2],
        }

    def _analyze_rating_distribution(self) -> Dict:
        """分析评分分布"""
        ratings = [p.get("rating", 0) for p in self.amazon_data if p.get("rating")]

        if not ratings:
            return {}

        return {
            "avg": sum(ratings) / len(ratings),
            "distribution": {
                "5_star": len([r for r in ratings if r >= 4.5]),
                "4_star": len([r for r in ratings if 4.0 <= r < 4.5]),
                "3_star": len([r for r in ratings if 3.0 <= r < 4.0]),
                "below_3": len([r for r in ratings if r < 3.0]),
            }
        }

    def _identify_blue_ocean(self) -> List[Dict]:
        """识别蓝海市场机会"""
        opportunities = []

        # 基于分析结果识别机会
        brand_analysis = self._analyze_brand_concentration()
        if brand_analysis["top10_concentration"] < 0.3:
            opportunities.append({
                "type": "low_concentration",
                "title": "品牌分散机会",
                "description": "Top 10 品牌集中度低，新品牌有机会",
                "score": 90,
            })

        price_analysis = self._analyze_price_distribution()
        if price_analysis.get("avg", 0) < 30:
            opportunities.append({
                "type": "price_gap",
                "title": "价格带机会",
                "description": "市场以中低价位为主，可布局中高端",
                "score": 85,
            })

        return attach_image_prompts(
            opportunities,
            category=self.data.get("metadata", {}).get("category", ""),
            market=self.data.get("metadata", {}).get("market", ""),
        )

    def _calculate_market_scores(self) -> Dict:
        """计算市场综合评分"""
        criteria = SELECTION_CRITERIA

        scores = {
            "search_volume": 0.8,  # TODO: 接入真实数据
            "brand_concentration": 0.2,  # TODO: 计算真实值
            "profit_margin": 0.7,
            "tiktok_views": 0.6,
        }

        return scores


class TikTokAnalyzer:
    """TikTok 传播分析器"""

    def __init__(self, data: dict):
        self.data = data
        self.tiktok_data = data.get("tiktok", [])

    def analyze(self) -> Dict:
        """
        分析 TikTok 传播潜力

        Returns:
            TikTok 分析结果
        """
        return {
            "hashtag_performance": self._analyze_hashtags(),
            "content_types": self._analyze_content_types(),
            "creator_landscape": self._analyze_creators(),
            "virality_score": self._calculate_virality_score(),
            "recommendations": self._generate_recommendations(),
        }

    def _analyze_hashtags(self) -> List[Dict]:
        """分析标签表现"""
        totals = {}
        for video in self.tiktok_data:
            hashtags = video.get("hashtags") or video.get("hashtag") or []
            if isinstance(hashtags, str):
                hashtags = [hashtags]
            for hashtag in hashtags:
                name = hashtag.get("name", "") if isinstance(hashtag, dict) else str(hashtag)
                name = name if name.startswith("#") else f"#{name}"
                if name == "#":
                    continue
                row = totals.setdefault(name, {"hashtag": name, "views": 0, "videos": 0})
                row["views"] += video.get("views", video.get("plays", 0)) or 0
                row["videos"] += 1
        return sorted(totals.values(), key=lambda item: item["views"], reverse=True)

    def _analyze_content_types(self) -> Dict:
        """分析内容类型"""
        return {
            "product_review": {"popularity": "high", "engagement": 0.05},
            "unboxing": {"popularity": "medium", "engagement": 0.03},
            "how_to": {"popularity": "high", "engagement": 0.07},
        }

    def _analyze_creators(self) -> Dict:
        """分析创作者生态"""
        return {
            "top_creators": 10,
            "mid_tier_creators": 50,
            "niche_creators": 200,
        }

    def _calculate_virality_score(self) -> float:
        """计算病毒传播评分"""
        total_views = sum(t.get("views", 0) for t in self.tiktok_data)

        if total_views > 100000000:
            return 0.9
        elif total_views > 10000000:
            return 0.7
        elif total_views > 1000000:
            return 0.5
        else:
            return 0.3

    def _generate_recommendations(self) -> List[str]:
        """生成 TikTok 营销建议"""
        return [
            "优先布局 #howto 类内容，教育用户",
            "寻找腰部达人合作，性价比最高",
            "制作 15-30 秒的短视频，突出核心卖点",
        ]


class ProfitModelBuilder:
    """利润模型构建器"""

    def __init__(self, data: dict):
        self.data = data
        self.config = PROFIT_CONFIG

    def build(self) -> Dict:
        """
        构建利润模型

        Returns:
            利润模型结果
        """
        return {
            "cost_structure": self._calculate_cost_structure(),
            "pricing_tiers": self._calculate_pricing_tiers(),
            "profit_analysis": self._analyze_profits(),
            "recommendations": self._generate_recommendations(),
        }

    def _calculate_cost_structure(self, sale_price: float = 25.0) -> Dict:
        """
        计算成本结构

        Args:
            sale_price: 售价

        Returns:
            成本结构
        """
        cogs = (
            self.config["product_cost"]
            + self.config["shipping_cost"]
            + self.config["packaging_cost"]
        )

        platform_fee = sale_price * self.config["platform_fee_rate"]
        fba_fee = self.config["fba_fulfillment_fee"]
        refund = sale_price * self.config["refund_rate"]
        advertising = sale_price * self.config["advertising_rate"]
        exchange_loss = sale_price * self.config["exchange_loss"]

        total_cost = cogs + platform_fee + fba_fee + refund + advertising + exchange_loss
        net_profit = sale_price - total_cost

        return {
            "sale_price": sale_price,
            "cogs": cogs,
            "platform_fee": platform_fee,
            "fba_fee": fba_fee,
            "refund": refund,
            "advertising": advertising,
            "exchange_loss": exchange_loss,
            "total_cost": total_cost,
            "net_profit": net_profit,
            "gross_margin": (sale_price - cogs) / sale_price,
            "net_margin": net_profit / sale_price,
        }

    def _calculate_pricing_tiers(self) -> List[Dict]:
        """
        计算不同定价档位

        Returns:
            定价方案列表
        """
        tiers = [
            {"name": "引流款", "price": 14.99, "role": "traffic"},
            {"name": "主打款", "price": 22.99, "role": "main"},
            {"name": "利润款", "price": 29.99, "role": "profit"},
            {"name": "高端款", "price": 39.99, "role": "premium"},
        ]

        for tier in tiers:
            cost_analysis = self._calculate_cost_structure(tier["price"])
            tier.update({
                "cost": cost_analysis["total_cost"],
                "profit": cost_analysis["net_profit"],
                "margin": cost_analysis["net_margin"],
            })

        return tiers

    def _analyze_profits(self) -> Dict:
        """分析利润空间"""
        tiers = self._calculate_pricing_tiers()

        return {
            "min_profitable_price": self._find_min_profitable_price(),
            "optimal_price_range": (20, 35),
            "recommended_tier": tiers[1],  # 主打款
        }

    def _find_min_profitable_price(self) -> float:
        """找到最低盈利价格"""
        for price in range(5, 100):
            cost_analysis = self._calculate_cost_structure(price)
            if cost_analysis["net_margin"] >= self.config["min_margin"]:
                return price
        return 100

    def _generate_recommendations(self) -> List[str]:
        """生成利润优化建议"""
        return [
            "定价建议: $20-35 区间利润空间最佳",
            "成本优化: 寻找更优供应商，降低 COGS 10%",
            "广告控制: ACOS 控制在 25% 以内",
            "退款率: 建立品控体系，将退款率控制在 3% 以下",
        ]
