from time import sleep
from typing import Sequence, Union, Optional, Callable

from bridge import load_bridge

class SceneException(Exception):
    pass

class SceneManager():
    def __init__(self, delay: int=5, group: str='1'):
        self.bridge, _ = load_bridge()
        self.delay = delay
        groups = self.bridge.groups()
        if group not in groups:
            group = {v['name']: k for k, v in groups.items()}.get(group, None)
            if group is None:
                raise SceneException(f'Unknown group {group}')
        self.group = group
        self.refresh()

    def refresh(self):
        self.scenes = self.bridge.scenes()
        self.names_to_id = {v['name']: k for k, v in self.scenes.items()}

    def _get_scene(self, scene: str) -> str:
        scene = self.names_to_id.get(scene, scene)
        return scene if scene in self.scenes else None

    def _assert_scene(self, scene: str) -> str:
        res = self._get_scene(scene)
        if res is None:
            raise SceneException(f'Unknown scene {scene}')
        return res

    def switch(self, scene: str):
        scene = self._assert_scene(scene)
        self.bridge.groups[self.group].action(
            scene=scene, transitiontime=10*self.delay)

class TimeTrackingSceneManager(SceneManager):
    """
    Keeps track of the current time of day and switches between all the
    itermediate times when calling switch

    Args:
        times: A sequence of time scenes. The last scene will wrap to the
            beginning scene. Each entry can either be a string of the scene name
            or a sequence of possible scene names. The first entry in the sequence 
            will be used when traversing scenes, the other entries are valid 
            starting points
        delay_func: A func to calculate the delay. Will be passed the standard
            delay (in ms) and a list of the scenes to be traversed. When unspecified,
            the delay will be devided by the number of scenes to traverse
    """
    def __init__(self, times: Sequence[Union[str, Sequence[str]]], 
                 delay_func: Optional[Callable[[int, Sequence[str]], int]] = None, 
                 *args, **kwargs):
        self._cur_scene = None
        self.delay_func = delay_func or self.linear_delay
        super().__init__(*args, **kwargs)
        normalized_times = [[time] if isinstance(time, str) else time for time in times]
        self.times = [[self._assert_scene(scene) for scene in seq] for seq in normalized_times]

    def _index_of(self, scene: str):
        for i, scenes in enumerate(self.times):
            if scene in scenes:
                return i
        return -1

    def switch(self, scene: str):
        end_scene = self._assert_scene(scene)
        end_index = self._index_of(end_scene)
        if end_index == -1 or self._cur_scene is None:
            if end_index != -1:
                self._cur_scene = end_scene
            return super().switch(end_scene)
        
        cur_index = self._index_of(self._cur_scene)
        times = self.times
        if end_index < cur_index:
            times = [*self.times, *self.times]
            end_index += len(self.times)
        scenes = [*[time[0] for time in times[cur_index + 1:end_index]], end_scene]

        delay = int(self.delay_func(self.delay*1000, scenes) / 100)
        for scene in scenes:
            self.bridge.groups[self.group].action(scene=scene, transitiontime=delay)
            sleep(0.95 * ((delay) / 10))
        self._cur_scene = end_scene
    

    @staticmethod
    def linear_delay(delay: int, scenes: Sequence[str]) -> int:
        return int(delay / len(scenes))
