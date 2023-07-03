import socket

SOCK = "%2Frun%2Ftailscale%2Ftailscaled.sock"

from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError

from tailscale_localapi._util.error import TailscaleException


class SockConnection(HTTPConnection):
    def __init__(self):
        super().__init__("local-tailscaled.sock")

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect("/run/tailscale/tailscaled.sock")
        except ConnectionError:
            raise TailscaleException.connection_error()


class SockConnectionPool(HTTPConnectionPool):
    def __init__(self):
        super().__init__("local-tailscaled.sock")

    def _new_conn(self):
        return SockConnection()


class SockAdapter(HTTPAdapter):
    def get_connection(self, url, proxies=None):
        return SockConnectionPool()
