import json

from qhue import Bridge

from tahlia.util import get_config


def load_bridge():
    config = get_config()
    bridge = Bridge(config['ip'], config['user'])
    name_id_map = {}
    for i, light in bridge.lights().items():
        name_id_map[light['name']] = i
    return bridge, name_id_map
