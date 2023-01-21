"""
Тесты класса Мультивселенной
"""
import numpy as np

from ledmx.layout import BYTES_PER_PIXEL, PIXELS_PER_UNI
from ledmx.multiverse import Multiverse
from ledmx.utils import random_color

import pytest
from mock.mock import patch


# создание тестируемого экземпляра
@pytest.fixture
def mvs() -> Multiverse:
    return Multiverse({
        'nodes': [
            {'host': '1.1.1.1', 'name': 'test0', 'outs': {0: '3-10, 210-220', 3: '100-130', 5: '1001-1004'}},
            {'host': '1.1.1.3', 'name': 'test1', 'outs': {2: '666, 696-708'}},
            {'host': '1.1.1.7', 'name': 'test2', 'outs': {6: '901-904, 990, 995-999'}},
        ]
    })


COLOR_BLACK = 0, 0, 0
COLOR_0 = random_color()
COLOR_1 = random_color()
COLOR_2 = random_color()
COLOR_3 = random_color()
COLOR_4 = random_color()
COLOR_5 = random_color()
COLOR_6 = random_color()
COLOR_7 = random_color()
COLOR_8 = random_color()
COLOR_9 = random_color()


def arr_eq(arr0, arr1):
    assert (np.array(arr0) == np.array(arr1)).all()


def test_multiverse_len(mvs):
    """
    тест длины мультивселенной
    ОР: числа перечисленных в диапазонах пикселей
    """
    #  total pixels amount: 10-3 + 220-210 + 130-100 + 1004-1001 + 1 + 708-696 + 904-901 + 1 + 999-995
    assert len(mvs) == 71


def test_multiverse_iter(mvs):
    """
    тест итератора
    ОР: генерируемый итератором список == список пикселей в карте
    """
    pixels_list = []
    for pair in [
        (3, 10), (210, 220), (100, 130), (1001, 1004),
        (666, 667), (696, 708),
        (901, 904), (990, 991), (995, 999),
    ]:
        pixels_list.extend(list(range(*pair)))
    assert sorted(list(p for p in mvs)) == sorted(pixels_list)


def test_multiverse_bytes(mvs):
    """
    тест преобразования в байты
    ОР: полученные байты идентичны ожидаемым
    """
    assert bytes(mvs) == b'\0' * 64 * PIXELS_PER_UNI * BYTES_PER_PIXEL


def test_multiverse_first_last(mvs):
    assert mvs.first() == 3
    assert mvs.last() == 1003


def test_multiverse_get_set():
    """
    тест установки значений и получения значений данных
    ОР: данные в матрице соответствуют заданным при обращении через индекс
    """
    m = Multiverse({'nodes': [{'name': 'test', 'host': '10.0.0.11', 'outs': {
        0: '4-7, 35', 2: '12-14'
    }}]})
    # {4:, 5:, 6:, 12:, 13:, 35:}

    # установка по несуществующему индексу не выбрасывает исключения
    m.off()
    m[10] = COLOR_0
    assert m[10] is None

    m.off()
    m[5] = COLOR_0
    arr_eq(m[5], COLOR_0)

    m.off()
    #       4         5        6       12       13       35
    m[:] = COLOR_0, COLOR_1, COLOR_2, COLOR_3, COLOR_4, COLOR_5
    arr_eq(m[:], (COLOR_0, COLOR_1, COLOR_2, COLOR_3, COLOR_4, COLOR_5))

    m.off()
    m[:] = COLOR_8
    arr_eq(m[:], (COLOR_8, COLOR_8, COLOR_8, COLOR_8, COLOR_8, COLOR_8))

    m.off()
    m[:6] = COLOR_0, COLOR_7
    arr_eq(m[:6], (COLOR_0, COLOR_7))
    arr_eq(m[4], COLOR_0)

    m.off()
    m[10:] = COLOR_3, COLOR_5, COLOR_1
    arr_eq(m[10:], (COLOR_3, COLOR_5, COLOR_1))
    arr_eq(m[13], COLOR_5)

    m.off()
    m[::3] = COLOR_5
    arr_eq(m[:], (COLOR_5, COLOR_BLACK, COLOR_BLACK, COLOR_5, COLOR_BLACK, COLOR_BLACK))
    arr_eq(m[::3], COLOR_5)

    m.off()
    m[5:13] = COLOR_3
    m[13:25] = COLOR_7
    arr_eq(m[:], (COLOR_BLACK, COLOR_3, COLOR_3, COLOR_3, COLOR_7, COLOR_BLACK))


def test_multiverse_off(mvs):
    """
    тест обнуления данных
    ОР: после обнуления все байты равны нулям
    """
    mvs.off()
    assert bytes(mvs) == b'\0' * 64 * PIXELS_PER_UNI * BYTES_PER_PIXEL


def test_multiverse_pub(mvs):
    """
    тест отправки данных
    ОР: данные отправляются на указанные в адресах вселенных хосты
    ОР: счётчики - порядковые номера пакетов по хостам соответствуют ожидаемым
    """
    # noinspection PyUnusedLocal
    def fake_send(data: bytes, host: str, port: int = 6454) -> None:
        assert host in ['1.1.1.1', '1.1.1.3', '1.1.1.7']

    with patch.object(mvs, '_send', fake_send):
        mvs.pub()
        assert mvs._seq_map == {'1.1.1.1': 25, '1.1.1.3': 13, '1.1.1.7': 29}
