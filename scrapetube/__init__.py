from .scrapetube import get_channel, get_search, get_playlist, get_video, get_search_creative_commons

# Import CC functionality
from . import cc
from . import utils

__version__ = "2.5.1"

# Re-export for backward compatibility
__all__ = [
    "get_channel",
    "get_search", 
    "get_playlist",
    "get_video",
    "get_search_creative_commons",
    "cc",
    "utils",
    "__version__",
]
