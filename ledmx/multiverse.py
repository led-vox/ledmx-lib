from ledmx.layout import build_matrix, map_pixels, validate_yaml
from ledmx.model import Universe, PixInfo
from ledmx.transport import send
from ledmx.artnet.packet import art_dmx


class Multiverse:
    def __init__(self, layout: dict):

        validate_yaml(layout)

        self.__matrix: list[Universe] = []
        for uni in [build_matrix(node) for node in layout['nodes']]:
            self.__matrix.extend(uni)

        self.__pixel_map: dict[int, PixInfo] = {}
        for pix in [map_pixels(node, self.__matrix) for node in layout['nodes']]:
            self.__pixel_map.update(dict(pix))

        self._seq_map: dict[str, int] = {host: 1 for host in [u.addr.host for u in self.__matrix]}

        self._send = send

    def __len__(self) -> int:
        return len(self.__pixel_map.keys())

    def __iter__(self):
        return iter(self.__pixel_map.keys())

    def __getitem__(self, key: int) -> [int, int, int]:
        return self.__pixel_map[key].data

    def __setitem__(self, key: int, value: [int, int, int]):
        if key not in self.__pixel_map:
            raise KeyError(key)
        self.__pixel_map[key].data[0:3] = value

    def __bytes__(self) -> bytes:
        b_arr = bytearray()
        for u in self.__matrix:
            b_arr.extend(u.data)
        return bytes(b_arr)

    def pub(self):
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
        for uni in self.__matrix:
            uni.data.fill(0)
