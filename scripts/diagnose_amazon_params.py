"""
Apify Amazon Scraper 深度参数诊断
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.environ['APIFY_API_TOKEN'] = os.getenv("APIFY_API_TOKEN", "")
if not os.environ['APIFY_API_TOKEN']:
    print("ERROR: APIFY_API_TOKEN 环境变量未设置")
    sys.exit(1)

from apify_client import ApifyClient
client = ApifyClient(os.environ['APIFY_API_TOKEN'])

actor_id = "junglee/free-amazon-product-scraper"

# 1. 获取 Actor 的输入 schema
print("=" * 60)
print("Actor Input Schema")
print("=" * 60)
actor_info = client.actor(actor_id).get()
print(f"Title: {actor_info.get('title')}")
print(f"Description: {actor_info.get('description', 'N/A')[:200]}")

# Input schema
input_schema = actor_info.get('input', {})
print(f"\nInput properties:")
if isinstance(input_schema, dict) and 'properties' in input_schema:
    for key, prop in input_schema['properties'].items():
        req = "required" if key in input_schema.get('required', []) else "optional"
        desc = prop.get('description', '')[:80] if isinstance(prop, dict) else ''
        print(f"  {key} ({req}): {prop.get('title', '')[:60]} - {desc}")

# 2. 测试不同的参数组合
print("\n" + "=" * 60)
print("测试参数组合")
print("=" * 60)

test_cases = [
    {
        "name": "测试1: searchUrls",
        "input": {"searchUrls": [{"url": "https://www.amazon.com/s?k=kids+vitamins+gummies"}], "maxItems": 3}
    },
    {
        "name": "测试2: categoryUrls (BSR category)",
        "input": {"categoryUrls": [{"url": "https://www.amazon.com/Best-Sellers/zgbs/hpc/3775111"}], "maxItems": 3}
    },
    {
        "name": "测试3: categoryUrls (search result)",
        "input": {"categoryUrls": [{"url": "https://www.amazon.com/s?k=kids+vitamins+gummies&s=review-rank"}], "maxItems": 3}
    },
    {
        "name": "测试4: 纯search参数",
        "input": {"search": "kids vitamins gummies", "maxItems": 3, "proxyConfiguration": {"useApifyProxy": True}}
    },
    {
        "name": "测试5: startUrls",
        "input": {"startUrls": [{"url": "https://www.amazon.com/s?k=kids+vitamins+gummies"}], "maxItems": 3}
    },
    {
        "name": "测试6: keyword + domain",
        "input": {"keyword": "kids vitamins gummies", "domain": "com", "maxItems": 3}
    },
    {
        "name": "测试7: 最简参数",
        "input": {"categoryUrls": [{"url": "https://www.amazon.com/s?k=kids+vitamins"}], "maxItems": 3, "proxyConfiguration": {"useApifyProxy": True}}
    },
]

for tc in test_cases:
    print(f"\n▶ {tc['name']}")
    try:
        run = client.actor(actor_id).start(run_input=tc['input'], wait_for_finish=60)
        status = run.get('status', 'N/A')
        print(f"  Status: {status}")
        if status == 'SUCCEEDED':
            items = list(client.dataset(run['defaultDatasetId']).iterate_items())
            print(f"  ✅ Items: {len(items)}")
            if items:
                item = items[0]
                print(f"  title: {item.get('title', 'N/A')[:80]}")
                print(f"  asin: {item.get('asin', 'N/A')}")
                print(f"  price: {item.get('price', 'N/A')}")
                print(f"  stars: {item.get('stars', 'N/A')}")
        elif status == 'FAILED':
            # 获取日志
            try:
                log = client.run(run['id']).log().get()
                if log:
                    lines = [l for l in str(log).split('\n') if 'error' in l.lower() or 'Error' in l][:3]
                    for line in lines:
                        print(f"  Log: {line[:150]}")
            except:
                pass
    except Exception as e:
        # 尝试直接获取错误信息
        err_msg = str(e)[:200]
        print(f"  ❌ Error: {err_msg}")

# 3. 测试 epctex/amazon-scraper - 它是 paid 但有不同参数
print("\n" + "=" * 60)
print("测试 epctex/amazon-scraper 参数")
print("=" * 60)
try:
    info = client.actor("epctex/amazon-scraper").get()
    schema = info.get('input', {}).get('properties', {})
    print("Input keys:", list(schema.keys())[:15])
except Exception as e:
    print(f"Error: {e}")

print("\n诊断完成！")
