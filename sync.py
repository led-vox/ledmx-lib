"""
Проверка поддержки устройством механизма синхронизации
"""

import time

from ledmx.multiverse import Multiverse
from ledmx.layout import parse_file
from ledmx.transport import send
from ledmx.artnet.packet import art_sync

BLUE = 0, 0, 100
RED = 0, 100, 0
GREEN = 100, 0, 0

if __name__ == '__main__':
    layout = parse_file('layout.yaml')
    m_verse = Multiverse(layout)

    # отправляем первый синхр. пакет (вкл. синхр. режим)
    send(art_sync(), '10.0.0.255')

    # по очереди включаем на первом диоде цвета
    for color in [RED, BLUE, GREEN]:
        m_verse[0] = color
        m_verse.pub()

        time.sleep(1/5)

    # отправляем синхр. пакет
    send(art_sync(), '10.0.0.255')

    # на ленте должен отобразиться только последний цвет (зелёный)
    # если "проморгали" все, значит устройство отправило все пакеты сразу на выход
    # не дожидаясь синхр. пакета
