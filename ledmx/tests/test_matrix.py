from ledmx.multiverse import Matrix
import pytest

layout_conf = '''
---
nodes:
  - addr: [10.0.0.10, 0, 0]
    outs: {0: "0-600"}
  - addr: [10.0.0.10, 0, 1]
    outs: {0: "901, 1001-1010", 1: "600 - 725", 3: "725- 800,1015"}
  - addr: [10.0.0.10, 0, 3]
    outs: {2: "800-850" }
  - addr: [10.0.0.10, 0, 4]
    outs: {1: "1016-1028", 3: "1062"}
'''

matrix = Matrix(layout_conf)


def test_matrix_set_get():
    with pytest.raises(KeyError):
        # 999 pixel isn't in the matrix
        matrix[999] = 4, 5, 6

    with pytest.raises(KeyError):
        # 999 pixel isn't in the matrix
        _ = matrix[999]

    matrix[500] = 42, 43, 45

    # pixel 500 == [42, 43, 45]
    assert (matrix[500] == (42, 43, 45)).all()

    # pixel 500 != [5, 43, 45]
    assert (matrix[500] != (5, 43, 45)).any()
