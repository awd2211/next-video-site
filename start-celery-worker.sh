#!/bin/bash
# 启动 Celery Worker
# 用于执行异步任务和调度任务

cd "$(dirname "$0")/backend"

echo "======================================"
echo "启动 Celery Worker"
echo "======================================"
echo ""

# 激活虚拟环境
source venv/bin/activate

# 启动 Worker
celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --logfile=logs/celery-worker.log

echo ""
echo "Celery Worker 已停止"
