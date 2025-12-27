# tinyoscquery

A very simple, work in progress, OSCQuery library for python.

**THIS IS A WORK IN PROGRESS**

The [core functionality](https://github.com/Vidvox/OSCQueryProposal?tab=readme-ov-file#core-functionality) (according to
the specification) should be implemented.
Some [optional attributes](https://github.com/Vidvox/OSCQueryProposal?tab=readme-ov-file#optional-attributes) like
ACCESS, VALUE and DESCRIPTION are also implemented. However, lists (or other python
iterables) are not supported as value types.

Completely missing is the websocket communication. So no "listening" is possible.

### **NB: The following documentation is outdated.**

## Installation

1. Clone this repo
2. Run `pip install ./` in this repo folder

## Usage

### Advertising an OSCQuery Service

To register a OSCQuery Service, simply construct a `OSCQueryService` (in `tinyoscquery.queryservice`) object with a
name, and desired port numbers. The HTTP oscjson server and zeroconf advertisements will automataically start.

```Python
from tinyoscquery import OSCQueryService
import time

osc_port = 9020  # Find a predefined open port for OSC
http_port = 9020  # Find a predefined open port for the oscjson http server -- can be the same port as osc

# Set up an OSCServer, likely with the python-osc first...

oscqs = OSCQueryService("Test-Service", http_port, osc_port)

# Do something else, the zeroconf advertising and oscjson server runs in the background
while True:
    time.sleep(1)

```

If you want to select any open ports on the system to use, a port finder is provided in the `tinyoscquery.utility`
package.

```Python
from tinyoscquery import OSCQueryService
from tinyoscquery import get_open_tcp_port, get_open_udp_port
import time

osc_port = get_open_udp_port()  # Find a random open port for OSC
http_port = get_open_tcp_port()  # Find a random open port for the oscjson http server -- can be the same port as osc

# Set up an OSCServer, likely with the python-osc first...

oscqs = OSCQueryService("Test-Service", http_port, osc_port)

# Do something else, the zeroconf advertising and oscjson server runs in the background
while True:
    time.sleep(1)

```

### Discovering and Querying other OSCQuery Services

To find other OSCQuery Services and read host info, utilize the `tinyoscquery.query` package to make a `OSCQueryBrowser`
instance, wait for discovery, and then use `OSCQueryClient` to evaluate the HOST_INFO.

```python
import time

from tinyoscquery import OSCQueryClient
from tinyoscquery import OSCQueryBrowser

browser = OSCQueryBrowser()
time.sleep(2)  # Wait for discovery

for service_info in browser.get_discovered_oscquery():
    client = OSCQueryClient(service_info)

    # Find host info
    host_info = client.get_host_info()
    print(f"Found OSC Host: {host_info.name} with ip {host_info.osc_ip}:{host_info.osc_port}")

    # Query a node and print its value
    node = client.query_node("/test/node")
    print(f"Node is a {node.type_} with value {node.value}")
```

## Project To-Do

- [x] Advertise osc and oscjson on zeroconfig
- [x] Provide a basic oscjson server with a root node and HOST_INFO
- [X] Add a mechanism to advertise OSC nodes
- [ ] Use the configured OSC namespace to validate incoming OSC message (from another library?)
- [ ] Add a mechanism to update OSC nodes with new values
- [X] Add apis and tools to query other OSC services on the network
- [ ] Add websocket communication as per spec
- [ ] Add more documentation
- [ ] Add tests
- [ ] Finalize API design