'''
山寨指数
参考：https://www.blockchaincenter.net/altcoin-season-index/

月度指标/季度指标/年度指标

过去一个月/季度/年
山寨指数 = 全市场前50涨跌幅名中 > BTC涨跌幅的币种数量 / 50

'''

# 设置 matplotlib 使用非交互式后端，避免进程无法退出
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

from wechart_funtion import *
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.ticker import MaxNLocator, FuncFormatter
import os

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_rows', 500)  # 最多显示数据的行数
pd.set_option('display.max_columns', 500)  # 最多显示数据的列数
pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
plt.rcParams['font.sans-serif'] = ['PingFang HK', 'Arial Unicode MS', 'SimSun']


def draw_index(df, market_type, title='', xaxle='', min_val=0.25, max_val=0.75, border =0.25, border_n= 1,
               save_name='xxx.png', axhline_high=0.75, axhline_low=0.25, axhline_low2=0.1):
    """
    df Dataframe
    title= 输出图片标题
    xaxle= csv里面要读取数据的值，比如山寨指数，比如全市场涨跌幅30日指数
    min_val = 数据最低限，山寨指数的0。25，涨跌幅指数是-0.9        （小于这个变紫色）
    max_val = 数据最高限，山寨指数的 0.75，涨跌幅指数是 1  （大于这个就变红）
    border =0.25  怕数据超出y轴，给上下预留,这个是下边界，山寨+全市场下限都是0.25，上线山寨是0.25，全市场是2.5
    border_n= 1,   border*border_n=上边界预留距离，如果n=1说明上下预留距离相等。 山寨是1，全市场指数是10
    save_name='altcoin_index.png', 保存图片名称
    axhline_high=0.75,  山寨上平衡线，全市场涨跌幅是 1
    axhline_low=0.25, 山寨下平衡线，全市场涨跌幅是 -0.3
    axhline_low2=0.1):

    显示资金曲线图
    """

    # 确保 candle_begin_time 列是 datetime 类型
    df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])

    # 创建图表
    fig, ax = plt.subplots(figsize=(32, 8))

    # 设置颜色映射范围
    norm = Normalize(vmin=min_val, vmax=max_val)
    cmap = plt.cm.rainbow  # 使用彩虹色图谱

    def get_color(y):
        return cmap(norm(y))  # 根据y值归一化后获取对应的颜色

    # 将时间转换为数值以便绘图
    time_values = df['candle_begin_time'].map(pd.Timestamp.toordinal)

    # 检查 time_values 是否包含有效值
    if any(time_values < 1):
        raise ValueError("Some time values are invalid (less than 1).")

    # 绘制线条
    for i in range(len(time_values) - 1):
        x = [time_values.iloc[i], time_values.iloc[i + 1]]
        y = [df[xaxle].iloc[i], df[xaxle].iloc[i + 1]]
        color = get_color((y[0] + y[1]) / 2)
        ax.plot(x, y, color=color, linewidth=2)

    # 设置y轴限制以确保所有数据可见
    ax.set_ylim(min_val - border, max_val + border * border_n)

    # 添加水平虚线
    ax.axhline(y=axhline_high, color='red', linestyle='--', alpha=0.7)
    ax.axhline(y=axhline_low, color='green', linestyle='--', alpha=0.7)
    if axhline_low2 is not None:  # 检查axhline_low2是否被赋予有效值
        ax.axhline(y=axhline_low2, color='blue', linestyle='--', alpha=0.7)

    # 在这里添加颜色条
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.ax.set_ylabel('指数值', rotation=90)

    # 获取最后一个数据点的值并标注在右上角
    last_value = df[xaxle].iloc[-1]
    last_date = df['candle_begin_time'].iloc[-1]
    annotation_text = f"Latest Date: {last_date.strftime('%Y-%m-%d')}\nValue: {last_value:.2f}"
    ax.annotate(annotation_text, xy=(1.0, 1.0), xycoords='axes fraction',
                fontsize=12, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
                xytext=(-10, -10), textcoords='offset points')

    # 设置图表标题和标签
    ax.set_title(title, fontsize=15)
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('指数值', fontsize=12)

    # 优化 y 轴刻度显示
    from matplotlib.ticker import MaxNLocator, FuncFormatter
    # 设置最多显示 10 个刻度
    ax.yaxis.set_major_locator(MaxNLocator(nbins=10))
    # 可选：设置格式为保留两位小数（如果你希望统一显示格式）
    def format_func(value, tick_number):
        return f'{value:.2f}'
    ax.yaxis.set_major_formatter(FuncFormatter(format_func))


    # 优化x轴显示
    locator = plt.MaxNLocator(20)  # 限制X轴标签数量
    formatter = plt.FuncFormatter(lambda x, pos: pd.Timestamp.fromordinal(int(x)).strftime('%Y-%m-%d'))
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(rotation=45)

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)

    # 调整布局
    plt.tight_layout()

    # 假设 save_name 和 market_type 已定义
    save_dir = os.path.join('/Users/houjl/Downloads/FLdata', market_type)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    save_path = os.path.join(save_dir, save_name + '.png')

    # 保存图表
    plt.savefig(save_path)
    send_wechat_work_img(save_path)
    plt.clf()
    plt.cla()
    plt.close(fig)  # 显式关闭 figure 对象


def draw_index_list(df, market_type, title='', xaxle_list=None, min_val=0.25, max_val=0.75, border=0.25, border_n=1,
                    save_name='xxx.png', axhline_high=0.75, axhline_low=0.25, axhline_low2=0.1, days_limit=None):
    """
    df: Dataframe
    title: 输出图片标题
    xaxle_list: 要绘制的列名列表，如['market_swap_7d', 'market_spot_7d']
    其他参数同上...
    """

    # === ✅ 关键修复：安全地转换时间列，避免越界 ===
    df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])

    # === 新增逻辑：如果设置了days_limit，则只保留最近days_limit天的数据 ===
    if days_limit is not None and days_limit > 0:
        end_date = df['candle_begin_time'].max()
        start_date = end_date - pd.Timedelta(days=days_limit)
        df = df[df['candle_begin_time'] >= start_date]

    # 创建图表
    fig, ax = plt.subplots(figsize=(32, 8))

    # === ✅ 固定颜色设置：蓝色 和 橙色 ===
    fixed_colors = ['blue', 'orange']  # 你指定的颜色

    for idx, column in enumerate(xaxle_list):
        # 将时间转换为数值以便绘图（使用 ordinal）
        time_values = df['candle_begin_time'].map(pd.Timestamp.toordinal)
        color = fixed_colors[idx % len(fixed_colors)]  # 循环使用颜色

        # 绘制整条线（不再分段）
        ax.plot(time_values, df[column], color=color, linewidth=2, label=column)

    # 设置y轴限制以确保所有数据可见
    ax.set_ylim(min_val - border, max_val + border * border_n)

    # 添加水平虚线
    ax.axhline(y=axhline_high, color='red', linestyle='--', alpha=0.7)
    ax.axhline(y=axhline_low, color='green', linestyle='--', alpha=0.7)
    if axhline_low2 is not None:
        ax.axhline(y=axhline_low2, color='blue', linestyle='--', alpha=0.7)

    # 获取最后一个数据点的值并标注在右上角
    last_value = df[xaxle_list[0]].iloc[-1]
    last_date = df['candle_begin_time'].iloc[-1]
    annotation_text = f"Latest Date: {last_date.strftime('%Y-%m-%d')}\nValue: {last_value:.2f}"
    ax.annotate(annotation_text, xy=(1.0, 1.0), xycoords='axes fraction',
                fontsize=12, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
                xytext=(-10, -10), textcoords='offset points')

    # 设置图表标题和标签
    ax.set_title(title, fontsize=15)
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('指数值', fontsize=12)

    # 优化 y 轴刻度显示
    ax.yaxis.set_major_locator(MaxNLocator(nbins=10))

    def format_func(value, tick_number):
        return f'{value:.2f}'

    ax.yaxis.set_major_formatter(FuncFormatter(format_func))

    # 优化x轴显示
    locator = plt.MaxNLocator(20)  # 限制X轴标签数量
    formatter = plt.FuncFormatter(lambda x, pos: pd.Timestamp.fromordinal(int(x)).strftime('%Y-%m-%d'))
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(rotation=45)

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)

    # 添加图例
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    # 调整布局
    plt.tight_layout()

    # 保存路径
    save_dir = os.path.join('/Users/houjl/Downloads/FLdata', market_type)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, save_name + '.png')

    # 保存图表
    plt.savefig(save_path)

    # ✅ 发送企业微信（保持原逻辑）
    send_wechat_work_img(save_path)

    # 清理
    plt.clf()
    plt.cla()
    plt.close(fig)  # 显式关闭 figure 对象




def plot_y_idx(df):
    """
    绘制Y指数走势图

    参数:
    df: DataFrame, 包含 'candle_begin_time' 和 'Y_idx' 列的数据框
    """

    # 确保 candle_begin_time 列是 datetime 类型
    df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])


    # 创建图表
    fig, ax = plt.subplots(figsize=(32, 8))

    # 根据Y_idx的值设置不同的颜色
    def get_color(y):
        if y > 150:
            return 'red'
        elif y < -50:
            return 'blue'
        else:
            norm_val = (y + 150) / 200  # Normalize to [0, 1]
            return plt.cm.viridis(norm_val)

    colors = [get_color(y) for y in df['Y_idx']]

    # 将时间转换为数值以便绘图
    time_values = df['candle_begin_time'].map(pd.Timestamp.toordinal)

    # 检查 time_values 是否包含有效值
    if any(time_values < 1):
        raise ValueError("Some time values are invalid (less than 1).")


    # 绘制线条
    for i in range(len(time_values) - 1):
        x = [time_values.iloc[i], time_values.iloc[i + 1]]
        y = [df['Y_idx'].iloc[i], df['Y_idx'].iloc[i + 1]]
        color = get_color((y[0] + y[1]) / 2)
        ax.plot(x, y, color=color, linewidth=2)

    # 设置y轴限制以确保所有数据可见
    ax.set_ylim(min(df['Y_idx']) - 10, max(df['Y_idx']) + 10)

    # 添加200和-10的水平虚线
    ax.axhline(y=200, color='red', linestyle='--', alpha=0.7)
    ax.axhline(y=-10, color='green', linestyle='--', alpha=0.7)

    # 获取最后一个数据点的值并标注在右上角
    last_value = df['Y_idx'].iloc[-1]
    last_date = df['candle_begin_time'].iloc[-1]
    annotation_text = f"Latest Date: {last_date.strftime('%Y-%m-%d')}\nValue: {last_value:.2f}"
    ax.annotate(annotation_text, xy=(1.0, 1.0), xycoords='axes fraction',
                fontsize=12, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
                xytext=(-10, -10), textcoords='offset points')

    # 设置图表标题和标签
    ax.set_title('Yindex', fontsize=15)
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('指数值', fontsize=12)

    # 优化x轴显示
    locator = plt.MaxNLocator(10)  # 限制X轴标签数量
    formatter = plt.FuncFormatter(lambda x, pos: pd.Timestamp.fromordinal(int(x)).strftime('%Y-%m-%d'))
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(rotation=45)

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)

    # 调整布局
    plt.tight_layout()

    # 保存图表
    plt.savefig('Y_idx.png')
    send_wechat_work_img('Y_idx.png')
    plt.clf()
    plt.cla()
    plt.close(fig)  # 显式关闭 figure 对象
