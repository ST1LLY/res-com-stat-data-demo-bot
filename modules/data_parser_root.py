"""Корневой модуль для получения и обработки данных из БД
"""
import logging
# from logging import Logger
from datetime import date, timedelta
from typing import Dict, List

import numpy as np
import pandas as pd
from pandas import DataFrame

import modules.support_functions as sup_f

from .db_wrapper import DBWrapper


class DataParserRoot():
    """Корневой класс для получения и обработки данных из БД
    """

    def __init__(self, db_config) -> None:
        logging.debug('Инициализация')
        # Объект для работы с БД
        self.db_wrapper = DBWrapper(db_config)
        # Переменная хранящая основной изначальный массив данных
        # для обработки
        # устанавливается в методе set_data()
        self.data: DataFrame = pd.DataFrame({})
        # Вспомогательная переменная для обозначения пустых данных
        self.df_empty_row = pd.DataFrame({'id_custome': []})

        # Текущая дата отсчета обработки данных
        # что считаем за 'сегодня'
        # устанавливается в методе set_data()
        self.current_date: date = date(1970, 1, 1)
        self.current_date_str: str = ""

        # Предыдущая дата отсчета обработки данных
        # что считаем за 'вчера'
        # устанавливается в методе set_data()
        self.previous_date: date = date(1970, 1, 1)
        self.previous_date_str: str = ""

        logging.info('Инициализация выполнена')

    def set_common_attrs(self, agg_data: Dict, data_cur_date: DataFrame, data_prev_date: DataFrame) -> Dict:
        """Вычисление общих стат. значений для каждой записи атрибутов
        """
        prev_count = data_prev_date['id_custome'].count()
        cur_count = data_cur_date['id_custome'].count()
        # Если данных за пред. и текущее значение нет
        if not prev_count and not cur_count:
            # Возвращаем пустой словарь
            return {}

        # Проверяем количество предыдущих значений
        #
        if prev_count != 0:
            # Предыдущие значения присутствуют
            # Расчитываем стат. данные
            agg_data['pd_avg_flat_total_area'] = sup_f.round_area(data_prev_date['total_area'].mean())
            agg_data['pd_avg_flat_price'] = sup_f.round_million(data_prev_date['price'].mean())
            agg_data['pd_avg_flat_price_per_metr'] = sup_f.round_thousand(
                data_prev_date['price'].sum() / data_prev_date['total_area'].sum())
        else:
            # Предыдущие значения отсутствуют
            # Заполняем стат. данные нулями
            agg_data['pd_avg_flat_total_area'] = 0
            agg_data['pd_avg_flat_price'] = 0
            agg_data['pd_avg_flat_price_per_metr'] = 0

        # Проверяем количество текущих значений
        #
        if cur_count != 0:
            # Текущие значения присутствуют
            # Расчитываем стат. данные
            agg_data['avg_flat_total_area'] = sup_f.round_area(data_cur_date['total_area'].mean())
            agg_data['avg_flat_price'] = sup_f.round_million(data_cur_date['price'].mean())
            agg_data['avg_flat_price_per_metr'] = sup_f.round_thousand(
                data_cur_date['price'].sum() / data_cur_date['total_area'].sum())
        else:
            # Текущие значения отсутствуют
            # Заполняем стат. данные нулями
            agg_data['avg_flat_total_area'] = 0
            agg_data['avg_flat_price'] = 0
            agg_data['avg_flat_price_per_metr'] = 0
        # Заполняем значения дат
        agg_data['pd_price_actual_date'] = self.previous_date
        agg_data['price_actual_date'] = self.current_date

        # Расчитываем относительные изменения стат. данных
        agg_data['ch_avg_flat_total_area'] = sup_f.generate_percent(
            agg_data['pd_avg_flat_total_area'], agg_data['avg_flat_total_area'])
        agg_data['ch_avg_flat_price'] = sup_f.generate_percent(
            agg_data['pd_avg_flat_price'], agg_data['avg_flat_price'])
        agg_data['ch_avg_flat_price_per_metr'] = sup_f.generate_percent(
            agg_data['pd_avg_flat_price_per_metr'], agg_data['avg_flat_price_per_metr'])

        # Заполняем значения количества записей
        agg_data['pd_count_flats'] = prev_count
        agg_data['count_flats'] = cur_count
        # Заполняем значение изменения количества записей
        agg_data['ch_count_flats'] = agg_data['count_flats'] - agg_data['pd_count_flats']

        # Заполняем количество появившихся записей в текущую дату по id_custome
        agg_data['count_show'] = np.setdiff1d(data_cur_date['id_custome'], data_prev_date['id_custome']).size
        # Заполняем количество пропавших записей в текущую дату по id_custome
        agg_data['count_hide'] = np.setdiff1d(data_prev_date['id_custome'], data_cur_date['id_custome']).size

        return agg_data

    def generate_stat_data(self, cur_data: DataFrame, prev_data: DataFrame, group_rows: List[str]) -> List[Dict]:
        """Генерация стат. данных по двум наборам данных

        Args:
            cur_data (DataFrame): Данные, относительно которых
            считать изменения
            prev_data (DataFrame): Данные по которым считаются изменения
            group_rows (List[str]): Список из строк для группировки данных

        Returns:
            List[Dict]: Рассчитанные стат. данные
        """
        # Группируем наборы данных по указанным ключам
        cur_grouped = cur_data.groupby(group_rows)
        prev_grouped = prev_data.groupby(group_rows)
        # Получаем наименования групп
        cur_group_names = np.array(list(cur_grouped.groups.keys()))
        prev_group_names = np.array(list(prev_grouped.groups.keys()))
        # Общие групы для обоих массивов данных
        common_group_names = sup_f.merge_np_lists(cur_group_names, prev_group_names)
        logging.debug(f"common_group_names = {common_group_names}")
        # Группы только для массива данных текущей даты
        only_cur_group_names = sup_f.diff_np_lists(cur_group_names, prev_group_names)
        logging.debug(f"only_cur_group_names = {only_cur_group_names}")
        # Группы только для массива данных предыдущей даты
        only_prev_group_names = sup_f.diff_np_lists(prev_group_names, cur_group_names)
        logging.debug(f"only_prev_group_names = {only_prev_group_names}")

        output_data = []
        # Генерируем стат. данные по общим группам
        for group_name in common_group_names:

            if len(group_rows) > 1:
                # Дополняем вывод кастомными полями
                # {'rb_title': 'Аквилон Парк', 'rooms_count_title': '1'}
                agg_row_data = {value: group_name[key] for (key, value) in enumerate(group_rows)}
                group_name = tuple(group_name)
            else:
                # Дополняем вывод кастомными полями
                # {'rooms_count_title': '1'}
                agg_row_data = {group_rows[0]: group_name}

            # Получаем значения по имени групп
            cur_group = cur_grouped.get_group(group_name)
            prev_group = prev_grouped.get_group(group_name)
            # Генерируем стат. данные по этим данным из групп
            agg_row_data = self.set_common_attrs(agg_row_data, cur_group, prev_group)
            output_data.append(agg_row_data)

        for group_name in only_cur_group_names:
            if len(group_rows) > 1:
                # {'rb_title': 'Аквилон Парк', 'rooms_count_title': '1'}
                agg_row_data = {value: group_name[key] for (key, value) in enumerate(group_rows)}
                group_name = tuple(group_name)
            else:
                # {'rooms_count_title': '1'}
                agg_row_data = {group_rows[0]: group_name}

            cur_group = cur_grouped.get_group(group_name)
            agg_row_data = self.set_common_attrs(agg_row_data, cur_group, self.df_empty_row)
            output_data.append(agg_row_data)

        for group_name in only_prev_group_names:
            if len(group_rows) > 1:
                # {'rb_title': 'Аквилон Парк', 'rooms_count_title': '1'}
                agg_row_data = {value: group_name[key] for (key, value) in enumerate(group_rows)}
                group_name = tuple(group_name)
            else:
                # {'rooms_count_title': '1'}
                agg_row_data = {group_rows[0]: group_name}

            prev_group = prev_grouped.get_group(group_name)
            agg_row_data = self.set_common_attrs(agg_row_data, self.df_empty_row, prev_group)
            output_data.append(agg_row_data)

        return sup_f.sorted_data(output_data)

    def get_old_data(self, from_date: date, to_date: date) -> DataFrame:
        """Получение повторяющихся ежедневно записей
        за промежуток от from_date до to_date

        Args:
            from_date (datetime): Начало промежутка
            to_date (datetime): Конец промежутка

        Returns:
            Series: Данные с повторяющимися записями каждый день
        """
        # Получем общее количество дней в диапазоне
        len_days = (to_date - from_date).days + 1
        # Берем срез по диапазону из основного набора данных
        data_slice = self.data[(self.data.price_actual_date >= str(from_date)) &
                               (self.data.price_actual_date <= str(to_date))].copy()
        # Из среза берем только значения id_custome
        data_slice_min = data_slice[['id_custome']]
        # Группируем по id_custome и расчитываем количество каждого id_custome
        data_slice_min_grouped = data_slice_min.groupby('id_custome').agg(
            counted=pd.NamedAgg(column='id_custome', aggfunc='count'))
        # Получем срез где id_custome встречаются каждый день в диапазоне
        old_rows_ids = data_slice_min_grouped[data_slice_min_grouped.counted == len_days]
        # Переводим в список из уникальных значений id_custome
        old_ids_list = list(set(old_rows_ids.index.values))
        # Получем записи которые встречаются каждый день в диапазоне и
        # возвращаем их
        return data_slice[data_slice['id_custome'].isin(old_ids_list)].drop_duplicates(subset=['id_custome'])

    def get_new_data(self, from_date: date, to_date: date) -> DataFrame:
        """Получение уникальных записей новых квартир за промежуток
        с from_date по to_date.
        Данные которые появляются каждый последующий день и отсутствуют
        в предыдущем
        Args:
            from_date (datetime): Начало промежутка
            to_date (datetime): Конец промежутка

        Returns:
            Series: Данные с новыми записями каждый день
        """
        # Берем срез по диапазону из основного набора данных
        data_slice = self.data[(self.data.price_actual_date >= str(from_date)) &
                               (self.data.price_actual_date <= str(to_date))].copy()
        check_date = from_date
        diffed_ids = []
        while check_date <= to_date:
            # Расчитываем предыдущую дату от текущей
            prev_check_date = check_date + timedelta(days=-1)
            # Берем диапазон по предыдущей дате
            prev_day_slice = data_slice[data_slice.price_actual_date == str(prev_check_date)]
            # Берем диапазон по текущей дате
            cur_day_slice = data_slice[data_slice.price_actual_date == str(check_date)]
            # Получаем id_custome которые есть в наборе текущей даты но
            # отсутствуеют в наборе по предыдущей даты
            diffed_ids += list(np.setdiff1d(cur_day_slice['id_custome'], prev_day_slice['id_custome']))
            # Переходим к следующим текущей и предыдущей датам
            check_date += timedelta(days=1)
        # Получаем набор уникальных значений id_custome за диапазон
        # которые появлялись каждый день относительно предыдущего
        unique_ids_list = list(set(diffed_ids))
        # Получаем срез по таким id_custome и возвращаем его
        return data_slice[data_slice['id_custome'].isin(unique_ids_list)].drop_duplicates(subset=['id_custome'])

    def get_sell_data(self, from_date: date, to_date: date) -> DataFrame:
        """Получение уникальных записей проданных квартир за промежуток
        с from_date по to_date.
        Данные которые пропадают каждый последующий день и присутствуют
        в предыдущем
        Args:
            from_date (datetime): Начало промежутка
            to_date (datetime): Конец промежутка

        Returns:
            Series: Данные с пропадающими записями каждый день
        """
        # Берем срез по диапазону из основного набора данных
        data_slice = self.data[(self.data.price_actual_date >= str(from_date)) &
                               (self.data.price_actual_date <= str(to_date))].copy()
        check_date = from_date
        diffed_ids = []
        while check_date <= to_date:
            # Расчитываем предыдущую дату от текущей
            prev_check_date = check_date + timedelta(days=-1)
            # Берем диапазон по предыдущей дате
            prev_day_slice = data_slice[data_slice.price_actual_date == str(prev_check_date)]
            # Берем диапазон по текущей дате
            cur_day_slice = data_slice[data_slice.price_actual_date == str(check_date)]
            # Получаем id_custome которые есть в наборе предыдущей даты но
            # отсутствуеют в наборе по текущей даты
            diffed_ids += list(np.setdiff1d(prev_day_slice['id_custome'], cur_day_slice['id_custome']))
            # Переходим к следующим текущей и предыдущей датам
            check_date += timedelta(days=1)
        # Получаем набор уникальных значений id_custome за диапазон
        # которые пропадали каждый день относительно предыдущего
        unique_ids_list = list(set(diffed_ids))
        # Получаем срез по таким id_custome и возвращаем его
        return data_slice[data_slice['id_custome'].isin(unique_ids_list)].drop_duplicates(subset=['id_custome'])
