"""
Тесты генерации Art-Net пакетов
"""

from ledmx.artnet.packet import art_dmx, art_sync
import pytest


@pytest.mark.parametrize('args, result', [
    ({'net': 0, 'subnet': 0, 'universe': 0, 'seq': 0, 'data': b'\x11\x12\x21\x34'},
     b'Art-Net\x00\x00\x50\x00\x0E' +
     b'\x00' +  # seq
     b'\x00' +  # phys
     b'\x00' +  # sub_uni
     b'\x00' +  # net
     b'\x00\x04' +  # len
     b'\x11\x12\x21\x34'),  # data

    ({'net': 125, 'subnet': 11, 'universe': 14, 'seq': 210, 'data': b'\x11' * 410},
     b'Art-Net\x00\x00\x50\x00\x0E' +
     b'\xD2' +  # seq
     b'\x00' +  # phys
     b'\xBE' +  # sub_uni
     b'\x7d' +  # net
     b'\x01\x9A' +  # len
     b'\x11' * 410),  # data

])
def test_art_dmx(args, result):
    """
    тест на корректность формирования пакета
    на вход - параметры для формирования пакета
    ОР: байты пакета с правильными значениями
    """
    assert art_dmx(**args) == result


def test_art_sync():
    """
    тест на корректность формирования пакета
    ОР: байты пакета с правильными значениями
    """
    assert art_sync() == b'Art-Net\x00\x00\x52\x00\x0E\x00\x00'
