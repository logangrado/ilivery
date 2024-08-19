#!/usr/bin/env python3

import functools

from ilivery.layer import Layer
from ilivery import utils


def class_decal_layer(config, template_path) -> Layer:
    decal_path = template_path.parent / config.class_name
    decal_path = decal_path.with_suffix(".psd")

    decal, _, _ = utils.psd.load_layers(decal_path)

    # Alpha composite all layers in the decal
    decal = functools.reduce(lambda x, y: x.alpha_composite(y), decal.values())

    layer = Layer.from_image(decal, spec=config.spec)

    return layer
