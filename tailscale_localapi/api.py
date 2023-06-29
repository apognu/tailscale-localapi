"""
Main entrypoint for Tailscale's local API.

This is the class that should be used as a starting point to access a handle to
use this library.
"""

from tailscale_localapi.v0.api import API_V0


class TailscaleAPI:
    @classmethod
    def v0(cls, *, socket_path: str = "/run/tailscale/tailcaled.sock") -> API_V0:
        """
        Obtain a handle to the `v0` API.

        Args:
            socket_path (str):
                The path to the UNIX socket for `tailscaled` on the local
                filesystem.

        Returns:
            The class to access Tailscale's local API v0.
        """

        return API_V0(socket_path=socket_path)
