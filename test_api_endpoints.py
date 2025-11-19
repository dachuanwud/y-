#!/usr/bin/env python3
"""
测试所有后端API端点是否正常工作
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_endpoint(name, url, params=None):
    """测试API端点"""
    try:
        if params:
            response = requests.get(url, params=params)
        else:
            response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: 成功")
            if isinstance(data, dict):
                if 'data' in data:
                    print(f"   数据条数: {len(data['data'])}")
                if 'config' in data:
                    print(f"   配置: {list(data['config'].keys())}")
            return True
        else:
            print(f"❌ {name}: 失败 (状态码: {response.status_code})")
            print(f"   错误信息: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ {name}: 异常 - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("测试后端API端点")
    print("=" * 60)
    
    results = []
    
    # 测试健康检查
    results.append(test_endpoint("健康检查", f"{BASE_URL.replace('/api', '')}/"))
    
    # 测试配置端点
    results.append(test_endpoint("配置", f"{BASE_URL}/config"))
    
    # 测试摘要端点
    results.append(test_endpoint("摘要 (spot)", f"{BASE_URL}/summary", {"market_type": "spot"}))
    results.append(test_endpoint("摘要 (swap)", f"{BASE_URL}/summary", {"market_type": "swap"}))
    
    # 测试图表端点
    chart_keys = ['y_idx_30', 'y_idx_90', 'altcoin_30', 'altcoin_90', 'altcoin_365', 'market_7', 'market_30', 'market_90']
    market_types = ['spot', 'swap']
    
    for market_type in market_types:
        for chart_key in chart_keys:
            results.append(test_endpoint(
                f"图表 ({market_type}/{chart_key})",
                f"{BASE_URL}/chart/{market_type}/{chart_key}"
            ))
    
    # 汇总结果
    print("\n" + "=" * 60)
    success_count = sum(results)
    total_count = len(results)
    print(f"测试结果: {success_count}/{total_count} 通过")
    print("=" * 60)
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查后端日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())

