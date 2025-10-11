#!/bin/bash
#
# 安全的数据库迁移脚本
# 在执行迁移前进行各种检查和备份
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}VideoSite 数据库安全迁移脚本${NC}"
echo -e "${GREEN}================================${NC}"
echo

# 检查是否在backend目录
if [ ! -f "alembic.ini" ]; then
    echo -e "${RED}错误: 请在backend目录下运行此脚本${NC}"
    exit 1
fi

# 检查虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}警告: 虚拟环境未激活${NC}"
    echo "激活虚拟环境..."
    source venv/bin/activate || {
        echo -e "${RED}错误: 无法激活虚拟环境${NC}"
        exit 1
    }
fi

# 检查alembic是否可用
if ! command -v alembic &> /dev/null; then
    echo -e "${RED}错误: alembic命令未找到${NC}"
    echo "请安装: pip install alembic"
    exit 1
fi

echo -e "${YELLOW}步骤1: 检查数据库连接...${NC}"
python -c "
from app.database import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    db.close()
    print('✅ 数据库连接正常')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"

echo
echo -e "${YELLOW}步骤2: 检查当前迁移状态...${NC}"
alembic current

echo
echo -e "${YELLOW}步骤3: 查看待执行的迁移...${NC}"
echo "待执行的迁移："
alembic show head

echo
echo -e "${YELLOW}步骤4: 创建数据库备份...${NC}"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
echo "备份文件: $BACKUP_FILE"

# 从DATABASE_URL_SYNC提取数据库信息
DB_INFO=$(python -c "
from app.config import settings
import re
url = settings.DATABASE_URL_SYNC
match = re.match(r'postgresql://([^:]+):([^@]+)@([^/]+)/(.+)', url)
if match:
    print(f'{match.group(1)} {match.group(4)} {match.group(3)}')
")

if [ -n "$DB_INFO" ]; then
    read -r DB_USER DB_NAME DB_HOST <<< "$DB_INFO"
    echo "正在备份数据库 $DB_NAME..."
    PGPASSWORD=$(python -c "
from app.config import settings
import re
url = settings.DATABASE_URL_SYNC
match = re.match(r'postgresql://[^:]+:([^@]+)@', url)
if match:
    print(match.group(1))
") pg_dump -U $DB_USER -h $DB_HOST $DB_NAME > $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 数据库备份成功: $BACKUP_FILE${NC}"
    else
        echo -e "${RED}❌ 数据库备份失败${NC}"
        echo "是否继续？(y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  无法自动备份，请手动备份数据库${NC}"
fi

echo
echo -e "${YELLOW}步骤5: 执行迁移...${NC}"
echo -e "${RED}⚠️  警告: 此操作将修改数据库结构${NC}"
echo "待执行的迁移包括："
echo "  - 评分触发器（自动更新统计）"
echo "  - 点赞表和触发器"
echo "  - 10个性能索引（可能较慢）"
echo
echo "是否继续？(y/N)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "开始迁移..."
    alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 数据库迁移成功${NC}"
    else
        echo -e "${RED}❌ 数据库迁移失败${NC}"
        echo "请检查错误日志并考虑回滚"
        echo "回滚命令: alembic downgrade -3"
        exit 1
    fi
else
    echo "迁移已取消"
    exit 0
fi

echo
echo -e "${YELLOW}步骤6: 验证迁移结果...${NC}"
alembic current

echo
echo -e "${YELLOW}步骤7: 检查触发器和索引...${NC}"
python -c "
from app.database import SessionLocal

db = SessionLocal()

# 检查触发器
print('检查触发器...')
triggers = db.execute('''
    SELECT trigger_name, event_object_table
    FROM information_schema.triggers
    WHERE trigger_schema = 'public'
    AND trigger_name IN (
        'rating_insert_trigger',
        'rating_update_trigger',
        'rating_delete_trigger',
        'comment_like_insert_trigger',
        'comment_like_delete_trigger'
    )
''').fetchall()

for trigger in triggers:
    print(f'  ✅ {trigger[0]} on {trigger[1]}')

# 检查索引
print()
print('检查新索引...')
indexes = db.execute('''
    SELECT indexname, tablename
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND indexname LIKE 'idx_videos_status_%'
''').fetchall()

for index in indexes:
    print(f'  ✅ {index[0]} on {index[1]}')

db.close()
print()
print('✅ 验证完成')
"

echo
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}迁移完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo
echo "接下来的步骤："
echo "1. 清空Redis缓存: redis-cli FLUSHDB"
echo "2. 重启应用服务"
echo "3. 检查健康状态: curl http://localhost:8000/health"
echo "4. 查看部署清单: cat DEPLOYMENT_CHECKLIST.md"
echo
echo "备份文件: $BACKUP_FILE"
echo "如需回滚: alembic downgrade -3"
echo


