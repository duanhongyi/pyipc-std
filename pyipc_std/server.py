import os
import sys
import pickle
import struct
import threading


class StdServer(object):

    def __init__(self):
        self.registered_method_table = {}
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.is_running = False
        self._patch_std()


    def register_method(self, method_id, method):
        self.registered_method_table[method_id] = method

    def call_method(self, method_id, *args, **kwargs):
        data = pickle.dumps({
            "method_id": method_id,
            "args": args,
            "kwargs": kwargs,
        })
        os.write(self.stdout.fileno(), struct.pack('i', len(data)))
        os.write(self.stdout.fileno(), data)


    def serve_forever(self):
        self.is_running = True
        t = threading.Thread(target=self._read_task)
        t.setDaemon(True)
        t.start()

    def close(self):
        self.is_running = False
        sys.stdin.close()
        sys.stdout.close()
    
    def __del__(self):
        self.close()

    def _patch_std(self):
        sys.stdin = open("/var/log/pyipc-std.in", "w")
        sys.stdout = open("/var/log/pyipc-std.out", "w")
        sys.stderr = open("/var/log/pyipc-std.err", "w")

    def _read_task(self):
        while self.is_running:
            length = struct.unpack('i', os.read(self.stdin.fileno(), 4))[0] 
            data = os.read(self.stdin.fileno(), length)
            obj = pickle.loads(data)
            method = obj["method_id"]
            args = obj["args"]
            kwargs = obj["kwargs"]
            self.registered_method_table[method](*args, **kwargs)

