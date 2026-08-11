# Amazon Product Scraper v4.0 - PowerShell 启动器
# 用法: .\run_amazon_scraper.ps1 "搜索词" [数量] [排序方式]

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  亚马逊商品采集技能 v4.0  |  PowerShell 启动器" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ── 检查 Python ──────────────────────────────────────────────
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] 未检测到 Python，请先安装 Python 3.8+ 并加入 PATH" -ForegroundColor Red
    Write-Host "        下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按 Enter 退出"
    exit 1
}

# ── 检查参数 ──────────────────────────────────────────────────
if ($args.Count -eq 0) {
    Write-Host "用法:" -ForegroundColor Green
    Write-Host '  .\run_amazon_scraper.ps1 "搜索词" [数量] [排序方式]' -ForegroundColor White
    Write-Host ""
    Write-Host "参数说明:" -ForegroundColor Green
    Write-Host "  搜索词    必填，完整短语，用双引号包裹" -ForegroundColor White
    Write-Host "  数量      可选，1-100，默认 50" -ForegroundColor White
    Write-Host "  排序方式  可选，sales（按销量，默认）/ reviews（按评论数）" -ForegroundColor White
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Green
    Write-Host '  .\run_amazon_scraper.ps1 "birthday crochet gifts"' -ForegroundColor White
    Write-Host '  .\run_amazon_scraper.ps1 "graduation gift" 50' -ForegroundColor White
    Write-Host '  .\run_amazon_scraper.ps1 "wireless earbuds" 30 reviews' -ForegroundColor White
    Write-Host ""
    Read-Host "按 Enter 退出"
    exit 1
}

# ── 解析参数 ──────────────────────────────────────────────────
$keyword = $args[0].Trim()
$count   = 50
$sortBy  = "sales"

if ($args.Count -ge 2) {
    $a2 = $args[1]
    if ($a2 -match '^\d+$') {
        $count = [Math]::Max(1, [Math]::Min(100, [int]$a2))
    } elseif ($a2 -in @("sales","reviews")) {
        $sortBy = $a2
    } else {
        Write-Host "[WARNING] 第2个参数 '$a2' 无效，使用默认值" -ForegroundColor Yellow
    }
}

if ($args.Count -ge 3) {
    $a3 = $args[2]
    if ($a3 -in @("sales","reviews")) {
        $sortBy = $a3
    } else {
        Write-Host "[WARNING] 第3个参数 '$a3' 无效，使用默认排序 sales" -ForegroundColor Yellow
    }
}

if (-not $keyword) {
    Write-Host "[ERROR] 搜索词不能为空" -ForegroundColor Red
    exit 1
}

# ── 打印任务摘要 ──────────────────────────────────────────────
Write-Host "搜索词  : $keyword" -ForegroundColor White
Write-Host "采集数量: $count 个" -ForegroundColor White
Write-Host "排序方式: $sortBy" -ForegroundColor White
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# ── 切换到脚本所在目录 ────────────────────────────────────────
Set-Location $PSScriptRoot

# ── 调用 Python 入口脚本 ──────────────────────────────────────
python amazon_scraper.py $keyword $count $sortBy
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  [OK] 采集完成！" -ForegroundColor Green
    Write-Host "  输出目录: $PSScriptRoot\<今日日期>\" -ForegroundColor White
    Write-Host "    - Excel 数据文件  (*.xlsx)" -ForegroundColor White
    Write-Host "    - 商品图片文件夹  (images/)" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Green
} else {
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "  [FAIL] 采集失败，退出码: $exitCode" -ForegroundColor Red
    Write-Host "  请检查上方错误信息后重试" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Red
}

Write-Host ""
Read-Host "按 Enter 退出"
exit $exitCode
