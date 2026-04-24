from loguru import logger
from pathlib import Path

logger.remove()

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def configure_logger(log_name: str = "app"):
    logger.add(
        sink=f"logs/{log_name}.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} <green>{message}</green>",
    )
    return logger


__all__ = ["logger", "configure_logger"]
