from core.exchange import ExchangeClient
from core.models import Order, Position


class Trader:
    """
    Исполнитель сделок.
    
    ТОЛЬКО исполняет команды: купить, продать, закрыть.
    Конвертирует USDT в qty.
    Никакой логики принятия решений.
    """
    
    def __init__(self, client: ExchangeClient):
        self.client = client
    
    def _usdt_to_qty(self, symbol: str, amount_usdt: float) -> str:
        """Конвертировать USDT в количество монет."""
        ticker = self.client.get_ticker(symbol)
        qty = amount_usdt / ticker.last_price
        return f"{qty:.3f}"
    
    def enter_long(
        self,
        symbol: str,
        amount_usdt: float,
        leverage: int = 1,
    ) -> Order:
        """
        Войти в long.
        
        Args:
            symbol: Торговая пара
            amount_usdt: Сумма в USDT
            leverage: Плечо
        """
        if leverage > 1:
            self.client.set_leverage(symbol, leverage)
        
        qty = self._usdt_to_qty(symbol, amount_usdt)
        return self.client.buy(symbol, qty)
    
    def enter_short(
        self,
        symbol: str,
        amount_usdt: float,
        leverage: int = 1,
    ) -> Order:
        """
        Войти в short.
        
        Args:
            symbol: Торговая пара
            amount_usdt: Сумма в USDT
            leverage: Плечо
        """
        if leverage > 1:
            self.client.set_leverage(symbol, leverage)
        
        qty = self._usdt_to_qty(symbol, amount_usdt)
        return self.client.sell(symbol, qty)
    
    def close(self, symbol: str) -> Order | None:
        """Закрыть позицию."""
        return self.client.close_position(symbol)
    
    def set_stop_loss(self, symbol: str, price: float) -> None:
        """Установить stop loss."""
        self.client.set_stop_loss(symbol, price)
    
    def get_position(self, symbol: str) -> Position | None:
        """Получить текущую позицию."""
        positions = self.client.get_positions(symbol)
        return positions[0] if positions else None
