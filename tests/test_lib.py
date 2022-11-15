import pytest
from typing import List
from redqct.lib import Number, cube


@pytest.fixture
def cube_data() -> List[List[Number]]:
    return [[7, 8, 2], [8.2, 2.1, 4.8], [-10, 4.3, -853]]


def test_cube_function(cube_data: List[List[Number]]) -> None:
    ints, floats, mix = cube_data

    cubed_ints = [cube(x) for x in ints]
    cubed_floats = [cube(x) for x in floats]
    cubed_mix = [cube(x) for x in mix]

    assert cubed_ints == [343, 512, 8]
    assert cubed_floats == [551.368, 9.261, 110.592]
    assert cubed_mix == [-1000, 79.507, -620_650_477]
