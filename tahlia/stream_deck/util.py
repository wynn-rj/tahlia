import enum
import functools
import os

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

_loaded_key_images = dict()
_FPS = 30


class PredefinedKeys(enum.Enum):
    PREV_PAGE = 'chevron-left.png'
    NEXT_PAGE = 'chevron-right.png'
    HOME_PAGE = 'home.png'
    ERROR = 'error.png'


def get_key_image(deck: StreamDeck, key: PredefinedKeys) -> Image.Image:
    if key in _loaded_key_images:
        return _loaded_key_images[key]
    image = load_image(deck, os.path.join(os.path.dirname(__file__), 'assets', key.value))
    _loaded_key_images[key] = image
    return image


@functools.lru_cache()
def get_optimal_font_size(max_width: float, text: str):
    for i in range(14, 7, -1):
        font = ImageFont.load_default(i)
        if font.getlength(text) < (0.95 * max_width):
            break
    return i


def load_image(deck: StreamDeck, path: str) -> Image.Image:
    image = Image.open(path)
    return PILHelper.create_scaled_image(deck, image)


# Generates a custom tile with run-time generated text and custom image via the PIL module.
def add_text_to_image(deck: StreamDeck, image: Image.Image, label: str, font_size=-1):
    draw = ImageDraw.Draw(image)
    if font_size == -1:
        font_size = get_optimal_font_size(image.width, label)
    font = ImageFont.load_default(font_size)
    draw.text((image.width / 2, image.height - 5),
              text=label,
              font=font,
              anchor="ms",
              fill="white",
              stroke_width=1,
              stroke_fill='black')
    return image
