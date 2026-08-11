# product-market-researcher

这是这套 skills 的主 skill。

它的目标很简单：你只要输入“市场 + 类目”，它就会帮你做完整的选品调研，并输出可落地的 Excel 总表和 HTML 报告。

## 你可以把它理解成什么

它不是单纯的抓取脚本，而是一个“调研总控器”：

1. 先判断该抓什么数据
2. 再按平台选择合适的子 skill
3. 把采集到的真实数据统一整理成 Excel
4. 再基于 Excel 生成 HTML 可视化报告

所以，平时你大多数时候只需要用这个主 skill。

## 什么时候用主 skill

适合以下场景：

- 你想做一整套选品调研
- 你只给得出市场和类目，不知道该从哪里开始
- 你需要同时看 Amazon、TikTok、Reddit、1688、Google Trends、市场报告
- 你想要最后直接拿 Excel + HTML 报告

示例：

- `帮我调研美国市场的 kids supplements`
- `请分析英国市场的 probiotic gummies 选品机会`
- `帮我做一个美国 hair clips 的完整市场调研`

## 主 skill 会做什么

### 1. 解析你的需求

它会从你的输入里提取：

- 市场
- 类目
- 核心关键词
- 是否需要供应商、趋势、评论、利润模型、报告

### 2. 按规则采集数据

默认采集逻辑是：

- Amazon：先用 `amazon-product-scraper`
- Amazon 字段缺失/报错：再用 `apify-amazon-scraper`
- 其他平台：优先用 Apify 对应 Actor
- Apify 不可用时：再用 Web Search / Web Fetch 兜底

### 3. 统一成 Excel 总表

主 skill 会把所有真实可用的数据先写入 Excel 总表。

这张表是后面分析和报告的唯一数据底座。

### 4. 生成 HTML 报告

然后再基于 Excel 和分析结果生成 HTML 可视化报告。

如果某些数据没抓到，相关章节就不显示，不会硬编。

## 主 skill 和子 skills 的分工

| Skill | 作用 |
| --- | --- |
| `product-market-researcher` | 总控全流程，适合完整调研 |
| `amazon-product-scraper` | Amazon 本地抓取，低成本优先 |
| `apify-amazon-scraper` | Amazon 补缺，字段不够时兜底 |
| `apify-tiktok-scraper` | TikTok 视频和搜索词采集 |
| `tiktok-analytics` | TikTok 标签流量和趋势分析 |
| `apify-market-scraper` | 市场报告和行业公开数据采集 |
| `market-intelligence` | 行业规模、CAGR、市场洞察分析 |
| `profit-model-builder` | 成本、毛利、净利、定价模型 |
| `report-generator` | 把数据整理成最终 HTML 报告 |

## 输出物

默认会产出三类结果：

- Excel 总表：所有可用数据先落表
- HTML 报告：给人看的分析结果
- 原始数据：便于复核和二次分析

如果有 Google Trends，还会保存：

- 趋势截图
- 近 6 个月趋势数据

## 怎么直接运行

在仓库里可以这样跑：

```bash
python scripts/main.py --market US --category "kids supplements"
```

如果你有更明确的关键词：

```bash
python scripts/main.py --market US --category "kids supplements" --keywords "children vitamins" "gummy vitamins"
```

如果你只是想先试跑，不做正式采集：

```bash
python scripts/main.py --category demo --market US --dry-run
```

## 配置

至少需要：

- `APIFY_API_TOKEN`

如果你要用飞书写入或 TikTok 辅助脚本，还可能需要：

- `FEISHU_BASE_TOKEN`
- `FEISHU_TABLE_ID`
- `FEISHU_VIEW_ID`
- `TIKTOK_OUTPUT_DIR`

配置示例见：[`./.env.example`](./.env.example)

## 常见使用方式

### 方式一：只用主 skill

你只要告诉它：

> 帮我调研美国市场的 hair clips 选品机会

它会自动走完整流程。

### 方式二：只用某个子 skill

如果你已经知道自己只缺哪一块，就直接用对应子 skill。

例如：

- 只想抓 Amazon 竞品：用 `amazon-product-scraper`
- 只想抓 TikTok 热度：用 `apify-tiktok-scraper`
- 只想算利润：用 `profit-model-builder`
- 只想生成报告：用 `report-generator`

## 给新手的一句话建议

如果你不知道从哪开始，就直接用 `product-market-researcher`。

如果你已经有目标，只缺某一类数据，就直接找对应子 skill。
