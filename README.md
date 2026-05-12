# 🛒 Amazon Product Research Toolkit

> **AI驱动的亚马逊精细化选品调研工具链** —— 输入市场+类目，自动完成全链路数据采集与分析

[English](README_en.md) | 中文

---

## ✨ 核心特性

- **🚀 一键启动**：只需输入「市场 + 类目」，自动完成全流程
- **📊 多源数据采集**：Amazon + TikTok + Google Trends + 市场报告
- **🧠 智能分析**：基于精细化选品方法论，自动识别蓝海市场
- **💰 利润建模**：自动计算毛利率、净利率、成本结构
- **📝 专业报告**：生成完整的选品调研分析报告

---

## 🔄 选品方法论

本工具基于 **AI时代跨境电商精细化选品方法论**：

```
拆市场 → 找需求 → 分析竞争 → 判断利润 → 内容传播 → 供应链 → 小量测试 → 放大优势
```

### 选品决策标准

| 指标 | 标准 | 说明 |
|------|------|------|
| 搜索量 | 2-10万/月 | 有需求但不过度竞争 |
| 品牌集中度 | <30% | 市场分散，机会均等 |
| CPC | <$1 | 广告成本可控 |
| 利润率 | >30% | 可持续盈利 |

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    amazon-product-researcher                      │
│                         (主入口 Skill)                            │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│   数据采集层      │  │   分析层          │  │   输出层        │
├───────────────────┤  ├───────────────────┤  ├─────────────────┤
│                  │  │                  │  │                 │
│ amazon-product-  │  │ profit-model-    │  │ report-         │
│ scraper          │  │ builder          │  │ generator       │
│ 亚马逊商品采集    │  │ 利润模型构建      │  │ 报告生成        │
│                  │  │                  │  │                 │
│ apify-amazon-    │  │ market-          │  │ tiktok-         │
│ scraper          │  │ intelligence     │  │ analytics       │
│ Apify API采集     │  │ 市场情报分析      │  │ TikTok流量分析  │
│                  │  │                  │  │                 │
│ apify-market-    │  │                  │  │                 │
│ scraper          │  │                  │  │                 │
│ 市场数据采集      │  │                  │  │                 │
│                  │  │                  │  │                 │
│ apify-tiktok-    │  │                  │  │                 │
│ scraper          │  │                  │  │                 │
│ TikTok数据采集    │  │                  │  │                 │
│                  │  │                  │  │                 │
└───────────────────┘  └──────────────────┘  └─────────────────┘
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/amazon-product-researcher.git
cd amazon-product-researcher

# 安装 Python 依赖
pip install -r requirements.txt

# 配置 API Key (见下方)
cp .env.example .env
```

### 2. 配置 API Key

编辑 `.env` 文件：

```bash
# Apify API (用于数据采集)
APIFY_API_TOKEN=your-apify-token-here

# 可选：其他 API 配置
GOOGLE_TRENDS_COUNTRY=US
```

> 📖 详细配置说明：[配置指南](docs/configuration.md)

### 3. 运行选品调研

**方式一：WorkBuddy Skill (推荐)**

```
在 WorkBuddy 中输入：
"帮我分析美国市场儿童保健品类目的选品机会"
```

**方式二：命令行直接运行**

```bash
cd skills/amazon-product-researcher/scripts
python main.py --market US --category "kids supplements" --keywords "children vitamins,gummy vitamins"
```

---

## 📁 项目结构

```
amazon-product-researcher/
├── README.md                    # 本文件
├── README_en.md                 # English version
├── .env.example                 # 环境变量模板
├── requirements.txt             # Python 依赖
├── LICENSE                      # MIT 许可证
│
├── docs/                        # 文档
│   ├── configuration.md          # 配置指南
│   ├── methodolody.md            # 选品方法论详解
│   ├── faq.md                   # 常见问题
│   └── changelog.md             # 更新日志
│
├── skills/                      # Skill 模块
│   ├── amazon-product-researcher/      # 主 Skill (入口)
│   ├── amazon-product-scraper/         # 亚马逊商品采集
│   ├── apify-amazon-scraper/          # Apify 亚马逊采集
│   ├── apify-market-scraper/          # 市场数据采集
│   ├── apify-tiktok-scraper/          # TikTok 数据采集
│   ├── market-intelligence/            # 市场情报分析
│   ├── profit-model-builder/           # 利润模型构建
│   ├── report-generator/               # 报告生成器
│   └── tiktok-analytics/              # TikTok 流量分析
│
├── examples/                    # 示例
│   ├── sample_report.md          # 报告示例
│   └── sample_config.json        # 配置示例
│
└── output/                      # 输出目录 (自动创建)
    └── YYYY-MM-DD/              # 按日期分组的报告
```

---

## 📊 数据源

| 数据源 | 类型 | 说明 |
|--------|------|------|
| Amazon | 商品数据 | BSR排名、评论、价格、评分 |
| TikTok | 流量数据 | 标签播放量、爆款视频、达人 |
| Google Trends | 趋势数据 | 搜索热度、季节性 |
| Grand View Research | 市场报告 | 市场规模、CAGR |
| Mordor Intelligence | 行业报告 | 行业趋势、竞争格局 |

---

## 🔧 高级配置

### 自定义采集参数

在 `skills/amazon-product-researcher/scripts/config.py` 中配置：

```python
# 采集参数
CONFIG = {
    "max_products": 100,           # 最大采集商品数
    "min_review_count": 50,        # 最小评论数
    "price_range": (10, 50),       # 价格区间 (USD)
    "min_rating": 4.0,             # 最低评分
    "proxy_enabled": False,        # 是否使用代理
}
```

### 输出格式

支持多种输出格式：

```python
OUTPUT_FORMAT = "markdown"  # markdown / pdf / word / html
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

详见：[贡献指南](CONTRIBUTING.md)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Apify](https://apify.com/) - 数据采集平台
- [Selenium](https://www.selenium.dev/) - 浏览器自动化
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - 网页解析
- 所有开源贡献者

---

## 📬 联系

- GitHub Issues: [报告 Bug / 请求功能](https://github.com/yourusername/amazon-product-researcher/issues)
- Email: your.email@example.com

---

<p align="center">
  <strong>Made with ❤️ for Amazon Sellers</strong>
</p>
