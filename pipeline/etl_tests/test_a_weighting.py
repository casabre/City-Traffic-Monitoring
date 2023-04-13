import numpy as np
from dagster import build_op_context
from etl.ops.a_weigthing import a_weighting


def test_rms_a_weighting_db():
    context = build_op_context()
    # Generate a test signal (2 seconds of white noise at 44100 Hz)
    fs = 44100
    duration = 2
    test_signal = np.random.randn(fs * duration)

    # Compute the expected RMS A-weighting dB value using MATLAB's "A-weighted RMS level" function
    expected_rms_db = -3.3

    # Compute the actual RMS A-weighting dB value using the rms_a_weighting_db function
    actual_rms_db = a_weighting(context, test_signal, fs)

    # Compare the expected and actual RMS A-weighting dB values
    np.testing.assert_allclose(actual_rms_db, expected_rms_db, rtol=1e-1, atol=1e-3)
