#!/usr/bin/env python
import time
import threading
from pyipc_std.server import StdServer


class TestStdServer(object):

    def __init__(self):
        self.std_server = StdServer()


    def start(self):
        self.std_server.register_method("add", self.add)
        self.std_server.serve_forever()

    def add(self, x, y):
        z = x + y
        self.std_server.call_method("add_result", z)


if __name__ == "__main__":
    t = TestStdServer()
    t.start()
    time.sleep(5)
