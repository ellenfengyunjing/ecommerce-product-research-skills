---
name: apify-tiktok-scraper
description: |
  使用 Apify API 的 clockworks/tiktok-scraper Actor，按搜索词采集 TikTok 热门视频数据。
  当用户需要以下任务时应使用此技能：
  - 按搜索关键词采集 TikTok 热门视频
  - 获取视频的点赞/分享/播放量等互动数据
  - 采集视频字幕、标签、下载链接
  - TikTok 视频数据分析和趋势研究
triggers:
  - apify tiktok
  - tiktok apify
  - 采集TikTok
  - TikTok搜索
  - TikTok视频
  - TikTok热门视频
  - tiktok scraper
agent_created: true
---

# Apify TikTok 搜索视频采集器 v2.0

## 功能说明

本技能使用 **Apify `clockworks/tiktok-scraper` Actor** 的搜索功能，按搜索词采集 TikTok 上热度较高的视频数据。

与 `apify-amazon-scraper` 共享同一个 Apify API Token 配置。

## 前提条件

### 1. 获取 Apify API Token

1. 访问 [apify.com](https://apify.com) 注册/登录账号
2. 进入 [Settings → Integrations](https://console.apify.com/settings/integrations) 获取 API Token
3. 首次使用有 **$5 免费额度**

### 2. 配置 API Token

保存到 `~/.workbuddy/apify_config.json`（与 `apify-amazon-scraper` 共享）：

```json
{
  "api_token": "your-apify-api-token-here",
  "default_region": "US"
}
```

---

## 核心功能：按搜索词采集热门视频

## 调研链路成本规则

当本技能被 `amazon-product-researcher` 调用时，默认遵守以下规则：

1. 每轮 TikTok 验证只启动 1 个 `clockworks/tiktok-scraper` Actor Run。
2. 优先使用 1 个核心搜索词，`resultsPerPage` 控制在报告所需样本量内；不得把近义词拆成多个 Actor Run 重复采集。
3. 如果需要多个搜索词，优先放在同一个 `searchQueries` 数组内，并明确计算总条数：`搜索词数量 × resultsPerPage`。
4. 默认禁用字幕和视频下载，只有分析内容脚本、口播结构或素材复用时才启用。
5. 只有首轮样本量不足、结果偏题或关键字段缺失时，才追加第二个 Actor Run。
6. 输出给报告的数据必须包含 `collector=clockworks/tiktok-scraper`、Run ID、搜索词、采集时间、样本量和视频 URL。
7. 空结果、报错、未下载字幕等缺失信息不进入最终报告。

### 采集字段

| 字段 | 来源 | 说明 |
|------|------|------|
| **Video URL** | `webVideoUrl` | 视频在 TikTok 上的观看链接 |
| **Duration** | `videoMeta.duration` | 视频时长（秒） |
| **Profile Name** | `authorMeta.name` | 发布者用户名 |
| **Likes** | `diggCount` | 点赞数 |
| **Shares** | `shareCount` | 分享数 |
| **Plays** | `playCount` | 播放量 |
| **Video Description** | `text` | 视频文案/描述 |
| **Video Subtitles** | `videoMeta.transcriptionLink` | 字幕转录（需启用字幕下载） |
| **Hashtags Used** | `hashtags[].name` | 视频使用的所有标签 |
| **Video Download Link** | `videoMeta.downloadAddr` | 视频下载地址（付费功能） |

---

## Actor 参数说明

### 核心参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `searchQueries` | array | **搜索关键词**，支持多个搜索词。TikTok 上有效的任意查询均可 |
| `searchSection` | string | `""` = 综合排序（默认热门），`"/video"` = 仅视频 |
| `resultsPerPage` | int | ⚠️ **每个搜索词**返回的视频数量，默认 50，最大 1,000,000 |
| `proxyCountryCode` | string | 代理国家代码，如 `"US"`, `"None"` |

### 排序参数（付费）

| 参数 | 类型 | 选项 | 说明 |
|------|------|------|------|
| `videoSearchSorting` 💰 | string | `MOST_RELEVANT` / `MOST_LIKED` / `LATEST` | 视频排序方式 |

### 字幕参数

| 参数 | 类型 | 选项 | 说明 |
|------|------|------|------|
| `downloadSubtitlesOptions` | string | `NEVER_DOWNLOAD_SUBTITLES` / `DOWNLOAD_SUBTITLES` / `DOWNLOAD_AND_TRANSCRIBE_VIDEOS_WITHOUT_SUBTITLES` / `TRANSCRIBE_ALL_VIDEOS` | 字幕处理方式 |

> 💰 = 付费功能，需在 Apify 平台购买相应附加组件

---

## ⚠️ 重要：数量控制说明

**`resultsPerPage` 是"每个搜索词"的结果数，不是总数！**

```
总条数（去重前）≈ 搜索词数量 × resultsPerPage

例: 4个搜索词 × 50条/词 = 约 200 条（去重后通常会减少）
```

**控制费用的方法：**
1. **减少搜索词数量** — 建议先用 1-2 个核心词测试
2. **降低 `resultsPerPage`** — 根据需要的总量平摊到每个搜索词
3. **禁用字幕** — `NEVER_DOWNLOAD_SUBTITLES` 可节省额外费用

---

## 使用方式

### 快速示例（单搜索词，50条）

```python
from apify_client import ApifyClient
import json

client = ApifyClient("your-api-token")

# 搜索"kids supplements"，采集50条（1个词 × 50条 = 约50条）
run_input = {
    "searchQueries": ["kids supplements"],  # 只放1个搜索词
    "searchSection": "",                    # 空 = 综合排序（默认热门）
    "resultsPerPage": 50,                   # 该词采集50条
    "downloadSubtitlesOptions": "NEVER_DOWNLOAD_SUBTITLES",  # 禁用字幕节省费用
    "proxyConfiguration": {
        "useApifyProxy": True
    }
}

run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)

# 新版 apify-client 返回 Run 对象，用属性访问
run_id = run.id if hasattr(run, 'id') else run.get('id')
dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run.get('defaultDatasetId')

videos = []
for item in client.dataset(dataset_id).iterate_items():
    if item.get("error"):
        continue
    videos.append({
        "video_url": item.get("webVideoUrl"),
        "duration": item.get("videoMeta", {}).get("duration"),
        "profile_name": item.get("authorMeta", {}).get("name"),
        "likes": item.get("diggCount"),
        "shares": item.get("shareCount"),
        "plays": item.get("playCount"),
        "description": item.get("text"),
        "subtitles": item.get("videoMeta", {}).get("transcriptionLink"),
        "hashtags": [h["name"] for h in (item.get("hashtags") or [])],
        "download_link": item.get("videoMeta", {}).get("downloadAddr"),
    })

videos.sort(key=lambda x: x["plays"] or 0, reverse=True)
print(f"采集到 {len(videos)} 条视频")
```

### 多搜索词批量采集（注意总量！）

```python
search_keywords = ["kids vitamins", "kids supplements review", "best protein for kids"]

# 3个词 × 30条/词 = 约90条（去重前）
run_input = {
    "searchQueries": search_keywords,
    "searchSection": "/video",
    "resultsPerPage": 30,
    "downloadSubtitlesOptions": "NEVER_DOWNLOAD_SUBTITLES",
    "proxyConfiguration": {"useApifyProxy": True}
}

run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
# ... 处理结果同上
```

---

## 完整脚本

保存为 `apify_tiktok_search_scraper.py`：

```python
#!/usr/bin/env python3
"""
Apify TikTok Search Scraper — 按搜索词采集热门视频
使用方法: python apify_tiktok_search_scraper.py <搜索词> [数量(默认50)]

示例:
  python apify_tiktok_search_scraper.py "kids supplements"
  python apify_tiktok_search_scraper.py "skincare routine" 100
  python apify_tiktok_search_scraper.py "home workout,protein shake,yoga tips" 80
"""

import sys
import os
import json
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

def search_videos(client, search_queries, max_results=50,
                  with_subtitles=True, country_code=None):
    """
    按搜索词采集热门 TikTok 视频

    Args:
        client: ApifyClient 实例
        search_queries: 搜索词列表
        max_results: 每个搜索词的最大结果数（默认50）
        with_subtitles: 是否下载字幕转录
        country_code: 代理国家代码（如 "US"），None 表示不限

    Returns:
        list[dict]: 视频数据列表，按播放量降序排列
    """

    run_input = {
        "searchQueries": search_queries,
        "searchSection": "",  # 综合排序 = 默认热门
        "resultsPerPage": max_results,
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

    # 预估数量提示
    estimated = len(search_queries) * max_results
    print(f"\n📱 开始搜索 TikTok...")
    print(f"   搜索词: {', '.join(search_queries)} (共 {len(search_queries)} 个)")
    print(f"   每词数量: {max_results}")
    print(f"   预估总数: {estimated} 条（去重后会减少）")
    print(f"   字幕: {'✅ 启用' if with_subtitles else '❌ 禁用'}")
    if country_code:
        print(f"   地区: {country_code}")

    # 启动 Actor 并等待完成 —— 只创建 1 个 Run
    print(f"\n🚀 启动 Actor (clockworks/tiktok-scraper)...")
    run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
    run_id = run.id if hasattr(run, 'id') else run.get('id')
    print(f"   ✅ Actor Run ID: {run_id}")

    dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run.get('defaultDatasetId')
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
            # 额外辅助字段
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
        output_dir = Path(__file__).resolve().parent / "output" / "tiktok_data"
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
```

---

## 配置说明

### Token 共享

所有 Apify Skills 共享同一份配置：

| Skill | 配置文件 |
|-------|----------|
| `apify-amazon-scraper` | ✅ `~/.workbuddy/apify_config.json` |
| `apify-market-scraper` | ✅ 同上 |
| `apify-tiktok-scraper` | ✅ 同上 |

### 额度估算

| 采集任务 | 预估消耗 | 备注 |
|----------|----------|------|
| 1个搜索词 × 50条视频 | ~$0.3 | 推荐：控制数量的最佳方式 |
| 1个搜索词 × 100条视频 | ~$0.6 | 扩大采集量 |
| 4个搜索词 × 50条视频 | ~$1.2-2.0 | ⚠️ 实际约 200 条（去重前） |
| **免费额度** | **$5** | **建议先用 1 个词测试** |

> ⚠️ **数量陷阱**：4 个搜索词 × 50 条/词 = **200 条**（不是 50 条）！
> 💡 实际消耗取决于视频数据的复杂度和是否启用字幕，以上为估算值。

---

## 注意事项

1. **数量控制（最重要）**：`resultsPerPage` 是**每个搜索词**的数量。总条数 ≈ 搜索词数 × resultsPerPage。要控制费用，请减少搜索词或降低每词数量
2. **搜索词格式**：使用自然语言搜索词，如 `"kids vitamins"`, `"morning skincare"` — 就像在 TikTok 搜索框中输入一样
3. **热度排序**：设置 `searchSection: ""` 使用 TikTok 默认的综合排序（按热度），无需付费参数即可获取热门视频
4. **视频下载**：`downloadAddr` 需要启用付费的 `shouldDownloadVideos`，否则该字段可能为空
5. **字幕**：默认建议禁用字幕 (`NEVER_DOWNLOAD_SUBTITLES`) 以节省费用。如需转录再启用 `DOWNLOAD_AND_TRANSCRIBE_VIDEOS_WITHOUT_SUBTITLES`
6. **地区**：通过 `proxyCountryCode` 可限定搜索某个国家/地区的内容（如 `"US"` 仅美国）
7. **Token 安全**：配置文件存储在 `~/.workbuddy/` 下，不会提交到 Git
8. **只执行一次**：本 Skill 的脚本只会创建 **1 个 Actor Run**。如果意外执行两次会产生双倍费用

---

## 文件结构

```
apify-tiktok-scraper/
├── SKILL.md                          # 本文件（Skill 说明文档）
├── .env.example                      # 环境变量示例
├── apify_tiktok_search_scraper.py    # 主脚本（搜索采集）
└── scripts/                          # 辅助脚本目录
```

---

## 在 WorkBuddy 中使用

配置完成后，直接告诉 WorkBuddy：

```
帮我搜索 TikTok 上 "kids supplements" 的视频，采集50条热门视频
```

```
查一下 TikTok 上 vitamin gummies 的爆款视频数据
```

> 💡 建议明确指定"总共X条"，系统会自动用 1 个搜索词 + `resultsPerPage=X` 来控制数量

系统会自动调用本 Skill，使用 `clockworks/tiktok-scraper` 的 `searchQueries` 功能完成采集！
