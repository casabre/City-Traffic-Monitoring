import numpy as np
import pywt
from typing import Tuple


def scales_to_frequencies(
    scale: float, wavelet: str, sampling_rate: int
) -> Tuple[float, float]:
    # Calculate the frequency range for a given scale and wavelet
    wavelet_obj = pywt.Wavelet(wavelet)
    frequency_range = wavelet_obj.frequency_response(sampling_rate=sampling_rate)
    frequencies = pywt.scale2frequency(
        wavelet, scale, frequency_range=frequency_range, sampling_rate=sampling_rate
    )

    # Convert the frequencies to a tuple representing the frequency range of the scale
    return frequencies[0], np.mean(frequencies), frequencies[1]
