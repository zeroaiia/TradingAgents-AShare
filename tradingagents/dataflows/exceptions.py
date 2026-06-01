"""
数据源相关异常
"""


class DataSourceError(Exception):
    """数据源基础异常"""
    pass


class NoAvailableDataSourceError(DataSourceError):
    """无可用数据源"""
    pass


class DataSourceExhaustedError(DataSourceError):
    """所有数据源均失败"""

    def __init__(self, message: str, attempts: list[dict]):
        super().__init__(message)
        self.attempts = attempts  # 记录每次尝试的详细信息


class ConfigError(DataSourceError):
    """配置错误"""
    pass


class RateLimitError(DataSourceError):
    """频率限制"""
    pass


class AuthenticationError(DataSourceError):
    """认证失败"""
    pass
