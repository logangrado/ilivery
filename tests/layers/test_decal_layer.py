#!/usr/bin/env python3
import pydantic

from ilivery.layer import Layer
from ilivery.layers import layer_from_config
from ilivery.config import layer_configs

import pytest


class TestDecalLayer:
    def test_basic(self, compare_ref_layer):
        config = {
            "type": "DECAL",
            "decal": {
                "type": "NAMED",
                "name": "MAASR",
                "color": [255, 0, 0],
                "spec": [0, 255, 0],
                "size": [100, None],
            },
            "pos": [0, 0],
            "mirror": None,
            "rotate": 0,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    @pytest.mark.parametrize("ax", ["x", "y", "xy"])
    def test_size(self, compare_ref_layer, ax):
        if ax == "x":
            size = [100, None]
        elif ax == "y":
            size = [None, 100]
        else:
            size = [100, 100]

        config = {
            "type": "DECAL",
            "decal": {
                "type": "NAMED",
                "name": "MAASR",
                "color": [255, 0, 0],
                "spec": [0, 255, 0],
                "size": size,
            },
            "pos": [0, 0],
            "mirror": None,
            "rotate": 0,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)

        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_pos(self, compare_ref_layer):
        config = {
            "type": "DECAL",
            "decal": {
                "type": "NAMED",
                "name": "MAASR",
                "color": [255, 0, 0],
                "spec": [0, 255, 0],
                "size": [100, None],
            },
            "pos": [50, 150],
            "mirror": None,
            "rotate": 0,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)

        layer = layer_from_config(config, size=(300, 300))

        compare_ref_layer(layer)

    def test_rotate(self, compare_ref_layer):
        config = {
            "type": "DECAL",
            "decal": {
                "type": "NAMED",
                "name": "MAASR",
                "color": [255, 0, 0],
                "spec": [0, 255, 0],
                "size": [100, None],
            },
            "pos": [0, 0],
            "mirror": None,
            "rotate": 45,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)

        layer = layer_from_config(config, size=(300, 300))

        compare_ref_layer(layer)

    @pytest.mark.parametrize("ax", ["x", "y"])
    def test_mirror(self, compare_ref_layer, ax):
        config = {
            "type": "DECAL",
            "decal": {
                "type": "NAMED",
                "name": "MAASR",
                "color": [255, 0, 0],
                "spec": [0, 255, 0],
                "size": [100, None],
            },
            "pos": [50, 50],
            "mirror": {"axis": ax},
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)

        layer = layer_from_config(config, size=(300, 300))

        compare_ref_layer(layer)

    def test_pos_rotate(self, compare_ref_layer):
        config = {
            "type": "DECAL",
            "decal": {
                "type": "NAMED",
                "name": "MAASR",
                "color": [255, 0, 0],
                "spec": [0, 255, 0],
                "size": [100, None],
            },
            "pos": [50, 0],
            "mirror": None,
            "rotate": 45,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(300, 300))

        compare_ref_layer(layer)

    @pytest.mark.parametrize("ax", ["x", "y"])
    @pytest.mark.parametrize("rotate", [True, False])
    @pytest.mark.parametrize("offset", [0, 25])
    def test_pos_rotate_mirror(self, compare_ref_layer, ax, rotate, offset):
        config = {
            "type": "DECAL",
            "decal": {
                "type": "NAMED",
                "name": "MAASR",
                "color": [255, 0, 0],
                "spec": [0, 255, 0],
                "size": [100, None],
            },
            "pos": [50, 50],
            "mirror": {
                "axis": ax,
                "rotate": rotate,
                "offset": offset,
            },
            "rotate": 45,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(300, 300))

        compare_ref_layer(layer)


class TestLogoDecalLayer:
    def test_basic(self, compare_ref_layer):
        config = {
            "type": "DECAL",
            "decal": {
                "type": "LOGO",
                "size": 100,
                "facecolor": [255, 0, 0],
                "edgecolor": [0, 255, 0],
                "facespec": [0, 255, 0],
                "edgespec": [0, 0, 255],
                "edgeratio": 0.1,
            },
            "pos": [0, 0],
            "mirror": None,
            "rotate": 0,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)
