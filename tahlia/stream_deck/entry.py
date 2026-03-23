import logging
import time
from contextlib import contextmanager
from fractions import Fraction
from functools import partial
from typing import List

from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.Transport.Transport import TransportError

from tahlia.stream_deck.pages import PageManager
from tahlia.stream_deck.util import _FPS

_log = logging.getLogger(__name__)


def _run(deck: StreamDeck, page_manager: PageManager):

    def press(_: StreamDeck, key: int, pressed: bool):
        if pressed:
            try:
                page_manager.current_page.press_key(key)
            except:
                _log.exception('Unhandled exception during key press')

    deck.set_key_callback(press)
    page_manager.show_home()
    frame_time = Fraction(1, _FPS)
    next_frame = Fraction(time.monotonic())
    while deck.is_open():
        try:
            with deck:
                page_manager.current_page.render_keyframe()
        except TransportError as ex:
            if not deck.is_open():
                return
            logging.exception('Transport error')
        next_frame += frame_time
        sleep_interval = float(next_frame) - time.monotonic()
        if sleep_interval >= 0:
            time.sleep(sleep_interval)


@contextmanager
def use_stream_deck():
    streamdecks: List[StreamDeck] = DeviceManager().enumerate()
    deck = next(filter(lambda s: s.is_visual(), streamdecks), None)
    if deck is None:
        raise ConnectionError('Unable to find stream deck')

    deck.open()
    deck.reset()

    try:
        yield deck, partial(_run, deck)
    finally:
        with deck:
            deck.reset()
            deck.close()
