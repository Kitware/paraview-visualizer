from trame_client.utils.version import get_version

from .app import main

__version__ = get_version("pv-visualizer")

__all__ = [
    "__version__",
    "main",
]
