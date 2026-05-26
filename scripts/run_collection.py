# -*- coding: utf-8 -*-
"""临时采集脚本 - 美区儿童保健品数据"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

os.environ['APIFY_API_TOKEN'] = os.getenv("APIFY_API_TOKEN", "")
if not os.environ['APIFY_API_TOKEN']:
    print("ERROR: APIFY_API_TOKEN 环境变量未设置")
    sys.exit(1)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_connection():
    try:
        from apify_client import ApifyClient
        client = ApifyClient(os.environ['APIFY_API_TOKEN'])
        me = client.user().get()
        print(f"API connected: {me.get('id', 'N/A')}")
        return client
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def collect_amazon(client):
    """采集 Amazon 儿童保健品商品数据"""
    print("\n[1] Amazon Product Scraper...")
    keywords = [
        "children vitamins",
        "kids multivitamin gummies",
        "childrens probiotics",
        "kids omega supplements",
        "childrens immune support"
    ]
    
    all_products = []
    for kw in keywords:
        try:
            search_url = f"https://www.amazon.com/s?k={kw.replace(' ', '+')}&s=review-rank"
            run_input = {
                "searchUrls": [search_url],
                "maxItems": 40,
                "scrapeVariants": False,
                "includeFields": ["title","url","asin","brand","price","stars","reviewsCount","bestsellerRanks","images","features"]
            }
            
            # Try primary actor
            print(f"  Searching: {kw}")
            actor_call = client.actor("junglee/free-amazon-product-scraper").start(run_input=run_input)
            run_id = actor_call.get("id", "")
            print(f"  Run ID: {run_id}")
            client.actor(run_id).wait_for_finish(timeout_secs=180)
            items = client.dataset(actor_call["defaultDatasetId"]).list_items().items
            print(f"  Collected: {len(items)} items")
            
            for item in items:
                price_val = 0
                price_data = item.get("price", {})
                if isinstance(price_data, dict):
                    price_val = float(price_data.get("value", 0))
                elif price_data:
                    try:
                        price_val = float(str(price_data).replace("$","").replace(",",""))
                    except:
                        pass
                
                img = ""
                imgs = item.get("images", [])
                if isinstance(imgs, list) and imgs:
                    img = imgs[0].get("link", "") if isinstance(imgs[0], dict) else str(imgs[0])
                
                bsr = ""
                bsr_list = item.get("bestsellerRanks", [])
                if isinstance(bsr_list, list):
                    bsr = " | ".join([f"#{r.get('rank','')} in {r.get('category','')}" for r in bsr_list[:3]])
                
                all_products.append({
                    "asin": item.get("asin", ""),
                    "title": item.get("title", ""),
                    "brand": item.get("brand", ""),
                    "price": price_val,
                    "rating": float(item.get("stars", 0)),
                    "review_count": int(item.get("reviewsCount", 0)),
                    "bsr": bsr,
                    "image": img,
                    "keyword": kw,
                    "features": item.get("features", [])[:5],
                    "date_first": item.get("dateFirstAvailable", ""),
                })
        except Exception as e:
            print(f"  Failed for {kw}: {str(e)[:100]}")
    
    return all_products

def collect_tiktok(client):
    """采集 TikTok 数据"""
    print("\n[2] TikTok Scraper...")
    hashtags = ["kidssupplements", "childrensvitamins", "gummyvitamins", "kidshealth", "momsoftiktok"]
    tiktok_data = []
    
    for tag in hashtags:
        try:
            run_input = {
                "hashtags": [tag],
                "resultsPerPage": 5,
                "proxyConfiguration": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]}
            }
            actor_call = client.actor("clockworks/tiktok-scraper").start(run_input=run_input)
            client.actor(actor_call["id"]).wait_for_finish(timeout_secs=90)
            items = client.dataset(actor_call["defaultDatasetId"]).list_items().items
            
            if items:
                for item in items[:3]:
                    tiktok_data.append({
                        "hashtag": f"#{tag}",
                        "views": item.get("playCount", 0) or item.get("videoPlayCount", 0),
                        "videos": item.get("videoCount", 0) or item.get("postsCount", 0),
                        "keyword": tag,
                    })
                print(f"  #{tag}: {tiktok_data[-1].get('views', 0):,} views")
            else:
                print(f"  #{tag}: no data")
        except Exception as e:
            print(f"  #{tag} failed: {str(e)[:80]}")
    
    return tiktok_data

def collect_market_report(client):
    """采集市场报告"""
    print("\n[3] Market Report Scraper...")
    try:
        report_urls = [
            "https://www.grandviewresearch.com/industry-analysis/dietary-supplements-market",
        ]
        
        page_function = """
        async function pageFunction({ request, page, saveSnapshot }) {
            await page.waitForTimeout(3000);
            const data = await page.evaluate(() => {
                const main = document.querySelector('main, .content, article');
                return main ? main.innerText.substring(0, 5000) : document.body.innerText.substring(0, 5000);
            });
            await saveSnapshot({ url: request.url, text: data });
        }
        """
        
        for url in report_urls:
            run_input = {
                "startUrls": [{"url": url}],
                "pageFunction": page_function,
                "maxRequestsPerCrawl": 1,
                "proxyConfiguration": {"useApifyProxy": True}
            }
            actor_call = client.actor("apify/web-scraper").start(run_input=run_input)
            client.actor(actor_call["id"]).wait_for_finish(timeout_secs=120)
            items = client.dataset(actor_call["defaultDatasetId"]).list_items().items
            
            if items:
                text = items[0].get("text", "")
                print(f"  Market report text: {len(text)} chars")
                with open(os.path.join(OUTPUT_DIR, 'market_report_raw.txt'), 'w', encoding='utf-8') as f:
                    f.write(text)
            else:
                print(f"  No data from {url}")
    except Exception as e:
        print(f"  Market report failed: {str(e)[:100]}")

if __name__ == "__main__":
    print("=" * 60)
    print("Apify Data Collection - Kids Supplements (US Market)")
    print("=" * 60)
    
    client = test_connection()
    if not client:
        print("Cannot connect to Apify, exiting.")
        sys.exit(1)
    
    # Collect Amazon products
    amazon_data = collect_amazon(client)
    print(f"\nTotal Amazon products: {len(amazon_data)}")
    
    if amazon_data:
        with open(os.path.join(OUTPUT_DIR, 'apify_amazon_products.json'), 'w', encoding='utf-8') as f:
            json.dump(amazon_data, f, ensure_ascii=False, indent=2)
        print(f"Saved to output/apify_amazon_products.json")
        
        # Show top products
        sorted_by_reviews = sorted(amazon_data, key=lambda x: x.get("review_count", 0), reverse=True)
        print("\n--- Top Products by Reviews ---")
        for i, p in enumerate(sorted_by_reviews[:10]):
            print(f"  {i+1}. [{p['brand']}] {p['title'][:60]} | ${p['price']} | {p['rating']}* ({p['review_count']} reviews) | {p['asin']}")
    
    # Collect TikTok
    tiktok_data = collect_tiktok(client)
    if tiktok_data:
        with open(os.path.join(OUTPUT_DIR, 'apify_tiktok.json'), 'w', encoding='utf-8') as f:
            json.dump(tiktok_data, f, ensure_ascii=False, indent=2)
    
    # Collect market report
    collect_market_report(client)
    
    print("\n" + "=" * 60)
    print("Collection complete!")
