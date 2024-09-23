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


class TestPatternHexagon:
    def test_basic(self, compare_ref_layer):
        config = {
            "type": "PATTERN",
            "pattern": {
                "type": "HEXAGONS",
                "hexagon_size": 40,
                "facecolor": [255, 0, 0],
                "edgecolor": [0, 255, 0],
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
                "type": "HEXAGONS",
                "hexagon_size": 40,
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
                "type": "HEXAGONS",
                "hexagon_size": 40,
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
                "type": "HEXAGONS",
                "hexagon_size": 80,
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
                "type": "HEXAGONS",
                "hexagon_size": 80,
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

    def test_voronoi(self, compare_ref_layer):
        config = {
            "type": "PATTERN",
            "pattern": {
                "type": "HEXAGONS",
                # "angle": 90,
                "hexagon_size": 40,
                "face_cmap": {
                    "type": "LINEAR_SEGMENTED",
                    "colors": [
                        [0, 0, 0],
                        [150, 150, 150],
                        [239, 168, 58],
                        [218, 80, 117],
                    ],
                },
                "face_cfunc": {
                    "type": "VORONOI",
                    "spacing": 80,
                    "levels": [80, 12, 8, 8],
                    "anisotropy": 2,
                    "angle": 90,
                },
                "edgecolor": [0, 0, 0],
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(1000, 1000))

        # layer.show()
        compare_ref_layer(layer)
