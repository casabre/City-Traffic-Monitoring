from dagster import Definitions

from .jobs.extract_audio import extract_audio
from .sensor.listen_broker import listen_rabbitmq, broker_resource


defs = Definitions(
    jobs=[extract_audio],
    sensors=[listen_rabbitmq],
    resources={"broker": broker_resource},
)
