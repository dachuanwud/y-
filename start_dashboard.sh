#!/bin/bash

# 加密货币市场指数看板启动脚本

echo "🚀 正在启动加密货币市场指数看板..."
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查是否安装了依赖
echo "📦 检查依赖..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  检测到未安装依赖，正在安装..."
    pip3 install -r requirements_dashboard.txt
else
    echo "✅ 依赖已安装"
fi

echo ""
echo "🌐 启动看板..."
echo "📍 访问地址: http://localhost:8501"
echo "⌨️  按 Ctrl+C 停止服务"
echo ""

# 启动Streamlit应用
streamlit run dashboard.py

