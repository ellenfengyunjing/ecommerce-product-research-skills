# Amazon Product Scraper v6.2

亚马逊商品数据采集 Skill —— 支持 13 个核心字段采集，Tier0 精准价格定位，BSR 全量抓取。

---

## 采集字段（13 个核心字段）

| # | 字段 | 说明 | 示例 |
|---|------|------|------|
| 1 | **标题** | 商品标题 | "Children's Multivitamin Gummies..." |
| 2 | **ASIN** | 亚马逊商品 ID | B08N5WRWNW |
| 3 | **价格** | 当前售价 (USD) | $19.99 |
| 4 | **评分** | 平均评分 | 4.5 ⭐ |
| 5 | **评论数** | 总评论数 | 1234 |
| 6 | **月销量** | 预估月销量 | 300+ |
| 7 | **BSR 排名** | 销量排名 (各品类) | #1,254 in Health & Household |
| 8 | **五点描述** | 五点特性 | ["Supports immunity", ...] |
| 9 | **规格参数** | 详细信息 (W/D/M 可选) | Weight: 0.64 oz |
| 10 | **品牌名称** | 品牌 | "Nordic Naturals" |
| 11 | **首图** | 首图 URL | https://m.media-amazon.com/... |
| 12 | **变体数** | 变体数量 | 3 (草莓味/橙子味/混合味) |
| 13 | **商品链接** | 亚马逊商品页链接 | https://www.amazon.com/dp/B08N5WRWNW |

---

## 使用方法

### 方式一：自然语言

```
"帮我采集 Amazon 儿童维生素 Best Sellers 前 100 个商品"
"采集美国市场的 益生菌软糖 数据"
"抓取 BSR Top 500 的 儿童保健品"
```

### 方式二：命令行

```bash
cd skills/amazon-product-scraper/scripts
python amazon_scraper.py "kids vitamins" 100
```

---

## 核心特性

### 1. Tier0 精准价格定位

使用 `amazon-price` 工具获取精准价格，避免前端展示价格误导：

```
商品价格:     $18.98 (展示价)
实际价格:     $15.99 (Tier0 精准价)
月销量:       300+ 件
BSR 排名:     #1,254
```

### 2. BSR 全量抓取

| 方法 | 抓取页数 | 商品数量 | 推荐度 |
|------|----------|----------|--------|
| 搜索结果 | 7 页 (约 70 条) | 有限 | ⭐⭐ |
| BSR 分类页 | **全量** | 1000+ | ⭐⭐⭐⭐⭐ |

### 3. 防限流机制

- 随机 User-Agent
- 自动请求延迟
- 错误重试
- 代理支持

---

## 数据输出

### Excel 文件格式

文件名: `amazon_kids_vitamins_20260512_143025.xlsx`

| 标题 | ASIN | 价格 | 评分 | 评论数 | 月销量 | BSR排名 | ... |
|------|------|------|------|--------|--------|----------|-----|
| Children's... | B08N5... | $18.98 | 4.5 | 1234 | 300+ | #1254 | ... |

### 图片下载

同时下载商品首图到 `商品图片/` 文件夹：

```
商品图片/
├── B08N5WRWNW.jpg
├── B08G4HXL1S.jpg
└── ...
```

---

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MAX_PRODUCTS` | 100 | 最大采集数量 |
| `PRICE_RANGE` | (10, 50) | 价格区间 (USD) |
| `MIN_RATING` | 4.0 | 最低评分 |
| `MIN_REVIEW_COUNT` | 50 | 最小评论数 |
| `PROXY_ENABLED` | false | 是否启用代理 |
| `SAVE_IMAGES` | false | 是否下载商品图片 |

---

## 示例脚本

详见 `scripts/amazon_scraper.py`，核心功能：

```python
def scrape_bsr_category(max_items=100):
    """抓取 BSR 分类页商品（推荐）"""

def scrape_search_results(keyword, max_items=100):
    """抓取搜索结果商品（备用）"""

def download_product_image(asin, image_url, save_dir):
    """下载商品首图"""
```

---

## 注意事项

1. **采集速度**: 约 5-10 秒/商品
2. **限流风险**: 高频采集可能被限流，建议启用代理
3. **数据时效**: BSR 和价格实时变化，建议每周更新
4. **合规性**: 仅用于市场调研，请勿用于商业爬虫

---

## 下一步

- [返回主 README](../README.md)
- [配置指南](../docs/configuration.md)
- [常见问题](../docs/faq.md)
