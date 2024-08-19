#!/usr/bin/env python3

import inspect

from .solid_layer import solid_layer
from .decal_layer import decal_layer
from .texture_layer import texture_layer
from .class_decal_layer import class_decal_layer
from .patch_layer import patch_layer
from .pattern_layer import pattern_layer

from ilivery.layer import Layer

_layer_dict = {
    "SOLID": solid_layer,
    "DECAL": decal_layer,
    "TEXTURE": texture_layer,
    "CLASS_DECAL": class_decal_layer,
    "PATCH": patch_layer,
    "PATTERN": pattern_layer,
}


def layer_from_config(config, **kwargs) -> Layer:
    # Get the function name from the config
    layer_func = _layer_dict.get(config.type, None)

    if layer_func is None:
        raise ValueError(f"Unknown layer type: {config.type}\nThis layer likely needs to be added to the layer dict")

    # Inspect the function to get its signature
    sig = inspect.signature(layer_func)

    requested_args = [param.name for param in sig.parameters.values()]

    kwargs["config"] = config
    missing_args = set(requested_args) - set(kwargs.keys())
    if missing_args:
        raise ValueError(f"Layer {config.type} requesting unknown args: {missing_args}")

    kwargs = {k: kwargs[k] for k in requested_args}

    # Call the function with the matched arguments
    return layer_func(**kwargs)
