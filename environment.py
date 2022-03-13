"""
    Файл с общими конфигурационными параметрами
"""
import os
# Путь до корневой директории
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Путь до конфиг файла бота
BOT_CONFIG_PATH = os.path.join(ROOT_DIR, 'configs', 'settings.conf')
# Путь до конфиг файла бота
LOGS_DIR_PATH = os.path.join(ROOT_DIR, 'logs')
