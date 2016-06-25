import os
import time

from pyipc_std.client import StdClient

here = os.path.dirname(os.path.abspath(__file__))

result_map = {}

def test_pyipc_call_method():
    
    def add_result(z):
        result_map["z"] = 3
    
    client = StdClient(os.path.join(here, "pyipc_std_test_server.py"))
    client.register_method("add_result", add_result)
    client.start()
    client.call_method("add", 1, 2)
    time.sleep(1)
    assert result_map["z"] == 3
