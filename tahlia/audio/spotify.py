import asyncio
import json

import spotipy

from tahlia.util import get_config


class SpotifyAudioClient():

    def __init__(self):
        scope = "user-read-playback-state,user-modify-playback-state"
        config = get_config()
        auth = spotipy.SpotifyOAuth(scope=scope,
                                    client_id=config['spotify-id'],
                                    client_secret=config['spotify-secret'],
                                    redirect_uri=config['spotify-redirect-uri'],
                                    open_browser=False)
        self.client = spotipy.Spotify(client_credentials_manager=auth)
        devices = (self.client.devices() or {}).get('devices', [])
        device_map = {d['name']: d.get('id', None) for d in devices if 'name' in d}
        self.device_id = device_map.get(config.get('spotify-preferred-device', None), None)
        print(self.device_id)

    def play_playlist(self, uri):
        self.client.start_playback(device_id=self.device_id, context_uri=uri)
        self.client.shuffle(True, device_id=self.device_id)
        self.client.repeat('context', device_id=self.device_id)
        self.next()

    def toggle_pause(self):
        playing = (self.client.current_playback() or {}).get('is_playing', False)
        if playing:
            self.client.pause_playback(device_id=self.device_id)
        else:
            self.client.start_playback(device_id=self.device_id)

    def next(self):
        self.client.next_track(device_id=self.device_id)

    def volume_adjust(self, amt: int):
        if (info := self.client.current_playback()) is None:
            raise ValueError('No current playback context')
        volume = info['device']['volume_percent'] + amt
        volume = min(100, max(0, volume))
        self.client.volume(volume, device_id=self.device_id)

    def retrive_context(self, url: str):
        try:
            return self.client.playlist(url)
        except spotipy.SpotifyException:
            pass
        try:
            return self.client.album(url)
        except spotipy.SpotifyException:
            pass
        return None
