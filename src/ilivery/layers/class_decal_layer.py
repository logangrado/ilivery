#!/usr/bin/env python3

import functools
import logging

from ilivery import utils
from ilivery.layer import Layer

logger = logging.getLogger(__name__)


def class_decal_layer(config, template_path) -> Layer:
    decal_path = template_path.parent / config.class_name
    decal_path = decal_path.with_suffix(".psd")

    # Alpha composite all layers in the decal
    parent_logger = logger.parent if logger.parent else logger
    level = parent_logger.getEffectiveLevel()
    parent_logger.setLevel("ERROR")
    decal, _, _ = utils.psd.load_layers(decal_path)
    parent_logger.setLevel(level)

    decal = functools.reduce(lambda x, y: x.alpha_composite(y), decal.values())

    layer = Layer.from_image(decal, spec=config.spec)

    return layer
