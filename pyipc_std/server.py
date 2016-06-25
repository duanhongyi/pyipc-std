import os
import sys
import logging
import pickle
import struct
import threading


logger = logging.getLogger(__name__)

class StdServer(object):

    def __init__(self):
        self.registered_method_table = {}
        self.stdin = sys.stdin
        self.stdout = sys.stdout
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
        while True:
            try:
                length = struct.unpack('i', os.read(self.stdin.fileno(), 4))[0] 
                data = os.read(self.stdin.fileno(), length)
                obj = pickle.loads(data)
                method = obj["method_id"]
                args = obj["args"]
                kwargs = obj["kwargs"]
                self.registered_method_table[method](*args, **kwargs)
            except struct.error as e:
                logger.debug(e)
                break

    def close(self):
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
        self.stdin.close()
        self.stdout.close()
    
    def __del__(self):
        self.close()

    def _patch_std(self):
        sys.stdin = open("/var/log/pyipc-std.in", "w")
        sys.stdout = open("/var/log/pyipc-std.out", "w")
        sys.stderr = open("/var/log/pyipc-std.err", "w")
