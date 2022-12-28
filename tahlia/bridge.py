import json
from qhue import Bridge

def load_bridge(config_file='config.json'):
    with open(config_file) as cfg:
        config = json.load(cfg)
    bridge = Bridge(config['ip'], config['user'])
    name_id_map = {}
    for i, light in bridge.lights().items():
        name_id_map[light['name']] = i
    return bridge, name_id_map


