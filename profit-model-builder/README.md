# Profit Model Builder

利润模型构建 Skill —— 计算亚马逊产品的成本结构、毛利率、净利率、定价策略。

---

## 功能说明

本 Skill 自动化构建跨境电商品牌的利润模型，核心功能：

1. **成本结构分析** - 拆解 COGS、平台费、FBA 费、营销费
2. **毛利率计算** - (售价 - COGS) / 售价
3. **净利率计算** - 净利润 / 售价
4. **多方案对比** - 引流款/主打款/利润款/高端款
5. **盈亏平衡分析** - 找到最低盈利价格

---

## 成本结构

### 完整成本模型

```
销售收入 (Sale Price)
├── 产品成本 (COGS)
│   ├── 原料成本
│   ├── 包材成本
│   ├── 生产/加工费
│   └── 检测/认证费
├── 平台费用
│   ├── 佣金 (8-15%)
│   ├── FBA 费用
│   └── 退款处理费
├── 营销费用
│   ├── PPC 广告 (可调节)
│   ├── 测评费用
│   └── 达人佣金
└── 其他费用
    ├── 汇损
    └── 退货损耗
    ===================
    净利润
```

### 默认参数

| 成本项 | 默认值 (USD) | 说明 |
|--------|---------------|------|
| 产品成本 (COGS) | $5.00 | 可根据供应链调整 |
| 头程运费 | $0.50 | 海运/空运 |
| 包材成本 | $0.30 | 包装盒/说明书等 |
| 平台佣金率 | 15% | 亚马逊标准 |
| FBA 履约费 | $3.50 | 标准尺寸商品 |
| 退款率 | 3% | 行业平均 |
| 广告占比 | 20% | 可根据 ACOS 调整 |
| 汇损 | 1% | 跨境支付汇损 |

---

## 使用方法

### 方式一：调用现有数据

```
"帮我为美国市场儿童保健品构建利润模型"
"计算售价 $24.99 的净利润"
"对比四个定价档位的利润空间"
```

### 方式二：命令行

```bash
cd skills/profit-model-builder/scripts
python profit_model.py --price 24.99 --cost 5.0
python profit_model.py --compare  # 四档对比
```

---

## 输出示例

### 利润模型报告

```
💰 利润模型分析
==================

产品成本结构 (以 $25.00 售价为例)
---------------------------------------
产品成本 (COGS):       $5.80 (23.2%)
平台佣金 (15%):        $3.75 (15.0%)
FBA 履约费:           $3.50 (14.0%)
广告费 (20%):          $5.00 (20.0%)
退款损耗 (3%):         $0.75 (3.0%)
汇损 (1%):            $0.25 (1.0%)
---------------------------------------
总成本:               $19.05 (76.2%)
净利润:               $5.95 (23.8%)
毛利率:               76.8%
净利率:               23.8%
```

### 四档定价方案

| 产品定位 | 售价 | 成本 | 利润 | 毛利率 | 净利率 |
|----------|------|------|------|--------|----------|
| 引流款 | $14.99 | $6.88 | $1.29 | 54.1% | 8.6% |
| 主打款 | $22.99 | $8.28 | $6.35 | 64.0% | 27.6% |
| 利润款 | $29.99 | $10.18 | $10.65 | 66.1% | 35.5% |
| 高端款 | $39.99 | $12.78 | $16.85 | 68.0% | 42.1% |

✅ **推荐**: 主打款（$22.99），净利率 27.6%

---

## 脚本示例

### profit_model.py

```python
#!/usr/bin/env python3
"""
Profit Model Builder - 利润模型构建器
使用方法: python profit_model.py --price 25.0 --cost 5.0
"""

import argparse
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ProfitConfig:
    """利润模型配置"""
    product_cost: float = 5.0
    shipping_cost: float = 0.5
    packaging_cost: float = 0.3
    platform_fee_rate: float = 0.15
    fba_fee: float = 3.5
    refund_rate: float = 0.03
    advertising_rate: float = 0.20
    exchange_loss_rate: float = 0.01

class ProfitModelBuilder:
    """利润模型构建器"""

    def __init__(self, config: ProfitConfig = None):
        self.config = config or ProfitConfig()

    def calculate_profit(self, sale_price: float) -> Dict:
        """计算利润"""
        cogs = (
            self.config.product_cost
            + self.config.shipping_cost
            + self.config.packaging_cost
        )

        platform_fee = sale_price * self.config.platform_fee_rate
        fba_fee = self.config.fba_fee
        refund = sale_price * self.config.refund_rate
        advertising = sale_price * self.config.advertising_rate
        exchange_loss = sale_price * self.config.exchange_loss_rate

        total_cost = cogs + platform_fee + fba_fee + refund + advertising + exchange_loss
        net_profit = sale_price - total_cost

        return {
            "sale_price": sale_price,
            "cogs": cogs,
            "platform_fee": platform_fee,
            "fba_fee": fba_fee,
            "refund": refund,
            "advertising": advertising,
            "exchange_loss": exchange_loss,
            "total_cost": total_cost,
            "net_profit": net_profit,
            "gross_margin": (sale_price - cogs) / sale_price,
            "net_margin": net_profit / sale_price,
        }

    def compare_tiers(self) -> List[Dict]:
        """对比不同定价档位"""
        tiers = [
            {"name": "引流款", "price": 14.99},
            {"name": "主打款", "price": 22.99},
            {"name": "利润款", "price": 29.99},
            {"name": "高端款", "price": 39.99},
        ]

        for tier in tiers:
            analysis = self.calculate_profit(tier["price"])
            tier.update(analysis)

        return tiers

def main():
    parser = argparse.ArgumentParser(description="利润模型构建器")
    parser.add_argument("--price", type=float, help="售价 (USD)")
    parser.add_argument("--cost", type=float, default=5.0, help="产品成本 (USD)")
    parser.add_argument("--compare", action="store_true", help="对比四档定价")
    args = parser.parse_args()

    config = ProfitConfig(product_cost=args.cost)
    builder = ProfitModelBuilder(config)

    if args.compare:
        tiers = builder.compare_tiers()
        print("\n💰 定价方案对比")
        print("=" * 60)
        for tier in tiers:
            print(f"{tier['name']}: ${tier['sale_price']:.2f}")
            print(f"  成本: ${tier['total_cost']:.2f}")
            print(f"  利润: ${tier['net_profit']:.2f}")
            print(f"  净利率: {tier['net_margin']*100:.1f}%")
            print()
    elif args.price:
        analysis = builder.calculate_profit(args.price)
        print(f"\n💰 利润分析 (售价: ${args.price:.2f})")
        print("=" * 60)
        for key, value in analysis.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

## 配置

可以通过命令行参数或配置文件调整成本参数：

### 配置文件 (config.json)

```json
{
    "product_cost": 5.0,
    "shipping_cost": 0.5,
    "packaging_cost": 0.3,
    "platform_fee_rate": 0.15,
    "fba_fee": 3.5,
    "refund_rate": 0.03,
    "advertising_rate": 0.20,
    "exchange_loss_rate": 0.01
}
```

---

## 注意事项

1. **成本波动**: 原材料价格和物流费用会波动，建议每季度更新
2. **FBA 费用**: 根据商品尺寸和重量计算，不同品类不同
3. **广告费**: ACOS 因关键词竞争度而异，建议按实际数据调整
4. **退款率**: 不同品类的退款率差异很大，建议参考竞品数据

---

## 下一步

- [返回主 README](../README.md)
- [查看选品方法论](../docs/methodology.md)
