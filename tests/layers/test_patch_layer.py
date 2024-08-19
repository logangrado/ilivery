#!/usr/bin/env python3

import pydantic

from ilivery.layer import Layer
from ilivery.layers import layer_from_config
from ilivery.config import layer_configs

import pytest


class TestPatchLayer:
    def test_basic(self, compare_ref_layer):
        config = {
            "type": "PATCH",
            "vertices": [
                [0, 0],
                [100, 0],
                [0, 50],
            ],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 4,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_radii_single(self, compare_ref_layer):
        config = {
            "type": "PATCH",
            "vertices": [
                [-50, -50],
                [50, -50],
                [50, 50],
                [-50, 50],
            ],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 1,
            "radii": 25,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_radii_multiple(self, compare_ref_layer):
        config = {
            "type": "PATCH",
            "vertices": [
                [-50, -50],
                [50, -50],
                [50, 50],
                [-50, 50],
            ],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 1,
            "radii": [0, 10, 20, 50],
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    @pytest.mark.parametrize("axis", ["x", "y"])
    def test_mirror_patch(self, compare_ref_layer, axis):
        config = {
            "type": "PATCH",
            "vertices": [
                [10, 0],
                [90, 0],
                [10, 50],
            ],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 4,
            "mirror_patch": {
                "axis": axis,
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    @pytest.mark.parametrize("axis", ["x", "y"])
    def test_mirror_vertices(self, compare_ref_layer, axis):
        config = {
            "type": "PATCH",
            "vertices": [
                [90, 0],
                [0, 90],
                # [10, 50],
            ],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 4,
            "mirror_vertices": {
                "axis": axis,
            },
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)

    def test_patch_points_in_line(self, compare_ref_layer):
        """Test that we can handle points on a line (center points should just get dropped)"""
        config = {
            "type": "PATCH",
            "vertices": [
                [0, 0],
                [50, 0],
                [100, 0],
                [0, 50],
            ],
            "facecolor": [255, 0, 0],
            "edgecolor": [0, 255, 0],
            "facespec": [0, 255, 0],
            "edgespec": [0, 0, 255],
            "edgewidth": 4,
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)
