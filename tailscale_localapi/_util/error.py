from enum import Enum


class TailscaleError(Enum):
    OTHER = 0
    CONNECTION_ERROR = 1
    UNAUTHORIZED = 2
    HTTP_ERROR = 3


class TailscaleException(Exception):
    error: TailscaleError
    message: str

    def __init__(self, error: TailscaleError, message: str):
        self.error = error
        self.message = message

    def connection_error():
        return TailscaleException(TailscaleError.CONNECTION_ERROR, "could not connect to Tailscale socket")

    def from_status_code(code: int, message: str = ""):
        if code == 401:
            return TailscaleException(TailscaleError.UNAUTHORIZED, "unauthorized API access, try running as root")
        else:
            return TailscaleException(TailscaleError.HTTP_ERROR, f"got unexpected HTTP status code: ${code}: ${message}")

    def other(message):
        return TailscaleException(TailscaleError.OTHER, message)
