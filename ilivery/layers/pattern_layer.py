#!/usr/bin/env python3

from ilivery.layer import Layer
from ilivery.patterns.triangles import triangles

from ilivery.colormaps import colormap_from_config
from ilivery.colorfuncs import colorfunc_from_config


def pattern_layer(config, size):
    image, spec = triangles(
        triangle_size=config.pattern.triangle_size,
        size=size,
        angle=config.pattern.angle,
        facecolor=config.pattern.facecolor,
        face_cmap=colormap_from_config(config.pattern.face_cmap),
        face_cfunc=colorfunc_from_config(config.pattern.face_cfunc),
        edgecolor=config.pattern.edgecolor,
        edgewidth=config.pattern.edgewidth,
        facespec=config.pattern.facespec,
        facespec_cmap=colormap_from_config(config.pattern.facespec_cmap),
        facespec_cfunc=colorfunc_from_config(config.pattern.facespec_cfunc),
        edgespec=config.pattern.edgespec,
        spacing=config.pattern.spacing,
    )

    layer = Layer.from_image(image, spec)

    return layer
