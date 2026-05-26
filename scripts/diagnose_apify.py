"""
Apify 诊断脚本 — 逐个测试所有 Actor，输出可用性和参数要求
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.environ['APIFY_API_TOKEN'] = os.getenv("APIFY_API_TOKEN", "")
if not os.environ['APIFY_API_TOKEN']:
    print("ERROR: APIFY_API_TOKEN 环境变量未设置")
    sys.exit(1)

from apify_client import ApifyClient
client = ApifyClient(os.environ['APIFY_API_TOKEN'])

# 1. 检查账户信息
print("=" * 60)
print("1. 账户信息")
print("=" * 60)
try:
    me = client.user().get()
    print(f"  User ID: {me.get('id')}")
    print(f"  Email: {me.get('email')}")
    print(f"  Username: {me.get('username')}")
except Exception as e:
    print(f"  ❌ 账户连接失败: {e}")

# 2. 测试所有已知的 Amazon Actor
print("\n" + "=" * 60)
print("2. 测试 Amazon Product Actors")
print("=" * 60)

amazon_actors = [
    # 名称, Actor ID, 测试参数
    ("junglee/free-amazon-product-scraper (原版)", 
     "junglee/free-amazon-product-scraper",
     {"categoryUrls": [{"url": "https://www.amazon.com/Best-Sellers/zgbs/hpc/3764441"}], "maxItems": 3}),
    
    ("junglee/amazon-product-scraper (付费版)", 
     "junglee/amazon-product-scraper",
     {"categoryUrls": [{"url": "https://www.amazon.com/Best-Sellers/zgbs/hpc/3764441"}], "maxItems": 3}),
    
    ("shopity/amazon-product-scraper", 
     "shopity/amazon-product-scraper",
     {"search": "kids vitamins gummies", "maxItems": 3, "proxyConfiguration": {"useApifyProxy": True}}),
    
    ("lukaskrivka/amazon-scraper-by-urls", 
     "lukaskrivka/amazon-scraper-by-urls",
     {"startUrls": [{"url": "https://www.amazon.com/s?k=kids+vitamins+gummies"}], "maxItems": 3}),
    
    ("epctex/amazon-product-scraper (旧fallback)", 
     "epctex/amazon-product-scraper",
     {"keyword": "kids vitamins", "maxItems": 3}),
    
    ("epctex/amazon-scraper", 
     "epctex/amazon-scraper",
     {"searchTerms": ["kids vitamins"], "maxItems": 3}),
    
    ("mscraper/amazon-scraper", 
     "mscraper/amazon-scraper",
     {"keyword": "kids vitamins", "domain": "com", "maxItems": 3}),
]

for name, actor_id, test_input in amazon_actors:
    try:
        # 先获取 actor 信息
        info = client.actor(actor_id).get()
        actor_title = info.get('title', 'N/A')
        print(f"\n  ▶ {name}")
        print(f"    Title: {actor_title}")
        
        # 尝试启动
        try:
            run = client.actor(actor_id).start(run_input=test_input, wait_for_finish=60)
            status = run.get('status', 'N/A')
            print(f"    Run Status: {status}")
            
            if status == 'SUCCEEDED':
                items = list(client.dataset(run['defaultDatasetId']).iterate_items())
                print(f"    ✅ Items: {len(items)}")
                if items:
                    item = items[0]
                    for k in ['title', 'asin', 'price', 'stars']:
                        if k in item:
                            print(f"      {k}: {str(item[k])[:80]}")
        except Exception as run_e:
            print(f"    ⚠️ Run failed: {str(run_e)[:150]}")
            # 尝试获取该 Actor 的输入 schema
            try:
                schema = info.get('input', {}).get('properties', {})
                if schema:
                    print(f"    Required inputs: {list(schema.keys())[:10]}")
            except:
                pass
            
    except Exception as e:
        print(f"\n  ▶ {name}")
        print(f"    ❌ Actor not found or error: {str(e)[:150]}")

# 3. 测试 TikTok Actors
print("\n" + "=" * 60)
print("3. 测试 TikTok Actors")
print("=" * 60)

tiktok_actors = [
    ("clockworks/tiktok-scraper", "clockworks/tiktok-scraper",
     {"hashtags": ["kidssupplements"], "resultsPerPage": 3}),
    
    ("novi/free-tiktok-hashtag-scraper", "novi/free-tiktok-hashtag-scraper",
     {"hashtags": ["kidssupplements"]}),
    
    ("rocketapi/tiktok-scraper", "rocketapi/tiktok-scraper",
     {"hashtag": "kidssupplements", "count": 5}),
    
    ("apify/tiktok-scraper", "apify/tiktok-scraper",
     {"hashtags": ["kidssupplements"], "resultsPerPage": 3}),
    
    ("saadkhalid/tiktok-videos-scraper", "saadkhalid/tiktok-videos-scraper",
     {"hashtags": ["kidssupplements"]}),
    
    ("tikapi/tiktok-scraper-lite", "tikapi/tiktok-scraper-lite",
     {"hashtag": "kidssupplements", "limit": 3}),
]

for name, actor_id, test_input in tiktok_actors:
    try:
        info = client.actor(actor_id).get()
        actor_title = info.get('title', 'N/A')
        print(f"\n  ▶ {name}")
        print(f"    Title: {actor_title}")
        
        try:
            run = client.actor(actor_id).start(run_input=test_input, wait_for_finish=60)
            status = run.get('status', 'N/A')
            print(f"    Run Status: {status}")
            if status == 'SUCCEEDED':
                items = list(client.dataset(run['defaultDatasetId']).iterate_items())
                print(f"    ✅ Items: {len(items)}")
                if items:
                    sample = items[0]
                    for k in list(sample.keys())[:5]:
                        print(f"      {k}: {str(sample[k])[:80]}")
        except Exception as run_e:
            print(f"    ⚠️ Run failed: {str(run_e)[:150]}")
    except Exception as e:
        print(f"\n  ▶ {name}")
        print(f"    ❌ Not found: {str(e)[:150]}")

# 4. 测试 1688 Actors
print("\n" + "=" * 60)
print("4. 测试 1688 Actors")
print("=" * 60)

alibaba_actors = [
    ("luzhiyu/1688-product-scraper", "luzhiyu/1688-product-scraper",
     {"searchTerms": ["儿童维生素"], "maxItems": 3}),
    
    ("logical_api/1688-scraper", "logical_api/1688-scraper",
     {"keyword": "儿童维生素", "maxItems": 3}),
    
    ("easyapi/1688-product-scraper", "easyapi/1688-product-scraper",
     {"keyword": "儿童维生素"}),
]

for name, actor_id, test_input in alibaba_actors:
    try:
        info = client.actor(actor_id).get()
        print(f"\n  ▶ {name}")
        print(f"    Title: {info.get('title', 'N/A')}")
        try:
            run = client.actor(actor_id).start(run_input=test_input, wait_for_finish=60)
            status = run.get('status', 'N/A')
            print(f"    Run Status: {status}")
            if status == 'SUCCEEDED':
                items = list(client.dataset(run['defaultDatasetId']).iterate_items())
                print(f"    ✅ Items: {len(items)}")
        except Exception as run_e:
            print(f"    ⚠️ Run failed: {str(run_e)[:150]}")
    except Exception as e:
        print(f"\n  ▶ {name}")
        print(f"    ❌ Not found: {str(e)[:150]}")

# 5. 测试 Reviews Actor
print("\n" + "=" * 60)
print("5. 测试 Amazon Reviews Actor")
print("=" * 60)

review_actors = [
    ("junglee/amazon-reviews-scraper (原版)", "junglee/amazon-reviews-scraper",
     {"productUrls": [{"url": "https://www.amazon.com/dp/B0B52F7K5G"}], "maxReviews": 5, "filterByRatings": ["oneStar", "twoStar"]}),
    
    ("shopity/amazon-reviews-scraper", "shopity/amazon-reviews-scraper",
     {"asin": "B0B52F7K5G", "maxReviews": 5, "domain": "com"}),
]

for name, actor_id, test_input in review_actors:
    try:
        info = client.actor(actor_id).get()
        print(f"\n  ▶ {name}")
        print(f"    Title: {info.get('title', 'N/A')}")
        try:
            run = client.actor(actor_id).start(run_input=test_input, wait_for_finish=60)
            status = run.get('status', 'N/A')
            print(f"    Run Status: {status}")
            if status == 'SUCCEEDED':
                items = list(client.dataset(run['defaultDatasetId']).iterate_items())
                print(f"    ✅ Items: {len(items)}")
        except Exception as run_e:
            print(f"    ⚠️ Run failed: {str(run_e)[:150]}")
    except Exception as e:
        print(f"\n  ▶ {name}")
        print(f"    ❌ Not found: {str(e)[:150]}")

# 6. 测试 Reddit Actors
print("\n" + "=" * 60)
print("6. 测试 Reddit Actors")
print("=" * 60)

reddit_actors = [
    ("trudax/reddit-scraper", "trudax/reddit-scraper",
     {"searchTerms": ["kids vitamins"], "maxPosts": 5, "subreddits": ["Supplements"]}),
    
    ("carsonbot/reddit-scraper", "carsonbot/reddit-scraper",
     {"subreddits": ["Supplements"], "searchTerms": ["kids vitamins"], "maxItems": 5}),
    
    ("alvaro/reddit-scraper", "alvaro/reddit-scraper",
     {"subreddits": ["Supplements"], "search": "kids vitamins", "maxPosts": 5}),
]

for name, actor_id, test_input in reddit_actors:
    try:
        info = client.actor(actor_id).get()
        print(f"\n  ▶ {name}")
        print(f"    Title: {info.get('title', 'N/A')}")
        try:
            run = client.actor(actor_id).start(run_input=test_input, wait_for_finish=60)
            status = run.get('status', 'N/A')
            print(f"    Run Status: {status}")
            if status == 'SUCCEEDED':
                items = list(client.dataset(run['defaultDatasetId']).iterate_items())
                print(f"    ✅ Items: {len(items)}")
        except Exception as run_e:
            print(f"    ⚠️ Run failed: {str(run_e)[:150]}")
    except Exception as e:
        print(f"\n  ▶ {name}")
        print(f"    ❌ Not found: {str(e)[:150]}")

print("\n" + "=" * 60)
print("诊断完成!")
print("=" * 60)
