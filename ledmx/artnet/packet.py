from struct import pack

_H = b'Art-Net\x00'
_H_VER = b'\x00\x0E'


def art_sync() -> bytes:
    return _H + b'\x00\x52' + _H_VER + b'\0\0'


def art_dmx(data: bytes, net: int = 0, subnet: int = 0, universe: int = 0, seq: int = 0) -> bytes:
    assert 0 <= seq <= 255
    assert 0 <= net < 128
    assert 0 <= subnet < 16
    assert 0 <= universe < 16
    length = len(data)
    assert 2 <= length <= 512
    assert length % 2 == 0
    return _H + b'\x00\x50' + _H_VER + pack('BxBB', seq, subnet << 4 | universe, net) + pack('!H', length) + data
