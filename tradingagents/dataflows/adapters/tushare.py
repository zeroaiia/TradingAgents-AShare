"""
Tushare Pro 数据源适配器
"""
from datetime import datetime
import time
import tushare as ts
import pandas as pd
from typing import Callable, Any

from tradingagents.dataflows.adapters.base import DataSourceAdapter
from tradingagents.dataflows.models import DataSourceConfig, TestResult


class TushareAdapter(DataSourceAdapter):
    """Tushare Pro 数据源适配器"""

    source_id = "tushare"
    source_name = "Tushare Pro"
    supported_features = {
        'stock_daily', 'stock_realtime', 'trade_calendar',
        'stock_basic', 'index_daily', 'money_flow'
    }
    requires_token = True

    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.client = self._create_client()

    def _create_client(self) -> ts.pro_api:
        """创建 Tushare 客户端"""
        # 注意：tushare 库不支持自定义 API URL，使用库内置的默认 URL
        timeout = self.config.timeout or 30
        return ts.pro_api(
            self.config.tushare_token,
            timeout=timeout
        )

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取日线数据

        Args:
            symbol: 股票代码（如 600000）
            start_date: 开始日期（YYYYMMDD）
            end_date: 结束日期（YYYYMMDD）

        Returns:
            标准化的 DataFrame，包含列：symbol, date, open, high, low, close, volume, amount
        """
        ts_code = self._convert_to_ts_code(symbol)

        df = self._execute_with_retry(
            lambda: self.client.query(
                'daily',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
        )

        return self._standardize_columns(df)

    def get_stock_realtime(self, symbol: str) -> pd.DataFrame:
        """
        获取实时行情

        Args:
            symbol: 股票代码

        Returns:
            实时行情数据
        """
        ts_code = self._convert_to_ts_code(symbol)
        today = datetime.now().strftime("%Y%m%d")

        df = self._execute_with_retry(
            lambda: self.client.query(
                'daily',
                ts_code=ts_code,
                trade_date=today
            )
        )

        return self._standardize_columns(df)

    def get_trade_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期（YYYYMMDD）
            end_date: 结束日期（YYYYMMDD）

        Returns:
            交易日历数据
        """
        df = self._execute_with_retry(
            lambda: self.client.query(
                'trade_cal',
                exchange='SSE',
                start_date=start_date,
                end_date=end_date
            )
        )
        return df

    def test_connection(self) -> TestResult:
        """
        测试连接

        Returns:
            TestResult 包含连接状态、可用接口列表和账户积分
        """
        try:
            # 测试基础连接
            today = datetime.now().strftime("%Y%m%d")
            self.client.query(
                'trade_cal',
                exchange='SSE',
                start_date=today,
                end_date=today
            )

            # 获取用户积分
            user = self.client.query('user')

            # 获取可用接口列表
            api_list = list(self.supported_features)

            return TestResult(
                success=True,
                message="连接成功",
                api_list=api_list,
                account_points=user.get('points', 0)
            )

        except Exception as e:
            return TestResult(
                success=False,
                message=f"连接失败: {str(e)}",
                api_list=[],
                account_points=0
            )

    def _execute_with_retry(self, operation: Callable) -> Any:
        """
        执行操作并支持重试

        Args:
            operation: 要执行的操作

        Returns:
            操作结果

        Raises:
            Exception: 重试次数用尽后抛出原始异常
        """
        for attempt in range(self.config.max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise
                # 指数退避
                wait_time = min(2 ** attempt, 10)
                time.sleep(wait_time)

    def _convert_to_ts_code(self, symbol: str) -> str:
        """
        转换为 Tushare 格式代码

        Args:
            symbol: 股票代码（如 600000）

        Returns:
            Tushare 格式代码（如 600000.SH）
        """
        if '.' in symbol:
            return symbol
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        return f"{symbol}.SZ"

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化列名

        Args:
            df: 原始 DataFrame

        Returns:
            标准化后的 DataFrame
        """
        column_mapping = {
            'ts_code': 'symbol',
            'trade_date': 'date',
            'cal_date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'vol': 'volume',
            'amount': 'amount',
            'preclose': 'pre_close',
            'pct_chg': 'pct_change'
        }

        # 只重命名存在的列
        existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        return df.rename(columns=existing_mapping)
