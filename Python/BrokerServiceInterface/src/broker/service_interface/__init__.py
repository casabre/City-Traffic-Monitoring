from importlib.metadata import PackageNotFoundError, version

from .ServiceInterface import ServiceInterface
from .utility import to_async

try:
    __version__ = version("broker.service_interface")
except PackageNotFoundError:
    # package is not installed
    pass

__all__ = ["__version__", "ServiceInterface", "to_async"]
