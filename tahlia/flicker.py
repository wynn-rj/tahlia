from bridge import load_bridge
import time
import random
import signal

running = True
def handler(*args, **kwargs):
    print('Exiting shortly..')
    global running
    running = False

def coinflip():
    return random.randint(0, 1) == 0

def asid(light):
    if isinstance(light, Light):
        return light.id
    return light

class Light():

    def __init__(self, name, hid):
        self.name = name
        self.id = hid

class HueHaunt():

    def __init__(self):
        bridge, lights = load_bridge()
        self.bridge = bridge
        self.lights = [Light(k, v) for k, v in lights.items()]
        self.cur_light = None

    def light_api(self, light=None):
        light = light or self.cur_light
        return self.bridge.lights[asid(light)]

    def bri(self, light=None):
        return self.light_api(light)()['state']['bri']

    def set_bri(self, val, light=None, ttime=1):
        return self.light_api(light).state(bri=val, on=(val!=0), transitiontime=ttime)

    def obscure(self):
        fast=coinflip()
        bri = self.bri()
        print(f'Obscure-{"fast" if fast else "slow"} {self.cur_light.name}')
        self.set_bri(1 if fast else 0, ttime=(1 if fast else 2))
        time.sleep(0.10 if fast else 0.4)
        self.set_bri(bri, ttime=(1 if fast else 2))

    def flicker(self):
        cnt = random.randint(2, 4)
        print(f'Flicker-{cnt} {self.cur_light.name}')
        for _ in range(cnt):
            bri = self.bri()
            self.set_bri(max(1, bri-50))
            time.sleep(random.uniform(0.05, 0.1))
            self.set_bri(bri, ttime=0)

    def run_once(self):
        #self.cur_light = self.lights[2] #Dungeon 2
        self.cur_light = random.choice(self.lights)
        opt = random.randint(1, 4)
        #opt = 1
        if opt == 1:
            self.obscure()
        else:
            self.flicker()

def main():
    h = HueHaunt()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    while running:
        h.run_once()
        i, f = divmod(random.uniform(30, 60), 1)
        for _ in range(int(i)):
            time.sleep(1)
            if not running:
                return
        time.sleep(f)

if __name__ == '__main__':
    main()
