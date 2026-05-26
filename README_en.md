# 🛒 Amazon Product Research Toolkit

> **AI-powered Amazon Product Research Automation Tool Chain** —— Input market + category, automatically complete full-chain data collection and analysis

[中文](README.md) | English

---

## ✨ Features

- **🚀 One-Click Start**: Just input "Market + Category", auto-complete the full process
- **📊 Multi-Source Data Collection**: Amazon + 1688 suppliers + TikTok + Google Trends + Market Reports
- **🧠 Intelligent Analysis**: Based on refined product selection methodology, automatically identify blue ocean markets
- **🏭 Supply Cost Calibration**: Use Apify-powered 1688 supplier data to validate unit cost, MOQ, and supply stability
- **💰 Profit Modeling**: Automatically calculate gross margin, net margin, cost structure, and sensitivity ranges from 1688 median supplier cost
- **📝 Professional Reports**: Generate complete product research analysis reports

---

## 🔄 Product Selection Methodology

This tool is based on **AI Era Cross-border E-commerce Refined Product Selection Methodology**:

```
Market Analysis → Demand Discovery → Competition Analysis → Profit Assessment
    → Content Distribution → Supply Chain → Small-scale Testing → Scale Up
```

### Selection Decision Criteria

| Metric | Standard | Description |
|--------|----------|-------------|
| Search Volume | 200K-1M/month | Sufficient demand without excessive competition |
| Brand Concentration | <30% | Scattered market, equal opportunities |
| CPC | <$1 | Controllable advertising costs |
| Profit Margin | >30% | Sustainable profitability |
| Supply Chain Stability | Rating >4.0 | Based on 1688 supplier count, MOQ, price dispersion, transaction volume, and repurchase signals |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone the project
git clone https://github.com/yourusername/amazon-product-researcher.git
cd amazon-product-researcher

# Install Python dependencies
pip install -r requirements.txt

# Configure API Key (see below)
cp .env.example .env
```

### 2. Configure API Key

Edit the `.env` file:

```bash
# Apify API (for data collection)
APIFY_API_TOKEN=your-apify-token-here

# 1688 supplier cost collection (recommended)
APIFY_1688_ACTOR_ID=your-1688-actor-id
SUPPLIER_COST_SOURCE=1688
SUPPLIER_KEYWORDS_MAX=8
SUPPLIER_RESULTS_PER_KEYWORD=20
RMB_USD_RATE=auto
```

### 3. Run Product Research

**Method 1: WorkBuddy Skill (Recommended)**

```
In WorkBuddy, input:
"Research kids supplement opportunities in US market"
```

**Method 2: Command Line**

```bash
cd skills/amazon-product-researcher/scripts
python main.py --market US --category "kids supplements"
```

---

## 📁 Project Structure

```
amazon-product-researcher/
├── README.md
├── README_en.md
├── .env.example
├── requirements.txt
├── LICENSE
├── docs/
│   ├── configuration.md
│   ├── methodology.md
│   ├── faq.md
│   └── changelog.md
├── skills/
│   ├── amazon-product-researcher/
│   ├── amazon-product-scraper/
│   ├── apify-amazon-scraper/
│   ├── apify-market-scraper/
│   ├── apify-tiktok-scraper/
│   ├── market-intelligence/
│   ├── profit-model-builder/
│   ├── report-generator/
│   └── tiktok-analytics/
├── examples/
│   ├── sample_report.md
│   └── sample_config.json
└── output/
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

<p align="center">
  <strong>Made with ❤️ for Amazon Sellers</strong>
</p>
