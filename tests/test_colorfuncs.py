#!/usr/bin/env python3

import pydantic
import numpy as np
import matplotlib as mpl
from PIL import Image
import pytest

from ilivery.config.color_configs import ColorFunction
from ilivery.colorfuncs import colorfunc_from_config


def _image_from_cfunc(cfunc, size=(200, 200)):
    xx, yy = np.meshgrid(
        np.arange(size[0]),
        np.arange(size[1]),
    )

    cvals = cfunc(xx, yy)

    cmap = mpl.colormaps.get_cmap("Greens")

    cdata = cmap(cvals)

    # Convert to 8bit
    cdata = (cdata * 255).astype(np.uint8)

    image = Image.fromarray(cdata)

    return image


class TestGradientCFunc:
    def test_basic_x(self, compare_ref_image):
        config = {
            "type": "GRADIENT",
            "direction": [0, 1],
        }

        config = pydantic.TypeAdapter(ColorFunction).validate_python(config)
        cfunc = colorfunc_from_config(config)

        image = _image_from_cfunc(cfunc)

        compare_ref_image(image)

    def test_basic_xy(self, compare_ref_image):
        config = {
            "type": "GRADIENT",
            "direction": [1, 1],
        }

        config = pydantic.TypeAdapter(ColorFunction).validate_python(config)
        cfunc = colorfunc_from_config(config)

        image = _image_from_cfunc(cfunc)

        compare_ref_image(image)


class TestUniformNoiseCFunc:
    @pytest.mark.parametrize("seed", [0, 42])
    def test_basic(self, compare_ref_image, seed):
        config = {
            "type": "RANDOM_UNIFORM",
            "seed": seed,
        }

        config = pydantic.TypeAdapter(ColorFunction).validate_python(config)
        cfunc = colorfunc_from_config(config)

        image = _image_from_cfunc(cfunc)

        compare_ref_image(image)


class TestSimplexNoiseCFunc:
    @pytest.mark.parametrize("seed", [0, 42])
    def test_basic(self, compare_ref_image, seed):
        config = {
            "type": "SIMPLEX_NOISE",
            "length_scale": [10, 10],
            "seed": seed,
        }

        config = pydantic.TypeAdapter(ColorFunction).validate_python(config)
        cfunc = colorfunc_from_config(config)

        image = _image_from_cfunc(cfunc)

        compare_ref_image(image)

    @pytest.mark.parametrize("ax", ["x", "y"])
    def test_length_scale(self, compare_ref_image, ax):
        if ax == "x":
            length_scale = [100, 10]
        elif ax == "y":
            length_scale = [100, 10]
        else:
            raise ValueError("")

        config = {
            "type": "SIMPLEX_NOISE",
            "length_scale": length_scale,
            "seed": 0,
        }

        config = pydantic.TypeAdapter(ColorFunction).validate_python(config)
        cfunc = colorfunc_from_config(config)

        image = _image_from_cfunc(cfunc)

        compare_ref_image(image)

    @pytest.mark.parametrize("angle", [0, 15, 30])
    def test_angle(self, compare_ref_image, angle):
        config = {
            "type": "SIMPLEX_NOISE",
            "length_scale": [100, 10],
            "angle": angle,
            "seed": 0,
        }

        config = pydantic.TypeAdapter(ColorFunction).validate_python(config)
        cfunc = colorfunc_from_config(config)

        image = _image_from_cfunc(cfunc)

        compare_ref_image(image)


class TestComposedCFunc:
    def test_basic(self, compare_ref_image):
        config = {
            "type": "COMPOSED",
            "color_functions": [
                {
                    "type": "GRADIENT",
                    "direction": [0, 1],
                    "range": [0, 1],
                },
                {
                    "type": "RANDOM_UNIFORM",
                    "seed": 0,
                    "range": [0, 0.5],
                },
            ],
        }

        config = pydantic.TypeAdapter(ColorFunction).validate_python(config)
        cfunc = colorfunc_from_config(config)

        image = _image_from_cfunc(cfunc)

        compare_ref_image(image)
