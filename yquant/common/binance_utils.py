'''
币安工具函数
'''
import time
import pandas as pd
from datetime import datetime, timedelta
import traceback
from joblib import Parallel, delayed

def robust_(func, params=None, func_name=''):
    """
    健壮的API调用函数
    """
    for i in range(5):
        try:
            return func() if params is None else func(params)
        except Exception as e:
            print(f'{func_name} 第{i+1}次调用失败: {str(e)}')
            time.sleep(2)
    raise Exception(f'{func_name} 调用失败')

def u_furture_get_exchangeinfo(exchange):
    """
    获取U本位合约交易规则
    Args:
        exchange: ccxt.binance 实例
    Returns:
        dict: 包含交易规则的字典，主要包含 symbols 列表，每个symbol包含：
            - symbol: 交易对名称
            - status: 交易状态
            - baseAsset: 基础资产
            - quoteAsset: 报价资产
            - contractType: 合约类型
            - onboardDate: 上线时间
    """
    try:
        # 直接调用方法，不传递参数
        exchange_info = robust_(exchange.fapiPublicGetExchangeInfo, func_name='fapiPublicGetExchangeInfo')
        return exchange_info
    except Exception as e:
        print(f"获取交易规则失败: {str(e)}")
        return None

def process_single_symbol(args):
    """
    处理单个交易对的K线数据获取
    用于多进程调用
    """
    import ccxt
    from yquant.config.config import cfg  # 导入配置
    
    # 创建新的exchange实例并设置完整配置
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'timeout': cfg.binance.timeout,
        'rateLimit': cfg.binance.rateLimit,
        'verbose': cfg.binance.verbose,
        'hostname': cfg.binance.hostname,
        'proxies': cfg.binance.proxies,  # 添加代理配置

    })

    symbol, run_time, limit, interval = args  # 解包时添加interval
    return fetch_binance_swap_candle_data(exchange, symbol, run_time, limit, interval)

def u_furture_fetch_all_swap_candle_data(exchange, symbol_list, interval, run_time, limit, include_now=True, is_swap=True, njobs=8):
    """
    批量获取U本位合约K线数据

    Args:
        exchange: ccxt交易所实例
        symbol_list: 交易对列表
        interval: K线间隔
        run_time: 运行时间
        limit: K线数量限制
        include_now: 是否包含当前K线
        is_swap: 是否为永续合约
        njobs: 进程数

    Returns:
        dict: {symbol: DataFrame}
    """
    result = []
    # symbol_list = symbol_list[:4]
    if njobs == 1:
        # 单进程获取数据
        for symbol in symbol_list:
            res = fetch_binance_swap_candle_data(exchange, symbol, run_time, limit, interval)
            if res[1] is not None:  # 只添加成功获取的数据
                result.append(res)

    else:
        # 使用joblib进行多进程处理
        arg_list = [(symbol, run_time, limit, interval) for symbol in symbol_list]
        result = Parallel(n_jobs=njobs, verbose=10)(
            delayed(process_single_symbol)(args) for args in arg_list
        )
        # 过滤掉失败的结果
        result = [r for r in result if r[1] is not None]

    
    return dict(result)

def fetch_binance_swap_candle_data(exchange, symbol, run_time, limit, interval='1h'):
    """
    获取币安U本位合约K线数据
    
    Args:
        exchange: ccxt交易所对象
        symbol: 交易对名称
        run_time: 截止时间
        limit: K线数量限制
    
    Returns:
        tuple: (symbol, DataFrame)
            - symbol: 交易对名称
            - DataFrame: K线数据，如果获取失败则为None
    """
    try:
        kline = []
        remain_limit = limit
        
        # 根据interval调整时间计算
        current_time = datetime.now()
        if interval == '1h':
            start_time = int((current_time - timedelta(hours=limit)).timestamp() * 1000)
        elif interval == '1d':
            start_time = int((current_time - timedelta(days=limit)).timestamp() * 1000)
        else:
            raise ValueError(f"不支持的时间间隔: {interval}")
            
        cur_start_time = start_time
        
        # 尝试不同的方法名称
        klines_methods = [
            'fapiPublic_get_continuousklines',
            'fapiPublicGetContinuousKlines',
            'fapiPublic_getContinuousKlines'
        ]
        
        method_found = None
        for method_name in klines_methods:
            if hasattr(exchange, method_name):
                method_found = method_name
                break
                
        if method_found is None:
            raise ValueError("找不到合适的K线数据获取方法")

        while remain_limit > 0:
            cur_limit = min(remain_limit, 499)
            
            params = {
                'pair': symbol,
                'contractType': 'PERPETUAL',
                'interval': interval,  # 使用传入的interval参数
                'limit': cur_limit,
                'startTime': cur_start_time,
            }
            
            cur_kline = robust_(getattr(exchange, method_found), params=params,
                              func_name=method_found)
            
            if cur_kline:
                kline.extend(cur_kline)
                remain_limit -= cur_limit
                cur_start_time = int(cur_kline[-1][0]) + 1
            else:
                break

        if not kline:
            print(f"获取{symbol}的K线数据为空")
            return symbol, None
            
        # 将数据转换为DataFrame
        columns = [
            'timestamp',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'close_time',
            'quote_volume',
            'trades',
            'taker_buy_volume',
            'taker_buy_quote_volume',
            'ignore'
        ]
        df = pd.DataFrame(kline, columns=columns, dtype='float')

        # 处理数据类型
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        
        # 重命名和整理列
        df = df.rename(columns={'timestamp': 'candle_begin_time'})
        df['symbol'] = symbol
        df = df[[
            'candle_begin_time',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'quote_volume',
            'symbol'
        ]]
        
        return symbol, df
        
    except Exception as e:
        print(f"获取{symbol}的K线数据失败: {str(e)}")
        traceback.print_exc()  # 添加更详细的错误信息
        return symbol, None

