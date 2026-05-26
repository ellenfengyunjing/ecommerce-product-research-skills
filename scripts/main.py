"""
Amazon Product Research Toolkit v3.0 - Main Entry Script
========================================================

使用方法:
    python main.py --market US --category "kids supplements"
    python main.py --market UK --category "probiotics" --keywords "digestive health"
    python main.py --config config.json --output-format html

v3.0 核心原则:
    - 所有数据必须真实准确，采集失败则不显示，绝不捏造
    - 每个章节底部标注数据来源 (Data Lineage)
    - 强制输出"为什么不选"反对意见 (至少3条)

环境变量:
    必需: APIFY_API_TOKEN
    可选: DEFAULT_MARKET, OUTPUT_FORMAT, MAX_PRODUCTS 等
"""

import sys

# Fix Windows GBK encoding for emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
from html_report_generator import HTMLReportGenerator


class ProductResearchPipeline:
    """选品调研全流程管道 v3.0"""

    def __init__(self, market: str, category: str, keywords: list = None, **kwargs):
        self.market = market.upper()
        self.category = category
        self.keywords = keywords or [category]
        self.config = CONFIG.copy()
        self.config.update(kwargs)

        # 初始化输出目录
        self.output_dir = Path(self.config.get("output_dir", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化数据存储 (v3.0: 增加数据溯源字段)
        gen_time = datetime.now().isoformat()
        self.data = {
            "metadata": {
                "market": self.market,
                "category": self.category,
                "keywords": self.keywords,
                "generated_at": gen_time,
                "version": "3.0",
                "data_lineage": {},  # v3.0: 全局数据溯源记录
            },
            "amazon": [],
            "tiktok": [],
            "review_analysis": {},
            "reddit": {},
            "google_trends": {},
            "supplier": {},
            "market": {},
            "analysis": {},
        }

    def run(self, output_format: str = "html") -> dict:
        """执行完整的选品调研流程 (v3.0)"""
        print(f"\n{'='*60}")
        print(f"🛒 Amazon Product Research Pipeline v3.0")
        print(f"{'='*60}")
        print(f"市场: {self.market} | 类目: {self.category}")
        print(f"关键词: {', '.join(self.keywords)}")
        print(f"输出格式: {output_format}")
        print(f"数据原则: 真实数据，不捏造，不mock")
        print(f"{'='*60}\n")

        # Step 1: 全量数据采集 (7大数据源)
        self._collect_all_data()

        # Step 2: 数据分析
        self._analyze_data()

        # Step 3: 生成报告 (含数据溯源)
        report_path = self._generate_report(output_format)

        print(f"\n{'='*60}")
        print(f"✅ 选品调研完成!")
        print(f"📁 报告位置: {report_path}")
        print(f"📊 数据溯源记录: {len(self.data['metadata']['data_lineage'])} 个数据源")
        print(f"{'='*60}\n")

        return self.data

    def _collect_all_data(self):
        """全量数据采集 (v3.1: Apify真实数据 + Web Search补充)"""
        print("\n📊 Step 1: 全量数据采集 (7大数据源)...")

        collector = DataCollector(self.market, self.config)
        collector.metadata = self.data["metadata"]
        lineage = self.data["metadata"]["data_lineage"]
        collect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Amazon 商品数据 (Apify: junglee/free-amazon-product-scraper)
        print("   ├─ [1/7] 采集 Amazon 商品数据...")
        self.data["amazon"] = collector.fetch_amazon_products(self.keywords)
        count = len(self.data["amazon"])
        lineage["amazon_products"] = {
            "source": "Apify Amazon Product Scraper (junglee/free-amazon-product-scraper)",
            "count": count,
            "time": collect_time,
            "status": "success" if count > 0 else "no_data (由 Web Search 补充)",
        }
        print(f"   │   └─ {count} 个商品" if count > 0 else "   │   └─ 由 Web Search 补充")

        # 2. Amazon 差评数据 (Apify: junglee/amazon-reviews-scraper)
        print("   ├─ [2/7] 采集竞品差评数据...")
        asins = [p.get("asin") for p in self.data["amazon"] if p.get("asin")][:20]
        self.data["review_analysis"] = collector.fetch_negative_reviews(asins)
        review_count = self.data["review_analysis"].get("total_reviews", 0)
        lineage["amazon_reviews"] = {
            "source": "Apify Amazon Review Scraper (junglee/amazon-reviews-scraper)",
            "count": review_count,
            "asins": len(asins),
            "time": collect_time,
            "status": "success" if review_count > 0 else "no_data",
        }
        print(f"   │   └─ {review_count} 条差评" if review_count > 0 else "   │   └─ 无差评数据")

        # 3. TikTok 数据 (Apify: clockworks/tiktok-scraper)
        print("   ├─ [3/7] 采集 TikTok 流量数据...")
        self.data["tiktok"] = collector.fetch_tiktok_data(self.keywords)
        tiktok_count = len(self.data["tiktok"])
        lineage["tiktok"] = {
            "source": "Apify TikTok Scraper (clockworks/tiktok-scraper)",
            "count": tiktok_count,
            "time": collect_time,
            "status": "success" if tiktok_count > 0 else "no_data (由 Web Search 补充)",
        }
        print(f"   │   └─ {tiktok_count} 个标签" if tiktok_count > 0 else "   │   └─ 由 Web Search 补充")

        # 4. Reddit 数据 (Apify: 无免费Actor → Web Search)
        print("   ├─ [4/7] 采集 Reddit 用户讨论...")
        self.data["reddit"] = collector.fetch_reddit_data(self.keywords)
        reddit_count = self.data["reddit"].get("total_posts", 0)
        source_note = "Apify" if self.data["reddit"].get("_source") != "unavailable" else "Web Search"
        lineage["reddit"] = {
            "source": f"Reddit User Discussion ({source_note})",
            "count": reddit_count,
            "time": collect_time,
            "status": "success" if reddit_count > 0 else "no_data (由 Web Search 补充)",
        }
        print(f"   │   └─ {reddit_count} 条讨论" if reddit_count > 0 else "   │   └─ 由 Web Search 补充")

        # 5. Google Trends (可跳过)
        if self.config.get("trends", {}).get("enabled", True):
            print("   ├─ [5/7] 采集 Google Trends 数据...")
            try:
                self.data["google_trends"] = collector.fetch_google_trends(self.keywords)
                kw_count = len(self.data["google_trends"].get("keywords", {}))
                lineage["google_trends"] = {
                    "source": "Google Trends (pytrends)",
                    "keywords": kw_count,
                    "time": collect_time,
                    "status": "success" if kw_count > 0 else "no_data (中国网络受限)",
                }
                print(f"   │   └─ {kw_count} 个关键词趋势" if kw_count > 0 else "   │   └─ 中国网络受限")
            except Exception as e:
                print(f"   │   └─ ⚠️ 跳过 (无法连接): {str(e)[:80]}")
                self.data["google_trends"] = {"keywords": {}, "error": str(e)}
                lineage["google_trends"] = {
                    "source": "Google Trends",
                    "status": "skipped (中国网络受限)",
                }
        else:
            print("   ├─ [5/7] Google Trends: 跳过 (配置禁用)")
            self.data["google_trends"] = {"keywords": {}, "status": "skipped"}
            lineage["google_trends"] = {"source": "Google Trends", "status": "skipped"}

        # 6. 1688 供应商 (Apify: 无免费Actor → Web Search)
        print("   ├─ [6/7] 采集 1688 供应商数据...")
        supplier_kw = self.config.get("supplier_keywords", [])
        self.data["supplier"] = collector.fetch_supplier_data(supplier_kw)
        supplier_count = self.data["supplier"].get("total", 0)
        supplier_source = "Web Search" if self.data["supplier"].get("_source") == "unavailable" else "Apify"
        lineage["1688_supplier"] = {
            "source": f"1688 Supplier ({supplier_source})",
            "count": supplier_count,
            "time": collect_time,
            "status": "success" if supplier_count > 0 else f"no_data (由 {supplier_source} 补充)",
        }
        print(f"   │   └─ {supplier_count} 个供应商" if supplier_count > 0 else "   │   └─ 由 Web Search 补充")

        # 7. 市场报告 (Apify web-scraper → Web Search/Web Fetch)
        print("   └─ [7/7] 采集市场报告数据...")
        self.data["market"] = collector.fetch_market_data(self.category)
        market_size = self.data["market"].get("market_size", "")
        market_source = self.data["market"].get("source", "Web Search")
        lineage["market_report"] = {
            "source": f"Market Report ({market_source})",
            "size": market_size if market_size else "由 Web Search 补充",
            "time": collect_time,
            "status": "success" if market_size else "由 Web Search 补充",
        }
        print(f"       └─ 市场规模: {market_size if market_size else '由 Web Search 补充'}")

        print(f"\n   ✅ 全量采集完成! 数据溯源记录: {len(lineage)} 项")

    def _analyze_data(self):
        """分析数据"""
        print("\n🧠 Step 2: 多维度数据分析中...")

        # 市场分析
        print("   ├─ 市场机会分析...")
        market_analyzer = MarketAnalyzer(self.data)
        self.data["analysis"]["market"] = market_analyzer.analyze()

        # TikTok 分析
        print("   ├─ TikTok 传播潜力分析...")
        tiktok_analyzer = TikTokAnalyzer(self.data)
        self.data["analysis"]["tiktok"] = tiktok_analyzer.analyze()

        # 利润建模
        print("   └─ 利润模型构建...")
        profit_builder = ProfitModelBuilder(self.data)
        self.data["analysis"]["profit"] = profit_builder.build()

        print("   ✅ 分析完成")

    def _generate_report(self, output_format: str = "html") -> Path:
        """生成报告"""
        print(f"\n📝 Step 3: 生成报告中 ({output_format.upper()})...")

        if output_format == "html":
            generator = HTMLReportGenerator(self.data, self.output_dir)
            return generator.generate()
        else:
            generator = ReportGenerator(self.data, self.output_dir)
            return generator.generate(format=output_format)


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="Amazon Product Research Toolkit v3.0 - 15章深度选品调研自动化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --market US --category "kids supplements"
  python main.py --market UK --category "probiotics" --keywords "digestive health, gut health"
  python main.py --config config.json --output-format html

数据源 (v3.0):
  📊 Amazon 商品+差评  📱 TikTok 流量  🗣️ Reddit 用户洞察
  📈 Google Trends  🏭 1688 供应商  📊 市场报告数据

v3.0 新维度:
  🧑 消费者画像  📊 五维交叉验证  📈 市场容量筛选
  🔄 产品生命周期定位  🛡️ 研发壁垒构建  ⚠️ "为什么不选"风险评估
  📋 90天执行路线图  📌 每章数据溯源标注

核心原则:
  ⚠️ 所有数据必须真实，采集失败则不显示，绝不捏造

环境变量:
  APIFY_API_TOKEN    - Apify API Token (必需)
  DEFAULT_MARKET     - 默认市场 (默认: US)
  OUTPUT_FORMAT      - 输出格式 (默认: html)
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
    parser.add_argument("--output-format", "-f", default="html",
                        choices=["html", "markdown", "pdf", "word"],
                        help="报告输出格式 (默认 html)")
    parser.add_argument("--output-dir", "-o", type=Path,
                        help="输出目录")
    parser.add_argument("--max-products", type=int,
                        default=int(os.getenv("MAX_PRODUCTS", "100")),
                        help="最大采集商品数")

    # 数据源开关
    parser.add_argument("--skip-reddit", action="store_true",
                        help="跳过 Reddit 数据采集")
    parser.add_argument("--skip-trends", action="store_true",
                        help="跳过 Google Trends 采集")
    parser.add_argument("--skip-reviews", action="store_true",
                        help="跳过差评分析")
    parser.add_argument("--skip-tiktok", action="store_true",
                        help="跳过 TikTok 采集")
    parser.add_argument("--skip-supplier", action="store_true",
                        help="跳过 1688 供应商采集")

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

    # 数据源跳过配置
    if args.skip_reddit:
        config["reddit"] = {"enabled": False}
    if args.skip_trends:
        config["trends"] = {"enabled": False}
    if args.skip_reviews:
        config["review_analysis"] = {"enabled": False}
    if args.skip_supplier:
        config["collection"]["skip_supplier"] = True

    # 检查 API Token
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        print("\n⚠️  警告: APIFY_API_TOKEN 未设置")
        print("   部分数据源需要 Apify API 才能采集真实数据")
        print("   设置环境变量: export APIFY_API_TOKEN='your-token'\n")
        print("   📌 v3.0 原则: 绝不使用mock数据，采集失败的数据源将跳过\n")

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
        pipeline.run(output_format=args.output_format)
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
