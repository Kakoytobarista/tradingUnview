from dataclasses import dataclass
from core.models import Signal, SignalType


@dataclass
class AnalyzerConfig:
    """Конфигурация анализатора."""
    spike_percent: float = 0.5   # Порог скачка для входа (%)
    spikes_to_enter: int = 2     # Кол-во скачков для подтверждения


class Analyzer:
    """
    Анализатор рынка.
    
    ТОЛЬКО анализирует цены и возвращает сигнал.
    Никакого состояния, никакой логики позиций.
    """
    
    def __init__(self, config: AnalyzerConfig | None = None):
        self.config = config or AnalyzerConfig()
    
    def check_entry(self, prices: list[float], symbol: str = "BTCUSDT") -> Signal:
        """
        Проверить условия для входа в позицию.
        
        Args:
            prices: Список последних цен (минимум spikes_to_enter + 1)
            symbol: Торговая пара
        
        Returns:
            Signal (LONG / SHORT / NONE)
        """
        required = self.config.spikes_to_enter + 1
        
        if len(prices) < required:
            return Signal(
                type=SignalType.NONE,
                symbol=symbol,
                price=prices[-1] if prices else 0,
                reason=f"Недостаточно данных (нужно {required})"
            )
        
        # Берём последние N+1 цен
        recent = prices[-required:]
        
        # Считаем скачки
        up_spikes = 0
        down_spikes = 0
        
        for i in range(1, len(recent)):
            change = ((recent[i] - recent[i-1]) / recent[i-1]) * 100
            
            if change >= self.config.spike_percent:
                up_spikes += 1
                down_spikes = 0  # Сбрасываем противоположный
            elif change <= -self.config.spike_percent:
                down_spikes += 1
                up_spikes = 0
            else:
                up_spikes = 0
                down_spikes = 0
        
        current_price = recent[-1]
        
        # Проверяем сигнал
        if up_spikes >= self.config.spikes_to_enter:
            return Signal(
                type=SignalType.LONG,
                symbol=symbol,
                price=current_price,
                reason=f"Momentum LONG: {up_spikes} скачков ≥{self.config.spike_percent}%"
            )
        
        if down_spikes >= self.config.spikes_to_enter:
            return Signal(
                type=SignalType.SHORT,
                symbol=symbol,
                price=current_price,
                reason=f"Momentum SHORT: {down_spikes} скачков ≥{self.config.spike_percent}%"
            )
        
        return Signal(
            type=SignalType.NONE,
            symbol=symbol,
            price=current_price,
            reason="Нет сигнала"
        )
