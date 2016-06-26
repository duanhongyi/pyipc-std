import os
import queue
import logging
import pickle
import struct
import socket
import threading


logger = logging.getLogger(__name__)

class StdServer(object):

    def __init__(self, fd):
        self.registered_method_table = {}
        if os.path.exists(fd):  
            os.unlink(fd) 
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(fd)     
        self.server.listen(5) 
        self.sock = None
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


    def serve_forever(self):
        while True:
            self.sock, _ = self.server.accept()
            try:
                while True:
                    buffer = self.sock.recv(4)
                    if not buffer:
                        break
                    length = struct.unpack('i', buffer)[0] 
                    buffer = self.sock.recv(length)
                    if not buffer or len(buffer) != length:
                        break
                    obj = pickle.loads(buffer)
                    method = obj["method_id"]
                    args = obj["args"]
                    kwargs = obj["kwargs"]
                    self.registered_method_table[method](*args, **kwargs)
            finally:
                self.sock.close()

    def close(self):
        self.server.close()
    
    def __del__(self):
        self.close()
