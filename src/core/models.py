from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class SignalType(Enum):
    LONG = "long"
    SHORT = "short"
    NONE = "none"


@dataclass
class Candle:
    """Свеча (OHLCV)."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @classmethod
    def from_bybit(cls, data: list) -> "Candle":
        """Парсинг свечи из ответа Bybit API."""
        # Bybit возвращает: [timestamp, open, high, low, close, volume, turnover]
        return cls(
            timestamp=datetime.fromtimestamp(int(data[0]) / 1000),
            open=float(data[1]),
            high=float(data[2]),
            low=float(data[3]),
            close=float(data[4]),
            volume=float(data[5]),
        )


@dataclass
class Ticker:
    """Текущая цена инструмента."""
    symbol: str
    last_price: float
    bid: float
    ask: float
    volume_24h: float


@dataclass
class Order:
    """Ордер."""
    order_id: str
    symbol: str
    side: str  # "Buy" или "Sell"
    qty: str
    status: str


@dataclass
class Signal:
    """Торговый сигнал."""
    type: SignalType
    symbol: str
    price: float
    reason: str


@dataclass
class Position:
    """Открытая позиция."""
    symbol: str
    side: str  # "Buy" или "Sell"
    size: float
    entry_price: float
    unrealized_pnl: float
