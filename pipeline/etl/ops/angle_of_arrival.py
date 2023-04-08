import numpy as np
from typing import Tuple


def angle_of_arrival(
    audio_array: np.ndarray, sample_rate: float, spacing: float
) -> Tuple[float, float]:
    """
    Calculates the angle of arrival of a sound source given a Hilbert-transformed audio signal
    from a linear array of microphones with known spacing.

    Args:
    - audio_array (ndarray): 2D array of shape (n_mics, n_samples) containing the audio signals
      from each microphone.
    - sample_rate (float): The sampling rate of the audio signal in Hz.
    - spacing (float): The distance in meters between adjacent microphones in the linear array.

    Returns:
    - Tuple containing the angle of arrival (in degrees) and the delay (in seconds) of the sound
      source relative to the first microphone in the array.
    """
    # Compute the Hilbert transform of each microphone signal
    hilbert_array = np.apply_along_axis(
        lambda x: np.abs(np.fft.ifft(np.imag(np.fft.fft(x)))), 1, audio_array
    )

    # Compute the cross-correlation matrix of the Hilbert-transformed signals
    xcorr_matrix = (
        np.dot(hilbert_array, hilbert_array.T.conj()) / hilbert_array.shape[1]
    )

    # Compute the angle of arrival and delay of the sound source
    max_idx = np.unravel_index(np.argmax(np.abs(xcorr_matrix)), xcorr_matrix.shape)
    delay = max_idx[1] / sample_rate
    angle = np.arcsin(max_idx[0] * spacing / delay) * 180 / np.pi

    return angle, delay
