from base16_colorlib import catppuccin_mocha
from PIL import ImageColor, Image
from PIL.ImagePalette import ImagePalette


def extract_palette(base16_scheme: dict[str, str]):
    palette = []
    for key, value in base16_scheme.items():
        if key.startswith("base"):
            rgb = ImageColor.getrgb(value)
            palette.extend(rgb)
    print(palette)
    return ImagePalette(palette=palette)


def convert(input_, target):
    im = Image.open(input_)

    palette = extract_palette(catppuccin_mocha)

    converted = im.convert(mode="P", palette=palette)

    converted.save(target)


if __name__ == "__main__":
    convert()
