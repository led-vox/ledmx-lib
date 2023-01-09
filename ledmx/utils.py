# 901, 1001-1010 -> generator<[901, 1001, 1002, 1003, 1004 ... 1010]>
def parse_ranges(ranges: [str | int]) -> [int]:
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
