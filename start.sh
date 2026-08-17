#!/bin/bash

echo "================================"
echo "无障碍设施评价系统启动脚本"
echo "================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

echo "✓ Python3 已安装"

# 检查依赖
echo ""
echo "检查依赖..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "正在安装依赖..."
    python3 -m pip install -r requirements.txt
}

echo "✓ 依赖已安装"

# 初始化数据库（仅首次：standard_clauses 为空时才执行，init_db 本身已幂等）
echo ""
if python3 -c "
from app.core.database import SessionLocal
from app.models.models import StandardClause
db = SessionLocal()
empty = db.query(StandardClause).first() is None
db.close()
exit(0 if empty else 1)
" 2>/dev/null; then
    echo "首次启动，初始化数据库..."
    python3 init_db.py
else
    echo "✓ 数据库已初始化（如需重置请手动运行 python3 init_db.py）"
fi

# 启动服务
echo ""
echo "启动服务..."
echo ""
echo "服务将运行在: http://localhost:8001"
echo "API文档地址: http://localhost:8001/docs"
echo "前端页面地址: http://localhost:8001/"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload