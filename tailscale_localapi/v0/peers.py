from requests import Session
from requests.exceptions import ConnectionError
from typing import List

from tailscale_localapi._util.error import TailscaleException


class Peer:
    node_key: str
    connected: bool
    active: bool
    online: bool
    hostname: str
    dns_name: str
    ip_address: str
    ip_addresses: List[str] = []

    can_be_exit_node: bool
    exit_node: bool

    @classmethod
    def from_json(cls, obj):
        peer = Peer()
        peer.node_key = obj["PublicKey"]
        peer.id = obj["ID"]
        peer.hostname = obj["HostName"]
        peer.dns_name = obj["DNSName"]

        if len(obj["TailscaleIPs"]) > 0:
            peer.ip_address = obj["TailscaleIPs"][0]
            peer.ip_addresses = [ip for ip in obj["TailscaleIPs"] if ip != peer.ip_address]

        peer.user_id = obj["UserID"]

        peer.os = obj["OS"]

        peer.active = obj["Active"]
        peer.online = obj["Online"]
        peer.can_be_exit_node = obj["ExitNodeOption"]
        peer.exit_node = obj["ExitNode"]

        return peer

    def __str__(self) -> str:
        return f"Peer[{self.hostname} ({self.dns_name}/{self.ip_address})]"

    @classmethod
    def get(cls, client: Session, hostname: str):
        return next(filter(lambda peer: peer.hostname == hostname, Self.peers(client)), None)


class Self:
    @classmethod
    def from_json(cls, obj):
        return Peer.from_json(obj["Self"])

    @classmethod
    def status(cls, client: Session):
        try:
            response = client.get("http://ts/localapi/v0/status")

            if response.status_code != 200:
                raise TailscaleException.from_status_code(response.status_code, response.text)

            return Self.from_json(response.json())
        except ConnectionError:
            raise TailscaleException.connection_error()

    @classmethod
    def peers(cls, client: Session):
        try:
            response = client.get("http://ts/localapi/v0/status")

            if response.status_code != 200:
                raise TailscaleException.from_status_code(response.status_code, response.text)

            return Peers.from_json(response.json())
        except ConnectionError:
            raise TailscaleException.connection_error()


class Peers:
    @classmethod
    def from_json(cls, obj):
        return [Peer.from_json(peer) for peer in obj["Peer"].values()]
