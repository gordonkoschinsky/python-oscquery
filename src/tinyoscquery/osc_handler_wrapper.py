import logging

import pythonosc
from pythonosc.dispatcher import Dispatcher

from tinyoscquery.shared.osc_path_node import OSCPathNode


logger = logging.getLogger(__name__)

class OSCCallbackWrapper:
    def __init__(self, node:OSCPathNode, dispatcher: Dispatcher, callback: callable):
        self.node = node
        self.callback = callback
        self.handler = dispatcher.map(node.full_path, self)

    def __call__(self, *args, **kwargs):
        logger.debug(f"OSCHandlerWrapper {self.node.full_path} called with args={args} kwargs={kwargs}")
        return self.callback(*args, **kwargs)