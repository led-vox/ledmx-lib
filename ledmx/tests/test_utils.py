from ledmx.utils import parse_ranges, get_children_range
import pytest


@pytest.mark.parametrize('args, result', [
    ('', []),
    ('-', []),
    ('123', [123]),
    ('123-124', [123]),
    ('123,32-45', [
        123, 32, 33, 34, 35, 36, 37, 38, 39,
        40, 41, 42, 43, 44
    ]),
    ('123-124,32-45', [
        123, 32, 33, 34, 35, 36, 37, 38, 39,
        40, 41, 42, 43, 44
    ]),
    ('123-101,', [
        101, 102, 103, 104, 105, 106, 107, 108,
        109, 110, 111, 112, 113, 114, 115, 116,
        117, 118, 119, 120, 121, 122
    ]),
    ('123-101,4- 10, 321', [
        101, 102, 103, 104, 105, 106, 107, 108,
        109, 110, 111, 112, 113, 114, 115, 116,
        117, 118, 119, 120, 121, 122,
        4, 5, 6, 7, 8, 9, 321
    ]),
])
def test_parse_ranges(args, result):
    assert [r for r in parse_ranges(args)] == result


@pytest.mark.parametrize('args, result', [
    ((0, 0), (0, 0)),
    ((0, 10), (0, 10)),
    ((0, 40), (0, 40)),
    ((2, 40), (80, 120)),
    ((45, 650), (29250, 29900)),
])
def test_get_children_range(args, result):
    assert get_children_range(*args) == result
