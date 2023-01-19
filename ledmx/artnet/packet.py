"""
Генераторы разных типов Art-Net пакетов
"""

from struct import pack

# преамбула заголовка пакета
_H = b'Art-Net\x00'

# номер версии протокола
_H_VER = b'\x00\x0E'

# https://art-net.org.uk/how-it-works/streaming-packets/artdmx-packet-definition/


def art_sync() -> bytes:
    """
    Генератор ArtSync пакета.
    Пакет отправляется на широковещательный адрес сети для включения синхронного режима на нодах,
    либо для синхронной отправки буферизированного кадра на выходы.
    """

    # сборка пакета
    return _H + b'\x00\x52' + _H_VER + b'\0\0'


def art_dmx(data: bytes, net: int = 0, subnet: int = 0, universe: int = 0, seq: int = 0) -> bytes:
    """
    Генератор ArtDMX пакета.
    Пакет отправляется содержит заголовок с адресом вселенной, подсети, сети и порядковый номер.

    :param data:bytes: значения DMX каналов (байты уровней каждого цвета)
    :param net:int=0: номер сети (0 - 127)
    :param subnet:int=0: номер подсети (16 подсетей в каждой сети)
    :param universe:int=0: номер вселенной (16 вселенных в каждой подсети)
    :param seq:int=0: порядковый номер пакета (0 для отключения учёта порядка)
    """

    # номер пакета - от 0 до 256
    assert 0 <= seq <= 255

    # номер сети - от 0 до 128
    assert 0 <= net < 128

    # номер подсети - от 0 до 16
    assert 0 <= subnet < 16

    # номер вселенной - от 0 до 16
    assert 0 <= universe < 16

    # длина всех данных в байтах
    length = len(data)

    # длина всех данных в байтах
    assert 2 <= length <= 512

    # количество байт данных должно быть чётным
    assert length % 2 == 0

    # сборка пакета
    return _H + b'\x00\x50' + _H_VER + pack('BxBB', seq, subnet << 4 | universe, net) + pack('!H', length) + data
