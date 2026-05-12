---
name: amazon-product-researcher
description: |
  亚马逊精细化选品调研报告生成器 | Amazon Product Research Report Generator

  # 核心功能
  只需输入【市场 + 类目】，自动完成全链路数据采集与选品分析：
  - 📊 Amazon 竞品数据采集
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
version: 2.0
---

# 🛒 Amazon Product Research Toolkit

## 核心入口 Skill

> **输入市场 + 类目，自动生成完整选品调研报告**

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
```

---

## 自动化流程

当用户输入选品调研需求时，自动执行以下流程：

### Step 1: 解析用户输入

```python
# 自动解析以下参数
input_parser = {
    "market": "US/UK/DE/...",      # 市场
    "category": "kids supplements", # 类目
    "keywords": ["相关关键词"],    # 自动扩展
    "requirements": {...}          # 可选要求
}
```

### Step 2: 数据采集 (调用子 Skills)

```
📊 amazon-product-scraper
   └─→ 采集 Amazon BSR Top 100 商品数据

📱 apify-amazon-scraper
   └─→ 通过 Apify API 采集详细竞品数据

📈 apify-market-scraper
   └─→ 采集市场规模和 CAGR 数据

📱 apify-tiktok-scraper
   └─→ 采集 TikTok 标签和达人数据

🔍 market-intelligence
   └─→ 市场趋势和消费者洞察
```

### Step 3: 智能分析

```
🧠 关键词拆解 → 子类目分析
   └─→ 识别细分市场机会

📊 竞争分析 → 品牌集中度/CPC/评分
   └─→ 识别真正蓝海

📱 TikTok 验证 → 流量趋势/爆款内容
   └─→ 验证传播潜力

💰 利润建模 → 成本结构/毛利率/净利率
   └─→ 评估盈利空间
```

### Step 4: 报告生成

```
📝 report-generator
   └─→ 生成完整选品调研报告
      ├─ 市场定义
      ├─ 需求逻辑
      ├─ 竞争分析
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

---

## 配置

### 环境变量 (.env)

```bash
# 必需
APIFY_API_TOKEN=your-api-token

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
├── apify-market-scraper (可选)
├── apify-tiktok-scraper (可选)
├── market-intelligence (可选)
├── profit-model-builder (自动调用)
└── report-generator (必需)
```

*如无 Apify Token，将使用基础采集模式

---

## 输出

### 报告结构

```
1. 执行摘要
2. 市场定义与规模
3. 需求逻辑分析
4. 竞争格局分析
5. TikTok 流量验证
6. 利润模型构建
7. 产品矩阵规划
8. 执行路径
9. 风险评估
10. 选品建议
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
   - 引流款: $14.99 (毛利率: 51.3%)
   - 主打款: $22.99 (毛利率: 65.2%)
   - 利润款: $29.99 (毛利率: 69.7%)

📱 TikTok 验证:
   - #kidssupplements 播放量: 5.2亿
   - 主要内容: 产品评测、使用场景

📝 完整报告已生成...
```

---

## 注意事项

1. **API Token**: 确保配置了 Apify API Token
2. **数据新鲜度**: 市场数据建议定期更新
3. **市场差异**: 不同市场(US/UK/DE)的选品标准略有差异
4. **持续迭代**: 选品是一个持续优化的过程

---

## 相关 Skills

- [amazon-product-scraper](./amazon-product-scraper/) - 亚马逊商品采集
- [apify-amazon-scraper](./apify-amazon-scraper/) - Apify API 采集
- [profit-model-builder](./profit-model-builder/) - 利润模型构建
- [report-generator](./report-generator/) - 报告生成
- [market-intelligence](./market-intelligence/) - 市场情报分析
