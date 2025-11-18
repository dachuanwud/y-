'''
山寨指数
参考：https://www.blockchaincenter.net/altcoin-season-index/

月度指标/季度指标/年度指标

过去一个月/季度/年
山寨指数 = 全市场前50涨跌幅名中 > BTC涨跌幅的币种数量 / 50

'''
import yquant.common.binance_utils_spot as binance
import ccxt
from datetime import datetime
from yquant.db.models.bn_account import BnAccount
from yquant.config.config import cfg
import yquant.common.common_utils as common
from draw_spot import *
import warnings
import pandas as pd
import os
import time
import sys
warnings.filterwarnings("ignore")  # 忽略所有警告

# 设置 matplotlib 使用非交互式后端，避免进程无法退出
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_rows', 500)  # 最多显示数据的行数
pd.set_option('display.max_columns', 500)  # 最多显示数据的列数
pd.set_option('display.width', 180) # 设置打印宽度(**重要**)



def alcoin_stat(alcoin_df, statdays=[30], save_img=True, start_time=None, interval='1d', filename='altcoin_index30', market_type='swap'):
    print(f'alcoin统计开始，统计参数{statdays}')
    '''
    根据Altcoin网站上山寨指数计算方式：If 75% of the Top 50 coins performed better than Bitcoin over the last season (90 days) it is Altcoin Season.
    Excluded from the Top 50 are Stablecoins (Tether, DAI…) and asset backed tokens (WBTC, stETH, cLINK,…)的方法
    '''
    # 过滤稳定币和资产支持代币
    blacklist = ['BTCDOMUSDT', 'WBTCUSDT', 'WBETHUSDT', 'BNSOLUSDT', 'USDCUSDT', 'PAXGUSDT']  # 示例黑名单，请根据需要修改
    # 过滤掉黑名单中的币种
    alcoin_df = alcoin_df[~alcoin_df['symbol'].isin(blacklist)]
    print("过滤黑名单币种完成！")

    # 按币种分组计算N日涨跌幅
    df_list = []
    for symbol, _df in alcoin_df.groupby('symbol'):
        for statday in statdays:
            _df[f'涨跌幅{statday}d'] = _df['close'].pct_change(statday)

        if interval == '1h':
            _df['成交额'] = _df['quote_volume'].rolling(48, min_periods=48).sum()  # 48h成交额
        elif interval == '1d':
            _df['成交额'] = _df['quote_volume'].rolling(365, min_periods=365).mean()  # 过滤过去一年成交额最大的50个B构建指数
        df_list.append(_df)
    alcoin_df = pd.concat(df_list)
    alcoin_df.reset_index(inplace=True)

    # 计算山寨指数
    final_df = pd.DataFrame(columns=['candle_begin_time', 'BTC排名', '全币种数量', '山寨指数'])
    for candle_begin_time, _df in alcoin_df.groupby('candle_begin_time'):
        _df: pd.DataFrame = _df
        # 过滤成交额前50
        _df['成交额排名'] = _df['成交额'].rank(ascending=False, method='first')
        _df = _df[_df['成交额排名'] <= 50]

        # 通过涨跌幅排名计算山寨指数
        altcoin_index_sum = 0
        for statday in statdays:
            _df[f'涨跌幅排名{statday}d'] = _df[f'涨跌幅{statday}d'].rank(ascending=False, method='first')
            # 安全版本 ✅
            btc_row = _df[_df['symbol'] == 'BTCUSDT']
            total_rank = len(_df)
            if not btc_row.empty:
                btc_rank = btc_row[f'涨跌幅排名{statday}d'].iloc[0]
            else:
                # print(f"警告：未找到 BTCUSDT 在 {candle_begin_time} 时间点的数据")
                btc_rank = total_rank + 1  # BTC 不在名单内，则排最后一名
                continue  # 或者设为默认值、跳过该时间点计算

            if pd.isnull(btc_rank) or btc_rank > total_rank:
                btc_rank = total_rank

            altcoin_index = round(btc_rank / total_rank, 2)

            altcoin_index_sum += altcoin_index
        altcoin_index = altcoin_index_sum / len(statdays)
        data = {'candle_begin_time': candle_begin_time, 'BTC排名': btc_rank, '全币种数量': total_rank,
                '山寨指数': altcoin_index}
        row_df = pd.DataFrame(data, columns=['candle_begin_time', 'BTC排名', '全币种数量', '山寨指数'], index=[0])
        final_df = pd.concat([final_df, row_df], ignore_index=True)

    if start_time is not None:
        final_df = final_df[final_df['candle_begin_time'] > start_time]

    # 假设 save_name 和 market_type 已定义
    save_dir = os.path.join('/Users/houjl/Downloads/FLdata', market_type)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, filename + '.csv')

    final_df.to_csv(save_path, index=False, encoding='gbk')
    print('alcoin统计完成：', final_df)



    if save_img:
        draw_index(final_df, market_type, title=f'altcoin_index_{market_type}_{statdays}d', xaxle='山寨指数', min_val=0.05, max_val=0.75, border=0.25,
                   border_n=2, save_name=filename+'_v2', axhline_high=0.75, axhline_low=0.25, axhline_low2=0.1)

    return final_df


def market_zdf_stat(market_df, statdays=[30], save_img=True, start_time=None, interval='1d', filename='marketzdf_index30', market_type='swap'):
    print(f'market_zdf统计开始，统计参数{statdays}')
    # 按币种分组计算N日涨跌幅
    df_list = []
    for symbol, _df in market_df.groupby('symbol'):
        for statday in statdays:
            _df[f'涨跌幅{statday}d'] = _df['close'].pct_change(statday)

        if interval == '1h':
            _df['成交额'] = _df['quote_volume'].rolling(24 * 7, min_periods=7).sum()  # 7d成交额
        elif interval == '1d':
            _df['成交额'] = _df['quote_volume'].rolling(7, min_periods=7).sum()  # 7d成交额
        df_list.append(_df)
    market_df = pd.concat(df_list)
    market_df.reset_index(inplace=True)

    '''
    指数计算：
        对每个时间点：
        筛选成交额排名前20的币种
        计算这些币种在不同统计周期的平均涨跌幅
        最终指数 = 所有统计周期的平均涨跌幅的平均值
    '''
    dfs = []
    for candle_begin_time, _df in market_df.groupby('candle_begin_time'):
        _df = _df.copy()

        # 过滤成交额前n
        _df['成交额排名'] = _df['成交额'].rank(ascending=False, method='first')
        _df = _df[_df['成交额排名'] <= 50]

        marketdzf_index_sum = 0
        row = {'candle_begin_time': candle_begin_time}
        for statday in statdays:
            marketzdf_index = _df[f'涨跌幅{statday}d'].sum() / len(_df)
            marketdzf_index_sum += marketzdf_index
            row[f'全市场涨跌幅指数{statday}d'] = marketzdf_index
        marketzdf_index = marketdzf_index_sum / len(statdays)
        row['全市场涨跌幅指数'] = marketzdf_index
        dfs.append(pd.DataFrame([row]))

    final_df = pd.concat(dfs, ignore_index=True)

    if start_time is not None:
        final_df = final_df[final_df['candle_begin_time'] > start_time]

    # 假设 save_name 和 market_type 已定义
    save_dir = os.path.join('/Users/houjl/Downloads/FLdata', market_type)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, filename + '.csv')

    final_df.to_csv(save_path, index=False, encoding='gbk')
    print('market_zdf统计完成：', final_df)

    if save_img:
        draw_index(final_df, market_type, title=f'market_zdf_{market_type}_{statdays}d', xaxle='全市场涨跌幅指数', min_val=-0.75, max_val=1, border=0.25,
                   border_n=20, save_name=filename+'_v2', axhline_high=1, axhline_low=0, axhline_low2=-0.3)

    return final_df


def get_default_exchange(acc:str):
    api : BnAccount = cfg.binance.getApi(acc)
    exchange = ccxt.binance({
        'apiKey': api.api_key,
        'secret': api.api_secret,
        'timeout': cfg.binance.timeout,  # ms
        'rateLimit': cfg.binance.rateLimit, # ms
        'verbose': cfg.binance.verbose,
        'hostname': cfg.binance.hostname,
        'enableRateLimit': cfg.binance.enableRateLimit,
        'proxies': cfg.binance.proxies
    })
    return exchange


def close_exchange(exchange):
    """关闭 exchange 连接"""
    try:
        if exchange and hasattr(exchange, 'close'):
            exchange.close()
    except Exception as e:
        print(f"关闭 exchange 连接时出错: {e}")



def load_local_data(market_type='swap', start_time='2021-01-01'):
    """
    从本地CSV文件读取数据并聚合为日线数据
    """
    print(f'正在从本地读取数据，数据类型{market_type}')
    
    # 设置本地数据路径
    local_data_path = f'/Users/houjl/Downloads/FLdata/coin-binance-spot-swap-preprocess-pkl-1h/split/{market_type}/'
    
    # 获取所有CSV文件
    import glob
    csv_files = glob.glob(os.path.join(local_data_path, '*.csv'))
    print(f'找到 {len(csv_files)} 个币种数据文件')
    
    df_list = []
    total_files = len(csv_files)
    
    for idx, csv_file in enumerate(csv_files, 1):
        try:
            # 每处理50个文件显示一次进度
            if idx % 50 == 0 or idx == total_files:
                print(f'进度: {idx}/{total_files} ({idx*100//total_files}%)')
            
            # 读取CSV文件，只读取需要的列
            df = pd.read_csv(csv_file, 
                           usecols=['candle_begin_time', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', '是否交易'],
                           parse_dates=['candle_begin_time'])
            
            # 过滤有效数据
            df = df[df['是否交易'] == 1].copy()
            
            if len(df) == 0:
                continue
            
            # 提取symbol名称（从文件名）
            symbol_name = os.path.basename(csv_file).replace('.csv', '').replace('-', '')
            df['symbol'] = symbol_name
            
            # 聚合为日线数据
            df.set_index('candle_begin_time', inplace=True)
            df_daily = df.resample('D').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'quote_volume': 'sum',
                'symbol': 'first'
            }).dropna()
            
            df_daily.reset_index(inplace=True)
            df_list.append(df_daily)
            
        except Exception as e:
            print(f'读取文件 {os.path.basename(csv_file)} 失败: {e}')
            continue
    
    print(f'成功读取 {len(df_list)} 个币种的数据')
    
    # 合并所有数据
    print('正在合并数据...')
    all_df = pd.concat(df_list, ignore_index=True)
    print(f'合并完成，共 {len(all_df)} 条记录')
    
    # 过滤起始时间
    if start_time:
        print(f'过滤起始时间 >= {start_time}')
        all_df = all_df[all_df['candle_begin_time'] >= start_time]
        print(f'过滤后剩余 {len(all_df)} 条记录')
    
    return all_df


def download_data(acc:str, backdays=1800, interval = '1d', start_time='2024-01-01', market_type='swap'):
    print(f'正在下载数据，数据类型{market_type}')
    exchange = get_default_exchange(acc)
    try:
        # 获取合约数据
        if market_type == 'swap':
            # 获取永续合约交易对
            symbol_list = binance.get_symbol_list(exchange, market_type='swap')

        elif market_type == 'spot':
            # 获取现货交易对
            symbol_list = binance.get_symbol_list(exchange, market_type='spot')

        else:
            raise ValueError("market_type 必须是 'swap' 或 'spot'")

        run_time = common.cacu_run_time('1h', datetime.now())

        if interval == '1h':
            df_dict = binance.u_furture_fetch_all_candle_data(exchange, symbol_list, '1h', run_time, 24 * backdays * 2 + 10, market_type, njobs=8)
        elif interval == '1d':
            df_dict = binance.u_furture_fetch_all_candle_data(exchange, symbol_list, '1d', run_time, backdays * 2 + 10, market_type, njobs=8)

        # 全币种数据合成一个df
        df_list = []
        for symbol in df_dict:
            df = df_dict[symbol]
            df_list.append(df)
        all_df = pd.concat(df_list)
        all_df.reset_index(inplace=True)
        # print('null rows:', all_df.isna().any(axis=1).sum())
        all_df.to_csv(f'/Users/houjl/Downloads/FLdata/{market_type}/all_df_from_Y_idx_newV2.csv', index=False, encoding='gbk')
        print('数据储存完成')
        print('数据下载完成，开始计算指数')

        # =====权重涨跌幅指数=====
        print('开始计算涨跌幅指数')
        market_df = pd.DataFrame()
        for i in [7, 30, 90]:
            market_df = all_df.copy()
            if i == 30:
                mdf = market_zdf_stat(market_df, statdays=[i], save_img=True, start_time=start_time, interval='1d',
                                filename=f'marketzdf_index{i}', market_type=market_type)
            elif i == 90:
                mdf90 = market_zdf_stat(market_df, statdays=[i], save_img=True, start_time=start_time, interval='1d',
                                filename=f'marketzdf_index{i}', market_type=market_type)
            else:
                mdf90 = market_zdf_stat(market_df, statdays=[i], save_img=False, start_time=start_time, interval='1d',
                                filename=f'marketzdf_index{i}', market_type=market_type)


        # =====山寨指数=====
        print('开始计算山寨指数')
        # 画一个月山寨曲线看看
        alcoin_df30 = all_df.copy()
        adf = alcoin_stat(alcoin_df30, statdays=[30], save_img=True, start_time=start_time, interval='1d', filename='altcoin_index30', market_type=market_type)

        # 画一个季山寨曲线看看
        alcoin_df90 = all_df.copy()
        adf90 = alcoin_stat(alcoin_df90, statdays=[90], save_img=True, start_time=start_time, interval='1d', filename='altcoin_index90', market_type=market_type)

        # 画一个年山寨曲线看看
        alcoin_stat(all_df, statdays=[365], save_img=True, start_time=start_time, interval='1d', filename='altcoin_index365', market_type=market_type)

        return adf, mdf, adf90, mdf90
    finally:
        # 确保关闭 exchange 连接
        close_exchange(exchange)



def run_with_local_data(market_type='swap', start_time='2021-01-01'):
    """
    使用本地数据运行Y指数计算
    """
    print(f'开始处理{market_type}数据')
    
    # 从本地读取数据
    all_df = load_local_data(market_type=market_type, start_time=start_time)
    
    # 保存合并后的数据
    save_dir = os.path.join('/Users/houjl/Downloads/FLdata', market_type)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    all_df.to_csv(f'/Users/houjl/Downloads/FLdata/{market_type}/all_df_from_Y_idx_newV2.csv', index=False, encoding='gbk')
    print('数据储存完成')
    
    # =====权重涨跌幅指数=====
    print('开始计算涨跌幅指数')
    for i in [7, 30, 90]:
        market_df = all_df.copy()
        if i == 30:
            mdf = market_zdf_stat(market_df, statdays=[i], save_img=True, start_time=start_time, interval='1d',
                            filename=f'marketzdf_index{i}', market_type=market_type)
        elif i == 90:
            mdf90 = market_zdf_stat(market_df, statdays=[i], save_img=True, start_time=start_time, interval='1d',
                            filename=f'marketzdf_index{i}', market_type=market_type)
        else:
            mdf7 = market_zdf_stat(market_df, statdays=[i], save_img=False, start_time=start_time, interval='1d',
                            filename=f'marketzdf_index{i}', market_type=market_type)

    # =====山寨指数=====
    print('开始计算山寨指数')
    # 画一个月山寨曲线看看
    alcoin_df30 = all_df.copy()
    adf = alcoin_stat(alcoin_df30, statdays=[30], save_img=True, start_time=start_time, interval='1d', filename='altcoin_index30', market_type=market_type)

    # 画一个季山寨曲线看看
    alcoin_df90 = all_df.copy()
    adf90 = alcoin_stat(alcoin_df90, statdays=[90], save_img=True, start_time=start_time, interval='1d', filename='altcoin_index90', market_type=market_type)

    # 画一个年山寨曲线看看
    alcoin_stat(all_df, statdays=[365], save_img=True, start_time=start_time, interval='1d', filename='altcoin_index365', market_type=market_type)

    return adf, mdf, adf90, mdf90


def run(market_type='swap', start_time='2021-01-01'):
    # df1是山寨指数，df2是全市场涨跌幅指数
    df1, df2, df1_90, df2_90 = download_data(acc='qqdev', backdays=1800, interval='1d', start_time=start_time, market_type=market_type)

    # =========30天Y指数================================================
    # 确保candle_begin_time列是日期时间格式
    df1['candle_begin_time'] = pd.to_datetime(df1['candle_begin_time'])
    df2['candle_begin_time'] = pd.to_datetime(df2['candle_begin_time'])

    # 按candle_begin_time列合并
    merged_df = pd.merge(df1, df2, on='candle_begin_time', how='inner')

    # 按时间排序
    merged_df = merged_df.sort_values('candle_begin_time')
    print(merged_df)

    merged_df = merged_df[['candle_begin_time', '全市场涨跌幅指数', '山寨指数']]
    merged_df['Y_idx'] = (merged_df['全市场涨跌幅指数'] + merged_df['山寨指数']) * 100

    # 调用绘图函数
    draw_index(merged_df, market_type, title=f'Yindex_{market_type}', xaxle='Y_idx', min_val=-50, max_val=150, border=10,
               border_n=18, save_name=f'Y_idx_v2_{market_type}', axhline_high=150, axhline_low=0, axhline_low2=-20)

    # 保存Y指数数据
    merged_df[['candle_begin_time', 'Y_idx']].to_csv(f'/Users/houjl/Downloads/FLdata/{market_type}/Y_idx_V2.csv', index=False)

    # =========90天Y指数================================================
    # 确保candle_begin_time列是日期时间格式
    df1_90['candle_begin_time'] = pd.to_datetime(df1_90['candle_begin_time'])
    df2_90['candle_begin_time'] = pd.to_datetime(df2_90['candle_begin_time'])

    # 按candle_begin_time列合并
    merged_df90 = pd.merge(df1_90, df2_90, on='candle_begin_time', how='inner')

    # 按时间排序
    merged_df90 = merged_df90.sort_values('candle_begin_time')
    print(merged_df90)

    merged_df90 = merged_df90[['candle_begin_time', '全市场涨跌幅指数', '山寨指数']]
    merged_df90['Y_idx90'] = (merged_df90['全市场涨跌幅指数'] + merged_df90['山寨指数']) * 100

    # 调用绘图函数
    draw_index(merged_df90, market_type, title=f'Yindex90_{market_type}', xaxle='Y_idx90', min_val=-50, max_val=150, border=10,
               border_n=18, save_name=f'Y_idx90_v2_{market_type}', axhline_high=200, axhline_low=0, axhline_low2=-20)

    # 保存Y指数数据
    merged_df90[['candle_begin_time', 'Y_idx90']].to_csv(f'/Users/houjl/Downloads/FLdata/{market_type}/Y_idx90_V2.csv', index=False)

    return


def job():
    # 使用循环而不是递归，避免进程无法退出
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 处理合约数据
            print('开始处理swap数据')
            df1_swap, df2_swap, df1_90_swap, df2_90_swap = run_with_local_data(market_type='swap', start_time='2021-01-01')

            print('等待3秒计算spot数据')
            print(datetime.now())
            # 休息3秒后处理现货数据
            time.sleep(3)
            print('休息完成，开始计算spot数据')
            print(datetime.now())

            # 处理现货数据
            df1_spot, df2_spot, df1_90_spot, df2_90_spot = run_with_local_data(market_type='spot', start_time='2021-01-01')
            
            # =========计算Y指数（swap）================================================
            print('开始计算swap的Y指数')
            # 30天Y指数
            df1_swap['candle_begin_time'] = pd.to_datetime(df1_swap['candle_begin_time'])
            df2_swap['candle_begin_time'] = pd.to_datetime(df2_swap['candle_begin_time'])
            merged_df_swap = pd.merge(df1_swap, df2_swap, on='candle_begin_time', how='inner')
            merged_df_swap = merged_df_swap.sort_values('candle_begin_time')
            merged_df_swap = merged_df_swap[['candle_begin_time', '全市场涨跌幅指数', '山寨指数']]
            merged_df_swap['Y_idx'] = (merged_df_swap['全市场涨跌幅指数'] + merged_df_swap['山寨指数']) * 100
            draw_index(merged_df_swap, 'swap', title=f'Yindex_swap', xaxle='Y_idx', min_val=-50, max_val=150, border=10,
                       border_n=18, save_name=f'Y_idx_v2_swap', axhline_high=150, axhline_low=0, axhline_low2=-20)
            merged_df_swap[['candle_begin_time', 'Y_idx']].to_csv(f'/Users/houjl/Downloads/FLdata/swap/Y_idx_V2.csv', index=False)
            
            # 90天Y指数
            df1_90_swap['candle_begin_time'] = pd.to_datetime(df1_90_swap['candle_begin_time'])
            df2_90_swap['candle_begin_time'] = pd.to_datetime(df2_90_swap['candle_begin_time'])
            merged_df90_swap = pd.merge(df1_90_swap, df2_90_swap, on='candle_begin_time', how='inner')
            merged_df90_swap = merged_df90_swap.sort_values('candle_begin_time')
            merged_df90_swap = merged_df90_swap[['candle_begin_time', '全市场涨跌幅指数', '山寨指数']]
            merged_df90_swap['Y_idx90'] = (merged_df90_swap['全市场涨跌幅指数'] + merged_df90_swap['山寨指数']) * 100
            draw_index(merged_df90_swap, 'swap', title=f'Yindex90_swap', xaxle='Y_idx90', min_val=-50, max_val=150, border=10,
                       border_n=18, save_name=f'Y_idx90_v2_swap', axhline_high=200, axhline_low=0, axhline_low2=-20)
            merged_df90_swap[['candle_begin_time', 'Y_idx90']].to_csv(f'/Users/houjl/Downloads/FLdata/swap/Y_idx90_V2.csv', index=False)
            
            # =========计算Y指数（spot）================================================
            print('开始计算spot的Y指数')
            print(f'df1_spot shape: {df1_spot.shape}, df2_spot shape: {df2_spot.shape}')
            
            # 30天Y指数
            df1_spot['candle_begin_time'] = pd.to_datetime(df1_spot['candle_begin_time'])
            df2_spot['candle_begin_time'] = pd.to_datetime(df2_spot['candle_begin_time'])
            print('开始合并spot的30天数据')
            merged_df_spot = pd.merge(df1_spot, df2_spot, on='candle_begin_time', how='inner')
            print(f'合并后数据shape: {merged_df_spot.shape}')
            merged_df_spot = merged_df_spot.sort_values('candle_begin_time')
            merged_df_spot = merged_df_spot[['candle_begin_time', '全市场涨跌幅指数', '山寨指数']]
            merged_df_spot['Y_idx'] = (merged_df_spot['全市场涨跌幅指数'] + merged_df_spot['山寨指数']) * 100
            print('开始绘制spot的Y_idx图表')
            draw_index(merged_df_spot, 'spot', title=f'Yindex_spot', xaxle='Y_idx', min_val=-50, max_val=150, border=10,
                       border_n=18, save_name=f'Y_idx_v2_spot', axhline_high=150, axhline_low=0, axhline_low2=-20)
            merged_df_spot[['candle_begin_time', 'Y_idx']].to_csv(f'/Users/houjl/Downloads/FLdata/spot/Y_idx_V2.csv', index=False)
            print('spot的30天Y指数计算完成')
            
            # 90天Y指数
            print('开始计算spot的90天Y指数')
            df1_90_spot['candle_begin_time'] = pd.to_datetime(df1_90_spot['candle_begin_time'])
            df2_90_spot['candle_begin_time'] = pd.to_datetime(df2_90_spot['candle_begin_time'])
            print('开始合并spot的90天数据')
            merged_df90_spot = pd.merge(df1_90_spot, df2_90_spot, on='candle_begin_time', how='inner')
            print(f'合并后90天数据shape: {merged_df90_spot.shape}')
            merged_df90_spot = merged_df90_spot.sort_values('candle_begin_time')
            merged_df90_spot = merged_df90_spot[['candle_begin_time', '全市场涨跌幅指数', '山寨指数']]
            merged_df90_spot['Y_idx90'] = (merged_df90_spot['全市场涨跌幅指数'] + merged_df90_spot['山寨指数']) * 100
            print('开始绘制spot的Y_idx90图表')
            draw_index(merged_df90_spot, 'spot', title=f'Yindex90_spot', xaxle='Y_idx90', min_val=-50, max_val=150, border=10,
                       border_n=18, save_name=f'Y_idx90_v2_spot', axhline_high=200, axhline_low=0, axhline_low2=-20)
            merged_df90_spot[['candle_begin_time', 'Y_idx90']].to_csv(f'/Users/houjl/Downloads/FLdata/spot/Y_idx90_V2.csv', index=False)
            print('spot的90天Y指数计算完成')

            # 绘制合约现货比曲线
            df_swap = pd.DataFrame()
            df_spot = pd.DataFrame()
            df_swap_spot = pd.DataFrame()
            
            # 确保 ALL 目录存在
            all_dir = '/Users/houjl/Downloads/FLdata/ALL'
            if not os.path.exists(all_dir):
                os.makedirs(all_dir)
                print(f'创建目录: {all_dir}')
            
            for i in [7, 30]:
                print(f'开始处理合约现货比{i}天数据')
                for s in ['swap', 'spot']:
                    try:
                        if s == 'swap':
                            df_swap = pd.read_csv(f'/Users/houjl/Downloads/FLdata/{s}/marketzdf_index{i}.csv', encoding='gbk', usecols=['candle_begin_time', f'全市场涨跌幅指数{i}d'])
                            df_swap.rename(columns={f'全市场涨跌幅指数{i}d': f'market_{s}_{i}d'}, inplace=True)
                            print(f'成功读取 {s} 市场 {i}天数据')
                        if s == 'spot':
                            df_spot = pd.read_csv(f'/Users/houjl/Downloads/FLdata/{s}/marketzdf_index{i}.csv', encoding='gbk', usecols=['candle_begin_time', f'全市场涨跌幅指数{i}d'])
                            df_spot.rename(columns={f'全市场涨跌幅指数{i}d': f'market_{s}_{i}d'}, inplace=True)
                            print(f'成功读取 {s} 市场 {i}天数据')
                    except Exception as e:
                        print(f'读取 {s} 市场 {i}天数据失败: {e}')
                        raise
                
                # 合并及计算期货现货比
                print(f'开始合并 {i}天数据')
                df_swap_spot = pd.merge(df_swap, df_spot, on='candle_begin_time', how='inner')
                df_swap_spot.to_csv(f'/Users/houjl/Downloads/FLdata/ALL/df_swap_spot_{i}.csv', index=False, encoding='gbk')
                print(f'成功保存合并后的 {i}天数据')
                if i == 7:
                    # 调用绘图函数画图
                    draw_index_list(df_swap_spot, market_type='ALL', title=f'market_{i}d',
                                    xaxle_list=[f'market_swap_{i}d', f'market_spot_{i}d'], min_val=-0.35, max_val=0.35,
                                    border=0.15, border_n=6, save_name=f'market_{i}d', axhline_high=0.5, axhline_low=0,
                                    axhline_low2=-0.25, days_limit=180)
                else:
                    # 调用绘图函数画图
                    draw_index_list(df_swap_spot, market_type='ALL', title=f'market_{i}d',
                                    xaxle_list=[f'market_swap_{i}d', f'market_spot_{i}d'], min_val=-0.75, max_val=1,
                                    border=0.15, border_n=25, save_name=f'market_{i}d', axhline_high=1, axhline_low=0,
                                    axhline_low2=-0.3, days_limit=600)
            
            # 任务成功完成，退出循环
            break

        except Exception as e:
            retry_count += 1
            print(f"任务执行失败（第{retry_count}次）：{e}")
            import traceback
            print(traceback.format_exc())
            if retry_count < max_retries:
                print(f"等待10分钟后重试...")
                time.sleep(10 * 60)
            else:
                print(f"已达到最大重试次数({max_retries})，程序退出")
                raise  # 重新抛出异常，让程序知道失败了


if __name__ == '__main__':
    try:
        print(datetime.now())
        print('程序启动')
        job()
        print(datetime.now())
        print('统计完成！程序休息等待下次工作时间执行')
    except KeyboardInterrupt:
        print('\n程序被用户中断')
        sys.exit(0)
    except Exception as e:
        print(f'程序执行出错: {e}')
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
    finally:
        # 确保所有资源都被释放
        import matplotlib.pyplot as plt
        plt.close('all')  # 关闭所有图形窗口
        print('资源清理完成，程序退出')