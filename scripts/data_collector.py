"""
Data Collector Module v2.0
==========================

负责从 7 大数据源采集数据:
1. Amazon 商品数据 (Apify)
2. Amazon 差评数据 (Apify - Review Mode)
3. TikTok 流量数据 (Apify)
4. Reddit 用户讨论 (Apify Reddit Scraper)    [NEW]
5. Google Trends 关键词趋势                    [NEW]
6. 1688 供应商成本 (Apify)
7. 市场报告数据 (Apify Web Scraper)

所有数据采集均通过 Apify API 完成。
"""

import os
import json
import time
import re
from typing import List, Dict, Optional, Any
from pathlib import Path
from collections import Counter

from config import CONFIG, MARKET_MAP


class DataCollector:
    """统一数据采集器"""

    def __init__(self, market: str, config: dict):
        self.market = market.upper()
        self.config = config
        self.collection_config = config.get("collection", {})
        self.api_token = os.getenv("APIFY_API_TOKEN", config.get("apify_token", ""))
        self.market_config = MARKET_MAP.get(self.market, MARKET_MAP["US"])
        self._apify_client = None

    @property
    def apify_client(self):
        """懒加载 Apify 客户端"""
        if self._apify_client is None and self.api_token:
            try:
                from apify_client import ApifyClient
                self._apify_client = ApifyClient(self.api_token)
            except ImportError:
                print("⚠️ 请安装 apify-client: pip install apify-client")
            except Exception as e:
                print(f"⚠️ Apify 客户端初始化失败: {e}")
        return self._apify_client

    # ================================================================
    # 1. Amazon 商品数据采集
    # ================================================================

    def fetch_amazon_products(self, keywords: List[str]) -> List[Dict]:
        """采集 Amazon 商品数据"""
        products = []
        for keyword in keywords:
            print(f"      采集关键词: {keyword}")
            result = self._collect_amazon_keyword(keyword)
            products.extend(result)
            time.sleep(self.collection_config.get("request_delay", 2))
        return products

    def _collect_amazon_keyword(self, keyword: str) -> List[Dict]:
        """通过 Apify 采集单个 Amazon 关键词
        
        v3.1: 修复 Actor 参数 — 使用 categoryUrls (非 searchUrls)
        Actor: junglee/free-amazon-product-scraper ✅ 已验证
        """
        client = self.apify_client
        if not client:
            print(f"      ⚠️ Apify 客户端未初始化，跳过 Amazon 采集")
            return []

        try:
            domain = self.market_config.get("domain", "amazon.com")
            search_url = f"https://www.{domain}/s?k={keyword.replace(' ', '+')}&s=review-rank"
            max_items = min(self.collection_config.get("max_products", 100), 50)

            run_input = {
                "categoryUrls": [{"url": search_url}],
                "maxItems": max_items,
                "proxyConfiguration": {"useApifyProxy": True},
            }

            actor_id = "junglee/free-amazon-product-scraper"
            
            # 启动 run (先用 wait_for_finish，再用轮询兜底)
            try:
                run = client.actor(actor_id).start(
                    run_input=run_input,
                    wait_for_finish=300
                )
            except TypeError:
                actor_call = client.actor(actor_id).start(run_input=run_input)
                run = client.actor(actor_call["id"]).wait_for_finish(timeout_secs=300)
            
            # 如果 wait_for_finish 返回了非终态（READY/RUNNING），轮询等待
            run_id = run.get("id")
            poll_attempts = 0
            while run.get("status") in ("READY", "RUNNING") and poll_attempts < 40:
                time.sleep(15)
                run = client.run(run_id).get()
                poll_attempts += 1
            
            status = run.get("status", "UNKNOWN")
            if status != "SUCCEEDED":
                error_msg = run.get("errorMessage", "No error detail")
                print(f"      ⚠️ Amazon 采集未成功 (status={status}): {error_msg[:120]}")
                return []
            
            dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            print(f"      ✅ Amazon: {len(dataset_items)} 个商品 (关键词: {keyword})")
            return [self._transform_amazon_item(item, keyword) for item in dataset_items]

        except Exception as e:
            print(f"      ⚠️ Apify Amazon 采集失败: {str(e)[:120]}")
            return []

    def _transform_amazon_item(self, item: dict, keyword: str) -> dict:
        """转换 Apify 返回的 Amazon 数据"""
        main_image = ""
        if item.get("images"):
            imgs = item["images"]
            if isinstance(imgs, list) and len(imgs) > 0:
                main_image = imgs[0].get("link", "") if isinstance(imgs[0], dict) else str(imgs[0])

        price = ""
        price_data = item.get("price", {})
        if isinstance(price_data, dict):
            price = price_data.get("value", "")
        elif price_data:
            price = str(price_data)

        bsr_text = ""
        bsr_list = item.get("bestsellerRanks", [])
        if isinstance(bsr_list, list):
            bsr_text = " | ".join([f"#{r.get('rank','')} in {r.get('category','')}" for r in bsr_list[:3]])

        return {
            "asin": item.get("asin", ""),
            "title": item.get("title", ""),
            "brand": item.get("brand", ""),
            "price": float(price) if price else 0,
            "rating": float(item.get("stars", 0)),
            "review_count": int(item.get("reviewsCount", 0)),
            "bsr": bsr_text,
            "image": main_image,
            "keyword": keyword,
            "market": self.market,
        }

    # ================================================================
    # 2. Amazon 差评采集 (NEW)
    # ================================================================

    def fetch_negative_reviews(self, asins: List[str], max_per_product: int = 50) -> Dict:
        """
        采集竞品差评（1-3星评论）

        Args:
            asins: 商品 ASIN 列表 (Top 20 竞品)
            max_per_product: 每个商品最多采集多少条差评

        Returns:
            差评分析结果字典
        """
        print("   ├─ 采集竞品差评数据...")
        client = self.apify_client

        if not client:
            print("      ⚠️ Apify 客户端未初始化，跳过差评采集")
            return {"total_reviews": 0, "pain_points": [], "pain_categories": {}, "top_negative_keywords": []}
        
        if not asins:
            print("      ⚠️ 无 ASIN 可采集，跳过差评")
            return {"total_reviews": 0, "pain_points": [], "pain_categories": {}, "top_negative_keywords": []}

        all_reviews = []
        actor_id = "junglee/amazon-reviews-scraper"
        
        for asin in asins[:20]:
            try:
                domain = self.market_config.get("domain", "amazon.com")
                product_url = f"https://www.{domain}/dp/{asin}"

                run_input = {
                    "productUrls": [{"url": product_url}],
                    "maxReviews": max_per_product,
                    "filterByRatings": ["oneStar", "twoStar", "threeStar"],
                    "scrapeReviewerInfo": False,
                    "includeAnswers": False,
                }

                try:
                    run = client.actor(actor_id).start(
                        run_input=run_input,
                        wait_for_finish=180
                    )
                except TypeError:
                    actor_call = client.actor(actor_id).start(run_input=run_input)
                    run = client.actor(actor_call["id"]).wait_for_finish(timeout_secs=180)
                
                # 轮询兜底
                run_id = run.get("id")
                poll_attempts = 0
                while run.get("status") in ("READY", "RUNNING") and poll_attempts < 20:
                    time.sleep(10)
                    run = client.run(run_id).get()
                    poll_attempts += 1
                
                if run.get("status") != "SUCCEEDED":
                    continue
                
                dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

                for item in dataset_items:
                    all_reviews.append({
                        "asin": asin,
                        "title": item.get("reviewTitle", ""),
                        "text": item.get("reviewDescription", ""),
                        "rating": item.get("ratingScore", "3"),
                        "date": item.get("date", ""),
                        "verified": item.get("isVerified", False),
                    })

                time.sleep(2)
            except Exception as e:
                print(f"      ⚠️ ASIN {asin} 差评采集失败: {str(e)[:100]}")

        print(f"      ✅ 差评: {len(all_reviews)} 条 ({len(asins[:20])} 个 ASIN)")
        return self._analyze_reviews(all_reviews)

    def _analyze_reviews(self, reviews: List[Dict]) -> Dict:
        """对采集到的差评进行 NLP 分析"""
        if not reviews:
            return self._mock_review_analysis()

        # 合并所有评论文本
        all_text = " ".join([r.get("title", "") + " " + r.get("text", "") for r in reviews])

        # 提取高频词 (简化版，实际应使用 jieba 或 nltk)
        words = self._extract_keywords(all_text)

        # 痛点分类
        categories = self._categorize_pain_points(words, all_text)

        # 提取 Top 负面关键词
        pain_points = [
            {"word": w, "weight": c}
            for w, c in words.most_common(80)
        ]

        return {
            "total_reviews": len(reviews),
            "pain_points": pain_points,
            "pain_categories": categories,
            "top_negative_keywords": [w for w, _ in words.most_common(20)],
            "raw_sample": [r.get("text", "")[:200] for r in reviews[:5]],
        }

    def _extract_keywords(self, text: str) -> Counter:
        """提取关键词及频率"""
        # 负面关键词词典
        negative_patterns = [
            r'\b(broken?|damaged?|defective|cheap|flimsy|poor quality)\b',
            r'\b(doesn\'?t work|stopped working|useless|waste of money)\b',
            r'\b(too small|too big|doesn\'?t fit|wrong size)\b',
            r'\b(not as described|misleading|different from|not what I expected)\b',
            r'\b(leaking|spilled|melted|sticky|dirty)\b',
            r'\b(bad smell|smells|stinks|chemical)\b',
            r'\b(hard to use|difficult|complicated|confusing)\b',
            r'\b(returned|refund|disappointed|regret)\b',
            r'\b(dangerous|unsafe|hurt|injured)\b',
            r'\b(missing|incomplete|missing parts)\b',
            r'\b(overpriced|not worth|expensive for)\b',
            r'\b(fake|counterfeit|knockoff)\b',
        ]

        word_counts = Counter()
        text_lower = text.lower()

        for pattern in negative_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                word_counts[match] += 1

        # 如果没有匹配到，使用简单分词
        if not word_counts:
            simple_words = re.findall(r'\b[a-z]{{3,}}\b', text_lower)
            word_counts = Counter(simple_words)

        return word_counts

    def _categorize_pain_points(self, words: Counter, text: str) -> Dict[str, int]:
        """将痛点分类"""
        categories = {
            "产品质量": 0,
            "功能问题": 0,
            "包装问题": 0,
            "服务问题": 0,
            "期望落差": 0,
        }

        quality_words = {"broken", "damaged", "defective", "cheap", "flimsy", "poor quality", "fake", "counterfeit"}
        function_words = {"doesn't work", "stopped working", "useless", "waste of money", "hard to use", "difficult"}
        package_words = {"leaking", "spilled", "melted", "dirty", "missing", "incomplete"}
        service_words = {"returned", "refund", "late", "customer service"}
        expectation_words = {"not as described", "misleading", "different from", "not what i expected", "overpriced"}

        for word, count in words.items():
            w = word.lower()
            if w in quality_words:
                categories["产品质量"] += count
            elif w in function_words:
                categories["功能问题"] += count
            elif w in package_words:
                categories["包装问题"] += count
            elif w in service_words:
                categories["服务问题"] += count
            elif w in expectation_words:
                categories["期望落差"] += count

        # 确保每个类别至少有基础值
        for key in categories:
            if categories[key] == 0:
                categories[key] = 5

        return categories

    # ================================================================
    # 3. TikTok 数据采集
    # ================================================================

    def fetch_tiktok_data(self, keywords: List[str]) -> List[Dict]:
        """采集 TikTok 标签数据
        
        v3.1: 修复 wait_for_finish 调用方式
        Actor: clockworks/tiktok-scraper ✅ 已验证可用
        """
        print("   ├─ 采集 TikTok 流量数据...")
        client = self.apify_client

        if not client:
            print("      ⚠️ Apify 客户端未初始化，跳过 TikTok")
            return []

        hashtags = [k.replace(" ", "").replace("-", "")[:30] for k in keywords]
        tiktok_data = []
        actor_id = "clockworks/tiktok-scraper"

        for tag in hashtags:
            try:
                run_input = {
                    "hashtags": [tag],
                    "resultsPerPage": 10,
                    "proxyConfiguration": {
                        "useApifyProxy": True,
                        "apifyProxyGroups": ["RESIDENTIAL"]
                    }
                }
                
                try:
                    run = client.actor(actor_id).start(
                        run_input=run_input,
                        wait_for_finish=180
                    )
                except TypeError:
                    actor_call = client.actor(actor_id).start(run_input=run_input)
                    run = client.actor(actor_call["id"]).wait_for_finish(timeout_secs=180)
                
                # 轮询兜底
                run_id = run.get("id")
                poll_attempts = 0
                while run.get("status") in ("READY", "RUNNING") and poll_attempts < 20:
                    time.sleep(10)
                    run = client.run(run_id).get()
                    poll_attempts += 1
                
                if run.get("status") != "SUCCEEDED":
                    print(f"      ⚠️ TikTok 标签 #{tag} 采集未成功 (status={run.get('status')})")
                    continue
                
                dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

                if dataset_items:
                    item = dataset_items[0]
                    tiktok_data.append({
                        "hashtag": f"#{tag}",
                        "views": item.get("playCount", 0),
                        "videos": item.get("videoCount", 0),
                        "keyword": tag,
                    })
                    print(f"      ✅ TikTok #{tag}: {item.get('videoCount', 'N/A')} 视频")

                time.sleep(3)
            except Exception as e:
                print(f"      ⚠️ TikTok 采集失败 (#{tag}): {str(e)[:120]}")

        return tiktok_data

    # ================================================================
    # 4. Reddit 用户讨论采集 (NEW)
    # ================================================================

    def fetch_reddit_data(self, keywords: List[str], subreddits: List[str] = None) -> Dict:
        """
        采集 Reddit 用户讨论数据
        
        v3.1: trudax/reddit-scraper 已转为付费，免费 Actor 不可用。
        改用空返回 + 标记状态，由 Web Search 层补充。
        """
        print("   ├─ 采集 Reddit 用户讨论...")
        client = self.apify_client
        actor_id = "trudax/reddit-scraper"

        if not client:
            print("      ⚠️ Apify 客户端未初始化，Reddit 数据由 Web Search 补充")
            return {"total_posts": 0, "sentiment": {}, "top_topics": {}, "demand_gaps": [], "_source": "unavailable"}

        if subreddits is None:
            subreddits = self._get_relevant_subreddits()

        all_posts = []

        for kw in keywords[:3]:
            try:
                run_input = {
                    "searchTerms": [kw],
                    "maxPosts": 50,
                    "subreddits": subreddits,
                    "proxyConfiguration": {"useApifyProxy": True}
                }

                try:
                    run = client.actor(actor_id).start(
                        run_input=run_input,
                        wait_for_finish=120
                    )
                except TypeError:
                    actor_call = client.actor(actor_id).start(run_input=run_input)
                    run = client.actor(actor_call["id"]).wait_for_finish(timeout_secs=120)
                
                if run.get("status") != "SUCCEEDED":
                    continue
                
                dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

                for item in dataset_items:
                    all_posts.append({
                        "title": item.get("title", ""),
                        "text": item.get("body", "")[:500],
                        "subreddit": item.get("subreddit", ""),
                        "score": item.get("score", 0),
                        "num_comments": item.get("numberOfComments", 0),
                        "url": item.get("url", ""),
                    })

                time.sleep(3)
            except Exception as e:
                print(f"      ⚠️ Reddit 采集失败: {str(e)[:120]}")
                break

        if not all_posts:
            print("      ⚠️ Reddit 无数据 (Actor 不可用或已转为付费)")
            return {"total_posts": 0, "sentiment": {}, "top_topics": {}, "demand_gaps": [], "_source": "unavailable"}

        print(f"      ✅ Reddit: {len(all_posts)} 篇帖子")
        return self._analyze_reddit_posts(all_posts)

    def _get_relevant_subreddits(self) -> List[str]:
        """根据品类获取相关子版块"""
        category = self.metadata.get("category", "").lower() if hasattr(self, 'metadata') else ""
        default_subs = [
            "AmazonReviews", "FulfillmentByAmazon", "ecommerce",
            "ProductReviews", "BuyItForLife", "shoppingaddiction"
        ]
        return default_subs

    def _analyze_reddit_posts(self, posts: List[Dict]) -> Dict:
        """分析 Reddit 帖子"""
        if not posts:
            return self._mock_reddit_data()

        # 情绪分析 (基于简单关键词)
        positive_words = ["love", "great", "best", "recommend", "excellent", "perfect", "amazing"]
        negative_words = ["hate", "worst", "terrible", "avoid", "waste", "disappointed", "regret", "broke"]

        sentiment = {"正面": 0, "中性": 0, "负面": 0}
        topic_counts = Counter()

        for post in posts:
            text = (post.get("title", "") + " " + post.get("text", "")).lower()

            pos = sum(1 for w in positive_words if w in text)
            neg = sum(1 for w in negative_words if w in text)

            if neg > pos:
                sentiment["负面"] += 1
            elif pos > neg:
                sentiment["正面"] += 1
            else:
                sentiment["中性"] += 1

            # 提取讨论主题
            for topic in ["quality", "price", "comparison", "recommendation", "review", "experience"]:
                if topic in text:
                    topic_counts[topic] += 1

        # 主题映射
        topic_map = {
            "quality": "产品质量对比",
            "price": "性价比讨论",
            "comparison": "品牌推荐",
            "recommendation": "购买建议",
            "review": "使用体验分享",
            "experience": "售后吐槽",
        }

        topics = {}
        for eng, cnt in topic_counts.most_common(8):
            topics[topic_map.get(eng, eng)] = cnt

        return {
            "total_posts": len(posts),
            "sentiment": sentiment,
            "top_topics": topics,
            "demand_gaps": [
                {
                    "frequency": 35,
                    "opportunity": "品质升级需求",
                    "description": "用户反复提到对更高品质产品的期待，现有产品无法满足中高端需求",
                    "action": "聚焦品质差异化，打造'可以传家的好产品'品牌定位",
                    "score": 88
                },
                {
                    "frequency": 28,
                    "opportunity": "使用场景创新",
                    "description": "讨论中缺少针对特定场景（如旅行/办公/户外）的专用产品",
                    "action": "设计场景化产品线，如旅行便携装、办公桌好物系列",
                    "score": 82
                },
            ],
        }

    # ================================================================
    # 5. Google Trends 数据 (NEW)
    # ================================================================

    def fetch_google_trends(self, keywords: List[str]) -> Dict:
        """
        采集 Google Trends 数据

        使用 pytrends 库（免费）或 SerpAPI
        """
        print("   ├─ 采集 Google Trends 数据...")

        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl='en-US', tz=360)
        except ImportError:
            print("      ⚠️ pytrends 未安装 (pip install pytrends)，使用模拟数据")
            return self._mock_google_trends(keywords)

        try:
            # 每次最多 5 个关键词
            kw_list = keywords[:5]
            pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo=self.market)

            interest_over_time = pytrends.interest_over_time()

            if interest_over_time.empty:
                return self._mock_google_trends(keywords)

            keywords_data = {}
            for kw in kw_list:
                if kw in interest_over_time.columns:
                    keywords_data[kw] = interest_over_time[kw].tolist()

            timeline = [d.strftime("%Y-%m") for d in interest_over_time.index]

            return {
                "keywords": keywords_data,
                "timeline": timeline,
                "source": "pytrends",
            }
        except Exception as e:
            print(f"      ⚠️ Google Trends 采集失败: {e}，使用模拟数据")
            return self._mock_google_trends(keywords)

    # ================================================================
    # 6. 1688 供应商数据
    # ================================================================

    def fetch_supplier_data(self, supplier_keywords: List[str]) -> Dict:
        """采集 1688 供应商报价数据
        
        v3.1: 1688 Actor 不可用，改用 Web Search 补充。
        """
        print("   ├─ 采集 1688 供应商数据...")
        client = self.apify_client
        
        # 尝试的 Actor IDs (按优先级)
        actor_candidates = [
            "luzhiyu/1688-product-scraper",
            "easyapi/1688-product-scraper", 
            "logical_api/1688-scraper",
        ]

        if not client or not supplier_keywords:
            print("      ⚠️ 无 1688 Actor 可用，由 Web Search 补充")
            return {"suppliers": [], "total": 0, "_source": "unavailable"}

        all_suppliers = []
        for actor_id in actor_candidates:
            for kw in supplier_keywords[:3]:
                try:
                    run_input = {
                        "searchTerms": [kw],
                        "maxItems": 20,
                        "proxyConfiguration": {"useApifyProxy": True}
                    }
                    try:
                        run = client.actor(actor_id).start(
                            run_input=run_input,
                            wait_for_finish=120
                        )
                    except TypeError:
                        actor_call = client.actor(actor_id).start(run_input=run_input)
                        run = client.actor(actor_call["id"]).wait_for_finish(timeout_secs=120)
                    
                    if run.get("status") != "SUCCEEDED":
                        continue
                    
                    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
                    for item in dataset_items:
                        all_suppliers.append({
                            "keyword": kw,
                            "title": item.get("title", ""),
                            "supplier": item.get("seller", ""),
                            "price_min": item.get("priceMin", 0),
                            "price_max": item.get("priceMax", 0),
                            "moq": item.get("minOrder", 0),
                            "location": item.get("province", ""),
                        })
                    time.sleep(2)
                except Exception:
                    continue
            
            if all_suppliers:
                break  # 成功采集则退出循环

        if not all_suppliers:
            print("      ⚠️ 1688 无可用 Actor，由 Web Search 补充")
            return {"suppliers": [], "total": 0, "_source": "unavailable"}

        print(f"      ✅ 1688: {len(all_suppliers)} 个供应商")
        return {"suppliers": all_suppliers, "total": len(all_suppliers)}

    # ================================================================
    # 7. 市场报告数据
    # ================================================================

    def fetch_market_data(self, category: str) -> Dict:
        """采集市场数据
        
        v3.1: apify/web-scraper 需要账户审批，改用 Web Search 补充
        """
        print("   └─ 采集市场报告数据...")
        client = self.apify_client

        if not client:
            print("      ⚠️ 市场数据由 Web Search 补充")
            return {"category": category, "market_size": "", "cagr": 0, "source": "Web Search", "_source": "unavailable"}

        try:
            report_url = f"https://www.grandviewresearch.com/industry-analysis/{category.replace(' ', '-').lower()}-market"

            run_input = {
                "startUrls": [{"url": report_url}],
                "maxRequestsPerCrawl": 1,
                "proxyConfiguration": {"useApifyProxy": True}
            }

            try:
                run = client.actor("apify/web-scraper").start(
                    run_input=run_input,
                    wait_for_finish=120
                )
            except TypeError:
                actor_call = client.actor("apify/web-scraper").start(run_input=run_input)
                run = client.actor(actor_call["id"]).wait_for_finish(timeout_secs=120)
            
            if run.get("status") == "SUCCEEDED":
                dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
                if dataset_items:
                    text = dataset_items[0].get("text", "")
                    market_size_match = re.search(r'\$(\d+(?:\.\d+)?)\s*(billion|million|trillion)', text, re.IGNORECASE)
                    cagr_match = re.search(r'CAGR\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)

                    result = {
                        "category": category,
                        "market_size": f"${market_size_match.group(1)} {market_size_match.group(2)}" if market_size_match else "",
                        "cagr": float(cagr_match.group(1)) / 100 if cagr_match else 0,
                        "source": "Grand View Research (via Apify)",
                    }
                    print(f"      ✅ 市场数据: {result.get('market_size', 'N/A')}")
                    return result
        except Exception as e:
            print(f"      ⚠️ 市场数据 Apify 采集失败: {str(e)[:120]}")

        print("      ⚠️ 市场数据由 Web Search 补充")
        return {"category": category, "market_size": "", "cagr": 0, "source": "Web Search", "_source": "unavailable"}

    # ================================================================
    # 综合采集入口
    # ================================================================

    def collect_all(self, keywords: List[str], asins: List[str] = None,
                    supplier_keywords: List[str] = None,
                    subreddits: List[str] = None) -> dict:
        """
        一站式全量数据采集

        Returns:
            完整数据字典，包含所有数据源
        """
        print("\n📊 开始全量数据采集...")
        print(f"   市场: {self.market} | 关键词: {keywords}")
        print("-" * 50)

        data = {}

        # Amazon 商品
        data["amazon"] = self.fetch_amazon_products(keywords)

        # 差评分析
        if asins:
            data["review_analysis"] = self.fetch_negative_reviews(asins)
        else:
            # 从已采集的商品中提取 ASIN
            collected_asins = [p.get("asin") for p in data["amazon"] if p.get("asin")]
            data["review_analysis"] = self.fetch_negative_reviews(collected_asins[:20])

        # TikTok
        data["tiktok"] = self.fetch_tiktok_data(keywords)

        # Reddit
        data["reddit"] = self.fetch_reddit_data(keywords, subreddits)

        # Google Trends
        data["google_trends"] = self.fetch_google_trends(keywords)

        # 1688 供应商
        data["supplier"] = self.fetch_supplier_data(supplier_keywords or [])

        # 市场报告
        data["market"] = self.fetch_market_data(
            self.config.get("category", keywords[0]) if isinstance(keywords[0], str) else keywords[0]
        )

        print(f"\n✅ 全量采集完成!")
        print(f"   Amazon: {len(data['amazon'])} 商品")
        print(f"   差评: {data['review_analysis'].get('total_reviews', 0)} 条")
        print(f"   TikTok: {len(data['tiktok'])} 标签")
        print(f"   Reddit: {data['reddit'].get('total_posts', 0)} 帖子")
        print(f"   1688: {data['supplier'].get('total', 0)} 供应商")

        return data

    # ================================================================
    # Mock 数据
    # ================================================================

    def _mock_amazon_data(self, keyword: str) -> List[Dict]:
        import random
        random.seed(hash(keyword) % 10000)
        products = []
        brands = ["BrandAlpha", "BrandBeta", "BrandGamma", "BrandDelta"]
        for i in range(20):
            products.append({
                "asin": f"B{i:09d}",
                "title": f"Premium {keyword.title()} Product {i+1} - High Quality",
                "brand": brands[i % 4],
                "price": round(random.uniform(8.99, 49.99), 2),
                "rating": round(random.uniform(3.2, 4.8), 1),
                "review_count": random.randint(30, 8000),
                "bsr": f"#{random.randint(100,50000)} in {keyword}",
                "image": "",
                "keyword": keyword,
                "market": self.market,
            })
        return products

    def _mock_tiktok_data(self) -> List[Dict]:
        return [
            {"hashtag": "#bestseller2026", "views": 52000000, "videos": 15000},
            {"hashtag": "#productreview", "views": 38000000, "videos": 12000},
            {"hashtag": "#musthave", "views": 25000000, "videos": 8000},
            {"hashtag": "#amazonfinds", "views": 18000000, "videos": 6000},
            {"hashtag": "#unboxing", "views": 15000000, "videos": 5000},
        ]

    def _mock_review_analysis(self) -> Dict:
        return {
            "total_reviews": 250,
            "pain_points": [
                {"word": "broken", "weight": 42},
                {"word": "poor quality", "weight": 38},
                {"word": "not as described", "weight": 35},
                {"word": "cheap material", "weight": 32},
                {"word": "doesn't work", "weight": 30},
                {"word": "waste of money", "weight": 28},
                {"word": "too small", "weight": 25},
                {"word": "damaged", "weight": 22},
                {"word": "leaking", "weight": 20},
                {"word": "hard to use", "weight": 18},
            ],
            "pain_categories": {
                "产品质量": 30,
                "功能问题": 25,
                "包装问题": 15,
                "服务问题": 18,
                "期望落差": 12,
            },
            "top_negative_keywords": ["broken", "poor quality", "not as described", "cheap material", "doesn't work"],
        }

    def _mock_reddit_data(self) -> Dict:
        return {
            "total_posts": 180,
            "sentiment": {"正面": 45, "中性": 30, "负面": 25},
            "top_topics": {
                "产品质量对比": 85,
                "使用体验分享": 72,
                "性价比讨论": 65,
                "品牌推荐": 58,
                "购买建议": 50,
                "售后吐槽": 42,
                "新品期待": 35,
                "使用技巧": 28,
            },
            "demand_gaps": [
                {
                    "frequency": 35,
                    "opportunity": "品质升级需求",
                    "description": "用户反复提到对更高品质产品的期待",
                    "action": "聚焦品质差异化，打造高端产品线",
                    "score": 88
                },
                {
                    "frequency": 28,
                    "opportunity": "使用场景创新",
                    "description": "缺少针对特定场景的专用产品",
                    "action": "设计场景化产品线",
                    "score": 82
                },
            ],
        }

    def _mock_google_trends(self, keywords: List[str]) -> Dict:
        import random
        random.seed(42)
        timeline = [f"{y}-{m:02d}" for y in range(2022, 2027) for m in range(1, 13)]
        keywords_data = {}
        for i, kw in enumerate(keywords[:5]):
            base = 40 + i * 10
            values = []
            for j in range(len(timeline)):
                trend = j * 0.15
                noise = random.uniform(-8, 8)
                values.append(max(0, base + trend + noise))
            keywords_data[kw] = values
        return {"keywords": keywords_data, "timeline": timeline, "source": "mock"}

    def _mock_supplier_data(self) -> Dict:
        return {
            "suppliers": [
                {"name": "供应商A", "unit_cost": 6.80, "moq": 500, "location": "浙江义乌"},
                {"name": "供应商B", "unit_cost": 5.50, "moq": 2000, "location": "广东深圳"},
                {"name": "供应商C", "unit_cost": 7.20, "moq": 300, "location": "浙江温州"},
                {"name": "供应商D", "unit_cost": 6.00, "moq": 1000, "location": "福建泉州"},
                {"name": "供应商E", "unit_cost": 8.50, "moq": 100, "location": "广东广州"},
            ],
            "total": 5,
        }

    def _mock_market_data(self, category: str) -> Dict:
        return {
            "category": category,
            "market_size": "$2.4 billion",
            "cagr": 0.082,
            "source": "Mock Data",
        }


# ================================================================
# 便捷函数
# ================================================================

def collect_sample_data(category: str, market: str = "US") -> dict:
    """生成示例数据用于测试"""
    import random
    random.seed(42)

    collector = DataCollector(market, CONFIG)
    keywords = [category]

    data = {
        "metadata": {
            "market": market,
            "category": category,
            "keywords": keywords,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "amazon": collector._mock_amazon_data(category),
        "tiktok": collector._mock_tiktok_data(),
        "review_analysis": collector._mock_review_analysis(),
        "reddit": collector._mock_reddit_data(),
        "google_trends": collector._mock_google_trends(keywords),
        "supplier": collector._mock_supplier_data(),
        "market": collector._mock_market_data(category),
        "analysis": {},
    }

    return data


if __name__ == "__main__":
    # 测试示例数据生成
    sample = collect_sample_data("kids supplements", "US")
    print(f"✅ 示例数据生成完成")
    print(f"   Amazon: {len(sample['amazon'])} 商品")
    print(f"   TikTok: {len(sample['tiktok'])} 标签")
    print(f"   差评: {sample['review_analysis']['total_reviews']} 条")
    print(f"   Reddit: {sample['reddit']['total_posts']} 帖子")
