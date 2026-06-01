"""
数据源数据模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from typing import Optional


@dataclass
class DataSourceConfig:
    """数据源配置"""
    source_id: str                    # 数据源ID (akshare/tushare/baostock)
    enabled: bool = True              # 是否启用
    priority: int = 2                 # 优先级 (1=主用, 2=备用)
    timeout: int = 30                 # 超时时间（秒）
    max_retries: int = 3              # 最大重试次数
    api_url: Optional[str] = None     # API端点URL
    rate_limit: Optional[int] = None  # 频率限制（次/分钟）
    token: Optional[str] = None       # 认证Token（Tushare专用）

    # Tushare 专用字段
    tushare_token: Optional[str] = None
    tushare_url: str = "https://api.tushare.pro"


@dataclass
class RequestRecord:
    """单次请求记录"""
    timestamp: datetime               # 请求时间
    success: bool                     # 是否成功
    response_time: float              # 响应时间（毫秒）
    error: Optional[str] = None       # 错误信息


@dataclass
class DataSourceMetrics:
    """数据源运行指标"""
    source_id: str                    # 数据源ID
    total_requests: int = 0           # 总请求次数
    successful_requests: int = 0      # 成功次数
    failed_requests: int = 0           # 失败次数
    success_rate: float = 0.0         # 成功率 (0-100)

    # 响应时间统计（毫秒）
    avg_response_time: float = 0.0    # 平均响应时间
    last_response_time: Optional[float] = None

    # 时间戳
    last_request_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None

    # 请求历史（最近100次）
    recent_requests: deque[RequestRecord] = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class TestResult:
    """连接测试结果"""
    success: bool
    message: str
    api_list: list[str] = field(default_factory=list)
    account_points: int = 0
