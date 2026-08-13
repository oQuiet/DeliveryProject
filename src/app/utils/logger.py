import sys

from loguru import logger

logger.remove()


logger.add(
    sink=sys.stdout,
    serialize=True,
    colorize=True,
    format="{message}",
    level="INFO",
    enqueue=True,
)
