import time
import sys
sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

from core import settings, BybitClient, logger
from services import Fetcher, Analyzer, Trader


def main():
    # Проверяем ключи
    if not settings.api_key or not settings.api_secret:
        logger.error("Установи BYBIT_API_KEY и BYBIT_API_SECRET в .env")
        return
    
    # Инициализация
    client = BybitClient(
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        testnet=settings.testnet,
    )
    
    fetcher = Fetcher(client)
    analyzer = Analyzer(spike_threshold=0.5)  # 0.5% скачок
    trader = Trader(client, default_qty="0.001")  # 0.001 BTC
    
    symbol = "BTCUSDT"
    interval = "5"  # 5-минутные свечи
    
    logger.info(f"Запуск бота для {symbol}")
    logger.info(f"Интервал: {interval}m | Порог скачка: {analyzer.spike_threshold}%")
    logger.info(f"Testnet: {settings.testnet}")
    logger.info("-" * 40)
    
    while True:
        try:
            # 1. Получаем данные
            candles = fetcher.get_candles(symbol, interval, limit=10)
            price = fetcher.get_current_price(symbol)
            
            # 2. Анализируем
            signal = analyzer.analyze(candles, symbol)
            
            # 3. Выводим информацию
            logger.info(f"{symbol}: ${price:.2f} | {signal.reason}")
            
            # 4. Исполняем (если есть сигнал)
            if signal.type.value != "none":
                logger.warning(f"СИГНАЛ: {signal.type.value.upper()}")
                # Раскомментируй для реальной торговли:
                # result = trader.execute(signal)
                # logger.info(f"Ордер: {result}")
            
            # Ждём до следующей проверки (60 сек)
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("Бот остановлен")
            break
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
