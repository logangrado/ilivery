#!/usr/bin/env python3

import numpy as np

from ilivery.layer import Layer
from ilivery.patches import poly_patch
from ilivery import utils


def _mirror_verts(verts, radii, config):
    mirror_verts = verts.copy()[::-1]

    if config.axis == "y":
        mirror_verts[:, 0] *= -1
    elif config.axis == "x":
        mirror_verts[:, 1] *= -1

    if config.offset != 0:
        raise NotImplementedError("")

    verts = np.concatenate([verts, mirror_verts])
    radii = np.concatenate([radii, radii[::-1]])
    return verts, radii


def _build_patch(size, vertices, radii, facecolor, edgecolor, facespec, edgespec, edgewidth):
    # Add center to vertices
    center = tuple([round(c / 2) for c in size])

    vertices = np.array(vertices) + center

    kwargs = {
        "vertices": vertices,
        "radii": radii,
        "linewidth": edgewidth,
        "size": size,
    }

    decal = poly_patch(facecolor=facecolor, edgecolor=edgecolor, **kwargs)

    if facespec or edgespec:
        decal_spec = poly_patch(facecolor=facespec, edgecolor=edgespec, **kwargs)
    else:
        decal_spec = None

    decal_layer = Layer.from_image(decal, decal_spec)

    return decal_layer


def patch_layer(config, size):
    layer = Layer(size)

    vertices = np.array(config.vertices)
    radii = config.radii
    if radii is None:
        radii = 0
    if not isinstance(radii, list):
        radii = np.array([radii] * len(vertices))

    if config.mirror_vertices:
        vertices, radii = _mirror_verts(vertices, radii, config.mirror_vertices)

    kwargs = {
        "facecolor": config.facecolor,
        "edgecolor": config.edgecolor,
        "facespec": config.facespec,
        "edgespec": config.edgespec,
        "edgewidth": config.edgewidth,
    }

    decal = _build_patch(size, vertices=vertices, radii=radii, **kwargs)
    layer = layer.flatten(decal)

    if config.mirror_patch:
        reflect = [-1, 1]
        offset = [config.mirror_patch.offset, 0]
        if config.mirror_patch.axis == "x":
            reflect = reflect[::-1]
            offset = offset[::-1]

        vertices = (vertices - offset) * reflect + offset

        decal = _build_patch(size, vertices=vertices, radii=radii, **kwargs)
        layer = layer.flatten(decal)

    return layer
