"""
Akshare 数据源适配器
"""
import akshare as ak
import pandas as pd

from tradingagents.dataflows.adapters.base import DataSourceAdapter
from tradingagents.dataflows.models import DataSourceConfig, TestResult


class AkshareAdapter(DataSourceAdapter):
    """Akshare 数据源适配器"""

    source_id = "akshare"
    source_name = "AkShare"
    supported_features = {
        'stock_daily', 'stock_realtime', 'trade_calendar'
    }
    requires_token = False
    priority = 1  # 主用数据源

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期（YYYYMMDD）
            end_date: 结束日期（YYYYMMDD）

        Returns:
            标准化的 DataFrame
        """
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            adjust=""
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
        df = ak.stock_zh_a_spot_em()
        stock_df = df[df['代码'] == symbol]
        return stock_df

    def get_trade_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期（YYYYMMDD）
            end_date: 结束日期（YYYYMMDD）

        Returns:
            交易日历数据
        """
        df = ak.tool_trade_date_hist_sina()
        df = df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)]
        return df

    def test_connection(self) -> TestResult:
        """
        测试连接

        Returns:
            TestResult
        """
        try:
            # 简单测试：获取交易日历
            df = self.get_trade_calendar("20240101", "20240131")
            if df.empty:
                return TestResult(
                    success=False,
                    message="测试失败：未返回数据",
                    api_list=list(self.supported_features)
                )

            return TestResult(
                success=True,
                message="连接成功",
                api_list=list(self.supported_features)
            )
        except Exception as e:
            return TestResult(
                success=False,
                message=f"连接失败: {str(e)}",
                api_list=[]
            )

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化列名

        Args:
            df: 原始 DataFrame

        Returns:
            标准化后的 DataFrame
        """
        column_mapping = {
            '股票代码': 'symbol',
            '代码': 'symbol',
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount',
            '涨跌幅': 'pct_change',
            'trade_date': 'date'
        }

        existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        return df.rename(columns=existing_mapping)
