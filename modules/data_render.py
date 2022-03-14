"""Модуль рендеринга данных в текстовый вид для вывода в боте
"""
import json
import logging
from datetime import date, timedelta
from typing import Dict, List

from typing_extensions import Literal

import modules.support_functions as sup_f

from .constants import RenderConsts
from .data_parser import DataParser
from .db_wrapper import DBWrapper


class DataRender():
    """Класс для перевода данных в текстовый вид для вывода в боте
    """

    def __init__(self, chat_config, db_config):
        logging.debug('Инициализация')

        self.__chat_config = chat_config

        # Инициализация обертки для работы с БД
        self.__db_wrapper = DBWrapper(db_config)
        # Инициализация парсера данных из БД
        self.__data_parser = DataParser(db_config)
        # Cегодняшняя дата для шапки
        self.__current_date: date = date(1970, 1, 1)
        # Предыдущая дата для шапки
        self.__previous_date: date = date(1970, 1, 1)

        # Словарь с отрендеренными данными для вывода в чат-боте
        self.__rendered_data: Dict = {
            # Общая сводка по всем окружениям только с критическими
            'cons_report_text_cut': '',
            # Список со стат. данными для вывода по каждому окружению
            'arround_list': []
        }

        # Устанавливаем текущую дату по которой получаем данные
        self.__current_data_date = sup_f.parse_date(self.__chat_config['current_date'])
        # Устанавливаем сегодняшнюю дату для шапки
        self.__current_date = sup_f.parse_current_date(self.__chat_config['current_date'])
        # Устанавливаем предыдущую дату для шапки
        self.__previous_date = self.__current_date + timedelta(days=-1)
        # Получаем id окружений из конфиг файла
        arround_ids = [x.strip() for x in self.__chat_config['arround_ids'].split(',')]
        logging.debug(
            f"id окружений из конфиг файла arround_ids = {arround_ids}")
        # Получаем title окружений из конфиг файла
        arround_titles = [x.strip() for x in self.__chat_config['arround_titles'].split(',')]
        logging.debug(
            f"title окружений из конфиг файла arround_titles = {arround_titles}")

        if len(arround_ids) != len(arround_titles):
            raise Exception(f"""
                В конфиг файле не мапятся настройки для окружений!
                len(arround_ids) = {len(arround_ids)}
                len(arround_titles) = {len(arround_titles)}
                """)

        self.__arround_list = [dict(
            id=arround_ids[i],
            title=arround_titles[i]
        ) for i in range(0, len(arround_ids))]

        self.__render_data(is_load_from_dump=bool(int(self.__chat_config['is_load_from_dump'])))

        logging.info('Инициализация выполнена')

    def __render_data(self, is_load_from_dump: bool = False) -> None:
        """Рендер словаря со текстовым предствалением данных для чат-бота

        Args:
            is_load_from_dump (bool): Загрузить данные из дамп файла
        """
        arround_ids = ','.join([x['id'] for x in self.__arround_list])

        dump_file_path = f'.\\data\\{arround_ids}.csv'
        if is_load_from_dump:
            self.__data_parser.init_data(file_path=dump_file_path)
        else:
            self.__data_parser.init_data(self.__get_data_select(arround_ids))
            self.__data_parser.data.to_csv(dump_file_path, encoding='utf-8')

        self.__rendered_data['cons_report_text_cut'] = self.__get_cons_report_text_cut_all_arounds()

        for arround in self.__arround_list:
            logging.info(f"Рендеринг текстового вывода для окружения {arround['title']}")
            arroud_data: Dict = {
                # Наименование окружения
                'arround_title': arround['title'],
                # Данные по общей статистике
                'summary_stat': {
                    # Текст общая сводка в урезанный
                    'cons_report_text_cut': '',
                    # Текст общая сводка в полный
                    'cons_report_text_full': '',
                    # Текст по всем типам квартир
                    'count_flats_all_text': '',
                    # Список текстов по каждому типу квартир
                    'count_flats_all_list': [],
                    # Текст по каждому ЖК
                    'each_rb_all_text': '',
                    # Список текстов по каждому ЖК
                    'each_rb_all_list': [],
                    # Список в разрезе ЖК по типу комнат
                    'each_rb_flats_list': [],
                    # Список в разрезе типа комнат по ЖК
                    'each_flats_rb_list': [],
                },
                # Данные только по новым
                'new_stat': {
                    # Текст общая сводка в урезанный
                    'cons_report_text_cut': '',
                    # Текст общая сводка в полный
                    'cons_report_text_full': '',
                    # Текст по всем типам квартир
                    'count_flats_all_text': '',
                    # Список текстов по каждому типу квартир
                    'count_flats_all_list': [],
                    # Текст по каждому ЖК
                    'each_rb_all_text': '',
                    # Список текстов по каждому ЖК
                    'each_rb_all_list': [],
                    # Список в разрезе ЖК по типу комнат
                    'each_rb_flats_list': [],
                    # Список в разрезе типа комнат по ЖК
                    'each_flats_rb_list': [],
                },
                # Данные только по старым
                'old_stat': {
                    # Текст общая сводка в урезанный
                    'cons_report_text_cut': '',
                    # Текст общая сводка в полный
                    'cons_report_text_full': '',
                    # Текст по всем типам квартир
                    'count_flats_all_text': '',
                    # Список текстов по каждому типу квартир
                    'count_flats_all_list': [],
                    # Текст по каждому ЖК
                    'each_rb_all_text': '',
                    # Список текстов по каждому ЖК
                    'each_rb_all_list': [],
                    # Список в разрезе ЖК по типу комнат
                    'each_rb_flats_list': [],
                    # Список в разрезе типа комнат по ЖК
                    'each_flats_rb_list': [],
                },
                # Данные только по проданным
                'sell_stat': {
                    # Текст общая сводка в урезанный
                    'cons_report_text_cut': '',
                    # Текст общая сводка в полный
                    'cons_report_text_full': '',
                    # Текст по всем типам квартир
                    'count_flats_all_text': '',
                    # Список текстов по каждому типу квартир
                    'count_flats_all_list': [],
                    # Текст по каждому ЖК
                    'each_rb_all_text': '',
                    # Список текстов по каждому ЖК
                    'each_rb_all_list': [],
                    # Список в разрезе ЖК по типу комнат
                    'each_rb_flats_list': [],
                    # Список в разрезе типа комнат по ЖК
                    'each_flats_rb_list': [],
                }

            }

            dump_file_path = f".\\data\\{arround['id']}.csv"
            if is_load_from_dump:
                self.__data_parser.init_data(file_path=dump_file_path)
            else:
                self.__data_parser.init_data(self.__get_data_select(arround['id']))
                self.__data_parser.data.to_csv(f".\\data\\{arround['id']}.csv", encoding='utf-8')

            # Заполнеяем текстовые данные для Общей статистики
            arroud_data['summary_stat']['cons_report_text_cut'] = self.__get_cons_report_text_cut(
                arround, RenderConsts.TYPE_SUMMARY_STAT)
            arroud_data['summary_stat']['cons_report_text_full'] = self.__get_cons_report_text_full(
                arround, RenderConsts.TYPE_SUMMARY_STAT)
            arroud_data['summary_stat']['count_flats_all_text'] = self.__get_count_flats_all_text(
                arround, RenderConsts.TYPE_SUMMARY_STAT)
            arroud_data['summary_stat']['count_flats_all_list'] = self.__get_count_flats_all_types_list(
                arround, RenderConsts.TYPE_SUMMARY_STAT)
            arroud_data['summary_stat']['each_rb_all_text'] = self.__get_each_rb_all_text(
                arround, RenderConsts.TYPE_SUMMARY_STAT)
            arroud_data['summary_stat']['each_rb_all_list'] = self.__get_each_rb_all_list(
                arround, RenderConsts.TYPE_SUMMARY_STAT)
            arroud_data['summary_stat']['each_rb_flats_list'] = self.__get_each_rb_flats_list(
                arround, RenderConsts.TYPE_SUMMARY_STAT)
            arroud_data['summary_stat']['each_flats_rb_list'] = self.__get_each_flats_rb_list(
                arround, RenderConsts.TYPE_SUMMARY_STAT)

            # Заполнеяем текстовые данные для Только по новым за 1 день
            arroud_data['new_stat']['cons_report_text_cut'] = self.__get_cons_report_text_cut(
                arround, RenderConsts.TYPE_NEW_STAT)
            arroud_data['new_stat']['cons_report_text_full'] = self.__get_cons_report_text_full(
                arround, RenderConsts.TYPE_NEW_STAT)
            arroud_data['new_stat']['count_flats_all_text'] = self.__get_count_flats_all_text(
                arround, RenderConsts.TYPE_NEW_STAT)
            arroud_data['new_stat']['count_flats_all_list'] = self.__get_count_flats_all_types_list(
                arround, RenderConsts.TYPE_NEW_STAT)
            arroud_data['new_stat']['each_rb_all_text'] = self.__get_each_rb_all_text(
                arround, RenderConsts.TYPE_NEW_STAT)
            arroud_data['new_stat']['each_rb_all_list'] = self.__get_each_rb_all_list(
                arround, RenderConsts.TYPE_NEW_STAT)
            arroud_data['new_stat']['each_rb_flats_list'] = self.__get_each_rb_flats_list(
                arround, RenderConsts.TYPE_NEW_STAT)
            arroud_data['new_stat']['each_flats_rb_list'] = self.__get_each_flats_rb_list(
                arround, RenderConsts.TYPE_NEW_STAT)

            # Заполнеяем текстовые данные для Только по старым за 1 день
            arroud_data['old_stat']['cons_report_text_cut'] = self.__get_cons_report_text_cut(
                arround, RenderConsts.TYPE_OLD_STAT)
            arroud_data['old_stat']['cons_report_text_full'] = self.__get_cons_report_text_full(
                arround, RenderConsts.TYPE_OLD_STAT)
            arroud_data['old_stat']['count_flats_all_text'] = self.__get_count_flats_all_text(
                arround, RenderConsts.TYPE_OLD_STAT)
            arroud_data['old_stat']['count_flats_all_list'] = self.__get_count_flats_all_types_list(
                arround, RenderConsts.TYPE_OLD_STAT)
            arroud_data['old_stat']['each_rb_all_text'] = self.__get_each_rb_all_text(
                arround, RenderConsts.TYPE_OLD_STAT)
            arroud_data['old_stat']['each_rb_all_list'] = self.__get_each_rb_all_list(
                arround, RenderConsts.TYPE_OLD_STAT)
            arroud_data['old_stat']['each_rb_flats_list'] = self.__get_each_rb_flats_list(
                arround, RenderConsts.TYPE_OLD_STAT)
            arroud_data['old_stat']['each_flats_rb_list'] = self.__get_each_flats_rb_list(
                arround, RenderConsts.TYPE_OLD_STAT)

            # Заполняем текстовые данные для Только по проданным за 1 день
            arroud_data['sell_stat']['cons_report_text_cut'] = self.__get_cons_report_text_cut(
                arround, RenderConsts.TYPE_SELL_STAT)
            arroud_data['sell_stat']['cons_report_text_full'] = self.__get_cons_report_text_full(
                arround, RenderConsts.TYPE_SELL_STAT)
            arroud_data['sell_stat']['count_flats_all_text'] = self.__get_count_flats_all_text(
                arround, RenderConsts.TYPE_SELL_STAT)
            arroud_data['sell_stat']['count_flats_all_list'] = self.__get_count_flats_all_types_list(
                arround, RenderConsts.TYPE_SELL_STAT)
            arroud_data['sell_stat']['each_rb_all_text'] = self.__get_each_rb_all_text(
                arround, RenderConsts.TYPE_SELL_STAT)
            arroud_data['sell_stat']['each_rb_all_list'] = self.__get_each_rb_all_list(
                arround, RenderConsts.TYPE_SELL_STAT)
            arroud_data['sell_stat']['each_rb_flats_list'] = self.__get_each_rb_flats_list(
                arround, RenderConsts.TYPE_SELL_STAT)
            arroud_data['sell_stat']['each_flats_rb_list'] = self.__get_each_flats_rb_list(
                arround, RenderConsts.TYPE_SELL_STAT)

            self.__rendered_data['arround_list'].append(arroud_data)

        file_dump = ".\\data\\rendered_data.json"
        with open(file_dump, 'w', encoding='utf-8') as file:
            json.dump(self.__rendered_data, file)
            logging.info(f"{file_dump} dumped")

    def get_rendered_data(self):
        return self.__rendered_data

    def __get_cons_report_text_cut(
            self,
            arround: Dict,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> str:
        """Генерация текста Общей сводки урезанной

        Args:
            arround (Dict): Данные окружения
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации

        Returns:
            str: текст Общей сводки урезанной
        """

        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            text_inner = sup_f.get_cons_all_rb(self.__data_parser.get_common_cons_all_rb())
            return f"📊 📃 The general summary for {arround['title']} from " \
                   f'{sup_f.datetime_to_str(self.__previous_date)} to {sup_f.datetime_to_str(self.__current_date)}:' \
                   '\n' + text_inner

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            text_inner = sup_f.get_cons_all_rb(self.__data_parser.get_new_cons_all_rb())
            return f"📊 📃 The general summary of new flats relative to old ones in {arround['title']} on " \
                   f'{sup_f.datetime_to_str(self.__current_date)}:' \
                   '\n' + text_inner

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            text_inner = sup_f.get_cons_all_rb(self.__data_parser.get_old_cons_all_rb())
            return f"📊 📃 The general summary old flats in {arround['title']} from " \
                   f'{sup_f.datetime_to_str(self.__previous_date)} to {sup_f.datetime_to_str(self.__current_date)}:' \
                   '\n' + text_inner

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            text_inner = sup_f.get_cons_all_rb(self.__data_parser.get_sell_cons_all_rb())
            return f"📊 📃 The general summary of old flats relative to old ones in {arround['title']} on " \
                   f'{sup_f.datetime_to_str(self.__current_date)}:' \
                   '\n' + text_inner

        raise Exception(f'Unknown type_stat: {type_stat}')

    def __get_cons_report_text_full(
            self,
            arround: Dict,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> str:
        """Генерация текста Общей сводки полной

        Args:
            arround (Dict): Данные окружения
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации
        Returns:
            str: текст Общей сводки полной
        """
        o_text = ''
        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            o_text = f"📤 The changes in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to {sup_f.datetime_to_str(self.__current_date)}:'

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            o_text = f"📤 The changes in {arround['title']} by new flats relative to old ones on " \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            o_text = f"📤 The changes in {arround['title']} by old flats from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to {sup_f.datetime_to_str(self.__current_date)}:'

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            o_text = f"📤 The changes in {arround['title']} by sold flats relative to old ones on " \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'

        o_text += '\n' + self.__generate_general_changes_body(type_stat)
        return o_text

    def __get_each_rb_flats_list(
            self,
            arround: Dict,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> List:
        """Генерация текстового вывода по всем типам ЖК по типам квартир

        Args:
            arround (Dict): Данные окружения
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации
        Returns:
            List: Текстовый вывод по всем типам ЖК по типам квартир
        """

        data_each_rb_flats_list = []
        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            data_each_rb_flats_list = self.__data_parser.get_common_cons_each_rb_to_count_flats()

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            data_each_rb_flats_list = self.__data_parser.get_new_cons_each_rb_to_count_flats()

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            data_each_rb_flats_list = self.__data_parser.get_old_cons_each_rb_to_count_flats()

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            data_each_rb_flats_list = self.__data_parser.get_sell_cons_each_rb_to_count_flats()

        o_list = sup_f.gen_cons_each_rb_to_count_flats(data_each_rb_flats_list)['each_rb_flats_list']

        for rb_row in o_list:
            header = ''

            if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
                header = f"📊 🔢 The changes by number of rooms in {rb_row['rb_title']} of {arround['title']} " \
                         f'from {sup_f.datetime_to_str(self.__previous_date)} ' \
                         f'to {sup_f.datetime_to_str(self.__current_date)}:'

            elif type_stat == RenderConsts.TYPE_NEW_STAT:
                header = f"📊 🔢 The changes of new flats relative to old ones by number of rooms in {rb_row['rb_title']}" \
                         f" of {arround['title']} on " \
                         f'{sup_f.datetime_to_str(self.__current_date)}:'

            elif type_stat == RenderConsts.TYPE_OLD_STAT:
                header = f"📊 🔢 The changes of old flats by number of rooms in {rb_row['rb_title']}" \
                         f" of {arround['title']} from " \
                         f'{sup_f.datetime_to_str(self.__previous_date)} to {sup_f.datetime_to_str(self.__current_date)}:'

            elif type_stat == RenderConsts.TYPE_SELL_STAT:
                header = f"📊 🔢 The changes of sold flats relative to old ones by number of rooms " \
                         f"in {rb_row['rb_title']} in {arround['title']} on " \
                         f'{sup_f.datetime_to_str(self.__current_date)}:'

            if not 'all_types_text' in rb_row or not 'all_types_list' in rb_row:
                continue

            for row in rb_row['all_types_list']:
                row['text'] = header + '\n' + row['text']

            rb_row['all_types_text'] = header + '\n' + rb_row['all_types_text']

        return o_list

    def __get_each_flats_rb_list(
            self,
            arround: Dict,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> List:
        """Генерация текстового вывода по всем типам квартир в разрезе ЖК

        Args:
            arround (Dict): Данные окружения
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации
        Returns:
            List: Текстовый вывод по всем типам квартир в разрезе ЖК
        """
        o_list = []
        data_each_count_flats_to_rb = []
        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            data_each_count_flats_to_rb = self.__data_parser.get_common_cons_each_rb_to_count_flats()

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            data_each_count_flats_to_rb = self.__data_parser.get_new_cons_each_rb_to_count_flats()

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            data_each_count_flats_to_rb = self.__data_parser.get_old_cons_each_rb_to_count_flats()

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            data_each_count_flats_to_rb = self.__data_parser.get_sell_cons_each_rb_to_count_flats()

        o_list = sup_f.gen_cons_each_count_flats_to_rb(data_each_count_flats_to_rb)['each_flats_rb_list']

        for flat_row in o_list:
            if not 'all_types_text' in flat_row or not 'all_types_list' in flat_row:
                continue
            for row in flat_row['all_types_list']:
                header = ''
                if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
                    header = f"📊 🔢 The changes by number of rooms in {row['type']} of {arround['title']} " \
                             f'from {sup_f.datetime_to_str(self.__previous_date)} ' \
                             f'to {sup_f.datetime_to_str(self.__current_date)}:'

                elif type_stat == RenderConsts.TYPE_NEW_STAT:
                    header = f"📊 🔢 The changes of new flats relative to old ones by number of rooms " \
                             f"in {row['type']} of {arround['title']} on " \
                             f'{sup_f.datetime_to_str(self.__current_date)}:'

                elif type_stat == RenderConsts.TYPE_OLD_STAT:
                    header = f"📊 🔢 The changes of old flats by number of rooms in {row['type']}" \
                             f"of {arround['title']} from {sup_f.datetime_to_str(self.__previous_date)}" \
                             f"to {sup_f.datetime_to_str(self.__current_date)}:"

                elif type_stat == RenderConsts.TYPE_SELL_STAT:
                    header = f"📊 🔢 The changes of sold flats relative to old ones by number of rooms " \
                             f"in {row['type']} of {arround['title']} on " \
                             f'{sup_f.datetime_to_str(self.__current_date)}:'

                row['text'] = header + '\n' + row['text']
            header = ''
            if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
                header = f"📊 🏘 The changes by {flat_row['rooms_count_title']} in {arround['title']} from " \
                         f'{sup_f.datetime_to_str(self.__previous_date)} to ' \
                         f'{sup_f.datetime_to_str(self.__current_date)}:'
            elif type_stat == RenderConsts.TYPE_NEW_STAT:
                header = f"📊 🏘 The changes of new flats relative to old ones by {flat_row['rooms_count_title']} " \
                         f"in {arround['title']} on " \
                         f'{sup_f.datetime_to_str(self.__current_date)}:'
            elif type_stat == RenderConsts.TYPE_OLD_STAT:
                header = f"📊 🏘 The changes of old flats by {flat_row['rooms_count_title']} " \
                         f"in {arround['title']} from " \
                         f'{sup_f.datetime_to_str(self.__previous_date)} to ' \
                         f'{sup_f.datetime_to_str(self.__current_date)}:'
            elif type_stat == RenderConsts.TYPE_SELL_STAT:
                header = f"📊 🏘 The changes of sold flats relative to old ones by {flat_row['rooms_count_title']} " \
                         f"in {arround['title']} on " \
                         f'{sup_f.datetime_to_str(self.__current_date)}:'

            flat_row['all_types_text'] = header + '\n' + flat_row['all_types_text']
        return o_list

    def __get_each_rb_all_list(
            self,
            arround: Dict,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> List:
        """Получение списка текста по каждому типу ЖК

        Args:
            arround (Dict): Данные окружения
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации
        Returns:
            List: текст по каждому типу ЖК
        """
        o_list = []
        header = ''

        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            o_list = sup_f.gen_cons_each_rb(
                self.__data_parser.get_common_cons_each_rbs(), False)['all_types_list']
            header = f"📊 🔢 The changes in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to ' \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            o_list = sup_f.gen_cons_each_rb(
                self.__data_parser.get_new_cons_each_rbs(), False)['all_types_list']
            header = f"📊 🔢 The changes of new flats relative to old ones by residential complex " \
                     f"in {arround['title']} on " \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            o_list = sup_f.gen_cons_each_rb(
                self.__data_parser.get_old_cons_each_rbs(), False)['all_types_list']
            header = f"📊 🔢 The changes of old flats by residential complex in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to ' \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            o_list = sup_f.gen_cons_each_rb(
                self.__data_parser.get_sell_cons_each_rbs(), False)['all_types_list']
            header = f"📊 🔢 The changes of sold flats relative to old ones by residential complex " \
                     f"in {arround['title']} on {sup_f.datetime_to_str(self.__current_date)}:"

        for row in o_list:
            row['text'] = header + '\n' + row['text']
        return o_list

    def __get_each_rb_all_text(
            self, arround: Dict,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> str:
        """Получения текста изменений по всем типам ЖК

        Args:
            arround (Dict): Данные окружения
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации
        Returns:
            str: текст изменений по всем типам ЖК
        """
        o_text = ''
        text_inner = ''
        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            o_text = f"📊 🔢 The changes by residential complex in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to ' \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'
            text_inner = sup_f.gen_cons_each_rb(self.__data_parser.get_common_cons_each_rbs(), False)['all_types_text']

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            o_text = f"📊 🔢 The changes of new flats relative to old ones by residential complex " \
                     f"in {arround['title']} on {sup_f.datetime_to_str(self.__current_date)}:"

            text_inner = sup_f.gen_cons_each_rb(
                self.__data_parser.get_new_cons_each_rbs(), False)['all_types_text']

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            o_text = f"📊 🔢 The changes of old flats by residential complex in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to {sup_f.datetime_to_str(self.__current_date)}:'
            text_inner = sup_f.gen_cons_each_rb(
                self.__data_parser.get_old_cons_each_rbs(), False)['all_types_text']

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            o_text = f"📊 🔢 The changes of sold flats relative to old ones by residential complex in" \
                     f" {arround['title']} on {sup_f.datetime_to_str(self.__current_date)}:"

            text_inner = sup_f.gen_cons_each_rb(
                self.__data_parser.get_sell_cons_each_rbs(), False)['all_types_text']

        o_text += '\n' + text_inner
        return o_text

    def __get_count_flats_all_types_list(
            self,
            arround: Dict,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> List:
        """Получение списка текста по каждому типу квартир

        Args:
            arround (Dict): Данные окружения
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации

        Returns:
            List: текст по каждому типу квартир
        """
        o_list = []
        header = ''

        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            header = f"📊 🔢 The changes by number of rooms in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to ' \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'
            o_list = sup_f.gen_cons_each_count_flats(
                self.__data_parser.get_common_cons_each_count_flats(), False)['all_types_list']

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            header = f"📊 🔢 The changes of new flats relative to old ones by number of rooms in" \
                     f"{arround['title']} on {sup_f.datetime_to_str(self.__current_date)}:"

            o_list = sup_f.gen_cons_each_count_flats(
                self.__data_parser.get_new_cons_each_count_flats(), False)['all_types_list']

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            header = f"📊 🔢 The changes of old flats by number of rooms in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to {sup_f.datetime_to_str(self.__current_date)}:'

            o_list = sup_f.gen_cons_each_count_flats(
                self.__data_parser.get_old_cons_each_count_flats(), False)['all_types_list']

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            header = f"📊 🔢 The changes of sold flats relative to old ones by number of rooms" \
                     f" in {arround['title']} on " \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'
            o_list = sup_f.gen_cons_each_count_flats(
                self.__data_parser.get_sell_cons_each_count_flats(), False)['all_types_list']

        for row in o_list:
            row['text'] = header + '\n' + row['text']
        return o_list

    def __get_count_flats_all_text(
            self,
            arround: Dict,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> str:
        """Получения текста изменений по всем типам квартир

        Args:
            arround (Dict): Данные окружения
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации
        Returns:
            str: текст изменений по всем типам квартир
        """
        o_text = ''
        text_inner = ''
        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            o_text = f"📊 🔢 The changes by number of rooms in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to ' \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'
            text_inner = sup_f.gen_cons_each_count_flats(
                self.__data_parser.get_common_cons_each_count_flats(), False)['all_types_text']

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            o_text = f"📊 🔢 The changes of new flats relative to old ones by number of rooms" \
                     f" in {arround['title']} on " \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'
            text_inner = sup_f.gen_cons_each_count_flats(
                self.__data_parser.get_new_cons_each_count_flats(), False)['all_types_text']

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            o_text = f"📊 🔢 The changes of old flats by number of rooms" \
                     f" in {arround['title']} from " \
                     f'{sup_f.datetime_to_str(self.__previous_date)} to {sup_f.datetime_to_str(self.__current_date)}:'

            text_inner = sup_f.gen_cons_each_count_flats(
                self.__data_parser.get_old_cons_each_count_flats(), False)['all_types_text']

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            o_text = f"📊 🔢 The changes of sold flats relative to old ones by number of rooms" \
                     f" in {arround['title']} on " \
                     f'{sup_f.datetime_to_str(self.__current_date)}:'
            text_inner = sup_f.gen_cons_each_count_flats(
                self.__data_parser.get_sell_cons_each_count_flats(), False)['all_types_text']

        o_text += '\n' + text_inner
        return o_text

    def __generate_general_changes_body(
            self,
            type_stat: Literal[RenderConsts.ALLOWED_TYPES_STATS]) -> str:
        """Генерация части текста полной общей сводки по общая сводка,
        типу квартир и типу ЖК

        Args:
            type_stat (Literal[RenderConsts.ALLOWED_TYPES_STATS]): Тип статистики для генерации

        Returns:
            str: Тескст части текста полной общей сводки по общая сводка,
        типу квартир и типу ЖК
        """
        data_all_rb = {}
        data_each_count_flats = []
        data_each_rbs = []
        if type_stat == RenderConsts.TYPE_SUMMARY_STAT:
            data_all_rb = self.__data_parser.get_common_cons_all_rb()
            data_each_count_flats = self.__data_parser.get_common_cons_each_count_flats()
            data_each_rbs = self.__data_parser.get_common_cons_each_rbs()

        elif type_stat == RenderConsts.TYPE_NEW_STAT:
            data_all_rb = self.__data_parser.get_new_cons_all_rb()
            data_each_count_flats = self.__data_parser.get_new_cons_each_count_flats()
            data_each_rbs = self.__data_parser.get_new_cons_each_rbs()

        elif type_stat == RenderConsts.TYPE_OLD_STAT:
            data_all_rb = self.__data_parser.get_old_cons_all_rb()
            data_each_count_flats = self.__data_parser.get_old_cons_each_count_flats()
            data_each_rbs = self.__data_parser.get_old_cons_each_rbs()

        elif type_stat == RenderConsts.TYPE_SELL_STAT:
            data_all_rb = self.__data_parser.get_sell_cons_all_rb()
            data_each_count_flats = self.__data_parser.get_sell_cons_each_count_flats()
            data_each_rbs = self.__data_parser.get_sell_cons_each_rbs()

        text_inner_all_rb = sup_f.get_cons_all_rb(data_all_rb)
        text_inner_each_count_flats = sup_f.gen_cons_each_count_flats(data_each_count_flats, True)
        text_inner_each_rbs = sup_f.gen_cons_each_rb(data_each_rbs, True)

        o_text = '📊 📃 The general summary:' + '\n' + text_inner_all_rb
        o_text += 2 * '\n' + '📊 🔢 The significant changes by number of rooms:' + \
                  '\n' + text_inner_each_count_flats['all_types_text']
        o_text += 2 * '\n' + '📊 🏘 The significant changes by residential complex:' + '\n' + \
                  text_inner_each_rbs['all_types_text']
        return o_text

    def __get_cons_report_text_cut_all_arounds(self) -> str:
        """Генерация текста общей сводки по всем окружениям

        Returns:
            str: текст общей сводки по всем окружениям
        """
        o_text = f"📤 The general summary of {', '.join([x['title'] for x in self.__arround_list])} from " \
                 f'{sup_f.datetime_to_str(self.__previous_date)} to ' \
                 f'{sup_f.datetime_to_str(self.__current_date)}:'
        o_text += '\n' + self.__generate_general_changes_body(RenderConsts.TYPE_SUMMARY_STAT)
        return o_text

    def __get_data_select(self, arround_ids: str) -> str:
        """Генерация SELECT SQL-запроса для получения основного массива
        данных для обработки

        Args:
            arround_ids (str): Окружения через запятую

        Returns:
            str: SELECT SQL-запрос
        """
        query = f"""
        SELECT 
            fp.id_custome,
            frct.title as rooms_count_title, 
            fp.total_area,
            case when fp.discount_price <> 0 then fp.discount_price
            else fp.price
            end as price,
            fp.price_actual_date, 
            rl.title as rb_title
        FROM public.flat_prices fp
        inner join public.flat_room_count_types frct on frct.id = fp.rooms_count_id
        inner join public.rb_list rl on rl.id = fp.rb_id
        where  fp.price_actual_date <= '{self.__current_data_date}'::date 
        and fp.price_actual_date >= ('{self.__current_data_date}'::date - interval '30' day)
        and fp.rb_id in (select rb_id from public.around_rb_list where around_id in ({arround_ids}));
        """
        return query
