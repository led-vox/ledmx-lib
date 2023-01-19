"""
Описание класса Мультивселенной
"""

from ledmx.layout import build_matrix, map_pixels, validate_yaml
from ledmx.model import Universe, PixInfo
from ledmx.transport import send
from ledmx.artnet.packet import art_dmx


class Multiverse:
    """
    Мультивселенная - матрица данных + карта пикселей и ссылок а данные
    """

    def __init__(self, layout: dict):
        """
        Конструктор
        :param layout: словарь - конфиг со списком узлов
        """

        # валидация конфига
        validate_yaml(layout)

        # матрица вселенных (список)
        self.__matrix: list[Universe] = []

        # для каждого узла формируем матрицу и дополняем её глобальную матрицу
        for uni in [build_matrix(node) for node in layout['nodes']]:
            self.__matrix.extend(uni)

        # карта пикселей (словарь номер_пикселя : указатель_на_данные)
        self.__pixel_map: dict[int, PixInfo] = {}

        #  для каждого узла формируем карту и дополняем её глобальную карту пикселей
        for pix in [map_pixels(node, self.__matrix) for node in layout['nodes']]:
            self.__pixel_map.update(dict(pix))

        # словарь порядковых номеров пакетов для каждого узла
        self._seq_map: dict[str, int] = {host: 1 for host in [u.addr.host for u in self.__matrix]}

        # назначение функции отпарвки данных (для мокинга в тестах)
        self._send = send

    def __len__(self) -> int:
        """ длина мультивселенной == количество номеров пикселей в карте """
        return len(self.__pixel_map.keys())

    def __iter__(self):
        """ итератор по элементам == итератор по номерам пикселей в карте """
        return iter(self.__pixel_map.keys())

    def __getitem__(self, key: int) -> [int, int, int]:
        """ получение значение элемента == указатель на данные пикселя по его номеру """
        return self.__pixel_map[key].data

    def __setitem__(self, key: int, value: [int, int, int]):
        """ установка значения для элемента == заполнение данных пикселя по указателю """
        if key not in self.__pixel_map:
            raise KeyError(key)
        self.__pixel_map[key].data[0:3] = value

    def __bytes__(self) -> bytes:
        """ конвертирование в байты == объединение данных всех вселенных матрицы """
        b_arr = bytearray()
        for u in self.__matrix:
            b_arr.extend(u.data)
        return bytes(b_arr)

    def pub(self):
        """
        Отправка данных матрицы в сеть
        """

        # из каждой вселенной матрицы, формируется ArtDMX пакет,
        # порядковый номер пакета высчитывается для каждого узла отдельно,
        # сформированный пакет отправляется в сеть
        for uni in self.__matrix:
            packet = art_dmx(
                bytes(uni.data),
                uni.addr.net,
                uni.addr.subnet,
                uni.addr.uni_idx)
            self._seq_map[uni.addr.host] = 1 \
                if self._seq_map[uni.addr.host] > 255 \
                else self._seq_map[uni.addr.host] + 1
            self._send(packet, uni.addr.host)

    def off(self):
        """
        Обнуление (заполнение нулями) всех байт матрицы
        """
        for uni in self.__matrix:
            uni.data.fill(0)
