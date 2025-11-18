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
    健壮的API调用函数，支持无参数和有参数调用
    """
    for i in range(5):  # 最多重试5次
        try:
            if params is None:
                result = func()
            else:
                result = func(params)
            return result
        except Exception as e:
            print(f'{func_name} 第{i+1}次调用失败: {str(e)}')
            time.sleep(2)  # 失败后等待2秒
    raise Exception(f'{func_name} 调用失败')



def get_exchangeinfo(exchange, market_type='swap'):
    """
    根据市场类型获取相应的交易规则信息

    Args:
        exchange: ccxt.binance 实例
        market_type: 市场类型 ('swap' 或 'spot')

    Returns:
        dict: 包含交易规则的字典
    """
    try:
        if market_type == 'swap':
            # 获取合约交易规则
            exchange_info = robust_(exchange.fapiPublicGetExchangeInfo, params=None, func_name='fapiPublicGetExchangeInfo')
        elif market_type == 'spot':
            # 获取现货交易规则
            exchange_info = robust_(exchange.publicGetExchangeInfo, params=None, func_name='publicGetExchangeInfo')
        else:
            raise ValueError("market_type 必须是 'swap' 或 'spot'")

        return exchange_info
    except Exception as e:
        print(f"获取{market_type}交易规则失败: {str(e)}")
        return None




def get_symbol_list(exchange, quote_asset='USDT', market_type='swap'):
    """
    获取指定市场类型的交易对列表

    Args:
        exchange: ccxt交易所实例
        quote_asset: 计价货币，默认 USDT
        market_type: 市场类型 ('spot' 现货 / 'swap' 合约)

    Returns:
        List[str]: 符合条件的 symbol 列表
    """
    exchange_info = get_exchangeinfo(exchange, market_type)

    if exchange_info is None:
        print(f"无法获取{market_type}市场的交易规则")
        return []

    if market_type == 'swap':
        # 获取永续合约交易对
        symbols = list(filter(
            lambda s: s['status'] == 'TRADING'
                      and s['quoteAsset'] == quote_asset
                      and s['contractType'] == 'PERPETUAL',
            exchange_info['symbols']
        ))
    elif market_type == 'spot':
        # 获取现货交易对
        symbols = list(filter(
            lambda s: s['status'] == 'TRADING'
                      and s['quoteAsset'] == quote_asset,
            exchange_info['symbols']
        ))
    else:
        raise ValueError("market_type 必须是 'swap' 或 'spot'")

    return [s['symbol'] for s in symbols]


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

    exchange, symbol, run_time, limit, interval, market_type = args  # 解包时添加interval
    return fetch_binance_market_candle_data(*args)



def u_furture_fetch_all_candle_data(exchange, symbol_list, interval, run_time, limit, market_type='', njobs=8):
    """
    批量获取K线数据（支持U本位合约、现货）

    Args:
        exchange: ccxt交易所实例
        symbol_list: 交易对列表
        interval: K线间隔
        run_time: 运行时间
        limit: K线数量限制
        include_now: 是否包含当前K线
        market_type: 市场类型 ('spot' 或 'swap')
        njobs: 进程数

    Returns:
        dict: {symbol: DataFrame}
    """
    result = []

    if njobs == 1:
        # 单进程获取数据
        for symbol in symbol_list:
            res = fetch_binance_market_candle_data(exchange, symbol, run_time, limit, interval, market_type)
            if res[1] is not None:  # 只添加成功获取的数据
                result.append(res)
    else:
        # 使用joblib进行多进程处理
        arg_list = [(exchange, symbol, run_time, limit, interval, market_type) for symbol in symbol_list]
        result = Parallel(n_jobs=njobs, verbose=10)(
            delayed(process_single_symbol)(args) for args in arg_list
        )
        # 过滤掉失败的结果
        result = [r for r in result if r[1] is not None]

    return dict(result)


# def process_single_symbol(args):
#     symbol, run_time, limit, interval, market_type = args
#     return fetch_binance_market_candle_data(*args)


def fetch_binance_market_candle_data(exchange, symbol, run_time, limit, interval='1h', market_type='swap'):
    """
    获取币安市场K线数据（支持U本位合约、现货）

    Args:
        exchange: ccxt交易所对象
        symbol: 交易对名称
        run_time: 截止时间
        limit: K线数量限制
        market_type: 市场类型 ('spot' 或 'swap')

    Returns:
        tuple: (symbol, DataFrame)
            - symbol: 交易对名称
            - DataFrame: K线数据，如果获取失败则为None
    """
    try:
        kline = []
        remain_limit = limit

        current_time = datetime.now()
        if interval == '1h':
            start_time = int((current_time - timedelta(hours=limit)).timestamp() * 1000)
        elif interval == '1d':
            start_time = int((current_time - timedelta(days=limit)).timestamp() * 1000)
        else:
            raise ValueError(f"不支持的时间间隔: {interval}")

        cur_start_time = start_time

        # 根据market_type选择API方法
        if market_type == 'swap':
            klines_methods = [
                'fapiPublic_get_continuousklines',
                'fapiPublicGetContinuousKlines',
                'fapiPublic_getContinuousKlines'
            ]
            params_key = 'pair'
            contract_type = 'PERPETUAL'
        elif market_type == 'spot':
            klines_methods = ['public_get_klines']
            params_key = 'symbol'
            contract_type = None
        else:
            raise ValueError("market_type 必须是 'spot' 或 'swap'")

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
                params_key: symbol,
                'interval': interval,
                'limit': cur_limit,
                'startTime': cur_start_time,
            }

            if market_type == 'swap':
                params['contractType'] = contract_type

            cur_kline = robust_(getattr(exchange, method_found), params=params, func_name=method_found)

            if cur_kline:
                kline.extend(cur_kline)
                remain_limit -= cur_limit
                cur_start_time = int(cur_kline[-1][0]) + 1
            else:
                break

        if not kline:
            print(f"获取{symbol}的K线数据为空")
            return symbol, None

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

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

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
        return symbol, None
