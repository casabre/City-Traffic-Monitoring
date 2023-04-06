import numpy as np
from dagster import get_dagster_logger, op

from .a_weighting_helper.A_weighting import A_weight


@op
def a_weighting(context, signal: np.ndarray, fs: int) -> float:
    """Calculate the dBFS A-weighted RMS value.

    Found under https://stackoverflow.com/a/74446976/18168710
    License: https://creativecommons.org/licenses/by-sa/4.0/
    """
    weighted_signal = A_weight(signal, fs)
    rms_value = np.sqrt(np.mean(np.abs(weighted_signal) ** 2))
    result = 20 * np.log10(rms_value)
    context.log.info(f"A-weighting: {result} dBFS")
    return result
