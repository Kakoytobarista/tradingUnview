from .base import ExchangeClient
from ..models import Candle, Ticker, Order, Position


class BinanceClient(ExchangeClient):
    """
    Клиент для работы с Binance API.
    
    TODO: Реализовать методы.
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet = testnet
    
    def connect(self) -> None:
        raise NotImplementedError("Binance client not implemented yet")
    
    def get_ticker(self, symbol: str) -> Ticker:
        raise NotImplementedError("Binance client not implemented yet")
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> list[Candle]:
        raise NotImplementedError("Binance client not implemented yet")
    
    def buy(self, symbol: str, qty: str) -> Order:
        raise NotImplementedError("Binance client not implemented yet")
    
    def sell(self, symbol: str, qty: str) -> Order:
        raise NotImplementedError("Binance client not implemented yet")
    
    def get_positions(self, symbol: str) -> list[Position]:
        raise NotImplementedError("Binance client not implemented yet")
    
    def close_position(self, symbol: str) -> Order | None:
        raise NotImplementedError("Binance client not implemented yet")
