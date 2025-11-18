# import matplotlib.pyplot as plt
import os.path
import base64
import hashlib
import requests
import json
import traceback
import time


# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
wx_webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=3c6aeee7-f437-4601-adb9-a58bd9a97132'

# 上传图片，解析bytes
class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        """
        只要检查到了是bytes类型的数据就把它转为str类型
        :param obj:
        :return:
        """
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


# 企业微信发送图片
def send_wechat_work_img(file_path, url=wx_webhook_url):
    if not os.path.exists(file_path):
        print('找不到图片')
        return
    if not url:
        print('未配置wechat_webhook_url，不发送信息')
        return
    try:
        with open(file_path, 'rb') as f:
            image_content = f.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        md5 = hashlib.md5()
        md5.update(image_content)
        image_md5 = md5.hexdigest()
        data = {
            'msgtype': 'image',
            'image': {
                'base64': image_base64,
                'md5': image_md5
            }
        }
        # 服务器上传bytes图片的时候，json.dumps解析会出错，需要自己手动去转一下
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                r = requests.post(url, data=json.dumps(data, cls=MyEncoder, indent=4), timeout=30, proxies={})
                print(f'调用企业微信接口返回： {r.text}')
                print('成功发送企业微信')
                break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    print(f"发送企业微信失败:{e}")
                    print(traceback.format_exc())
                else:
                    print(f"第{retry_count}次重试发送企业微信...")
                    time.sleep(2)  # 重试前等待2秒
    except Exception as e:
        print(f"发送企业微信失败:{e}")
        print(traceback.format_exc())
    # finally:
    #     if os.path.exists(file_path):
    #         os.remove(file_path)



# 设置 matplotlib 使用非交互式后端，避免进程无法退出
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

import matplotlib.pyplot as plt
import pandas as pd

def plot_rainbow_idx(df, index_label='Y_idx', y_high=100, y_low=-100, axhline_high=200, axhline_low=-10, axhline_low2=''):
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
        if y > y_high:
            return 'red'
        elif y < -y_low:
            return 'blue'
        else:
            norm_val = (y + y_high) / (y_high+abs(y_low))  # Normalize to [0, 1] ( (y + 100) / (200))
            return plt.cm.viridis(norm_val)

    colors = [get_color(y) for y in df[index_label]]

    # 将时间转换为数值以便绘图
    time_values = df['candle_begin_time'].map(pd.Timestamp.toordinal)

    # 检查 time_values 是否包含有效值
    if any(time_values < 1):
        raise ValueError("Some time values are invalid (less than 1).")

    # 绘制线条
    for i in range(len(time_values) - 1):
        x = [time_values.iloc[i], time_values.iloc[i + 1]]
        y = [df[index_label].iloc[i], df[index_label].iloc[i + 1]]
        color = get_color((y[0] + y[1]) / 2)
        ax.plot(x, y, color=color, linewidth=2)

    # 设置y轴限制以确保所有数据可见
    ax.set_ylim(min(df[index_label]) - 10, max(df[index_label]) + 10)

    # 添加200和-10的水平虚线
    ax.axhline(y=axhline_high, color='red', linestyle='--', alpha=0.7)
    ax.axhline(y=-axhline_low, color='green', linestyle='--', alpha=0.7)
    if axhline_low2 is not None:  # 检查axhline_low2是否被赋予有效值
        ax.axhline(y=axhline_low2, color='green', linestyle='--', alpha=0.7)


    # 获取最后一个数据点的值并标注在右上角
    last_value = df[index_label].iloc[-1]
    last_date = df['candle_begin_time'].iloc[-1]
    annotation_text = f"Latest Date: {last_date.strftime('%Y-%m-%d')}\nValue: {last_value:.2f}"
    ax.annotate(annotation_text, xy=(1.0, 1.0), xycoords='axes fraction',
                fontsize=12, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
                xytext=(-10, -10), textcoords='offset points')

    # 设置图表标题和标签
    ax.set_title(index_label, fontsize=15)
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
    # img_path = f"Y_idx_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.png"
    # plt.savefig(img_path)
    plt.savefig(index_label+'.png')
    send_wechat_work_img(index_label+'.png')
    plt.clf()
    plt.cla()
    plt.close(fig)  # 显式关闭 figure 对象
