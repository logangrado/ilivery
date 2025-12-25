#!/usr/bin/env python3
import pydantic

from ilivery.config import layer_configs
from ilivery.layers import layer_from_config


class TestTextureLayer:
    def test_carbon_fiber(self, compare_ref_layer):
        config = {
            "type": "TEXTURE",
            "texture": "CARBON_FIBER",
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)
        layer = layer_from_config(config, size=(200, 200))

        compare_ref_layer(layer)
