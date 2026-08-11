@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

echo ============================================================
echo   亚马逊商品采集技能 v4.0  ^|  Windows 批处理启动器
echo ============================================================
echo.

:: ── 检查 Python ────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未检测到 Python，请先安装 Python 3.8+ 并加入 PATH
    echo         下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: ── 检查参数 ────────────────────────────────────────────────
if "%~1"=="" (
    echo 用法:
    echo   run_amazon_scraper.bat "搜索词" [数量] [排序方式]
    echo.
    echo 参数说明:
    echo   搜索词    必填，完整短语，用双引号包裹
    echo   数量      可选，1-100，默认 50
    echo   排序方式  可选，sales（按销量，默认）/ reviews（按评论数）
    echo.
    echo 示例:
    echo   run_amazon_scraper.bat "birthday crochet gifts"
    echo   run_amazon_scraper.bat "graduation gift" 50
    echo   run_amazon_scraper.bat "wireless earbuds" 30 reviews
    echo.
    pause
    exit /b 1
)

:: ── 解析参数 ────────────────────────────────────────────────
set "KEYWORD=%~1"
set "COUNT=50"
set "SORT=sales"

if not "%~2"=="" (
    :: 判断第2个参数是数字还是排序方式
    echo %~2| findstr /r "^[0-9][0-9]*$" >nul 2>&1
    if !errorlevel! equ 0 (
        set "COUNT=%~2"
    ) else (
        if "%~2"=="reviews" ( set "SORT=reviews" ) else (
        if "%~2"=="sales"   ( set "SORT=sales"   ) else (
            echo [WARNING] 第2个参数 "%~2" 无效，使用默认值
        ))
    )
)

if not "%~3"=="" (
    if "%~3"=="reviews" ( set "SORT=reviews" ) else (
    if "%~3"=="sales"   ( set "SORT=sales"   ) else (
        echo [WARNING] 第3个参数 "%~3" 无效，使用默认排序 sales
    ))
)

:: ── 打印任务摘要 ────────────────────────────────────────────
echo 搜索词  : !KEYWORD!
echo 采集数量: !COUNT! 个
echo 排序方式: !SORT!
echo ────────────────────────────────────────────────────────────
echo.

:: ── 切换到脚本所在目录 ──────────────────────────────────────
cd /d "%~dp0"

:: ── 调用 Python 入口脚本 ────────────────────────────────────
python amazon_scraper.py "!KEYWORD!" !COUNT! !SORT!
set "EXIT_CODE=%errorlevel%"

echo.
if %EXIT_CODE% equ 0 (
    echo ============================================================
    echo   [OK] 采集完成！
    echo   输出目录: %~dp0^<今日日期^>\
    echo     - Excel 数据文件  ^(*.xlsx^)
    echo     - 商品图片文件夹  ^(images/^)
    echo ============================================================
) else (
    echo ============================================================
    echo   [FAIL] 采集失败，退出码: %EXIT_CODE%
    echo   请检查上方错误信息后重试
    echo ============================================================
)

echo.
pause
endlocal
exit /b %EXIT_CODE%
