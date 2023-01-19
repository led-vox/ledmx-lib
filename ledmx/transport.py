"""
Транспортный протокол
"""

import socket


def send(data: bytes, host: str, port: int = 6454) -> None:
    """
    Отправка UDP пакета с указанными данными, адресом и портом.
    Если адрес заканчивается на .255, то будет отправлен широковещательный пакет.
    :param data: байты данных
    :param host: адрес хоста
    :param port: UDP порт
    :return:
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sck:
        # если адрес заканчивается на .255 -> широковещательный пакет.
        if host.endswith('.255'):
            sck.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # отправка данных в сокет
        sck.sendto(data, (host, port))
