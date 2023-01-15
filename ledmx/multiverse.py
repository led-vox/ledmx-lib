import numpy as np
from dataclasses import dataclass
from ledmx.utils import get_children_range, parse_ranges
from ledmx.transport import send
from ledmx.artnet.packet import art_dmx

PIXELS_PER_UNI = 170
BYTES_PER_PIXEL = 3
UNI_PER_OUT = 4


@dataclass(frozen=True, unsafe_hash=True)
class UniAddr:
    node: str
    ip: str
    net: int
    subnet: int
    out_idx: int
    uni_idx: int

    def __repr__(self) -> str:
        return f'{self.node}[{self.ip}]n:{self.net}|s:{self.subnet}|o:{self.out_idx}|u:{self.uni_idx}'


@dataclass
class Universe:
    addr: UniAddr
    data: np.ndarray


@dataclass(frozen=True)
class PixInfo:
    data: np.ndarray
    uni: Universe
    offset: int


def get_uni_addr(uni_idx: int) -> (int, int, int):
    subnet, local_uni_idx = divmod(uni_idx, 16)
    net, local_subnet = divmod(subnet, 16)
    return net, local_subnet, local_uni_idx


def build_matrix(node: dict) -> list[Universe]:
    outs_amount = max(node['outs'].keys()) + 1
    for out_idx in range(outs_amount):
        for uni_idx in range(*get_children_range(out_idx, UNI_PER_OUT)):
            net, subnet, local_uni_idx = get_uni_addr(uni_idx)
            yield Universe(
                UniAddr(
                    node=node['name'],
                    ip=node['ip'],
                    net=net,
                    subnet=subnet,
                    out_idx=out_idx,
                    uni_idx=local_uni_idx),
                np.zeros((PIXELS_PER_UNI, BYTES_PER_PIXEL), 'b')
            )


def map_pixels(node: dict, matrix: list[Universe]) -> dict[int, PixInfo]:
    for out_idx, out_val in node['outs'].items():
        u_first_idx, _ = get_children_range(out_idx, UNI_PER_OUT)
        uni_idx, offset = u_first_idx, 0
        for pix_id in parse_ranges(out_val):
            yield pix_id, PixInfo(matrix[uni_idx].data[offset], matrix[uni_idx], offset)
            offset += 1
            if offset >= PIXELS_PER_UNI:
                uni_idx, offset = uni_idx + 1, 0


class Multiverse:
    def __init__(self, layout: dict):

        self.__matrix: list[Universe] = []
        for uni in [build_matrix(node) for node in layout['nodes']]:
            self.__matrix.extend(uni)

        self.__map: dict[int, PixInfo] = {}
        for pix in [map_pixels(node, self.__matrix) for node in layout['nodes']]:
            self.__map.update(dict(pix))

    def __len__(self) -> int:
        return len(self.__map.keys())

    def __iter__(self):
        return iter(self.__map.keys())

    def __getitem__(self, key: int) -> [int, int, int]:
        return self.__map[key].data

    def __setitem__(self, key: int, value: [int, int, int]):
        if key not in self.__map:
            raise KeyError(key)
        self.__map[key].data[0:3] = value

    def pub(self):
        seq = 0
        for uni in self.__matrix:
            packet = art_dmx(bytes(uni.data), uni.addr.net, uni.addr.subnet, uni.addr.uni_idx, seq)
            seq = 0 if seq > 254 else seq + 1
            send(packet, uni.addr.ip)

    def off(self):
        for uni in self.__matrix:
            uni.data.fill(0)
