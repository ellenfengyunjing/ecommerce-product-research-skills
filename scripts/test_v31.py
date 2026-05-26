"""
v3.1 修复后 Apify 采集集成测试
测试: Amazon产品 / Amazon差评 / TikTok — 三个已验证可用的 Actor
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.environ['APIFY_API_TOKEN'] = os.getenv("APIFY_API_TOKEN", "")
if not os.environ['APIFY_API_TOKEN']:
    print("ERROR: APIFY_API_TOKEN 环境变量未设置")
    sys.exit(1)

from data_collector import DataCollector
from config import CONFIG

print("=" * 60)
print("v3.1 Apify 采集集成测试")
print("=" * 60)

# 测试用关键词
keywords = ["kids vitamins gummies", "childrens probiotics", "kids omega 3"]
supplier_keywords = ["儿童维生素软糖", "儿童益生菌"]

collector = DataCollector(market="US", config=CONFIG)
print(f"\nMarket: US  |  Token: {collector.api_token[:8]}...")

# ============================================
# Test 1: Amazon 商品采集
# ============================================
print("\n" + "=" * 60)
print("TEST 1: Amazon 商品采集")
print("=" * 60)
start = time.time()
products = collector.fetch_amazon_products(keywords)
elapsed = time.time() - start

print(f"\n结果: {len(products)} 个商品 ({elapsed:.1f}s)")
if products:
    print(f"\n前5个商品:")
    for i, p in enumerate(products[:5]):
        print(f"  {i+1}. [{p.get('asin')}] {p.get('title','')[:70]}")
        print(f"     Brand: {p.get('brand')} | ${p.get('price')} | ⭐{p.get('rating')} | {p.get('review_count')} reviews")
else:
    print("  ⚠️ 未采集到商品 (Apify可能额度不足)")

# ============================================
# Test 2: Amazon 差评采集
# ============================================
print("\n" + "=" * 60)
print("TEST 2: Amazon 差评采集")
print("=" * 60)
asins = [p.get("asin") for p in products if p.get("asin")][:5]
print(f"目标 ASINs: {asins}")

start = time.time()
reviews = collector.fetch_negative_reviews(asins, max_per_product=5)
elapsed = time.time() - start

print(f"\n结果: {reviews.get('total_reviews', 0)} 条差评 ({elapsed:.1f}s)")
if reviews.get("pain_categories"):
    print(f"痛点分类: {reviews['pain_categories']}")
    if reviews.get("top_negative_keywords"):
        print(f"Top关键词: {reviews['top_negative_keywords'][:5]}")

# ============================================
# Test 3: TikTok 采集
# ============================================
print("\n" + "=" * 60)
print("TEST 3: TikTok 流量采集")
print("=" * 60)

tiktok_kw = ["kidsvitamins", "childrenshealth"]
start = time.time()
tiktok_data = collector.fetch_tiktok_data(tiktok_kw)
elapsed = time.time() - start

print(f"\n结果: {len(tiktok_data)} 个标签 ({elapsed:.1f}s)")
for td in tiktok_data:
    print(f"  {td.get('hashtag')}: {td.get('videos',0)} videos | views: {td.get('views',0)}")

# ============================================
# Test 4: Reddit (预期: unavailable)
# ============================================
print("\n" + "=" * 60)
print("TEST 4: Reddit (预期回退)")
print("=" * 60)
reddit = collector.fetch_reddit_data(["kids vitamins"])
print(f"状态: {reddit.get('_source', 'unknown')}")
print(f"帖子数: {reddit.get('total_posts', 0)}")

# ============================================
# Test 5: 1688 (预期: unavailable)
# ============================================
print("\n" + "=" * 60)
print("TEST 5: 1688 (预期回退)")
print("=" * 60)
supplier = collector.fetch_supplier_data(supplier_keywords)
print(f"状态: {supplier.get('_source', 'unknown')}")
print(f"供应商数: {supplier.get('total', 0)}")

# ============================================
# Summary
# ============================================
print("\n" + "=" * 60)
print("集成测试总结")
print("=" * 60)
summary = {
    "Amazon商品": f"✅ {len(products)}件" if products else "❌ 空",
    "Amazon差评": f"✅ {reviews.get('total_reviews', 0)}条" if reviews.get('total_reviews', 0) > 0 else "❌ 空",
    "TikTok数据": f"✅ {len(tiktok_data)}标签" if tiktok_data else "❌ 空",
    "Reddit": f"⚠️ {reddit.get('_source', 'unknown')} → Web Search回退",
    "1688": f"⚠️ {supplier.get('_source', 'unknown')} → Web Search回退",
}
for k, v in summary.items():
    print(f"  {k}: {v}")
