from collections.abc import Mapping
import sys

from loguru import logger

from app.config import get_settings

setting = get_settings()

BASE_FORMAT = "<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>"


def development_formatter(record: Mapping[str, object]) -> str:
    if record["extra"]:
        return BASE_FORMAT + " | <yellow>{extra}</yellow>\n{exception}"

    return BASE_FORMAT + "\n{exception}"


def setup_logging() -> None:
    env = setting.APP_ENV
    level = setting.LOG_LEVEL

    logger.remove()

    if env == "prod":
        logger.add(sys.stdout, level=level, serialize=True, enqueue=True)
    else:
        logger.add(sys.stdout, level=level, format=development_formatter)

    logger.add(
        "logs/app.log",
        rotation="10 MB",  # новый файл каждые 10 МБ
        retention="7 days",  # хранить 7 дней
        compression="zip",  # старые архивировать
    )


setup_logging()
