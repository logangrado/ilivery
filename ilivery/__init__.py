try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata
__version__ = importlib_metadata.version(__name__)

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot

import logging
from pathlib import Path

ROOT = Path(__file__).parent
RESOURCE_DIR = ROOT.parent / "resources"
TEMPLATE_DIR = RESOURCE_DIR / "templates"
DECAL_DIR = RESOURCE_DIR / "decals"
TEXTURE_DIR = RESOURCE_DIR / "textures"
LAYER_CACHE_DIR = ROOT.parent / ".layer_cache"

import loggerado

logger = logging.getLogger(__name__)

loggerado.configure_logger(logger, level="INFO", ansi=True)
