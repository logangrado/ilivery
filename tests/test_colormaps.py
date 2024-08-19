#!/usr/bin/env python3

import pydantic
import numpy as np
import matplotlib as mpl
from PIL import Image
import pytest

from ilivery.config.color_configs import ColorMap
from ilivery.colormaps import colormap_from_config


def _image_from_cmap(cmap, size=(400, 20)):
    xx, yy = np.meshgrid(
        np.arange(size[0]),
        np.arange(size[1]),
    )

    cvals = xx / xx.max()

    cdata = cmap(cvals)

    # Convert to 8bit
    cdata = (cdata * 255).astype(np.uint8)

    image = Image.fromarray(cdata)

    return image


class TestLinearSegmentedColormap:
    def test_basic(self, compare_ref_image):
        config = {
            "type": "LINEAR_SEGMENTED",
            "colors": [
                [0, 0, 0],
                [255, 0, 0],
            ],
            "n_levels": 8,
        }

        config = pydantic.TypeAdapter(ColorMap).validate_python(config)
        cmap = colormap_from_config(config)

        image = _image_from_cmap(cmap)

        compare_ref_image(image, grid=None)

    def test_multi_color(self, compare_ref_image):
        config = {
            "type": "LINEAR_SEGMENTED",
            "colors": [
                [0, 0, 0],
                [255, 255, 255],
                [0, 255, 0],
            ],
            "segments": [0.25],
            "n_levels": 32,
        }

        config = pydantic.TypeAdapter(ColorMap).validate_python(config)
        cmap = colormap_from_config(config)

        image = _image_from_cmap(cmap)

        compare_ref_image(image, grid=None)

    def test_multi_color_sharp(self, compare_ref_image):
        config = {
            "type": "LINEAR_SEGMENTED",
            "colors": [
                [0, 0, 0],
                [255, 255, 255],
                [128, 0, 0],
                [255, 0, 0],
            ],
            "segments": [0.25, 0.25],
            "n_levels": 512,
        }

        config = pydantic.TypeAdapter(ColorMap).validate_python(config)
        cmap = colormap_from_config(config)

        image = _image_from_cmap(cmap)

        compare_ref_image(image, grid=None)
