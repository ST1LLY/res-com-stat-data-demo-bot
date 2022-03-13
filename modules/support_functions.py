"""Модуль со вспомогательными функциями для обработки данных
для нет необходимости использования  переменных из объекта класса
"""
import configparser
from datetime import date, datetime, timedelta
from operator import itemgetter
from functools import cmp_to_key
from typing import Any, Dict, List
from typing import Union
import numpy as np
from pandas import DataFrame
import logging
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter


# Common function
#
#

def get_config(config_path, config_section) -> dict:
    """
    Получение конфигурационных параметров из конфиг файла
    """
    config = configparser.RawConfigParser(comment_prefixes=('#',))
    config.read(config_path, encoding='utf-8')
    output_config = config[config_section]
    return dict(output_config)


def init_custome_logger(
        all_log_file_path,
        error_log_file_path,
        logging_level='DEBUG'
) -> logging.Logger:
    """
    Создание кастомного логгера
    """
    # Настройка хендлера для вывова в консоль

    stream_formatter = ColoredFormatter(
        '%(process)s %(thread)s: %(asctime)s - %(filename)s:%(lineno)d - %(funcName)s -%(log_color)s '
        '%(levelname)s %(reset)s - %(message)s')
    logging_level_num = 20 if logging_level == 'INFO' else 10
    max_bytes = 20 * 1024 * 1024  # 20MB максимальный размер лог файла
    backup_count = 10

    file_format = '%(process)s %(thread)s: %(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - '
    '%(message)s'

    # Настройка хендлера для вывода в лог файл
    file_handler = RotatingFileHandler(
        filename=all_log_file_path,
        mode='a',
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(fmt=file_format))
    file_handler.setLevel(logging_level_num)

    # Настройка хендлера для вывода в лог файл ошибок
    error_file_handler = RotatingFileHandler(
        filename=error_log_file_path,
        mode='a',
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8')
    error_file_handler.setFormatter(logging.Formatter(fmt=file_format))
    error_file_handler.setLevel(logging.WARNING)

    # Берем корневой логгер, который использует Flask
    # и добавляем к нему кастомные хендлеры для полуения логов Flask в
    # наши лог файлы
    logging.basicConfig(level=logging_level_num)

    logger = logging.getLogger()
    # Переопределяем для root stream handler'а формат вывода
    logger.handlers[0].setFormatter(stream_formatter)

    # logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
    return logger


# Вспомогательные функции для модуля обработки данных
#
#


def cmp(x_val: Any, y_val: Any) -> Any:
    """
    Replacement for built-in function cmp that was removed in Python 3

    Compare the two objects x and y and return an integer according to
    the outcome. The return value is negative if x < y, zero if x == y
    and strictly positive if x > y.

    https://portingguide.readthedocs.io/en/latest/comparisons.html#the-cmp-function
    """
    return (x_val > y_val) - (x_val < y_val)


def multikeysort(items: List[Dict], columns: List[str]) -> List[Dict]:
    """Сортировка списка из словарей по ключам

    Args:
        items (List[Dict]): Список словарей для сортировки
        columns (List[str]): Список ключей по которым производится сортировка

    Returns:
        List[Dict]: Отсортированный список словарей
    """
    comparers = [
        ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1))
        for col in columns
    ]

    def comparer(left: Any, right: Any) -> Any:
        """Вспомогательная функция
        """
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)

    return sorted(items, key=cmp_to_key(comparer))


def generate_percent(pd_value: float, value: float) -> float:
    """Вычисление процента изменения текущего значения
    относительно предыдущего

    Args:
        pd_value (float): Предыдущее значение
        value (float): Текущее значение

    Returns:
        float: Значение изменения в процентном соотношении
    """
    if pd_value == 0 and value > 0:
        return 100

    if pd_value > 0 and value == -100:
        return -100

    if pd_value == 0 and value == 0:
        return 0

    return round(100 * ((value - pd_value) / pd_value), 1)


def round_area(value: Any) -> float:
    """Округление значений площади до 1 знака после запятой
    Например: 53.3469545990566038 -> 53.3
    Args:
        value (Any): Округляемое значение

    Returns:
        Any: Округленное значение
    """
    return round(value, 1)


def round_million(value: Any) -> float:
    """Приведение значения цены к миллионам до 2 знаков после запятой
    Например: 8707362.502358490566 -> 8.71
    Args:
        value (Any): Округляемое значение

    Returns:
        Any: Округленное значение
    """
    return round(value / 10 ** 6, 2)


def round_thousand(value: Any) -> float:
    """Приведение значения к тысячам до 2 знаков после запятой
    163221.360390691786 -> 163.22
    Args:
        value (Any): Округляемое значение

    Returns:
        Any: Округленное значение
    """
    return round(value / 10 ** 3, 2)


def merge_np_lists(a_np_array: Any, b_np_array: Any) -> Any:
    """
        Получение общих записей в a_np_array и b_np_array
        intersect1d не отрабатывает корректно
        при ndim = 1 и ndim > 1
    """

    if a_np_array.ndim == 1:
        return np.intersect1d(a_np_array, b_np_array)

    return np.array([x for x in set(tuple(x) for x in a_np_array) & set(tuple(x) for x in b_np_array)])
    # Падает на ValueError: When changing to a larger dtype,
    # its size must be a divisor of the total size in bytes of the last axis of the array
    # ncols = a_np_array.shape[1]
    # dtype = {'names': ['f{}'.format(i) for i in range(ncols)],
    #          'formats': ncols * [a_np_array.dtype]}
    # c_np_array = np.intersect1d(a_np_array.view(dtype), b_np_array.view(dtype))
    # c_np_array = c_np_array.view(a_np_array.dtype).reshape(-1, ncols)
    # return c_np_array


def diff_np_lists(a_np_array: Any, b_np_array: Any) -> Any:
    """
        Уникальные записи в a_np_array
        относительно b_np_array
        setdiff1d не отрабатывает корректно
        при ndim = 1 и ndim > 1
    """
    if a_np_array.ndim == 1:
        return np.setdiff1d(a_np_array, b_np_array)
    return np.array([x for x in set(tuple(x) for x in a_np_array) if x not in set(tuple(x) for x in b_np_array)])
    # Падает на ValueError: When changing to a larger dtype,
    # its size must be a divisor of the total size in bytes of the last axis of the array
    # ncols = a_np_array.shape[1]
    # dtype = {'names': ['f{}'.format(i) for i in range(ncols)],
    #          'formats': ncols * [a_np_array.dtype]}
    # c_np_array = np.setdiff1d(a_np_array.view(dtype), b_np_array.view(dtype))
    # c_np_array = c_np_array.view(a_np_array.dtype).reshape(-1, ncols)
    # return c_np_array


def set_studio_to_0(data: List[Dict]) -> List[Dict]:
    """Установка значения '0' вместо 'Студия' до сортировки

    Args:
        data (List[Dict]): Список словарей со стат. данными с 'Студия'
        вместо '0'

    Returns:
        List[Dict]: Список словарей со стат. данными с '0'
        вместо 'Студия'
    """
    for row in data:
        if row['rooms_count_title'] == 'Студия':
            row['rooms_count_title'] = '0'
    return data


def set_0_to_studio(data: List[Dict]) -> List[Dict]:
    """Установка значения 'Студия' вместо '0' после сортировки

    Args:
        data (List[Dict]): Список словарей со стат. данными с '0'
        вместо 'Студия'

    Returns:
        List[Dict]: Список словарей со стат. данными с 'Студия'
        вместо '0'
    """
    for row in data:
        if row['rooms_count_title'] == '0':
            row['rooms_count_title'] = 'Студия'
    return data


def sorted_data(data: List[Dict]) -> List[Dict]:
    """Сортировка списка словарей со стат. данными

    Args:
        data (List[Dict]): Список словарей для сортировки

    Returns:
        List[Dict]: Отсортированный список словарей
    """
    if len(data) < 1:
        return data

    if 'rb_title' in data[0] and 'rooms_count_title' in data[0]:
        data = set_studio_to_0(data)
        data = multikeysort(data, ['rb_title', 'rooms_count_title'])

        data = set_0_to_studio(data)
        return data
    if 'rooms_count_title' in data[0]:
        data = set_studio_to_0(data)
        data = multikeysort(data, ['rooms_count_title'])
        data = set_0_to_studio(data)
        return data
    if 'rb_title' in data[0]:
        return multikeysort(data, ['rb_title'])

    return data


def get_diff_data(first_data: DataFrame, second_data: DataFrame) -> DataFrame:
    """
    Получение уникальный записей в first_data
    относительно second_data


    Args:
        first_data (DataFrame): Где искать уникальные записи
        second_data (DataFrame): Где искать повторяющиеся записи

    Returns:
        DataFrame: Уникальные записи из first_data
    """
    diffed_ids = np.setdiff1d(first_data['id_custome'], second_data['id_custome'])
    return first_data[first_data['id_custome'].isin(diffed_ids)]


# Вспомогательные функции при рендеринге данных в текстовый вывод для чат-бота
#
#
#


def parse_date(config_date: str) -> date:
    """Парсинг даты в строчном виде из конфиг файла
    для определения текущей даты для получения обработки данных из БД
    Args:
        config_date (str): Значение current_date из конфиг файла

    Returns:
        date: Преобразованное значение в тип date
    """
    if config_date == 'now()':
        return datetime.now().date()
    if config_date == 'now()-1':
        return datetime.now().date() + timedelta(days=-1)

    return datetime.strptime(config_date, '%Y-%m-%d').date()


def parse_current_date(config_date: str) -> date:
    """Парсинг даты в строчном виде из конфиг файла
    для определения текущей даты для вывода в боте
    Args:
        config_date (str): Значение current_date из конфиг файла

    Returns:
        date: Преобразованное значение в тип date
    """
    if config_date == 'now()' or config_date == 'now()-1':
        return datetime.now().date()
    return datetime.strptime(config_date, '%Y-%m-%d').date()


def get_cons_all_rb(data: Dict, type_only_today: str = '') -> str:
    """Генерация текстового представление по всем ЖК в наборе данных
    для общей сводки

    Args:
        data (Dict): Набор данных для рендеринга
        type_only_today (str, optional): тип данных сравнимаемых со старыми,
        если сравниваются данные по текущей даты
    Returns:
        str: Текст значений общей сводки для вывода в чат-бот
    """
    if not data:
        return ''
    body_data = gen_body_text(data, insignificant_only=False, type_only_today=type_only_today)
    return body_data


def gen_cons_each_count_flats(data: List[Dict],
                              is_daily_part: bool = False,
                              type_only_today: str = '') -> Dict:
    """Генерация для вывода по типу квартир

    Args:
        data (List[Dict]): Данные для рендеринга
        is_daily_part (bool, optional): Часть для ежедневного отчета.
        Defaults to False.
        type_only_today (str, optional): тип данных сравнимаемых со старыми,
        если сравниваются данные по текущей даты. Defaults to ''.

    Returns:
        Dict: Возвращаемое значение, если выбран
        is_daily_part = True, то расчитываются только критические значения
        Если выбран is_daily_part = False, то расчитываются все значения
    """
    if len(data) == 0:
        return {'all_types_text': '', 'all_types_list': []}

    # Текст по всем типам вместе
    all_types_text = ''
    # Список с текстами по каждому типу отдельно
    all_types_list = []
    last_data_index = len(data) - 1
    for i, row in enumerate(data):

        type_head_desc = ''
        type_menu_desc = ''
        if row['rooms_count_title'] == 'Студия':
            type_head_desc = type_menu_desc = 'Studios'
        else:
            type_head_desc = f"{row['rooms_count_title']}-room apartments"
            type_menu_desc = f"{row['rooms_count_title']}-room"

        if is_daily_part:
            body_text = gen_body_text(row, insignificant_only=True, type_only_today=type_only_today)
        else:
            body_text = gen_body_text(row, insignificant_only=False, type_only_today=type_only_today)

        if body_text:
            if not all_types_text:
                all_types_text += type_head_desc + '\n' + body_text + '\n'
            elif last_data_index != i:
                all_types_text += '\n' + type_head_desc + '\n' + body_text + '\n'
            else:
                all_types_text += '\n' + type_head_desc + '\n' + body_text

            all_types_list.append(
                {
                    'type': type_menu_desc,
                    'text': type_head_desc + '\n' + body_text,
                }
            )
    # [:-1] Вырезаем последний '\n'
    return {'all_types_text': all_types_text, 'all_types_list': all_types_list}


def gen_cons_each_rb(data: List[Dict],
                     is_daily_part: bool = False,
                     type_only_today: str = '') -> Dict:
    """Генерация для вывода по типу ЖК

    Args:
        data (List[Dict]): Данные для рендеринга
        is_daily_part (bool, optional): Часть для ежедневного отчета.
        Defaults to False.
        type_only_today (str, optional): тип данных сравнимаемых со старыми,
        если сравниваются данные по текущей даты. Defaults to ''.

    Returns:
        Dict: Возвращаемое значение, если выбран
        is_daily_part = True, то расчитываются только критические значения
        Если выбран is_daily_part = False, то расчитываются все значения
    """
    if len(data) == 0:
        return {'all_types_text': '', 'all_types_list': []}

    # Текст по всем типам вместе
    all_types_text = ''
    # Список с текстами по каждому типу отдельно
    all_types_list = []

    last_data_index = len(data) - 1
    for i, row in enumerate(data):

        type_head_desc = type_menu_desc = "🏠 " + row['rb_title']

        if is_daily_part:
            body_text = gen_body_text(row, insignificant_only=True, type_only_today=type_only_today)
        else:
            body_text = gen_body_text(row, insignificant_only=False, type_only_today=type_only_today)

        if body_text:
            if not all_types_text:
                all_types_text += type_head_desc + '\n' + body_text + '\n'
            elif last_data_index != i:
                all_types_text += '\n' + type_head_desc + '\n' + body_text + '\n'
            else:
                all_types_text += '\n' + type_head_desc + '\n' + body_text

            all_types_list.append(
                {
                    'type': type_menu_desc,
                    'text': type_head_desc + '\n' + body_text,
                }
            )
    # [:-1] Вырезаем последний '\n'
    return {'all_types_text': all_types_text, 'all_types_list': all_types_list}


def gen_cons_each_rb_to_count_flats(data: List[Dict], type_only_today: str = '') -> Dict:
    """Генерация текстов в разрезе ЖК по типу квартир

    Args:
        data (List[Dict]): Данные для рендеринга
        type_only_today (str, optional): тип данных сравнимаемых со старыми,
        если сравниваются данные по текущей даты. Defaults to ''.

    Returns:
        Dict: Возвращаемое значение
    """
    o_data: Dict = {'each_rb_flats_list': []}
    if not data:
        return o_data

    # Список уникальных наменований ЖК
    rb_titles_unic = list(set([x['rb_title'] for x in data]))
    # Список уникальных типов квартир
    # rooms_count_titles_unic = list(set([x['rooms_count_title'] for x in data]))
    for rb_title in rb_titles_unic:
        one_rb_flats_stat = {'rb_title': "🏠 " + rb_title, 'all_types_list': [], 'all_types_text': ''}

        last_data_index = len(data) - 1
        for i, row in enumerate(data):

            if row['rb_title'] != rb_title:
                continue

            if row['rooms_count_title'] == 'Студия':
                type_head_desc = type_menu_desc = 'Studios'
            else:
                type_head_desc = f"{row['rooms_count_title']}-room apartments"
                type_menu_desc = f"{row['rooms_count_title']}-room"

            body_text = gen_body_text(row, False, type_only_today)
            if body_text:
                if not one_rb_flats_stat['all_types_text']:
                    one_rb_flats_stat['all_types_text'] += type_head_desc + '\n' + body_text + '\n'
                elif last_data_index != i:
                    one_rb_flats_stat['all_types_text'] += '\n' + type_head_desc + '\n' + body_text + '\n'
                else:
                    one_rb_flats_stat['all_types_text'] += '\n' + type_head_desc + '\n' + body_text

                one_rb_flats_stat['all_types_list'].append(
                    {
                        'type': type_menu_desc,
                        'text': type_head_desc + '\n' + body_text,
                    })
        o_data['each_rb_flats_list'].append(one_rb_flats_stat)
    return o_data


def gen_cons_each_count_flats_to_rb(data: List[Dict], type_only_today: str = '') -> Dict:
    """Генерация текстов в разрезе типов квартир по типу ЖК

    Args:
        data (List[Dict]): Данные для рендеринга
        type_only_today (str, optional): тип данных сравнимаемых со старыми,
        если сравниваются данные по текущей даты. Defaults to ''.

    Returns:
        Dict: Возвращаемое значение
    """
    o_data: Dict = {'each_flats_rb_list': []}
    if not data:
        return o_data

    # Список уникальных типов квартир
    rooms_count_titles_unic = list(set([x['rooms_count_title'] for x in data]))
    for rooms_count_title in rooms_count_titles_unic:
        if rooms_count_title == 'Студия':
            type_head_desc = type_menu_desc = 'Studios'
        else:
            type_menu_desc = f"{rooms_count_title}-room"
            type_head_desc = f"{rooms_count_title}-room apartments"

        one_flat_rbs_stat: Dict = {'rooms_count_title': str, 'all_types_list': List, 'all_types_text': str}
        one_flat_rbs_stat = {'rooms_count_title': type_menu_desc, 'all_types_list': [], 'all_types_text': ''}

        last_data_index = len(data) - 1
        for i, row in enumerate(data):

            if row['rooms_count_title'] != rooms_count_title:
                continue

            body_text = gen_body_text(row, False, type_only_today)
            if body_text:
                type_head_rb_title = "🏠 " + row['rb_title']
                if not one_flat_rbs_stat['all_types_text']:
                    one_flat_rbs_stat['all_types_text'] += type_head_rb_title + '\n' + body_text + '\n'
                elif last_data_index != i:
                    one_flat_rbs_stat['all_types_text'] += '\n' + type_head_rb_title + '\n' + body_text + '\n'
                else:
                    one_flat_rbs_stat['all_types_text'] += '\n' + type_head_rb_title + '\n' + body_text

                one_flat_rbs_stat['all_types_list'].append(
                    {
                        'type': type_head_rb_title,
                        'text': type_head_desc + '\n' + body_text,
                    })
        o_data['each_flats_rb_list'].append(one_flat_rbs_stat)
    return o_data


def gen_body_text(data: Dict, insignificant_only: bool = False, type_only_today: str = '') -> str:
    """Построчная генерация текстовой информации по ключевым параметрам

    Args:
        data (Dict): Данные для парсинга
        insignificant_only (bool, optional): Только по крическим порогам.
        Defaults to False.
        type_only_today (str, optional): тип данных сравнимаемых со старыми,
        если сравниваются данные по текущей даты. Defaults to ''.

    Returns:
        str: Текст со стат. данными для вывода
    """
    strings_array = []
    # Цена за кв. метр: ⬆️ +0.1 % (174.77->174.98 тыс. руб.)
    if (not insignificant_only) or (insignificant_only and abs(float(data['ch_avg_flat_price_per_metr'])) >= 1):
        strings_array.append(gen_avg_flat_price_per_metr_str(
            data['pd_avg_flat_price_per_metr'],
            data['avg_flat_price_per_metr'],
            data['ch_avg_flat_price_per_metr'], type_only_today=type_only_today))

    # Бюджет: ⬆️ + 0.4 % (10.72->10.76 млн.руб.)
    if (not insignificant_only) or (insignificant_only and abs(float(data['ch_avg_flat_price'])) >= 1):
        strings_array.append(gen_avg_flat_price_str(
            data['pd_avg_flat_price'],
            data['avg_flat_price'],
            data['ch_avg_flat_price'], type_only_today=type_only_today))

    # Площадь: ⬆️ + 0.2 % (61.3->61.5 м²)
    if (not insignificant_only) or (insignificant_only and abs(float(data['ch_avg_flat_total_area'])) >= 1):
        strings_array.append(gen_avg_flat_total_area_str(
            data['pd_avg_flat_total_area'],
            data['avg_flat_total_area'],
            data['ch_avg_flat_total_area'], type_only_today=type_only_today))

    # Количество: 🔻 -4 кв.(557->553 кв.)
    if (not insignificant_only) or (insignificant_only and abs(float(data['ch_count_flats'])) >= 1):

        if type_only_today:
            strings_array.append(gen_avg_count_flats_str_unic(
                data['pd_count_flats'],
                data['count_flats'],
                data['count_hide'],
                data['count_show']))
        else:
            strings_array.append(gen_avg_count_flats_str(
                data['pd_count_flats'],
                data['count_flats'],
                data['ch_count_flats'], type_only_today=type_only_today))

    return '\n'.join(strings_array)


def fraction_design_str(frac_number: Union[float, int]) -> str:
    """Дизайн изменения значения доли / количества

    Args:
        frac_number (float, int): Число для отрисовки

    Returns:
        str: Задесигненное число
    """
    frac_number_norm = normalize_number(frac_number)
    if frac_number > 0:
        fraction_str = f"⬆️ +{frac_number_norm}"
    elif frac_number < 0:
        fraction_str = f"🔻️ {frac_number_norm}"
    else:
        fraction_str = "0"
    return fraction_str


def gen_avg_flat_price_per_metr_str(pd_avg_flat_price_per_metr: float,
                                    avg_flat_price_per_metr: float,
                                    ch_avg_flat_price_per_metr: float,
                                    type_only_today: str = "") -> str:
    """Генерация строки со значениями цена за кв. метр

    Args:
        pd_avg_flat_price_per_metr (float): Значение с которым сравниваем
        avg_flat_price_per_metr (float): Сравниваемое значение
        ch_avg_flat_price_per_metr (float): Изменение
        type_only_today (str, optional): Тип данных сравниваемого значения.
        Defaults to "".

    Returns:
        str: Сгенерированная строка для вывода в чат-боте
    """
    fraction_str = fraction_design_str(ch_avg_flat_price_per_metr)
    output_str = ""
    desc_str = "Price per sq. meter: "

    if type_only_today:
        pd_value = normalize_number(pd_avg_flat_price_per_metr)
        if pd_value:
            output_str = f"{desc_str}{fraction_str} % (₽{normalize_number(avg_flat_price_per_metr)}K" \
                         f"| ₽{pd_value}K)"
        else:
            output_str = f"{desc_str}₽{normalize_number(avg_flat_price_per_metr)}K"
    else:
        output_str = f"{desc_str}{fraction_str} % (₽{normalize_number(pd_avg_flat_price_per_metr)}K -> " \
                     f"₽{normalize_number(avg_flat_price_per_metr)}K)"
    return output_str


def gen_avg_flat_price_str(pd_avg_flat_price: float,
                           avg_flat_price: float,
                           ch_avg_flat_price: float,
                           type_only_today: str = "") -> str:
    """Генерация строки со значениями Бюджет

    Args:
        pd_avg_flat_price (float): Значение с которым сравниваем
        avg_flat_price (float): Сравниваемое значение
        ch_avg_flat_price (float): Изменение
        type_only_today (str, optional): Тип данных сравниваемого значения.
        Defaults to "".

    Returns:
        str: Сгенерированная строка для вывода в чат-боте
    """
    fraction_str = fraction_design_str(ch_avg_flat_price)
    output_str = ""
    desc_str = "Price: "

    if type_only_today:
        pd_value = normalize_number(pd_avg_flat_price)
        if pd_value:
            output_str = f"{desc_str}{fraction_str} % (₽{normalize_number(avg_flat_price)}M " \
                         f"| ₽{pd_value}M)"
        else:
            output_str = f"₽{desc_str}{normalize_number(avg_flat_price)}M"
    else:
        output_str = f"{desc_str}{fraction_str} % (₽{normalize_number(pd_avg_flat_price)}M -> " \
                     f"₽{normalize_number(avg_flat_price)}M)"
    return output_str


def gen_avg_flat_total_area_str(pd_avg_flat_total_area: float,
                                avg_flat_total_area: float,
                                ch_avg_flat_total_area: float,
                                type_only_today: str = "") -> str:
    """Генерация строки со значениями Площадь

    Args:
        pd_avg_flat_total_area (float): Значение с которым сравниваем
        avg_flat_total_area (float): Сравниваемое значение
        ch_avg_flat_total_area (float): Изменение
        type_only_today (str, optional): Тип данных сравниваемого значения.
        Defaults to "".

    Returns:
        str: Сгенерированная строка для вывода в чат-боте
    """
    fraction_str = fraction_design_str(ch_avg_flat_total_area)
    output_str = ""
    desc_str = "Square: "

    if type_only_today:
        pd_value = normalize_number(pd_avg_flat_total_area)
        if pd_value:
            output_str = f"{desc_str}{fraction_str} % ({normalize_number(avg_flat_total_area)} м² | {pd_value} м²)"
        else:
            output_str = f"{desc_str}{normalize_number(avg_flat_total_area)} м²"
    else:
        output_str = f"{desc_str}{fraction_str} % ({normalize_number(pd_avg_flat_total_area)} -> " \
                     f"{normalize_number(avg_flat_total_area)} м²)"
    return output_str


# Генерация строки количество квартир с уникальными


def gen_avg_count_flats_str_unic(pd_count: int, count_flats: int, count_hide: int, count_show: int) -> str:
    """Генерация строки со значениями количество квартир, когда
    получили данные с уникальными квартирами
    Args:
        pd_count (int): Значение с которым сравниваем
        count_flats (int): Сравниваемое значение
        count_hide (int): Количество появившихся записей
        count_show (int): Количество пропавших записей

    Returns:
        str: Сгенерированная строка для вывода в чат-боте
    """
    fr_count_hide = fraction_design_str(count_hide * (-1))
    fr_count_show = fraction_design_str(count_show)

    desc_str = "Number: "

    output_str = ""

    if count_show == 0 and count_hide == 0:
        output_str = f"{desc_str}0 ({pd_count} -> " \
                     f"{count_flats} fl.)"
    elif count_show == 0 and count_hide != 0:
        output_str = f"{desc_str}{fr_count_hide} ({pd_count} -> " \
                     f"{count_flats} fl.)"
    elif count_hide == 0 and count_show != 0:
        output_str = f"{desc_str}{fr_count_show} ({pd_count} -> " \
                     f"{count_flats} fl.)"
    else:
        output_str = f"{desc_str}{fr_count_show} / {fr_count_hide} ({pd_count} -> " \
                     f"{count_flats} fl.)"

    return output_str


# Генерация строки количество квартир без уникальных


def gen_avg_count_flats_str(pd_count: int, count_flats: int, ch_count_flats: int, type_only_today: str = "") -> str:
    """Генерация строки со значениями количество квартир, когда
    получили данные с общим количеством квартир

    Args:
        pd_count (int): Значение с которым сравниваем
        count_flats (int): Сравниваемое значение
        ch_count_flats (int): Изменение
        type_only_today (str, optional): Тип данных сравниваемого значения.
        Defaults to "".

    Returns:
        str: Сгенерированная строка для вывода в чат-боте
    """
    fr_ch_count_flats = fraction_design_str(ch_count_flats)
    output_str = ""
    desc_str = "Number: "

    if type_only_today:
        # output_str = f"Количество: {fr_ch_count_flats} кв. ({count_flats} кв. "\
        # " {__type_only_today} | {pd_count} кв. старых)"
        output_str = f"{desc_str}{count_flats} fl. {type_only_today} ({pd_count} old fl.)"
    else:
        output_str = f"{desc_str}{fr_ch_count_flats} fl. ({pd_count} -> " \
                     f"{count_flats} fl.)"
    return output_str


def datetime_to_str(datetime_val: date) -> str:
    """Преобразование даты в единый вид вывода

    Args:
        datetime_val (date): Дата

    Returns:
        str: Текстовый вид даты
    """
    # return datetime_val.strftime("%d.%m.%Y")
    return str(datetime_val)


def normalize_number(number: Union[float, int]) -> str:
    """Нормализация десятичного числа

    Args:
        number (float, int): Число

    Returns:
        str: Преобразованное число
    """

    # norm_number = int(number) if 'E' in str(number.normalize()) else number.normalize()
    return str(number)
