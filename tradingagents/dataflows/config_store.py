"""
数据源配置存储
"""
import json
from datetime import datetime
from typing import Optional

from tradingagents.dataflows.models import DataSourceConfig


class ConfigStore:
    """数据源配置存储"""

    def __init__(self, db_path: str = "tradingagents.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        """初始化数据库表"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_source_config (
                source_id VARCHAR(50) PRIMARY KEY,
                enabled BOOLEAN DEFAULT TRUE,
                priority INTEGER DEFAULT 2,
                timeout INTEGER DEFAULT 30,
                max_retries INTEGER DEFAULT 3,
                api_url VARCHAR(255),
                rate_limit INTEGER,
                token VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 插入默认配置
        default_configs = [
            ('akshare', True, 1, 30, 3, None, None, None),
            ('baostock', True, 2, 30, 3, None, None, None),
            ('tushare', False, 2, 30, 3, 'https://api.tushare.pro', 200, None)
        ]

        for config in default_configs:
            cursor.execute("""
                INSERT OR IGNORE INTO data_source_config
                (source_id, enabled, priority, timeout, max_retries, api_url, rate_limit, token)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, config)

        conn.commit()
        conn.close()

    def get_config(self, source_id: str) -> Optional[DataSourceConfig]:
        """
        获取数据源配置

        Args:
            source_id: 数据源ID

        Returns:
            DataSourceConfig 或 None
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT source_id, enabled, priority, timeout, max_retries, api_url, rate_limit, token
            FROM data_source_config
            WHERE source_id = ?
        """, (source_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return DataSourceConfig(
                source_id=row[0],
                enabled=bool(row[1]),
                priority=row[2],
                timeout=row[3],
                max_retries=row[4],
                api_url=row[5],
                rate_limit=row[6],
                token=row[7],
                tushare_token=row[7] if source_id == 'tushare' else None,
                tushare_url=row[5] if source_id == 'tushare' else 'https://api.tushare.pro'
            )
        return None

    def save_config(self, config: DataSourceConfig) -> bool:
        """
        保存数据源配置

        Args:
            config: 数据源配置

        Returns:
            是否保存成功
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE data_source_config
            SET enabled = ?, priority = ?, timeout = ?, max_retries = ?,
                api_url = ?, rate_limit = ?, token = ?, updated_at = ?
            WHERE source_id = ?
        """, (
            config.enabled,
            config.priority,
            config.timeout,
            config.max_retries,
            config.api_url,
            config.rate_limit,
            config.token,
            datetime.now().isoformat(),
            config.source_id
        ))

        conn.commit()
        affected = cursor.rowcount
        conn.close()

        return affected > 0

    def get_all_configs(self) -> dict[str, DataSourceConfig]:
        """
        获取所有数据源配置

        Returns:
            数据源配置字典
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT source_id, enabled, priority, timeout, max_retries, api_url, rate_limit, token
            FROM data_source_config
        """)

        configs = {}
        for row in cursor.fetchall():
            source_id = row[0]
            configs[source_id] = DataSourceConfig(
                source_id=row[0],
                enabled=bool(row[1]),
                priority=row[2],
                timeout=row[3],
                max_retries=row[4],
                api_url=row[5],
                rate_limit=row[6],
                token=row[7],
                tushare_token=row[7] if source_id == 'tushare' else None,
                tushare_url=row[5] if source_id == 'tushare' else 'https://api.tushare.pro'
            )

        conn.close()
        return configs
