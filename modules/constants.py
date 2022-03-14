"""Модуль содержащий константы
"""
from enum import Enum, auto

from typing_extensions import Literal


class RenderConsts(Enum):
    """Константы для модуля data_render.py

    Args:
        Enum (class): Стандартный класс библиотеки python
    """
    # Типы генерации данных статистики
    TYPE_SUMMARY_STAT = auto()
    TYPE_NEW_STAT = auto()
    TYPE_OLD_STAT = auto()
    TYPE_SELL_STAT = auto()
    ALLOWED_TYPES_STATS = Literal[TYPE_SUMMARY_STAT, TYPE_NEW_STAT, TYPE_OLD_STAT, TYPE_SELL_STAT]
