"""
配置文件 - 加密货币市场指数看板
"""

import os

# 数据路径配置
DATA_BASE_PATH = '/Users/houjl/Downloads/FLdata'

# 市场类型
MARKET_TYPES = ['swap', 'spot']

# 数据文件配置
DATA_FILES = {
    'y_idx_30': 'Y_idx_V2.csv',
    'y_idx_90': 'Y_idx90_V2.csv',
    'altcoin_30': 'altcoin_index30.csv',
    'altcoin_90': 'altcoin_index90.csv',
    'altcoin_365': 'altcoin_index365.csv',
    'market_7': 'marketzdf_index7.csv',
    'market_30': 'marketzdf_index30.csv',
    'market_90': 'marketzdf_index90.csv',
}

# ALL市场数据文件
ALL_DATA_FILES = {
    'market_7': 'df_swap_spot_7.csv',
    'market_30': 'df_swap_spot_30.csv',
}

# 图表配置
CHART_CONFIG = {
    'y_idx_30': {
        'title': 'Y指数 (30天)',
        'min_val': -50,
        'max_val': 150,
        'axhline_high': 150,
        'axhline_low': 0,
        'axhline_low2': -20,
    },
    'y_idx_90': {
        'title': 'Y指数 (90天)',
        'min_val': -50,
        'max_val': 150,
        'axhline_high': 200,
        'axhline_low': 0,
        'axhline_low2': -20,
    },
    'altcoin_30': {
        'title': '山寨指数 (30天)',
        'min_val': 0.05,
        'max_val': 0.75,
        'axhline_high': 0.75,
        'axhline_low': 0.25,
        'axhline_low2': 0.1,
    },
    'altcoin_90': {
        'title': '山寨指数 (90天)',
        'min_val': 0.05,
        'max_val': 0.75,
        'axhline_high': 0.75,
        'axhline_low': 0.25,
        'axhline_low2': 0.1,
    },
    'altcoin_365': {
        'title': '山寨指数 (365天)',
        'min_val': 0.05,
        'max_val': 0.75,
        'axhline_high': 0.75,
        'axhline_low': 0.25,
        'axhline_low2': 0.1,
    },
    'market_7': {
        'title': '市场涨跌幅 (7天)',
        'min_val': -0.75,
        'max_val': 1,
        'axhline_high': 1,
        'axhline_low': 0,
        'axhline_low2': -0.3,
    },
    'market_30': {
        'title': '市场涨跌幅 (30天)',
        'min_val': -0.75,
        'max_val': 1,
        'axhline_high': 1,
        'axhline_low': 0,
        'axhline_low2': -0.3,
    },
    'market_90': {
        'title': '市场涨跌幅 (90天)',
        'min_val': -0.75,
        'max_val': 1,
        'axhline_high': 1,
        'axhline_low': 0,
        'axhline_low2': -0.3,
    },
}

# UI配置
UI_CONFIG = {
    'page_title': '加密货币市场指数看板',
    'page_icon': '📊',
    'layout': 'wide',
    'sidebar_title': '市场选择',
}

# 颜色配置（彩虹色映射）
COLOR_SCALE = 'Rainbow'

# 图表平滑配置
SMOOTH_WINDOW = 5  # 滚动均值窗口大小，设置为0或1表示不平滑

