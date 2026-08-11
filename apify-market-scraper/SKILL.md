---
name: apify-market-scraper
description: |
  使用 Apify API 采集市场调研数据技能。当用户需要以下任务时应使用此技能：
  - 采集市场规模和CAGR数据
  - 获取行业趋势和消费者洞察
  - 抓取 Grand View Research / Mordor Intelligence 等市场报告
  - 使用同一个 Apify API Token 采集多种数据
triggers:
  - apify market
  - apify 市场数据
  - 采集市场报告
  - market research apify
  - Apify市场抓取
agent_created: true
---

# Apify Market Scraper v1.0

## 功能说明

本技能使用 **同一个 Apify API Token** 采集市场调研数据，与 `apify-amazon-scraper` 和 `apify-tiktok-scraper` **共享 API 配置**。

## 调研链路成本规则

当本技能被 `amazon-product-researcher` 调用时，默认遵守以下规则：

1. 每轮市场报告采集优先启动 1 个 Apify Actor Run，使用 1 个最相关报告 URL、搜索结果页或行业报告入口页。
2. 不为同一类目同时开启多个 Web Scraper/Google Search Actor。需要多个报告来源时，优先在同一个 Actor Run 中放入有限的 URL 列表。
3. 首轮采集后若没有市场规模、CAGR、年份、地区范围或报告来源 URL 等核心字段，才追加第二个 Actor Run 或使用 Web Search/Web Fetch 兜底。
4. Web Search 仅作为 Apify 不可用、权限/配额不足、目标站不可抓或字段缺失时的兜底来源。
5. 输出给报告的数据必须包含来源 URL、报告名称、发布年份或页面访问时间、采集方式、Actor/脚本名、Run ID 和样本量。
6. 报错、付费墙不可见内容、空页面和无法验证数字不进入最终报告。

---

## 前提条件

### 配置 API Token

**只需配置一次**，所有 Apify 相关 Skills 共享配置！

保存到 `~/.workbuddy/apify_config.json`：

```json
{
  "api_token": "your-apify-api-token-here",
  "default_region": "US"
}
```

获取方式：访问 [apify.com](https://apify.com) → Settings → Integrations

---

## Apify Actor 推荐

### 市场数据抓取

| Actor | 费用 | 功能 | 推荐度 |
|--------|------|------|--------|
| **`apify/web-scraper`** | 消耗平台额度 | 通用网页抓取 | ⭐⭐⭐⭐⭐ |
| **`dtrungten/web-scraper`** | 消耗平台额度 | 增强版网页抓取 | ⭐⭐⭐⭐ |

### 适用网站

| 网站 | URL | 数据类型 |
|------|-----|----------|
| Grand View Research | grandviewresearch.com | 市场规模/CAGR/细分 |
| Mordor Intelligence | mordorintelligence.com | CAGR/驱动因素 |
| Statista | statista.com | 统计数据/图表 |
| SPINS | spins.com | 天然有机市场 |

---

## 使用方式

### 方式一：使用 `apify/web-scraper`（推荐）

```python
from apify_client import ApifyClient
import json
import time

# 初始化客户端（使用同一个 Token）
client = ApifyClient("your-apify-api-token")

def scrape_market_report(url, page_function=None):
    """
    使用 apify/web-scraper 抓取市场报告

    Args:
        url: 目标网页 URL
        page_function: 自定义页面处理函数（可选）
    """

    # 默认页面处理函数（提取正文文本）
    if page_function is None:
        page_function = """
        async function pageFunction({ request, page, enqueueLinks, saveSnapshot }) {
            // 等待页面加载
            await page.waitForTimeout(2000);

            // 提取正文文本
            const data = await page.evaluate(() => {
                // 移除脚本和样式
                const clone = document.cloneNode(true);
                clone.querySelectorAll('script, style, nav, footer').forEach(el => el.remove());

                // 提取主要内容
                const content = clone.querySelector('main, article, .content, .report-content');
                return content ? content.innerText : clone.innerText;
            });

            // 保存数据
            await saveSnapshot({
                url: request.url,
                text: data
            });
        }
        """

    # 准备输入
    run_input = {
        "startUrls": [{ "url": url }],
        "pageFunction": page_function,
        "maxRequestsPerCrawl": 1,
        "maxCrawlingDepth": 1,
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        }
    }

    print(f"📈 开始抓取: {url}")

    # 启动 Actor
    actor_call = client.actor("apify/web-scraper").start(run_input=run_input)
    print(f"Actor 运行 ID: {actor_call['id']}")

    # 等待完成（最多 120 秒）
    try:
        client.actor(actor_call["id"]).wait_for_finish(timeout_secs=120)
    except Exception as e:
        print(f"⚠️  等待超时: {e}")

    # 获取数据集
    dataset_items = client.dataset(actor_call["defaultDatasetId"]).list_items().items

    return dataset_items

# 使用示例：抓取 Grand View Research 报告
report_url = "https://www.grandviewresearch.com/industry-analysis/kids-supplements-market"

data = scrape_market_report(report_url)

if data:
    print("\n✅ 抓取成功!")
    print(f"数据长度: {len(data[0].get('text', ''))} 字符")

    # 提取关键信息
    text = data[0]['text']

    # 保存原始数据
    with open('market_report_raw.txt', 'w', encoding='utf-8') as f:
        f.write(text)

    print("📁 原始数据已保存: market_report_raw.txt")
```

### 方式二：批量抓取多个报告

```python
def scrape_multiple_reports(urls):
    """批量抓取多个市场报告"""

    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 抓取: {url}")

        try:
            data = scrape_market_report(url)

            if data:
                results.append({
                    "url": url,
                    "data": data[0].get("text", "") if data else ""
                })

            # 避免请求过快
            if i < len(urls):
                time.sleep(5)

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            results.append({
                "url": url,
                "data": "",
                "error": str(e)
            })

    return results

# 使用示例
urls = [
    "https://www.grandviewresearch.com/industry-analysis/kids-supplements-market",
    "https://www.mordorintelligence.com/industry-reports/children-supplements-market",
    "https://www.statista.com/topics/...."
]

all_data = scrape_multiple_reports(urls)

# 保存汇总
with open('market_reports.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print("\n✅ 所有报告已保存: market_reports.json")
```

---

## 完整脚本示例

```python
#!/usr/bin/env python3
"""
Apify Market Scraper - 采集市场调研数据
使用方法: python apify_market_scraper.py <URL1> <URL2> ...
"""

import sys
import os
import json
import time
from pathlib import Path

try:
    from apify_client import ApifyClient
except ImportError:
    print("请先安装 apify-client: pip install apify-client")
    sys.exit(1)


def get_apify_token():
    """从配置文件获取 API Token（共享配置）"""
    config_path = Path.home() / ".workbuddy" / "apify_config.json"

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("api_token", "")

    # 如果配置文件不存在，提示用户输入
    print("⚠️  未找到 Apify 配置文件")
    token = input("请输入 Apify API Token: ").strip()

    # 保存配置
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump({"api_token": token, "default_region": "US"}, f, indent=2)

    return token


def scrape_with_web_scraper(client, url):
    """使用 apify/web-scraper 抓取网页"""

    # 页面处理函数（提取正文）
    page_function = """
    async function pageFunction({ request, page, enqueueLinks, saveSnapshot }) {
        await page.waitForTimeout(3000);

        const data = await page.evaluate(() => {
            const clone = document.cloneNode(true);
            clone.querySelectorAll('script, style, nav, footer, .ad, .cookie-banner').forEach(el => el.remove());

            // 尝试提取主要内容区域
            const selectors = [
                'main', 'article', '.content', '.report-content',
                '.market-report', '#main-content', '.post-content'
            ];

            let content = null;
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText.length > 200) {
                    content = el;
                    break;
                }
            }

            return content ? content.innerText : clone.innerText;
        });

        await saveSnapshot({
            url: request.url,
            text: data,
            timestamp: new Date().toISOString()
        });
    }
    """

    run_input = {
        "startUrls": [{ "url": url }],
        "pageFunction": page_function,
        "maxRequestsPerCrawl": 1,
        "maxCrawlingDepth": 1,
        "proxyConfiguration": {
            "useApifyProxy": True
        }
    }

    print(f"  ▶ 启动 Actor: apify/web-scraper")

    # 启动 Actor
    actor_call = client.actor("apify/web-scraper").start(run_input=run_input)
    print(f"  ▶ Actor ID: {actor_call['id']}")

    # 等待完成
    print(f"  ▶ 等待完成...")
    client.actor(actor_call["id"]).wait_for_finish(timeout_secs=120)

    # 获取数据集
    dataset_items = client.dataset(actor_call["defaultDatasetId"]).list_items().items

    return dataset_items


def extract_market_data(text):
    """从文本中提取市场数据（简单规则）"""

    import re

    result = {
        "market_size": "",
        "cagr": "",
        "forecast": "",
        "segments": []
    }

    # 提取市场规模（如：$35.9 billion）
    size_patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(billion|million|trillion)',
        r'(\d+(?:\.\d+)?)\s*(USD|EUR)\s*(billion|million)',
    ]
    for pattern in size_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["market_size"] = f"${match.group(1)} {match.group(2)}"
            break

    # 提取 CAGR（如：CAGR of 7.6%）
    cagr_pattern = r'CAGR\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%'
    match = re.search(cagr_pattern, text, re.IGNORECASE)
    if match:
        result["cagr"] = f"{match.group(1)}%"

    # 提取预测年份（如：by 2033）
    forecast_pattern = r'by\s*(\d{4})'
    match = re.search(forecast_pattern, text, re.IGNORECASE)
    if match:
        result["forecast"] = match.group(1)

    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python apify_market_scraper.py <URL1> [URL2] ...")
        print("示例: python apify_market_scraper.py https://www.grandviewresearch.com/...")
        sys.exit(1)

    urls = sys.argv[1:]

    print("=" * 60)
    print("📈 Apify Market Scraper")
    print("=" * 60)
    print(f"URL 数量: {len(urls)}")
    print("=" * 60)

    # 获取 Token
    api_token = get_apify_token()
    if not api_token:
        print("❌ 错误: 无法获取 API Token")
        sys.exit(1)

    # 初始化客户端
    client = ApifyClient(api_token)

    # 抓取所有 URL
    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 抓取: {url}")

        try:
            data = scrape_with_web_scraper(client, url)

            if data:
                raw_text = data[0].get("text", "")
                print(f"  ✅ 抓取成功! 数据长度: {len(raw_text)} 字符")

                # 提取结构化数据
                extracted = extract_market_data(raw_text)
                print(f"  📊 提取数据: {extracted}")

                results.append({
                    "url": url,
                    "raw_text": raw_text[:5000],  # 只保存前 5000 字符
                    "extracted": extracted
                })
            else:
                print(f"  ⚠️  未获取到数据")

        except Exception as e:
            print(f"  ❌ 抓取失败: {e}")
            results.append({
                "url": url,
                "error": str(e)
            })

        # 避免请求过快
        if i < len(urls):
            print(f"  ⏳ 等待 5 秒...")
            time.sleep(5)

    # 保存结果
    output_file = "market_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"✅ 所有数据已保存: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

---

## 配置说明

### 方式一：.env 文件 (推荐)

1. 复制 `.env.example` 为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件:
   ```bash
   APIFY_API_TOKEN=your-apify-api-token-here
   ```

### 方式二：共享配置文件

所有 Apify Skills 共享配置：

| Skill | 配置文件 |
|-------|----------|
| `apify-amazon-scraper` | ✅ `~/.workbuddy/apify_config.json` |
| `apify-tiktok-scraper` | ✅ 同上 |
| `apify-market-scraper` | ✅ 同上 |

> 💡 **提示**: `.env` 文件不会提交到 Git，推荐使用这种方式管理 API Key。

### Actor 使用额度估算

| 采集任务 | 预估消耗 | 备注 |
|----------|----------|------|
| 1个市场报告 | ~$0.3 | 约 1000 次请求 |
| 5个报告批量 | ~$1.2 | 批量更划算 |
| 深度抓取（含子页） | ~$0.8/报告 | 包含细分数据 |

**免费额度 $5 可采集约 6-8 个市场报告**

---

## 注意事项

1. **免费额度**：$5 免费额度约可采集 6-8 个市场报告
2. **Actor 选择**：`apify/web-scraper` 是官方通用抓取工具，稳定性好
3. **代理配置**：建议启用 Apify Proxy 避免 IP 限流
4. **数据提取**：需要根据不同网站定制 `pageFunction`
5. **Token 共享**：与 `apify-amazon-scraper` 和 `apify-tiktok-scraper` 使用同一个配置文件

---

## 文件结构

```
apify-market-scraper/
├── SKILL.md                      # 本文件
├── .env.example                  # 环境变量模板
├── apify_market_scraper.py       # 主脚本
└── scripts/
    └── requirements.txt           # 依赖列表
```

---

## 下一步

配置完成后，在 WorkBuddy 中使用：

```
帮我用 Apify 采集以下市场报告：
https://www.grandviewresearch.com/industry-analysis/kids-supplements-market
```

系统会自动调用本 Skill 完成采集，并与 `apify-amazon-scraper` 和 `apify-tiktok-scraper` **共享同一个 API Token**！
