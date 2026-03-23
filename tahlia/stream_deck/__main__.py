import os
import threading
from entry import use_stream_deck
from PIL import Image
from pages import PageChangingKey, PageManager, Page, TabbedPage, TabHelperKey
from keys import StaticKey
from util import PredefinedKeys, get_key_image, load_image



if __name__ == '__main__':
    images = list(filter(lambda f: not f.startswith('.'), os.listdir('images')))
    pm = PageManager()

    with use_stream_deck() as (deck, run):
        keys = [StaticKey(load_image(deck, f'images/{img}'), img) for img in images]
        last_image = keys[-1].image
        test_page = TabbedPage(deck, pm, keys)
        tester = TabHelperKey(deck, PredefinedKeys.PREV_PAGE, lambda: test_page.add_key(StaticKey(last_image, 'yoo')))
        test_page.add_key(tester)
        show_test_page = PageChangingKey(get_key_image(deck, PredefinedKeys.NEXT_PAGE), test_page, pm)
        pm.home_page = Page(deck, [*[None]*7, show_test_page])
        run(pm)
    for t in threading.enumerate():
        try:
            t.join()
        except RuntimeError:
            pass