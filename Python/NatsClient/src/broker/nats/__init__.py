from importlib.metadata import PackageNotFoundError, version

from .NastsClient import NatsClient

try:
    __version__ = version("broker.nats")
except PackageNotFoundError:
    # package is not installed
    pass

__all__ = ["__version__", "NatsClient"]
