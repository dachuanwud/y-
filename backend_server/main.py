from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import pandas as pd
from typing import Optional, List, Dict, Any

# 将根目录添加到 sys.path 以便导入现有组件
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入现有逻辑
from components.data_loader import load_market_data, load_all_market_data, get_data_summary
from config import MARKET_TYPES, CHART_CONFIG
import Y_idx_newV2_spot

app = FastAPI(title="Crypto Dashboard API", version="2.0")

# 配置 CORS，允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "online", "version": "2.0"}

@app.get("/api/config")
def get_config():
    """获取全局配置和图表元数据"""
    return {
        "market_types": MARKET_TYPES,
        "chart_config": CHART_CONFIG
    }

@app.get("/api/summary")
def get_summary(market_type: str = Query(..., description="Market type (spot or swap)")):
    """获取首页核心指标摘要"""
    if market_type not in MARKET_TYPES:
        raise HTTPException(status_code=400, detail="Invalid market type")
    
    summary = get_data_summary(market_type)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary data not available")
    
    # 处理 NaN 值，以便 JSON 序列化
    def clean_nan(obj):
        if isinstance(obj, dict):
            return {k: clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, float) and (obj != obj):  # check for NaN
            return None
        return obj
        
    return clean_nan(summary)

@app.get("/api/chart/{market_type}/{chart_key}")
def get_chart_data(market_type: str, chart_key: str):
    """获取特定图表的历史数据"""
    try:
        # 特殊处理 'comparison' 类型的请求，虽然目前前端可能分开调用
        if chart_key in ['market_7', 'market_30'] and market_type == 'ALL':
            df = load_all_market_data(chart_key)
        else:
            df = load_market_data(market_type, chart_key)
            
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Chart data not found")
        
        # 转换为 JSON 友好格式
        # 确保时间列格式化
        if 'candle_begin_time' in df.columns:
            df['date'] = df['candle_begin_time'].dt.strftime('%Y-%m-%d')
            # 将candle_begin_time也转换为字符串格式，避免Timestamp序列化问题
            df['candle_begin_time'] = df['candle_begin_time'].dt.strftime('%Y-%m-%d')
        
        # 替换 NaN 为 None，并确保所有Timestamp对象都转换为字符串
        df_clean = df.where(pd.notnull(df), None).copy()
        
        # 将Timestamp对象转换为字符串
        for col in df_clean.columns:
            if df_clean[col].dtype == 'datetime64[ns]':
                df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d')
        
        records = df_clean.to_dict(orient='records')
        
        # 清理记录中的Timestamp对象和NaN值（双重保险）
        def clean_record(record):
            cleaned = {}
            for k, v in record.items():
                if v is None:
                    cleaned[k] = None
                elif isinstance(v, pd.Timestamp):
                    cleaned[k] = v.strftime('%Y-%m-%d')
                elif isinstance(v, float) and pd.isna(v):
                    cleaned[k] = None
                else:
                    cleaned[k] = v
            return cleaned
        
        records = [clean_record(r) for r in records]
        
        return {
            "data": records,
            "config": CHART_CONFIG.get(chart_key, {})
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/api/refresh")
def refresh_data():
    """触发数据重新计算"""
    try:
        # 调用原有的计算逻辑
        Y_idx_newV2_spot.calculate_indices_from_local(start_time='2021-01-01')
        return {"status": "success", "message": "Indices recalculated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

