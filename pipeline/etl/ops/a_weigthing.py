import numpy as np
from dagster import get_dagster_logger, op

from .a_weighting_helper.A_weighting import A_weight


@op
def a_weighting(context, signal: np.ndarray, fs: int) -> float:
    """Calculate the dBFS A-weighted RMS value.

    Args:
    audio_signal (np.ndarray): The input audio signal as a multi-dimensional numpy array.
    fs (float): The sampling frequency of the audio signal.

    Returns:
    float: The RMS A-weighting dB value of the audio signal.

    Found under https://stackoverflow.com/a/74446976/18168710
    License: https://creativecommons.org/licenses/by-sa/4.0/
    """
    weighted_signal = A_weight(signal, fs)
    rms_value = np.sqrt(np.mean(np.abs(weighted_signal) ** 2))
    result = 20 * np.log10(rms_value)
    context.log.debug(f"A-weighting: {result} dBFS")
    return result
