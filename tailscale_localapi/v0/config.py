import json

from requests import Session
from typing import List, Any

from tailscale_localapi._util.error import TailscaleException


class Node:
    id: int


class User:
    id: int
    username: str
    name: str


class Config:
    control_url: str

    up: bool

    accept_wildcard_route: bool
    advertise_routes: List[str]
    advertise_tags: List[str]

    exit_node_id: int
    exit_node_ip: str

    user: User

    @classmethod
    def from_json(cls, obj):
        config = Config()

        config.control_url = obj["ControlURL"]

        config.up = obj["WantRunning"]

        config.accept_wildcard_route = obj["RouteAll"]
        config.advertise_routes = obj["AdvertiseRoutes"]
        config.advertise_tags = obj["AdvertiseTags"]

        config.exit_node_id = obj["ExitNodeID"]
        config.exit_node_ip = obj["ExitNodeIP"]

        config.user = User()
        config.user.id = obj["Config"]["UserProfile"]["ID"]
        config.user.username = obj["Config"]["UserProfile"]["LoginName"]
        config.user.name = obj["Config"]["UserProfile"]["DisplayName"]

        config.node = Node()
        config.node.id = obj["Config"]["NodeID"]

        return config

    @classmethod
    def get(cls, client: Session):
        response = client.get("http://ts/localapi/v0/prefs")

        if response.status_code != 200:
            raise TailscaleException(f"api error ({response.status_code}): {response.text}")

        return Config.from_json(response.json())

    @classmethod
    def set_preference(cls, client: Session, key: str, value: Any):
        body = {
            f"{key}Set": True,
            key: value,
        }

        response = client.patch("http://ts/localapi/v0/prefs", data=json.dumps(body))

        if response.status_code != 200:
            raise TailscaleException(f"api error ({response.status_code}): {response.text}")
