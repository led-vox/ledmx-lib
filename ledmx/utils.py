"""
Утилитарные функции
"""
import numpy as np
from numpy.random import randint


def parse_ranges(ranges: [str | int]) -> [int]:
    """
    конвертер строки с диапазонами пикселей в список номеров пикселей
    901, 1001-1010 -> generator<[901, 1001, 1002, 1003, 1004 ... 1010]>

    :param ranges: строка с диапазонами пикселей или одиночный номер пикселя
    :return: генератор глобальных номеров пикселей
    """

    # если диапазон пуст - возвращаем пустой список
    if not ranges:
        return []

    # если диапазон - одиночный номер пикселя, возвращаем список с
    # единственным элементом - номером пикселя
    if isinstance(ranges, int):
        return [ranges]

    # цикл по подстрокам (разделенным запятой)
    for pcs in ranges.split(','):

        # разделение символом "-"
        b_e = pcs.split('-')

        try:
            # начало диапазона
            b_int = int(b_e[0])

            # конец диапазона, если диапазон состоит больше, чем из одного номера
            e_int = int(b_e[1]) if len(b_e) > 1 else b_int + 1

            # сортировка начала и конца диапазона по возрастанию
            if b_int > e_int:
                b_int, e_int = e_int, b_int

            # генерация списка и поэлементная его выдача
            for el in range(b_int, e_int):
                yield el

        # в случае ошибки - пропустить шаг
        except ValueError:
            continue


def get_children_range(parent_idx: int, parent_size: int) -> (int, int):
    """
    возвращает индексы первого и последнего элементов списка по
    заданному номеру и размеру списка
    :param parent_idx: номер списка
    :param parent_size: размер списка
    :return: первый и последний индексы
    """
    _first = parent_idx * parent_size
    _last = _first + parent_size
    return _first, _last


def get_uni_addr(uni_idx: int) -> (int, int, int):
    """
    вычисление адреса вселенной по её номеру
    :param uni_idx: индекс вселенной
    :return: номер сети, номер подсети, номер вселенной в подсети
    """
    assert 0 <= uni_idx < 32768
    subnet, local_uni_idx = divmod(uni_idx, 16)
    net, local_subnet = divmod(subnet, 16)
    return net, local_subnet, local_uni_idx


def random_color() -> np.ndarray:
    """
    генератор случайных значений пикселей
    """
    return randint(0, 255, 3, 'uint8')
