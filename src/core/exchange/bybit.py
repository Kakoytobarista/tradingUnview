from pybit.unified_trading import HTTP

from .base import ExchangeClient
from ..models import Candle, Ticker, Order, Position


class BybitClient(ExchangeClient):
    """
    Клиент для работы с Bybit API.
    
    Тупые ручки к API — никакой бизнес-логики.
    """
    
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
        
        candles = [Candle.from_bybit(k) for k in raw_klines]
        return list(reversed(candles))
    
    # === Leverage ===
    
    def set_leverage(self, symbol: str, leverage: int) -> None:
        """Установить плечо."""
        self.session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=str(leverage),
            sellLeverage=str(leverage),
        )
    
    # === Trading ===
    
    def buy(self, symbol: str, qty: str) -> Order:
        """Купить (long)."""
        return self._place_order(symbol, "Buy", qty)
    
    def sell(self, symbol: str, qty: str) -> Order:
        """Продать (short)."""
        return self._place_order(symbol, "Sell", qty)
    
    def _place_order(self, symbol: str, side: str, qty: str) -> Order:
        """Разместить ордер."""
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
                    leverage=int(pos.get("leverage", 1)),
                    take_profit=float(pos.get("takeProfit", 0)) or None,
                    stop_loss=float(pos.get("stopLoss", 0)) or None,
                ))
        
        return positions
    
    def close_position(self, symbol: str, qty: str | None = None) -> Order | None:
        """Закрыть позицию."""
        positions = self.get_positions(symbol)
        
        if not positions:
            return None
        
        position = positions[0]
        close_side = "Sell" if position.side == "Buy" else "Buy"
        close_qty = qty if qty else str(position.size)
        
        return self._place_order(symbol, close_side, close_qty)
    
    # === TP/SL ===
    
    def set_take_profit(self, symbol: str, price: float) -> None:
        """Установить тейк-профит."""
        self.session.set_trading_stop(
            category="linear",
            symbol=symbol,
            takeProfit=str(price),
        )
    
    def set_stop_loss(self, symbol: str, price: float) -> None:
        """Установить стоп-лосс."""
        self.session.set_trading_stop(
            category="linear",
            symbol=symbol,
            stopLoss=str(price),
        )
