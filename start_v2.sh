#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 正在启动 Crypto Dashboard V2 (React + FastAPI)...${NC}"

# 1. 检查 Python 环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️ 未检测到虚拟环境，建议使用 python -m venv .venv 创建"
fi

# 2. 安装后端依赖
echo -e "${BLUE}📦 正在检查后端依赖...${NC}"
pip install -r requirements_v2.txt > /dev/null 2>&1

# 3. 启动后端 (后台运行)
echo -e "${GREEN}🔌 启动 FastAPI 后端 (Port 8000)...${NC}"
cd backend_server
# 确保能导入上级目录模块，使用 python3 -m 运行
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 4. 启动前端
echo -e "${GREEN}🎨 启动 React 前端...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，安装前端依赖 (可能需要几分钟)..."
    npm install
fi

echo -e "${BLUE}🌐 访问地址: http://localhost:5173${NC}"
npm run dev

# 退出处理
kill $BACKEND_PID

