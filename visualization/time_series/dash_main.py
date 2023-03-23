import datetime
import logging
from queue import Queue

import numpy as np
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from pathos.threading import ThreadPool as Pool

from src.utils import call_wrapper

LOGGER = logging.getLogger(__name__)


def main():
    q: Queue = Queue()

    def update_from_broker(data: np.ndarray, sampling_frequency: float, timestamp: int):
        nonlocal q
        try:
            df = pd.DataFrame(data, [f"microphone {x}" for x in range(min(data.shape))])
            q.put(df)
        except Exception as err:
            LOGGER.error("Error: %s" % err)

    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
    app = Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(
        html.Div(
            [
                html.H4("Live time series update"),
                dcc.Graph(id="live-update-graph"),
                dcc.Interval(
                    id="interval-component",
                    interval=1 * 1000,  # in milliseconds
                    n_intervals=0,
                ),
            ]
        )
    )

    cache = None

    @app.callback(
        Output("live-update-graph", "children"),
        Input("interval-component", "n_intervals"),
    )
    def update_graph(n):
        nonlocal q, cache
        value = q.get()
        if value is not None:
            cache = value
        return cache

    app.run(debug=True)

    func_list = [[lambda: app.run(debug=True), ()], [update_from_broker, ()]]
    funcs, args = zip(*func_list)
    with Pool() as pool:
        pool.map(call_wrapper, funcs, args)


if __name__ == "__main__":
    main()
