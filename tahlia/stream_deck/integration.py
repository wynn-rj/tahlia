from pathlib import Path
from typing import List, Union

from PIL.Image import Image
from StreamDeck.Devices.StreamDeck import StreamDeck

from tahlia.audio.spotify import SpotifyAudioClient
from tahlia.lights.scene import SceneManager
from tahlia.stream_deck.keys import Key, StaticKey
from tahlia.stream_deck.pages import PageChangingKey, PageManager, TabbedPage
from tahlia.stream_deck.util import load_image
from tahlia.util import IMAGE_DIR, get_image, load_layout_file
from tahlia.window.window import display_on_window


class PageLoader():

    def __init__(self, deck: StreamDeck, scene_manager: SceneManager, audio_client: SpotifyAudioClient):
        self.deck = deck
        self.scene_manager = scene_manager
        self.page_manager = None
        self.audio_client = audio_client

    def load_manager(self, key_config: List[dict]):
        self.page_manager = PageManager()
        self.page_manager.home_page = self.load_page(key_config, show_home=False)
        return self.page_manager

    def load_page(self, key_config: list = [], show_home=True):
        keys = [self.create_key_from_config(c) for c in key_config]
        return TabbedPage(self.deck, self.page_manager, keys, show_home)

    def create_key_from_config(self, config) -> Union[Key, None]:
        if not isinstance(config, dict):
            return None
        create_func = {
            'scene': SwitchSceneKey.from_config,
            'window': WindowImageKey.from_config,
            'folder': self.create_folder,
            'playlist': AudioPlayPlaylistKey.from_config,
            'volume': AudioVolumeChangeKey.from_config,
            'play/pause': AudioPlayPauseKey.from_config,
            'next': AudioNextKey.from_config
        }.get(config.get('type'))
        return None if create_func is None else create_func(self, config)

    def get_image(self, config: dict):
        if (img_path := get_image(config.get('image'))) is None:
            return None
        image = load_image(self.deck, img_path)
        return (image, img_path)

    def create_folder(self, _, config: dict):
        if 'keys' not in config or (image := self.get_image(config)) is None:
            print('Abort folder add')
            return None
        page = self.load_page(load_layout_file(config['keys']))
        return PageChangingKey(image[0], page, self.page_manager, label=config.get('label'))


class SwitchSceneKey(StaticKey):

    def __init__(self, image: Image, manager: SceneManager, scene: str, label: str = ''):
        super().__init__(image, label or scene)
        self._scene = scene
        self._scene_manager = manager

    def perform_action(self):
        self._scene_manager.switch(self._scene)

    @staticmethod
    def from_config(loader: PageLoader, config: dict):
        if 'scene' not in config or (image := loader.get_image(config)) is None:
            return None
        if not loader.scene_manager.has_scene(scene := config['scene']):
            print(f"Unknown scene '{scene}'")
            return None
        return SwitchSceneKey(image[0], loader.scene_manager, scene, config.get('label'))


class WindowImageKey(StaticKey):

    def __init__(self, image: Image, label: str, file: str):
        super().__init__(image, label)
        self._file = file

    def perform_action(self):
        display_on_window(self._file)

    @staticmethod
    def from_config(loader: PageLoader, config: dict):
        if 'label' not in config or (image := loader.get_image(config)) is None:
            return None
        return WindowImageKey(image[0], config['label'], image[1])


class AudioPlayPlaylistKey(StaticKey):

    def __init__(self, image: Image, audio_client: SpotifyAudioClient, label: str, uri: str):
        super().__init__(image, label)
        self._uri = uri
        self._client = audio_client

    def perform_action(self):
        self._client.play_playlist(self._uri)

    @staticmethod
    def from_config(loader: PageLoader, config: dict):
        if 'label' not in config or 'uri' not in config or (image := loader.get_image(config)) is None:
            return None
        return AudioPlayPlaylistKey(image[0], loader.audio_client, config['label'], config['uri'])


class AudioNextKey(StaticKey):

    def __init__(self, image: Image, audio_client: SpotifyAudioClient):
        super().__init__(image)
        self._client = audio_client

    def perform_action(self):
        self._client.next()

    @staticmethod
    def from_config(loader: PageLoader, config: dict):
        if (image := loader.get_image(config)) is None:
            return None
        return AudioNextKey(image[0], loader.audio_client)


class AudioPlayPauseKey(StaticKey):

    def __init__(self, image: Image, audio_client: SpotifyAudioClient):
        super().__init__(image)
        self._client = audio_client

    def perform_action(self):
        self._client.toggle_pause()

    @staticmethod
    def from_config(loader: PageLoader, config: dict):
        if (image := loader.get_image(config)) is None:
            return None
        return AudioPlayPauseKey(image[0], loader.audio_client)


class AudioVolumeChangeKey(StaticKey):

    def __init__(self, image: Image, audio_client: SpotifyAudioClient, amount: int):
        super().__init__(image)
        self._client = audio_client
        self._amount = amount

    def perform_action(self):
        self._client.volume_adjust(self._amount)

    @staticmethod
    def from_config(loader: PageLoader, config: dict):
        if 'amount' not in config or (image := loader.get_image(config)) is None:
            return None
        return AudioVolumeChangeKey(image[0], loader.audio_client, config['amount'])
