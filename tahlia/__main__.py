import asyncio
import http.server
import json
import random
import sys
import threading
import time
from functools import partial
from threading import Thread
from urllib import parse

import tahlia.lights.flicker as flicker
import tahlia.lights.scene as scene
import tahlia.window.window as window
from tahlia.audio.spotify import SpotifyAudioClient
from tahlia.bot.audio import AudioManagerCog
from tahlia.bot.entry import setup as bot_setup
from tahlia.bot.lights import SceneManagerCog
from tahlia.bot.window import WindowManagerCog
from tahlia.stream_deck.entry import use_stream_deck
from tahlia.stream_deck.integration import PageLoader
from tahlia.stream_deck.pages import PageChangingKey, PageManager
from tahlia.util import get_config, load_layout_file


def load_bot():
    return asyncio.run(bot_setup()), get_config()["token"]


def load_light_manager():

    def delay_func(delay, scenes):
        return [3000, 2400, 2100, 1400, 1000][len(scenes)]

    times = ["Sunup", "Midday", "Sundown", ["Night", "Night Town"]]
    return scene.TimeTrackingSceneManager(delay=3, delay_func=delay_func, times=times)


def get_page(pm: PageManager, layout: list, label: str):
    i = next(
        filter(lambda x: (x[1] or {}).get("label") == label, enumerate(layout)), (None,)
    )[0]
    if i is None or not isinstance((key := pm.home_page.keys[i]), PageChangingKey):
        raise ValueError(f"Failed to find page '{label}'")
    return key.page


def main():
    print("Loading light manager")
    light_manager = load_light_manager()
    print("Loading bot")
    bot, token = load_bot()
    print("Loading layout")
    layout = load_layout_file("home.json")
    print("Loading audio client")
    audio_client = SpotifyAudioClient()
    if audio_client.device_id:
        print("  Audio client connected to preferred device")

    print("Loading stream deck")
    with use_stream_deck() as (deck, run_deck):
        page_manager = PageLoader(deck, light_manager, audio_client).load_manager(
            layout
        )
        threading.Thread(target=partial(run_deck, page_manager)).start()

        print("Loading scene manager cog")
        light_page = get_page(page_manager, layout, "Lights")
        asyncio.run(bot.add_cog(SceneManagerCog(bot, light_manager, light_page)))
        print("Loading window manager cog")
        window_page = get_page(page_manager, layout, "Window")
        asyncio.run(bot.add_cog(WindowManagerCog(bot, window_page)))
        print("Loading audio manager cog")
        music_page = get_page(page_manager, layout, "Music")
        asyncio.run(bot.add_cog(AudioManagerCog(bot, music_page, audio_client)))

        bot.run(token)

    for t in threading.enumerate():
        try:
            t.join()
        except RuntimeError:
            pass


if __name__ == "__main__":
    # main()
    import time

    c = SpotifyAudioClient()
    while True:
        c.client.current_playback()
        time.sleep(5)
