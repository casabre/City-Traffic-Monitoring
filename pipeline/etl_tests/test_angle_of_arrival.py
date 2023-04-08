import numpy as np
from typing import Tuple
from etl.ops.angle_of_arrival import angle_of_arrival


def test_angle_of_arrival():
    # Generate a test audio signal and compute the expected angle of arrival
    n_mics = 8
    n_samples = 1024
    sample_rate = 48000
    spacing = 0.05
    angle = 30
    delay = spacing * np.sin(angle * np.pi / 180) / 343
    t = np.arange(n_samples) / sample_rate
    audio_array = np.zeros((n_mics, n_samples))
    for i in range(n_mics):
        audio_array[i, :] = np.sin(
            2 * np.pi * (i * spacing * np.sin(angle * np.pi / 180) / 343 + delay) * t
        )
    expected_angle = angle

    # Compute the actual angle of arrival using the angle_of_arrival function
    actual_angle, actual_delay = angle_of_arrival(audio_array, sample_rate, spacing)

    # Check that the actual angle of arrival is close to the expected angle of arrival
    assert np.isclose(actual_angle, expected_angle, rtol=1e-2)

    # Check that the actual delay is close to the expected delay
    assert np.isclose(actual_delay, delay, rtol=1e-6)
