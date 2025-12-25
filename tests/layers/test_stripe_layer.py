#!/usr/bin/env python3

import pydantic

from ilivery.config import layer_configs
from ilivery.layers import layer_from_config


class TestStripeLayer:
    def test_basic(self, compare_ref_layer):
        config = {
            "type": "STRIPE",
            "vertices": [
                [0, 0],
                [50, 0],
                [50, 50],
            ],
            "width": 10,
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 2,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_radii(self, compare_ref_layer):
        config = {
            "type": "STRIPE",
            "vertices": [
                [0, 0],
                [50, 0],
                [50, 50],
            ],
            "width": 10,
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 2,
            "radii": [0, 20, 2],
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_widths(self, compare_ref_layer):
        config = {
            "type": "STRIPE",
            "vertices": [
                [-50, -50],
                [0, -50],
                [0, 0],
            ],
            "width": [10, 20],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 2,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_widths_mixed(self, compare_ref_layer):
        config = {
            "type": "STRIPE",
            "vertices": [
                [-50, -50],
                [0, -50],
                [0, 0],
            ],
            "width": [10, [10, 20]],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 2,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_widths_dense(self, compare_ref_layer):
        config = {
            "type": "STRIPE",
            "vertices": [
                [-50, -50],
                [0, -50],
                [0, 0],
            ],
            "width": [[10, 5], [10, 20]],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 2,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_mirror(self, compare_ref_layer):
        config = {
            "type": "STRIPE",
            "vertices": [
                [0, 30],
                [50, 30],
            ],
            "width": 5,
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 1,
            "mirror_patch": {
                "axis": "x",
                "offset": 5,
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_vertex_path(self, compare_ref_layer):
        config = {
            "type": "STRIPE",
            "vertex_path": [
                [0, 0],
                [90, 30],
                [130, 30],
            ],
            "width": 5,
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 1,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_tip_angles(self, compare_ref_layer):
        config = {
            "type": "STRIPE",
            "vertices": [
                [0, 0],
                [50, 0],
                [50, 50],
            ],
            "width": 10,
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 2,
            "tip_angles": [30, 60],
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)
