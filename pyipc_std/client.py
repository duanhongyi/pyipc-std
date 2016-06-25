import struct
import pickle
import threading
from subprocess import Popen, PIPE


class StdClient(object):

    def __init__(self, command):
        self.registered_method_table = {}
        self.is_running = False
        self.subprocess = Popen(command, stdin=PIPE, stdout=PIPE) 

    def register_method(self, method_id, method):
        self.registered_method_table[method_id] = method

    def call_method(self, method_id, *args, **kwargs):
        data = pickle.dumps({
            "method_id": method_id,
            "args": args,
            "kwargs": kwargs,
        })
        self.subprocess.stdin.write(struct.pack('i', len(data)))
        self.subprocess.stdin.write(data)
        self.subprocess.stdin.flush()


    def start(self):
        self.is_running = True
        t = threading.Thread(target=self._read_task)
        t.setDaemon(True)
        t.start()

    def close(self):
        self.is_running = False
        self.subprocess.terminate()
    
    def __del__(self):
        self.close()


    def _read_task(self):
        while self.is_running:
            length = struct.unpack('i', self.subprocess.stdout.read(4))[0]
            data = self.subprocess.stdout.read(length)
            obj = pickle.loads(data)
            method_id = obj["method_id"]
            args = obj["args"]
            kwargs = obj["kwargs"]
            self.registered_method_table[method_id](*args, **kwargs)
