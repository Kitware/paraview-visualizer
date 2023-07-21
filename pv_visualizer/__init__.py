import os
from trame_client.utils.version import get_version

# Disable warning
os.environ["TRAME_DISABLE_V3_WARNING"] = "1"

__version__ = get_version("pv-visualizer")

__all__ = [
    "__version__",
]
