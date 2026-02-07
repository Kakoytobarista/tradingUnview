from core.models import Candle, Signal, SignalType


class Analyzer:
    """Сервис анализа рынка и генерации сигналов."""
    
    def __init__(self, spike_threshold: float = 0.5):
        """
        Args:
            spike_threshold: Порог скачка в процентах (по умолчанию 0.5%)
        """
        self.spike_threshold = spike_threshold
    
    def analyze(self, candles: list[Candle], symbol: str = "BTCUSDT") -> Signal:
        """
        Анализирует свечи и возвращает сигнал.
        
        Args:
            candles: Список свечей (от старых к новым)
            symbol: Торговая пара
        
        Returns:
            Signal с типом LONG, SHORT или NONE
        """
        if len(candles) < 2:
            return Signal(
                type=SignalType.NONE,
                symbol=symbol,
                price=0,
                reason="Недостаточно данных"
            )
        
        # Берём последнюю свечу
        last_candle = candles[-1]
        prev_candle = candles[-2]
        
        # Считаем процент изменения
        price_change = ((last_candle.close - prev_candle.close) / prev_candle.close) * 100
        
        # Определяем сигнал
        if price_change >= self.spike_threshold:
            return Signal(
                type=SignalType.LONG,
                symbol=symbol,
                price=last_candle.close,
                reason=f"Скачок вверх: {price_change:.2f}%"
            )
        elif price_change <= -self.spike_threshold:
            return Signal(
                type=SignalType.SHORT,
                symbol=symbol,
                price=last_candle.close,
                reason=f"Скачок вниз: {price_change:.2f}%"
            )
        
        return Signal(
            type=SignalType.NONE,
            symbol=symbol,
            price=last_candle.close,
            reason=f"Нет скачка: {price_change:.2f}%"
        )
