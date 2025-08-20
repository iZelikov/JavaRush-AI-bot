from datetime import datetime

from utils import logger

def on_start():
    start_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    logger.info(f'✨ Бот запущен: {start_time}')

def on_shutdown():
    stop_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    logger.info(f'⛔ Бот остановлен: {stop_time}')