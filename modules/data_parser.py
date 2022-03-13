"""Модуль для получения и обработки данных из БД
"""
import logging
from datetime import timedelta
from typing import Dict, List
import pandas as pd
from pandas import DataFrame
from .data_parser_root import DataParserRoot
from . import support_functions as sup_f


class DataParser(DataParserRoot):
    """Класс для получения и обработки данных из БД

    Args:
        DataParserRoot (class): Корневой класс для получения и обработки данных из БД
    """

    def __init__(self, db_config):
        logging.debug('Инициализация')
        DataParserRoot.__init__(self, db_config)
        # Срез новых записей данных за текущий день
        self.__new_data_current_day: DataFrame = pd.DataFrame({})

        # Срез старых записей данных за текущий день
        self.__old_data_current_day: DataFrame = pd.DataFrame({})

        # Срез старых записей данных за предыдущий день
        self.__old_data_previous_day: DataFrame = pd.DataFrame({})

        # Срез проданных записей данных за текущий день
        self.__sell_data_current_day: DataFrame = pd.DataFrame({})

        # Срез данных за текущий день
        self.data_current_day: DataFrame = pd.DataFrame({})

        # Срез данных за предыдущий день
        self.data_previous_day: DataFrame = pd.DataFrame({})

    def init_data(self, sql_query: str = '', file_path: str = '') -> None:
        """Инициализация данных для последующих обработки и получения

        Args:
            sql_query (str): SQL-запрос для полученния данных из БД
            file_path (str): The path to the file contained data
        """
        logging.info('Инициализация значений для последующей обработки')

        if not sql_query and not file_path:
            raise Exception('The sql_query param or the file_path param must be provided')

        # Получаем данные для обработки
        if sql_query:
            logging.debug(f'Получение основного набора данных по запросу: \n {sql_query}')
            self.data = self.db_wrapper.execute_select_pd(sql_query)
            # self.data.to_csv('data.csv', encoding='utf-8')
        else:
            logging.debug(f'Getting data from the file: \n {file_path}')
            self.data = pd.read_csv(file_path, encoding='utf-8', parse_dates=['price_actual_date'])

        logging.debug(f'Записей получено: {len(self.data)}')

        # Получаем текущую дату 'сегодня' из данных
        self.current_date = self.data.price_actual_date.max().date()
        logging.debug(f'Текущая дата определена: {self.current_date}')
        # Переводим текущую дату в тектовый формат для сравнения в pd
        self.current_date_str = str(self.current_date)

        # Устанавливаем дату предыдущего дня
        self.previous_date = self.current_date + timedelta(days=-1)
        logging.debug(f'Предыдущая дата: {self.previous_date}')
        # Переводим дату предыдущего дня в строчный вид
        self.previous_date_str = str(self.previous_date)

        # Устанавливаем срез данных за текущий день
        self.data_current_day = self.data[self.data.price_actual_date == self.current_date_str].copy()
        logging.debug(
            f'Количество записей в срезе за дату {self.current_date_str}: {len(self.data_current_day)}')
        # Устанавливаем срез данных за предыдущий день
        self.data_previous_day = self.data[self.data.price_actual_date == self.previous_date_str].copy()
        logging.debug(
            f'Количество записей в срезе за дату {self.previous_date_str}: {len(self.data_previous_day)}')

        self.__old_data_current_day = self.get_old_data(
            self.current_date + timedelta(days=-30), self.current_date)
        logging.debug(
            f'Количество старых записей за текущую дату {self.current_date}: {len(self.__old_data_current_day)}')

        self.__old_data_previous_day = self.get_old_data(
            self.previous_date + timedelta(days=-30), self.previous_date)
        logging.debug(
            f'Количество старых записей за предыдущую дату: {len(self.__old_data_previous_day)}')

        self.__new_data_current_day = sup_f.get_diff_data(self.data_current_day, self.data_previous_day)
        logging.debug(
            f'Количество новых записей за текущую дату: {len(self.__new_data_current_day)}')

        self.__sell_data_current_day = self.get_sell_data(self.previous_date, self.current_date)
        logging.debug(
            f'Количество проданных записей за текущую дату: {len(self.__sell_data_current_day)}')

    def get_common_cons_all_rb(self) -> Dict:
        """Полученние стат. данных общей сводки общей статистики
        по всему окружению

        Returns:
            Dict: стат. данные общей сводки общей статистики
        """
        return self.set_common_attrs({}, self.data_current_day, self.data_previous_day)

    def get_common_cons_each_count_flats(self) -> List[Dict]:
        """Получение стат. данных общей статистики в разрезе типа комнат

        Returns:
            List[Dict]: Стат. данные общей статистики в разрезе типа комнат
        """
        return self.generate_stat_data(self.data_current_day, self.data_previous_day, ['rooms_count_title'])

    def get_common_cons_each_rbs(self) -> List[Dict]:
        """Получение стат. данных общей статистики в разрезе типа ЖК

        Returns:
            List[Dict]: Стат. данные общей статистики в разрезе типа ЖК
        """
        return self.generate_stat_data(self.data_current_day, self.data_previous_day, ['rb_title'])

    def get_common_cons_each_rb_to_count_flats(self) -> List[Dict]:
        """Получение стат. данных общей статистики в разрезе типа ЖК
        по типу комнат

        Returns:
            List[Dict]: Стат. данные общей статистики в разрезе типа ЖК
            по типу комнат
        """
        return self.generate_stat_data(self.data_current_day,
                                       self.data_previous_day,
                                       ['rb_title', 'rooms_count_title'])

    def get_new_cons_all_rb(self) -> Dict:
        """Получение стат. данных новых за текущую дату относительно старых
        за текущую дату общей сводки

        Returns:
            List[Dict]: Стат. данные общей сводки
        """

        return self.set_common_attrs({}, self.__new_data_current_day, self.__old_data_current_day)

    def get_new_cons_each_count_flats(self) -> List[Dict]:
        """Стат. данные новые за текущую дату относительно старых за пред.
        дату по типу квартир

        Returns:
            List[Dict]: Стат. данные по типу квартир
        """
        return self.generate_stat_data(self.__new_data_current_day,
                                       self.__old_data_current_day,
                                       ['rooms_count_title'])

    def get_new_cons_each_rbs(self) -> List[Dict]:
        """Стат. данные новые за текущую дату относительно старых за пред.
        дату по типу ЖК

        Returns:
            List[Dict]: Стат. данные по типу ЖК
        """
        return self.generate_stat_data(self.__new_data_current_day,
                                       self.__old_data_current_day,
                                       ['rb_title'])

    def get_new_cons_each_rb_to_count_flats(self) -> List[Dict]:
        """Стат. данные новые за текущую дату относительно старых за пред.
        дату по типу ЖК и типу квартир

        Returns:
            List[Dict]: Стат. данные по типу ЖК и типу квартир
        """
        return self.generate_stat_data(self.__new_data_current_day,
                                       self.__old_data_current_day,
                                       ['rb_title', 'rooms_count_title'])

    ######

    def get_sell_cons_all_rb(self) -> Dict:
        """Получение стат. данных проданных за текущую дату относительно старых
        за текущую дату общей сводки

        Returns:
            List[Dict]: Стат. данные общей сводки
        """

        return self.set_common_attrs({}, self.__sell_data_current_day, self.__old_data_current_day)

    def get_sell_cons_each_count_flats(self) -> List[Dict]:
        """Стат. данные проданные за текущую дату относительно старых за пред.
        дату по типу квартир

        Returns:
            List[Dict]: Стат. данные по типу квартир
        """
        return self.generate_stat_data(self.__sell_data_current_day,
                                       self.__old_data_current_day,
                                       ['rooms_count_title'])

    def get_sell_cons_each_rbs(self) -> List[Dict]:
        """Стат. данные проданные за текущую дату относительно старых за пред.
        дату по типу ЖК

        Returns:
            List[Dict]: Стат. данные по типу ЖК
        """
        return self.generate_stat_data(self.__sell_data_current_day,
                                       self.__old_data_current_day,
                                       ['rb_title'])

    def get_sell_cons_each_rb_to_count_flats(self) -> List[Dict]:
        """Стат. данные проданные за текущую дату относительно старых за пред.
        дату по типу ЖК и типу квартир

        Returns:
            List[Dict]: Стат. данные по типу ЖК и типу квартир
        """
        return self.generate_stat_data(self.__sell_data_current_day,
                                       self.__old_data_current_day,
                                       ['rb_title', 'rooms_count_title'])

    def get_old_cons_all_rb(self) -> Dict:
        """Полученние стат. данных общей сводки общей статистики
        по всему окружению старые за текушую дату со старыми за
        предыдущую дату

        Returns:
            Dict: стат. данные общей сводки общей статистики
        """
        return self.set_common_attrs({}, self.__old_data_current_day, self.__old_data_previous_day)

    def get_old_cons_each_count_flats(self) -> List[Dict]:
        """Получение стат. данных общей статистики в разрезе типа комнат
        по старые за текушую дату со старыми за предыдущую дату
        Returns:
            List[Dict]: Стат. данные общей статистики в разрезе типа комнат
        """
        return self.generate_stat_data(self.__old_data_current_day,
                                       self.__old_data_previous_day,
                                       ['rooms_count_title'])

    def get_old_cons_each_rbs(self) -> List[Dict]:
        """Получение стат. данных общей статистики в разрезе типа ЖК
        по старые за текушую дату со старыми за предыдущую дату
        Returns:
            List[Dict]: Стат. данные общей статистики в разрезе типа ЖК
        """
        return self.generate_stat_data(self.__old_data_current_day,
                                       self.__old_data_previous_day,
                                       ['rb_title'])

    def get_old_cons_each_rb_to_count_flats(self) -> List[Dict]:
        """Получение стат. данных общей статистики в разрезе типа ЖК
        по типу комнат по старые за текушую дату со старыми за предыдущую дату

        Returns:
            List[Dict]: Стат. данные общей статистики в разрезе типа ЖК
            по типу комнат
        """
        return self.generate_stat_data(self.__old_data_current_day,
                                       self.__old_data_previous_day,
                                       ['rb_title', 'rooms_count_title'])
