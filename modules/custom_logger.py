# """
# Питон файл с инициализированными логгерами для импорта в модули
# """
# import os
# import logging.config
# from colorlog import ColoredFormatter
# from settings import LOGGING_CONFIG_PATH
# os.system('color')
#
# # Инициалзиация логгера (start)
# logging.config.fileConfig(LOGGING_CONFIG_PATH,
#                           disable_existing_loggers=False)
# # Установка форматирования для кастомного логгирования
# MY_LOGFORMAT = '%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(funcName)s - %(log_color)s %(levelname)s ' \
#     '%(reset)s - %(message)s'
# formatter = ColoredFormatter(MY_LOGFORMAT)
# stream = logging.StreamHandler()
# stream.setFormatter(formatter)
#
# # Создания кастомного логгера
# logger = logging.getLogger('backendLogger')
# logger.addHandler(stream)
# # Инициализиация логгера (end)
