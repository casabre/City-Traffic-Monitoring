import typing
from dagster import op
import numpy as np


@op
def angle_of_arrival(
    context,
    audio_array: np.ndarray,
    spacing: float,
    num_expected_signals: typing.Optional[int] = None,
) -> np.ndarray:
    """
    Calculates the angle of arrival of a sound source given an audio signal
    from a linear array of microphones with known spacing.

    For a more detailed explanation see https://pysdr.org/content/doa.html

    Args:
    - audio_array (ndarray): 2D array of shape (n_mics, n_samples) containing the audio signals
      from each microphone.
    - spacing (float): The distance in meters between adjacent microphones in the linear array.
    - num_expected_signal (typing.Optional[int]): Number of the expected signals. Defaults to number of antennas - 1

    Returns:
    - The angle of arrival (in degrees).
    """
    num_antennas, _ = audio_array.shape
    if num_expected_signals is None:
        num_expected_signals = num_antennas - 1
    theta_scan, results = _aoa_music_detector(
        audio_array=audio_array,
        spacing=spacing,
        num_expected_signals=num_expected_signals,
    )
    max_power_indices = _extract_signal_aoa(
        results=results, num_expected_signal=num_expected_signals
    )
    angle = theta_scan[max_power_indices] * 180 / np.pi
    context.log.debug(f"Angle of arrival: {angle} degrees")
    return angle


def _extract_signal_aoa(results: typing.List[float], num_expected_signal: int):
    indices = np.argsort(results)[::-1]
    if num_expected_signal < len(indices):
        indices = indices[:num_expected_signal]
    return indices


def _aoa_music_detector(
    audio_array: np.ndarray,
    spacing: float,
    num_expected_signals: int,
) -> typing.Tuple[np.ndarray, np.ndarray]:
    num_antennas, _ = audio_array.shape
    # part that doesn't change with theta_i
    r = np.asmatrix(audio_array)
    # Calc covariance matrix, it's Nr x Nr
    R = r @ r.H
    # eigenvalue decomposition, v[:,i] is the eigenvector corresponding
    # to the eigenvalue w[i]
    w, v = np.linalg.eig(R)
    # find order of magnitude of eigenvalues
    eig_val_order = np.argsort(np.abs(w))
    # sort eigenvectors using this order
    v = v[:, eig_val_order]
    # We make a new eigenvector matrix representing the "noise subspace",
    # it's just the rest of the eigenvalues
    V = np.asmatrix(
        np.zeros(
            (num_antennas, num_antennas - num_expected_signals), dtype=np.complex64
        )
    )
    for i in range(num_antennas - num_expected_signals):
        V[:, i] = v[:, i]

    theta_scan = np.linspace(-1 * np.pi, np.pi, 1000)  # -180 to +180 degrees
    results = []
    for theta_i in theta_scan:
        a = np.asmatrix(
            np.exp(-2j * np.pi * spacing * np.arange(num_antennas) * np.sin(theta_i))
        )  # array factor
        a = a.T
        metric = 1 / (a.H @ V @ V.H @ a)  # The main MUSIC equation
        metric = np.abs(metric[0, 0])  # take magnitude
        # metric = 10 * np.log10(metric)  # convert to dB
        results.append(metric)

    results /= np.max(results)  # normalize
    return theta_scan, results
