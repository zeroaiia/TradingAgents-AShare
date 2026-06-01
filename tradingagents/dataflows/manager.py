"""
数据源管理器
"""
from typing import Callable, Any, Optional
import time

from tradingagents.dataflows.models import DataSourceConfig, DataSourceMetrics
from tradingagents.dataflows.config_store import ConfigStore
from tradingagents.dataflows.metrics_store import MetricsStore
from tradingagents.dataflows.adapters.base import DataSourceAdapter
from tradingagents.dataflows.exceptions import (
    NoAvailableDataSourceError,
    DataSourceExhaustedError,
    AuthenticationError
)


class DataSourceManager:
    """数据源管理器"""

    def __init__(self, db_path: str = "tradingagents.db"):
        self.adapters: dict[str, DataSourceAdapter] = {}
        self.config_store = ConfigStore(db_path)
        self.metrics_store = MetricsStore(db_path)

    def register_adapter(self, adapter: DataSourceAdapter) -> None:
        """
        注册数据源适配器

        Args:
            adapter: 适配器实例
        """
        self.adapters[adapter.source_id] = adapter

    def get_enabled_adapters(self) -> list[DataSourceAdapter]:
        """
        获取启用的适配器列表

        Returns:
            启用的适配器列表
        """
        enabled_adapters = []
        all_configs = self.config_store.get_all_configs()

        for source_id, adapter in self.adapters.items():
            config = all_configs.get(source_id)
            if config and config.enabled:
                adapter.config = config
                enabled_adapters.append(adapter)

        return enabled_adapters

    def select_best_source(self, required_feature: str) -> DataSourceAdapter:
        """
        选择最优数据源

        Args:
            required_feature: 需要的功能（如 'stock_daily'）

        Returns:
            最优数据源适配器

        Raises:
            NoAvailableDataSourceError: 无可用数据源
        """
        enabled_adapters = self.get_enabled_adapters()

        # 筛选支持所需功能的数据源
        capable_adapters = [
            adapter for adapter in enabled_adapters
            if required_feature in adapter.supported_features
        ]

        if not capable_adapters:
            raise NoAvailableDataSourceError(f"无可用数据源支持: {required_feature}")

        # 计算得分并选择最优
        scored_adapters = [
            (adapter, self._calculate_score(adapter.source_id))
            for adapter in capable_adapters
        ]

        scored_adapters.sort(key=lambda x: x[1], reverse=True)
        return scored_adapters[0][0]

    def _calculate_score(self, source_id: str) -> float:
        """
        计算数据源得分

        Args:
            source_id: 数据源ID

        Returns:
            综合得分（0-100）
        """
        metrics = self.metrics_store.get_metrics(source_id)

        # 成功率得分 (0-100)
        success_score = metrics.success_rate

        # 响应时间得分 (100ms = 100分，每增加10ms减1分，最低0分)
        if metrics.avg_response_time > 0:
            response_score = max(0, 100 - (metrics.avg_response_time - 100) / 10)
        else:
            response_score = 50  # 默认中等分数

        # 综合得分：成功率 60%, 响应时间 40%
        return success_score * 0.6 + response_score * 0.4

    def _rank_adapters_by_score(self, required_feature: str) -> list[DataSourceAdapter]:
        """
        按得分排序适配器

        Args:
            required_feature: 需要的功能

        Returns:
            排序后的适配器列表
        """
        enabled_adapters = self.get_enabled_adapters()
        capable_adapters = [
            adapter for adapter in enabled_adapters
            if required_feature in adapter.supported_features
        ]

        scored_adapters = [
            (adapter, self._calculate_score(adapter.source_id))
            for adapter in capable_adapters
        ]

        scored_adapters.sort(key=lambda x: x[1], reverse=True)
        return [adapter for adapter, _ in scored_adapters]

    def execute_with_fallback(self,
                             required_feature: str,
                             operation: Callable,
                             **kwargs) -> Any:
        """
        执行数据获取操作，支持自动切换

        Args:
            required_feature: 需要的功能
            operation: 要执行的操作（接收适配器作为参数）
            **kwargs: 操作的其他参数

        Returns:
            操作结果

        Raises:
            DataSourceExhaustedError: 所有数据源均失败
        """
        ranked_adapters = self._rank_adapters_by_score(required_feature)

        if not ranked_adapters:
            raise NoAvailableDataSourceError(f"无可用数据源支持: {required_feature}")

        attempts = []
        last_error = None

        for adapter in ranked_adapters:
            start_time = time.time()
            attempt_info = {
                'source_id': adapter.source_id,
                'timestamp': time.time()
            }

            try:
                result = operation(adapter, **kwargs)
                response_time = (time.time() - start_time) * 1000

                # 记录成功
                self.metrics_store.record_request(
                    source_id=adapter.source_id,
                    success=True,
                    response_time=response_time
                )

                return result

            except AuthenticationError as e:
                # 认证错误 - 不继续尝试
                attempt_info['error'] = str(e)
                attempt_info['error_type'] = 'authentication'
                attempts.append(attempt_info)
                raise

            except Exception as e:
                # 其他错误 - 继续尝试下一个数据源
                last_error = e
                response_time = (time.time() - start_time) * 1000

                attempt_info['error'] = str(e)
                attempt_info['error_type'] = 'unknown'
                attempts.append(attempt_info)

                # 记录失败
                self.metrics_store.record_request(
                    source_id=adapter.source_id,
                    success=False,
                    response_time=response_time,
                    error=str(e)
                )
                continue

        # 所有数据源都失败
        raise DataSourceExhaustedError(
            f"所有数据源均失败，最后错误: {last_error}",
            attempts=attempts
        )

    def get_all_status(self) -> list[dict]:
        """
        获取所有数据源状态

        Returns:
            数据源状态列表
        """
        all_configs = self.config_store.get_all_configs()
        statuses = []

        for source_id, config in all_configs.items():
            status = self.metrics_store.get_status(source_id)
            status['enabled'] = config.enabled
            status['priority'] = config.priority
            statuses.append(status)

        return statuses
