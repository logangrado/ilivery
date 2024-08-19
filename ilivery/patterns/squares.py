import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from ilivery import utils
from ilivery.decorators import param_groups
from ilivery.patterns.poly_pattern import poly_pattern

_square_verts = np.array([[0.5, 0.5], [0.5, -0.5], [-0.5, -0.5], [-0.5, 0.5]])


def _transform_shape(verts, xy, scale, angle):
    verts = np.array(verts)
    angle = angle % 360
    if angle != 0:
        angle = np.pi * angle / 180
        rot_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        verts = np.matmul(verts, rot_matrix)

    verts = verts * scale + np.array(xy)

    return verts


def _get_square_verticies(row, size, angle=0):
    # Vertex of polygon centered at 0 that inscribes a circle with diameter == 1

    verts = _transform_shape(_square_verts, xy=row[["x", "y"]].tolist(), scale=size, angle=angle)

    verts = tuple([tuple(x) for x in verts])

    return verts


def _get_square_grid(size, square_size, angle, spacing):
    """
    Get a list of squareagon centers in grid
    """

    out = []

    max_size = max(size) * np.sqrt(2)

    # Determine number of squareagons in x/y directions
    #
    n_x = int(max_size / (square_size / 2)) + 2
    n_y = int(max_size / (square_size * np.sqrt(3) / 2)) + 2

    # Create the initial square grid, where 3rd value is up/down
    out = pd.DataFrame([[i, j] for i in range(-n_x, n_x) for j in range(-n_y, n_y)], columns=["i", "j"])

    out["x"] = out["i"]
    out["y"] = out["j"]

    # Rotate/scale grid
    out[["x", "y"]] = _transform_shape(
        verts=np.array(out[["x", "y"]]), scale=(square_size + spacing), xy=(0, 0), angle=angle
    )

    # Prune grid
    x_min, x_max = [-square_size, size[0] + square_size]
    y_min, y_max = [-square_size, size[1] + square_size]

    out = out[(out["x"] > x_min) & (out["x"] < x_max) & (out["y"] > y_min) & (out["y"] < y_max)].reset_index(drop=True)

    return out[["x", "y"]]


@param_groups(exclusive=["color", "cmap"])
def squares(
    square_size,
    size,
    angle=0,
    cmap=None,
    cfunc=None,
    color=None,
    edgecolor=None,
    spacing=0,
    edgewidth=None,
    facespec=None,
    edgespec=None,
):
    # Generate poly grid
    poly_grid = _get_square_grid(size=size, square_size=square_size, angle=angle, spacing=spacing)
    poly_grid["verts"] = poly_grid.apply(_get_square_verticies, axis=1, size=square_size, angle=angle)

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
