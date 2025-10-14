#!/bin/bash
# 启动 Celery Beat
# 用于定时调度任务

cd "$(dirname "$0")/backend"

echo "======================================"
echo "启动 Celery Beat"
echo "======================================"
echo ""

# 激活虚拟环境
source venv/bin/activate

# 启动 Beat
celery -A app.celery_app beat \
    --loglevel=info \
    --logfile=logs/celery-beat.log

echo ""
echo "Celery Beat 已停止"
