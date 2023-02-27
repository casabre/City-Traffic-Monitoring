from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("broker.consumer")
except PackageNotFoundError:
    # package is not installed
    pass

import typing

try:
    from broker.nats import NatsClient as Client
except ImportError:
    from broker.amqp import AmqpClient as Client

import asyncio
import base64
import functools
import json as pickle
import zlib

import cbor2
import numpy as np
from broker.service_interface.utility import to_async

HANDLES = {}


def consume(url: str, topic: str = "sensor.data", **options):
    def wrapper(func):
        client = HANDLES.get("client")
        if not client:
            client = Client(url, **options)
            HANDLES["client"] = client

        @client.on(topic=topic)
        async def _(data: bytes) -> None:
            extracted = await extract_content(data)
            if not extracted:
                return
            stream, sampling_rate = extracted
            await func(stream, sampling_rate)

        def inner_wrapper(*args, **kwargs):
            raise RuntimeError(
                f"Function {func.__name__} already consumed. "
                f"Don't call it directly anymore."
            )

        return inner_wrapper

    return wrapper


async def extract_content(
    body: bytes,
) -> typing.Optional[typing.Tuple[np.ndarray, float]]:
    data = await to_async(pickle.loads, body)
    if "audio" not in data.get("n"):
        return None
    return await extract_raw_stream(data)


async def extract_raw_stream(data: dict) -> typing.Tuple[np.ndarray, float]:
    decoded = base64.b64decode(data["vd"])
    serde = zlib.decompress(decoded)
    audio_raw = cbor2.loads(serde)
    sampling_rate = audio_raw["sr"]
    raw = np.array(audio_raw["r"]["data"]).reshape(audio_raw["r"]["dim"])
    return raw, sampling_rate


async def run():
    c = HANDLES.get("client")
    if not c:
        raise Exception("Client not available.")
    await c.start()
    while True:
        await asyncio.sleep(1)


__all__ = ["__version__", "run", "consume"]
