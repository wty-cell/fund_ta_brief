#!/bin/bash
# 基金TA每日简报系统 — 一键部署脚本（Linux/macOS）

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "======================================"
echo "  基金TA每日简报系统 — 环境初始化"
echo "======================================"
echo "项目目录: $PROJECT_DIR"

# 1. 检查 Python
if ! command -v python3 &>/dev/null; then
    echo "[错误] 未找到 python3，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[OK] Python 版本: $PYTHON_VERSION"

# 2. 创建虚拟环境
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "[步骤1] 创建虚拟环境..."
    python3 -m venv "$PROJECT_DIR/venv"
    echo "[OK] 虚拟环境已创建"
else
    echo "[跳过] 虚拟环境已存在"
fi

# 3. 激活并安装依赖
echo "[步骤2] 安装 Python 依赖..."
"$PROJECT_DIR/venv/bin/pip" install --upgrade pip -q
"$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt" -q
echo "[OK] Python 依赖安装完成"

# 4. 安装 Playwright 浏览器
echo "[步骤3] 安装 Playwright Chromium 浏览器..."
"$PROJECT_DIR/venv/bin/playwright" install chromium
echo "[OK] Playwright 浏览器安装完成"

# 5. 创建 data 目录
echo "[步骤4] 创建数据目录..."
mkdir -p "$PROJECT_DIR/data/raw"
mkdir -p "$PROJECT_DIR/data/processed"
mkdir -p "$PROJECT_DIR/data/candidate_pool"
mkdir -p "$PROJECT_DIR/data/reports"
mkdir -p "$PROJECT_DIR/data/logs"
echo "[OK] 数据目录已就绪"

# 6. 创建 .env（如果不存在）
if [ ! -f "$PROJECT_DIR/config/.env" ]; then
    echo "[步骤5] 创建环境变量文件..."
    cp "$PROJECT_DIR/config/.env.example" "$PROJECT_DIR/config/.env"
    echo ""
    echo "⚠️  请编辑 config/.env 填入你的 API Key 和邮箱配置："
    echo "    nano $PROJECT_DIR/config/.env"
    echo ""
else
    echo "[跳过] config/.env 已存在"
fi

# 7. 设置定时任务（可选）
echo ""
echo "======================================"
echo "  定时任务配置（每日自动运行）"
echo "======================================"
read -p "是否设置每日定时任务？(y/N): " SETUP_CRON

if [[ "$SETUP_CRON" =~ ^[Yy]$ ]]; then
    read -p "请输入每日运行时间（格式 HH:MM，默认 08:00）: " RUN_TIME
    RUN_TIME=${RUN_TIME:-"08:00"}
    HOUR=$(echo "$RUN_TIME" | cut -d: -f1)
    MINUTE=$(echo "$RUN_TIME" | cut -d: -f2)

    CRON_CMD="$MINUTE $HOUR * * * cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python run_full_pipeline.py >> $PROJECT_DIR/data/logs/cron.log 2>&1"

    # 写入 crontab（去重）
    (crontab -l 2>/dev/null | grep -v "fund_ta_brief"; echo "$CRON_CMD") | crontab -

    echo "[OK] 定时任务已设置：每天 $RUN_TIME 自动运行"
    echo "     查看任务: crontab -l"
    echo "     取消任务: crontab -e  (删除对应行)"
fi

echo ""
echo "======================================"
echo "  部署完成！"
echo "======================================"
echo ""
echo "手动运行项目:"
echo "  source venv/bin/activate"
echo "  python run_full_pipeline.py"
echo ""
echo "或直接运行（不激活 venv）:"
echo "  ./venv/bin/python run_full_pipeline.py"
echo ""
