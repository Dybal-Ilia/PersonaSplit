import logging
import sys

logger = logging.getLogger("PersonaSplit_logger")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)

console_handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(console_handler)
