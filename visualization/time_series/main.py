import asyncio
import logging
import typing
from queue import Empty, Queue

from threading import Thread

import numpy as np

from broker.consumer import consume, run
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


LOGGER = logging.getLogger(__name__)
q: Queue = Queue()
cache: typing.Optional[np.ndarray] = None
MULTYPlIER = 8
SAMPLES = 16384
CHANNELS = 4


def test_data(q: Queue):
    import time

    sampling_rate = 16384
    timestamp = time.time()
    while True:
        try:
            df = {
                "data": np.random.random_sample((sampling_rate, 2)),
                "fs": sampling_rate,
                "timestamp": timestamp,
            }
            q.put(df)
            time.sleep(1)
        except Exception as err:
            LOGGER.error("Error: %s" % err)


def create_broker(q: Queue):
    @consume(
        topic="sensor.data",
        url="amqp://broker.sctmp.ai:5672",
        auth={"user": "guest", "password": "guest"},
        exchange="amq.topic",
    )
    async def on(stream: np.ndarray, sampling_rate: float, timestamp: int) -> None:
        nonlocal q
        try:
            df = {"data": stream, "fs": sampling_rate, "timestamp": timestamp}
            q.put(df)
        except Exception as err:
            LOGGER.error("Error: %s" % err)

    asyncio.run(run())


# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
external_stylesheets = []
app = Dash(__name__)  # , external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.layout = html.Div(
    html.Div(
        [
            html.H4("Live time series update"),
            dcc.Graph(id="live-update-graph", animate=True),
            dcc.Interval(
                id="interval-component",
                interval=1 * 1000,  # in milliseconds
                n_intervals=0,
            ),
        ]
    )
)


@app.callback(
    Output("live-update-graph", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_graph(n_intervals):
    global q, cache
    try:
        value = q.get(timeout=0)
    except Empty:
        value = None

    if cache is None:
        if value is not None:
            rows = MULTYPlIER * value["data"].shape[0]
            columns = value["data"].shape[1]
        else:
            rows = MULTYPlIER * SAMPLES
            columns = CHANNELS
        cache = -1 * np.ones((rows, columns))
    if value is not None:
        update_count = np.max(value["data"].shape)
        cache[:-update_count, :] = cache[update_count:, :]
        if value["data"].shape[0] > value["data"].shape[1]:
            cache[-update_count:, : value["data"].shape[1]] = value["data"]
        else:
            cache[-update_count:, : value["data"].shape[0]] = value["data"].tranpose()
    minimum = np.min(cache)
    maximum = np.max(cache)
    rows = cache.shape[0]
    columns = cache.shape[1]
    x = list(range(rows))
    traces = [
        {
            "x": x,
            "y": cache[:, idx].tolist(),
            "name": f"microphone {idx}",
            "type": "line",
        }
        for idx in range(columns)
    ]
    update = {
        "data": traces,
        "layout": {
            # You need to supply the axes ranges for smooth animations
            "xaxis": {"range": [min(x), max(x)]},
            "yaxis": {"range": [minimum, maximum]},
            "transition": {"duration": 500, "easing": "cubic-in-out"},
        },
    }
    return update


if __name__ == "__main__":
    Thread(target=create_broker, args=(q,)).start()
    app.run(debug=True)
