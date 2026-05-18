---
name: amazon-product-researcher
description: |
  亚马逊精细化选品调研报告生成器 | Amazon Product Research Report Generator

  # 核心功能
  只需输入【市场 + 类目】，自动完成全链路数据采集与选品分析：
  - 📊 Amazon 竞品数据采集
  - 🏭 1688 供应商成本价格采集
  - 📱 TikTok 流量验证
  - 📈 市场趋势分析
  - 💰 利润模型构建
  - 📝 完整报告生成

  # 选品方法论
  拆市场 → 找需求 → 分析竞争 → 判断利润 → 内容传播 → 供应链 → 小量测试 → 放大优势

triggers:
  - 选品调研报告
  - 生成选品报告
  - 产品调研
  - 市场分析报告
  - 亚马逊选品
  - 类目调研
  - 细分市场分析
  - product research
  - product selection
  - market analysis
  - 帮我选品
  - 分析选品

agent_created: true
version: 2.1
---

# 🛒 Amazon Product Research Toolkit

## 核心入口 Skill

> **输入市场 + 类目，自动生成完整选品调研报告，并用 1688 供应商数据校准成本与利润模型**

---

## 使用方法

### 方式一：自然语言输入 (推荐)

```
"分析美国市场儿童保健品类目的选品机会"
"帮我调研英国市场益生菌产品的市场情况"
"研究澳洲市场宠物保健品的市场规模"
```

### 方式二：结构化输入

```
市场: US
类目: kids supplements
关键词: children's vitamins, gummy vitamins, kids probiotic
供应商成本: 需要 1688 准确成本
```

---

## 自动化流程

当用户输入选品调研需求时，自动执行以下流程：

### Step 1: 解析用户输入

```python
# 自动解析以下参数
input_parser = {
    "market": "US/UK/DE/...",       # 市场
    "category": "kids supplements", # 类目
    "keywords": ["相关关键词"],     # 自动扩展
    "supplier_keywords_zh": ["1688 中文供应商关键词"], # 由类目/竞品标题自动翻译和扩展
    "need_supplier_cost": True,     # 默认开启：报告需要准确成本时采集 1688
    "requirements": {...}           # 可选要求
}
```

### Step 2: 数据采集 (调用子 Skills)

```
📊 amazon-product-scraper
   └─→ 采集 Amazon BSR Top 100 商品数据

📱 apify-amazon-scraper
   └─→ 通过 Apify API 采集详细竞品数据

🏭 Apify 1688 供应商采集
   └─→ 当报告需要国内供应商准确成本时，使用 Apify 采集 1688 商品/供应商报价

📈 apify-market-scraper
   └─→ 采集市场规模和 CAGR 数据

📱 apify-tiktok-scraper
   └─→ 采集 TikTok 标签和达人数据

🔍 market-intelligence
   └─→ 市场趋势和消费者洞察
```

#### 1688 供应商成本采集要求

当用户要求生成选品调研报告、利润模型或供应链评估时，默认需要采集对应品类在 1688 的供应商成本价格；只有用户明确表示“不需要供应链成本/1688 数据”时才跳过。

1. **关键词生成**: 根据 Amazon 类目、竞品标题、五点描述和核心卖点，生成 3-8 个中文 1688 搜索关键词。例如 `kids probiotic gummies` → `儿童益生菌软糖`、`益生菌凝胶糖果代工`、`儿童营养软糖 OEM`。
2. **Apify 采集**: 使用 `APIFY_API_TOKEN` 调用可用的 1688/Alibaba 采集 Actor，按关键词抓取商品和供应商数据。优先选择支持商品标题、价格区间、MOQ、销量/成交、复购率、供应商年限、评分、地区、商品链接、主图的 Actor。
3. **字段标准化**: 输出统一字段：
   - `keyword`: 1688 搜索关键词
   - `title`: 商品标题
   - `supplier_name`: 供应商名称
   - `price_min_rmb` / `price_max_rmb`: 价格区间
   - `moq`: 起订量
   - `monthly_sales` 或 `transaction_count`: 月销量/成交量
   - `supplier_years`: 供应商年限
   - `rating` / `repurchase_rate`: 店铺评分/复购率
   - `location`: 供应商地区
   - `product_url`: 1688 商品链接
   - `image_url`: 主图
4. **成本清洗**: 剔除明显异常值、非同类产品、低可信供应商；按 MOQ 和规格统一到单件成本。无法确认规格时必须标注假设，不得把粗略报价写成确定成本。
5. **成本估算**: 计算 `low_cost_rmb`、`median_cost_rmb`、`high_cost_rmb`，并换算为目标市场币种。利润模型优先使用中位供应商成本，同时保留低/高成本敏感性分析。
6. **供应商筛选**: 至少列出 5-10 个候选供应商；如果有效供应商少于 5 个，报告必须提示“供应链数据不足”，并降低该细分机会评分。
7. **证据留存**: 报告中必须保留 1688 商品链接和采集时间，方便复核报价新鲜度。

### Step 3: 智能分析

```
🧠 关键词拆解 → 子类目分析
   └─→ 识别细分市场机会

📊 竞争分析 → 品牌集中度/CPC/评分
   └─→ 识别真正蓝海

📱 TikTok 验证 → 流量趋势/爆款内容
   └─→ 验证传播潜力

🏭 供应链验证 → 1688 报价/MOQ/供应商质量
   └─→ 判断国内供应是否充足、成本是否支撑目标售价

💰 利润建模 → 成本结构/毛利率/净利率
   └─→ 结合 1688 供应商成本、MOQ、包装/头程/FBA/平台费，评估盈利空间
```

### Step 4: 报告生成

```
📝 report-generator
   └─→ 生成完整选品调研报告
      ├─ 市场定义
      ├─ 需求逻辑
      ├─ 竞争分析
      ├─ TikTok 验证
      ├─ 1688 供应商成本
      ├─ 利润模型
      ├─ 产品矩阵
      └─ 选品建议
```

---

## 选品决策标准

| 指标 | 标准 | 权重 |
|------|------|------|
| 搜索量 | 2-10万/月 | 20% |
| 品牌集中度 | <30% | 15% |
| CPC | <$1 | 10% |
| 利润率 | >30% | 25% |
| TikTok 热度 | 播放量>1000万 | 15% |
| 供应链稳定 | 评分>4.0 | 15% |

供应链稳定评分必须综合 1688 可用供应商数量、报价离散度、MOQ、供应商年限/评分、成交量/复购率；不能只用单个最低报价判断。

---

## 配置

### 环境变量 (.env)

```bash
# 必需
APIFY_API_TOKEN=your-api-token

# 1688 供应商成本采集（可选但推荐）
APIFY_1688_ACTOR_ID=your-1688-actor-id
SUPPLIER_COST_SOURCE=1688
SUPPLIER_KEYWORDS_MAX=8
SUPPLIER_RESULTS_PER_KEYWORD=20
RMB_USD_RATE=auto

# 可选
DEFAULT_MARKET=US
OUTPUT_FORMAT=markdown
MAX_PRODUCTS=100
```

详见: [.env.example](../.env.example)

### 子 Skill 依赖关系

```
amazon-product-researcher (主入口)
├── amazon-product-scraper (可选)
├── apify-amazon-scraper (必需*)
├── Apify 1688 供应商采集 (利润模型需要准确成本时必需)
├── apify-market-scraper (可选)
├── apify-tiktok-scraper (可选)
├── market-intelligence (可选)
├── profit-model-builder (自动调用)
└── report-generator (必需)
```

*如无 Apify Token，将使用基础采集模式；如无 1688 Actor 配置，报告必须说明供应商成本未能自动采集，不能虚构成本数据。

---

## 输出

### 报告结构

```
1. 执行摘要
2. 市场定义与规模
3. 需求逻辑分析
4. 竞争格局分析
5. TikTok 流量验证
6. 1688 供应商成本与供应链验证
7. 利润模型构建
8. 产品矩阵规划
9. 执行路径
10. 风险评估
11. 选品建议
```

### 支持格式

- Markdown (默认)
- PDF
- Word
- HTML

---

## 示例

### 输入

```
"帮我分析美国市场儿童保健品类目的选品机会"
```

### 输出

```
📊 选品调研报告：美国市场 - 儿童保健品

✅ 识别出 3 个蓝海细分市场:
   1. kids digestive health supplement (评分: 95)
   2. kids immune support supplement (评分: 92)
   3. kids probiotic gummies (评分: 88)

💰 利润模型:
   - 1688 中位供应商成本: ¥8.60/件 (样本: 18 个有效供应商)
   - 引流款: $14.99 (毛利率: 51.3%)
   - 主打款: $22.99 (毛利率: 65.2%)
   - 利润款: $29.99 (毛利率: 69.7%)

🏭 1688 供应链验证:
   - 关键词: 儿童益生菌软糖、儿童营养软糖 OEM
   - MOQ 区间: 500-3000 件
   - 供应商风险: 需要确认配方资质、出口合规和标签备案

📱 TikTok 验证:
   - #kidssupplements 播放量: 5.2亿
   - 主要内容: 产品评测、使用场景

📝 完整报告已生成...
```

---

## 注意事项

1. **API Token**: 确保配置了 Apify API Token
2. **1688 成本准确性**: 1688 报价通常受规格、MOQ、包装、是否 OEM/ODM、税票和运费影响；报告必须标注成本假设和采集时间
3. **合规校验**: 保健品、儿童用品、食品接触类、带电产品等品类必须额外检查目标市场合规和认证成本
4. **数据新鲜度**: 市场数据和供应商报价建议定期更新
5. **市场差异**: 不同市场(US/UK/DE)的选品标准略有差异
6. **持续迭代**: 选品是一个持续优化的过程

---

## 相关 Skills

- [amazon-product-scraper](./amazon-product-scraper/) - 亚马逊商品采集
- [apify-amazon-scraper](./apify-amazon-scraper/) - Apify API 采集
- [profit-model-builder](./profit-model-builder/) - 利润模型构建
- [report-generator](./report-generator/) - 报告生成
- [market-intelligence](./market-intelligence/) - 市场情报分析
