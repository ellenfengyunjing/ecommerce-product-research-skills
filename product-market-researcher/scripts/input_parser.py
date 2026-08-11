"""
Input Parser Module
===================

解析用户的自然语言输入，提取市场、类目和关键词信息。

支持的输入格式:
    "分析美国市场儿童保健品类目的选品机会"
    "US, kids supplements, children's vitamins"
    {"market": "US", "category": "kids supplements"}
"""

import re
from typing import Dict, List, Optional


# 市场映射表
MARKET_MAP = {
    # 英文代码
    "US": "US", "UK": "UK", "GB": "UK",
    "DE": "DE", "GERMANY": "DE",
    "FR": "FR", "FRANCE": "FR",
    "IT": "IT", "ITALY": "IT",
    "ES": "ES", "SPAIN": "ES",
    "JP": "JP", "JAPAN": "JP",
    "CA": "CA", "CANADA": "CA",
    "AU": "AU", "AUSTRALIA": "AU",
    "IN": "IN", "INDIA": "IN",

    # 中文名称
    "美国": "US", "美区": "US", "美站": "US",
    "英国": "UK", "英区": "UK", "英站": "UK",
    "德国": "DE", "德区": "DE", "德站": "DE",
    "法国": "FR", "法区": "FR", "法站": "FR",
    "意大利": "IT", "意区": "IT",
    "西班牙": "ES", "西班区": "ES",
    "日本": "JP", "日区": "JP", "日站": "JP",
    "加拿大": "CA", "加区": "CA",
    "澳洲": "AU", "澳大利亚": "AU",
    "印度": "IN",
}

# 类目扩展关键词
CATEGORY_EXPANSIONS = {
    "supplements": ["vitamins", "health supplements", "nutritional supplements"],
    "vitamins": ["multivitamin", "vitamin c", "vitamin d", "b-complex"],
    "probiotics": ["probiotic supplements", "gut health", "digestive health"],
    "kids": ["children", "child", "toddler", "infant", "baby"],
    "pet": ["dog", "cat", "pets", "animal"],
    "beauty": ["skincare", "cosmetics", "makeup", "skin care"],
    "health": ["wellness", "healthcare", "healthy"],
}


def normalize_market(text: str) -> Optional[str]:
    """从文本中提取并标准化市场代码"""
    text = text.strip().upper()

    # 直接匹配
    if text in MARKET_MAP:
        return MARKET_MAP[text]

    # 模糊匹配
    for key, value in MARKET_MAP.items():
        if key.lower() in text.lower() or key in text:
            return value

    return None


def expand_keywords(keywords: List[str]) -> List[str]:
    """扩展关键词列表"""
    expanded = list(keywords)

    for keyword in keywords:
        keyword_lower = keyword.lower()

        # 检查是否需要扩展
        for base, expansions in CATEGORY_EXPANSIONS.items():
            if base in keyword_lower:
                for exp in expansions:
                    if exp not in expanded:
                        expanded.append(exp)

    return expanded


def parse_chinese_input(text: str) -> Dict:
    """解析中文自然语言输入"""
    result = {
        "market": "US",  # 默认市场
        "category": "",
        "keywords": [],
    }

    text = text.strip()

    # 提取市场
    market_patterns = [
        r'([A-Z]{2})\s*市场',
        r'([\u4e00-\u9fa5]+)\s*市场',
        r'市场[:：]\s*([A-Z]{2}|[\u4e00-\u9fa5]+)',
        r'([A-Z]{2})\s*站',
    ]

    for pattern in market_patterns:
        match = re.search(pattern, text)
        if match:
            market_text = match.group(1)
            market = normalize_market(market_text)
            if market:
                result["market"] = market
                break

    # 提取类目
    category_patterns = [
        r'([\u4e00-\u9fa5]+\s*[\u4e00-\u9fa5]*)\s*类目',
        r'类目[:：]\s*([\u4e00-\u9fa5]+\s*[\u4e00-\u9fa5]*)',
        r'([a-z]+\s*[a-z]+)\s*类目',
        r'类目[:：]\s*([a-z]+\s*[a-z]+)',
    ]

    for pattern in category_patterns:
        match = re.search(pattern, text)
        if match:
            result["category"] = match.group(1).strip()
            break

    # 如果没有明确提取类目，尝试其他模式
    if not result["category"]:
        # "儿童保健品" 模式
        category_match = re.search(r'([\u4e00-\u9fa5]{2,6}保健品|[\u4e00-\u9fa5]{2,6}用品)', text)
        if category_match:
            result["category"] = category_match.group(1)
        else:
            # 英文类目
            category_match = re.search(r'([a-z]+\s*[a-z]+)', text, re.IGNORECASE)
            if category_match:
                result["category"] = category_match.group(1)

    # 提取关键词
    keyword_patterns = [
        r'关键词[:：]\s*([^\s,，]+(?:[,\s][^\s,，]+)*)',
        r'keywords?\s*:\s*(.+)',
    ]

    for pattern in keyword_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            kw_text = match.group(1)
            result["keywords"] = [k.strip() for k in re.split(r'[,，\s]+', kw_text) if k.strip()]
            break

    # 默认使用类目作为关键词
    if not result["keywords"]:
        result["keywords"] = [result["category"]] if result["category"] else []

    return result


def parse_english_input(text: str) -> Dict:
    """解析英文输入"""
    result = {
        "market": "US",
        "category": "",
        "keywords": [],
    }

    text = text.strip()

    # 分割逗号分隔的输入
    parts = [p.strip() for p in text.split(',')]

    if len(parts) >= 1:
        # 第一个可能是市场
        market = normalize_market(parts[0])
        if market:
            result["market"] = market
            parts = parts[1:]

        # 第二个是类目
        if parts:
            result["category"] = parts[0]
            result["keywords"] = [parts[0]]

        # 第三个及之后是额外关键词
        if len(parts) > 1:
            result["keywords"] = parts

    return result


def parse_structured_input(text: str) -> Dict:
    """解析结构化输入 (JSON 格式)"""
    import json

    try:
        data = json.loads(text)
        return {
            "market": data.get("market", "US"),
            "category": data.get("category", ""),
            "keywords": data.get("keywords", [data.get("category", "")]),
        }
    except json.JSONDecodeError:
        return None


def parse_input(market: str, category: str, keywords: List[str] = None) -> Dict:
    """
    解析输入参数，返回标准化的选品请求

    Args:
        market: 市场代码 (如 US, UK, DE)
        category: 产品类目
        keywords: 关键词列表 (可选)

    Returns:
        Dict: {
            "market": "US",
            "category": "kids supplements",
            "keywords": ["kids supplements", "children vitamins"]
        }
    """
    result = {
        "market": normalize_market(market) or "US",
        "category": category.strip().lower() if category else "",
        "keywords": [],
    }

    # 处理关键词
    if keywords:
        result["keywords"] = [k.strip().lower() for k in keywords]
    else:
        result["keywords"] = [result["category"]]

    # 扩展关键词
    result["keywords"] = expand_keywords(result["keywords"])

    return result


def parse_natural_language(text: str) -> Dict:
    """
    解析自然语言输入，自动检测语言并解析

    Args:
        text: 用户输入的自然语言

    Returns:
        Dict: 解析后的结构化数据
    """
    text = text.strip()

    # 尝试 JSON 格式
    if text.startswith('{'):
        result = parse_structured_input(text)
        if result:
            return result

    # 检测语言并解析
    # 包含中文字符 -> 中文输入
    if re.search(r'[\u4e00-\u9fa5]', text):
        return parse_chinese_input(text)
    else:
        return parse_english_input(text)


# 测试
if __name__ == "__main__":
    test_cases = [
        "分析美国市场儿童保健品类目的选品机会",
        "帮我调研英国市场益生菌产品的市场情况",
        "US, kids supplements, children's vitamins, gummy vitamins",
        "research probiotics market in UK",
        "{\"market\": \"US\", \"category\": \"pet supplements\"}",
    ]

    print("=" * 60)
    print("Input Parser Test")
    print("=" * 60)

    for text in test_cases:
        result = parse_natural_language(text)
        print(f"\n输入: {text}")
        print(f"解析: {result}")
