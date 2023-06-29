# Tailscale Local API

This library can be used to control and get information from Tailscaled's local socket API.

It is not a Tailscale SaaS API library.

## Usage

```python
ts = TailscaleAPI.v0()

ts.connect()
ts.set_exit_node("hostname")

peer1 = ts.peer("hostname")
print(peer1.ip_address)

for peer in ts.peers():
  print(peer.ip_address)
```
