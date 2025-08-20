import logging
import sys

from config import LOG_DIR

LOG_FILE = LOG_DIR / 'bot.log'


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )

    return logging.getLogger(__name__)
