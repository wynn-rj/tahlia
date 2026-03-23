from typing import Callable, List, Union

from PIL import Image
from StreamDeck.Devices.StreamDeck import StreamDeck
from StreamDeck.ImageHelpers import PILHelper

from tahlia.stream_deck.keys import Key, StaticKey
from tahlia.stream_deck.util import PredefinedKeys, get_key_image


class Page():

    def __init__(self, deck: StreamDeck, keys: List[Union[Key, None]]):
        self.deck = deck
        if len(keys) > deck.key_count():
            raise ValueError('Cannot define more keys than the deck supports')
        self._keys = keys
        self._enabled = False

    def _all_keys(self, action: Callable[[Key], None]):
        for key in filter(lambda k: k is not None, self.keys):
            action(key)

    @property
    def keys(self):
        return self._keys

    def render_keyframe(self):
        for i, key in enumerate(self.keys):
            if key is None or (image := key.keyframe(self.deck)) is None:
                continue
            self.deck.set_key_image(i, PILHelper.to_native_format(self.deck, image))

    def enable(self):
        with self.deck:
            for i in range(self.deck.key_count()):
                self.deck.set_key_image(i, None)
            self._all_keys(lambda key: key.enable())
        self._enabled = True

    def disable(self):
        with self.deck:
            self._all_keys(lambda key: key.disable())
        self._enabled = False

    def press_key(self, i: int):
        if not 0 <= i < len(self.keys) or (key := self.keys[i]) is None:
            return
        key.press()

    def add_key(self, key: Union[Key, None]) -> bool:
        if len(self.keys) == self.deck.key_count():
            return False
        self.keys.append(key)
        key.enable()
        return True


class PageManager():

    def __init__(self, home: Union[Page, None] = None):
        self._current_page: Union[None, Page] = None
        self.home_page = home

    def show_page(self, page: Page):
        if self._current_page:
            self._current_page.disable()
        page.enable()
        self._current_page = page

    def show_home(self):
        if self.home_page is not None:
            self.show_page(self.home_page)

    @property
    def current_page(self):
        return self._current_page


class PageChangingKey(StaticKey):

    def __init__(self, image: Image.Image, page: Page, page_manager: PageManager, label: str = ''):
        super().__init__(image, label)
        self.page = page
        self._page_manager = page_manager

    def perform_action(self):
        self._page_manager.show_page(self.page)


class TabHelperKey(StaticKey):

    def __init__(self, deck: StreamDeck, key: PredefinedKeys, action: Callable):
        super().__init__(get_key_image(deck, key), '')
        self._action = action

    def perform_action(self):
        self._action()


class TabbedPage(Page):

    def __init__(self, deck: StreamDeck, page_manager: PageManager, keys: List[Union[Key, None]], show_home=True):
        self._page_size = deck.key_count() - 2
        self._page_manager = page_manager
        super().__init__(deck, [])

        if show_home:
            keys = [TabHelperKey(deck, PredefinedKeys.HOME_PAGE, page_manager.show_home), *keys]
        page1 = keys[:self._page_size + 1]
        other_pages = [keys[i:i + self._page_size] for i in range(len(page1), len(keys), self._page_size)]
        self._pages = [page1, *other_pages]
        self._cur_page = 0
        self._next_page = 0

        self._keys_on_final_page = len(self._pages[-1])
        rows, cols = deck.key_layout()
        self._prev_key_index = (rows - 1) * cols

        if (missing := self._page_size - len(page1)) > 0:
            page1.extend([None] * missing)
        prev_page = page1
        for page in self._pages[1:]:
            prev_page.append(TabHelperKey(deck, PredefinedKeys.NEXT_PAGE, self.next_page))
            if (missing := self._page_size - len(page)) > 0:
                page.extend([None] * missing)
            page.insert(self._prev_key_index, TabHelperKey(deck, PredefinedKeys.PREV_PAGE, self.prev_page))
            prev_page = page

    @property
    def keys(self):
        return self._pages[self._cur_page]

    def next_page(self):
        if self._cur_page == len(self._pages) - 1:
            return
        self._next_page = self._cur_page + 1
        self._page_manager.show_page(self)

    def prev_page(self):
        if self._cur_page == 0:
            return
        self._next_page = self._cur_page - 1
        self._page_manager.show_page(self)

    def disable(self):
        super().disable()
        self._cur_page = self._next_page
        self._next_page = 0

    def add_key(self, key: Union[Key, None]) -> bool:
        if self._keys_on_final_page < self._page_size:
            i = self._keys_on_final_page
            if i >= self._prev_key_index:
                i += 1
            self._keys_on_final_page += 1
            self._pages[-1][i] = key
            return
        self._keys_on_final_page = 1
        self._pages[-1].append(TabHelperKey(self.deck, PredefinedKeys.NEXT_PAGE, self.next_page))
        self._pages.append([key, *([None] * (self._page_size))])
        self._pages[-1][self._prev_key_index] = TabHelperKey(self.deck, PredefinedKeys.PREV_PAGE, self.prev_page)
