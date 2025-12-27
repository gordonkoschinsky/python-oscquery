import logging
from typing import Any

import pythonosc
from pythonosc.dispatcher import Dispatcher, Handler

from tinyoscquery.shared.osc_namespace import OSCNamespace
from tinyoscquery.shared.osc_path_node import OSCPathNode

logger = logging.getLogger(__name__)


class OSCCallbackWrapper:
    """Wrapper class to type-check python-osc callbacks."""

    def __init__(self, node: OSCPathNode, callback: callable):
        self.node = node
        self.callback = callback
        self.handler: pythonosc.dispatcher.Handler | None = None

    def register_handler(self, handler: pythonosc.dispatcher.Handler):
        self.handler = handler

    def __call__(self, *args, **kwargs):
        logger.debug(
            f"{self.__class__.__name__} {self.node.full_path} called with args={args} kwargs={kwargs}"
        )

        if not self.handler:
            raise TypeError(
                f"{self.__class__.__name__} for {self.node.full_path} has no handler"
            )

        values = args

        if self.handler.needs_reply_address:
            # the osc client address, when required by the callback, is always the first argument. We don't need to check it.
            values = values[1:]

        # the osc message address is always the next argument. We don't need to check it.
        values = values[1:]

        if self.handler.args:
            # fixed parameters, when required by the callback, are always the next argument. We don't need to check them.
            values = values[1:]

        if len(values) != len(self.node.type):
            raise TypeError(
                f"Expected {len(self.node.type)} value(s), got {len(values)} when calling callback {repr(self.callback)} for {self.node.full_path}"
            )

        for i, type_ in enumerate(self.node.type):
            if type(values[i]) is not type_:
                raise TypeError(f"Expected {type_} for value {i}, got {values[i]}")

        return self.callback(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}(address: {self.node.full_path} callback={repr(self.callback)})"


def map_node(
    node: OSCPathNode,
    dispatcher: Dispatcher,
    callback: callable,
    namespace: OSCNamespace | None = None,
    *args: Any | list[Any],
    needs_reply_address: bool = False,
) -> Handler:
    """Map the given callback on the given dispatcher.
    Wraps the callback so that the values can be checked if they match the values from the given node.

    Args:
        node: OSCPathNode to use for type checking
        dispatcher: python-osc dispatcher
        callback: the callback function that is called when the python-osc server receives a matching message
        namespace: When given, adds the node to this namespace for us in the OSCQuery server
        *args: Fixed arguments that will be passed to the callback function
        needs_reply_address: Whether the IP address from which the message originated from shall be passed as
            an argument to the handler callback

    Returns:
        The python-osc handler object that will be invoked should the given address match
    """
    wrapper = OSCCallbackWrapper(node, callback)
    handler = dispatcher.map(
        node.full_path, wrapper, *args, needs_reply_address=needs_reply_address
    )
    wrapper.register_handler(handler)

    if namespace:
        namespace.add_node(node)

    return handler
