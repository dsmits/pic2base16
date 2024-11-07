#! /usr/bin/env python3
import requests
import yaml
from pathlib import Path, PosixPath
from pic2base16 import config
import clize
from PIL import ImageColor, Image
from PIL.Image import Dither
from PIL.ImageFile import ImageFile
import tempfile

from git import repo, Repo

NUM_COLORS = 16
TARGET_WIDTH = 256


def extract_palette(base16_scheme: dict[str, str]):
    palette = []
    for key, value in base16_scheme.items():
        if key.startswith("base"):
            if value [0] != "#":
                value = "#" + value
            rgb = ImageColor.getrgb(value)
            palette.extend(rgb)
    print(palette)
    return palette


def get_target_size(im: ImageFile):
    scale = TARGET_WIDTH / im.width

    return TARGET_WIDTH, int(im.height * scale)


def convert(input_: Path, target: Path, scheme_name: str, overwrite: bool = False):
    if target.exists() and not overwrite:
        raise FileExistsError(f"{target} already exists")

    palette = get_palette(scheme_name)

    im = Image.open(input_)
    target_size = get_target_size(im)
    im = im.resize(target_size)

    palette_image = Image.new("P", (1, 1))

    palette_image.putpalette(palette)
    converted = im.quantize(palette=palette_image, dither=Dither.FLOYDSTEINBERG)

    converted.save(target)


def load_scheme_list():
    response = requests.get(config.SCHEME_LIST_URI)
    scheme_list = yaml.safe_load(response.content)

    return scheme_list

def get_palette(scheme_name: str):
    scheme = get_scheme(scheme_name)

    return extract_palette(scheme)

def get_scheme(scheme_name: str):
    name_parts = scheme_name.split("-")
    root_name = name_parts[0]
    variant_name = "-".join(name_parts[1:])
    scheme_list = load_scheme_list()

    print(scheme_list)

    scheme_uri = scheme_list[root_name]

    with (tempfile.TemporaryDirectory() as tempdir):
        repo_dir = Path(tempdir) / "scheme_repo"

        repo = Repo.clone_from(scheme_uri, repo_dir)

        repo_path = Path(repo.working_tree_dir)

        for f in repo_path.iterdir():
            if f.match(f"{root_name}-{variant_name}.yaml"):
                with f.open() as scheme_file:
                    return yaml.safe_load(scheme_file)


def main():
    clize.run(convert)