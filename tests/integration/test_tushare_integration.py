"""
Tushare 集成测试
"""
import pytest
import os

from tradingagents.dataflows.adapters.tushare import TushareAdapter
from tradingagents.dataflows.models import DataSourceConfig


@pytest.mark.integration
class TestTushareIntegration:
    """Tushare 集成测试（需要真实 Token）"""

    @pytest.fixture
    def real_config(self):
        """获取真实配置"""
        token = os.getenv('TUSHARE_TEST_TOKEN')
        if not token:
            pytest.skip("未设置 TUSHARE_TEST_TOKEN 环境变量")

        return DataSourceConfig(
            source_id='tushare',
            enabled=True,
            tushare_token=token,
            timeout=30,
            max_retries=3
        )

    def test_connection(self, real_config):
        """测试连接"""
        adapter = TushareAdapter(real_config)
        result = adapter.test_connection()

        assert result.success is True
        assert len(result.api_list) > 0
        assert result.account_points >= 0

    def test_get_trade_calendar(self, real_config):
        """测试获取交易日历"""
        adapter = TushareAdapter(real_config)
        df = adapter.get_trade_calendar('20240101', '20240131')

        assert df is not None
        assert len(df) > 0
