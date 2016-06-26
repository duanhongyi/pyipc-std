import struct
import pickle
import threading
import socket
import queue


class StdClient(object):

    def __init__(self, fd):
        self.registered_method_table = {}
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(None)
        self.lock = threading.RLock()

    def register_method(self, method_id, method):
        self.registered_method_table[method_id] = method

    def call_method(self, method_id, *args, **kwargs):
        try:
            self.lock.acquire()
            data = pickle.dumps({
                "method_id": method_id,
                "args": args,
                "kwargs": kwargs,
            })
            self.sock.sendall(struct.pack('i', len(data)))
            self.sock.sendall(data)
        finally:
            self.lock.release()

    def connect(self):
        self.sock.connect()
        t1 = threading.Thread(target=self._read_task)
        t1.setDaemon(True)
        t1.start()

    def close(self):
        self.sock.close()
    
    def __del__(self):
        self.close()


    def _read_task(self):
        while True:
            buffer = self.sock.recv(4)
            if not buffer:
                break
            length = struct.unpack('i', buffer)[0]
            buffer = self.sock.recv(length)
            if not buffer or len(buffer) != length:
                break
            obj = pickle.loads(buffer)
            method_id = obj["method_id"]
            args = obj["args"]
            kwargs = obj["kwargs"]
            self.registered_method_table[method_id](*args, **kwargs)
