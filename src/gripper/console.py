from loguru import logger
from overhead_log import Level
from rich.console import Console
from rich.logging import RichHandler

console = Console()


def configure_logging(level: Level = Level.DEFAULT):
    logger.remove()
    logger.add(
        RichHandler(level, console=console),
        colorize=True,
        level=level,
        format=lambda _: "{message}",
        backtrace=False,
    )
