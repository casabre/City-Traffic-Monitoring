import json as pickle
from contextlib import contextmanager
from dagster import DefaultSensorStatus, RunRequest, sensor, resource
from ..jobs.extract_audio import extract_audio
import paho.mqtt.subscribe as subscribe


class BrokerConnection:
    def __init__(self, url: str):
        self.broker = url

    def recv(self) -> dict:
        return {}

    def close(self) -> None:
        self.broker.close()


@resource(config_schema={"connection": str})
@contextmanager
def broker_resource(init_context):
    broker = None
    try:
        connection = init_context.resource_config["connection"]
        broker = BrokerConnection(connection)
        yield broker
    finally:
        if broker is not None:
            broker.close()


@sensor(
    job=extract_audio,
    minimum_interval_seconds=5,
    default_status=DefaultSensorStatus.RUNNING,
)
def listen_rabbitmq():
    msg = subscribe.simple("sensor/data", hostname="mqtt.sctmp.ai", keepalive=2)
    data = pickle.loads(msg.payload)
    if "audio" not in data.get("n"):
        return
    yield RunRequest(
        run_key=data.get("t"),
        run_config={"ops": {"extract_senml": {"config": {"data": data}}}},
    )
