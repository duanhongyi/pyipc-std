import os
import struct
import time
import logging
import pickle
import select
import threading
import queue

logger = logging.getLogger(__name__)

class StdClient(object):

    def __init__(self, fd):
        self.registered_method_table = {}
        self.fd = fd
        self.read_fd = None
        self.write_fd = None
        self.lock = threading.RLock()
        self.closed = False

    def register_method(self, method_id, method):
        if self.closed:
            raise ValueError("Connection is close.")
        self.registered_method_table[method_id] = method

    def call_method(self, method_id, *args, **kwargs):
        if not self.read_fd or not self.write_fd:
            raise ValueError("Not connect fd %s" % self.fd)
        if self.closed:
            raise ValueError("Connection is close.")
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
    
    def _connect_fd(self):
        self.read_fd = os.open("%s.out" % self.fd, os.O_NONBLOCK | os.O_RDONLY)
        self.write_fd = os.open("%s.in" % self.fd, os.O_NONBLOCK | os.O_WRONLY)

    def connect(self):
        if self.closed:
            raise ValueError("Connection is close.")
        t1 = threading.Thread(target=self._read_task)
        t1.setDaemon(True)
        t1.start()

    def close(self):
        try:
            if self.read_fd:
                os.close(self.read_fd)
                del self.read_fd
            if self.write_fd:
                os.close(self.write_fd)
                del self.write_fd
        except:
            pass
        self.closed = True
    
    def __del__(self):
        self.close()


    def _read_task(self):
        while not self.closed:
            try:
                self._connect_fd()
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
                    method_id = obj["method_id"]
                    args = obj["args"]
                    kwargs = obj["kwargs"]
                    self.registered_method_table[method_id](*args, **kwargs)
            except BaseException as e:
                logger.exception(e)
            time.sleep(1)
