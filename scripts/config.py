"""
Configuration Module v3.1
=========================

集中管理所有配置参数，支持环境变量和配置文件。

v3.1 更新:
  - 修复 Apify Actor ID 和参数格式
  - 已验证可用: ✅ Amazon Product / ✅ Amazon Reviews / ✅ TikTok
  - 不可用回退: Reddit/1688 → Web Search
  - 移除所有 mock 数据配置

使用方法:
    from config import CONFIG
    print(CONFIG["apify_token"])
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
MARKET_MAP = {
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
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "html")  # v2.0 默认 HTML 可视化
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
    
    # v3.1: Apify Actor 映射 (已验证可用标记 ✅)
    "apify_actors": {
        "amazon_product": {
            "id": "junglee/free-amazon-product-scraper",
            "status": "verified",
            "note": "必须使用 categoryUrls 参数（非 searchUrls）",
            "input_params": ["categoryUrls", "maxItems", "proxyConfiguration"],
        },
        "amazon_reviews": {
            "id": "junglee/amazon-reviews-scraper",
            "status": "verified",
            "note": "使用 productUrls 参数",
            "input_params": ["productUrls", "maxReviews", "filterByRatings"],
        },
        "tiktok_scraper": {
            "id": "clockworks/tiktok-scraper",
            "status": "verified",
            "note": "使用 hashtags 参数",
            "input_params": ["hashtags", "resultsPerPage", "proxyConfiguration"],
        },
        "reddit_scraper": {
            "id": "trudax/reddit-scraper",
            "status": "paid_only",
            "note": "已转为付费Actor，无免费版本可用",
            "fallback": "web_search",
        },
        "supplier_1688": {
            "ids": ["luzhiyu/1688-product-scraper", "easyapi/1688-product-scraper"],
            "status": "unavailable",
            "note": "无可用免费Actor",
            "fallback": "web_search",
        },
        "market_report": {
            "id": "apify/web-scraper",
            "status": "approval_required",
            "note": "需要账户审批才能使用",
            "fallback": "web_fetch + web_search",
        },
    },
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
# Reddit 采集配置 (NEW)
# ============================================================

REDDIT_CONFIG = {
    "enabled": os.getenv("REDDIT_ENABLED", "true").lower() == "true",
    "max_posts": 100,
    "default_subreddits": [
        "AmazonReviews",
        "FulfillmentByAmazon",
        "ecommerce",
        "ProductReviews",
        "BuyItForLife",
    ],
    "positive_keywords": [
        "love", "great", "best", "recommend", "excellent",
        "perfect", "amazing", "worth", "favorite"
    ],
    "negative_keywords": [
        "hate", "worst", "terrible", "avoid", "waste",
        "disappointed", "regret", "broke", "returned"
    ],
}

# ============================================================
# Google Trends 配置 (NEW)
# ============================================================

TRENDS_CONFIG = {
    "enabled": os.getenv("TRENDS_ENABLED", "true").lower() == "true",
    "timeframe": "today 5-y",
    "geo": "",  # 自动根据市场设置
    "category": 0,  # All categories
    "max_keywords": 5,
}

# ============================================================
# 差评分析配置 (NEW)
# ============================================================

REVIEW_ANALYSIS_CONFIG = {
    "enabled": os.getenv("REVIEW_ANALYSIS_ENABLED", "true").lower() == "true",
    "max_reviews_per_product": 50,
    "min_star_rating": 3,  # 采集 1-3 星评论
    "target_products": 20,  # 分析 Top 20 竞品
}

# ============================================================
# 消费者画像配置 (v3.0 NEW)
# ============================================================

CONSUMER_PERSONA_CONFIG = {
    "enabled": True,
    "persona_types": [
        "quality_first",      # 品质优先型
        "value_seeker",       # 性价比型
        "ingredient_focused", # 成分党
        "brand_loyal",        # 品牌忠诚型
        "trend_follower",     # 潮流追随型
    ],
    "analysis_dimensions": [
        "purchase_motivation",  # 购买动机
        "price_sensitivity",    # 价格敏感度
        "channel_preference",   # 渠道偏好
        "decision_chain",       # 决策链
        "usage_scenario",       # 使用场景
        "purchase_frequency",   # 购买频率
    ],
    "data_sources": ["reddit", "amazon_reviews", "tiktok_comments", "market_report"],
}

# ============================================================
# 五维趋势交叉验证配置 (v3.0 NEW)
# ============================================================

CROSS_VALIDATION_CONFIG = {
    "enabled": True,
    "dimensions": {
        "industry_data": {
            "label": "行业数据",
            "weight": 0.25,
            "sources": ["market_report", "grand_view_research", "mordor_intelligence"],
        },
        "tiktok_heat": {
            "label": "TikTok热度",
            "weight": 0.20,
            "sources": ["tiktok_scraper"],
        },
        "offline_channel": {
            "label": "线下渠道",
            "weight": 0.15,
            "sources": ["web_search", "walmart_target_data"],
        },
        "competitor_dynamics": {
            "label": "竞品动态",
            "weight": 0.20,
            "sources": ["amazon_scraper", "web_search"],
        },
        "policy_compliance": {
            "label": "政策合规",
            "weight": 0.20,
            "sources": ["fda_website", "ftc_website", "web_search"],
        },
    },
    "contradiction_threshold": 0.4,  # 任一维度与其他维度偏差>40%标记矛盾
    "min_dimensions_required": 3,     # 至少需要3个维度有数据才能做验证
}

# ============================================================
# 市场容量筛选配置 (v3.0 NEW)
# ============================================================

MARKET_CAPACITY_CONFIG = {
    "enabled": True,
    "screening_dimensions": {
        "ingredient": {               # 成分维度
            "label": "成分赛道",
            "max_items": 10,
        },
        "dosage_form": {              # 剂型维度
            "label": "剂型赛道",
            "max_items": 5,
            "default_forms": [
                "gummies", "capsules", "tablets", "liquid", "powder",
            ],
        },
        "price_band": {               # 价格带维度
            "label": "价格带",
            "bands": [
                {"min": 0, "max": 10, "label": "低价带"},
                {"min": 10, "max": 20, "label": "中低价带"},
                {"min": 20, "max": 35, "label": "中价带"},
                {"min": 35, "max": 50, "label": "中高价带"},
                {"min": 50, "max": 999, "label": "高价带"},
            ],
        },
    },
    "scoring_dimensions": [
        "market_size",        # 市场规模
        "growth_rate",        # 年增速
        "competition_level",  # 竞争度
        "entry_barrier",      # 进入壁垒
        "margin_potential",   # 利润潜力
    ],
}

# ============================================================
# 产品生命周期定位配置 (v3.0 NEW)
# ============================================================

LIFECYCLE_CONFIG = {
    "enabled": True,
    "stages": {
        "introduction": {
            "label": "导入期",
            "strategy": "教育市场",
            "pricing": "中高",
            "promotion": "内容营销+达人",
            "product": "MVP快速迭代",
        },
        "growth": {
            "label": "成长期",
            "strategy": "抢占份额",
            "pricing": "中",
            "promotion": "广告+达人+SEO",
            "product": "差异化+矩阵",
        },
        "maturity": {
            "label": "成熟期",
            "strategy": "利润最大化",
            "pricing": "中低",
            "promotion": "品牌+复购",
            "product": "微创新+成本优化",
        },
        "decline": {
            "label": "衰退期",
            "strategy": "退出/收割",
            "pricing": "低",
            "promotion": "减少",
            "product": "清库存",
        },
    },
    "judgment_indicators": [
        "search_trend_shape",      # 搜索趋势曲线形态
        "sku_growth_rate",         # SKU增速
        "avg_price_trend",         # 平均价格走势
        "new_product_success_rate", # 新品成功进入率
        "review_concentration_change", # 评论集中度变化
    ],
}

# ============================================================
# 研发壁垒构建配置 (v3.0 NEW)
# ============================================================

RND_MOAT_CONFIG = {
    "enabled": True,
    "moat_types": {
        "formula": {
            "label": "配方壁垒",
            "description": "专利配方/独家成分/技术配方",
            "build_difficulty": "高",
            "typical_timeline": "6-18月",
        },
        "supply_chain": {
            "label": "供应链壁垒",
            "description": "独家供应商/垂直整合/规模优势",
            "build_difficulty": "中",
            "typical_timeline": "3-12月",
        },
        "certification": {
            "label": "认证壁垒",
            "description": "FDA/GRAS/Organic/Non-GMO/Gluten-Free等",
            "build_difficulty": "中",
            "typical_timeline": "3-24月",
        },
        "brand": {
            "label": "品牌壁垒",
            "description": "品牌认知/口碑/社区/忠诚度",
            "build_difficulty": "高",
            "typical_timeline": "12-36月",
        },
        "patent": {
            "label": "专利壁垒",
            "description": "发明专利/外观专利/实用新型",
            "build_difficulty": "很高",
            "typical_timeline": "12-36月",
        },
    },
    "required_certifications": [
        "FDA Registration",
        "GMP Compliance",
        "Third-party Testing",
    ],
    "optional_certifications": [
        "USDA Organic",
        "Non-GMO Project Verified",
        "NSF Certified",
        "Gluten-Free Certified",
        "Vegan Certified",
        "B Corp",
    ],
}

# ============================================================
# 风险评估与"为什么不选"配置 (v3.0 NEW)
# ============================================================

RISK_CONFIG = {
    "enabled": True,
    "false_blue_ocean_detection": {
        "min_search_volume": 10000,
        "trend_keywords": ["declining", "seasonal"],
        "min_gross_margin": 25,
        "max_brand_concentration": 40,
        "min_new_product_count": 5,
    },
    "risk_categories": [
        "market_risk",      # 市场风险
        "competition_risk", # 竞争风险
        "policy_risk",      # 政策风险
        "supply_risk",      # 供应链风险
        "execution_risk",   # 执行风险
    ],
    "why_not_choose": {
        "min_reasons": 3,   # 强制至少3条反对理由
        "max_reasons": 6,
        "require_data_backed": True,  # 每条理由必须基于真实数据
    },
}

# ============================================================
# 90天执行路线图配置 (v3.0 NEW)
# ============================================================

EXECUTION_ROADMAP_CONFIG = {
    "enabled": True,
    "phases": [
        {
            "phase": 1,
            "name": "供应链搭建",
            "days": "1-30",
            "milestones": [
                "供应商筛选完成",
                "打样确认",
                "小批量下单",
                "包材设计",
            ],
        },
        {
            "phase": 2,
            "name": "Listing上线",
            "days": "31-60",
            "milestones": [
                "视觉内容拍摄",
                "Listing文案优化",
                "关键词布局",
                "FBA入仓",
            ],
        },
        {
            "phase": 3,
            "name": "冷启动验证",
            "days": "61-90",
            "milestones": [
                "广告测试启动",
                "达人合作首批",
                "首批评价获取",
                "数据复盘",
            ],
        },
    ],
    "resource_categories": [
        "product_procurement",
        "advertising",
        "influencer",
        "content_creation",
        "tools_software",
    ],
}

# ============================================================
# 数据溯源配置 (v3.0 NEW)
# ============================================================

DATA_LINEAGE_CONFIG = {
    "enabled": True,
    "per_section": True,           # 每个章节底部标注数据来源
    "format": "collapsible",       # 可折叠的数据溯源块
    "required_fields": [
        "source_name",             # Apify actor / 网站域名 / 报告名称
        "source_url",              # 数据来源URL（如有）
        "collection_date",         # 采集/获取时间
        "data_scope",              # 数据范围（采集条数/时间跨度等）
    ],
    "data_source_mapping": {
        "amazon_products": "Apify Amazon (junglee/free-amazon-product-scraper)",
        "amazon_reviews": "Apify Amazon Reviews (junglee/amazon-reviews-scraper)",
        "tiktok_data": "Apify TikTok (clockworks/tiktok-scraper)",
        "reddit_data": "Reddit (Web Search 补充)",
        "1688_supplier": "1688 (Web Search 补充)",
        "market_report": "行业报告 (Grand View Research / Mordor Intelligence / TBRC 等)",
        "google_trends": "Google Trends (pytrends, 中国网络受限)",
        "web_search": "联网搜索验证",
        "fda_website": "FDA官网",
    },
}

# ============================================================
# 选品标准配置 (v3.0 更新)
# ============================================================

SELECTION_CRITERIA = {
    # 市场指标
    "search_volume": {
        "min": 20000,              # 最少 2万/月
        "max": 100000,             # 最多 10万/月
        "weight": 0.15,            # v2: 下调，引入新指标
    },
    "brand_concentration": {
        "max": 0.30,               # Top 10 品牌 < 30%
        "weight": 0.10,            # v2: 下调
    },
    "cpc": {
        "max": 1.0,                # CPC < $1
        "weight": 0.10,
    },

    # 利润指标
    "profit_margin": {
        "min": 0.30,               # 净利润 > 30%
        "weight": 0.20,
    },

    # TikTok 指标
    "tiktok_views": {
        "min": 10000000,           # 播放量 > 1000万
        "weight": 0.10,
    },

    # 供应链指标
    "supplier_stability": {
        "min": 4.0,                # 供应商评分 > 4.0
        "weight": 0.10,
    },

    # v2.0 新增指标
    "review_improvable": {         # 差评可改进空间
        "min_score": 60,
        "weight": 0.15,
    },
    "reddit_demand": {             # Reddit 需求验证
        "min_posts": 30,
        "weight": 0.10,
    },
}

# ============================================================
# 报告配置
# ============================================================

REPORT_CONFIG = {
    "format": OUTPUT_FORMAT,
    "title_template": "{market}市场{category}深度选品调研报告",
    "include_sections": [
        # v3.0 15章结构
        "ch01_executive_summary",        # 执行摘要仪表盘
        "ch02_market_product_definition", # 市场与产品定义
        "ch03_demand_persona",            # 需求逻辑与消费者画像
        "ch04_cross_validation",          # 五维趋势交叉验证
        "ch05_market_capacity",           # 市场容量筛选
        "ch06_lifecycle",                 # 产品生命周期定位
        "ch07_competition_benchmarking",  # 竞争格局与对标
        "ch08_pain_point_analysis",       # 差评痛点深度分析
        "ch09_reddit_insights",           # Reddit 用户洞察
        "ch10_tiktok_validation",         # TikTok 流量验证
        "ch11_supply_chain",              # 供应链与成本验证
        "ch12_profit_model",              # 利润模型构建
        "ch13_rd_moat",                   # 研发壁垒构建
        "ch14_differentiation_matrix",    # 差异化选品与产品矩阵
        "ch15_risk_why_not",              # 风险评估与"为什么不选"
        "ch16_execution_roadmap",         # 90天执行路线图
    ],
    "include_charts": True,
    "include_data_tables": True,
    "include_wordcloud": True,
    "include_data_lineage": True,    # v3.0 NEW: 每章数据溯源标注
    "html_theme": "dark",
    "html_accent": "#58a6ff",
    # v3.0 数据溯源样式
    "data_lineage_style": "collapsible",  # 可折叠展开
    "data_lineage_position": "bottom",    # 每章底部
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
    "supported_markets": MARKET_MAP,

    # 采集
    "collection": COLLECTION_CONFIG,

    # TikTok
    "tiktok": TIKTOK_CONFIG,

    # Reddit
    "reddit": REDDIT_CONFIG,

    # Google Trends
    "trends": TRENDS_CONFIG,

    # 差评分析
    "review_analysis": REVIEW_ANALYSIS_CONFIG,

    # 利润
    "profit": PROFIT_CONFIG,

    # 选品标准
    "selection_criteria": SELECTION_CRITERIA,

    # v3.0 新增维度
    "consumer_persona": CONSUMER_PERSONA_CONFIG,       # 消费者画像
    "cross_validation": CROSS_VALIDATION_CONFIG,       # 五维交叉验证
    "market_capacity": MARKET_CAPACITY_CONFIG,         # 市场容量筛选
    "lifecycle": LIFECYCLE_CONFIG,                     # 产品生命周期
    "rd_moat": RND_MOAT_CONFIG,                        # 研发壁垒
    "risk": RISK_CONFIG,                               # 风险评估
    "execution_roadmap": EXECUTION_ROADMAP_CONFIG,     # 90天执行路线图
    "data_lineage": DATA_LINEAGE_CONFIG,               # 数据溯源

    # 报告
    "report": REPORT_CONFIG,

    # 日志
    "log": LOG_CONFIG,

    # 输出
    "output_format": OUTPUT_FORMAT,
    "output_dir": OUTPUT_DIR,
}
