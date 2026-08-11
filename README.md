# Ecommerce Product Research Skills

这不是单个 skill，而是一套“选品调研 skill 包”。

主入口在 `product-market-researcher/`，它负责完整的市场调研流程；其他目录是给主 skill 复用的子 skills，适合单独调用某个平台或单一能力。

## 这套 skills 能做什么

- 输入一个「市场 + 类目」，自动做完整选品调研
- 抓取 Amazon 竞品、差评、评论、图片、BSR、价格等数据
- 抓取 TikTok 热度、视频、标签流量趋势
- 抓取 Reddit 用户讨论、1688 供应商与报价、Google Trends 趋势
- 抓取市场报告中的公开数据
- 输出 Excel 总表、HTML 可视化报告、原始数据和趋势截图
- 基于真实数据做利润模型、机会判断、风险判断和落地建议

## 使用方式

如果你想做完整调研，直接用主 skill：

- `product-market-researcher`

如果你只想做单项任务，就直接用对应子 skill：

- 只抓 Amazon：`amazon-product-scraper` / `apify-amazon-scraper`
- 只抓 TikTok：`apify-tiktok-scraper` / `tiktok-analytics`
- 只抓市场报告：`apify-market-scraper` / `market-intelligence`
- 只算利润：`profit-model-builder`
- 只生成报告：`report-generator`

## 子 skill 速查

| Skill | 主要作用 | 适合场景 |
| --- | --- | --- |
| `product-market-researcher` | 主控全流程：采集、分析、出 Excel、出 HTML 报告 | 你要做一整套选品调研 |
| `amazon-product-scraper` | Amazon 本地低成本抓取 | 只想先抓 Amazon 商品和评论 |
| `apify-amazon-scraper` | Amazon 补缺采集 | 本地脚本缺字段、报错、限流时兜底 |
| `apify-tiktok-scraper` | TikTok 搜索词采集 | 只想抓 TikTok 视频/热度/文案 |
| `tiktok-analytics` | TikTok 标签和趋势分析 | 只想看某个话题/标签有没有量 |
| `apify-market-scraper` | 市场报告采集 | 只想抓市场规模、CAGR、公开报告摘要 |
| `market-intelligence` | 行业情报分析 | 只想做行业洞察、市场机会判断 |
| `profit-model-builder` | 利润/成本模型 | 只想算毛利、净利、定价空间 |
| `report-generator` | HTML 报告生成 | 已有数据，想生成最终报告页 |

## 新手建议

第一次用这套 skills，推荐直接走主 skill：

1. 只给一句话：`帮我调研美国市场的 kids supplements 选品机会`
2. 主 skill 会自动拆解关键词、采集数据、做分析
3. 最后你会拿到：
   - Excel 总表
   - HTML 可视化报告
   - 原始数据文件

如果你只想先验证某个平台，再回到主流程，也可以先单独跑对应子 skill。

## 配置提醒

- 不要把真实 `.env` 上传到 GitHub
- API Key、Token、飞书表格信息都要放在环境变量或本地 `.env.example` 中
- 公开仓库里只保留占位符，不保留个人路径和密码

主 skill 的详细使用说明见：[product-market-researcher/README.md](./product-market-researcher/README.md)
