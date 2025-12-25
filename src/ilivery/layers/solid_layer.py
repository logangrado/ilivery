#!/usr/bin/env python3

from ilivery.layer import Layer


def solid_layer(config, size: tuple[int]) -> Layer:
    layer = Layer.from_color(size=size, color=config.color, spec=config.spec)

    return layer
