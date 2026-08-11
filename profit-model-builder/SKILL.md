---
name: profit-model-builder
description: |
  利润模型构建和成本分析技能。当用户需要以下任务时应使用此技能：
  - 计算亚马逊/TikTok产品的毛利率和净利率
  - 构建完整成本结构模型
  - 进行多方案利润对比分析
  - 制定定价策略和利润优化方案
triggers:
  - 利润模型
  - 成本结构
  - 毛利率计算
  - 净利率
  - 定价策略
  - profit margin
  - cost analysis
agent_created: true
---

# Profit Model Builder v1.0

## 功能说明

本技能用于构建亚马逊/TikTok渠道的完整利润模型，包括成本结构、毛利率、净利率计算，为选品决策提供财务数据支撑。

## 数据准入规则

当本技能被 `amazon-product-researcher` 调用时，利润模型只能使用以下输入：

1. 1688、供应商报价单或其他可追溯来源采集到的采购价、MOQ、包材和生产成本。
2. Amazon/TikTok 官方费率、FBA/物流费率表、或用户提供的已确认费率。
3. Amazon 商品采集得到的竞品售价、规格、评论数、销量/BSR 等可验证数据。
4. 用户明确给出的假设参数。

缺少来源的成本项不得进入最终报告的 KPI、图表和结论。必须估算时，只能在内部模型中作为敏感性分析假设，并标明为“用户假设/模型假设”；如果最终报告没有展示假设说明的上下文，则该估算项不展示。

## 输出给报告的来源字段

每个利润模型结果建议同时输出：

```json
{
  "metric": "毛利率",
  "value": "36.8%",
  "inputs": ["1688供应商报价", "Amazon竞品售价", "FBA费率表"],
  "lineage": {
    "collector": "1688 Apify Actor + amazon-product-scraper",
    "collected_at": "YYYY-MM-DD HH:mm:ss",
    "sample_size": 25,
    "urls": ["https://..."]
  }
}
```

## 成本结构分解

### 固定成本项

| 成本项 | 说明 | 估算值（60粒软糖） |
|--------|------|-------------------|
| **原料成本** | 活性成分+辅料 | $1.8-4.2/瓶 |
| **包材成本** | 瓶/盖/标签/纸盒 | $1.2/瓶 |
| **生产费用** | cGMP工厂加工 | $1.5/瓶 |
| **检测费用** | 重金属/微生物/含量 | $0.5/瓶 |
| **物流成本** | 头程+尾程 | $2.5/瓶 |

### 变动成本项

| 成本项 | 说明 | 估算占比 |
|--------|------|----------|
| **TikTok营销** | 达人+广告 | 18-25% |
| **平台佣金** | TikTok/Amazon | 8-15% |
| **退款率** | 行业平均3-5% | 3-5% |
| **汇损** | 跨境收款 | 1-2% |

## 利润计算公式

### 毛利润
```
毛利 = 售价 - 产品成本（原料+包材+生产+检测+物流）
毛利率 = (毛利 / 售价) × 100%
```

### 净利润
```
净利 = 毛利 - 营销费用 - 平台佣金 - 退款 - 汇损
净利率 = (净利 / 售价) × 100%
```

### 全域利润
```
全域净利 = (线上净利 × 线上占比) + (线下净利 × 线下占比)
```

## 使用方式

### 基础计算

```python
class ProfitModel:
    def __init__(self, product_type="standard"):
        # 默认成本结构（60粒软糖）
        self.costs = {
            "原料成本": 2.0,      # 美元/瓶
            "包材成本": 1.2,      # 美元/瓶
            "生产费用": 1.5,      # 美元/瓶
            "检测费用": 0.5,      # 美元/瓶
            "物流成本": 2.5,      # 美元/瓶
        }

    def calculate_total_cost(self):
        """计算产品总成本"""
        return sum(self.costs.values())

    def calculate_profit(self, selling_price, marketing_rate=0.20,
                         platform_fee=0.08, refund_rate=0.03):
        """计算利润模型"""
        total_cost = self.calculate_total_cost()
        gross_profit = selling_price - total_cost
        gross_margin = (gross_profit / selling_price) * 100

        # 变动成本
        marketing_cost = selling_price * marketing_rate
        platform_cost = selling_price * platform_fee
        refund_cost = selling_price * refund_rate

        net_profit = gross_profit - marketing_cost - platform_cost - refund_cost
        net_margin = (net_profit / selling_price) * 100

        return {
            "售价": selling_price,
            "总成本": total_cost,
            "毛利": gross_profit,
            "毛利率": round(gross_margin, 1),
            "营销费用": marketing_cost,
            "平台佣金": platform_cost,
            "退款": refund_cost,
            "净利": net_profit,
            "净利率": round(net_margin, 1)
        }

# 使用示例
model = ProfitModel()
result = model.calculate_profit(
    selling_price=24.99,
    marketing_rate=0.22,
    platform_fee=0.08,
    refund_rate=0.03
)
```

### 多产品线对比

```python
def compare_product_lines():
    """对比多条产品线的利润"""

    products = [
        {
            "name": "引流款-儿童多维软糖",
            "selling_price": 14.99,
            "原料成本": 1.8,
            "营销占比": 0.18,
            "毛利目标": 50
        },
        {
            "name": "主打款-姜黄多维复合",
            "selling_price": 24.99,
            "原料成本": 2.6,
            "营销占比": 0.22,
            "毛利目标": 65
        },
        {
            "name": "利润款-虾青素护眼",
            "selling_price": 34.99,
            "原料成本": 4.2,
            "营销占比": 0.25,
            "毛利目标": 70
        },
        {
            "name": "配套款-儿童植物蛋白",
            "selling_price": 19.99,
            "原料成本": 2.1,
            "营销占比": 0.20,
            "毛利目标": 55
        }
    ]

    results = []
    for p in products:
        model = ProfitModel()
        # 覆盖默认原料成本
        model.costs["原料成本"] = p["原料成本"]

        profit = model.calculate_profit(
            selling_price=p["selling_price"],
            marketing_rate=p["营销占比"]
        )

        results.append({
            "产品": p["name"],
            **profit
        })

    return results
```

## 预设产品模板

### 儿童保健品类目

| 产品类型 | 售价 | 原料成本 | 毛利 | 净利（TikTok） |
|----------|------|----------|------|----------------|
| **引流款** 多维软糖 | $14.99 | $1.8 | 49.9% | 31.9% |
| **主打款** 姜黄复合 | $24.99 | $2.6 | 68% | 46% |
| **利润款** 虾青素护眼 | $34.99 | $4.2 | 70.3% | 45.3% |
| **配套款** 植物蛋白 | $19.99 | $2.1 | 61% | 41% |

### 成本细分模板

```yaml
# 引流款-儿童多维软糖 60粒
成本结构:
  原料:
    - 复合维生素预混料: $1.20
    - 软糖基底(明胶/果胶): $0.35
    - 天然色素/香精: $0.15
    - 小计: $1.70
  包材:
    - 瓶身(儿童安全): $0.60
    - 瓶盖(防误食): $0.25
    - 标签(FDA合规): $0.20
    - 纸盒包装: $0.15
    - 小计: $1.20
  生产: $1.50
  检测: $0.50
  物流(头程+尾程): $2.50
  总成本: $7.40

# 主打款-姜黄多维复合 60粒
成本结构:
  原料:
    - 姜黄提取物(95%): $0.80
    - 黑胡椒提取物: $0.15
    - 复合维生素: $1.20
    - 软糖基底: $0.35
    - 小计: $2.50
  包材: $1.20
  生产: $1.50
  检测: $0.50
  物流: $2.50
  总成本: $8.20
```

## 全域利润模型

```python
def calculate_omni_profit():
    """计算线上+线下全域利润"""

    # TikTok线上（60%）
    tiktok_net_margin = 42  # 净利率42-46%
    tiktok_revenue_ratio = 0.60

    # 线下渠道（40%）
    offline_net_margin = 37  # 净利率35-40%（含渠道佣金15%）
    offline_revenue_ratio = 0.40

    # 全域综合净利率
    omni_net_margin = (tiktok_net_margin * tiktok_revenue_ratio +
                       offline_net_margin * offline_revenue_ratio)

    return {
        "TikTok线上占比": "60%",
        "TikTok净利率": "42-46%",
        "线下渠道占比": "40%",
        "线下净利率": "35-40%",
        "全域综合净利率": f"{omni_net_margin:.1f}%+",
        "行业平均净利率": "12-15%",
        "优势倍数": f"{omni_net_margin / 13.5:.1f}x"
    }
```

## 定价策略

### 价格带分析

| 产品类型 | 竞品价格 | 自研定价 | 策略 |
|----------|----------|----------|------|
| 引流款 | $19.99-24.99 | $14.99 | 低价获客，比竞品低20% |
| 主打款 | $21.99 | $24.99 | 品质对标中高价位 |
| 利润款 | $39.99 | $34.99 | 高端溢价，技术壁垒 |
| 套装 | - | $59.99 | 客单提升40%+ |

### 定价公式
```
最优售价 = (竞品最低价 + 竞品最高价) / 2 × 品质系数

示例：
- 姜黄软糖竞品：$16.25-$21.99
- 品质系数：1.1（有机+无敏+复合配方）
- 最优售价：(16.25 + 21.99) / 2 × 1.1 = $21.03 → 定价 $22.99
```

## 输出格式

```json
{
  "产品名称": "姜黄多维免疫复合软糖",
  "成本结构": {
    "原料成本": 2.60,
    "包材成本": 1.20,
    "生产费用": 1.50,
    "检测费用": 0.50,
    "物流成本": 2.50,
    "总成本": 8.30
  },
  "利润模型": {
    "售价": 24.99,
    "毛利": 16.69,
    "毛利率": 66.8,
    "营销费用(22%)": 5.50,
    "平台佣金(8%)": 2.00,
    "净利": 9.19,
    "净利率": 36.8
  },
  "竞品对比": {
    "竞品价格": 21.99,
    "自研定价": 24.99,
    "溢价": 13.6
  }
}
```

## 注意事项

1. 成本为估算值，需结合实际供应商报价
2. 营销费用因渠道和策略差异较大
3. 退款率需根据品类历史数据调整
4. 利润模型应每月更新一次
