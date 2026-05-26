# -*- coding: utf-8 -*-
"""Apify 数据采集 v2 - 修复版"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

os.environ['APIFY_API_TOKEN'] = os.getenv("APIFY_API_TOKEN", "")
if not os.environ['APIFY_API_TOKEN']:
    print("ERROR: APIFY_API_TOKEN 环境变量未设置")
    sys.exit(1)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    from apify_client import ApifyClient
    client = ApifyClient(os.environ['APIFY_API_TOKEN'])
    print("API connected OK")
except Exception as e:
    print(f"Connection error: {e}")
    sys.exit(1)

all_products = []

# Try actor 1: epctex/amazon-product-scraper (uses 'keyword' param)
print("\n=== Trying epctex/amazon-product-scraper ===")
keywords = [
    "children vitamins supplements",
    "kids gummy vitamins",
    "childrens probiotics",
    "kids omega 3"
]

for kw in keywords:
    try:
        run_input = {
            "keyword": kw,
            "maxItems": 30,
            "domain": "amazon.com"
        }
        print(f"  Search: {kw}")
        run = client.actor("epctex/amazon-product-scraper").call(run_input=run_input, timeout_secs=120)
        
        if run and "defaultDatasetId" in run:
            items = client.dataset(run["defaultDatasetId"]).list_items().items
            print(f"  Got {len(items)} items")
            
            for item in items:
                price_val = 0
                price_data = item.get("price", {})
                if isinstance(price_data, dict):
                    price_val = float(price_data.get("value", 0) or 0)
                elif isinstance(price_data, (int, float)):
                    price_val = float(price_data)
                
                img = ""
                imgs = item.get("images", [])
                if isinstance(imgs, list) and imgs:
                    img = imgs[0].get("link", "") if isinstance(imgs[0], dict) else str(imgs[0])
                
                features = item.get("features", [])
                if isinstance(features, str):
                    features = [features]
                
                all_products.append({
                    "asin": item.get("asin", ""),
                    "title": item.get("title", ""),
                    "brand": item.get("brand", ""),
                    "price": price_val,
                    "rating": float(item.get("stars", 0) or 0),
                    "review_count": int(item.get("reviewsCount", 0) or 0),
                    "bsr": str(item.get("bestsellerRanks", ""))[:200],
                    "image": img,
                    "keyword": kw,
                    "features": features[:5] if isinstance(features, list) else [str(features)[:200]],
                    "url": item.get("url", ""),
                    "date_first": item.get("dateFirstAvailable", ""),
                })
        else:
            print(f"  No dataset from run")
    except Exception as e:
        print(f"  Failed: {str(e)[:150]}")

print(f"\nTotal collected: {len(all_products)}")

# Deduplicate by ASIN
seen = set()
unique_products = []
for p in all_products:
    if p['asin'] and p['asin'] not in seen:
        seen.add(p['asin'])
        unique_products.append(p)

print(f"Unique products: {len(unique_products)}")

if unique_products:
    # Filter: only products with reviews > 10
    filtered = [p for p in unique_products if p.get('review_count', 0) > 10]
    filtered.sort(key=lambda x: x.get('review_count', 0), reverse=True)
    print(f"Filtered (reviews>10): {len(filtered)}")
    
    with open(os.path.join(OUTPUT_DIR, 'apify_amazon_products.json'), 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"Saved to output/apify_amazon_products.json")
    
    print("\n--- Top 10 Products ---")
    for i, p in enumerate(filtered[:10]):
        print(f"  {i+1}. [{p['brand']}] {p['title'][:70]}")
        print(f"     ${p['price']} | {p['rating']}* ({p['review_count']:,} reviews) | ASIN:{p['asin']}")
else:
    print("No products collected, will use web search data")
