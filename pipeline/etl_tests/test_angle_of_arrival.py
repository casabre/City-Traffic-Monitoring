from dagster import build_op_context
import numpy as np
from typing import Tuple
from etl.ops.angle_of_arrival import angle_of_arrival


def test_angle_of_arrival():
    # For a detailed explanation see https://pysdr.org/content/doa.html
    context = build_op_context()
    sample_rate = 1e6
    number_of_samples = 10000
    time = np.arange(number_of_samples) / sample_rate
    signal_frequency = 0.02e6
    received_signal = np.asmatrix(np.exp(2j * np.pi * signal_frequency * time))
    mic_spacing = 0.5
    number_of_antennas = 3
    aoa_theta_in_degrees = 20
    aoa_theta_in_radian = aoa_theta_in_degrees / 180 * np.pi
    array_factor = np.asmatrix(
        np.exp(
            -2j
            * np.pi
            * mic_spacing
            * np.arange(number_of_antennas)
            * np.sin(aoa_theta_in_radian)
        )
    )
    audio_signal = array_factor.T @ received_signal
    actual_angle = angle_of_arrival(context, audio_signal, mic_spacing, 1)

    # Test equality within certain tolerance
    assert np.isclose(aoa_theta_in_degrees, actual_angle, rtol=0.01)
