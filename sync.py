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

    send(art_sync(), '10.0.0.255')

    for color in [RED, BLUE, GREEN]:
        m_verse[0] = color
        m_verse.pub()

        time.sleep(1/5)

    send(art_sync(), '10.0.0.255')
