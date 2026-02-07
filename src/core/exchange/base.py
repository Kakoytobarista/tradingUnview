from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models import Candle, Ticker, Order, Position


class ExchangeClient(ABC):
    """
    Абстрактный интерфейс для работы с биржей.
    
    Клиент — это тупые ручки к API. Никакой бизнес-логики.
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
    
    # === Leverage ===
    
    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> None:
        """Установить плечо для символа."""
        pass
    
    # === Trading ===
    
    @abstractmethod
    def buy(self, symbol: str, qty: str) -> "Order":
        """
        Купить (long).
        
        Args:
            symbol: Торговая пара
            qty: Количество в монетах (например "0.001" BTC)
        """
        pass
    
    @abstractmethod
    def sell(self, symbol: str, qty: str) -> "Order":
        """
        Продать (short).
        
        Args:
            symbol: Торговая пара
            qty: Количество в монетах
        """
        pass
    
    # === Positions ===
    
    @abstractmethod
    def get_positions(self, symbol: str) -> list["Position"]:
        """Получить открытые позиции."""
        pass
    
    @abstractmethod
    def close_position(self, symbol: str, qty: str | None = None) -> "Order | None":
        """
        Закрыть позицию.
        
        Args:
            symbol: Торговая пара
            qty: Количество (None = закрыть всю)
        """
        pass
    
    # === TP/SL ===
    
    @abstractmethod
    def set_take_profit(self, symbol: str, price: float) -> None:
        """Установить тейк-профит для позиции."""
        pass
    
    @abstractmethod
    def set_stop_loss(self, symbol: str, price: float) -> None:
        """Установить стоп-лосс для позиции."""
        pass
