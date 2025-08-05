from datetime import datetime

def on_start():
    start_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(f'Бот запущен: {start_time}')

def on_shutdown():
    stop_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(f'Бот остановлен: {stop_time}')