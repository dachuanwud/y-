# 快速开始指南 🚀

## 一键启动

### 方式1: 使用启动脚本（推荐）

```bash
./start_dashboard.sh
```

### 方式2: 手动启动

```bash
# 1. 安装依赖
pip3 install -r requirements_dashboard.txt

# 2. 启动看板
streamlit run dashboard.py
```

## 访问看板

启动后，浏览器会自动打开，或手动访问：
```
http://localhost:8501
```

## 主要功能

### 📊 核心指标卡片
在页面顶部显示4个关键指标：
- Y指数 (30天/90天)
- 山寨指数 (30天)
- 市场涨跌幅 (30天)

每个卡片显示：
- 最新值
- 变化值（带颜色和图标）
- 更新日期

### 📈 图表区域

**Y指数趋势** - 2列布局
- 30天趋势
- 90天趋势

**山寨指数趋势** - 3列布局
- 30天趋势
- 90天趋势
- 365天趋势

**市场涨跌幅趋势** - 多列布局
- 7天趋势
- 30天趋势
- 90天趋势

**合约现货对比** - 2列布局
- 7天对比
- 30天对比

### 🎛️ 侧边栏控制

- **市场选择**: 切换合约(SWAP)或现货(SPOT)市场
- **刷新数据**: 清除缓存，重新加载数据
- **指标说明**: 查看各指标的含义和阈值

## 图表交互

Plotly交互式图表支持：
- 🖱️ **缩放**: 滚轮或双指缩放
- 👆 **平移**: 拖拽移动
- 📍 **悬停**: 显示详细数据
- 📷 **截图**: 点击相机图标保存
- 🔍 **框选缩放**: 框选区域放大

## 数据说明

### 数据位置
```
/Users/houjl/Downloads/FLdata/
├── swap/          # 合约市场数据
├── spot/          # 现货市场数据
└── ALL/           # 对比数据
```

### 数据更新
运行原始计算脚本更新数据：
```bash
python Y_idx_newV2_spot.py
```

建议每天运行一次以保持数据最新。

## 常见问题

### Q: 数据显示"加载中"？
**A**: 检查数据文件是否存在：
```bash
ls /Users/houjl/Downloads/FLdata/swap/*.csv
ls /Users/houjl/Downloads/FLdata/spot/*.csv
```

### Q: 如何更改端口？
**A**: 启动时指定端口：
```bash
streamlit run dashboard.py --server.port 8502
```

### Q: 如何禁用自动打开浏览器？
**A**: 
```bash
streamlit run dashboard.py --server.headless true
```

### Q: 数据缓存多久？
**A**: 默认5分钟，点击"刷新数据"按钮立即更新。

## 性能优化

- 数据缓存：避免重复读取CSV文件
- 按需加载：只加载选中市场的数据
- 轻量图表：Plotly优化渲染性能

## 系统要求

- Python >= 3.8
- 内存 >= 2GB
- 支持现代浏览器（Chrome、Firefox、Safari、Edge）

## 下一步

- 查看 `README_DASHBOARD.md` 了解详细文档
- 编辑 `config.py` 自定义配置
- 修改 `styles/custom.css` 调整界面样式

---

💡 **提示**: 首次启动可能需要几秒钟加载数据，请耐心等待。

