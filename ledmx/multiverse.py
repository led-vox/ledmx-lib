import numpy as np
from dataclasses import dataclass
from ledmx.utils import parse_ranges
from ledmx.transport import send
from ledmx.artnet.packet import art_dmx

PIXELS_PER_UNI = 170
UNI_PER_OUT = 4
PIXELS_PER_OUT = UNI_PER_OUT * PIXELS_PER_UNI
BYTES_PER_PIXEL = 3


@dataclass(frozen=True, unsafe_hash=True)
class UniAddr:
    label: str
    ip: str
    net: int
    subnet: int
    out_idx: int
    uni_idx: int

    def __repr__(self) -> str:
        return f'{self.label}:{self.ip}:{self.net}:{self.subnet}:{self.out_idx}:{self.uni_idx}'


@dataclass
class Universe:
    addr: UniAddr
    data: np.ndarray


@dataclass(frozen=True)
class PixInfo:
    data: np.ndarray
    uni: Universe
    offset: int


class Multiverse:
    def __init__(self, layout: dict):
        self.__matrix: list[Universe] = []
        self.__map: dict[int, PixInfo] = {}

        for node in layout['nodes']:
            # go through all the outputs, including empty
            outs_amount = max(node['outs'].keys()) + 1
            for out_idx in range(outs_amount):
                uni_idx_first = out_idx * UNI_PER_OUT
                uni_idx_last = uni_idx_first + UNI_PER_OUT
                for uni_idx in range(uni_idx_first, uni_idx_last):
                    self.__matrix.append(Universe(
                        UniAddr(label=node['label'], **node['addr'], out_idx=out_idx, uni_idx=uni_idx),
                        np.zeros((PIXELS_PER_UNI, BYTES_PER_PIXEL), 'b')
                    ))

                if out_idx not in node['outs']:
                    continue    # next output index

                pix_ranges = node['outs'][out_idx]
                if not pix_ranges:
                    continue    # next output index

                uni_idx, offset = uni_idx_first, 0
                for pix_id in parse_ranges(pix_ranges):
                    self.__map[pix_id] = PixInfo(
                        self.__matrix[uni_idx].data[offset],
                        self.__matrix[uni_idx],
                        offset
                    )

                    offset += 1
                    if offset >= PIXELS_PER_UNI:
                        uni_idx, offset = uni_idx + 1, 0

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
