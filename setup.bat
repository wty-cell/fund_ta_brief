@echo off
chcp 65001 >nul
echo ======================================
echo   基金TA每日简报系统 — 环境初始化
echo ======================================

set PROJECT_DIR=%~dp0

:: 1. 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [OK] Python 版本: %%v

:: 2. 创建虚拟环境
if not exist "%PROJECT_DIR%venv\" (
    echo [步骤1] 创建虚拟环境...
    python -m venv "%PROJECT_DIR%venv"
    echo [OK] 虚拟环境已创建
) else (
    echo [跳过] 虚拟环境已存在
)

:: 3. 安装依赖
echo [步骤2] 安装 Python 依赖...
"%PROJECT_DIR%venv\Scripts\pip.exe" install --upgrade pip -q
"%PROJECT_DIR%venv\Scripts\pip.exe" install -r "%PROJECT_DIR%requirements.txt" -q
echo [OK] Python 依赖安装完成

:: 4. 安装 Playwright 浏览器
echo [步骤3] 安装 Playwright Chromium 浏览器...
"%PROJECT_DIR%venv\Scripts\playwright.exe" install chromium
echo [OK] Playwright 浏览器安装完成

:: 5. 创建 data 目录
echo [步骤4] 创建数据目录...
mkdir "%PROJECT_DIR%data\raw" 2>nul
mkdir "%PROJECT_DIR%data\processed" 2>nul
mkdir "%PROJECT_DIR%data\candidate_pool" 2>nul
mkdir "%PROJECT_DIR%data\reports" 2>nul
mkdir "%PROJECT_DIR%data\logs" 2>nul
echo [OK] 数据目录已就绪

:: 6. 创建 .env（如果不存在）
if not exist "%PROJECT_DIR%config\.env" (
    echo [步骤5] 创建环境变量文件...
    copy "%PROJECT_DIR%config\.env.example" "%PROJECT_DIR%config\.env" >nul
    echo.
    echo ⚠️  请编辑 config\.env 填入你的 API Key 和邮箱配置
    echo     用记事本打开: notepad "%PROJECT_DIR%config\.env"
    echo.
) else (
    echo [跳过] config\.env 已存在
)

:: 7. 设置 Windows 任务计划
echo.
echo ======================================
echo   定时任务配置（每日自动运行）
echo ======================================
set /p SETUP_TASK=是否设置每日定时任务？(y/N):

if /i "%SETUP_TASK%"=="y" (
    set /p RUN_TIME=请输入每日运行时间（格式 HH:MM，默认 08:00）:
    if "%RUN_TIME%"=="" set RUN_TIME=08:00

    schtasks /create /tn "基金TA每日简报" ^
        /tr "\"%PROJECT_DIR%venv\Scripts\python.exe\" \"%PROJECT_DIR%run_full_pipeline.py\"" ^
        /sc daily /st %RUN_TIME% /f >nul 2>&1

    if errorlevel 1 (
        echo [警告] 任务计划创建失败，请以管理员身份运行此脚本
    ) else (
        echo [OK] 定时任务已设置：每天 %RUN_TIME% 自动运行
        echo      查看任务: 任务计划程序 ^> 基金TA每日简报
        echo      删除任务: schtasks /delete /tn "基金TA每日简报" /f
    )
)

echo.
echo ======================================
echo   部署完成！
echo ======================================
echo.
echo 手动运行项目:
echo   venv\Scripts\activate
echo   python run_full_pipeline.py
echo.
pause
