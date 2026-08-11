#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊商品采集技能 - 入口脚本 v4.0
用法:
    python amazon_scraper.py "搜索词" [数量] [排序方式]
示例:
    python amazon_scraper.py "birthday crochet gifts"
    python amazon_scraper.py "graduation gift" 50
    python amazon_scraper.py "wireless earbuds" 30 reviews
"""

import sys
import os
import subprocess


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_SCRIPT = os.path.join(BASE_DIR, "scripts", "amazon_scraper_core.py")


def auto_install_deps():
    """检查并自动安装缺失依赖"""
    deps = {
        "requests":       "requests>=2.28.0",
        "bs4":            "beautifulsoup4>=4.11.0",
        "openpyxl":       "openpyxl>=3.1.0",
        "PIL":            "Pillow>=10.0.0",
    }
    missing = []
    for mod, pkg in deps.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"[依赖检查] 正在安装缺失依赖: {', '.join(missing)}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + missing,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[依赖检查] 安装完成\n")
    else:
        print("[依赖检查] 所有依赖已就绪\n")


def print_usage():
    print("=" * 60)
    print("亚马逊商品采集技能 v4.0")
    print("=" * 60)
    print("用法:  python amazon_scraper.py \"搜索词\" [数量] [排序方式]")
    print()
    print("参数:")
    print("  搜索词    必填，完整短语，用双引号包裹")
    print("  数量      可选，1-100，默认 50")
    print("  排序方式  可选，sales（按销量，默认）/ reviews（按评论数）")
    print()
    print("示例:")
    print("  python amazon_scraper.py \"birthday crochet gifts\"")
    print("  python amazon_scraper.py \"graduation gift\" 50")
    print("  python amazon_scraper.py \"wireless earbuds\" 30 reviews")
    print("=" * 60)


def main():
    # ── 参数解析 ──────────────────────────────────────────────
    if len(sys.argv) < 2:
        print_usage()
        return 1

    keyword  = sys.argv[1].strip()
    count    = 50
    sort_by  = "sales"
    output_dir = ""

    if len(sys.argv) >= 3:
        arg2 = sys.argv[2]
        if arg2.isdigit():
            count = max(1, min(100, int(arg2)))
        elif arg2 in ("sales", "reviews"):
            sort_by = arg2
        else:
            print(f"[警告] 第2个参数 '{arg2}' 无效，使用默认值（数量=50）")

    if len(sys.argv) >= 4:
        arg3 = sys.argv[3]
        if arg3 in ("sales", "reviews"):
            sort_by = arg3
        else:
            print(f"[警告] 第3个参数 '{arg3}' 无效，使用默认排序 sales")

    # 支持第4个参数：输出目录（可选）
    if len(sys.argv) >= 5:
        output_dir = sys.argv[4].strip()

    if not keyword:
        print("[错误] 搜索词不能为空")
        return 1

    # ── 依赖检查 ──────────────────────────────────────────────
    print("=" * 60)
    print("亚马逊商品采集技能 v4.0")
    print("=" * 60)
    auto_install_deps()

    # ── 打印任务摘要 ──────────────────────────────────────────
    print(f"搜索词  : {keyword}")
    print(f"采集数量: {count} 个")
    print(f"排序方式: {sort_by}")
    print("-" * 60)

    # ── 调用核心脚本 ──────────────────────────────────────────
    if not os.path.exists(CORE_SCRIPT):
        print(f"[错误] 找不到核心脚本: {CORE_SCRIPT}")
        return 1

    env = os.environ.copy()
    # 输出目录：通过环境变量或第4个参数传递给核心脚本
    # 如果未指定，核心脚本会默认使用 桌面/YYYY-MM-DD/
    output_dir = getattr(output_dir, 'strip', lambda: '')(output_dir) if 'output_dir' in dir() else ''
    if output_dir:
        env["SKILL_OUTPUT_DIR"] = output_dir

    cmd_args = [sys.executable, CORE_SCRIPT, keyword, sort_by, str(count)]
    if output_dir:
        cmd_args.append(output_dir)

    result = subprocess.run(
        cmd_args,
        cwd=BASE_DIR,
        env=env,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
