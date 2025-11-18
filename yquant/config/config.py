'''
配置文件
'''

class BinanceConfig:
    """
    Binance配置类
    """
    def __init__(self):
        # API请求基础配置
        self.timeout = 30000  # 超时时间（毫秒）
        self.rateLimit = 1000  # 请求频率限制（毫秒）
        self.verbose = False  # 是否显示详细日志
        self.hostname = 'fapi.binance.com'  # API主机名，修改为futures API
        self.enableRateLimit = True  # 是否启用频率限制
        # 代理配置
        self.proxies = {
            # "http": "http://127.0.0.1:8888",
            # "https": "http://127.0.0.1:8888"
        }
        
    def getApi(self, acc):
        """获取API配置
        
        Args:
            acc (str): 账户名
            
        Returns:
            BnAccount: 账户实例
        """
        from ..db.models.bn_account import BnAccount
        return BnAccount(acc=acc)  # 使用acc参数创建账户实例

class Config:
    """
    全局配置类
    """
    def __init__(self):
        self.binance = BinanceConfig()

# 全局配置实例
cfg = Config()
