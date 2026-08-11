# Report Generator

选品调研报告生成器 —— 将采集和分析的数据自动生成完整报告。

---

## 功能说明

本 Skill 将 `amazon-product-researcher` 全流程采集和分析的数据，生成专业格式的选品调研报告。

### 支持格式

| 格式 | 依赖 | 用途 |
|------|------|------|
| **Markdown** | 无需额外依赖 | 推荐格式，易于分享 |
| **PDF** | `pandoc` | 正式报告，可打印 |
| **Word** | `python-docx` | 可编辑，便于协作 |
| **HTML** | 无需额外依赖 | 网页展示，交互性好 |

---

## 报告结构

生成的完整报告包含以下章节：

```
🛒 亚马逊选品调研报告
==================================

📋 执行摘要
├── 🎯 识别到的蓝海机会 (Top 3)
├── 💰 推荐定价方案
└── ✅ 综合推荐

📊 市场分析
├── 市场规模 (金额, CAGR)
├── 品牌集中度
└── 价格分布

🏆 竞争分析
├── 竞品定位
├── 评分分布
└── 差异化机会

📱 TikTok 传播验证
├── 病毒传播评分
├── 标签表现
└── 营销建议

💰 利润模型
├── 成本结构
├── 定价方案 (四档对比)
└── 盈亏平衡分析

✅ 选品建议
├── 综合推荐
└── ⚠️ 风险提示
```

---

## 使用方法

### 方式一：通过主 Skill 调用

```
"帮我生成美国市场儿童保健品的选品调研报告"
```

主 Skill 会自动调用本 Skill 生成报告。

### 方式二：命令行

```bash
cd skills/report-generator/scripts
python report_generator.py --input ./data/processed.json --format markdown
python report_generator.py --input ./data/processed.json --format word
```

---

## 脚本示例

### report_generator.py

```python
#!/usr/bin/env python3
"""
Report Generator - 报告生成器
使用方法: python report_generator.py --input data.json --format markdown
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

def load_data(input_file):
    """加载分析数据"""
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_markdown(data, output_file):
    """生成 Markdown 报告"""
    lines = []

    # 标题
    lines.append(f"# 🛒 亚马逊选品调研报告")
    lines.append("")
    lines.append(f"**市场:** {data.get('market', 'N/A')} | **类目:** {data.get('category', 'N/A')}")
    lines.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 执行摘要
    lines.extend(generate_executive_summary(data))

    # 市场分析
    lines.extend(generate_market_section(data))

    # 利润模型
    lines.extend(generate_profit_section(data))

    # 选品建议
    lines.extend(generate_recommendations(data))

    # 保存
    content = "\n".join(lines)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_file

def generate_executive_summary(data):
    """生成执行摘要"""
    lines = []
    lines.append("## 📋 执行摘要")
    lines.append("")

    analysis = data.get("analysis", {})
    market = analysis.get("market", {})
    profit = analysis.get("profit", {})

    # 蓝海机会
    blue_ocean = market.get("blue_ocean_opportunities", [])
    if blue_ocean:
        lines.append("### 🎯 识别到的蓝海机会")
        lines.append("")
        for i, opp in enumerate(blue_ocean[:3], 1):
            lines.append(f"{i}. **{opp.get('title', 'Unknown')}**")
            lines.append(f"   - {opp.get('description', '')}")
            lines.append(f"   - 评分: {opp.get('score', 0)}/100")
            lines.append("")

    # 推荐定价
    if profit:
        recommended = profit.get("recommended_tier", {})
        if recommended:
            lines.append("### 💰 推荐定价方案")
            lines.append("")
            lines.append(f"| 产品定位 | 售价 | 利润 | 利润率 |")
            lines.append(f"|----------|------|------|--------|")
            lines.append(f"| {recommended.get('name', 'N/A')} | ${recommended.get('price', 0):.2f} | ${recommended.get('profit', 0):.2f} | {recommended.get('margin', 0)*100:.1f}% |")
            lines.append("")

    lines.append("---")
    lines.append("")

    return lines

def generate_market_section(data):
    """生成市场分析章节"""
    lines = []
    lines.append("## 📊 市场分析")
    lines.append("")

    analysis = data.get("analysis", {})
    market = analysis.get("market", {})
    market_size = market.get("market_size", {})

    lines.append(f"### 市场规模")
    lines.append("")
    lines.append(f"- **市场规模:** {market_size.get('estimated_size', 'N/A')}")
    lines.append(f"- **年增长率 (CAGR):** {market_size.get('cagr', 0)*100:.1f}%")
    lines.append(f"- **商品总数:** {market_size.get('total_products', 0)}")
    lines.append("")

    lines.append("---")
    lines.append("")

    return lines

def generate_profit_section(data):
    """生成利润模型章节"""
    lines = []
    lines.append("## 💰 利润模型")
    lines.append("")

    analysis = data.get("analysis", {})
    profit = analysis.get("profit", {})
    tiers = profit.get("pricing_tiers", [])

    if tiers:
        lines.append("### 定价方案")
        lines.append("")
        lines.append("| 产品定位 | 售价 | 成本 | 利润 | 毛利率 | 净利率 |")
        lines.append("|----------|------|------|------|--------|----------|")
        for tier in tiers:
            lines.append(
                f"| {tier.get('name', 'N/A')} "
                f"| ${tier.get('price', 0):.2f} "
                f"| ${tier.get('cost', 0):.2f} "
                f"| ${tier.get('profit', 0):.2f} "
                f"| {(1 - tier.get('cost', 0)/tier.get('price', 1))*100:.1f}% "
                f"| {tier.get('margin', 0)*100:.1f}% |"
            )
        lines.append("")

    lines.append("---")
    lines.append("")

    return lines

def generate_recommendations(data):
    """生成选品建议"""
    lines = []
    lines.append("## ✅ 选品建议")
    lines.append("")

    analysis = data.get("analysis", {})
    market = analysis.get("market", {})
    blue_ocean = market.get("blue_ocean_opportunities", [])

    lines.append("### 综合推荐")
    lines.append("")

    if blue_ocean:
        for i, opp in enumerate(blue_ocean[:3], 1):
            lines.append(f"{i}. **{opp.get('title', 'Unknown')}**")
            lines.append("")
            lines.append(f"   **描述:** {opp.get('description', '')}")
            lines.append("")
            lines.append(f"   **评分:** {opp.get('score', 0)}/100")
            lines.append("")
    else:
        lines.append("基于当前数据分析，建议关注以下方向：")
        lines.append("")
        lines.append("1. **细分市场差异化** - 寻找头部品牌的弱点切入")
        lines.append("2. **内容营销驱动** - 利用 TikTok 等社交媒体建立品牌")
        lines.append("3. **品质驱动定价** - 不要陷入价格战，注重产品品质")
        lines.append("")

    # 风险提示
    lines.append("### ⚠️ 风险提示")
    lines.append("")
    lines.append("- 市场变化快，需持续关注竞品动态")
    lines.append("- 供应链稳定性至关重要，建议多供应商备选")
    lines.append("- 合规性检查，确保产品符合目标市场法规")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*本报告由 Amazon Product Research Toolkit 自动生成*")

    return lines

def main():
    parser = argparse.ArgumentParser(description="选品调研报告生成器")
    parser.add_argument("--input", "-i", required=True, help="输入数据文件 (JSON)")
    parser.add_argument("--output", "-o", help="输出文件路径 (可选)")
    parser.add_argument("--format", "-f", default="markdown", choices=["markdown", "pdf", "word", "html"], help="输出格式")
    args = parser.parse_args()

    # 加载数据
    data = load_data(args.input)

    # 生成输出文件名
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        category = data.get("category", "report").replace(" ", "_")
        output_file = f"{timestamp}_{category}_report.{args.format}"

    # 生成报告
    if args.format == "markdown":
        generate_markdown(data, output_file)
    else:
        print(f"⚠️  格式 {args.format} 暂未实现，使用 markdown")
        generate_markdown(data, output_file.replace(args.format, "md"))

    print(f"\n✅ 报告已生成: {output_file}")

if __name__ == "__main__":
    main()
```

---

## 配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `OUTPUT_FORMAT` | markdown | 输出格式 |
| `INCLUDE_CHARTS` | True | 是否包含图表 |
| `INCLUDE_DATA_TABLES` | True | 是否包含数据表格 |
| `LANGUAGE` | zh-CN | 报告语言 |

---

## 注意事项

1. **数据新鲜度**: 报告数据应定期更新，建议每周重新生成
2. **格式选择**: Markdown 最通用，Word 便于协作，PDF 适合正式提交
3. **定制化**: 可修改报告模板，增删章节
4. **自动化**: 可与主 Skill 结合，实现一键生成

---

## 下一步

- [返回主 README](../README.md)
- [配置指南](../docs/configuration.md)
