"""
图表生成模块 - 使用Plotly创建交互式图表
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, List
from config import CHART_CONFIG, SMOOTH_WINDOW


def create_rainbow_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    config: dict,
    height: int = 400,
    smooth_window: int = 5,
    y_axis_title: str = "指数值"
) -> Optional[go.Figure]:
    """
    创建彩虹色渐变的指数折线图
    
    Args:
        df: 数据DataFrame
        x_column: x轴列名（时间）
        y_column: y轴列名（指数值）
        title: 图表标题
        config: 图表配置（包含阈值线等）
        height: 图表高度
        smooth_window: 滚动均值窗口大小（0或1表示不平滑）
        
    Returns:
        Plotly Figure对象
    """
    if df is None or df.empty or x_column not in df.columns or y_column not in df.columns:
        return None
    
    # 获取配置
    min_val = config.get('min_val', 0)
    max_val = config.get('max_val', 1)
    axhline_high = config.get('axhline_high')
    axhline_low = config.get('axhline_low')
    axhline_low2 = config.get('axhline_low2')
    
    # 创建图表
    fig = go.Figure()
    
    # 获取原始数据
    y_values = df[y_column].values.astype(float)
    x_values = df[x_column].values
    
    # 应用滚动均值平滑（仅用于展示，不改变原数据）
    if smooth_window > 1:
        y_smooth = pd.Series(y_values).rolling(window=smooth_window, center=True, min_periods=1).mean().values
    else:
        y_smooth = y_values
    
    # 使用插值增加数据点，使折线更平滑
    from scipy import interpolate
    
    # 创建有效数据的掩码（非NaN）
    valid_mask = ~np.isnan(y_smooth)
    if valid_mask.sum() < 2:
        # 数据点太少，无法插值
        x_interp = x_values
        y_interp = y_smooth
    else:
        # 对时间进行数值化处理
        x_numeric = np.arange(len(x_values))
        x_valid = x_numeric[valid_mask]
        y_valid = y_smooth[valid_mask]
        
        # 创建插值函数
        f_interp = interpolate.interp1d(x_valid, y_valid, kind='cubic', fill_value='extrapolate')
        
        # 生成更密集的点（增加5倍密度）
        x_numeric_dense = np.linspace(x_numeric[0], x_numeric[-1], len(x_numeric) * 5)
        y_interp = f_interp(x_numeric_dense)
        
        # 将数值索引映射回时间
        x_interp = pd.to_datetime(np.interp(x_numeric_dense, x_numeric, 
                                            pd.to_datetime(x_values).astype(np.int64)))
    
    # 归一化值用于颜色映射（0-1之间）
    value_range = max(max_val - min_val, 1e-9)
    normalized = (y_interp - min_val) / value_range
    normalized = np.clip(normalized, 0, 1)  # 限制在0-1之间
    line_color_values = np.nan_to_num(normalized, nan=0.5)
    
    # 添加彩虹渐变折线（收敛配色，不展示色带）
    # 使用细小的 marker 配合线条实现柔和的渐变效果
    fig.add_trace(go.Scatter(
        x=x_interp,
        y=y_interp,
        mode='lines+markers',
        line=dict(
            width=3,
            color='rgba(200, 200, 200, 0.25)'  # 底层浅色线条
        ),
        marker=dict(
            size=3,
            color=line_color_values,
            colorscale='Rainbow',
            cmin=0,
            cmax=1,
            showscale=False,
            line=dict(width=0)  # 去掉 marker 边框
        ),
        name=y_column,
        hovertemplate='<b>日期</b>: %{x|%Y-%m-%d}<br><b>指数</b>: %{y:.2f}<extra></extra>'
    ))
    
    # 添加阈值线
    if axhline_high is not None:
        fig.add_hline(
            y=axhline_high,
            line_dash="dash",
            line_color="rgba(255, 50, 50, 0.6)",
            annotation_text=f"高位: {axhline_high}",
            annotation_position="right"
        )
    
    if axhline_low is not None:
        fig.add_hline(
            y=axhline_low,
            line_dash="dash",
            line_color="rgba(50, 255, 50, 0.6)",
            annotation_text=f"中位: {axhline_low}",
            annotation_position="right"
        )
    
    if axhline_low2 is not None:
        fig.add_hline(
            y=axhline_low2,
            line_dash="dash",
            line_color="rgba(50, 150, 255, 0.6)",
            annotation_text=f"低位: {axhline_low2}",
            annotation_position="right"
        )
    
    # 获取最新值（使用插值后的最后一个值）
    latest_value = y_interp[-1]
    latest_date = x_interp[-1]
    
    # 添加最新值标注（仅当值不为 NaN 时）
    if not np.isnan(latest_value):
        fig.add_annotation(
            x=latest_date,
            y=latest_value,
            text=f"{latest_value:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="white",
            ax=-40,
            ay=-40,
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="white",
            borderwidth=2,
            font=dict(size=14, color="white")
        )
    
    # 更新布局
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'white'}
        },
        xaxis_title="日期",
        yaxis_title=y_axis_title,
        height=height,
        hovermode='x unified',
        plot_bgcolor='rgba(30, 30, 30, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128, 128, 128, 0.3)'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128, 128, 128, 0.3)',
            range=[min_val - (max_val - min_val) * 0.1, max_val + (max_val - min_val) * 0.1]
        ),
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_comparison_chart(
    df: pd.DataFrame,
    x_column: str,
    y_columns: List[str],
    title: str,
    height: int = 400,
    y_axis_title: str = "指数值"
) -> Optional[go.Figure]:
    """
    创建对比图表（如合约vs现货）
    
    Args:
        df: 数据DataFrame
        x_column: x轴列名（时间）
        y_columns: y轴列名列表
        title: 图表标题
        height: 图表高度
        
    Returns:
        Plotly Figure对象
    """
    if df is None or df.empty or x_column not in df.columns:
        return None
    
    fig = go.Figure()
    
    # 颜色配置
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    name_mapping = {
        "market_swap_7d": "合约市场 7天涨跌幅指数",
        "market_spot_7d": "现货市场 7天涨跌幅指数",
        "market_swap_30d": "合约市场 30天涨跌幅指数",
        "market_spot_30d": "现货市场 30天涨跌幅指数",
    }
    
    for idx, col in enumerate(y_columns):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_column],
                y=df[col],
                mode='lines',
                name=name_mapping.get(col, col),
                line=dict(width=3, color=colors[idx % len(colors)]),
                hovertemplate=f'<b>{col}</b><br>日期: %{{x|%Y-%m-%d}}<br>值: %{{y:.4f}}<extra></extra>'
            ))
    
    # 添加零线
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="rgba(200, 200, 200, 0.5)",
        annotation_text="零线",
        annotation_position="right"
    )
    
    # 更新布局
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'white'}
        },
        xaxis_title="日期",
        yaxis_title=y_axis_title,
        height=height,
        hovermode='x unified',
        plot_bgcolor='rgba(30, 30, 30, 0.5)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128, 128, 128, 0.3)'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=True,
            linewidth=2,
            linecolor='rgba(128, 128, 128, 0.3)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="white",
            borderwidth=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_chart_by_key(market_type: str, data_key: str, df: pd.DataFrame) -> Optional[go.Figure]:
    """
    根据数据键创建对应的图表
    
    Args:
        market_type: 市场类型
        data_key: 数据键
        df: 数据DataFrame
        
    Returns:
        Plotly Figure对象
    """
    if df is None or df.empty:
        return None
    
    config = CHART_CONFIG.get(data_key, {})
    
    # 确定y轴列名与坐标轴标题
    if data_key == 'y_idx_30':
        y_column = 'Y_idx'
        y_axis_title = "Y指数值"
    elif data_key == 'y_idx_90':
        y_column = 'Y_idx90'
        y_axis_title = "Y指数值"
    elif data_key in ['altcoin_30', 'altcoin_90', 'altcoin_365']:
        y_column = '山寨指数'
        y_axis_title = "山寨指数值"
    elif data_key == 'market_7':
        y_column = '全市场涨跌幅指数7d'
        y_axis_title = "全市场涨跌幅指数"
    elif data_key == 'market_30':
        y_column = '全市场涨跌幅指数30d'
        y_axis_title = "全市场涨跌幅指数"
    elif data_key == 'market_90':
        y_column = '全市场涨跌幅指数90d'
        y_axis_title = "全市场涨跌幅指数"
    else:
        return None
    
    if y_column not in df.columns:
        return None
    
    # 标题中同时包含指标名称、周期与市场类型（中文）
    market_label = "合约市场 (SWAP)" if market_type == "swap" else "现货市场 (SPOT)"
    title = f"{config.get('title', data_key)} · {market_label}"
    
    return create_rainbow_line_chart(
        df=df,
        x_column='candle_begin_time',
        y_column=y_column,
        title=title,
        config=config,
        height=400,
        smooth_window=SMOOTH_WINDOW,
        y_axis_title=y_axis_title
    )
