"""Base data source adapter class."""
from abc import ABC, abstractmethod
from typing import Any, Callable
import pandas as pd


class DataSourceAdapter(ABC):
    """Base class for data source adapters."""

    def __init__(self, config):
        """Initialize adapter with configuration."""
        self.config = config

    @abstractmethod
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get daily stock data."""
        pass

    @abstractmethod
    def get_stock_realtime(self, symbol: str) -> pd.DataFrame:
        """Get realtime stock data."""
        pass

    @abstractmethod
    def get_trade_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get trade calendar."""
        pass

    @abstractmethod
    def test_connection(self):
        """Test data source connection."""
        pass
