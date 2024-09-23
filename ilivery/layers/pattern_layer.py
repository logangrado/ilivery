#!/usr/bin/env python3

from ilivery.layer import Layer
from ilivery.patterns.triangles import triangles
from ilivery.patterns.hexagons import hexagons

from ilivery.colormaps import colormap_from_config
from ilivery.colorfuncs import colorfunc_from_config


def triangle_pattern_layer(config, size):
    image, spec = triangles(
        triangle_size=config.pattern.triangle_size,
        # SIZING
        size=size,
        angle=config.pattern.angle,
        edgewidth=config.pattern.edgewidth,
        spacing=config.pattern.spacing,
        # COLOR ARGS
        facecolor=config.pattern.facecolor,
        face_cmap=colormap_from_config(config.pattern.face_cmap),
        face_cfunc=colorfunc_from_config(config.pattern.face_cfunc),
        edgecolor=config.pattern.edgecolor,
        # SPEC ARGS
        facespec=config.pattern.facespec,
        facespec_cmap=colormap_from_config(config.pattern.facespec_cmap),
        facespec_cfunc=colorfunc_from_config(config.pattern.facespec_cfunc),
        edgespec=config.pattern.edgespec,
    )

    layer = Layer.from_image(image, spec)

    return layer


def hexagon_pattern_layer(config, size):
    image, spec = hexagons(
        hexagon_size=config.pattern.hexagon_size,
        # SIZING
        size=size,
        angle=config.pattern.angle,
        edgewidth=config.pattern.edgewidth,
        spacing=config.pattern.spacing,
        # COLOR ARGS
        facecolor=config.pattern.facecolor,
        face_cmap=colormap_from_config(config.pattern.face_cmap),
        face_cfunc=colorfunc_from_config(config.pattern.face_cfunc),
        edgecolor=config.pattern.edgecolor,
        # SPEC ARGS
        facespec=config.pattern.facespec,
        facespec_cmap=colormap_from_config(config.pattern.facespec_cmap),
        facespec_cfunc=colorfunc_from_config(config.pattern.facespec_cfunc),
        edgespec=config.pattern.edgespec,
    )

    layer = Layer.from_image(image, spec)

    return layer


def pattern_layer(config, size):
    patterns = {
        "TRIANGLES": triangle_pattern_layer,
        "HEXAGONS": hexagon_pattern_layer,
    }

    pattern = patterns[config.pattern.type]

    return pattern(config, size)
