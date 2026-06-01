"""
设置服务 - 处理数据源配置和状态
"""
import os
from pathlib import Path
from typing import Dict, List, Optional

from tradingagents.dataflows.config_store import ConfigStore
from tradingagents.dataflows.metrics_store import MetricsStore
from tradingagents.dataflows.models import DataSourceConfig, TestResult
from tradingagents.dataflows.adapters.tushare import TushareAdapter


# 数据库路径
_DB_PATH = os.path.join(os.getcwd(), "data", "tradingagents.db")

# 确保 data 目录存在
os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)


def _get_config_store() -> ConfigStore:
    """获取配置存储实例"""
    return ConfigStore(db_path=_DB_PATH)


def _get_metrics_store() -> MetricsStore:
    """获取指标存储实例"""
    return MetricsStore(db_path=_DB_PATH)


def save_tushare_config(config_dict: Dict) -> bool:
    """
    保存 Tushare 配置

    Args:
        config_dict: 配置字典，包含 enabled, tushare_token, timeout, max_retries, tushare_url, rate_limit

    Returns:
        是否保存成功
    """
    try:
        config = DataSourceConfig(
            source_id='tushare',
            enabled=config_dict.get('enabled', False),
            tushare_token=config_dict.get('tushare_token', ''),
            tushare_url=config_dict.get('tushare_url', 'https://api.tushare.pro'),
            timeout=config_dict.get('timeout', 30),
            max_retries=config_dict.get('max_retries', 3),
            rate_limit=config_dict.get('rate_limit'),
            priority=2,
            api_url=config_dict.get('tushare_url', 'https://api.tushare.pro'),
            token=config_dict.get('tushare_token', '')
        )

        store = _get_config_store()
        return store.save_config(config)
    except Exception as e:
        raise RuntimeError(f"保存配置失败: {str(e)}")


def test_tushare_connection(config_dict: Dict) -> Dict:
    """
    测试 Tushare 连接

    Args:
        config_dict: 配置字典

    Returns:
        测试结果字典
    """
    try:
        # 如果 token 是 '__SAVED__'，则从数据库获取已保存的配置
        if config_dict.get('tushare_token') == '__SAVED__':
            config_store = _get_config_store()
            saved_config = config_store.get_config('tushare')
            if saved_config is None or not saved_config.tushare_token:
                return {
                    'success': False,
                    'message': '未找到已保存的 Token',
                    'api_list': [],
                    'account_points': 0
                }
            tushare_token = saved_config.tushare_token
            tushare_url = saved_config.tushare_url
        else:
            tushare_token = config_dict.get('tushare_token', '')
            tushare_url = config_dict.get('tushare_url', 'https://api.tushare.pro')

        config = DataSourceConfig(
            source_id='tushare',
            enabled=config_dict.get('enabled', False),
            tushare_token=tushare_token,
            tushare_url=tushare_url,
            timeout=config_dict.get('timeout', 30),
            max_retries=config_dict.get('max_retries', 3),
            rate_limit=config_dict.get('rate_limit'),
            priority=2,
            api_url=tushare_url,
            token=tushare_token
        )

        adapter = TushareAdapter(config)
        result: TestResult = adapter.test_connection()

        return {
            'success': result.success,
            'message': result.message,
            'api_list': result.api_list,
            'account_points': result.account_points
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"测试连接失败: {str(e)}",
            'api_list': [],
            'account_points': 0
        }


def get_tushare_config() -> Dict:
    """
    获取 Tushare 配置（不返回 token 明文，仅返回是否已设置）

    Returns:
        配置字典
    """
    try:
        config_store = _get_config_store()
        config = config_store.get_config('tushare')

        if config is None:
            return {
                'enabled': False,
                'has_token': False,
                'timeout': 30,
                'max_retries': 3,
                'tushare_url': 'https://api.tushare.pro',
                'rate_limit': 200
            }

        return {
            'enabled': config.enabled,
            'has_token': bool(config.tushare_token),
            'timeout': config.timeout,
            'max_retries': config.max_retries,
            'tushare_url': config.tushare_url,
            'rate_limit': config.rate_limit
        }
    except Exception as e:
        raise RuntimeError(f"获取 Tushare 配置失败: {str(e)}")


def get_data_sources_status() -> List[Dict]:
    """
    获取所有数据源状态

    Returns:
        数据源状态列表
    """
    try:
        config_store = _get_config_store()
        metrics_store = _get_metrics_store()

        # 获取所有配置
        all_configs = config_store.get_all_configs()

        # 获取所有指标状态
        all_metrics = metrics_store.get_all_status()

        # 合并配置和指标
        status_by_source = {m['source_id']: m for m in all_metrics}

        result = []
        for source_id, config in all_configs.items():
            metrics = status_by_source.get(source_id, {
                'source_id': source_id,
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'last_request_time': None,
                'last_success_time': None,
                'last_failure_time': None
            })

            result.append({
                'source_id': source_id,
                'enabled': config.enabled,
                'priority': config.priority,
                'success_rate': metrics['success_rate'],
                'avg_response_time': metrics['avg_response_time'],
                'total_requests': metrics['total_requests'],
                'successful_requests': metrics['successful_requests'],
                'failed_requests': metrics['failed_requests'],
                'last_request_time': metrics['last_request_time'],
                'last_success_time': metrics['last_success_time'],
                'last_failure_time': metrics['last_failure_time']
            })

        return result
    except Exception as e:
        raise RuntimeError(f"获取数据源状态失败: {str(e)}")
