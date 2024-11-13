from pic2base16.convert import convert, get_scheme
from pathlib import Path

TEST_PIC = Path("./tests/test_pic.png")
TEST_SCHEME = "woodland"


def test_convert_runs():
    result_file = TEST_PIC.parent / "result.png"

    convert(TEST_PIC, result_file, TEST_SCHEME, overwrite=True)

def test_get_scheme():
    scheme = get_scheme(TEST_SCHEME)

    print(scheme)