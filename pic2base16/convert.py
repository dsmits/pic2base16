#! /usr/bin/env python3
import os

import requests
import yaml
from pathlib import Path, PosixPath

from clize import Parameter

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
            if value[0] != "#":
                value = "#" + value
            rgb = ImageColor.getrgb(value)
            palette.extend(rgb)
    return palette


def get_target_size(im: ImageFile):
    scale = TARGET_WIDTH / im.width

    return TARGET_WIDTH, int(im.height * scale)

def retrieve_scheme_name():
    home = os.getenv("HOME")

    manager_file = Path(home)/".config/base16-universal-manager/config.yaml"

    with manager_file.open() as f:
        manager_config = yaml.safe_load(f)
        return manager_config["Colorscheme"]


def convert(input_: Path, target: Path, scheme_name = None, *, overwrite: bool = False,
            resize: bool= False, dither=False):
    print(f"Converting {input_} to {target} using scheme {scheme_name}")
    if scheme_name is None:
        scheme_name = retrieve_scheme_name()

    if target.exists() and not overwrite:
        raise FileExistsError(f"{target} already exists")

    if not dither:
        dither = Dither.NONE
    else:
        dither = Dither.FLOYDSTEINBERG

    palette = get_palette(scheme_name)

    im = Image.open(input_)
    target_size = get_target_size(im)
    if resize:
        im = im.resize(target_size)

    # Make sure image can be quantized
    im = im.convert("RGB")

    palette_image = Image.new("P", (1, 1))

    palette_image.putpalette(palette)
    converted = im.quantize(palette=palette_image, dither=dither)

    converted.save(target)


def load_scheme_list():
    response = requests.get(config.SCHEME_LIST_URI)
    scheme_list = yaml.safe_load(response.content)

    return scheme_list


def get_palette(scheme_name: str):
    scheme = get_scheme(scheme_name)

    return extract_palette(scheme)


def get_scheme(scheme_name: str):
    scheme_list = load_scheme_list()

    try:
        root_name, variant_name, scheme_uri = retrieve_base_scheme(scheme_name, scheme_list)
    except KeyError:
        raise KeyError(f"Scheme {scheme_name} not found. Available schemes: {scheme_list.keys()}")
    with (tempfile.TemporaryDirectory() as tempdir):
        repo_dir = Path(tempdir) / "scheme_repo"
        repo = Repo.clone_from(scheme_uri, repo_dir)

        repo_path = Path(repo.working_tree_dir)

        print(f"Looking for {root_name}-{variant_name}.yaml")
        if variant_name:
            pattern = f"{root_name}-{variant_name}.yaml"
        else:
            pattern = f"{root_name}.yaml"

        print(f"Using scheme file {pattern}")

        for f in repo_path.iterdir():
            if f.match(pattern):
                with f.open() as scheme_file:
                    return yaml.safe_load(scheme_file)
        raise KeyError(f"""Variant {variant_name} not found in scheme {root_name}
                            Existing files: {list(repo_path.iterdir())}""")


def retrieve_base_scheme(scheme_name, scheme_list):
    for key, scheme_uri in scheme_list.items():
        if scheme_name.startswith(key):
            root_name = key
            variant_name = scheme_name[len(key) + 1:]
            if not variant_name:
                variant_name = None
            scheme_uri = scheme_list[root_name]
            return root_name, variant_name, scheme_uri
    raise KeyError


def main():
    clize.run(convert)
