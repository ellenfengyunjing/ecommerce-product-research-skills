---
name: apify-amazon-scraper
description: |
  使用 Apify API 采集亚马逊商品数据技能。当用户需要以下任务时应使用此技能：
  - 通过 Apify 平台抓取亚马逊商品数据
  - 采集 children's health products 等品类的畅销商品
  - 获取 title/brand/category/images/launch date/BSR/月销量/price history/buy box price/review count/rating/variation count
  - 将采集数据导出为 Excel 表格
triggers:
  - apify亚马逊
  - apify采集
  - apify爬取
  - amazon apify
  - apify amazon scraper
---

# Apify Amazon Scraper

本技能使用 Apify API 调用 Amazon Product Scraper 采集亚马逊商品数据。

## 在 amazon-product-researcher 中的调用边界

`amazon-product-researcher` 进行 Amazon 调研时，必须先使用 `amazon-product-scraper` 低成本采集商品和差评数据。本技能只在以下情况作为补缺工具使用：

1. `amazon-product-scraper` 采集失败、被限流/验证码阻断，或有效样本量不足。
2. 本地采集结果缺少关键字段，例如 BSR、月销量、价格历史、变体、上架日期或完整 review metadata。
3. 用户明确要求使用 Apify 采集 Amazon 数据。

使用本技能补采时，不得重新全量抓取已经由 `amazon-product-scraper` 成功采集的同一关键词/同一类目。优先传入缺口 ASIN、缺口字段或单个搜索 URL，控制 `maxItems`，并保留 Actor Run ID 与 dataset ID 作为 lineage。

## 成本控制规则

- 每轮 Amazon 补采默认只启动 1 个 Actor Run。
- 默认使用 1 个核心关键词、1 个类目 URL 或一组缺口 ASIN，不为同义词重复启动 Actor。
- 只有首轮补采后核心字段仍缺失，才允许追加第二个 Actor Run。
- 追加采集必须记录原因、缺口字段、Actor ID、Run ID、采集时间和样本量。
- 采集失败或空结果不进入最终报告，只记录在内部采集日志。

## 采集字段（11个核心字段）

| # | 字段 | 说明 |
|---|------|------|
| 1 | **title** | 商品标题 |
| 2 | **brand** | 品牌名称 |
| 3 | **category** | 分类信息 |
| 4 | **images** | 商品图片URL |
| 5 | **launch date** | 上架日期 |
| 6 | **sales rank (BSR)** | 销量排名 |
| 7 | **estimated monthly sales** | 预估月销量 |
| 8 | **price history** | 价格历史 |
| 9 | **buy box price** | Buy Box 价格 |
| 10 | **review count** | 评论数量 |
| 11 | **review rating** | 评分星级 |
| 12 | **variation count** | 变体数量 |

## 使用前提

### 1. 获取 Apify API Token

1. 访问 [apify.com](https://apify.com) 注册/登录账号
2. 进入 [Settings → Integrations](https://console.apify.com/settings/integrations) 获取 API Token
3. 首次使用有免费配额（约 $5 额度）

### 2. 安装 Apify SDK

```bash
pip install apify-client
```

## 使用方式

### 基础命令格式

```
/apify-amazon-scraper <关键词> <数量> [输出目录]
```

### 示例

```
// 采集 children's health products 前50个商品
/apify-amazon-scraper children's health products 50

// 采集指定数量
/apify-amazon-scraper vitamins 100

// 指定输出目录
/apify-amazon-scraper baby supplements 50 ./output
```

## 实现步骤

### Step 1: 调用 Apify Amazon Scraper Actor

Apify Actor ID: `junglee/free-amazon-product-scraper` 或 `sas蛙/amazon-product-scraper`

```python
from apify_client import ApifyClient

# 初始化客户端
client = ApifyClient("YOUR-API-TOKEN")

# 准备输入
# Amazon 搜索页URL示例
search_url = "https://www.amazon.com/s?k=children%27s+health+products&s=review_rank"

run_input = {
    "searchUrls": [search_url],
    "maxItems": 50,
    "fields": [
        "title",
        "brand",
        "category",
        "images",
        "launchDate",
        "salesRank",
        "estimatedMonthlySales",
        "priceHistory",
        "buyBoxPrice",
        "reviewCount",
        "reviewRating",
        "variationCount"
    ],
    "timeoutMs": 120000,
    "memoryMbytes": 512
}

# 启动Actor
actor_call = client.actor("junglee/free-amazon-product-scraper").start(run_input=run_input)

# 等待完成
client.actor(actor_call["id"]).wait_for_finish()

# 获取数据集
dataset_items = client.dataset(actor_call["defaultDatasetId"]).list_items().items
```

### Step 2: 数据转换

Apify 返回的数据需要映射到目标字段：

```python
def transform_data(item):
    return {
        "title": item.get("title", ""),
        "brand": item.get("brand", ""),
        "category": item.get("breadCrumbs", ""),
        "images": item.get("images", [{}])[0].get("link", "") if item.get("images") else "",
        "launch_date": item.get("dateFirstAvailable", ""),
        "sales_rank_BSR": item.get("bestsellerRanks", ""),
        "estimated_monthly_sales": extract_monthly_sales(item),
        "price_history": item.get("priceHistory", ""),
        "buy_box_price": item.get("price", {}).get("value", ""),
        "review_count": item.get("reviewsCount", 0),
        "review_rating": item.get("stars", 0.0),
        "variation_count": len(item.get("variantAsins", []))
    }

def extract_monthly_sales(item):
    # 从搜索结果提取月销量
    # 格式如 "300+ bought in past month"
    sales_text = item.get("sales", "")
    if sales_text:
        import re
        match = re.search(r'(\d+,?\d*)\+?\s*bought', sales_text)
        if match:
            return int(match.group(1).replace(',', ''))
    return 0
```

### Step 3: 写入 Excel

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill

def save_to_excel(data, output_path):
    df = pd.DataFrame(data)

    # 重命名列为中文（可选）
    columns = [
        "标题", "品牌", "分类", "首图URL", "上架日期",
        "BSR排名", "预估月销量", "价格历史", "Buy Box价格",
        "评论数", "评分", "变体数量"
    ]
    df.columns = columns

    # 保存Excel
    df.to_excel(output_path, index=False, engine='openpyxl')

    # 格式化
    wb = load_workbook(output_path)
    ws = wb.active

    # 设置表头样式
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center")

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # 自动列宽
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    wb.save(output_path)
    return output_path
```

## 完整脚本示例

```python
#!/usr/bin/env python3
"""
Apify Amazon Scraper - 采集亚马逊商品数据
使用方法: python apify_amazon_scraper.py <关键词> <数量> [输出目录]
"""

import sys
import os
from datetime import datetime

try:
    from apify_client import ApifyClient
except ImportError:
    print("请先安装 apify-client: pip install apify-client")
    sys.exit(1)

try:
    import pandas as pd
    from openpyxl import load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill
except ImportError:
    print("请先安装依赖: pip install pandas openpyxl")
    sys.exit(1)


def get_apify_token():
    """从环境变量或配置文件获取API Token"""
    token = os.environ.get("APIFY_API_TOKEN")
    if token:
        return token

    config_path = os.path.expanduser("~/.workbuddy/apify_config.json")
    if os.path.exists(config_path):
        import json
        with open(config_path) as f:
            config = json.load(f)
            return config.get("api_token", "")

    return input("请输入 Apify API Token: ").strip()


def create_search_url(keyword, sort="sales"):
    """创建Amazon搜索URL"""
    import urllib.parse
    encoded = urllib.parse.quote(keyword)
    # sales = 按销量排序, review_rank = 按评论排序
    return f"https://www.amazon.com/s?k={encoded}&s={sort}"


def scrape_amazon(client, search_url, max_items=50):
    """调用Apify Actor抓取数据"""
    run_input = {
        "searchUrls": [search_url],
        "maxItems": max_items,
        "scrapeVariants": True,
        "scrapeFromCategory": True,
        "includeFields": [
            "title", "url", "asin", "brand", "price",
            "stars", "reviewsCount", "bestsellerRanks",
            "images", "description", "variantAsins",
            "features", "dateFirstAvailable"
        ]
    }

    print(f"启动Apify Actor抓取任务...")
    actor_call = client.actor("junglee/free-amazon-product-scraper").start(run_input=run_input)

    print(f"Actor运行ID: {actor_call['id']}, 等待完成...")
    client.actor(actor_call["id"]).wait_for_finish()

    print(f"获取数据集...")
    dataset_items = client.dataset(actor_call["defaultDatasetId"]).list_items().items

    return dataset_items


def transform_item(item):
    """转换数据字段"""
    # 提取主图
    main_image = ""
    if item.get("images"):
        if isinstance(item["images"], list):
            main_image = item["images"][0].get("link", "") if isinstance(item["images"][0], dict) else str(item["images"][0])
        elif isinstance(item["images"], dict):
            main_image = item["images"].get("link", "")

    # 提取Buy Box价格
    buy_box_price = ""
    price_data = item.get("price", {})
    if isinstance(price_data, dict):
        buy_box_price = f"{price_data.get('currency', '$')}{price_data.get('value', '')}"
    elif price_data:
        buy_box_price = str(price_data)

    # 提取BSR排名
    bsr_list = item.get("bestsellerRanks", [])
    bsr_text = ""
    if isinstance(bsr_list, list):
        bsr_text = " | ".join([f"#{r.get('rank', '')} in {r.get('category', '')}" for r in bsr_list[:3]])
    elif bsr_list:
        bsr_text = str(bsr_list)

    # 提取分类
    category = ""
    bread_crumbs = item.get("breadCrumbs", "")
    if bread_crumbs:
        category = " > ".join(bread_crumbs) if isinstance(bread_crumbs, list) else bread_crumbs

    # 提取变体数量
    variant_count = 0
    variants = item.get("variantAsins", [])
    if isinstance(variants, list):
        variant_count = len(variants)

    # 提取上架日期
    launch_date = item.get("dateFirstAvailable", "")
    if isinstance(launch_date, dict):
        launch_date = launch_date.get("value", "")

    return {
        "标题": item.get("title", ""),
        "品牌": item.get("brand", ""),
        "分类": category,
        "首图URL": main_image,
        "上架日期": launch_date,
        "BSR排名": bsr_text,
        "预估月销量": "",  # 需要从搜索页提取
        "价格历史": "",     # 需要单独接口
        "Buy Box价格": buy_box_price,
        "评论数": item.get("reviewsCount", 0),
        "评分": item.get("stars", 0.0),
        "变体数量": variant_count
    }


def save_to_excel(data, output_path):
    """保存数据到Excel并格式化"""
    df = pd.DataFrame(data)

    # 保存
    df.to_excel(output_path, index=False, engine='openpyxl')

    # 格式化
    wb = load_workbook(output_path)
    ws = wb.active

    # 表头样式
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # 自动列宽
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = min(max_length + 2, 60)

    # 冻结首行
    ws.freeze_panes = "A2"

    wb.save(output_path)
    return output_path


def main():
    # 解析参数
    if len(sys.argv) < 3:
        print("用法: python apify_amazon_scraper.py <关键词> <数量> [输出目录]")
        print("示例: python apify_amazon_scraper.py children's health products 50")
        sys.exit(1)

    keyword = sys.argv[1]
    max_items = int(sys.argv[2])
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None

    # 设置输出目录
    if not output_dir:
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_keyword = keyword.replace(" ", "_").replace("'", "")[:20]
    excel_file = os.path.join(output_dir, f"amazon_{safe_keyword}_{timestamp}.xlsx")

    # 获取Token
    api_token = get_apify_token()
    if not api_token:
        print("错误: 请设置APIFY_API_TOKEN环境变量或创建配置文件")
        sys.exit(1)

    # 初始化客户端
    client = ApifyClient(api_token)

    # 创建搜索URL
    search_url = create_search_url(keyword)

    print(f"\n关键词: {keyword}")
    print(f"最大数量: {max_items}")
    print(f"搜索URL: {search_url}\n")

    # 抓取数据
    raw_data = scrape_amazon(client, search_url, max_items)

    print(f"获取到 {len(raw_data)} 条原始数据")

    # 转换数据
    transformed_data = [transform_item(item) for item in raw_data[:max_items]]

    # 保存Excel
    excel_path = save_to_excel(transformed_data, excel_file)

    print(f"\n✅ 数据已保存到: {excel_path}")
    print(f"共 {len(transformed_data)} 条商品记录")


if __name__ == "__main__":
    main()
```

## 配置说明

### 环境变量方式 (推荐)

1. 复制 `.env.example` 为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入你的 API Token:
   ```bash
   APIFY_API_TOKEN=your-apify-api-token-here
   ```

3. 程序会自动从 `.env` 文件加载配置

### 配置文件方式

创建 `~/.workbuddy/apify_config.json`:

```json
{
    "api_token": "your-apify-api-token-here"
}
```

### 环境变量方式

```bash
export APIFY_API_TOKEN="your-token-here"
```

> 💡 **提示**: `.env` 文件不会提交到 Git，推荐使用这种方式管理 API Key。

## 注意事项

1. **免费配额**: Apify 新用户有约 $5 免费额度，可抓取约 500-800 条数据
2. **抓取限制**: Amazon 搜索结果通常最多返回 7 页（约 70 条），可使用分类 URL 获取更多
3. **字段说明**: `price history` 和 `estimated monthly sales` 需要单独配置或从搜索页提取
4. **Rate Limit**: 遇到限流时可使用 `proxyConfiguration` 配置代理

## 文件结构

```
apify-amazon-scraper/
├── SKILL.md                      # 本文件
├── .env.example                  # 环境变量模板
├── apify_amazon_scraper.py       # 主脚本
└── scripts/
    └── requirements.txt           # 依赖列表
```
