from core.exchange import ExchangeClient
from core.models import Signal, SignalType, Position, Order


class Trader:
    """Сервис исполнения сделок."""
    
    def __init__(self, client: ExchangeClient, default_qty: str = "0.001"):
        """
        Args:
            client: Биржевой клиент (любая биржа)
            default_qty: Размер позиции по умолчанию
        """
        self.client = client
        self.default_qty = default_qty
    
    def execute(self, signal: Signal, qty: str | None = None) -> Order | None:
        """
        Исполнить сигнал.
        
        Args:
            signal: Сигнал от анализатора
            qty: Размер позиции (если None, используется default_qty)
        
        Returns:
            Order или None если сигнал NONE
        """
        if signal.type == SignalType.NONE:
            return None
        
        qty = qty or self.default_qty
        
        if signal.type == SignalType.LONG:
            return self.client.buy(signal.symbol, qty)
        else:
            return self.client.sell(signal.symbol, qty)
    
    def get_position(self, symbol: str) -> Position | None:
        """Получить текущую позицию."""
        positions = self.client.get_positions(symbol)
        return positions[0] if positions else None
    
    def close_position(self, symbol: str) -> Order | None:
        """Закрыть текущую позицию."""
        return self.client.close_position(symbol)
