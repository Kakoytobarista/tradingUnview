import sys
from pathlib import Path
from loguru import logger

# Убираем дефолтный handler
logger.remove()

# === Консоль (цветной вывод) ===
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# === Файл (с ротацией) ===
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "bot_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level="DEBUG",
    rotation="00:00",     # Новый файл каждый день в полночь
    retention="7 days",   # Храним логи 7 дней
    compression="zip",    # Старые логи сжимаем
    encoding="utf-8",
)

__all__ = ["logger"]
