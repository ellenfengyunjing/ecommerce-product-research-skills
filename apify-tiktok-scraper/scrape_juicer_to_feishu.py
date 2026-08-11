#!/usr/bin/env python3
"""
采集 TikTok Juicer/榨汁机爆款视频并写入飞书多维表格
数量控制：resultsPerPage 是"每个搜索词"的数量，总条数 ≈ 搜索词数 × resultsPerPage
"""

import os
import sys
import json
import math
from pathlib import Path
from datetime import datetime

# ---- 加载 .env ----
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
if not API_TOKEN:
    print("❌ 未找到 APIFY_API_TOKEN，请检查 .env 文件")
    sys.exit(1)

from apify_client import ApifyClient

# ============================================================
# 1. 采集 TikTok 视频 —— 严格控制数量，只执行一次
# ============================================================

# ⚠️ 关键：resultsPerPage 是"每个搜索词"返回的数量
# 总条数 ≈ len(SEARCH_QUERIES) × RESULTS_PER_QUERY
# 要控制总费用，请控制搜索词数量或降低 RESULTS_PER_QUERY

SEARCH_QUERIES = ["juicer", "cold press juicer"]  # 2个搜索词
RESULTS_PER_QUERY = 25  # 每个词25条 → 总共约50条（去重前）
# 如需精确控制为50条总共，建议只保留1个搜索词并设置 RESULTS_PER_QUERY = 50

# 计算预估总数
estimated_total = len(SEARCH_QUERIES) * RESULTS_PER_QUERY
print(f"\n{'='*60}")
print(f"📱 TikTok Juicer/榨汁机爆款视频采集")
print(f"{'='*60}")
print(f"   搜索词: {', '.join(SEARCH_QUERIES)} (共 {len(SEARCH_QUERIES)} 个)")
print(f"   每词数量: {RESULTS_PER_QUERY}")
print(f"   预估总数: {estimated_total} 条（去重后会减少）")
print(f"   ⚠️  本脚本只执行一次，请确认参数后按回车继续...")
input()

client = ApifyClient(API_TOKEN)

run_input = {
    "searchQueries": SEARCH_QUERIES,
    "searchSection": "",  # 综合排序 = 默认热门
    "resultsPerPage": RESULTS_PER_QUERY,
    "downloadSubtitlesOptions": "NEVER_DOWNLOAD_SUBTITLES",  # 禁用字幕以节省费用
    "proxyConfiguration": {"useApifyProxy": True},
}

print(f"\n🚀 启动 Actor (clockworks/tiktok-scraper)...")
print(f"   本次只会创建 1 个 Actor Run，请等待完成...")

run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
run_id = run.id if hasattr(run, 'id') else run.get('id')
dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run.get('defaultDatasetId')
print(f"   ✅ Actor Run ID: {run_id}")

if not dataset_id:
    print("❌ Actor 未返回数据集 ID")
    sys.exit(1)

print("📥 正在提取数据...")
videos = []
error_count = 0

for item in client.dataset(dataset_id).iterate_items():
    if item.get("error"):
        error_count += 1
        continue

    video_meta = item.get("videoMeta") or {}
    author_meta = item.get("authorMeta") or {}

    videos.append({
        "video_url": item.get("webVideoUrl"),
        "duration": video_meta.get("duration"),
        "profile_name": author_meta.get("name"),
        "likes": item.get("diggCount"),
        "shares": item.get("shareCount"),
        "plays": item.get("playCount"),
        "description": item.get("text"),
        "subtitles": video_meta.get("transcriptionLink"),
        "hashtags": [h["name"] for h in (item.get("hashtags") or [])],
        "download_link": video_meta.get("downloadAddr"),
        "comment_count": item.get("commentCount"),
        "create_time": item.get("createTimeISO"),
        "search_query": item.get("searchQuery"),
    })

# 按播放量降序排列
videos.sort(key=lambda v: v["plays"] or 0, reverse=True)

if error_count:
    print(f"   ⚠️ 跳过 {error_count} 条错误条目")
print(f"   ✅ 成功采集 {len(videos)} 条视频")

# ---- 保存本地 JSON 备份 ----
backup_dir = Path(os.getenv("TIKTOK_OUTPUT_DIR", Path(__file__).resolve().parent / "output" / "tiktok_data"))
backup_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = backup_dir / f"tiktok_juicer_{timestamp}.json"
with open(backup_path, "w", encoding="utf-8") as f:
    json.dump({
        "search_queries": SEARCH_QUERIES,
        "results_per_query": RESULTS_PER_QUERY,
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_videos": len(videos),
        "videos": videos,
    }, f, indent=2, ensure_ascii=False)
print(f"   📄 本地备份: {backup_path}")

# ---- 打印 Top 10 ----
def fmt(n):
    if n is None: return "N/A"
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)

print(f"\n🏆 Top 10 热门视频:")
for i, v in enumerate(videos[:10], 1):
    desc = (v["description"] or "")[:60]
    print(f"  {i:>2}. [{fmt(v['plays'])} ▶ | {fmt(v['likes'])} ❤] {desc}")
    print(f"      @{v['profile_name']} | ⏱{v['duration']}s | 💬{v['comment_count'] or 0}")

# ============================================================
# 2. 写入飞书多维表格
# ============================================================

print(f"\n{'='*60}")
print(f"📝 开始写入飞书多维表格...")
print(f"{'='*60}")

# 去重（按 video_url 去重）
seen = set()
unique_videos = []
for v in videos:
    url = v.get("video_url") or ""
    if url and url not in seen:
        seen.add(url)
        unique_videos.append(v)

print(f"   去重后: {len(unique_videos)} 条（原始 {len(videos)} 条）")

# 分批写入（每批10条）
BATCH_SIZE = 10
total_written = 0
total_errors = 0

for batch_start in range(0, len(unique_videos), BATCH_SIZE):
    batch = unique_videos[batch_start:batch_start + BATCH_SIZE]
    records_json = []

    for v in batch:
        fields = {
            "fldClKoodR": v.get("video_url") or "",
            "fldBooPG3h": str(v.get("plays") or ""),
            "fldJzDREO0": str(v.get("likes") or ""),
            "fldfOASqJn": str(v.get("shares") or ""),
            "fld26w9OmT": str(v.get("comment_count") or ""),
            "fldMqeJGqK": v.get("description") or "",
            "fldrRfZ2Fe": ", ".join(v.get("hashtags") or []),
            "flda7V8tof": v.get("download_link") or "",
        }
        fields = {k: v_val for k, v_val in fields.items() if v_val}
        records_json.append({"fields": fields})

    import subprocess
    cmd = [
        "lark-cli", "base", "+record-batch-create",
        "--as", "user",
        "--base-token", os.getenv("FEISHU_BASE_TOKEN", ""),
        "--table-id", os.getenv("FEISHU_TABLE_ID", ""),
        "--records", json.dumps(records_json, ensure_ascii=False),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=60)

    if result.returncode == 0:
        try:
            resp = json.loads(result.stdout)
            if resp.get("ok"):
                created = len(resp.get("data", {}).get("records", []))
                total_written += created
                print(f"   ✅ 批次 {batch_start//BATCH_SIZE + 1}: 写入 {created} 条")
            else:
                total_errors += len(batch)
                print(f"   ❌ 批次 {batch_start//BATCH_SIZE + 1} 失败: {resp.get('error', result.stdout[:200])}")
        except json.JSONDecodeError:
            total_errors += len(batch)
            print(f"   ❌ 批次 {batch_start//BATCH_SIZE + 1} 解析失败: {result.stdout[:200]}")
    else:
        total_errors += len(batch)
        print(f"   ❌ 批次 {batch_start//BATCH_SIZE + 1} 命令失败: {result.stderr[:200]}")

print(f"\n{'='*60}")
print(f"📊 写入完成!")
print(f"   成功写入: {total_written} 条")
print(f"   失败: {total_errors} 条")
print(f"   ????: {os.getenv("FEISHU_BASE_URL", "https://feishu.cn/base")}?table={os.getenv("FEISHU_TABLE_ID", "")}" + (f"&view={os.getenv("FEISHU_VIEW_ID", "")}" if os.getenv("FEISHU_VIEW_ID", "") else ""))
print(f"{'='*60}")
