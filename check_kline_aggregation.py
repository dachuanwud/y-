"""
K线聚合验证脚本
检查从小时K线聚合到日K线的正确性
"""
import pandas as pd
import os
import glob
import warnings
warnings.filterwarnings("ignore")

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 200)


def check_single_file_aggregation(csv_file, verbose=True):
    """
    检查单个文件的K线聚合
    """
    symbol_name = os.path.basename(csv_file).replace('.csv', '').replace('-', '')
    
    if verbose:
        print(f'\n{"="*80}')
        print(f'正在检查: {symbol_name}')
        print(f'{"="*80}')
    
    # 读取原始数据
    df_raw = pd.read_csv(csv_file, parse_dates=['candle_begin_time'])
    
    if verbose:
        print(f'\n1. 原始数据信息:')
        print(f'   总行数: {len(df_raw)}')
        print(f'   列名: {df_raw.columns.tolist()}')
        print(f'   时间范围: {df_raw["candle_begin_time"].min()} 到 {df_raw["candle_begin_time"].max()}')
    
    # 过滤有效交易数据
    df = df_raw[df_raw['是否交易'] == 1].copy()
    
    if verbose:
        print(f'\n2. 有效交易数据:')
        print(f'   有效行数: {len(df)}')
        print(f'   过滤掉的行数: {len(df_raw) - len(df)}')
    
    if len(df) == 0:
        if verbose:
            print(f'   ⚠️ 警告: 没有有效交易数据')
        return None
    
    df['symbol'] = symbol_name
    
    # 检查时间戳的时区信息
    if verbose:
        print(f'\n3. 时间戳信息:')
        print(f'   时区信息: {df["candle_begin_time"].dt.tz}')
        sample_times = df["candle_begin_time"].head(5)
        print(f'   前5个时间戳示例:')
        for t in sample_times:
            print(f'     {t} (星期{t.dayofweek}, 小时{t.hour})')
    
    # 检查是否有重复的时间戳
    duplicates = df[df.duplicated(subset=['candle_begin_time'], keep=False)]
    if len(duplicates) > 0:
        print(f'\n   ⚠️ 警告: 发现 {len(duplicates)} 个重复的时间戳!')
        if verbose:
            print(f'   重复时间戳示例:')
            print(duplicates[['candle_begin_time', 'open', 'close']].head(10))
    
    # 检查时间序列的连续性
    df_sorted = df.sort_values('candle_begin_time').copy()
    df_sorted['time_diff'] = df_sorted['candle_begin_time'].diff()
    
    # 预期的时间间隔是1小时
    expected_diff = pd.Timedelta(hours=1)
    gaps = df_sorted[df_sorted['time_diff'] > expected_diff * 1.5]  # 允许一些误差
    
    if len(gaps) > 0 and verbose:
        print(f'\n   ⚠️ 警告: 发现 {len(gaps)} 个时间间隔大于1.5小时的间隙')
        print(f'   前5个间隙:')
        print(gaps[['candle_begin_time', 'time_diff']].head())
    
    # 执行聚合
    if verbose:
        print(f'\n4. 执行K线聚合 (小时 -> 日线):')
    
    df_for_agg = df.copy()
    df_for_agg.set_index('candle_begin_time', inplace=True)
    
    # 当前的聚合方式
    df_daily = df_for_agg.resample('D').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'quote_volume': 'sum',
        'symbol': 'first'
    }).dropna()
    
    df_daily.reset_index(inplace=True)
    
    if verbose:
        print(f'   聚合后行数: {len(df_daily)}')
        print(f'   聚合后时间范围: {df_daily["candle_begin_time"].min()} 到 {df_daily["candle_begin_time"].max()}')
    
    # 验证聚合的正确性 - 抽样检查几天
    if verbose:
        print(f'\n5. 抽样验证聚合结果:')
    
    # 取中间的3天进行详细检查
    sample_dates = df_daily['candle_begin_time'].iloc[len(df_daily)//2:len(df_daily)//2+3]
    
    issues_found = []
    
    for date in sample_dates:
        # 获取这一天的原始小时数据
        day_start = date
        day_end = date + pd.Timedelta(days=1)
        
        hourly_data = df[(df['candle_begin_time'] >= day_start) & 
                        (df['candle_begin_time'] < day_end)].copy()
        
        if len(hourly_data) == 0:
            continue
        
        # 获取聚合后的日线数据
        daily_row = df_daily[df_daily['candle_begin_time'] == date].iloc[0]
        
        # 手动计算预期值
        expected_open = hourly_data.sort_values('candle_begin_time')['open'].iloc[0]
        expected_high = hourly_data['high'].max()
        expected_low = hourly_data['low'].min()
        expected_close = hourly_data.sort_values('candle_begin_time')['close'].iloc[-1]
        expected_volume = hourly_data['volume'].sum()
        expected_quote_volume = hourly_data['quote_volume'].sum()
        
        # 对比结果
        if verbose:
            print(f'\n   日期: {date.date()} (包含 {len(hourly_data)} 个小时K线)')
            print(f'     Open  - 聚合: {daily_row["open"]:.6f}, 预期: {expected_open:.6f}, 匹配: {abs(daily_row["open"] - expected_open) < 1e-6}')
            print(f'     High  - 聚合: {daily_row["high"]:.6f}, 预期: {expected_high:.6f}, 匹配: {abs(daily_row["high"] - expected_high) < 1e-6}')
            print(f'     Low   - 聚合: {daily_row["low"]:.6f}, 预期: {expected_low:.6f}, 匹配: {abs(daily_row["low"] - expected_low) < 1e-6}')
            print(f'     Close - 聚合: {daily_row["close"]:.6f}, 预期: {expected_close:.6f}, 匹配: {abs(daily_row["close"] - expected_close) < 1e-6}')
            print(f'     Volume - 聚合: {daily_row["volume"]:.2f}, 预期: {expected_volume:.2f}, 匹配: {abs(daily_row["volume"] - expected_volume) < 1e-2}')
            print(f'     Quote Volume - 聚合: {daily_row["quote_volume"]:.2f}, 预期: {expected_quote_volume:.2f}, 匹配: {abs(daily_row["quote_volume"] - expected_quote_volume) < 1e-2}')
        
        # 检查是否有不匹配的情况
        if not (abs(daily_row["open"] - expected_open) < 1e-6 and
                abs(daily_row["high"] - expected_high) < 1e-6 and
                abs(daily_row["low"] - expected_low) < 1e-6 and
                abs(daily_row["close"] - expected_close) < 1e-6):
            issues_found.append(f'{date.date()}: OHLC值不匹配')
        
        # 检查是否有不完整的日线（少于20小时的数据被认为可能不完整）
        if len(hourly_data) < 20:
            issues_found.append(f'{date.date()}: 仅包含{len(hourly_data)}个小时K线（可能不完整）')
            if verbose:
                print(f'     ⚠️ 警告: 该日仅有 {len(hourly_data)} 个小时K线')
    
    # 检查整体的不完整日线数量
    if verbose:
        print(f'\n6. 检查不完整的日线:')
    
    incomplete_days = []
    for date in df_daily['candle_begin_time'].head(20):  # 检查前20天
        day_start = date
        day_end = date + pd.Timedelta(days=1)
        hourly_count = len(df[(df['candle_begin_time'] >= day_start) & 
                             (df['candle_begin_time'] < day_end)])
        if hourly_count < 24:
            incomplete_days.append((date, hourly_count))
    
    if len(incomplete_days) > 0 and verbose:
        print(f'   前20天中有 {len(incomplete_days)} 天数据不完整:')
        for date, count in incomplete_days[:5]:
            print(f'     {date.date()}: {count} 小时 (缺失 {24-count} 小时)')
    
    # 总结
    if verbose:
        print(f'\n7. 聚合验证总结:')
        if len(issues_found) == 0:
            print(f'   ✅ 抽样检查通过，聚合逻辑正确')
        else:
            print(f'   ⚠️ 发现 {len(issues_found)} 个潜在问题:')
            for issue in issues_found:
                print(f'     - {issue}')
    
    return {
        'symbol': symbol_name,
        'total_rows': len(df_raw),
        'valid_rows': len(df),
        'daily_rows': len(df_daily),
        'has_duplicates': len(duplicates) > 0,
        'has_gaps': len(gaps) > 0,
        'incomplete_days': len(incomplete_days),
        'issues': issues_found
    }


def check_aggregation_for_market(market_type='swap', max_files=3):
    """
    检查指定市场类型的K线聚合
    """
    print(f'\n{"#"*80}')
    print(f'# 检查 {market_type.upper()} 市场的K线聚合')
    print(f'{"#"*80}')
    
    local_data_path = f'/Users/houjl/Downloads/FLdata/coin-binance-spot-swap-preprocess-pkl-1h/split/{market_type}/'
    
    if not os.path.exists(local_data_path):
        print(f'❌ 错误: 路径不存在 {local_data_path}')
        return
    
    csv_files = glob.glob(os.path.join(local_data_path, '*.csv'))
    print(f'\n找到 {len(csv_files)} 个币种数据文件')
    
    if len(csv_files) == 0:
        print(f'❌ 错误: 没有找到任何CSV文件')
        return
    
    # 只检查前几个文件
    test_files = csv_files[:max_files]
    print(f'将检查前 {len(test_files)} 个文件')
    
    results = []
    for csv_file in test_files:
        result = check_single_file_aggregation(csv_file, verbose=True)
        if result:
            results.append(result)
    
    # 汇总报告
    print(f'\n{"#"*80}')
    print(f'# 汇总报告')
    print(f'{"#"*80}')
    print(f'\n总共检查了 {len(results)} 个币种')
    
    total_issues = sum(len(r['issues']) for r in results)
    files_with_duplicates = sum(1 for r in results if r['has_duplicates'])
    files_with_gaps = sum(1 for r in results if r['has_gaps'])
    files_with_incomplete = sum(1 for r in results if r['incomplete_days'] > 0)
    
    print(f'\n问题统计:')
    print(f'  - 发现聚合问题的文件数: {sum(1 for r in results if len(r["issues"]) > 0)}')
    print(f'  - 总问题数: {total_issues}')
    print(f'  - 有重复时间戳的文件数: {files_with_duplicates}')
    print(f'  - 有时间间隙的文件数: {files_with_gaps}')
    print(f'  - 有不完整日线的文件数: {files_with_incomplete}')
    
    if total_issues == 0 and files_with_duplicates == 0:
        print(f'\n✅ 结论: K线聚合逻辑正确，未发现问题')
    else:
        print(f'\n⚠️ 结论: 发现一些需要注意的问题')
        print(f'\n建议:')
        if files_with_duplicates > 0:
            print(f'  1. 检查并去除重复的时间戳')
        if files_with_incomplete > 0:
            print(f'  2. 不完整的日线数据可能影响指标计算的准确性')
        if files_with_gaps > 0:
            print(f'  3. 时间间隙可能导致某些日期的数据缺失')


if __name__ == '__main__':
    # 检查swap市场
    check_aggregation_for_market('swap', max_files=3)
    
    print('\n' + '='*80 + '\n')
    
    # 检查spot市场
    check_aggregation_for_market('spot', max_files=3)



