# Amazon Product Scraper v6.3

## 功能说明

本技能用于采集 Amazon.com 上任意关键词的 Best Seller Top 100 商品**全量数据（13个字段）**，
可选采集**客户差评内容**（每商品约 20 条 1-2 星差评）。

在 `amazon-product-researcher` 的调研链路中，本技能是 Amazon 商品和差评数据的**首选低成本采集方式**。只有当本技能采集失败、遇到限流/验证码、样本量不足，或需要本技能未覆盖字段时，才降级使用 `apify-amazon-scraper` 补采，避免重复消耗 Apify API 额度。

## 调研链路采集规则

1. **单关键词/单类目优先**：每轮 Amazon 调研默认只用 1 个核心关键词或 1 个 Amazon 类目 URL 采集 Top 商品，不把近义词拆成多次重复采集。
2. **一次采集尽量拿全字段**：商品字段和差评字段能在同一轮完成时，不另开任务重复访问同一批 ASIN。
3. **缺口才补采**：如果价格、BSR、评分、评论数、五点描述、图片或差评等核心字段缺失，先复查本地输出；确认缺口后再调用 `apify-amazon-scraper` 针对缺口补采。
4. **记录 lineage**：输出给报告的数据必须带采集时间、搜索词/类目、采集脚本名、样本量、商品 URL 或 ASIN。
5. **失败不进报告**：采集失败、空字段和报错信息只保存在采集日志，不进入最终分析报告。

### 字段列表（v6.3）

| # | 字段 | 来源 | 说明 |
|---|------|------|------|
| 1 | 序号 | 自动 | 商品编号 |
| 2 | 首图 | 搜索页 | 高清PNG嵌入Excel |
| 3 | **ASIN** | 详情页 | 亚马逊10位标准识别码 |
| 4 | **商品标题** | 搜索页 | 完整名称 |
| 5 | **品牌名称** | 详情页 | Brand Name |
| 6 | **价格($)** | 详情页 BuyBox核心区 | **TierP 精准选择器**，排除划线价/分期价/配件价 |
| 7 | **评分** | 详情页 | 星级数字，如 4.8 |
| 8 | **评论数** | 搜索页 | 累计评论量 |
| 9 | **BSR排名** | 详情页 | 全量大类+小类（最多8条） |
| 10 | **五点描述** | 详情页 | About this item Bullet Points |
| 11 | **规格参数** | 详情页 | **仅含3类**: Weight / Size-Dimension / Material |
| 12 | **月销量** | 搜索页 | 过去30天购买量 |
| 13 | **客户差评** | 评论页（可选）| 1-2星差评，前3条摘要（每条前150字）+总条数 |
| 14 | **商品链接** | 搜索页 | 可点击URL |

> 不采集评论时，字段为13列（无"客户差评"列）；采集时为14列。

---

## 使用方式

```
# 仅采集商品数据（默认，不含评论）
用户输入：搜索 "wireless earbuds" 的 Best Seller 商品

# 采集商品数据 + 差评（每商品约20条 1-2星差评）
用户输入：采集 "yoga mat" 前20个畅销商品，并采集每个商品的差评
```

### 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| 搜索词 | ✅ | - | 完整短语 |
| 数量 | ❌ | 50 | 1–100 |
| 排序方式 | ❌ | sales | sales=按销量, reviews=按评论数 |
| 输出目录 | ❌ | Desktop/YYYY-MM-DD/ | 可指定任意路径 |
| 评论模式 | ❌ | skip | reviews=差评 / all=全部 / skip=不采集 |
| 差评页数 | ❌ | 2 | 每商品采几页评论，每页10条 |

---

## 输出结果

```bash
Desktop/YYYY-MM-DD/
├── amazon_YYYYMMDD_HHMMSS.xlsx   # Excel（13或14列）
├── amazon_YYYYMMDD_HHMMSS.lineage.json # 建议输出：采集来源、搜索词、脚本版本、样本量、时间
└── images/
    ├── 001.png ~ 050.png          # 高清首图
```

---

## 技术特性

### 价格提取策略（v6.3 核心修复）

| 优先级 | 选择器/方法 | 说明 |
|--------|------------|------|
| **Tier P**（新增） | `#corePriceDisplay_desktop_feature_div .a-offscreen` / `.priceToPay span.a-offscreen` 等 | Amazon 最新版核心价格容器，不包含划线价 |
| **Tier 0a** | `#corePrice_feature_div .a-offscreen` | 核心价格容器 |
| **Tier 0b** | `#priceblock_ourprice` / `#priceblock_dealprice` | 旧版经典价格 ID |
| **Tier 0b+**（修复） | BuyBox 容器内 `.a-offscreen`，**跳过 `a-text-strike` 划线价** | 不再全局命中，严格限制范围 |
| **Tier 0c** | BuyBox 整体文本正则 | 二次兜底 |
| **Tier 1** | 其他价格 ID/class | 备用 |
| **Tier 2** | LD+JSON `offers.price` (USD) | 结构化数据 |
| **Tier 3**（优化） | 全文正则 + **中位数策略** | 不再取最低价（避免配件低价），取合理区间中位数 |

**v6.2→v6.3 价格修复说明**：
- 旧版 `.a-price .a-offscreen` 全局命中，可能误取划线原价或配件价
- v6.3 新增 Tier P 层，优先命中 `corePriceDisplay`/`priceToPay` 等专属容器
- `.a-price .a-offscreen` 严格限制在已知 BuyBox 容器（`#buyBoxSection` 等）内
- Tier 3 兜底从"最低价"改为"中位数策略"，减少干扰

### 评论采集功能（v6.3 新增）

| 参数 | 说明 |
|------|------|
| `negative` / `critical` | 1-2星差评（最常用，用于竞品痛点分析） |
| `one_star` | 仅1星评论 |
| `two_star` | 仅2星评论 |
| `all` | 全部评论（不过滤） |
| `positive` | 4-5星好评 |

**采集量说明**：
- 每页约 **10 条**评论
- 默认采 **2 页 = ~20 条**差评（可调整为 3 页 = ~30 条）
- Amazon 评论页对爬虫相对宽松，但仍建议保持 2 秒间隔
- 每条评论内容截取前 **400 字**，Excel 展示前 **150 字** × 3 条摘要

**Excel 输出格式**（"客户差评"列）：
```
共 18 条差评
──────────────────────────────
[差评 1]
★ 1.0 out of 5 stars
【标题文字】
正文前150字...
Reviewed in the United States on May 2, 2025

[差评 2]
...（另有15条差评未显示）
```

### 防限流机制

| 场景 | 策略 |
|------|------|
| 搜索翻页间隔 | 3 秒 |
| 详情页访问间隔 | 2 秒 |
| 评论页访问间隔 | 2 秒（在详情页后额外间隔1.5秒再访问） |
| 每5页额外等待 | +2 秒 |
| 遇到 429/503 | 指数退避 5→60秒 |
| User-Agent轮换 | 3种UA随机 |

---

## 命令行用法

```bash
# 仅采集商品（不含评论）
python amazon_scraper_core.py "wireless earbuds" sales 20

# 采集商品 + 差评（2页≈20条/商品）
python amazon_scraper_core.py "yoga mat" sales 20 "" reviews 2

# 采集商品 + 差评（3页≈30条/商品），指定输出目录
python amazon_scraper_core.py "phone case" sales 30 "C:/data/output" reviews 3

# 采集商品 + 全部评论
python amazon_scraper_core.py "baby monitor" sales 10 "" all 2
```

---

## 常见问题

**Q: 什么时候还需要 apify-amazon-scraper？**
仅在本技能无法拿到关键字段、样本量明显不足、被 Amazon 限流/验证码拦截，或需要本技能未覆盖的字段时使用。Apify 补采应限定缺口字段或缺口 ASIN，不重新全量抓取同一关键词。

**Q: 价格还是不准？**
v6.3 新增 Tier P 层专门针对 Amazon 最新版页面（corePriceDisplay/priceToPay），同时 .a-price .a-offscreen 严格限制在 BuyBox 容器内，不会误命中划线价。

**Q: 评论能采集多少条？**
默认每个商品采 2 页 ≈ 20 条差评。调整第6个参数可采更多（如 3 页 ≈ 30 条）。

**Q: 能只采差评吗？**
可以。评论模式填 `reviews` 或 `negative` 即只采 1-2 星差评，非常适合竞品痛点分析。

**Q: 采集评论会不会更慢？**
会。每个商品多 2 次网络请求（评论页 × 2 页）+ 延迟，整体时间约增加 30-50%。

**Q: 为什么有些字段是 null？**
页面未展示的字段记为 null。详情页请求失败时深度字段为 null。

---

## 文件结构

```
amazon-product-scraper/
├── SKILL.md                        # 本文件（v6.3）
├── _meta.json                      # 元数据
├── requirements.txt                # Python依赖
├── amazon_scraper.py               # 入口脚本
└── scripts/
    └── amazon_scraper_core.py      # 核心采集逻辑 v6.3
```

## 版本历史

| 版本 | 主要变更 |
|------|---------|
| v6.3 | 价格精准修复（Tier P + BuyBox限制 + 中位数兜底）；新增差评采集（20条/商品） |
| v6.2 | 价格 Tier0 重构；BSR全量；规格精简（W/D/M）；路径可配置 |
| v6.1 | 评分精准定位；品牌合并；BSR改进 |
| v6.0 | 架构重构，搜索页+详情页分离采集 |
