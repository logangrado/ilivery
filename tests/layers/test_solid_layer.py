import pydantic

from ilivery.layer import Layer
from ilivery.layers import layer_from_config
from ilivery.config import layer_configs

import pytest


class TestSolidLayer:
    def test_basic(self):
        config = {
            "type": "SOLID",
            "color": [0, 1, 2],
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)

        layer = layer_from_config(config, size=(4, 6))

        data = layer.to_numpy()

        assert (data["paint"] == [0, 1, 2, 255]).all()
        assert (data["spec"] == [0, 0, 0, 0]).all()

    def test_with_spec(self):
        config = {
            "type": "SOLID",
            "color": [0, 1, 2],
            "spec": "MATTE",
        }

        config = pydantic.TypeAdapter(layer_configs.LayerConfig).validate_python(config)

        layer = layer_from_config(config, size=(4, 6))

        data = layer.to_numpy()

        assert (data["paint"] == [0, 1, 2, 255]).all()
        assert (data["spec"] == [0, 127, 0, 255]).all()
