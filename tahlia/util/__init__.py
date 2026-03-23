import contextlib
import json
from pathlib import Path
from typing import ContextManager

IMAGE_DIR = Path(Path(__file__).parent.parent.parent, 'images')
LAYOUT_DIR = Path(Path(__file__).parent.parent.parent, 'layout')
CONFIG = Path(Path(__file__).parent.parent.parent, 'config.json')

_loaded_config = None


def get_config() -> dict:
    global _loaded_config
    if _loaded_config is None:
        with open(CONFIG) as config:
            _loaded_config = json.load(config)
    return _loaded_config


def get_file(file: str, dir: Path):
    if not isinstance(file, str):
        return None
    absfile = str(Path(file).absolute().name)
    if absfile != file or absfile.startswith('.'):
        return
    path = dir.joinpath(absfile).resolve()
    if not path.exists():
        return
    return str(path)


def get_image(path: str):
    if (image := get_file(path, IMAGE_DIR)) is None:
        print(f"Bad image '{path}'")
    return image


@contextlib.contextmanager
def update_layout_file(name: str, no_save=False) -> ContextManager[list]:
    if (file := get_file(name, LAYOUT_DIR)) is None:
        raise ValueError(f"Unknown layout file '{name}'")
    with open(file) as f:
        if not isinstance(layout := json.load(f), list):
            raise ValueError(f"Invalid layout file '{name}'")
    yield layout
    if no_save:
        return
    with open(file, 'w') as f:
        json.dump(layout, f)


def load_layout_file(name: str):
    with update_layout_file(name, no_save=True) as layout:
        return layout
