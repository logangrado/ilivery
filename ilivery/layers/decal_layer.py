#!/usr/bin/env python3

import logging

import numpy as np
from PIL import Image

from ilivery.layer import Layer
from ilivery import DECAL_DIR
from ilivery.patterns.logo import logo


def _center_decal_pos(decal, pos, section_bbox):
    """
    Compute upper-left coords that puts the center of the decal at pos
    """
    # Update dest relative to center of bounding box
    pos = (
        pos[0] + int((section_bbox[0] + section_bbox[2]) / 2),
        pos[1] + int((section_bbox[1] + section_bbox[3]) / 2),
    )

    # Find pos at upper left
    pos = tuple([int(x - y / 2) for x, y in zip(pos, decal.size)])

    return pos


def _mirror_decal(pos, original_rotate, mirror_config):  # axis, offset=0, rotate=False):
    reflect = [-1, 1]
    offset = [mirror_config.offset, 0]

    if mirror_config.axis == "x":
        reflect = reflect[::-1]
        # PIL thinks y positive y is down, multiply by -1
        offset = -1 * np.array(offset[::-1])

    pos = (np.array(pos) - offset) * reflect + offset
    pos = pos.tolist()

    if mirror_config.rotate:
        new_rotate = 180 - original_rotate
    else:
        new_rotate = original_rotate

    return pos, new_rotate


def _add_decal_helper(layer, decal, rotate, pos, section_bbox) -> Layer:
    if rotate != 0:
        rotate_kwargs = {"expand": True, "resample": Image.Resampling.BICUBIC}
        decal = decal.rotate(rotate, **rotate_kwargs)

    layer = layer.flatten(decal, dest=_center_decal_pos(decal, pos, section_bbox))

    return layer


def decal_from_decal_config(config):
    if config.type == "NAMED":
        decal_path = DECAL_DIR / f"{config.name}.png"
        decal = Image.open(decal_path).convert("RGBA")

        decal_size = config.size
        # Resize
        if decal_size[0] is None:
            resize = (int(decal.size[0] / decal.size[1] * decal_size[1]), decal_size[1])
        elif decal_size[1] is None:
            resize = (decal_size[0], int(decal.size[1] / decal.size[0] * decal_size[0]))
        else:
            resize = decal_size

        decal = decal.resize(resize)

        # Apply color, if any
        if config.color is not None:
            data = np.array(decal)
            data[:, :, :3] = config.color
            decal = Image.fromarray(data)

        # Create a decal Layer
        decal_layer = Layer.from_image(decal, config.spec)

    elif config.type == "LOGO":
        logo_paint = logo(
            size=config.size,
            facecolor=config.facecolor,
            edgecolor=config.edgecolor,
            edgewidth=config.edgewidth,
            edgeratio=config.edgeratio,
        )
        logo_spec = logo(
            size=config.size,
            facecolor=config.facespec,
            edgecolor=config.edgespec,
            edgewidth=config.edgewidth,
            edgeratio=config.edgeratio,
        )

        decal_layer = Layer.from_image(logo_paint, logo_spec)

    else:
        raise ValueError("")

    return decal_layer


def decal_layer(config, size: tuple[int]) -> Layer:
    layer = Layer(size)

    decal = decal_from_decal_config(config.decal)

    section_bbox = (0, 0, size[0], size[1])

    # Reflect position across x axis - PIL things positive y is down.
    pos = np.array(config.pos) * [1, -1]

    layer = _add_decal_helper(
        layer=layer,
        decal=decal,
        rotate=config.rotate,
        pos=pos,
        section_bbox=section_bbox,
    )
    if config.mirror:
        mirror_pos, mirror_rotate = _mirror_decal(pos=pos, original_rotate=config.rotate, mirror_config=config.mirror)

        layer = _add_decal_helper(
            layer=layer,
            decal=decal,
            rotate=mirror_rotate,
            pos=mirror_pos,
            section_bbox=section_bbox,
        )

    return layer
