from core.exchange import ExchangeClient
from core.models import Candle


class Fetcher:
    """Сервис получения рыночных данных."""
    
    def __init__(self, client: ExchangeClient):
        self.client = client
    
    def get_candles(self, symbol: str, interval: str = "5", limit: int = 100) -> list[Candle]:
        """
        Получить свечи.
        
        Args:
            symbol: Торговая пара (например, "BTCUSDT")
            interval: Интервал свечи ("1", "5", "15", "60", "240", "D")
            limit: Количество свечей
        
        Returns:
            Список свечей от старых к новым
        """
        return self.client.get_klines(symbol, interval, limit)
    
    def get_current_price(self, symbol: str) -> float:
        """Получить текущую цену."""
        ticker = self.client.get_ticker(symbol)
        return ticker.last_price
