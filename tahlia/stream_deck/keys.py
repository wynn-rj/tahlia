from typing import Union

from PIL.Image import Image
from StreamDeck.Devices.StreamDeck import StreamDeck

from tahlia.stream_deck.util import (
    _FPS,
    PredefinedKeys,
    add_text_to_image,
    get_key_image,
)


class Key:
    def __init__(self) -> None:
        self._error_state = None

    def keyframe(self, deck: StreamDeck) -> Union[Image, None]:
        if self._error_state is None:
            return self.render_keyframe(deck)
        self._error_state += 1
        if self._error_state == 1:
            return get_key_image(deck, PredefinedKeys.ERROR)
        if self._error_state > 2 * _FPS:
            self._error_state = None
            self.enable()

    def render_keyframe(self, deck: StreamDeck) -> Union[Image, None]:
        pass

    def press(self):
        if self._error_state is not None:
            return
        try:
            return self.perform_action()
        except:
            self.disable()
            self._error_state = 0
            raise

    def perform_action(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass


class StaticKey(Key):
    def __init__(self, image: Image, text: str = ""):
        super().__init__()
        self._redraw = True
        self._image = image
        self._text = text

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value: Image):
        self._image = value
        self._redraw = True

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self._redraw = True

    def enable(self):
        self._redraw = True

    def render_keyframe(self, deck: StreamDeck) -> Union[Image, None]:
        if not self._redraw:
            return None
        self._redraw = False
        return add_text_to_image(deck, self._image, self._text)
