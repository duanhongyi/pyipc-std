import os
import time
import threading

from pyipc_std.client import StdClient
from pyipc_std.server import StdServer


class TestStdServer(object):

    def __init__(self):
        self.std_server = StdServer("test.sock")


    def start(self):
        self.std_server.register_method("add", self.add)
        t = threading.Thread(target=self.std_server.serve_forever)
        t.setDaemon(True)
        t.start()

    def add(self, x, y):
        z = x + y
        self.std_server.call_method("add_result", z)


result_map = {}
TestStdServer().start()

def test_pyipc_call_method():
    
    def add_result(z):
        result_map["z"] = 3
    
    client = StdClient("test.sock")
    client.register_method("add_result", add_result)
    client.start()
    client.call_method("add", 1, 2)
    time.sleep(1)
    assert result_map["z"] == 3
