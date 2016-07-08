import os
import logging
import pickle
import struct
import select
import threading


logger = logging.getLogger(__name__)

class StdServer(object):

    def __init__(self, fd):
        self.registered_method_table = {}

        read_file = "%s.in" % fd
        if os.path.exists(read_file):  
            os.unlink(read_file) 
        os.mkfifo(read_file)
        self.read_fd = os.open(read_file, os.O_NONBLOCK | os.O_RDONLY)

        write_file = "%s.out" % fd
        if os.path.exists(write_file):  
            os.unlink(write_file) 
        os.mkfifo(write_file)
        self.write_fd = os.open(write_file, os.O_NONBLOCK | os.O_RDWR)

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
            os.write(self.write_fd, struct.pack('i', len(data)))
            os.write(self.write_fd, data)
        finally:
            self.lock.release()


    def serve_forever(self):
        while True:
            if not select.select([self.read_fd,],[],[], 99)[0]:
                continue
            buff = os.read(self.read_fd, 4)
            if not buff:
                break
            length = struct.unpack('i', buff)[0] 
            if not select.select([self.read_fd,],[],[], 1)[0]:
                break
            buff = os.read(self.read_fd, length)
            if not buff or len(buff) != length:
                break
            obj = pickle.loads(buff)
            method = obj["method_id"]
            args = obj["args"]
            kwargs = obj["kwargs"]
            self.registered_method_table[method](*args, **kwargs)

    def close(self):
        os.close(self.read_fd)
        os.close(self.write_fd)
    
    def __del__(self):
        self.close()
