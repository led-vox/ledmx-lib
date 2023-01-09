import numpy as np
import yaml
from dataclasses import dataclass
from ledmx.utils import parse_ranges

PIXELS_PER_UNI = 170
UNI_PER_OUT = 4
PIXELS_PER_OUT = UNI_PER_OUT * PIXELS_PER_UNI
BYTES_PER_PIXEL = 3


@dataclass(frozen=True, unsafe_hash=True)
class UniverseAddr:
    ip: str
    net: int
    subnet: int
    universe: int


@dataclass(frozen=True)
class LayoutConf:
    nodes: list[dict]


class Matrix:
    def __init__(self, layout_yaml: str):
        self.__universes: dict[UniverseAddr, np.ndarray] = {}
        self.__pixels_map: dict[int, np.ndarray] = {}

        layout = LayoutConf(**yaml.safe_load(layout_yaml))

        for node in layout.nodes:
            ip, net, subnet = node['addr']
            assert node['outs'] is not None

            for out_num, ranges in node['outs'].items():
                assert ranges is not None

                u_idx = out_num * UNI_PER_OUT
                offset = 0
                for idx, pix_id in enumerate(parse_ranges(ranges)):
                    if idx % PIXELS_PER_UNI == 0:
                        u_idx += 1
                        offset = 0

                    u_addr = UniverseAddr(ip, net, subnet, u_idx)
                    if u_addr not in self.__universes:
                        self.__universes[u_addr] = np.zeros((PIXELS_PER_UNI, BYTES_PER_PIXEL), 'b')
                    self.__pixels_map[pix_id] = self.__universes[u_addr][offset]
                    offset += 1

    def __len__(self) -> int:
        return len(self.__pixels_map.keys())

    def __iter__(self):
        return iter(self.__pixels_map.keys())

    def __getitem__(self, key: int) -> [int, int, int]:
        return self.__pixels_map[key]

    def __setitem__(self, key: int, value: [int, int, int]):
        if key not in self.__pixels_map:
            raise KeyError(key)
        self.__pixels_map[key][0:3] = value

    def off(self):
        for uni_bytes in self.__universes.values():
            uni_bytes.fill(0)

    def get_packets(self) -> [UniverseAddr, bytes]:
        return iter(self.__universes.items())
