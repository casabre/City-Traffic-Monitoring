import json as pickle
from contextlib import contextmanager
from dagster import DefaultSensorStatus, RunRequest, sensor, resource
from ..jobs.extract_audio import extract_audio


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
    import uuid
    import time

    # todo: use real data from broker here
    data = {"n": f"sensor_audio_{uuid.uuid4()}", "vd": "", "t": time.time()}
    # data = pickle.loads(body)
    if "audio" not in data.get("n"):
        return
    yield RunRequest(
        run_key=data.get("n"),
        run_config={"ops": {"extract_senml": {"config": {"data": data}}}},
    )
