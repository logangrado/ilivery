from ._version import __version__

import matplotlib
import logging
from pathlib import Path
import loggerado

matplotlib.use("agg")
import matplotlib.pyplot


logger = logging.getLogger(__name__)
loggerado.configure_logger(logger, level="INFO", ansi=True)


ROOT = Path(__file__).parent
RESOURCE_DIR = ROOT.parent / "resources"
TEMPLATE_DIR = RESOURCE_DIR / "templates"
DECAL_DIR = RESOURCE_DIR / "decals"
TEXTURE_DIR = RESOURCE_DIR / "textures"
LAYER_CACHE_DIR = ROOT.parent / ".layer_cache"
print(f"FILE: {__file__}")
print(f"ROOT_DIR: {ROOT}")
print(f"RESOURCE_DIR: {RESOURCE_DIR}")
