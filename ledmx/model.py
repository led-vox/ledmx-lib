from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True, unsafe_hash=True)
class UniAddr:
    node: str
    host: str
    net: int
    subnet: int
    out_idx: int
    uni_idx: int

    def __repr__(self) -> str:
        return f'{self.node}[{self.host}]n:{self.net}|s:{self.subnet}|o:{self.out_idx}|u:{self.uni_idx}'


@dataclass
class Universe:
    addr: UniAddr
    data: np.ndarray


@dataclass(frozen=True)
class PixInfo:
    data: np.ndarray
    uni: Universe
    offset: int
