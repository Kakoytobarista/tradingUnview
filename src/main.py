import time
import sys
sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

from core import settings, BybitClient, logger
from services import Fetcher, Trader, Strategy, StrategyConfig


def main():
    # Проверяем ключи
    if not settings.api_key or not settings.api_secret:
        logger.error("Установи BYBIT_API_KEY и BYBIT_API_SECRET в .env")
        return
    
    # Инициализация клиента
    client = BybitClient(
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        testnet=settings.testnet,
    )
    
    # Сервисы
    fetcher = Fetcher(client)
    trader = Trader(client)
    
    # Конфиг стратегии
    config = StrategyConfig(
        symbol="BTCUSDT",
        amount_usdt=100.0,
        leverage=1,
        
        # Вход
        entry_spike_percent=0.3,    # 0.3% скачок
        spikes_to_enter=2,          # 2 подряд
        
        # Stop Loss
        initial_sl_percent=0.3,
        breakeven_trigger=0.3,
        
        # Trailing
        trailing_tight=0.30,
        trailing_medium=0.28,
        trailing_normal=0.25,
        trailing_loose=0.20,
        
        # Защита
        guaranteed_trigger=10.0,
        guaranteed_min=5.0,
        
        # Лимиты
        cooldown_minutes=15,
        max_losses_per_day=3,
        
        # ⚠️ DRY RUN MODE - БЕЗ РЕАЛЬНЫХ СДЕЛОК
        dry_run=True,
    )
    
    strategy = Strategy(trader, fetcher, config)
    
    logger.info("=" * 50)
    logger.info("🤖 TRADING BOT STARTED")
    logger.info("=" * 50)
    logger.info(f"Symbol: {config.symbol}")
    logger.info(f"Amount: ${config.amount_usdt} | Leverage: {config.leverage}x")
    logger.info(f"Entry: {config.spikes_to_enter} spikes of {config.entry_spike_percent}%")
    logger.info(f"Initial SL: {config.initial_sl_percent}%")
    logger.info(f"Cooldown: {config.cooldown_minutes} min | Max losses: {config.max_losses_per_day}/day")
    logger.info(f"Testnet: {settings.testnet}")
    logger.info(f"⚠️  DRY RUN: {config.dry_run} (no real trades)")
    logger.info("=" * 50)
    
    tick_interval = 5  # секунд между проверками
    
    while True:
        try:
            # Один тик стратегии
            result = strategy.tick()
            
            # Логируем
            action = result["action"]
            price = result["price"]
            details = result["details"]
            
            if action == "none":
                logger.debug(f"${price:.2f} | {details}")
            elif action == "blocked":
                logger.warning(f"${price:.2f} | BLOCKED: {details}")
            elif action in ("enter_long", "enter_short"):
                logger.info(f"${price:.2f} | 🚀 {action.upper()}: {details}")
            elif action == "update_sl":
                logger.info(f"${price:.2f} | 📊 {details}")
            elif action == "close":
                logger.info(f"${price:.2f} | 🔴 CLOSED: {details}")
            
            time.sleep(tick_interval)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
