"""
快速调试 Amazon Actor 执行状态
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.environ['APIFY_API_TOKEN'] = os.getenv("APIFY_API_TOKEN", "")
if not os.environ['APIFY_API_TOKEN']:
    print("ERROR: APIFY_API_TOKEN 环境变量未设置")
    sys.exit(1)
from apify_client import ApifyClient
client = ApifyClient(os.environ['APIFY_API_TOKEN'])

actor_id = "junglee/free-amazon-product-scraper"

# 先启动 run，不等待
run_input = {
    "categoryUrls": [{"url": "https://www.amazon.com/s?k=kids+vitamins+gummies&s=review-rank"}],
    "maxItems": 20,
    "proxyConfiguration": {"useApifyProxy": True},
}

print("Starting Actor...")
run = client.actor(actor_id).start(run_input=run_input)
run_id = run.get('id')
print(f"Run ID: {run_id}")
print(f"Status: {run.get('status')}")

# 手动轮询状态
print("\nPolling status...")
for i in range(20):  # 最多等 300 秒
    time.sleep(15)
    status_info = client.run(run_id).get()
    status = status_info.get('status', 'UNKNOWN')
    stats = status_info.get('stats', {})
    print(f"  [{i*15}s] Status: {status} | Input: {stats.get('inputBodyLen', '?')} Items: {stats.get('outputBodyLen', '?')}")
    
    if status in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
        break

final = client.run(run_id).get()
print(f"\nFinal Status: {final.get('status')}")
print(f"Finished At: {final.get('finishedAt')}")

if final.get('status') == 'SUCCEEDED':
    items = list(client.dataset(final['defaultDatasetId']).iterate_items())
    print(f"✅ Items: {len(items)}")
    for item in items[:3]:
        print(f"  - {item.get('title', 'N/A')[:80]}")
        print(f"    ASIN: {item.get('asin')} | ${item.get('price', {})} | ⭐{item.get('stars')}")
else:
    print(f"❌ Run failed: {final.get('errorMessage', 'Unknown error')[:200]}")
    
    # 检查日志
    try:
        log = client.run(run_id).log().get()
        if log:
            lines = [l for l in str(log).split('\n') if 'error' in l.lower() or 'Error' in l or 'ERROR' in l]
            for line in lines[:5]:
                print(f"  Log: {line[:200]}")
    except Exception as e:
        print(f"  Log unavailable: {e}")
