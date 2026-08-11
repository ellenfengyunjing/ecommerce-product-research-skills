---
name: report-generator
description: |
  选品调研报告自动生成技能。当用户需要以下任务时应使用此技能：
  - 根据采集的数据生成完整选品调研报告
  - 根据真实采集数据生成 HTML 可视化报告
  - 将 Markdown 报告转换为 PDF
  - 生成包含竞品数据、利润模型的完整报告
  - 按照指定模板生成报告
triggers:
  - 生成报告
  - 生成选品报告
  - 输出PDF
  - 生成调研报告
  - report generation
  - 输出报告
agent_created: true
---

# Report Generator v1.1

## 功能说明

本技能根据采集的数据自动生成完整的选品调研报告。被 `amazon-product-researcher` 调用时，默认输出 HTML 可视化报告；Markdown/PDF/Word 仅在用户明确要求时作为辅助格式输出。

## 数据渲染硬规则

1. **只渲染已采集数据**：任何报错、空字段、空表、占位符、示例值、未采集字段、无法验证字段，都不得进入最终报告。
2. **不显示失败提示**：最终报告正文不得出现“暂无数据”“未采集”“采集失败”“报错”“待补充”等提示。采集失败只写入内部采集日志或原始数据目录。
3. **逐板块来源标注**：每个可见章节/图表/表格底部必须标注实际使用的数据来源，至少包含平台、采集方式、脚本或 Actor 名、采集时间、样本量或 URL。
4. **无来源不分析**：没有 lineage 的数据不得参与 KPI、评分、图表、结论、风险判断和产品推荐。
5. **章节静默隐藏**：某章节核心数据不足时，隐藏该章节或隐藏对应图表，不用空表和提示语占位。
6. **分析优先于原始堆砌**：可以附录呈现部分完整采集数据，但主体报告必须以分析过程、交叉验证和结论为主。

### HTML 报告优先级

`amazon-product-researcher` 调用本技能时使用以下输出顺序：

1. HTML 主报告：Chart.js 图表、来源折叠块、分析结论。
2. 原始数据文件：JSON/CSV/XLSX，保留采集日志、失败原因和缺口说明。
3. Markdown/PDF/Word：仅按用户要求额外导出，不替代 HTML 主报告。

### Data Lineage 最小结构

```json
{
  "source_platform": "Amazon | TikTok | Reddit | 1688 | Google Trends | Market Report | Web",
  "collector": "amazon-product-scraper | apify-tiktok-scraper | apify/web-scraper | web-search",
  "run_id": "Apify run id or local script batch id",
  "collected_at": "YYYY-MM-DD HH:mm:ss",
  "sample_size": 50,
  "url": "https://..."
}
```

## 报告模板

通用模板仍可用于 Markdown/PDF 辅助输出。用于深度选品调研时，优先遵循 `amazon-product-researcher` 的 16 章 HTML 结构；本 12 章节模板不得覆盖主 skill 的章节框架。

```markdown
# {类目} {市场} 深度选品调研报告

**报告编号**：{TK-CATEGORY-YYYYMMDD}
**调研周期**：{YYYY年MM月}
**覆盖维度**：市场定义、需求逻辑、落地路径、消费者画像、趋势验证、容量筛选、产品生命周期定位、竞品对标、利润模型、产品矩阵、自主研发策略

---

## 一、市场与成分定义（精准定位）

### 1. 市场定义
{目标市场} {类目}（{年龄范围}）
- 官方范畴：{合规分类}
- {年份}市场规模：{金额}
- 年增速：{CAGR}
- 线上占比：{占比}
- 线下占比：{占比}

### 2. 主要成分科学定义
- **成分A**：{定义}；{功能}；{安全剂量}
- **成分B**：{定义}；{功能}；{安全剂量}

---

## 二、需求逻辑与市场价值（数据驱动）

### 1. 消费者核心需求
| 需求 | 占比 | 说明 |
|------|------|------|
| 免疫防护 | XX% | {说明} |
| 护眼抗蓝光 | XX% | {说明} |
| 肠胃与抗炎 | XX% | {说明} |

### 2. 各成分价值与风险
| 成分 | 价值 | 风险 | 推荐度 |
|------|------|------|--------|
| 成分A | {描述} | {描述} | ⭐⭐⭐⭐⭐ |
| 成分B | {描述} | {描述} | ⭐⭐⭐⭐ |

---

## 三、消费者画像

### 1. 决策人画像
- 年龄：{范围}
- 性别：女{占比}/男{占比}
- 收入：${范围}
- 核心行为：{描述}

### 2. 使用者分龄
| 年龄段 | 使用率 | 偏好剂型 | 痛点 |
|--------|--------|----------|------|
| 2-5岁 | XX% | 软糖/滴剂 | {痛点} |
| 6-11岁 | XX% | 咀嚼片/软糖 | {痛点} |

### 3. 痛点与决策关键词
- 家长痛点：{列举}
- 决策关键词：{列举}

---

## 四、市场趋势交叉验证

### 1. 行业趋势
- 市场规模：{金额}
- CAGR：{百分比}
- 剂型趋势：{描述}
- 功能趋势：{分布}

### 2. TikTok流量趋势
| 标签 | 播放量 | 热度 |
|------|--------|------|
| #标签1 | XX亿+ | 🔥🔥🔥🔥🔥 |
| #标签2 | XX亿+ | 🔥🔥🔥🔥 |

### 3. 渠道趋势
- 药房：{增速}
- 有机店：{增速}
- 商超：{价格带}

### 4. 竞品趋势
- 主流品牌：{列举}
- 爆款：{列举}
- 市场缺失：{机会}

---

## 五、市场容量筛选

### 1. 分成分容量与增速

| 成分 | 市场规模 | 年增速 | 竞争度 | 壁垒 | 准入评分 |
|------|----------|--------|--------|------|----------|
| 成分A | X亿美元 | XX% | {等级} | {等级} | ⭐⭐⭐⭐ |
| 成分B | X亿美元 | XX% | {等级} | {等级} | ⭐⭐⭐ |

### 2. 筛选结论
- **必选**：{成分}
- **优选**：{成分}
- **淘汰**：{成分}

---

## 六、产品生命周期定位

### 1. 生命周期判断
| 成分 | 阶段 | 特征 | 策略 |
|------|------|------|------|
| 成分A | 成熟期 | {描述} | {策略} |
| 成分B | 成长期 | {描述} | {策略} |

### 2. 组合策略
- 引流款：{成分}（{阶段}）
- 主打款：{成分}（{阶段}）
- 利润款：{成分}（{阶段}）

---

## 七、竞品价格对标

### 1. 分成分竞品对比

#### {成分A}
| 品牌 | 价格 | 规格 | 毛利 | 卖点 |
|------|------|------|------|------|
| 竞品A | $XX | XX粒 | XX% | {卖点} |
| 竞品B | $XX | XX粒 | XX% | {卖点} |
| **自研对标** | $XX | XX粒 | XX% | {卖点} |

---

## 八、利润模型

### 1. 成本结构

| 成本项 | 金额/瓶 | 占比 |
|--------|---------|------|
| 原料成本 | $X.XX | XX% |
| 包材成本 | $X.XX | XX% |
| 生产费用 | $X.XX | XX% |
| 检测费用 | $X.XX | XX% |
| 物流成本 | $X.XX | XX% |
| **总计** | **$X.XX** | **100%** |

### 2. 利润模型

| 产品 | 售价 | 总成本 | 毛利 | 毛利率 | 净利 | 净利率 |
|------|------|--------|------|--------|------|--------|
| 引流款 | $XX | $X | $X | XX% | $X | XX% |
| 主打款 | $XX | $X | $X | XX% | $X | XX% |
| 利润款 | $XX | $X | $X | XX% | $X | XX% |

### 3. 全域利润
- TikTok（60%）：净利率 XX%
- 线下（40%）：净利率 XX%
- **综合净利率**：XX%+

---

## 九、产品矩阵

### 1. 引流款
- **产品名**：{名称}
- **配方**：{配方描述}
- **定价**：${价格}
- **渠道**：{渠道}

### 2. 主打款
- **产品名**：{名称}
- **配方**：{配方描述}
- **定价**：${价格}
- **渠道**：{渠道}

### 3. 利润款
- **产品名**：{名称}
- **配方**：{配方描述}
- **定价**：${价格}
- **渠道**：{渠道}

### 4. 配套款
- **产品名**：{名称}
- **配方**：{配方描述}
- **定价**：${价格}
- **渠道**：{渠道}

---

## 十、落地执行路径

### 1. 研发阶段（1-30天）
- 配方定稿：{描述}
- 原料锁定：{描述}
- 检测认证：{描述}

### 2. 产品与包装（31-45天）
- 剂型：{描述}
- 包装：{描述}
- 视觉：{描述}

### 3. TikTok运营（46-60天）
- 内容矩阵：{描述}
- 流量打法：{描述}
- 合规红线：{描述}

### 4. 线下铺货（61-90天）
- 渠道分级：{描述}
- 政策：{描述}

### 5. 数据复盘
- 线上KPIs：{指标}
- 线下KPIs：{指标}

---

## 十一、核心优势与壁垒

| 壁垒类型 | 说明 |
|----------|------|
| 配方壁垒 | {描述} |
| 原料壁垒 | {描述} |
| 技术壁垒 | {描述} |
| 合规壁垒 | {描述} |
| 全域壁垒 | {描述} |

---

## 十二、总结与战略路径

### 1. 核心结论
- 主力：{成分}
- 基础：{成分}
- 利润：{成分}
- 配套：{成分}

### 2. 1年战略目标
- 月销：{数量}+瓶
- 营收：${金额}+
- 净利：${金额}+（XX%）
- 渠道：TikTok（XX%）+ 线下（XX%）

### 3. 风险控制
- 合规：{策略}
- 供应链：{策略}
- 竞争：{策略}

---

**报告生成时间**：{YYYY-MM-DD HH:MM:SS}
```

## 使用方式

### 方式一：生成 HTML 主报告（推荐）

```python
def visible(value):
    """只允许真实、非空、非错误的数据进入报告。"""
    if value in (None, "", [], {}, "N/A", "暂无数据", "未采集", "采集失败"):
        return False
    if isinstance(value, dict) and value.get("error"):
        return False
    return True

def has_lineage(block):
    lineage = block.get("lineage") if isinstance(block, dict) else None
    return bool(lineage and (lineage.get("collector") or lineage.get("url")) and lineage.get("collected_at"))

def render_section(section):
    if not visible(section.get("data")) or not has_lineage(section):
        return ""
    return render_html_section(section)
```

### 方式二：直接生成 Markdown 报告

```python
def generate_report(data):
    """根据采集数据生成选品调研报告"""

    template = """
# {类目} {市场} 深度选品调研报告

报告编号：{report_id}
调研周期：{start_date} - {end_date}

---

## 一、市场与成分定义

### 1. 市场定义
{market_definition}

### 2. 主要成分科学定义
{ingredients_definition}

---

## 二、需求逻辑与市场价值

{...完整12章节...}
"""

    # 填充数据
    report = template.format(**data)

    # 保存
    save_path = f"./output/{data['report_id']}.md"
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return save_path
```

### 方式三：生成 PDF 报告

```python
def generate_pdf_report(markdown_path):
    """将 Markdown 转换为 PDF"""

    # 使用 pandoc 转换
    import subprocess

    output_pdf = markdown_path.replace('.md', '.pdf')

    cmd = [
        'pandoc',
        markdown_path,
        '-o', output_pdf,
        '--pdf-engine=xelatex',
        '-V', 'mainfont=SimSun',
        '-V', 'geometry:margin=1in'
    ]

    subprocess.run(cmd, check=True)

    return output_pdf
```

### 方式四：生成 Word 报告

```python
def generate_word_report(markdown_path):
    """将 Markdown 转换为 Word"""

    import subprocess

    output_docx = markdown_path.replace('.md', '.docx')

    cmd = [
        'pandoc',
        markdown_path,
        '-o', output_docx,
        '-s'  # standalone
    ]

    subprocess.run(cmd, check=True)

    return output_docx
```

## 报告数据结构

```python
report_data = {
    # 基本信息
    "report_id": "TK-KIDSUP-20260511",
    "category": "儿童保健品",
    "market": "美区",
    "period": "2026年1-5月",

    # 市场数据
    "market_size": {
        "global_2025": "35.9亿美元",
        "global_2033": "63.5亿美元",
        "us_2025": "124亿美元",
        "cagr": "7.9%"
    },

    # 成分数据
    "ingredients": [
        {
            "name": "复合维生素",
            "market_size": "43.4亿美元",
            "growth_rate": "9.1%",
            "competition": "高（红海）",
            "recommendation": "必选"
        },
        # ...
    ],

    # 竞品数据
    "competitors": [...],

    # TikTok数据
    "tiktok_tags": [...],

    # 消费者画像
    "consumer_profile": {...},

    # 利润模型
    "profit_model": {
        "products": [
            {
                "type": "引流款",
                "name": "儿童多维软糖",
                "selling_price": 14.99,
                "cost": 7.40,
                "gross_margin": 49.9,
                "net_margin": 31.9
            },
            # ...
        ]
    },

    # 产品矩阵
    "product_matrix": {...},

    # 执行路径
    "execution_plan": {...}
}
```

## 输出路径

```
./output/
├── 2026-05-11_儿童保健品_美区/
│   ├── 选品调研报告.md          # 主报告
│   ├── 选品调研报告.pdf          # PDF版
│   ├── 竞品数据.xlsx             # 竞品数据表
│   ├── TikTok数据.json          # TikTok数据
│   └── 利润模型.xlsx            # 利润模型表
```

## 依赖工具

| 工具 | 安装方式 | 用途 |
|------|----------|------|
| pandoc | `brew install pandoc` 或官网下载 | Markdown转PDF/Word |
| python-docx | `pip install python-docx` | Word报告生成 |
| reportlab | `pip install reportlab` | PDF报告生成 |

## 注意事项

1. 报告数据需先通过 amazon-product-scraper、Apify 系列 skills、market-intelligence 或可验证公开来源采集。
2. 最终报告只展示采集到且可验证的数据和分析结果；失败、缺失、报错信息只保存在采集日志。
3. Markdown/PDF/Word 为辅助格式，HTML 是深度选品调研的默认主交付物。
4. 报告中的图片需要单独保存并在 Markdown/HTML 中引用。
5. 建议生成报告后审核关键数据来源和结论链路。
