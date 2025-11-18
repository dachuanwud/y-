"""
指标卡片组件 - 显示关键指标的最新值和变化
"""

import streamlit as st
from typing import Optional


def format_value(value: Optional[float], decimals: int = 2) -> str:
    """
    格式化数值显示
    
    Args:
        value: 数值
        decimals: 保留小数位数
        
    Returns:
        格式化后的字符串
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def get_change_color(change: Optional[float]) -> str:
    """
    根据变化值获取颜色
    
    Args:
        change: 变化值
        
    Returns:
        颜色代码
    """
    if change is None:
        return "#888888"
    elif change > 0:
        return "#00ff88"  # 绿色（涨）
    elif change < 0:
        return "#ff5555"  # 红色（跌）
    else:
        return "#888888"  # 灰色（持平）


def get_change_icon(change: Optional[float]) -> str:
    """
    根据变化值获取图标
    
    Args:
        change: 变化值
        
    Returns:
        图标字符串
    """
    if change is None:
        return "➖"
    elif change > 0:
        return "📈"
    elif change < 0:
        return "📉"
    else:
        return "➖"


def render_metric_card(
    title: str,
    value: Optional[float],
    change: Optional[float],
    date: Optional[str] = None,
    decimals: int = 2,
    prefix: str = "",
    suffix: str = ""
):
    """
    渲染指标卡片
    
    Args:
        title: 指标标题
        value: 指标值
        change: 变化值
        date: 日期
        decimals: 小数位数
        prefix: 前缀
        suffix: 后缀
    """
    change_color = get_change_color(change)
    change_icon = get_change_icon(change)
    
    # 格式化值
    value_str = format_value(value, decimals)
    change_str = format_value(change, decimals) if change is not None else "N/A"
    
    # 使用HTML+CSS创建卡片
    card_html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{prefix}{value_str}{suffix}</div>
        <div class="metric-change" style="color: {change_color};">
            <span class="change-icon">{change_icon}</span>
            <span class="change-value">{change_str if change is not None else 'N/A'}</span>
        </div>
        {f'<div class="metric-date">更新: {date}</div>' if date else ''}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_summary_cards(summary: dict, market_type: str):
    """
    渲染概要指标卡片组
    
    Args:
        summary: 摘要数据
        market_type: 市场类型
    """
    st.markdown(f"### 📊 {market_type.upper()} 市场核心指标")
    
    cols = st.columns(4)
    
    # Y指数30天
    with cols[0]:
        y30_data = summary.get('y_idx_30', {})
        if y30_data:
            render_metric_card(
                title="Y指数 (30天)",
                value=y30_data.get('value'),
                change=y30_data.get('change'),
                date=y30_data.get('date'),
                decimals=2
            )
        else:
            st.info("数据加载中...")
    
    # Y指数90天
    with cols[1]:
        y90_data = summary.get('y_idx_90', {})
        if y90_data:
            render_metric_card(
                title="Y指数 (90天)",
                value=y90_data.get('value'),
                change=y90_data.get('change'),
                date=y90_data.get('date'),
                decimals=2
            )
        else:
            st.info("数据加载中...")
    
    # 山寨指数
    with cols[2]:
        alt_data = summary.get('altcoin_30', {})
        if alt_data:
            render_metric_card(
                title="山寨指数 (30天)",
                value=alt_data.get('value'),
                change=alt_data.get('change'),
                date=alt_data.get('date'),
                decimals=3,
                suffix=""
            )
        else:
            st.info("数据加载中...")
    
    # 市场涨跌幅
    with cols[3]:
        mkt_data = summary.get('market_30', {})
        if mkt_data:
            render_metric_card(
                title="市场涨跌幅 (30天)",
                value=mkt_data.get('value'),
                change=mkt_data.get('change'),
                date=mkt_data.get('date'),
                decimals=4,
                suffix=""
            )
        else:
            st.info("数据加载中...")


def render_status_indicator(value: Optional[float], thresholds: dict):
    """
    渲染状态指示器
    
    Args:
        value: 指标值
        thresholds: 阈值字典 {'high': 0.75, 'low': 0.25}
    """
    if value is None:
        status = "未知"
        color = "#888888"
        icon = "❓"
    elif value >= thresholds.get('high', float('inf')):
        status = "高位"
        color = "#ff5555"
        icon = "🔥"
    elif value <= thresholds.get('low', float('-inf')):
        status = "低位"
        color = "#5555ff"
        icon = "❄️"
    else:
        status = "中位"
        color = "#ffaa00"
        icon = "⚠️"
    
    indicator_html = f"""
    <div class="status-indicator" style="background-color: {color}20; border-left: 4px solid {color};">
        <span style="font-size: 24px;">{icon}</span>
        <span style="color: {color}; font-weight: bold; margin-left: 10px;">{status}</span>
    </div>
    """
    
    st.markdown(indicator_html, unsafe_allow_html=True)


def render_mini_card(label: str, value: str, icon: str = "📌"):
    """
    渲染小型信息卡片
    
    Args:
        label: 标签
        value: 值
        icon: 图标
    """
    mini_card_html = f"""
    <div class="mini-card">
        <span class="mini-icon">{icon}</span>
        <span class="mini-label">{label}:</span>
        <span class="mini-value">{value}</span>
    </div>
    """
    
    st.markdown(mini_card_html, unsafe_allow_html=True)

