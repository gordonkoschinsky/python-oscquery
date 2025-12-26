import logging

from pythonosc import osc_message_builder
from pythonosc.dispatcher import Dispatcher

logging.basicConfig(level=logging.DEBUG)
from tinyoscquery.osc_handler_wrapper import OSCCallbackWrapper
from tinyoscquery.shared.osc_path_node import OSCPathNode

class TestHandlerWrapper:
    callback_called = False

    def test_callback_wrapper_calls_callback_when_called(self):
        def osc_callback(*args, **kwargs):
            logging.debug(f"osc_callback called with args={args} kwargs={kwargs}")
            self.callback_called = True

        def create_wrapper(address):
            OSCCallbackWrapper(OSCPathNode(address), dispatcher=d, callback=osc_callback)

        address = "/test"
        d = Dispatcher()
        create_wrapper(address)

        for h in d.handlers_for_address(address):
            h.invoke("dummy", osc_message_builder.OscMessageBuilder(address).build())

        assert self.callback_called == True

    def test_callback_wrapper_does_not_call_callback_when_called_with_other_address(self):
        def osc_callback(*args, **kwargs):
            logging.debug(f"osc_callback called with args={args} kwargs={kwargs}")
            self.callback_called = True

        def create_wrapper(address):
            OSCCallbackWrapper(OSCPathNode(address), dispatcher=d, callback=osc_callback)

        address = "/other"
        d = Dispatcher()
        create_wrapper("/test")

        for h in d.handlers_for_address(address):
            h.invoke("dummy", osc_message_builder.OscMessageBuilder(address).build())

        assert self.callback_called == False
