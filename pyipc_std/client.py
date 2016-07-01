import struct
import time
import logger
import pickle
import threading
import socket
import queue

logger = logging.getLogger(__name__)

class StdClient(object):

    def __init__(self, fd):
        self.registered_method_table = {}
        self.fd = fd
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(None)
        self.lock = threading.RLock()
        self.is_closed = False

    def register_method(self, method_id, method):
        if self.is_closed:
            raise socket.error("Connection closed.")
        self.registered_method_table[method_id] = method

    def call_method(self, method_id, *args, **kwargs):
        if self.is_closed:
            raise socket.error("Connection closed.")
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
        if self.is_closed:
            raise socket.error("Connection closed.")
        t1 = threading.Thread(target=self._read_task)
        t1.setDaemon(True)
        t1.start()

    def close(self):
        self.is_closed = True
        self.sock.close()
    
    def __del__(self):
        self.close()


    def _read_task(self):
        try:
            self.sock.connect(self.fd)
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
        except FileNotFoundError as e:
            logger.exception(e)
            time.sleep(5)
        finally:
            if not self.is_closed:
                self.connect()
