"""Модуль для подключения к БД Postgres для выполнения запросов
"""
import sys
import logging
from typing import List
import pandas as pd
from pandas import DataFrame
from sqlalchemy import create_engine
import psycopg2


class DBWrapper():
    """Класс коннектор для выполнения запросов к БД Postgres
    """

    def __init__(self, db_config):
        logging.debug('Инициализация')
        # Получение конфигурационных параметров для подключения к БД
        self.__db_config = db_config
        # Конструирование engine sqlalchemy строки подключения
        engine_string = f"postgresql+psycopg2://{self.__db_config['user']}:{self.__db_config['password']}@" \
                        f"{self.__db_config['host']}:{self.__db_config['port']}/{self.__db_config['database']}"

        # Проверяем подключение к БД
        self.__test_connection()
        # Создание sqlalchemy engine
        self.__engine = create_engine(engine_string)

        logging.info('Инициализация выполнена')

    def execute_select_pd(self, str_query: str) -> DataFrame:
        """Метод для выполнения SELECT SQL-запроса
        и получения pandas DataFrame из таблицы результата запроса

        Args:
            str_query (str): SELECT SQL-запрос на выполнение

        Returns:
            DataFrame: pandas DataFrame из таблицы результата запроса
        """
        return pd.read_sql_query(str_query, con=self.__engine, parse_dates={'price_actual_date': '%Y-%m-%d'})

    def execute_select(self, str_query: str) -> List[dict]:
        """Выполнение SELECT SQL-запроса к БД

        Args:
            str_query (str): SELECT SQL-запрос

        Returns:
            List[dict]: Результат выполнения SELECT SQL-запроса
        """
        connection = None
        output_data = []
        try:
            connection = psycopg2.connect(**self.__db_config)
            cursor = connection.cursor()
            cursor.execute(str_query)
            colnames = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            output_data = [dict(zip(colnames, row)) for row in rows]
        except Exception as e:
            logging.error('Executing SQL query has been failed', exc_info=sys.exc_info())
            raise Exception(e)
        finally:
            # Закрываем подключение к БД
            if connection is not None:
                connection.close()
                logging.debug('PostgreSQL подключение закрыто')
        return output_data

    def __test_connection(self) -> None:
        """Тестирование подключения к БД
        """
        connection = None
        try:
            connection = psycopg2.connect(**self.__db_config)

            cursor = connection.cursor()
            # Выводим PostgreSQL Connection properties
            logging.debug(f'{connection.get_dsn_parameters()}')

            # Выводим версию PostgreSQL
            cursor.execute('SELECT version();')
            record = cursor.fetchone()
            logging.info(f'Подключено к {record}')
        except Exception as e:
            logging.error('Testing connection to DB has been failed', exc_info=sys.exc_info())
            raise Exception(e)
        finally:
            # Закрываем подключение к БД
            if connection is not None:
                connection.close()
                logging.debug('PostgreSQL подключение закрыто')
