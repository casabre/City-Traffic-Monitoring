import abc
import logging
import typing


class ServiceInterface(abc.ABC):
    def __init__(self, url, auth: typing.Optional[dict] = None, logger=None):
        self.url = url
        self.auth = auth
        self.logger = logger or logging.getLogger()
        self.consumers = []

    def _add_consumer(self, routing_key, on_message):
        self.consumers.append({routing_key: routing_key, on_message: on_message})

    def on(self, topic):
        def wrap(async_fn):
            self._add_consumer(routing_key=topic, on_message=async_fn)
            return async_fn

        return wrap

    @abc.abstractmethod
    async def publish(self, topic, body: bytes):
        pass

    @abc.abstractmethod
    async def _connect(self):
        pass

    @abc.abstractmethod
    async def _process_message(self, message, on_message):
        pass

    @abc.abstractmethod
    async def start(self):
        pass
