import asyncio
import functools
import logging
import typing

import aio_pika
from broker.service_interface import ServiceInterface


class AmqpClient(ServiceInterface):
    def __init__(self, url, exchange, auth: typing.Optional[dict] = None, logger=None):
        super().__init__(url, auth, logger)
        self.exchange_name = exchange
        self.connection: typing.Optional[aio_pika.Connection] = None
        self.channel: typing.Optional[aio_pika.Channel] = None

    async def publish(self, topic, body):
        while self.connection is None:
            self.logger.warning("Publish waiting for AMQP connection...")
            await asyncio.sleep(delay=1)
        exchange = await typing.cast(aio_pika.Channel, self.channel).get_exchange(
            self.exchange_name
        )
        await exchange.publish(aio_pika.Message(body=body), routing_key=topic)

    async def _connect(self):
        while True:
            try:
                kwargs = {"url": self.url}
                if self.auth is not None:
                    kwargs["login"] = self.auth.get("user", "guest")
                    kwargs["password"] = self.auth.get("password", "guest")
                return await aio_pika.connect_robust(**kwargs)
            except Exception as e:
                self.logger.warning(f"Retrying connection to AMQP server: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, message: aio_pika.IncomingMessage, on_message):
        async with message.process():
            await on_message(message.body)

    async def start(self):
        try:
            self.logger.info(f"Connecting to AMQP server...")
            connection = await self._connect()
            self.logger.info(f"Successfully connected to AMQP server")
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                name=self.exchange_name, type="topic", durable=True
            )
            for routing_key, on_message in self.consumers:
                queue_name = routing_key.replace("*", "_")
                self.logger.warning(f"Creating queue: {queue_name}")
                queue = await channel.declare_queue(queue_name)
                await queue.bind(exchange, routing_key)
                await queue.consume(
                    functools.partial(self._process_message, on_message=on_message)
                )
        except Exception as e:
            self.logger.exception(f"Errored starting AMQP consumers: {e}")
        self.connection = connection
        self.channel = channel
