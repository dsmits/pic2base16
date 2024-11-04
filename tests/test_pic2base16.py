from pic2base16 import convert
from pathlib import Path

TEST_PIC = Path("./tests/test_pic.jpg")
TEST_SCHEME = "solarized"


def test_convert_runs():
    result_file = TEST_PIC.parent / "result.bmp"

    convert(TEST_PIC, result_file, TEST_SCHEME)
