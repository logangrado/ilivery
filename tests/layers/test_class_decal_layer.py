#!/usr/bin/env python3
import pydantic

from ilivery.layer import Layer
from ilivery.layers import layer_from_config
from ilivery.config import layer_configs
from ilivery import TEMPLATE_DIR

import pytest


class TestTextureLayer:
    @pytest.mark.parametrize("class_name", ["s12/pro", "s12/club"])
    def test_carbon_fiber(self, class_name, compare_ref_layer):
        config = {
            "type": "CLASS_DECAL",
            "class_name": class_name,
            "spec": [255, 0, 0],
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)

        template_path = TEMPLATE_DIR / "porsche992cup" / "segmented.psd"
        layer = layer_from_config(config, size=(2048, 2048), template_path=template_path)

        compare_ref_layer(layer)
