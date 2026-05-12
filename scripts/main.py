"""
Amazon Product Research Toolkit - Main Entry Script
=====================================================

使用方法:
    python main.py --market US --category "kids supplements"
    python main.py --market UK --category "probiotics" --keywords "digestive health"
    python main.py --config config.json

环境变量:
    必需: APIFY_API_TOKEN
    可选: DEFAULT_MARKET, OUTPUT_FORMAT, MAX_PRODUCTS 等
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG
from input_parser import parse_input
from data_collector import DataCollector
from analyzer import MarketAnalyzer, TikTokAnalyzer, ProfitModelBuilder
from report_generator import ReportGenerator


class ProductResearchPipeline:
    """选品调研全流程管道"""

    def __init__(self, market: str, category: str, keywords: list = None, **kwargs):
        self.market = market.upper()
        self.category = category
        self.keywords = keywords or [category]
        self.config = CONFIG.copy()
        self.config.update(kwargs)

        # 初始化输出目录
        self.output_dir = Path(self.config.get("output_dir", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化数据存储
        self.data = {
            "metadata": {
                "market": self.market,
                "category": self.category,
                "keywords": self.keywords,
                "generated_at": datetime.now().isoformat(),
            },
            "amazon": [],
            "tiktok": [],
            "market": {},
            "analysis": {},
        }

    def run(self) -> dict:
        """执行完整的选品调研流程"""
        print(f"\n{'='*60}")
        print(f"🛒 Amazon Product Research Pipeline")
        print(f"{'='*60}")
        print(f"市场: {self.market} | 类目: {self.category}")
        print(f"关键词: {', '.join(self.keywords)}")
        print(f"{'='*60}\n")

        # Step 1: 数据采集
        self._collect_data()

        # Step 2: 数据分析
        self._analyze_data()

        # Step 3: 生成报告
        report_path = self._generate_report()

        print(f"\n{'='*60}")
        print(f"✅ 选品调研完成!")
        print(f"📁 报告位置: {report_path}")
        print(f"{'='*60}\n")

        return self.data

    def _collect_data(self):
        """采集数据"""
        print("\n📊 Step 1: 数据采集中...")

        collector = DataCollector(self.market, self.config)

        # 采集 Amazon 数据
        print("   ├─ 采集 Amazon 商品数据...")
        self.data["amazon"] = collector.fetch_amazon_products(self.keywords)

        # 采集 TikTok 数据
        print("   ├─ 采集 TikTok 流量数据...")
        self.data["tiktok"] = collector.fetch_tiktok_data(self.keywords)

        # 采集市场数据
        print("   └─ 采集市场数据...")
        self.data["market"] = collector.fetch_market_data(self.category)

        print(f"   ✅ 采集完成: {len(self.data['amazon'])} 个商品, "
              f"{len(self.data['tiktok'])} 条 TikTok 数据")

    def _analyze_data(self):
        """分析数据"""
        print("\n🧠 Step 2: 数据分析中...")

        # 市场分析
        print("   ├─ 分析市场机会...")
        market_analyzer = MarketAnalyzer(self.data)
        self.data["analysis"]["market"] = market_analyzer.analyze()

        # TikTok 分析
        print("   ├─ 分析 TikTok 传播潜力...")
        tiktok_analyzer = TikTokAnalyzer(self.data)
        self.data["analysis"]["tiktok"] = tiktok_analyzer.analyze()

        # 利润建模
        print("   └─ 构建利润模型...")
        profit_builder = ProfitModelBuilder(self.data)
        self.data["analysis"]["profit"] = profit_builder.build()

        print("   ✅ 分析完成")

    def _generate_report(self) -> Path:
        """生成报告"""
        print("\n📝 Step 3: 生成报告中...")

        generator = ReportGenerator(self.data, self.output_dir)
        report_path = generator.generate(format=self.config.get("output_format", "markdown"))

        return report_path


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="Amazon Product Research Toolkit - 选品调研自动化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --market US --category "kids supplements"
  python main.py --market UK --category "probiotics" --keywords "digestive health, gut health"
  python main.py --config config.json --output-format pdf

环境变量:
  APIFY_API_TOKEN    - Apify API Token (必需)
  DEFAULT_MARKET     - 默认市场 (默认: US)
  OUTPUT_FORMAT      - 输出格式 (默认: markdown)
  MAX_PRODUCTS       - 最大采集数量 (默认: 100)
        """
    )

    # 主要参数
    parser.add_argument("--market", "-m", default=os.getenv("DEFAULT_MARKET", "US"),
                        help="市场代码 (US/UK/DE/FR/IT/ES/JP/CA/AU), 默认: US")
    parser.add_argument("--category", "-c", required=True,
                        help="产品类目")
    parser.add_argument("--keywords", "-k", nargs="+",
                        help="关键词列表 (可选, 默认使用类目作为关键词)")

    # 配置选项
    parser.add_argument("--config", type=Path,
                        help="配置文件路径 (JSON)")
    parser.add_argument("--output-format", "-f", default="markdown",
                        choices=["markdown", "pdf", "word", "html"],
                        help="报告输出格式")
    parser.add_argument("--output-dir", "-o", type=Path,
                        help="输出目录")
    parser.add_argument("--max-products", type=int,
                        default=int(os.getenv("MAX_PRODUCTS", "100")),
                        help="最大采集商品数")

    # 调试选项
    parser.add_argument("--debug", action="store_true",
                        help="启用调试模式")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅解析输入,不执行采集")

    args = parser.parse_args()

    # 加载配置文件
    config = CONFIG.copy()
    if args.config and args.config.exists():
        with open(args.config) as f:
            config.update(json.load(f))

    # 覆盖配置
    config["output_format"] = args.output_format
    if args.output_dir:
        config["output_dir"] = str(args.output_dir)
    config["max_products"] = args.max_products
    config["debug"] = args.debug

    # 检查 API Token
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        print("\n⚠️  警告: APIFY_API_TOKEN 未设置")
        print("   部分功能可能无法使用")
        print("   请设置环境变量或创建 .env 文件\n")

    # 解析用户输入
    parsed_input = parse_input(args.market, args.category, args.keywords)

    if args.debug:
        print(f"\n📋 解析结果: {json.dumps(parsed_input, indent=2, ensure_ascii=False)}")

    if args.dry_run:
        print("\n✅ Dry run 完成")
        return

    # 运行调研管道
    try:
        pipeline = ProductResearchPipeline(
            market=parsed_input["market"],
            category=parsed_input["category"],
            keywords=parsed_input["keywords"],
            **config
        )
        pipeline.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
