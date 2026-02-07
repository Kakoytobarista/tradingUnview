from pybit.unified_trading import HTTP

from .base import ExchangeClient
from ..models import Candle, Ticker, Order, Position


class BybitClient(ExchangeClient):
    """Клиент для работы с Bybit API."""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet = testnet
        self._session: HTTP | None = None
    
    def connect(self) -> None:
        """Установить соединение с Bybit."""
        self._session = HTTP(
            api_key=self._api_key,
            api_secret=self._api_secret,
            testnet=self._testnet,
        )
    
    @property
    def session(self) -> HTTP:
        """Получить сессию, автоматически подключаясь если нужно."""
        if self._session is None:
            self.connect()
        return self._session
    
    # === Market Data ===
    
    def get_ticker(self, symbol: str) -> Ticker:
        """Получить текущую цену."""
        response = self.session.get_tickers(
            category="linear",
            symbol=symbol,
        )
        tickers = response.get("result", {}).get("list", [])
        raw = tickers[0] if tickers else {}
        
        return Ticker(
            symbol=symbol,
            last_price=float(raw.get("lastPrice", 0)),
            bid=float(raw.get("bid1Price", 0)),
            ask=float(raw.get("ask1Price", 0)),
            volume_24h=float(raw.get("volume24h", 0)),
        )
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> list[Candle]:
        """Получить свечи."""
        response = self.session.get_kline(
            category="linear",
            symbol=symbol,
            interval=interval,
            limit=limit,
        )
        raw_klines = response.get("result", {}).get("list", [])
        
        # Bybit возвращает от новых к старым, разворачиваем
        candles = [Candle.from_bybit(k) for k in raw_klines]
        return list(reversed(candles))
    
    # === Trading ===
    
    def buy(self, symbol: str, qty: str) -> Order:
        """Открыть long позицию."""
        return self._place_order(symbol, "Buy", qty)
    
    def sell(self, symbol: str, qty: str) -> Order:
        """Открыть short позицию."""
        return self._place_order(symbol, "Sell", qty)
    
    def _place_order(self, symbol: str, side: str, qty: str) -> Order:
        """Внутренний метод для размещения ордера."""
        response = self.session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=qty,
        )
        
        result = response.get("result", {})
        return Order(
            order_id=result.get("orderId", ""),
            symbol=symbol,
            side=side,
            qty=qty,
            status="created",
        )
    
    # === Positions ===
    
    def get_positions(self, symbol: str) -> list[Position]:
        """Получить открытые позиции."""
        response = self.session.get_positions(
            category="linear",
            symbol=symbol,
        )
        raw_positions = response.get("result", {}).get("list", [])
        
        positions = []
        for pos in raw_positions:
            size = float(pos.get("size", 0))
            if size > 0:
                positions.append(Position(
                    symbol=symbol,
                    side=pos.get("side", ""),
                    size=size,
                    entry_price=float(pos.get("avgPrice", 0)),
                    unrealized_pnl=float(pos.get("unrealisedPnl", 0)),
                ))
        
        return positions
    
    def close_position(self, symbol: str) -> Order | None:
        """Закрыть позицию."""
        positions = self.get_positions(symbol)
        
        if not positions:
            return None
        
        position = positions[0]
        close_side = "Sell" if position.side == "Buy" else "Buy"
        
        return self._place_order(symbol, close_side, str(position.size))
