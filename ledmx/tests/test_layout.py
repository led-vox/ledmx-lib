"""
Тесты функций для работы с конфигурацией
"""

from ledmx.layout import build_matrix, map_pixels, validate_yaml
from ledmx.layout import UNI_PER_OUT, UNI_PER_SUBNET
from ledmx.model import UniAddr

import pytest


@pytest.mark.parametrize('node, u_addr_list', [
    ({'host': '1.1.1.1', 'name': 'test', 'outs': {0: '0-10'}},
     [UniAddr('test', '1.1.1.1', 0, 0, 0, u) for u in range(UNI_PER_OUT)]),
    ({'host': '1.1.1.1', 'name': 'test', 'outs': {0: '0-10, 210-220', 3: '100-130'}},
     [UniAddr('test', '1.1.1.1', 0, 0, u // UNI_PER_OUT, u) for u in range(UNI_PER_SUBNET)]),
    ({'host': '1.1.1.1', 'name': 'test', 'outs': {0: '0-10, 210-220', 3: '100-130', 5: '1001-1004'}},
     [UniAddr('test', '1.1.1.1', 0, 0, u // UNI_PER_OUT, u) for u in range(UNI_PER_SUBNET)] +
     [UniAddr('test', '1.1.1.1', 0, 1, 4, u) for u in range(0, 4)] +
     [UniAddr('test', '1.1.1.1', 0, 1, 5, u) for u in range(4, 8)]),
    ({'host': '1.1.1.1', 'name': 'test', 'outs': {3: '100-130', 69: '30000-30100'}},
     [UniAddr('test', '1.1.1.1',
              _u // 256,  # net
              _u // 16 - (_u // 256) * 16,  # subnet
              _u // UNI_PER_OUT,  # output
              _u % UNI_PER_SUBNET)  # universe
      for _u in range(68 * UNI_PER_OUT)] +
     [UniAddr('test', '1.1.1.1', 1, 1, 68 + u // UNI_PER_OUT, u) for u in range(8)])
])
def test_build_matrix(node: dict, u_addr_list: list[UniAddr]):
    """
    тест на корректность формирования матрицы по конфигу узла
    на входе - конфиг узла
    ОР: матрица - список вселенных
    """
    got = list(u.addr for u in build_matrix(node))
    assert got == u_addr_list


def test_build_matrix_assertion():
    """
    тест на выброс исключения при передаче некорректного конфига узла при сборке матрицы
    """
    with pytest.raises(AssertionError):
        list(build_matrix({'outs': {}}))


def test_map_pixels_assertion():
    """
    тест на выброс исключения при передаче некорректного конфига узла при построении карты
    """
    with pytest.raises(AssertionError):
        dict(map_pixels({'outs': {}}, []))


def test_map_pixels():
    """
    тест на корректность построения карты пикселей
    на входе - конфиг узла и матрица
    ОР: корректная длина карты
    ОР: соответствие значений смещений пикселей и указателей на вселенные
    ОР: соответствие данных по указателю пикселя и данных в матрице
    """
    node = {'host': '1.1.1.1', 'name': 'test', 'outs': {0: '0-10, 210-220', 3: '100-130', 5: '1001-1004'}}
    matrix = list(build_matrix(node))
    p_map = dict(map_pixels(node, matrix))
    assert len(p_map.items()) == 53
    assert p_map[120].offset == 20 and p_map[120].uni == matrix[12]
    assert (p_map[1002].data == matrix[20].data[1]).all()


@pytest.mark.parametrize('conf', [
    # empty
    {},

    # empty nodes
    {'nodes'},
    {'nodes': []},
    {'nodes': [{}]},
    {'nodes': [{}, {}]},

    # not enough attributes
    {'nodes': [{'name'},
               {'host'}]},
    {'nodes': [{'name': 'test0'},
               {'host': '1.1.1.1'}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1'},
               {'host': '1.1.1.2'}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1'},
               {'name': 'node-1', 'host': '1.1.1.2'}]},

    # empty outputs | wrong outputs type
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': []},
               {'name': 'node-1', 'host': '1.1.1.2'}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': []},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {}}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {'3'}},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {'d'}}]},

    # wrong output's keys or values types
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {'3': 999}},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {'3': 'd-d'}}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {0: 999}},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {'3': 'd-d'}}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {0: '999'}},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {'3': 'd-d'}}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {0: '999'}},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {'3': '0-15'}}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {0: '999-5001'}},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {'3': '0-15'}}]},

    # too big values
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {0: '100500-200300'}},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {3: '0-15', 100500: '3333'}}]},

    # too small values
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {0: '-100500-200300'}},
               {'name': 'node-1', 'host': '1.1.1.2', 'outs': {-3: '0-15', 100500: '3333'}}]},
])
def test_validate_yaml_bad(conf: dict):
    """
    тест валидации конфига некорректными данными
    на входе - некорректный текст конфига
    ОР: выброс исключения
    """
    with pytest.raises(Exception):
        validate_yaml(conf)


@pytest.mark.parametrize('conf', [
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.1', 'outs': {0: '999'}}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.2', 'outs': {0: '999', 3: '85'}}]},
    {'nodes': [{'name': 'node-0', 'host': '1.1.1.2', 'outs': {0: '8-45, 65', 3: '85'}}]},
    {'nodes': [
        {'name': 'node-0', 'host': '1.1.1.2', 'outs': {0: '8-45, 65', 3: '85'}},
        {'name': 'node-1', 'host': '1.1.1.3', 'outs': {2: '8-45, 65', 8: '85-96, 104'}},
    ]},
])
def test_validate_yaml_good(conf: dict):
    """
    тест валидации конфига корректными данными
    на входе - корректный текст конфига
    ОР: True как признак валидности переданных данных
    """
    assert validate_yaml(conf)
