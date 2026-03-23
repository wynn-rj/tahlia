from threading import Thread
from tahlia.lights.bridge import load_bridge
import time
import random


def coinflip():
    return random.randint(0, 1) == 0


def asid(light):
    if isinstance(light, Light):
        return light.id
    return light


class Light:
    def __init__(self, name, hid):
        self.name = name
        self.id = hid


class HueHaunt:
    def __init__(self):
        bridge, lights = load_bridge()
        self.bridge = bridge
        self.lights = [Light(k, v) for k, v in lights.items()]
        self.cur_light = None

    def light_api(self, light=None):
        light = light or self.cur_light
        return self.bridge.lights[asid(light)]

    def bri(self, light=None):
        return self.light_api(light)()["state"]["bri"]

    def set_bri(self, val, light=None, ttime=1):
        return self.light_api(light).state(bri=val, on=(val != 0), transitiontime=ttime)

    def obscure(self):
        fast = coinflip()
        bri = self.bri()
        print(f"Obscure-{'fast' if fast else 'slow'} {self.cur_light.name}")
        self.set_bri(1 if fast else 0, ttime=(1 if fast else 2))
        time.sleep(0.10 if fast else 0.4)
        self.set_bri(bri, ttime=(1 if fast else 2))

    def flicker(self):
        cnt = random.randint(2, 4)
        print(f"Flicker-{cnt} {self.cur_light.name}")
        for _ in range(cnt):
            bri = self.bri()
            self.set_bri(max(1, bri - 50))
            time.sleep(random.uniform(0.05, 0.1))
            self.set_bri(bri, ttime=0)

    def run_once(self):
        # self.cur_light = self.lights[2] #Dungeon 2
        self.cur_light = random.choice(self.lights)
        opt = random.randint(1, 4)
        # opt = 1
        if opt == 1:
            self.obscure()
        else:
            self.flicker()


class Haunter:
    def __init__(self, *args, **kwargs):
        self.haunting = False
        self.haunt_thread = None

    def haunt(self):
        h = HueHaunt()
        while self.haunting:
            h.run_once()
            i, f = divmod(random.uniform(5, 10), 1)
            for _ in range(int(i)):
                time.sleep(1)
                if not self.haunting:
                    return
            time.sleep(f)

    def start(self):
        if self.haunting:
            return
        self.haunting = True
        self.haunt_thread = Thread(target=self.haunt)
        self.haunt_thread.start()

    def stop(self):
        if not self.haunting:
            return
        self.haunting = False
        self.haunt_thread.join()
        self.haunt_thread = None
