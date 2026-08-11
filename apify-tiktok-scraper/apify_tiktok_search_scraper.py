#!/usr/bin/env python3
"""
Apify TikTok Search Scraper — 按搜索词采集热门视频
使用方法: python apify_tiktok_search_scraper.py <搜索词> [每词数量(默认50)]

⚠️  数量控制说明:
    resultsPerPage 是"每个搜索词"的结果数。
    总条数 ≈ 搜索词数量 × 每词数量
    例如: 2个搜索词 × 每词50 = 约100条（去重前）

示例:
  python apify_tiktok_search_scraper.py "juicer"
  python apify_tiktok_search_scraper.py "juicer" 30
  python apify_tiktok_search_scraper.py "juicer,cold press juicer" 25
"""

import sys
import os
import json
import math
from datetime import datetime
from pathlib import Path

try:
    from apify_client import ApifyClient
except ImportError:
    print("请先安装 apify-client: pip install apify-client")
    sys.exit(1)


# ---- 配置加载 ----

def get_apify_config():
    """从共享配置文件读取 API Token"""
    config_path = Path.home() / ".workbuddy" / "apify_config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def prompt_for_token():
    """引导用户输入 API Token 并保存"""
    print("⚠️  未找到 Apify 配置文件")
    token = input("请输入 Apify API Token: ").strip()
    if not token:
        print("❌ Token 不能为空")
        sys.exit(1)
    config_path = Path.home() / ".workbuddy" / "apify_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump({"api_token": token, "default_region": "US"}, f, indent=2)
    print("✅ Token 已保存到", config_path)
    return {"api_token": token}


def get_token():
    config = get_apify_config()
    if not config or not config.get("api_token"):
        config = prompt_for_token()
    return config["api_token"]


# ---- 核心采集函数 ----

def search_videos(client, search_queries, results_per_query=50,
                  with_subtitles=False, country_code=None):
    """
    按搜索词采集热门 TikTok 视频

    Args:
        client: ApifyClient 实例
        search_queries: 搜索词列表
        results_per_query: 每个搜索词的结果数（默认50）
        with_subtitles: 是否下载字幕转录（会额外消耗费用）
        country_code: 代理国家代码（如 "US"），None 表示不限

    Returns:
        list[dict]: 视频数据列表，按播放量降序排列

    ⚠️  费用说明:
        总条数（去重前）≈ len(search_queries) × results_per_query
        要控制费用，请减少搜索词数量或降低 results_per_query
    """

    # 预估数量提示
    estimated = len(search_queries) * results_per_query
    print(f"\n📱 开始搜索 TikTok...")
    print(f"   搜索词: {', '.join(search_queries)} (共 {len(search_queries)} 个)")
    print(f"   每词数量: {results_per_query}")
    print(f"   预估总数: {estimated} 条（去重后会减少）")
    print(f"   字幕: {'✅ 启用' if with_subtitles else '❌ 禁用'}")
    if country_code:
        print(f"   地区: {country_code}")

    run_input = {
        "searchQueries": search_queries,
        "searchSection": "",  # 综合排序 = 默认热门
        "resultsPerPage": results_per_query,
        "downloadSubtitlesOptions": (
            "DOWNLOAD_AND_TRANSCRIBE_VIDEOS_WITHOUT_SUBTITLES"
            if with_subtitles else "NEVER_DOWNLOAD_SUBTITLES"
        ),
        "proxyConfiguration": {
            "useApifyProxy": True
        }
    }

    if country_code:
        run_input["proxyCountryCode"] = country_code

    # 启动 Actor 并等待完成 —— 只执行一次
    print(f"\n🚀 启动 Actor (clockworks/tiktok-scraper)...")
    print(f"   本次只会创建 1 个 Actor Run")

    run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
    # 新版 apify-client 返回 Run 对象，用属性访问
    run_id = run.id if hasattr(run, 'id') else run.get('id')
    dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run.get('defaultDatasetId')
    print(f"   ✅ Actor Run ID: {run_id}")

    if not dataset_id:
        print("❌ Actor 未返回数据集 ID")
        return []

    # 提取并转换数据
    videos = []
    for item in client.dataset(dataset_id).iterate_items():
        if item.get("error"):
            continue  # 跳过错误条目

        meta = item.get("videoMeta") or {}
        author = item.get("authorMeta") or {}

        videos.append({
            "video_url": item.get("webVideoUrl"),
            "duration": meta.get("duration"),
            "profile_name": author.get("name"),
            "likes": item.get("diggCount"),
            "shares": item.get("shareCount"),
            "plays": item.get("playCount"),
            "description": item.get("text"),
            "subtitles": meta.get("transcriptionLink"),
            "hashtags": [h["name"] for h in (item.get("hashtags") or [])],
            "download_link": meta.get("downloadAddr"),
            "profile_url": author.get("profileUrl"),
            "create_time": item.get("createTimeISO"),
            "comment_count": item.get("commentCount"),
            "music_name": (item.get("musicMeta") or {}).get("musicName"),
        })

    # 按播放量降序排列
    videos.sort(key=lambda x: x["plays"] or 0, reverse=True)

    print(f"   ✅ 成功采集 {len(videos)} 条视频")
    return videos


# ---- 输出 ----

def save_results(videos, search_queries, results_per_query, output_dir=None):
    """保存结果到 JSON 和 CSV"""
    if output_dir is None:
        output_dir = Path(os.getenv("TIKTOK_OUTPUT_DIR", Path(__file__).resolve().parent / "output" / "tiktok_data"))
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "_".join(search_queries)[:60].replace(" ", "_")

    # JSON
    json_path = output_dir / f"tiktok_{safe_name}_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "search_queries": search_queries,
            "results_per_query": results_per_query,
            "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_videos": len(videos),
            "videos": videos
        }, f, indent=2, ensure_ascii=False)
    print(f"\n📄 JSON 已保存: {json_path}")

    # CSV
    csv_path = output_dir / f"tiktok_{safe_name}_{timestamp}.csv"
    import csv
    fieldnames = ["video_url", "duration", "profile_name", "likes", "shares",
                  "plays", "description", "hashtags", "download_link",
                  "create_time", "comment_count", "music_name", "subtitles"]
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for v in videos:
            row = dict(v)
            row["hashtags"] = ", ".join(row.get("hashtags") or [])
            writer.writerow(row)
    print(f"📊 CSV 已保存:  {csv_path}")

    return json_path, csv_path


def print_summary(videos, top_n=10):
    """打印 Top N 视频摘要"""
    print(f"\n{'='*80}")
    print(f"🏆 Top {min(top_n, len(videos))} 热门视频")
    print(f"{'='*80}")
    for i, v in enumerate(videos[:top_n], 1):
        plays = v["plays"] or 0
        likes = v["likes"] or 0
        if plays >= 1_000_000:
            plays_str = f"{plays/1_000_000:.1f}M"
        elif plays >= 1_000:
            plays_str = f"{plays/1_000:.1f}K"
        else:
            plays_str = str(plays)

        desc = (v["description"] or "")[:60]
        print(f"  {i:>2}. [{plays_str} ▶️  {likes} ❤️] {desc}")
        print(f"      By: @{v['profile_name']}  |  ⏱ {v['duration']}s")
        tags = v.get("hashtags") or []
        if tags:
            print(f"      Tags: {', '.join(tags[:5])}")
        print()


# ---- 主入口 ----

def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("📱 Apify TikTok 搜索视频采集器 v2.1")
        print("=" * 60)
        print()
        print("用法:")
        print('  python apify_tiktok_search_scraper.py "<搜索词>" [每词数量]')
        print()
        print("参数:")
        print('  <搜索词>     支持逗号分隔的多个搜索词')
        print('  [每词数量]   每个搜索词采集的数量（默认50）')
        print()
        print("⚠️  数量控制:")
        print('    总条数（去重前）≈ 搜索词数 × 每词数量')
        print('    例: 2个词 × 50条/词 = 约100条')
        print()
        print("示例:")
        print('  python apify_tiktok_search_scraper.py "juicer"')
        print('  python apify_tiktok_search_scraper.py "juicer" 30')
        print('  python apify_tiktok_search_scraper.py "juicer,cold press juicer" 25')
        sys.exit(0)

    # 解析参数
    search_input = sys.argv[1]
    search_queries = [q.strip() for q in search_input.split(",") if q.strip()]

    results_per_query = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    if results_per_query < 1:
        print("❌ 数量必须 >= 1")
        sys.exit(1)
    if results_per_query > 1000:
        print("⚠️  每词最多 1000 条，已自动调整为 1000")
        results_per_query = 1000

    # 预估费用提示
    estimated = len(search_queries) * results_per_query
    print(f"\n⚠️  预估采集数量: {estimated} 条（去重前）")
    print(f"    搜索词: {len(search_queries)} 个")
    print(f"    每词数量: {results_per_query}")
    if estimated > 200:
        print(f"    💡 提示: 预估超过 200 条，如需控制费用可减少搜索词或降低每词数量")

    # 获取 Token
    api_token = get_token()
    client = ApifyClient(api_token)

    # 执行搜索
    videos = search_videos(client, search_queries, results_per_query=results_per_query)

    if not videos:
        print("⚠️  未采集到视频数据，请检查搜索词或稍后重试")
        return

    # 保存结果
    json_path, csv_path = save_results(videos, search_queries, results_per_query)

    # 打印摘要
    print_summary(videos)

    # 统计
    total_plays = sum(v["plays"] or 0 for v in videos)
    total_likes = sum(v["likes"] or 0 for v in videos)
    avg_plays = total_plays // len(videos) if videos else 0
    print(f"📊 统计: {len(videos)} 条视频 | 总播放 {total_plays:,} | 平均播放 {avg_plays:,} | 总点赞 {total_likes:,}")


if __name__ == "__main__":
    main()
