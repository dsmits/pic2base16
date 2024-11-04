from pathlib import Path

import base16_colorlib
from PIL.Image import Palette
from PIL.ImageFile import ImageFile
from base16_colorlib import catppuccin_mocha
from PIL import ImageColor, Image
from PIL.ImagePalette import ImagePalette

NUM_COLORS = 16
TARGET_WIDTH = 256


def extract_palette(base16_scheme: dict[str, str]):
    palette = []
    for key, value in base16_scheme.items():
        if key.startswith("base"):
            rgb = ImageColor.getrgb(value)
            palette.extend(rgb)
    print(palette)
    return palette


def get_target_size(im: ImageFile):
    scale = TARGET_WIDTH / im.width

    return TARGET_WIDTH, int(im.height * scale)


def convert(input_, target: Path, scheme_name, overwrite=False):
    if target.exists() and not overwrite:
        raise FileExistsError(f"{target} already exists")

    scheme = getattr(base16_colorlib, scheme_name)
    palette = extract_palette(scheme)

    im = Image.open(input_)
    target_size = get_target_size(im)
    im = im.resize(target_size)

    paletteImage = Image.new("P", (1, 1))

    paletteImage.putpalette(palette)
    converted = im.quantize(palette=paletteImage, dither=2)

    converted.save(target)


if __name__ == "__main__":
    convert()
