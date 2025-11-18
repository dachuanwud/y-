"""
数据加载模块 - 从CSV文件读取所有指标数据
"""

import pandas as pd
import os
from typing import Dict, Optional
import streamlit as st
from config import DATA_BASE_PATH, DATA_FILES, ALL_DATA_FILES


@st.cache_data(ttl=300)  # 缓存5分钟
def load_market_data(market_type: str, data_key: str) -> Optional[pd.DataFrame]:
    """
    加载特定市场的数据文件
    
    Args:
        market_type: 市场类型 ('swap' 或 'spot')
        data_key: 数据文件键名
        
    Returns:
        DataFrame 或 None（如果文件不存在）
    """
    try:
        file_name = DATA_FILES.get(data_key)
        if not file_name:
            return None
            
        file_path = os.path.join(DATA_BASE_PATH, market_type, file_name)
        
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
        
        # 尝试不同的编码
        try:
            df = pd.read_csv(file_path, encoding='gbk')
        except:
            df = pd.read_csv(file_path, encoding='utf-8')
        
        # 确保时间列是datetime类型
        if 'candle_begin_time' in df.columns:
            df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])
        
        return df
    
    except Exception as e:
        print(f"加载数据失败 ({market_type}/{data_key}): {e}")
        return None


@st.cache_data(ttl=300)
def load_all_market_data(data_key: str) -> Optional[pd.DataFrame]:
    """
    加载ALL市场的数据文件（合约现货对比）
    
    Args:
        data_key: 数据文件键名
        
    Returns:
        DataFrame 或 None（如果文件不存在）
    """
    try:
        file_name = ALL_DATA_FILES.get(data_key)
        if not file_name:
            return None
            
        file_path = os.path.join(DATA_BASE_PATH, 'ALL', file_name)
        
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
        
        # 尝试不同的编码
        try:
            df = pd.read_csv(file_path, encoding='gbk')
        except:
            df = pd.read_csv(file_path, encoding='utf-8')
        
        # 确保时间列是datetime类型
        if 'candle_begin_time' in df.columns:
            df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])
        
        return df
    
    except Exception as e:
        print(f"加载ALL数据失败 ({data_key}): {e}")
        return None


def get_latest_value(df: pd.DataFrame, column: str) -> Optional[float]:
    """
    获取指定列的最新值
    
    Args:
        df: DataFrame
        column: 列名
        
    Returns:
        最新值或None
    """
    if df is None or df.empty or column not in df.columns:
        return None
    
    return df[column].iloc[-1]


def get_value_change(df: pd.DataFrame, column: str, periods: int = 1) -> Optional[float]:
    """
    计算指定列的变化值
    
    Args:
        df: DataFrame
        column: 列名
        periods: 回溯周期数
        
    Returns:
        变化值或None
    """
    if df is None or df.empty or column not in df.columns or len(df) < periods + 1:
        return None
    
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-(periods + 1)]
    
    return current_value - previous_value


def get_percentage_change(df: pd.DataFrame, column: str, periods: int = 1) -> Optional[float]:
    """
    计算指定列的百分比变化
    
    Args:
        df: DataFrame
        column: 列名
        periods: 回溯周期数
        
    Returns:
        百分比变化或None
    """
    if df is None or df.empty or column not in df.columns or len(df) < periods + 1:
        return None
    
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-(periods + 1)]
    
    if previous_value == 0:
        return None
    
    return ((current_value - previous_value) / abs(previous_value)) * 100


def get_all_data_for_market(market_type: str) -> Dict[str, pd.DataFrame]:
    """
    加载指定市场的所有数据
    
    Args:
        market_type: 市场类型 ('swap' 或 'spot')
        
    Returns:
        包含所有数据的字典
    """
    data = {}
    
    for key in DATA_FILES.keys():
        df = load_market_data(market_type, key)
        if df is not None:
            data[key] = df
    
    return data


def get_latest_date(df: pd.DataFrame) -> Optional[str]:
    """
    获取数据的最新日期
    
    Args:
        df: DataFrame
        
    Returns:
        最新日期字符串或None
    """
    if df is None or df.empty or 'candle_begin_time' not in df.columns:
        return None
    
    return df['candle_begin_time'].iloc[-1].strftime('%Y-%m-%d')


@st.cache_data(ttl=60)
def get_data_summary(market_type: str) -> Dict:
    """
    获取市场数据摘要
    
    Args:
        market_type: 市场类型
        
    Returns:
        包含摘要信息的字典
    """
    summary = {
        'market_type': market_type,
        'y_idx_30': None,
        'y_idx_90': None,
        'altcoin_30': None,
        'market_30': None,
        'latest_date': None,
    }
    
    # Y指数30天
    df_y30 = load_market_data(market_type, 'y_idx_30')
    if df_y30 is not None and not df_y30.empty:
        summary['y_idx_30'] = {
            'value': get_latest_value(df_y30, 'Y_idx'),
            'change': get_value_change(df_y30, 'Y_idx', 1),
            'date': get_latest_date(df_y30),
        }
        summary['latest_date'] = get_latest_date(df_y30)
    
    # Y指数90天
    df_y90 = load_market_data(market_type, 'y_idx_90')
    if df_y90 is not None and not df_y90.empty:
        summary['y_idx_90'] = {
            'value': get_latest_value(df_y90, 'Y_idx90'),
            'change': get_value_change(df_y90, 'Y_idx90', 1),
            'date': get_latest_date(df_y90),
        }
    
    # 山寨指数30天
    df_alt30 = load_market_data(market_type, 'altcoin_30')
    if df_alt30 is not None and not df_alt30.empty:
        summary['altcoin_30'] = {
            'value': get_latest_value(df_alt30, '山寨指数'),
            'change': get_value_change(df_alt30, '山寨指数', 1),
            'date': get_latest_date(df_alt30),
        }
    
    # 市场涨跌幅30天
    df_mkt30 = load_market_data(market_type, 'market_30')
    if df_mkt30 is not None and not df_mkt30.empty:
        summary['market_30'] = {
            'value': get_latest_value(df_mkt30, '全市场涨跌幅指数30d'),
            'change': get_value_change(df_mkt30, '全市场涨跌幅指数30d', 1),
            'date': get_latest_date(df_mkt30),
        }
    
    return summary

