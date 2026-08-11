---
name: tiktok-analytics
description: |
  TikTok流量和趋势数据采集技能。当用户需要以下任务时应使用此技能：
  - 采集TikTok相关标签播放量（#KidsSupplements等）
  - 分析TikTok爆款内容类型
  - 获取TikTok达人带货数据
  - 进行TikTok选品和流量分析
triggers:
  - TikTok流量
  - TikTok标签
  - TikTok数据
  - tiktok analytics
  - 标签播放量
  - TikTok爆款
  - 达人数据
agent_created: true
---

# TikTok Analytics v1.0

## 功能说明

本技能用于采集 TikTok 平台上的流量趋势和达人数据，支持选品调研报告中的 TikTok 流量分析维度。

## 数据来源

| 平台 | 费用 | 数据质量 | 推荐度 |
|------|------|----------|--------|
| **TikCreativeCenter** | 免费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **嘀嗒狗** | ¥299/月 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **PiPiADS** | ¥399/月 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **广大大** | ¥599/月 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 数据输出

### 1. 标签数据
```json
{
  "tag_name": "#KidsSupplements",
  "播放量": "420亿+",
  "视频数": "85万+",
  "涨速": "+32%/月",
  "热度趋势": "上升"
}
```

### 2. 爆款内容类型
```json
{
  "content_type": "软糖开箱",
  "代表视频": "URL",
  "播放量": "500万+",
  "互动率": "8.5%"
}
```

### 3. 达人数据
```json
{
  "达人名称": "Dr. Organic Mom",
  "粉丝量": "45万",
  "互动率": "6.2%",
  "带货能力": "优秀",
  "内容类型": ["成分科普", "产品测评", "日常分享"]
}
```

## 使用方式

### 方式一：TikCreativeCenter（免费）

```python
import requests
import json

# TikCreativeCenter API 示例
def get_tiktok_trends(keyword):
    """获取TikTok热门标签数据"""
    url = f"https://www.tiktokcreativesearch.com/api/v1/trending/hashtag"
    params = {"keyword": keyword}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()

# 示例调用
tags = [
    "#KidsSupplements",
    "#KidsMultivitamin",
    "#TurmericForKids",
    "#KidsEyeHealth",
    "#KidsProtein"
]

for tag in tags:
    data = get_tiktok_trends(tag)
    print(f"{tag}: {data}")
```

### 方式二：嘀嗒狗 API

```python
import requests

# 嘀嗒狗 API 配置
DIDADG_API_KEY = "your-api-key"  # 从 ~/.workbuddy/didadg_config.json 读取

def search_tiktok_trends(keyword, platform="tiktok"):
    """搜索TikTok趋势数据"""
    url = "https://api.didadg.com/v1/trends/search"

    payload = {
        "keyword": keyword,
        "platform": platform,
        "time_range": "30d"  # 最近30天
    }

    headers = {
        "Authorization": f"Bearer {DIDADG_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def get_product_videos(category):
    """获取指定品类的带货视频"""
    url = "https://api.didadg.com/v1/product/videos"

    params = {
        "category": category,
        "platform": "tiktok",
        "sort_by": "sales_volume"
    }

    headers = {"Authorization": f"Bearer {DIDADG_API_KEY}"}

    response = requests.get(url, params=params, headers=headers)
    return response.json()
```

### 方式三：WebScraper（网页采集）

当 API 不可用时，使用 Web Scraper 技能采集：

```python
# TikCreativeCenter 网页采集
TiktokCreaticeCenter_URL = "https://www.tiktokcreativesearch.com"

def scrape_tiktok_tags(keywords):
    """采集TikTok标签播放量"""
    results = []

    for keyword in keywords:
        url = f"{TiktokCreaticeCenter_URL}/hashtag/{keyword.replace('#', '')}"

        # 使用 Browser 或 WebFetch 采集
        # 详见 Browser Automation 技能

        results.append({
            "tag": keyword,
            "views": extract_views(html_content),
            "videos": extract_video_count(html_content)
        })

    return results
```

## 核心标签库

### 儿童保健品类目常用标签

| 标签 | 播放量级 | 内容类型 | 热度 |
|------|----------|----------|------|
| #KidsSupplements | 420亿+ | 综合 | 🔥🔥🔥🔥🔥 |
| #KidsMultivitamin | 120亿+ | 多维软糖 | 🔥🔥🔥🔥 |
| #TurmericForKids | 28亿+ | 姜黄功效 | 🔥🔥🔥🔥 |
| #KidsEyeHealth | 65亿+ | 护眼 | 🔥🔥🔥🔥 |
| #KidsProtein | 18亿+ | 蛋白 | 🔥🔥🔥 |
| #BlueLightProtection | 8亿+ | 护眼成分 | 🔥🔥🔥 |
| #ImmuneSupportKids | 35亿+ | 免疫 | 🔥🔥🔥🔥 |
| #NaturalVitamins | 12亿+ | 天然成分 | 🔥🔥🔥 |

## 爆款内容类型

| 内容类型 | 占比 | 平均播放 | 转化率 |
|----------|------|----------|--------|
| 软糖开箱 | 28% | 50万+ | 3.2% |
| 成分科普 | 22% | 80万+ | 2.8% |
| 儿科医生测评 | 18% | 150万+ | 5.5% |
| 家庭日常 | 20% | 30万+ | 1.8% |
| 对比测试 | 12% | 100万+ | 4.2% |

## 数据保存

采集的数据保存为 JSON 格式：

```json
{
  "采集时间": "2026-05-11",
  "目标市场": "美国",
  "类目": "儿童保健品",
  "标签数据": [...],
  "爆款内容": [...],
  "达人数据": [...]
}
```

保存路径：`./output/tiktok_data_{timestamp}.json`

## 配置说明

创建配置文件 `~/.workbuddy/didadg_config.json`：

```json
{
  "api_key": "your-didadg-api-key",
  "platform": "tiktok",
  "default_region": "US"
}
```

## 注意事项

1. TikCreativeCenter 为免费工具，但数据更新可能有延迟
2. 嘀嗒狗/PiPiADS 等付费工具数据更实时
3. TikTok 数据变化快，建议采集后尽快使用
4. 达人数据需要单独授权才能获取联系方式
