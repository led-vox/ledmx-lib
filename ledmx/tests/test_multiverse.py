from ledmx.layout import BYTES_PER_PIXEL, PIXELS_PER_UNI
from ledmx.multiverse import Multiverse

import pytest
from mock.mock import patch


@pytest.fixture
def mvs() -> Multiverse:
    return Multiverse({
        'nodes': [
            {'host': '1.1.1.1', 'name': 'test0', 'outs': {0: '0-10, 210-220', 3: '100-130', 5: '1001-1004'}},
            {'host': '1.1.1.3', 'name': 'test1', 'outs': {2: '666, 696-708'}},
            {'host': '1.1.1.7', 'name': 'test2', 'outs': {6: '901-904, 990, 995-999'}},
        ]
    })


def test_multiverse_len(mvs):
    #  total pixels amount: 10-0 + 220-210 + 130-100 + 1004-1001 + 1 + 708-696 + 904-901 + 1 + 999-995
    assert len(mvs) == 74


def test_multiverse_iter(mvs):
    #  iteration through multiverse is the iteration through pixels id
    pixels_list = []
    for pair in [
        (0, 10), (210, 220), (100, 130), (1001, 1004),
        (666, 667), (696, 708),
        (901, 904), (990, 991), (995, 999),
    ]:
        pixels_list.extend(list(range(*pair)))
    assert sorted(list(p for p in mvs)) == sorted(pixels_list)


def test_multiverse_index(mvs):
    #  wrong indexing assertion
    with pytest.raises(KeyError):
        mvs[255] = [45, 98, 24]
        _ = mvs[200]


def test_multiverse_bytes(mvs):
    assert bytes(mvs) == b'\0' * 64 * PIXELS_PER_UNI * BYTES_PER_PIXEL


def test_multiverse_get_set(mvs):

    #  get/set by index
    mvs[217] = [45, 98, 24]

    m_bytes = bytes(mvs)
    assert m_bytes[:51] == b'\0' * 51 and m_bytes[51:54] == b'\x2d\x62\x18' and m_bytes[54:] == b'\0' * 32586

    assert (mvs[217] == [45, 98, 24]).all()


def test_multiverse_off(mvs):
    mvs.off()
    assert bytes(mvs) == b'\0' * 64 * PIXELS_PER_UNI * BYTES_PER_PIXEL


def test_multiverse_pub(mvs):
    # noinspection PyUnusedLocal
    def fake_send(data: bytes, host: str, port: int = 6454) -> None:
        assert host in ['1.1.1.1', '1.1.1.3', '1.1.1.7']

    with patch.object(mvs, '_send', fake_send):
        mvs.pub()
        assert mvs._seq_map == {'1.1.1.1': 25, '1.1.1.3': 13, '1.1.1.7': 29}
