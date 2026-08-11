---
name: market-intelligence
description: |
  市场调研数据采集技能。当用户需要以下任务时应使用此技能：
  - 采集市场规模和CAGR数据
  - 获取行业趋势和消费者洞察
  - 进行品类增速分析和市场容量评估
  - 采集市场研究报告中的关键数据
triggers:
  - 市场规模
  - CAGR
  - 品类增速
  - 市场调研
  - 行业报告
  - 消费者洞察
  - market research
  - market size
agent_created: true
---

# Market Intelligence v1.0

## 功能说明

本技能用于采集市场调研数据，包括市场规模、CAGR、消费者趋势等宏观数据，为选品调研报告提供市场数据支撑。

## 数据来源

| 来源 | 费用 | 数据类型 | 推荐度 |
|------|------|----------|--------|
| **Grand View Research** | 免费摘要/付费报告 | 市场规模/细分/预测 | ⭐⭐⭐⭐⭐ |
| **Mordor Intelligence** | 免费摘要/付费报告 | CAGR/驱动因素 | ⭐⭐⭐⭐⭐ |
| **Statista** | 部分免费 | 统计数据/图表 | ⭐⭐⭐⭐ |
| **Grand View Research** | 免费 | 市场规模 | ⭐⭐⭐⭐ |
| **SPINS** | 付费 | 天然有机市场 | ⭐⭐⭐⭐ |
| **NeoData金融数据** | 免费 | 财经数据 | ⭐⭐⭐⭐ |

## 数据输出

### 市场规模数据
```json
{
  "市场名称": "美区儿童保健品",
  "2025年规模": "124亿美元",
  "2030年预测": "180亿美元",
  "CAGR": "7.9%",
  "线上占比": "37%",
  "线下占比": "62%"
}
```

### 成分细分数据
```json
{
  "成分": "姜黄素（儿童）",
  "市场规模": "3.2亿美元",
  "年增速": "48.9%",
  "竞争度": "中低",
  "壁垒": "中"
}
```

### 消费者趋势
```json
{
  "趋势1": "软糖剂型CAGR 12.01%",
  "趋势2": "天然草本占比28%+",
  "趋势3": "免疫功能35%/护眼25%/肠胃18%/成长12%"
}
```

## 使用方式

### 方式一：WebSearch + WebFetch（免费）

```python
import requests
from bs4 import BeautifulSoup

# Grand View Research 数据采集
def get_market_size_gvr(keyword):
    """从Grand View Research采集市场规模数据"""
    search_url = f"https://www.grandviewresearch.com/search?q={keyword}"

    # 使用 WebSearch 获取相关报告
    # 使用 WebFetch 获取报告摘要

    return {
        "market_size": "extract from page",
        "cagr": "extract from page",
        "forecast": "extract from page"
    }

# Mordor Intelligence 数据采集
def get_market_size_mordor(keyword):
    """从Mordor Intelligence采集数据"""
    search_url = f"https://www.mordorintelligence.com/search?q={keyword}"

    # 同上

    return data
```

### 方式二：NeoData金融数据（免费/内置）

```python
# 使用内置的 finance-data 技能
# 搜索市场数据

# 示例：搜索儿童营养品市场规模
query = "儿童营养品市场规模 美区 2025"

# NeoData 返回结构化数据
```

### 方式三：Web Scraper 技能

使用 Web Scraper 技能批量采集：

```python
# 需要采集的URL列表
urls = [
    "https://www.grandviewresearch.com/industry-analysis/...",
    "https://www.mordorintelligence.com/prod-snapshots/...",
    "https://www.statista.com/topics/..."
]

def scrape_market_reports(urls):
    """批量采集市场报告数据"""
    results = []

    for url in urls:
        # 使用 Browser 或 WebFetch
        html = fetch_page(url)
        data = extract_market_data(html)
        results.append(data)

    return results
```

## 核心市场数据清单

### 儿童保健品类目

| 数据项 | 数据值 | 来源 |
|--------|--------|------|
| **2025全球市场规模** | 35.9亿美元 | Grand View Research |
| **2033预测规模** | 63.5亿美元 | Grand View Research |
| **全球CAGR** | 7.6% | Mordor Intelligence |
| **美区2025规模** | 124亿美元 | 行业报告 |
| **美区增速** | 7.9% | 行业报告 |
| **TikTok增速** | 32%+ | TikTok官方 |

### 成分市场规模（美区儿童）

| 成分 | 市场规模 | 年增速 | 竞争度 |
|------|----------|--------|--------|
| 复合维生素 | 43.4亿美元 | 9.1% | 高（红海） |
| 姜黄素（儿童） | 3.2亿美元 | 48.9% | 中低（蓝海） |
| 虾青素（儿童） | 1.8亿美元 | 32% | 低（蓝海） |
| 儿童蛋白 | 8.7亿美元 | 14.4% | 中 |

### 消费者趋势

| 趋势 | 数据 | 说明 |
|------|------|------|
| 剂型趋势 | 软糖CAGR 12.01% | 行业3倍增速 |
| 功能趋势 | 免疫35%/护眼25%/肠胃18%/成长12% | 功能分布 |
| 原料趋势 | 天然草本28%+ | 清洁标签 |
| 渠道趋势 | TikTok增速32%+/线下58.2% | 全域布局 |

## 市场数据采集模板

```json
{
  "采集时间": "2026-05-11",
  "目标市场": "美国/美区",
  "类目": "儿童保健品",
  "市场规模": {
    "2025年": "XX亿美元",
    "预测年份": "XX年",
    "预测规模": "XX亿美元",
    "CAGR": "XX%"
  },
  "细分数据": {
    "成分A": {...},
    "成分B": {...}
  },
  "消费者趋势": {...},
  "渠道分布": {...},
  "数据来源": [...]
}
```

## 数据清洗规则

1. **单位统一**：统一为"亿美元"或"亿元人民币"
2. **CAGR计算**：确认时间周期（5年/7年/10年）
3. **数据校验**：多源交叉验证
4. **时效标注**：标注数据采集时间

## 注意事项

1. 市场数据存在6-12个月滞后
2. 付费报告数据更准确但需要购买
3. 估算数据需标注"估算"字样
4. 建议多个数据源交叉验证
