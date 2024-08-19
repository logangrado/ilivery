#!/usr/bin/env python3
import pydantic

from ilivery.layer import Layer
from ilivery.layers import layer_from_config
from ilivery.config import layer_configs

import pytest


class TestTextureLayer:
    def test_carbon_fiber(self, compare_ref_layer):
        config = {
            "type": "TEXTURE",
            "texture": "CARBON_FIBER",
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)
