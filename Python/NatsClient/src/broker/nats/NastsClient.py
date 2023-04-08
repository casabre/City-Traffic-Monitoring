import asyncio
import functools
import typing

import nats
from broker.service_interface import ServiceInterface


class NatsClient(ServiceInterface):
    def __init__(self, url, auth: typing.Optional[dict] = None, logger=None, **kwargs):
        super().__init__(url, auth, logger)
        self.connection: typing.Optional[nats.Client] = None
        self.subscription: dict = {}

    async def publish(self, topic, body: bytes):
        while self.connection is None:
            self.logger.warning("Publish waiting for NATS connection...")
            await asyncio.sleep(delay=1)
        await self.connection(nats.Message(body=body), routing_key=topic)

    async def _connect(self):
        while True:
            try:
                kwargs = {"servers": self.url}
                if self.auth is not None:
                    kwargs["login"] = self.auth.get("user", "guest")
                    kwargs["password"] = self.auth.get("password", "guest")
                return await nats.connect(**kwargs)
            except Exception as e:
                self.logger.warning(f"Retrying connection to NATS server: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, message, on_message):
        await on_message(message.data)

    async def start(self):
        try:
            self.logger.info(f"Connecting to NATS server...")
            connection = await self._connect()
            self.logger.info(f"Successfully connected to NATS server")
            for routing_key, on_message in self.consumers:
                queue_name = routing_key.replace("*", "_")
                self.logger.warning(f"Creating queue: {queue_name}")
                self.subscription.update(
                    {
                        queue_name: await connection.subscribe(
                            routing_key,
                            cb=functools.partial(
                                self._process_message, on_message=on_message
                            ),
                        )
                    }
                )
        except Exception as e:
            self.logger.exception(f"Errored starting NATS consumers: {e}")
        self.connection = connection
