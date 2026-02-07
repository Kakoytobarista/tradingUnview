from dataclasses import dataclass, field
from datetime import datetime, timedelta
from core.models import SignalType
from core.logger import logger
from .analyzer import Analyzer, AnalyzerConfig
from .trader import Trader
from .fetcher import Fetcher


@dataclass
class StrategyConfig:
    """Конфигурация стратегии."""
    # Символ и сумма
    symbol: str = "BTCUSDT"
    amount_usdt: float = 100.0
    leverage: int = 1
    
    # Вход (передаётся в Analyzer)
    entry_spike_percent: float = 0.5
    spikes_to_enter: int = 2
    
    # Stop Loss
    initial_sl_percent: float = 0.3     # Начальный SL
    breakeven_trigger: float = 0.3      # Когда переводить в breakeven
    
    # Trailing offset (динамический)
    trailing_tight: float = 0.30        # <2% профита
    trailing_medium: float = 0.28       # 2-5% профита
    trailing_normal: float = 0.25       # 5-10% профита
    trailing_loose: float = 0.20        # >10% профита
    
    # Защита
    guaranteed_trigger: float = 10.0    # После +10%...
    guaranteed_min: float = 5.0         # ...минимум +5%
    
    # Cooldown и лимиты
    cooldown_minutes: int = 15          # После SL не входить N минут
    max_losses_per_day: int = 3         # Макс убыточных сделок в день
    
    # DEBUG MODE
    dry_run: bool = True                # True = только логи, без реальных сделок


@dataclass
class TradeState:
    """Состояние текущей сделки."""
    in_position: bool = False
    side: str = ""                      # "long" / "short"
    entry_price: float = 0.0
    max_price: float = 0.0              # Максимум для long, минимум для short
    current_sl: float = 0.0
    
    # История цен для анализа входа
    price_history: list[float] = field(default_factory=list)
    
    # Cooldown и лимиты
    last_loss_time: datetime | None = None
    losses_today: int = 0
    last_loss_date: str = ""            # Для сброса счётчика каждый день


class Strategy:
    """
    Торговая стратегия.
    
    ВСЯ ЛОГИКА ЗДЕСЬ:
    - Состояние позиции
    - Решение когда входить/выходить
    - Trailing stop
    - Cooldown после убытка
    - Лимит убытков в день
    """
    
    def __init__(
        self,
        trader: Trader,
        fetcher: Fetcher,
        config: StrategyConfig | None = None,
    ):
        self.config = config or StrategyConfig()
        self.trader = trader
        self.fetcher = fetcher
        self.state = TradeState()
        
        # Создаём анализатор с нужным конфигом
        self.analyzer = Analyzer(AnalyzerConfig(
            spike_percent=self.config.entry_spike_percent,
            spikes_to_enter=self.config.spikes_to_enter,
        ))
    
    def tick(self) -> dict:
        """
        Один тик стратегии. Вызывать периодически.
        
        Returns:
            {
                "action": "none" | "enter_long" | "enter_short" | "update_sl" | "close" | "blocked",
                "price": float,
                "details": str
            }
        """
        # Получаем текущую цену
        current_price = self.fetcher.get_current_price(self.config.symbol)
        
        # Добавляем в историю
        self.state.price_history.append(current_price)
        if len(self.state.price_history) > 20:
            self.state.price_history.pop(0)
        
        if not self.state.in_position:
            return self._check_entry(current_price)
        else:
            return self._manage_position(current_price)
    
    def _is_blocked(self) -> tuple[bool, str]:
        """Проверить блокировки (cooldown, лимит убытков)."""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # Сброс счётчика убытков на новый день
        if self.state.last_loss_date != today:
            self.state.losses_today = 0
            self.state.last_loss_date = today
        
        # Проверка лимита убытков
        if self.state.losses_today >= self.config.max_losses_per_day:
            return True, f"Лимит убытков ({self.config.max_losses_per_day}) исчерпан на сегодня"
        
        # Проверка cooldown
        if self.state.last_loss_time:
            cooldown_end = self.state.last_loss_time + timedelta(minutes=self.config.cooldown_minutes)
            if now < cooldown_end:
                remaining = (cooldown_end - now).seconds // 60
                return True, f"Cooldown: ждём ещё {remaining} мин"
        
        return False, ""
    
    def _check_entry(self, current_price: float) -> dict:
        """Проверить условия входа."""
        # Проверяем блокировки
        blocked, reason = self._is_blocked()
        if blocked:
            return {
                "action": "blocked",
                "price": current_price,
                "details": reason
            }
        
        signal = self.analyzer.check_entry(
            self.state.price_history,
            self.config.symbol
        )
        
        if signal.type == SignalType.LONG:
            self._enter_position(current_price, "long")
            return {
                "action": "enter_long",
                "price": current_price,
                "details": signal.reason
            }
        
        if signal.type == SignalType.SHORT:
            self._enter_position(current_price, "short")
            return {
                "action": "enter_short",
                "price": current_price,
                "details": signal.reason
            }
        
        return {
            "action": "none",
            "price": current_price,
            "details": signal.reason
        }
    
    def _enter_position(self, price: float, side: str):
        """Войти в позицию."""
        # Исполняем (если не dry_run)
        if not self.config.dry_run:
            if side == "long":
                self.trader.enter_long(
                    self.config.symbol,
                    self.config.amount_usdt,
                    self.config.leverage
                )
            else:
                self.trader.enter_short(
                    self.config.symbol,
                    self.config.amount_usdt,
                    self.config.leverage
                )
        
        # Обновляем состояние
        self.state.in_position = True
        self.state.side = side
        self.state.entry_price = price
        self.state.max_price = price
        
        # Начальный SL
        offset = price * (self.config.initial_sl_percent / 100)
        if side == "long":
            self.state.current_sl = price - offset
        else:
            self.state.current_sl = price + offset
        
        # Ставим SL на бирже (если не dry_run)
        if not self.config.dry_run:
            self.trader.set_stop_loss(self.config.symbol, self.state.current_sl)
        
        mode = "[DRY RUN] " if self.config.dry_run else ""
        logger.info(f"{mode}Вошли {side.upper()} на {price:.2f}, SL: {self.state.current_sl:.2f}")
    
    def _manage_position(self, current_price: float) -> dict:
        """Управление открытой позицией."""
        # Обновляем максимум/минимум
        if self.state.side == "long":
            if current_price > self.state.max_price:
                self.state.max_price = current_price
        else:
            if current_price < self.state.max_price:
                self.state.max_price = current_price
        
        # Проверяем SL
        sl_hit = False
        if self.state.side == "long" and current_price <= self.state.current_sl:
            sl_hit = True
        elif self.state.side == "short" and current_price >= self.state.current_sl:
            sl_hit = True
        
        if sl_hit:
            profit = self._calc_profit(current_price)
            is_loss = profit < 0
            self._close_position(is_loss)
            return {
                "action": "close",
                "price": current_price,
                "details": f"SL сработал. Профит: {profit:.2f}%"
            }
        
        # Рассчитываем новый SL
        new_sl = self._calc_trailing_sl(current_price)
        
        # Обновляем если нужно
        should_update = False
        if self.state.side == "long" and new_sl > self.state.current_sl:
            should_update = True
        elif self.state.side == "short" and new_sl < self.state.current_sl:
            should_update = True
        
        if should_update:
            self.state.current_sl = new_sl
            # Обновляем SL на бирже (если не dry_run)
            if not self.config.dry_run:
                self.trader.set_stop_loss(self.config.symbol, new_sl)
            profit = self._calc_profit(current_price)
            mode = "[DRY RUN] " if self.config.dry_run else ""
            return {
                "action": "update_sl",
                "price": current_price,
                "details": f"{mode}SL → {new_sl:.2f} (профит: {profit:.2f}%)"
            }
        
        profit = self._calc_profit(current_price)
        return {
            "action": "none",
            "price": current_price,
            "details": f"Держим. Профит: {profit:.2f}%, SL: {self.state.current_sl:.2f}"
        }
    
    def _calc_profit(self, current_price: float) -> float:
        """Рассчитать профит в процентах."""
        if self.state.entry_price == 0:
            return 0.0
        
        if self.state.side == "long":
            return ((current_price - self.state.entry_price) / self.state.entry_price) * 100
        else:
            return ((self.state.entry_price - current_price) / self.state.entry_price) * 100
    
    def _get_trailing_offset(self, profit: float) -> float:
        """Получить offset в зависимости от профита."""
        if profit < 2:
            return self.config.trailing_tight
        elif profit < 5:
            return self.config.trailing_medium
        elif profit < 10:
            return self.config.trailing_normal
        else:
            return self.config.trailing_loose
    
    def _calc_trailing_sl(self, current_price: float) -> float:
        """Рассчитать trailing stop loss."""
        profit = self._calc_profit(current_price)
        max_profit = self._calc_profit(self.state.max_price)
        entry = self.state.entry_price
        
        # Если не достигли breakeven — держим начальный
        if profit < self.config.breakeven_trigger:
            return self.state.current_sl
        
        # Breakeven
        breakeven_sl = entry
        
        # Trailing от максимума
        offset_pct = self._get_trailing_offset(max_profit)
        offset = self.state.max_price * (offset_pct / 100)
        
        if self.state.side == "long":
            trailing_sl = self.state.max_price - offset
        else:
            trailing_sl = self.state.max_price + offset
        
        # Гарантированный минимум
        guaranteed_sl = None
        if max_profit >= self.config.guaranteed_trigger:
            g_offset = entry * (self.config.guaranteed_min / 100)
            if self.state.side == "long":
                guaranteed_sl = entry + g_offset
            else:
                guaranteed_sl = entry - g_offset
        
        # Выбираем лучший
        if self.state.side == "long":
            candidates = [breakeven_sl, trailing_sl]
            if guaranteed_sl:
                candidates.append(guaranteed_sl)
            return max(candidates)
        else:
            candidates = [breakeven_sl, trailing_sl]
            if guaranteed_sl:
                candidates.append(guaranteed_sl)
            return min(candidates)
    
    def _close_position(self, is_loss: bool = False):
        """Закрыть позицию."""
        # Закрываем на бирже (если не dry_run)
        if not self.config.dry_run:
            self.trader.close(self.config.symbol)
        
        mode = "[DRY RUN] " if self.config.dry_run else ""
        
        # Если убыток — обновляем счётчики
        if is_loss:
            self.state.losses_today += 1
            self.state.last_loss_time = datetime.now()
            logger.warning(f"{mode}Позиция закрыта с убытком. Убытков сегодня: {self.state.losses_today}/{self.config.max_losses_per_day}")
        else:
            logger.info(f"{mode}Позиция закрыта с профитом")
        
        # Сбрасываем состояние позиции
        self.state.in_position = False
        self.state.side = ""
        self.state.entry_price = 0.0
        self.state.max_price = 0.0
        self.state.current_sl = 0.0
    
    def get_status(self) -> dict:
        """Получить текущий статус стратегии."""
        blocked, reason = self._is_blocked()
        return {
            "in_position": self.state.in_position,
            "side": self.state.side,
            "entry_price": self.state.entry_price,
            "current_sl": self.state.current_sl,
            "losses_today": self.state.losses_today,
            "max_losses": self.config.max_losses_per_day,
            "blocked": blocked,
            "block_reason": reason,
        }
