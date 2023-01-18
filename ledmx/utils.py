# 901, 1001-1010 -> generator<[901, 1001, 1002, 1003, 1004 ... 1010]>
def parse_ranges(ranges: [str | int]) -> [int]:
    if not ranges:
        return []
    if isinstance(ranges, int):
        return [ranges]
    for pcs in ranges.split(','):
        b_e = pcs.split('-')
        try:
            b_int = int(b_e[0])
            e_int = int(b_e[1]) if len(b_e) > 1 else b_int + 1
            if b_int > e_int:
                b_int, e_int = e_int, b_int
            for el in range(b_int, e_int):
                yield el
        except ValueError:
            continue


# return first and last global index of children by parent index and size
def get_children_range(parent_idx: int, parent_size: int) -> (int, int):
    _first = parent_idx * parent_size
    _last = _first + parent_size
    return _first, _last


def get_uni_addr(uni_idx: int) -> (int, int, int):
    assert 0 <= uni_idx < 32768
    subnet, local_uni_idx = divmod(uni_idx, 16)
    net, local_subnet = divmod(subnet, 16)
    return net, local_subnet, local_uni_idx
