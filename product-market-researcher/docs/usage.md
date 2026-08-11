# 📖 使用示例 (Usage Examples)

本文档提供 Amazon Product Research Toolkit 的完整使用示例。

---

## 目录

1. [快速开始](#快速开始)
2. [命令行使用](#命令行使用)
3. [WorkBuddy 使用](#workbuddy-使用)
4. [高级配置](#高级配置)
5. [完整案例](#完整案例)

---

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/amazon-product-researcher.git
cd amazon-product-researcher

# 安装依赖
pip install -r requirements.txt

# 安装 python-dotenv (环境变量支持)
pip install python-dotenv
```

### 2. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Apify API Token
notepad .env  # Windows
nano .env     # macOS/Linux
```

### 3. 运行

```bash
cd skills/amazon-product-researcher/scripts
python main.py --market US --category "kids supplements"
```

---

## 命令行使用

### 基础用法

```bash
python main.py --market <市场> --category <类目> [选项]
```

### 参数说明

| 参数 | 简写 | 必需 | 说明 |
|------|------|------|------|
| `--market` | `-m` | ✅ | 市场代码 (US/UK/DE/...) |
| `--category` | `-c` | ✅ | 产品类目 |
| `--keywords` | `-k` | ❌ | 关键词列表 (空格分隔) |
| `--config` | | ❌ | 配置文件路径 (JSON) |
| `--output-format` | `-f` | ❌ | 输出格式 (markdown/pdf/word/html) |
| `--output-dir` | `-o` | ❌ | 输出目录 |
| `--max-products` | | ❌ | 最大采集数量 |
| `--debug` | | ❌ | 启用调试模式 |
| `--dry-run` | | ❌ | 仅解析输入，不执行采集 |

### 示例 1：基础采集

```bash
# 采集美国市场儿童保健品数据
python main.py --market US --category "kids supplements"
```

### 示例 2：指定关键词

```bash
# 使用多个关键词采集
python main.py --market US --category "kids vitamins" \
    --keywords "children's vitamins" "gummy vitamins" "kids multivitamin"
```

### 示例 3：指定输出格式

```bash
# 生成 Word 格式报告
python main.py --market US --category "probiotics" --output-format word
```

### 示例 4：使用配置文件

```bash
# 创建配置文件 config.json
echo '{
    "market": "US",
    "category": "kids supplements",
    "keywords": ["kids vitamins", "children's supplements"],
    "max_products": 200,
    "output_format": "markdown"
}' > config.json

# 使用配置文件运行
python main.py --config config.json
```

### 示例 5：调试模式

```bash
# 启用调试模式，查看详细日志
python main.py --market US --category "pet supplements" --debug
```

### 示例 6：Dry Run

```bash
# 仅解析输入参数，不执行采集
python main.py --market US --category "beauty supplements" --dry-run
```

---

## WorkBuddy 使用

### 方式一：自然语言输入

在 WorkBuddy 中直接输入：

```
"帮我分析美国市场儿童保健品类目的选品机会"
"研究英国市场益生菌产品的市场情况"
"调研澳洲市场宠物保健品的市场规模和竞争格局"
```

### 方式二：结构化输入

```
市场: US
类目: kids supplements
关键词: children's vitamins, gummy vitamins, kids probiotic
```

### 方式三：调用特定 Skill

```
/ amazon-product-scraper "kids vitamins" 100
/apify-amazon-scraper "children's health products" 50
/profit-model-builder --price 24.99 --cost 5.0
/report-generator --input ./data/processed.json
```

---

## 高级配置

### 自定义采集参数

编辑 `scripts/config.py`：

```python
# 采集配置
COLLECTION_CONFIG = {
    "max_products": 200,              # 增加采集数量
    "min_review_count": 100,          # 提高评论数门槛
    "price_range": (15, 60),         # 调整价格区间
    "request_delay": 1,               # 加快采集速度
    "proxy_enabled": True,            # 启用代理
}
```

### 调整选品标准

```python
# 选品决策标准
SELECTION_CRITERIA = {
    "search_volume": {
        "min": 50000,                # 提高搜索量要求
        "max": 200000,
        "weight": 0.25,               # 增加权重
    },
    "brand_concentration": {
        "max": 0.25,                # 降低品牌集中度要求
        "weight": 0.20,
    },
    # ... 其他指标
}
```

### 利润模型调整

```python
# 成本结构
PROFIT_CONFIG = {
    "product_cost": 4.5,            # 降低产品成本
    "platform_fee_rate": 0.12,      # 降低平台费率 (12%)
    "advertising_rate": 0.15,       # 降低广告占比
    "min_margin": 0.35,            # 提高最低利润率要求
}
```

---

## 完整案例

### 案例 1：美国市场儿童保健品选品

**目标**：分析美国市场儿童保健品类的选品机会

#### Step 1: 运行采集

```bash
cd skills/amazon-product-researcher/scripts
python main.py --market US --category "kids supplements" \
    --keywords "children's vitamins" "kids probiotic" \
    --max-products 100 \
    --output-format markdown
```

#### Step 2: 查看输出

```
🛒 Amazon Product Research Pipeline
============================================================
市场: US | 类目: kids supplements
关键词: children's vitamins, kids probiotic
============================================================

📊 Step 1: 数据采集中...
   ├─ 采集 Amazon 商品数据...
   ├─ 采集 TikTok 流量数据...
   └─ 采集市场数据...
   ✅ 采集完成: 87 个商品, 6 条 TikTok 数据

🧠 Step 2: 数据分析中...
   ├─ 分析市场机会...
   ├─ 分析 TikTok 传播潜力...
   └─ 构建利润模型...
   ✅ 分析完成

📝 Step 3: 生成报告中...
   ✅ 报告已生成: ./output/20260512_143025_kids_supplements_report.md
```

#### Step 3: 查看报告

```bash
# 打开报告
notepad "./output/20260512_143025_kids_supplements_report.md"  # Windows
cat "./output/20260512_143025_kids_supplements_report.md"      # macOS/Linux
```

报告内容摘要：

```
# 🛒 亚马逊选品调研报告

**市场:** US | **类目:** kids supplements
**生成时间:** 2026-05-12T14:30:25

---

## 📋 执行摘要

### 🎯 识别到的蓝海机会

1. **kids digestive health supplement**
   - 搜索量: 2-4万/月
   - 品牌集中度低
   - 评分: 95/100

2. **kids immune support supplement**
   - 搜索量: 8-10万/月
   - 评分: 92/100

### 💰 推荐定价方案

| 产品定位 | 售价 | 利润 | 利润率 |
|----------|------|------|--------|
| 主打款 | $22.99 | $6.35 | 27.6% |
```

---

### 案例 2：英国市场益生菌产品分析

**目标**：分析英国市场益生菌产品的竞争格局

```bash
python main.py --market UK --category "probiotics" \
    --keywords "probiotic supplements" "gut health" \
    --output-format word
```

---

### 案例 3：批量分析多个类目

**目标**：一次性分析多个相关类目

```bash
# 创建批量分析脚本 batch_analysis.py
from main import ProductResearchPipeline
import json

categories = [
    {"market": "US", "category": "kids vitamins", "keywords": ["children's vitamins"]},
    {"market": "US", "category": "kids probiotics", "keywords": ["kids probiotic"]},
    {"market": "US", "category": "pet supplements", "keywords": ["dog vitamins"]},
]

results = []
for cat in categories:
    pipeline = ProductResearchPipeline(
        market=cat["market"],
        category=cat["category"],
        keywords=cat["keywords"]
    )
    result = pipeline.run()
    results.append(result)

# 保存汇总
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

运行：

```bash
python batch_analysis.py
```

---

## 故障排除

### 问题 1：提示 "APIFY_API_TOKEN 未设置"

**解决方案**：

```bash
# 检查 .env 文件是否存在
ls -la .env

# 如果不存在，创建它
cp .env.example .env

# 编辑 .env 文件，填入你的 API Token
```

### 问题 2：采集速度很慢

**解决方案**：

```bash
# 降低请求延迟
export REQUEST_DELAY=1

# 或减少采集数量
python main.py --market US --category "vitamins" --max-products 50
```

### 问题 3：生成报告失败

**解决方案**：

```bash
# 检查依赖是否安装
pip install markdown
pip install python-docx  # 如果要生成 Word
pip install pandoc     # 如果要生成 PDF

# 使用 markdown 格式（最稳定）
python main.py --output-format markdown
```

---

## 下一步

- [配置指南](docs/configuration.md)
- [选品方法论详解](docs/methodology.md)
- [常见问题](docs/faq.md)
- [贡献指南](CONTRIBUTING.md)
