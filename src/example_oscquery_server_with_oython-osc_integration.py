import logging

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from tinyoscquery.osc_query_service import OSCQueryService
from tinyoscquery.pythonosc_callback_wrapper import map_node
from tinyoscquery.shared.osc_access import OSCAccess
from tinyoscquery.shared.osc_namespace import OSCNamespace
from tinyoscquery.shared.osc_path_node import OSCPathNode


def generic_handler(address, *args, **kwargs):
    logging.debug(
        f"Default handler called with address {address} and args {args}, kwargs {kwargs}"
    )


if __name__ == "__main__":
    osc_namespace = OSCNamespace()

    dispatcher = Dispatcher()

    node = OSCPathNode(
        "/testing/is/cool",
        value=99,
        access=OSCAccess.READWRITE_VALUE,
        description="Read/write int value",
    )

    map_node(node, dispatcher, generic_handler, namespace=osc_namespace)

    node = OSCPathNode(
        "/testing/is/good", value=False, access=OSCAccess.READWRITE_VALUE
    )

    map_node(node, dispatcher, generic_handler, namespace=osc_namespace)

    oscqs = OSCQueryService(osc_namespace, "Test-Service", 9020, 9020)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("OSCQuery Server is up and serving namespace %s", osc_namespace)

    ip = "127.0.0.1"
    port = 1337
    server = BlockingOSCUDPServer((ip, port), dispatcher)
    server.serve_forever()
