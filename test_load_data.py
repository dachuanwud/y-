import pandas as pd
import os
import glob

def test_load_local_data(market_type='swap'):
    """
    测试从本地CSV文件读取数据
    """
    print(f'正在从本地读取数据，数据类型{market_type}')
    
    # 设置本地数据路径
    local_data_path = f'/Users/houjl/Downloads/FLdata/coin-binance-spot-swap-preprocess-pkl-1h/split/{market_type}/'
    
    # 获取所有CSV文件
    csv_files = glob.glob(os.path.join(local_data_path, '*.csv'))
    print(f'找到 {len(csv_files)} 个币种数据文件')
    
    # 只测试前5个文件
    test_files = csv_files[:5]
    print(f'测试前5个文件: {[os.path.basename(f) for f in test_files]}')
    
    df_list = []
    for csv_file in test_files:
        try:
            print(f'正在读取: {os.path.basename(csv_file)}')
            # 读取CSV文件
            df = pd.read_csv(csv_file, parse_dates=['candle_begin_time'])
            print(f'  原始数据行数: {len(df)}')
            
            # 过滤有效数据
            df = df[df['是否交易'] == 1].copy()
            print(f'  有效交易数据行数: {len(df)}')
            
            if len(df) == 0:
                print(f'  跳过（无有效数据）')
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
            print(f'  日线数据行数: {len(df_daily)}')
            df_list.append(df_daily)
            
        except Exception as e:
            print(f'读取文件 {csv_file} 失败: {e}')
            import traceback
            traceback.print_exc()
            continue
    
    if len(df_list) > 0:
        # 合并所有数据
        all_df = pd.concat(df_list, ignore_index=True)
        print(f'\n成功读取数据，共 {len(all_df)} 条记录')
        print(f'数据列: {all_df.columns.tolist()}')
        print(f'\n数据示例:')
        print(all_df.head(10))
        return all_df
    else:
        print('没有读取到任何有效数据')
        return None

if __name__ == '__main__':
    test_load_local_data('swap')

