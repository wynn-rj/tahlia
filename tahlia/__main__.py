import sys
import json
import http.server
from threading import Thread
import flicker
import scene
import random
import time
from urllib import parse

class Haunter():
    def __init__(self, *args, **kwargs):
        self.haunting = False
        self.haunt_thread = None

    def haunt(self):
        h = flicker.HueHaunt()
        while self.haunting:
            h.run_once()
            i, f = divmod(random.uniform(5, 10), 1)
            for _ in range(int(i)):
                time.sleep(1)
                if not self.haunting:
                    return
            time.sleep(f)

def delay_func(delay, scenes):
    return [3000, 2400, 2100, 1400, 1000][len(scenes)]

times = ['Sunup', 'Midday', 'Sundown', ['Night', 'Night Town']]
haunter = Haunter()
scene_manager = scene.TimeTrackingSceneManager(delay=3, delay_func=delay_func, times=times)

class Handler(http.server.BaseHTTPRequestHandler):

    def handle_on(self, _):
        if haunter.haunting:
            return
        haunter.haunting = True
        haunter.haunt_thread = Thread(target=haunter.haunt)
        haunter.haunt_thread.start()

    def handle_off(self, _):
        if not haunter.haunting:
            return
        haunter.haunting = False
        haunter.haunt_thread.join()
        haunter.haunt_thread = None

    def switch_scene(self, parsed: parse.ParseResult):
        qs = parse.parse_qsl(parsed.query)
        scene_manager.switch(qs[0][1])

    def do_GET(self):
        handlers = {
            '/flicker_on': self.handle_on,
            '/flicker_off': self.handle_off,
            '/scene': self.switch_scene
        }
        parsed = parse.urlparse(self.path)
        if parsed.path not in handlers:
            self.send_error(http.server.HTTPStatus.NOT_FOUND)
            return
        try:
            handlers[parsed.path](parsed)
        except:
            self.send_error(http.server.HTTPStatus.INTERNAL_SERVER_ERROR)
            raise
        sbody = json.dumps({"status":"ok"})
        body = sbody.encode(sys.getfilesystemencoding(), 'surrogateescape')
        self.send_response(http.server.HTTPStatus.OK)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def main():
    with http.server.HTTPServer(('', 7890), Handler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    main()
