from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models import Candle, Ticker, Order, Position


class ExchangeClient(ABC):
    """
    Абстрактный интерфейс для работы с биржей.
    
    Все биржевые клиенты должны реализовать эти методы.
    """
    
    @abstractmethod
    def connect(self) -> None:
        """Установить соединение с биржей."""
        pass
    
    # === Market Data ===
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> "Ticker":
        """Получить текущую цену."""
        pass
    
    @abstractmethod
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> list["Candle"]:
        """Получить свечи."""
        pass
    
    # === Trading ===
    
    @abstractmethod
    def buy(self, symbol: str, qty: str) -> "Order":
        """Открыть long позицию (купить)."""
        pass
    
    @abstractmethod
    def sell(self, symbol: str, qty: str) -> "Order":
        """Открыть short позицию (продать)."""
        pass
    
    # === Positions ===
    
    @abstractmethod
    def get_positions(self, symbol: str) -> list["Position"]:
        """Получить открытые позиции."""
        pass
    
    @abstractmethod
    def close_position(self, symbol: str) -> "Order | None":
        """Закрыть позицию по символу."""
        pass
