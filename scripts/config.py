"""
Configuration Module
====================

集中管理所有配置参数，支持环境变量和配置文件。

使用方法:
    from config import CONFIG
    print(CONFIG["max_products"])
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# ============================================================
# 基础配置
# ============================================================

# API 配置
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")

# 市场配置
DEFAULT_MARKET = os.getenv("DEFAULT_MARKET", "US")
SUPPORTED_MARKETS = {
    "US": {"domain": "amazon.com", "currency": "USD", "locale": "en-US"},
    "UK": {"domain": "amazon.co.uk", "currency": "GBP", "locale": "en-GB"},
    "DE": {"domain": "amazon.de", "currency": "EUR", "locale": "de-DE"},
    "FR": {"domain": "amazon.fr", "currency": "EUR", "locale": "fr-FR"},
    "IT": {"domain": "amazon.it", "currency": "EUR", "locale": "it-IT"},
    "ES": {"domain": "amazon.es", "currency": "EUR", "locale": "es-ES"},
    "JP": {"domain": "amazon.co.jp", "currency": "JPY", "locale": "ja-JP"},
    "CA": {"domain": "amazon.ca", "currency": "CAD", "locale": "en-CA"},
    "AU": {"domain": "amazon.com.au", "currency": "AUD", "locale": "en-AU"},
}

# 输出配置
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "markdown")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")

# ============================================================
# 采集配置
# ============================================================

COLLECTION_CONFIG = {
    # 基础参数
    "max_products": int(os.getenv("MAX_PRODUCTS", "100")),
    "min_review_count": int(os.getenv("MIN_REVIEW_COUNT", "50")),
    "min_rating": float(os.getenv("MIN_RATING", "4.0")),

    # 价格区间 (USD)
    "price_range": (
        float(os.getenv("MIN_PRICE", "10")),
        float(os.getenv("MAX_PRICE", "50"))
    ),

    # 采集深度
    "max_pages": 5,
    "include_sponsored": False,

    # 请求参数
    "request_delay": float(os.getenv("REQUEST_DELAY", "2")),
    "retry_times": int(os.getenv("RETRY_TIMES", "3")),
    "timeout": 30,

    # 代理配置
    "proxy_enabled": os.getenv("PROXY_ENABLED", "false").lower() == "true",
    "proxy_url": os.getenv("PROXY_URL", ""),

    # 浏览器配置
    "headless": True,
    "user_agent": "",

    # 数据存储
    "save_raw_data": True,
    "save_processed": True,
    "save_reports": True,
}

# ============================================================
# TikTok 配置
# ============================================================

TIKTOK_CONFIG = {
    # 标签列表
    "hashtags": os.getenv("TIKTOK_HASHTAGS", "").split(",") if os.getenv("TIKTOK_HASHTAGS") else [],

    # 采集数量
    "max_videos": 50,
    "max_creators": 20,

    # 内容类型
    "content_types": [
        "product_review",
        "unboxing",
        "how_to",
        "before_after",
        "lifestyle"
    ],
}

# ============================================================
# 利润模型配置
# ============================================================

PROFIT_CONFIG = {
    # 固定成本 (USD)
    "product_cost": 5.0,           # 产品成本
    "shipping_cost": 0.5,          # 头程运费
    "packaging_cost": 0.3,         # 包材成本

    # 平台费率
    "platform_fee_rate": 0.15,     # 平台佣金 15%
    "fba_fulfillment_fee": 3.5,   # FBA 履约费

    # 变动成本
    "refund_rate": 0.03,          # 退款率 3%
    "advertising_rate": 0.20,      # 广告占比 20%
    "exchange_loss": 0.01,         # 汇损 1%

    # 定价策略
    "default_markup": 2.5,         # 默认加价倍率
    "min_margin": 0.30,           # 最低利润率
}

# ============================================================
# 选品标准配置
# ============================================================

SELECTION_CRITERIA = {
    # 市场指标
    "search_volume": {
        "min": 20000,              # 最少 2万/月
        "max": 100000,             # 最多 10万/月
        "weight": 0.20,
    },
    "brand_concentration": {
        "max": 0.30,               # Top 10 品牌 < 30%
        "weight": 0.15,
    },
    "cpc": {
        "max": 1.0,                # CPC < $1
        "weight": 0.10,
    },

    # 利润指标
    "profit_margin": {
        "min": 0.30,               # 净利润 > 30%
        "weight": 0.25,
    },

    # TikTok 指标
    "tiktok_views": {
        "min": 10000000,           # 播放量 > 1000万
        "weight": 0.15,
    },

    # 供应链指标
    "review_rating": {
        "min": 4.0,                # 评分 > 4.0
        "weight": 0.15,
    },
}

# ============================================================
# 报告配置
# ============================================================

REPORT_CONFIG = {
    "format": OUTPUT_FORMAT,
    "include_sections": [
        "executive_summary",
        "market_overview",
        "demand_analysis",
        "competition_analysis",
        "tiktok_validation",
        "profit_model",
        "product_matrix",
        "execution_plan",
        "risk_assessment",
        "recommendations",
    ],
    "include_charts": True,
    "include_data_tables": True,
}

# ============================================================
# 日志配置
# ============================================================

LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    "rotation": "10 MB",
    "retention": "7 days",
}

# ============================================================
# 合并为统一配置
# ============================================================

CONFIG = {
    # API
    "apify_token": APIFY_API_TOKEN,

    # 市场
    "default_market": DEFAULT_MARKET,
    "supported_markets": SUPPORTED_MARKETS,

    # 采集
    "collection": COLLECTION_CONFIG,

    # TikTok
    "tiktok": TIKTOK_CONFIG,

    # 利润
    "profit": PROFIT_CONFIG,

    # 选品标准
    "selection_criteria": SELECTION_CRITERIA,

    # 报告
    "report": REPORT_CONFIG,

    # 日志
    "log": LOG_CONFIG,

    # 输出
    "output_format": OUTPUT_FORMAT,
    "output_dir": OUTPUT_DIR,
}
