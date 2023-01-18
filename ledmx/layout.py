from pathlib import Path

from schema import Schema, And, Or
import yaml
from ledmx.model import UniAddr, Universe, PixInfo
from ledmx.utils import get_uni_addr, get_children_range, parse_ranges
import numpy as np

PIXELS_PER_UNI = 170
BYTES_PER_PIXEL = 3
UNI_PER_OUT = 4
UNI_PER_SUBNET = 16
SUBNET_PER_NET = 16
NETS_MAX = 127
OUTS_MAX = (NETS_MAX * SUBNET_PER_NET * UNI_PER_SUBNET) // UNI_PER_OUT


def validate_yaml(yaml_dict: dict) -> bool:
    not_empty_str = Schema(And(str, lambda n: len(n) > 0))
    not_null_int = Schema(And(int, lambda n: n > 0))
    not_empty_list = Schema(And(list, lambda n: len(n) > 0))
    return Schema(
        {
            'nodes': And([
                {
                    'name': not_empty_str,
                    'host': not_empty_str,
                    'outs': {
                        And(int, lambda n: 0 <= n <= OUTS_MAX): Or(not_empty_str, not_null_int)
                    }
                }
            ], not_empty_list)
        }
    ).validate(yaml_dict)


def parse_file(filename: str) -> dict:
    return yaml.safe_load(Path(filename).read_text())


def build_matrix(node: dict) -> list[Universe]:
    assert len(node['outs']) > 0
    outs_amount = max(node['outs'].keys()) + 1
    for out_idx in range(outs_amount):
        for uni_idx in range(*get_children_range(out_idx, UNI_PER_OUT)):
            net, subnet, local_uni_idx = get_uni_addr(uni_idx)
            yield Universe(
                UniAddr(
                    node=node['name'],
                    host=node['host'],
                    net=net,
                    subnet=subnet,
                    out_idx=out_idx,
                    uni_idx=local_uni_idx),
                np.zeros((PIXELS_PER_UNI, BYTES_PER_PIXEL), 'b')
            )


def map_pixels(node: dict, matrix: list[Universe]) -> dict[int, PixInfo]:
    assert len(node['outs']) > 0
    for out_idx, out_val in node['outs'].items():
        u_first_idx, _ = get_children_range(out_idx, UNI_PER_OUT)
        uni_idx, offset = u_first_idx, 0
        for pix_id in parse_ranges(out_val):
            yield pix_id, PixInfo(matrix[uni_idx].data[offset], matrix[uni_idx], offset)
            offset += 1
            if offset >= PIXELS_PER_UNI:
                uni_idx, offset = uni_idx + 1, 0
