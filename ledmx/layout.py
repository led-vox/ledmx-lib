"""
Работа с конфигурационным файлом и генерация атрибутов вселенной
"""

from pathlib import Path

from schema import Schema, And, Or
import yaml
from ledmx.model import UniAddr, Universe, PixInfo
from ledmx.utils import get_uni_addr, get_children_range, parse_ranges
import numpy as np

PIXELS_PER_UNI = 170    # пикселей во вселенной
BYTES_PER_PIXEL = 3     # байт в пикселе
UNI_PER_OUT = 4         # вселенных на выход
UNI_PER_SUBNET = 16     # вселенных в подсети
SUBNET_PER_NET = 16     # подсетей в сети
NETS_MAX = 127          # максимальное число сетей

# теоретическое максимальное число выходов
OUTS_MAX = (NETS_MAX * SUBNET_PER_NET * UNI_PER_SUBNET) // UNI_PER_OUT


def validate_yaml(yaml_dict: dict) -> bool:
    """
    Валидация конфига
    :param yaml_dict: словарь - конфиг
    :return: является ли конфиг валидным
    """

    # проверка, что строка не пустая
    not_empty_str = Schema(And(str, lambda n: len(n) > 0))

    # проверка, что значение больше нуля
    not_null_int = Schema(And(int, lambda n: n >= 0))

    # проверка, что список не пуст
    not_empty_list = Schema(And(list, lambda n: len(n) > 0))

    # валидация конфига по предоставленной схеме
    return Schema(
        {
            # список узлов не может быть пустым
            'nodes': And([
                {
                    # имя узла не может быть пустым
                    'name': not_empty_str,

                    # адрес узла не может быть пустым
                    'host': not_empty_str,

                    # словарь выходов
                    'outs': {

                        # индекс выхода должен быть между нулём и максимумом
                        # строка диапазонов пикселей не может быть пустой,
                        # либо это - неотрицательное число
                        And(int, lambda n: 0 <= n <= OUTS_MAX): Or(not_empty_str, not_null_int)
                    }
                }
            ], not_empty_list)
        }
    ).validate(yaml_dict)


def parse_file(filename: str) -> dict:
    """
    Чтение и парсинг конфиг файла как yaml
    :param filename: путь к файлу
    :return: конфиг в виде словаря
    """
    return yaml.safe_load(Path(filename).read_text())


def build_matrix(node: dict) -> list[Universe]:
    """
    Формирование матрицы для узла
    :param node: описание узла
    :return: список вселенных для указанного узла
    """

    # список выходов узла не должен быть пустым
    assert len(node['outs']) > 0

    # число выходов узла (последний индекс из конфига + 1)
    outs_amount = max(node['outs'].keys()) + 1

    # проходим по всем выходам
    for out_idx in range(outs_amount):

        # проходим по всем вселенным для текущего выхода
        for uni_idx in range(*get_children_range(out_idx, UNI_PER_OUT)):

            # вычисление сети, подсети и индекса вселенной по её индексу для выхода
            net, subnet, local_uni_idx = get_uni_addr(uni_idx)

            # формируем и выдаём вселенную
            yield Universe(
                UniAddr(
                    node=node['name'],
                    host=node['host'],
                    net=net,
                    subnet=subnet,
                    out_idx=out_idx,
                    uni_idx=local_uni_idx),
                np.zeros((PIXELS_PER_UNI, BYTES_PER_PIXEL), 'uint8')
            )


def map_pixels(node: dict, matrix: list[Universe]) -> dict[int, PixInfo]:
    """
    Формирование карты матрицы для узла
    :param node: описание узла
    :param matrix: указатель на матрицу
    :return: словарь {номер_пикселя:данные_в_матрице}
    """

    # список выходов узла не должен быть пустым
    assert len(node['outs']) > 0

    # проходим по всем выходам (индекс выхода : строка диапазонов пикселей)
    for out_idx, out_val in node['outs'].items():

        # получаем индекс первой вселенной в текущем выходе
        u_first_idx, _ = get_children_range(out_idx, UNI_PER_OUT)

        # проходим по всем номерам пикселей из диапазона
        uni_idx, offset = u_first_idx, 0
        for pix_id in parse_ranges(out_val):

            # формируем ссылки на данные в матрице, на матрицу и значение смещения
            # выдаём на выход генератора
            yield pix_id, PixInfo(matrix[uni_idx].data[offset], matrix[uni_idx], offset)

            # инкремент смещения (к следующему пикселю)
            offset += 1

            # инкремент индекса вселенной и обнуление смещения,
            # если смещение превышает размер вселенной
            if offset >= PIXELS_PER_UNI:
                uni_idx, offset = uni_idx + 1, 0
