"""
Data Collector Module
=====================

负责从各个数据源采集数据：
- Amazon 商品数据
- 1688 供应商成本数据
- TikTok 流量数据
- 市场报告数据
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from config import CONFIG, MARKET_MAP


class DataCollector:
    """数据采集器"""

    def __init__(self, market: str, config: dict):
        self.market = market.upper()
        self.config = config
        self.collection_config = config.get("collection", {})
        self.supplier_config = config.get("supplier", {})
        self.api_token = config.get("apify_token", "")

        # 获取市场配置
        self.market_config = MARKET_MAP.get(self.market, MARKET_MAP["US"])

    def fetch_amazon_products(self, keywords: List[str]) -> List[Dict]:
        """
        采集 Amazon 商品数据

        Args:
            keywords: 关键词列表

        Returns:
            商品数据列表
        """
        products = []

        for keyword in keywords:
            print(f"      采集关键词: {keyword}")
            # 这里调用实际的采集逻辑
            # 1. 如果有 API Token，调用 Apify
            # 2. 否则使用 selenium 采集
            products.extend(self._collect_keyword(keyword))

            # 请求间隔
            time.sleep(self.collection_config.get("request_delay", 2))

        return products

    def fetch_supplier_costs(self, category: str, keywords: List[str]) -> List[Dict]:
        """
        采集 1688 供应商成本数据。

        Args:
            category: 产品类目
            keywords: Amazon/市场关键词列表

        Returns:
            标准化后的 1688 供应商数据列表
        """
        if not self.supplier_config.get("enabled", True):
            return []

        supplier_keywords = self._build_supplier_keywords(category, keywords)
        actor_id = self.supplier_config.get("apify_actor_id", "")

        if actor_id and self.api_token:
            print(f"      使用 Apify Actor 采集 1688: {actor_id}")
            collector = ApifyCollector(self.api_token)
            input_data = {
                "keywords": supplier_keywords,
                "maxItemsPerKeyword": self.supplier_config.get("results_per_keyword", 20),
                "source": "1688",
            }
            raw_items = collector.run_actor(actor_id, input_data)
            return self._normalize_supplier_items(raw_items, supplier_keywords)

        print("      未配置 APIFY_1688_ACTOR_ID，生成 1688 成本占位结构")
        return [
            {
                "keyword": keyword,
                "title": "",
                "supplier_name": "",
                "price_min_rmb": None,
                "price_max_rmb": None,
                "moq": None,
                "monthly_sales": None,
                "transaction_count": None,
                "supplier_years": None,
                "rating": None,
                "repurchase_rate": None,
                "location": "",
                "product_url": "",
                "image_url": "",
                "source": "1688",
                "collected_at": datetime.now().isoformat(),
                "note": "APIFY_1688_ACTOR_ID 未配置，未能自动采集真实 1688 报价",
            }
            for keyword in supplier_keywords
        ]

    def _build_supplier_keywords(self, category: str, keywords: List[str]) -> List[str]:
        """根据类目和关键词生成 1688 中文供应商搜索词。"""
        seed_terms = [category] + list(keywords or [])
        joined = " ".join(seed_terms).lower()
        suggestions = []

        keyword_map = {
            "kids": ["儿童", "儿童用品"],
            "children": ["儿童", "儿童用品"],
            "vitamin": ["维生素", "营养品"],
            "supplement": ["保健品", "营养补充剂"],
            "probiotic": ["益生菌", "益生菌代工"],
            "gummy": ["软糖", "凝胶糖果", "软糖 OEM"],
            "pet": ["宠物用品", "宠物保健品"],
            "beauty": ["美妆", "护肤品"],
            "skincare": ["护肤品", "护肤品代工"],
        }

        for token, mapped_terms in keyword_map.items():
            if token in joined:
                suggestions.extend(mapped_terms)

        if suggestions:
            base = "".join(dict.fromkeys(suggestions[:3]))
            suggestions.extend([base, f"{base} OEM", f"{base} 源头工厂"])
        else:
            suggestions.extend([category, f"{category} OEM", f"{category} 源头工厂"])

        deduped = []
        for keyword in suggestions:
            keyword = keyword.strip()
            if keyword and keyword not in deduped:
                deduped.append(keyword)

        return deduped[: self.supplier_config.get("keywords_max", 8)]

    def _normalize_supplier_items(self, raw_items: List[Dict], keywords: List[str]) -> List[Dict]:
        """将不同 1688 Actor 返回结果标准化为统一字段。"""
        normalized = []
        for item in raw_items or []:
            price = item.get("price") or item.get("price_min") or item.get("priceMin")
            price_max = item.get("price_max") or item.get("priceMax") or price
            normalized.append({
                "keyword": item.get("keyword") or item.get("searchKeyword") or (keywords[0] if keywords else ""),
                "title": item.get("title") or item.get("name") or "",
                "supplier_name": item.get("supplier_name") or item.get("supplierName") or item.get("shopName") or "",
                "price_min_rmb": self._to_float(price),
                "price_max_rmb": self._to_float(price_max),
                "moq": self._to_int(item.get("moq") or item.get("minOrderQuantity")),
                "monthly_sales": self._to_int(item.get("monthly_sales") or item.get("monthlySales")),
                "transaction_count": self._to_int(item.get("transaction_count") or item.get("transactionCount") or item.get("sales")),
                "supplier_years": self._to_int(item.get("supplier_years") or item.get("supplierYears")),
                "rating": self._to_float(item.get("rating") or item.get("shopRating")),
                "repurchase_rate": item.get("repurchase_rate") or item.get("repurchaseRate"),
                "location": item.get("location") or item.get("province") or "",
                "product_url": item.get("product_url") or item.get("url") or item.get("link") or "",
                "image_url": item.get("image_url") or item.get("image") or item.get("mainImage") or "",
                "source": "1688",
                "collected_at": datetime.now().isoformat(),
            })

        return normalized

    @staticmethod
    def _to_float(value):
        try:
            return float(str(value).replace("¥", "").replace(",", "").strip())
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_int(value):
        try:
            return int(float(str(value).replace(",", "").strip()))
        except (TypeError, ValueError):
            return None

    def _collect_keyword(self, keyword: str) -> List[Dict]:
        """采集单个关键词的数据"""
        # TODO: 实现实际采集逻辑
        # 目前返回示例数据结构
        return [
            {
                "asin": "B08N5WRWNW",
                "title": "Sample Product Title",
                "price": 19.99,
                "rating": 4.5,
                "review_count": 1234,
                "bsr_rank": 100,
                "brand": "Sample Brand",
                "keyword": keyword,
                "market": self.market,
            }
        ]

    def fetch_tiktok_data(self, keywords: List[str]) -> List[Dict]:
        """
        采集 TikTok 数据

        Args:
            keywords: 关键词列表

        Returns:
            TikTok 数据列表
        """
        tiktok_data = []

        for keyword in keywords:
            # TODO: 调用 TikTok 采集逻辑
            tiktok_data.extend(self._collect_tiktok_keyword(keyword))

        return tiktok_data

    def _collect_tiktok_keyword(self, keyword: str) -> List[Dict]:
        """采集单个关键词的 TikTok 数据"""
        # TODO: 实现实际采集逻辑
        return [
            {
                "hashtag": f"#{keyword.replace(' ', '')}",
                "views": 10000000,
                "videos": 500,
                "keyword": keyword,
            }
        ]

    def fetch_market_data(self, category: str) -> Dict:
        """
        采集市场数据

        Args:
            category: 产品类目

        Returns:
            市场数据字典
        """
        # TODO: 调用市场数据采集逻辑
        return {
            "category": category,
            "market_size": "1000000000",  # 市场规模 (USD)
            "cagr": 0.08,  # 年增长率
            "top_players": [],
            "trends": [],
        }


class ApifyCollector:
    """Apify API 数据采集器"""

    def __init__(self, api_token: str):
        self.api_token = api_token

    def run_actor(self, actor_id: str, input_data: dict) -> dict:
        """
        运行 Apify Actor

        Args:
            actor_id: Actor ID
            input_data: 输入数据

        Returns:
            Actor 运行结果
        """
        try:
            from apify_client import ApifyClient

            client = ApifyClient(self.api_token)

            # 启动 Actor
            actor_call = client.actor(actor_id).start(input_data)

            # 等待完成
            actor_run = client.actor(actor_id).run(input_data)

            # 获取数据
            dataset = client.dataset(actor_run["defaultDatasetId"])
            items = dataset.list_items().items

            return items

        except ImportError:
            print("⚠️  请安装 apify-client: pip install apify-client")
            return []
        except Exception as e:
            print(f"⚠️  Apify API 调用失败: {e}")
            return []


def collect_sample_data(category: str, market: str = "US") -> dict:
    """
    生成示例数据用于测试

    Args:
        category: 类目
        market: 市场

    Returns:
        模拟的数据字典
    """
    return {
        "metadata": {
            "market": market,
            "category": category,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "amazon": [
            {
                "asin": f"ASIN{i:08d}",
                "title": f"Sample Product {i}",
                "price": 19.99 + i,
                "rating": 4.0 + (i % 10) * 0.1,
                "review_count": 100 * i,
                "bsr_rank": 100 + i * 10,
                "brand": f"Brand{i % 5}",
            }
            for i in range(1, 11)
        ],
        "tiktok": [
            {
                "hashtag": f"#{category.replace(' ', '')}",
                "views": 10000000,
                "videos": 500,
            }
        ],
        "supplier": [
            {
                "keyword": f"{category} OEM",
                "title": "Sample 1688 Supplier Product",
                "supplier_name": "Sample Supplier",
                "price_min_rmb": 8.0,
                "price_max_rmb": 12.0,
                "moq": 1000,
                "transaction_count": 5000,
                "supplier_years": 5,
                "rating": 4.6,
                "repurchase_rate": "32%",
                "location": "Guangdong",
                "product_url": "https://www.1688.com/",
                "source": "1688",
                "collected_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        ],
        "market": {
            "category": category,
            "market_size": "$1B",
            "cagr": "8%",
        },
    }
