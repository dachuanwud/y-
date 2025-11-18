"""
加密货币市场指数看板 - Streamlit主应用
"""

import streamlit as st
import os
from components.data_loader import (
    load_market_data,
    load_all_market_data,
    get_data_summary
)
from components.charts import (
    create_chart_by_key,
    create_comparison_chart
)
from components.metrics import render_summary_cards
from config import UI_CONFIG, MARKET_TYPES
import Y_idx_newV2_spot

# 页面配置
st.set_page_config(
    page_title=UI_CONFIG['page_title'],
    page_icon=UI_CONFIG['page_icon'],
    layout=UI_CONFIG['layout'],
    initial_sidebar_state="expanded"
)

# 加载自定义CSS
def load_css():
    """加载自定义CSS样式"""
    css_file = os.path.join(os.path.dirname(__file__), 'styles', 'custom.css')
    if os.path.exists(css_file):
        with open(css_file, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()


# 主标题和导航栏
def render_header():
    """渲染页面头部"""
    st.markdown("""
    <div class="navbar">
        <div>
            <div class="navbar-title">📊 加密货币市场指数看板</div>
            <div class="navbar-subtitle">实时监控山寨指数、市场涨跌幅和Y指数</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# 侧边栏
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown(f"## {UI_CONFIG['sidebar_title']}")
        
        # 市场类型选择
        market_type = st.selectbox(
            "选择市场类型",
            options=MARKET_TYPES,
            format_func=lambda x: f"{'🔵 合约市场 (SWAP)' if x == 'swap' else '🟢 现货市场 (SPOT)'}",
            key="market_selector"
        )
        
        st.markdown("---")
        
        # 刷新按钮：基于本地最新元数据重算指数并刷新看板
        if st.button("🔄 刷新数据", use_container_width=True):
            with st.spinner("正在根据本地最新数据重新计算所有指数，请稍候..."):
                # 使用本地预处理好的K线数据重算所有指数并更新CSV
                Y_idx_newV2_spot.calculate_indices_from_local(start_time='2021-01-01')
            st.cache_data.clear()
            st.success("📊 指数已根据本地最新数据完成重算")
            st.rerun()
        
        st.markdown("---")
        
        # 信息面板
        st.markdown("### 📌 指标说明")
        
        with st.expander("Y指数"):
            st.markdown("""
            **Y指数** 是综合市场指标，结合了山寨指数和市场涨跌幅。
            
            - **高位 (>150)**: 市场过热
            - **中位 (0-150)**: 市场正常
            - **低位 (<0)**: 市场低迷
            """)
        
        with st.expander("山寨指数"):
            st.markdown("""
            **山寨指数** 反映山寨币相对比特币的表现。
            
            - **>0.75**: 山寨季节
            - **0.25-0.75**: 中性
            - **<0.25**: 比特币季节
            """)
        
        with st.expander("市场涨跌幅"):
            st.markdown("""
            **市场涨跌幅** 显示整体市场的涨跌趋势。
            
            - **>0**: 市场上涨
            - **<0**: 市场下跌
            """)
        
        st.markdown("---")
        
        # 版本信息
        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.8rem; margin-top: 2rem;">
            <p>Version 2.0</p>
            <p>© 2025 Crypto Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    
    return market_type


# 核心指标卡片区域
def render_metrics_section(market_type: str):
    """渲染核心指标区域"""
    summary = get_data_summary(market_type)
    
    if summary:
        render_summary_cards(summary, market_type)
        
        # 显示更新时间
        if summary.get('latest_date'):
            st.markdown(f"""
            <div style="text-align: right; color: #888; font-size: 0.9rem; margin-top: 10px;">
                最后更新: {summary['latest_date']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 无法加载市场数据摘要")


# Y指数图表区域
def render_y_index_section(market_type: str):
    """渲染Y指数图表区域"""
    st.markdown("### 📈 Y指数趋势")
    st.markdown(
        "Y指数综合山寨指数与市场涨跌幅，用于衡量整体市场热度、高低位与情绪。"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**周期：30天滚动 Y 指数**")
        df_y30 = load_market_data(market_type, 'y_idx_30')
        if df_y30 is not None and not df_y30.empty:
            fig = create_chart_by_key(market_type, 'y_idx_30', df_y30)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Y指数30天数据加载中...")
    
    with col2:
        st.markdown("**周期：90天滚动 Y 指数**")
        df_y90 = load_market_data(market_type, 'y_idx_90')
        if df_y90 is not None and not df_y90.empty:
            fig = create_chart_by_key(market_type, 'y_idx_90', df_y90)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Y指数90天数据加载中...")


# 山寨指数图表区域
def render_altcoin_section(market_type: str):
    """渲染山寨指数图表区域"""
    st.markdown("### 🪙 山寨指数趋势")
    st.markdown(
        "山寨指数反映山寨币相对比特币的表现，用于识别 Altcoin Season 或 Bitcoin Season。"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**周期：30天山寨指数**")
        df_alt30 = load_market_data(market_type, 'altcoin_30')
        if df_alt30 is not None and not df_alt30.empty:
            fig = create_chart_by_key(market_type, 'altcoin_30', df_alt30)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 山寨指数30天数据加载中...")
    
    with col2:
        st.markdown("**周期：90天山寨指数**")
        df_alt90 = load_market_data(market_type, 'altcoin_90')
        if df_alt90 is not None and not df_alt90.empty:
            fig = create_chart_by_key(market_type, 'altcoin_90', df_alt90)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 山寨指数90天数据加载中...")
    
    with col3:
        st.markdown("**周期：365天山寨指数**")
        df_alt365 = load_market_data(market_type, 'altcoin_365')
        if df_alt365 is not None and not df_alt365.empty:
            fig = create_chart_by_key(market_type, 'altcoin_365', df_alt365)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 山寨指数365天数据加载中...")


# 市场涨跌幅图表区域
def render_market_section(market_type: str):
    """渲染市场涨跌幅图表区域"""
    st.markdown("### 📊 市场涨跌幅趋势")
    st.markdown(
        "市场涨跌幅指数衡量全市场在不同时间窗口内的整体涨跌强度。"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**周期：7天全市场涨跌幅指数**")
        df_mkt7 = load_market_data(market_type, 'market_7')
        if df_mkt7 is not None and not df_mkt7.empty:
            fig = create_chart_by_key(market_type, 'market_7', df_mkt7)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 市场涨跌幅7天数据加载中...")
    
    with col2:
        st.markdown("**周期：30天全市场涨跌幅指数**")
        df_mkt30 = load_market_data(market_type, 'market_30')
        if df_mkt30 is not None and not df_mkt30.empty:
            fig = create_chart_by_key(market_type, 'market_30', df_mkt30)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 市场涨跌幅30天数据加载中...")
    
    # 90天数据单独一行
    st.markdown("**周期：90天全市场涨跌幅指数**")
    df_mkt90 = load_market_data(market_type, 'market_90')
    if df_mkt90 is not None and not df_mkt90.empty:
        fig = create_chart_by_key(market_type, 'market_90', df_mkt90)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 市场涨跌幅90天数据加载中...")


# 合约现货对比区域
def render_comparison_section():
    """渲染合约现货对比图表区域"""
    st.markdown("### 🔄 合约 vs 现货市场对比")
    st.markdown(
        "对比合约(SWAP)与现货(SPOT)的市场涨跌幅，观察两者在不同周期下的强弱分化。"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**周期：7天 · 合约 vs 现货**")
        df_comp7 = load_all_market_data('market_7')
        if df_comp7 is not None and not df_comp7.empty:
            fig = create_comparison_chart(
                df=df_comp7,
                x_column='candle_begin_time',
                y_columns=['market_swap_7d', 'market_spot_7d'],
                title='市场涨跌幅对比 (7天)',
                height=400,
                y_axis_title="全市场涨跌幅指数"
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 7天对比数据加载中...")
    
    with col2:
        st.markdown("**周期：30天 · 合约 vs 现货**")
        df_comp30 = load_all_market_data('market_30')
        if df_comp30 is not None and not df_comp30.empty:
            fig = create_comparison_chart(
                df=df_comp30,
                x_column='candle_begin_time',
                y_columns=['market_swap_30d', 'market_spot_30d'],
                title='市场涨跌幅对比 (30天)',
                height=400,
                y_axis_title="全市场涨跌幅指数"
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 30天对比数据加载中...")


# 主函数
def main():
    """主函数"""
    # 渲染头部
    render_header()
    
    # 渲染侧边栏并获取选择的市场类型
    market_type = render_sidebar()
    
    # 渲染核心指标卡片
    render_metrics_section(market_type)
    
    # 指标图表分组到标签页，提升信息结构清晰度
    tab_y, tab_alt, tab_market, tab_compare = st.tabs(
        ["Y指数", "山寨指数", "市场涨跌幅", "合约 vs 现货"]
    )

    with tab_y:
        render_y_index_section(market_type)

    with tab_alt:
        render_altcoin_section(market_type)

    with tab_market:
        render_market_section(market_type)

    with tab_compare:
        render_comparison_section()
    
    # 页脚
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.85rem; margin-top: 3rem; padding: 2rem 0; border-top: 1px solid #3a3d4a;">
        <p>💡 提示: 使用侧边栏切换市场类型，点击刷新按钮更新数据</p>
        <p>📊 数据来源: Binance | 🔄 自动更新: 每日</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
