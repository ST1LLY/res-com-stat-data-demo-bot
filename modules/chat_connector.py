"""
Модуль коннектор для логов чат-бота
"""
import logging


class ChatConnector():
    """Класс обертка для отправки логов чат-ботом в канал
    """

    def __init__(self, notify_config):
        logging.debug('Инициализация')
        self.bot_header = str(notify_config['header'])
        # self.bot = telepot.Bot(notify_config['token'])
        self.chat_id = notify_config['chat_id']
        logging.info('Инициализация выполнена')

    def send_message(self, text: str) -> None:
        """Отправка информационных сообщений

        Args:
            text (str): Текст сообщения
        """
        self.bot.sendMessage(self.chat_id, f'{self.bot_header} {text}', parse_mode='HTML')

    def send_error(self, text: str) -> None:
        """Отправка сообщений об ошибках

        Args:
            text (str): Текст сообщения
        """
        self.bot.sendMessage(self.chat_id, f'{self.bot_header} 🆘 {text}')

    def send_success(self, text: str) -> None:
        """Отправка сообщений об успешно выполненных действиях

        Args:
            text (str): Текст сообщения
        """
        self.bot.sendMessage(self.chat_id, f'{self.bot_header} ✅ {text}')
