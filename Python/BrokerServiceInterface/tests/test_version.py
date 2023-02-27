import re

from broker.service_interface import __version__


def test_version():
    assert re.match(r"[\d.]+", __version__)
