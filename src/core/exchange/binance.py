from .base import ExchangeClient
from ..models import Candle, Ticker, Order, Position


class BinanceClient(ExchangeClient):
    """
    Клиент для работы с Binance API.
    
    TODO: Реализовать.
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet = testnet
    
    def connect(self) -> None:
        raise NotImplementedError("Binance client not implemented")
    
    def get_ticker(self, symbol: str) -> Ticker:
        raise NotImplementedError("Binance client not implemented")
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> list[Candle]:
        raise NotImplementedError("Binance client not implemented")
    
    def set_leverage(self, symbol: str, leverage: int) -> None:
        raise NotImplementedError("Binance client not implemented")
    
    def buy(self, symbol: str, qty: str) -> Order:
        raise NotImplementedError("Binance client not implemented")
    
    def sell(self, symbol: str, qty: str) -> Order:
        raise NotImplementedError("Binance client not implemented")
    
    def get_positions(self, symbol: str) -> list[Position]:
        raise NotImplementedError("Binance client not implemented")
    
    def close_position(self, symbol: str, qty: str | None = None) -> Order | None:
        raise NotImplementedError("Binance client not implemented")
    
    def set_take_profit(self, symbol: str, price: float) -> None:
        raise NotImplementedError("Binance client not implemented")
    
    def set_stop_loss(self, symbol: str, price: float) -> None:
        raise NotImplementedError("Binance client not implemented")
