#!/usr/bin/env python3
#!/usr/bin/env python3

import pydantic

from ilivery.layer import Layer
from ilivery.layers import layer_from_config
from ilivery.config import layer_configs

import pytest


class TestPatternTriangle:
    def test_basic(self, compare_ref_layer):
        config = {
            "type": "PATTERN",
            "pattern": {
                "type": "TRIANGLES",
                "triangle_size": 40,
                "facecolor": [0, 0, 0],
                "edgecolor": [255, 255, 255],
                "edgewidth": 2,
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_angle(self, compare_ref_layer):
        config = {
            "type": "PATTERN",
            "pattern": {
                "type": "TRIANGLES",
                "triangle_size": 40,
                "facecolor": [0, 0, 0],
                "edgecolor": [255, 255, 255],
                "edgewidth": 2,
                "angle": 5,
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_spec_only(self, compare_ref_layer):
        config = {
            "type": "PATTERN",
            "pattern": {
                "type": "TRIANGLES",
                "triangle_size": 40,
                "facecolor": None,
                "edgecolor": None,
                "edgewidth": 2,
                "facespec": [255, 0, 0],
                "edgespec": [0, 255, 0],
                "angle": 0,
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_cmap(self, compare_ref_layer):
        config = {
            "type": "PATTERN",
            "pattern": {
                "type": "TRIANGLES",
                "triangle_size": 80,
                "face_cmap": {
                    "type": "LINEAR_SEGMENTED",
                    "colors": [
                        [255, 0, 0],
                        [0, 255, 0],
                    ],
                },
                "face_cfunc": {
                    "type": "GRADIENT",
                    "direction": [-1, 1],
                },
                "edgecolor": [255, 255, 255],
                "edgewidth": 2,
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_edge_cmap(self, compare_ref_layer):
        config = {
            "type": "PATTERN",
            "pattern": {
                "type": "TRIANGLES",
                "triangle_size": 80,
                "facespec_cmap": {
                    "type": "LINEAR_SEGMENTED",
                    "colors": [
                        [255, 0, 0],
                        [0, 255, 0],
                    ],
                },
                "facespec_cfunc": {
                    "type": "GRADIENT",
                    "direction": [-1, 1],
                },
                "edgespec": [255, 255, 255],
                "edgewidth": 2,
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)
