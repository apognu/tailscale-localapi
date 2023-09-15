import requests

from typing import List, Optional

from tailscale_localapi.v0.config import Config
from tailscale_localapi.v0.peers import Self, Peer
from tailscale_localapi._util.sock import SockAdapter
from tailscale_localapi._util.error import TailscaleException


class API_V0:
    """Handle to Tailscale's local API"""

    _client: requests.Session = requests.Session()
    _socket_path: str

    def __init__(self, *, socket_path: str = "/run/tailscale/tailscaled.sock"):
        """
        Creates a handle to Tailscale's local API, through the path to
        `tailscaled` UNIX socket.
        """

        self._client.mount("http://ts/", SockAdapter())
        self._socket_path = socket_path

    def is_connected(self) -> bool:
        """
        Get the state of the Tailscale connection.

        Returns:
            A boolean indicating whether the current host is online.
        """

        return Self.status(self._client).online

    def connect(self):
        """Sets the status of the connection to up."""

        Config.set_preference(self._client, "WantRunning", True)

    def disconnect(self):
        """Sets the status of the connection to down."""

        Config.set_preference(self._client, "WantRunning", False)

    def self(self) -> Peer:
        """
        Get the status of the current node in the Tailnet.

        Returns:
            A peer status for the current host.
        """

        return Self.status(self._client)

    def peers(self) -> List[Peer]:
        """
        Get the list of peer devices in the Tailnet and their status.

        Returns:
            A list of peer configuration added to the tailnet.
        """

        return Self.peers(self._client)

    def peer(self, hostname: str) -> Optional[Peer]:
        """
        Looks for a peer device with its hostname and, if found, returns its
        status.

        Args:
            hostname (str):
                The `hostname` for the peer you want to retrieve the status.

        Returns:
            The status for the requested peer, or `None` if it was not found.
        """

        return Peer.get(self._client, hostname)

    def config(self) -> Config:
        """
        Get the current node's configuration.

        Returns:
            The list of settings for the current node.
        """

        return Config.get(self._client)

    def set_exit_node(self, hostname: Optional[str], allow_lan: bool = False) -> None:
        """
        Enables routing through an exit node through its hostname.

        The provided peer device should be configured to act as an exit node,
        otherwise this method will raise.

        Args:
            hostname (str):
                The `hostname` for the peer you wish to use as an exit node, or
                `None` to disable the existing exit node.
        """

        exit_node_id = ""

        if hostname is not None:
            peer = self.peer(hostname)

            if peer is None:
                raise TailscaleException.other(f"host `{hostname}` not found on the tailnet")
            if not peer.can_be_exit_node:
                raise TailscaleException.other(f"host `{hostname}` cannot be used as an exit node")

            exit_node_id = peer.id

        Config.set_preference(self._client, "ExitNodeID", exit_node_id)
        Config.set_preference(self._client, "ExitNodeAllowLANAccess", allow_lan)

    def unset_exit_node(self):
        """Disables routing through the exit node."""

        self.set_exit_node(None)

    def set_routes(self, routes: List[str]):
        """
        Sets the list of routes advertised by the current node.

        Returns:
            A list of CIDR subnets this nodes advertises as routes.
        """

        Config.set_preference(self._client, "AdvertiseRoutes", routes)
