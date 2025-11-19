# Crypto Dashboard V2 (React + FastAPI)

这是一个经过全面重构的加密货币市场指数看板，采用了现代化的前后端分离架构。

## 🌟 特性
- **极致审美**: 采用 "Institutional Dark" 风格，磨砂玻璃质感，霓虹色数据可视化。
- **高性能**: 后端由 Streamlit 迁移至 **FastAPI**，响应速度更快。
- **流畅交互**: 前端采用 **React + Vite**，配合 **Recharts** 实现丝滑的图表交互。
- **实时性**: 支持数据热重载与实时计算。

## 📂 目录结构
- `frontend/`: React 前端代码 (Vite, Tailwind, Shadcn/UI)
- `backend_server/`: FastAPI 后端代码
- `components/`: 复用的核心数据处理逻辑 (Python)
- `config.py`: 全局配置文件

## 🚀 快速开始

### 方式一：一键启动 (推荐)
直接运行根目录下的脚本：
```bash
./start_v2.sh
```

### 方式二：手动启动

1. **启动后端**
```bash
pip install -r requirements_v2.txt
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m uvicorn backend_server.main:app --reload --port 8000
```

2. **启动前端**
```bash
cd frontend
npm install  # 仅首次
npm run dev
```

## 🛠 开发说明
- 前端通过 `http://localhost:8000/api` 访问后端数据。
- 修改 `config.py` 可直接影响前后端的数据源配置。

