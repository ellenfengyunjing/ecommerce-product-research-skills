# 配置指南

本文档详细介绍如何配置 Amazon Product Research Toolkit。

---

## 环境变量配置

### 1. 获取 Apify API Token

1. 访问 [Apify Console](https://console.apify.com/account/integrations)
2. 登录你的 Apify 账户
3. 复制你的 API Token

### 2. 配置 .env 文件

```bash
# 进入项目目录
cd amazon-product-researcher

# 复制模板
cp .env.example .env

# 编辑配置
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

### 3. 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `APIFY_API_TOKEN` | ✅ | - | Apify API Token |
| `APIFY_1688_ACTOR_ID` | ❌ | - | 1688/Alibaba 供应商采集 Actor ID；需要准确供应商成本时推荐配置 |
| `SUPPLIER_COST_SOURCE` | ❌ | 1688 | 供应商成本数据源 |
| `SUPPLIER_KEYWORDS_MAX` | ❌ | 8 | 每个品类最多生成的 1688 中文搜索关键词数量 |
| `SUPPLIER_RESULTS_PER_KEYWORD` | ❌ | 20 | 每个 1688 关键词采集的商品/供应商数量 |
| `RMB_USD_RATE` | ❌ | auto | 人民币到美元汇率；`auto` 表示由运行时自动获取或使用默认汇率 |
| `DEFAULT_MARKET` | ❌ | US | 默认市场 |
| `OUTPUT_FORMAT` | ❌ | markdown | 报告格式 |
| `OUTPUT_DIR` | ❌ | ./output | 输出目录 |
| `MAX_PRODUCTS` | ❌ | 100 | 最大采集数量 |
| `MIN_REVIEW_COUNT` | ❌ | 50 | 最小评论数 |
| `MIN_PRICE` | ❌ | 10 | 最低价格 (USD) |
| `MAX_PRICE` | ❌ | 50 | 最高价格 (USD) |
| `MIN_RATING` | ❌ | 4.0 | 最低评分 |
| `PROXY_ENABLED` | ❌ | false | 是否启用代理 |
| `DEBUG` | ❌ | false | DEBUG 模式 |
| `LOG_LEVEL` | ❌ | INFO | 日志级别 |

---

## 高级配置

### 采集参数配置

编辑 `skills/amazon-product-researcher/scripts/config.py`:

```python
# 采集配置
CONFIG = {
    # 基础参数
    "max_products": 100,              # 最大采集商品数
    "min_review_count": 50,           # 最小评论数
    "min_rating": 4.0,                # 最低评分

    # 价格区间 (USD)
    "price_range": (10, 50),

    # 采集深度
    "max_pages": 5,                   # 最大采集页数
    "include_sponsored": False,       # 是否包含 sponsored 商品

    # 请求参数
    "request_delay": 2,               # 请求间隔 (秒)
    "retry_times": 3,                # 重试次数
    "timeout": 30,                   # 超时时间 (秒)

    # 代理配置
    "proxy_enabled": False,
    "proxy_url": "",                  # 格式: http://user:pass@host:port

    # 浏览器配置
    "headless": True,                 # 无头模式
    "user_agent": "",                 # 自定义 User-Agent

    # 数据存储
    "save_raw_data": True,            # 保存原始数据
    "save_processed": True,          # 保存处理后数据
    "save_reports": True,             # 保存报告

    # 输出格式
    "output_format": "markdown",      # markdown, pdf, word, html
}
```

### 市场特定配置

```python
# 特定市场的配置
MARKET_CONFIG = {
    "US": {
        "domain": "amazon.com",
        "currency": "USD",
        "default_category": "All",
        "search_index": "aps",
    },
    "UK": {
        "domain": "amazon.co.uk",
        "currency": "GBP",
        "default_category": "All",
        "search_index": "aps",
    },
    "DE": {
        "domain": "amazon.de",
        "currency": "EUR",
        "default_category": "Alle",
        "search_index": "aps",
    },
}
```

---

## API 配置

### Apify Actors

本工具使用以下 Apify Actors:

| Actor | 用途 | 链接 |
|-------|------|------|
| `junglee/free-amazon-product-scraper` | 亚马逊商品数据 | [查看](https://apify.com/junglee/free-amazon-product-scraper) |
| 自定义 1688/Alibaba 采集 Actor | 1688 商品报价、MOQ、供应商资质、成交/复购信号 | 在 `.env` 中配置 `APIFY_1688_ACTOR_ID` |
| `clockworks/tiktok-scraper` | TikTok 数据 | [查看](https://apify.com/clockworks/tiktok-scraper) |
| `apify/web-scraper` | 通用网页采集 | [查看](https://apify.com/apify/web-scraper) |

### 1688 供应商成本采集

生成选品调研报告、利润模型或供应链评估时，默认会尝试采集对应品类在 1688 的供应商成本价格。流程如下：

1. 根据 Amazon 类目、竞品标题、五点描述和核心卖点生成 3-8 个中文 1688 搜索关键词。
2. 使用 `APIFY_1688_ACTOR_ID` 指定的 Actor 抓取 1688 商品和供应商数据。
3. 标准化商品标题、价格区间、MOQ、成交量、供应商年限、评分、复购率、地区、链接和主图。
4. 剔除明显异常值、非同类产品和低可信供应商。
5. 输出低/中/高供应商成本，并将中位成本接入利润模型。

如果没有配置 `APIFY_1688_ACTOR_ID`，报告必须说明未能自动采集供应商成本，不能虚构 1688 报价。

### 免费 vs 付费

| Actor | 免费配额 | 付费价格 |
|-------|----------|----------|
| free-amazon-product-scraper | 30分钟/月 | $49/月起 |
| tiktok-scraper | 100次/月 | $49/月起 |
| web-scraper | 30天 | 按使用量计费 |

---

## 代理配置

### 为什么要用代理

- 避免 IP 被封
- 多地区数据采集
- 提高采集稳定性

### 配置格式

```bash
# HTTP 代理
PROXY_URL=http://user:pass@host:port

# SOCKS5 代理
PROXY_URL=socks5://user:pass@host:port
```

### 推荐代理服务商

- [Bright Data](https://brightdata.com/) - 住宅代理
- [Oxylabs](https://oxylabs.io/) - 数据中心代理
- [Smartproxy](https://smartproxy.com/) - 性价比之选

---

## 故障排除

### Q: 提示 "API Token 无效"

**解决方案**:
1. 检查 `.env` 文件中的 `APIFY_API_TOKEN` 是否正确
2. 确保 Token 没有过期
3. 检查 Token 是否有足够的配额

### Q: 采集速度很慢

**解决方案**:
1. 启用代理
2. 降低 `request_delay`
3. 增加并发数 (需谨慎)

### Q: 数据采集不完整

**解决方案**:
1. 检查网络连接
2. 降低 `max_products` 数量
3. 增加 `retry_times`

---

## 环境变量优先级

配置按以下优先级生效（从高到低）：

1. **命令行参数** (最高)
2. **.env 文件**
3. **config.py 默认值** (最低)

```bash
# 命令行参数优先级最高
python main.py --market US --category "kids vitamins" --max-products 200
```

---

## 下一步

- 📖 [选品方法论详解](methodology.md)
- ❓ [常见问题](faq.md)
- 📝 [更新日志](changelog.md)
