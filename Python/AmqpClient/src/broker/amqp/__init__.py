from importlib.metadata import PackageNotFoundError, version

from .AmqpClient import AmqpClient

try:
    __version__ = version("broker.amqp")
except PackageNotFoundError:
    # package is not installed
    pass

__all__ = ["__version__", "AmqpClient"]
