#!/usr/bin/env python3
"""
重新采集 TikTok Juicer 视频 —— 开启 shouldDownloadVideos 获取下载链接
严格数量控制：1 个搜索词 × 50 条 = 约 50 条（去重前）
"""

import os
import sys
import json
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
# 严格数量控制：1 个搜索词 × 50 条 = 约 50 条
# ============================================================

SEARCH_QUERIES = ["juicer"]  # 只用1个搜索词
RESULTS_PER_QUERY = 50       # 50条 → 总共约50条

estimated_total = len(SEARCH_QUERIES) * RESULTS_PER_QUERY
print(f"\n{'='*60}")
print(f"📱 TikTok Juicer 视频采集（含下载链接）")
print(f"{'='*60}")
print(f"   搜索词: {', '.join(SEARCH_QUERIES)} (共 {len(SEARCH_QUERIES)} 个)")
print(f"   每词数量: {RESULTS_PER_QUERY}")
print(f"   预估总数: {estimated_total} 条")
print(f"   shouldDownloadVideos: ✅ 已开启（付费 Add-on）")
print(f"   预估额外费用: ~$0.07（视频下载附加费）")
print(f"{'='*60}")

client = ApifyClient(API_TOKEN)

run_input = {
    "searchQueries": SEARCH_QUERIES,
    "searchSection": "",           # 综合排序 = 默认热门
    "resultsPerPage": RESULTS_PER_QUERY,
    "shouldDownloadVideos": True,  # ⚠️ 付费 Add-on：开启视频下载
    "shouldDownloadCovers": False,
    "shouldDownloadSubtitles": False,
    "downloadSubtitlesOptions": "NEVER_DOWNLOAD_SUBTITLES",
    "proxyConfiguration": {"useApifyProxy": True},
}

print(f"\n🚀 启动 Actor (clockworks/tiktok-scraper)...")
print(f"   本次只创建 1 个 Actor Run")

run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
run_id = run.id if hasattr(run, 'id') else run.get('id')
dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run.get('defaultDatasetId')
print(f"   ✅ Actor Run ID: {run_id}")
print(f"   Dataset ID: {dataset_id}")

if not dataset_id:
    print("❌ Actor 未返回数据集 ID")
    sys.exit(1)

# 提取数据
print("📥 正在提取数据...")
videos = []
error_count = 0

for item in client.dataset(dataset_id).iterate_items():
    if item.get("error"):
        error_count += 1
        continue

    video_meta = item.get("videoMeta") or {}
    author_meta = item.get("authorMeta") or {}

    # 检查 videoMeta 中是否有 downloadAddr
    download_addr = video_meta.get("downloadAddr")
    # 也检查 mediaUrls 作为备选
    media_urls = item.get("mediaUrls") or []

    videos.append({
        "video_url": item.get("webVideoUrl"),
        "duration": video_meta.get("duration"),
        "profile_name": author_meta.get("name"),
        "likes": item.get("diggCount"),
        "shares": item.get("shareCount"),
        "plays": item.get("playCount"),
        "description": item.get("text"),
        "hashtags": [h["name"] for h in (item.get("hashtags") or [])],
        "download_link": download_addr,  # 主要来源
        "media_urls": media_urls,        # 备选来源
        "comment_count": item.get("commentCount"),
        "create_time": item.get("createTimeISO"),
        "search_query": item.get("searchQuery"),
        # videoMeta 完整字段（调试用）
        "video_definition": video_meta.get("definition"),
        "video_format": video_meta.get("format"),
        "cover_url": video_meta.get("coverUrl"),
    })

# 按播放量降序排列
videos.sort(key=lambda v: v["plays"] or 0, reverse=True)

if error_count:
    print(f"   ⚠️ 跳过 {error_count} 条错误条目")
print(f"   ✅ 成功采集 {len(videos)} 条视频")

# 检查下载链接可用率
has_download = sum(1 for v in videos if v.get("download_link"))
has_media = sum(1 for v in videos if v.get("media_urls"))
print(f"\n📊 下载链接统计:")
print(f"   videoMeta.downloadAddr 有值: {has_download}/{len(videos)}")
print(f"   mediaUrls 非空: {has_media}/{len(videos)}")

# 保存本地备份
backup_dir = Path(os.getenv("TIKTOK_OUTPUT_DIR", Path(__file__).resolve().parent / "output" / "tiktok_data"))
backup_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = backup_dir / f"tiktok_juicer_with_download_{timestamp}.json"
with open(backup_path, "w", encoding="utf-8") as f:
    json.dump({
        "search_queries": SEARCH_QUERIES,
        "results_per_query": RESULTS_PER_QUERY,
        "shouldDownloadVideos": True,
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_videos": len(videos),
        "download_link_stats": {
            "has_download_addr": has_download,
            "has_media_urls": has_media,
        },
        "videos": videos,
    }, f, indent=2, ensure_ascii=False)
print(f"   📄 本地备份: {backup_path}")

# 打印 Top 10
def fmt(n):
    if n is None: return "N/A"
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)

print(f"\n🏆 Top 10 热门视频:")
for i, v in enumerate(videos[:10], 1):
    desc = (v["description"] or "")[:60]
    dl = "✅有下载" if v.get("download_link") else "❌无下载"
    print(f"  {i:>2}. [{fmt(v['plays'])} ▶ | {fmt(v['likes'])} ❤] {desc}")
    print(f"      @{v['profile_name']} | ⏱{v['duration']}s | {dl}")

# 同时保存一份精简的仅下载链接映射（方便后续使用）
if has_download > 0:
    download_map = {}
    for v in videos:
        if v.get("download_link"):
            download_map[v["video_url"]] = v["download_link"]
    map_path = backup_dir / f"tiktok_juicer_download_map_{timestamp}.json"
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(download_map, f, indent=2, ensure_ascii=False)
    print(f"\n📄 下载链接映射已保存: {map_path}")
    print(f"   包含 {len(download_map)} 条视频的下载链接")
