import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
import matplotlib as mpl
import matplotlib.pyplot as plt

from ilivery import utils
from ilivery.decorators import param_groups
from ilivery.patterns.poly_pattern import poly_pattern

_hex_verts = np.array(
    [
        [1 / 2, 0],
        [1 / 4, np.sqrt(3) / 4],
        [-1 / 4, np.sqrt(3) / 4],
        [-1 / 2, 0],
        [-1 / 4, -np.sqrt(3) / 4],
        [1 / 4, -np.sqrt(3) / 4],
    ]
)


def _transform_shape(verts, xy, scale, angle):
    verts = np.array(verts)
    angle = angle % 360
    if angle != 0:
        angle = np.pi * angle / 180
        rot_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        verts = np.matmul(verts, rot_matrix)

    verts = verts * scale + np.array(xy)

    return verts


def _get_hex_verticies(row, size, angle=0):
    # Vertex of polygon centered at 0 that inscribes a circle with diameter == 1

    size *= 1.04

    verts = _transform_shape(_hex_verts, xy=row[["x", "y"]].tolist(), scale=size, angle=angle)

    verts = tuple([tuple(x) for x in verts])

    return verts


def _get_hex_grid(size, hex_size, angle, spacing):
    """
    Get a list of hexagon centers in grid
    """

    out = []

    square_size = max(size) * np.sqrt(2)

    # Determine number of hexagons in x/y directions
    n_x = int(square_size / (1.5 * hex_size)) + 2
    n_y = int(square_size / (np.sqrt(3) / 4 * hex_size)) + 2

    out = pd.DataFrame([[i, j] for i in range(-n_x, n_x) for j in range(-n_y, n_y)], columns=["i", "j"])

    out["x"] = out["i"] * 1.5 + out["j"] % 2 * 0.75
    out["y"] = out["j"] * np.sqrt(3) / 4

    # Rotate/scale grid
    out[["x", "y"]] = _transform_shape(
        verts=np.array(out[["x", "y"]]), scale=(hex_size + spacing), xy=(0, 0), angle=angle
    )

    # Prune grid
    x_min, x_max = [-hex_size, size[0] + hex_size]
    y_min, y_max = [-hex_size, size[1] + hex_size]

    out = out[(out["x"] > x_min) & (out["x"] < x_max) & (out["y"] > y_min) & (out["y"] < y_max)].reset_index(drop=True)

    return out[["x", "y"]]


@param_groups(exclusive=["color", "cmap"])
def hexagons(
    hex_size,
    size,
    angle,
    color=None,
    cmap=None,
    cfunc=None,
    edgecolor=None,
    edgewidth=0,
    spacing=0,
    facespec=None,
    edgespec=None,
):
    # Generate poly grid
    poly_grid = _get_hex_grid(size=size, hex_size=hex_size, angle=angle, spacing=spacing)
    poly_grid["verts"] = poly_grid.apply(_get_hex_verticies, axis=1, size=hex_size, angle=angle)

    return poly_pattern(
        size=size,
        poly_df=poly_grid,
        color=color,
        cmap=cmap,
        cfunc=cfunc,
        edgecolor=edgecolor,
        edgewidth=edgewidth,
        facespec=facespec,
        edgespec=edgespec,
    )
