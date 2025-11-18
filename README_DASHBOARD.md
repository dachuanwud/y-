# 加密货币市场指数看板 📊

一个现代化的Web看板，用于实时监控加密货币市场指标，包括山寨指数、市场涨跌幅和Y指数。

## ✨ 功能特性

- 📈 **Y指数监控**: 综合市场指标（30天/90天）
- 🪙 **山寨指数**: 监控山寨币相对比特币的表现（30/90/365天）
- 📊 **市场涨跌幅**: 全市场涨跌趋势分析（7/30/90天）
- 🔄 **合约现货对比**: 合约市场与现货市场对比分析
- 🎨 **现代UI**: 深色主题，简约设计，响应式布局
- 📱 **交互式图表**: 使用Plotly创建的彩虹色渐变图表

## 🏗️ 项目结构

```
Y_idx_newV2_spot/
├── dashboard.py              # Streamlit主应用
├── config.py                 # 配置文件
├── requirements_dashboard.txt # 依赖包
├── components/              # 组件模块
│   ├── data_loader.py       # 数据加载模块
│   ├── charts.py            # 图表生成模块
│   └── metrics.py           # 指标卡片组件
└── styles/                  # 样式文件
    └── custom.css           # 自定义CSS
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_dashboard.txt
```

### 2. 启动看板

```bash
streamlit run dashboard.py
```

### 3. 访问看板

浏览器会自动打开，或手动访问：
```
http://localhost:8501
```

## 📋 使用说明

### 市场选择

在左侧边栏选择要查看的市场类型：
- 🔵 **合约市场 (SWAP)**: 永续合约市场数据
- 🟢 **现货市场 (SPOT)**: 现货市场数据

### 数据刷新

点击侧边栏的 "🔄 刷新数据" 按钮更新数据（清除缓存）

### 指标说明

#### Y指数
综合市场指标，结合了山寨指数和市场涨跌幅：
- **高位 (>150)**: 市场过热，注意风险
- **中位 (0-150)**: 市场正常运行
- **低位 (<0)**: 市场低迷，可能存在机会

#### 山寨指数
反映山寨币相对比特币的表现：
- **>0.75**: 山寨季节（Altcoin Season）
- **0.25-0.75**: 中性市场
- **<0.25**: 比特币季节（Bitcoin Season）

#### 市场涨跌幅
显示整体市场的涨跌趋势：
- **>0**: 市场整体上涨
- **<0**: 市场整体下跌

## 📊 数据来源

- **数据路径**: `/Users/houjl/Downloads/FLdata/`
- **更新频率**: 每日自动更新
- **数据源**: Binance交易所

## 🎨 UI特性

- **深色主题**: 护眼且专业的深色配色
- **彩虹色图表**: 指数值通过颜色渐变直观展示
- **响应式设计**: 自适应不同屏幕尺寸
- **平滑动画**: 悬停效果和过渡动画
- **卡片设计**: 模块化信息展示

## ⚙️ 配置说明

### 修改数据路径

编辑 `config.py` 文件中的 `DATA_BASE_PATH` 变量：

```python
DATA_BASE_PATH = '/your/custom/path'
```

### 自定义图表阈值

在 `config.py` 的 `CHART_CONFIG` 中修改各指标的阈值线：

```python
'y_idx_30': {
    'title': 'Y指数 (30天)',
    'axhline_high': 150,  # 高位线
    'axhline_low': 0,     # 中位线
    'axhline_low2': -20,  # 低位线
}
```

### 修改UI样式

编辑 `styles/custom.css` 文件自定义颜色和样式：

```css
:root {
    --accent-blue: #4a90e2;
    --accent-green: #00ff88;
    /* ... 更多变量 */
}
```

## 🔧 高级功能

### 缓存控制

数据默认缓存5分钟，可在 `components/data_loader.py` 中修改：

```python
@st.cache_data(ttl=300)  # 修改为你需要的秒数
```

### 添加新指标

1. 在 `config.py` 中添加数据文件配置
2. 在 `components/data_loader.py` 中添加加载逻辑
3. 在 `components/charts.py` 中添加图表配置
4. 在 `dashboard.py` 中添加渲染代码

## 🐛 故障排除

### 数据加载失败

检查数据文件路径是否正确：
```bash
ls /Users/houjl/Downloads/FLdata/swap/
ls /Users/houjl/Downloads/FLdata/spot/
```

### 图表显示异常

清除浏览器缓存或使用无痕模式打开

### 端口被占用

指定其他端口启动：
```bash
streamlit run dashboard.py --server.port 8502
```

## 📝 版本信息

- **版本**: 2.0
- **更新日期**: 2025-11-18
- **Python版本**: >= 3.8

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可证

本项目仅供个人学习和研究使用。

---

**提示**: 确保定期运行 `Y_idx_newV2_spot.py` 脚本更新数据，以保证看板显示最新信息。

