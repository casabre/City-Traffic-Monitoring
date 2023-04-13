import base64
import json as pickle
import typing
import zlib

import cbor2
import numpy as np
from dagster import Out, op


@op(config_schema={"data": dict}, out={"signal": Out(), "fs": Out()})
def extract_senml(context) -> typing.Tuple[np.ndarray, int]:
    """Extract signal and sampling rate from SenML data."""
    data = context.op_config["data"]
    return extract_raw_stream(data)


def extract_raw_stream(data: dict) -> typing.Tuple[np.ndarray, int]:
    """Decode and extract signal and sampling rate."""
    decoded = base64.b64decode(data["vd"])
    serde = zlib.decompress(decoded)
    audio_raw = cbor2.loads(serde)
    sampling_rate = audio_raw["sr"]
    raw = np.array(audio_raw["r"]["data"]).reshape(audio_raw["r"]["dim"])
    return raw, sampling_rate
