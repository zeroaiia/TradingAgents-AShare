"""
数据源指标存储
"""
import json
from collections import deque
from datetime import datetime
from typing import Optional

from tradingagents.dataflows.models import DataSourceMetrics, RequestRecord


class MetricsStore:
    """数据源指标存储"""

    def __init__(self, db_path: str = "tradingagents.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        """初始化数据库表"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_source_metrics (
                source_id VARCHAR(50) PRIMARY KEY,
                total_requests INTEGER DEFAULT 0,
                successful_requests INTEGER DEFAULT 0,
                failed_requests INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                avg_response_time REAL DEFAULT 0.0,
                last_request_time TIMESTAMP,
                last_success_time TIMESTAMP,
                last_failure_time TIMESTAMP,
                recent_requests TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def get_metrics(self, source_id: str) -> DataSourceMetrics:
        """
        获取数据源指标

        Args:
            source_id: 数据源ID

        Returns:
            DataSourceMetrics
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT total_requests, successful_requests, failed_requests, success_rate,
                   avg_response_time, last_request_time, last_success_time, last_failure_time, recent_requests
            FROM data_source_metrics
            WHERE source_id = ?
        """, (source_id,))

        row = cursor.fetchone()
        conn.close()

        recent_requests = deque(maxlen=100)
        if row and row[8]:
            try:
                for record_data in json.loads(row[8]):
                    record = RequestRecord(
                        timestamp=datetime.fromisoformat(record_data['timestamp']),
                        success=record_data['success'],
                        response_time=record_data['response_time'],
                        error=record_data.get('error')
                    )
                    recent_requests.append(record)
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        if row:
            return DataSourceMetrics(
                source_id=source_id,
                total_requests=row[0] or 0,
                successful_requests=row[1] or 0,
                failed_requests=row[2] or 0,
                success_rate=row[3] or 0.0,
                avg_response_time=row[4] or 0.0,
                last_request_time=datetime.fromisoformat(row[5]) if row[5] else None,
                last_success_time=datetime.fromisoformat(row[6]) if row[6] else None,
                last_failure_time=datetime.fromisoformat(row[7]) if row[7] else None,
                recent_requests=recent_requests
            )

        # 返回默认指标
        return DataSourceMetrics(source_id=source_id)

    def record_request(self, source_id: str, success: bool,
                     response_time: float, error: Optional[str] = None) -> None:
        """
        记录请求结果

        Args:
            source_id: 数据源ID
            success: 是否成功
            response_time: 响应时间（毫秒）
            error: 错误信息
        """
        metrics = self.get_metrics(source_id)

        # 添加请求记录
        record = RequestRecord(
            timestamp=datetime.now(),
            success=success,
            response_time=response_time,
            error=error
        )
        metrics.recent_requests.append(record)

        # 更新统计
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
            metrics.last_success_time = record.timestamp
        else:
            metrics.failed_requests += 1
            metrics.last_failure_time = record.timestamp

        metrics.last_request_time = record.timestamp

        # 计算成功率
        if metrics.total_requests > 0:
            metrics.success_rate = (metrics.successful_requests / metrics.total_requests) * 100

        # 计算平均响应时间
        if metrics.recent_requests:
            total_time = sum(r.response_time for r in metrics.recent_requests)
            metrics.avg_response_time = total_time / len(metrics.recent_requests)

        # 序列化 recent_requests
        recent_requests_json = json.dumps([
            {
                'timestamp': r.timestamp.isoformat(),
                'success': r.success,
                'response_time': r.response_time,
                'error': r.error
            }
            for r in metrics.recent_requests
        ])

        # 保存到数据库
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO data_source_metrics
            (source_id, total_requests, successful_requests, failed_requests, success_rate,
             avg_response_time, last_request_time, last_success_time, last_failure_time, recent_requests, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source_id,
            metrics.total_requests,
            metrics.successful_requests,
            metrics.failed_requests,
            metrics.success_rate,
            metrics.avg_response_time,
            metrics.last_request_time.isoformat() if metrics.last_request_time else None,
            metrics.last_success_time.isoformat() if metrics.last_success_time else None,
            metrics.last_failure_time.isoformat() if metrics.last_failure_time else None,
            recent_requests_json,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_status(self, source_id: str) -> dict:
        """
        获取数据源状态（用于 API 返回）

        Args:
            source_id: 数据源ID

        Returns:
            状态字典
        """
        metrics = self.get_metrics(source_id)
        return {
            'source_id': source_id,
            'total_requests': metrics.total_requests,
            'successful_requests': metrics.successful_requests,
            'failed_requests': metrics.failed_requests,
            'success_rate': metrics.success_rate,
            'avg_response_time': metrics.avg_response_time,
            'last_request_time': metrics.last_request_time.isoformat() if metrics.last_request_time else None,
            'last_success_time': metrics.last_success_time.isoformat() if metrics.last_success_time else None,
            'last_failure_time': metrics.last_failure_time.isoformat() if metrics.last_failure_time else None
        }

    def get_all_status(self) -> list[dict]:
        """
        获取所有数据源状态

        Returns:
            数据源状态列表
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT source_id FROM data_source_metrics
        """)

        source_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.get_status(sid) for sid in source_ids]
