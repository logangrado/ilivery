#!/usr/bin/env python3

import numpy as np

from ilivery.layer import Layer
from ilivery.patches import poly_patch
from ilivery import utils

from .patch_layer import _build_patch


def _compute_intersection(p0, d0, p1, d1):
    # Create the matrix A and vector b for the system of equations A * [t1, t2]^T = b
    A = np.array([d0, -d1]).T
    b = p1 - p0

    # Check if the determinant is zero (i.e., lines are parallel)
    det = np.linalg.det(A)
    if np.abs(det) < 1e-10:
        return None  # Lines are parallel and do not intersect

    # Solve for t1 and t2 using np.linalg.solve
    t = np.linalg.solve(A, b)
    t1 = t[0]

    # Compute the intersection point using t1
    intersection = p0 + t1 * d0

    return intersection


def _compute_verticies(points, width):
    """Compute the verticies for constructing a stripe with the following points and width

    Parameters
    ----------
    points: (N,2) array
    width: Constant or (N,) array

    Returns
    -------
    verticies: (N*2,2) array
    """
    points = np.asarray(points).astype(float)
    N = points.shape[0]

    # Check if width is a constant or an array
    if isinstance(width, (int, float)):
        width = np.full(N, width)
    else:
        width = np.asarray(width)
    width = width.astype(float)

    # Ensure the widths array has the correct shape
    assert width.shape[0] == N, "Width must be a constant or have the same length as points."

    # Preallocate space for vertices
    verts_l = np.zeros((N, 2))
    verts_r = np.zeros((N, 2))

    for i in range(N):
        # Compute directions for segments before and after the current point
        if i == 0:
            # First point, use the segment to the next point
            direction_next = points[i + 1] - points[i]
            direction_prev = direction_next  # Duplicate for consistent handling
        elif i == N - 1:
            # Last point, use the segment from the previous point
            direction_prev = points[i] - points[i - 1]
            direction_next = direction_prev  # Duplicate for consistent handling
        else:
            # Middle points, use segments to next and from previous points
            direction_prev = points[i] - points[i - 1]
            direction_next = points[i + 1] - points[i]

        # Normalize directions
        direction_prev /= np.linalg.norm(direction_prev)
        direction_next /= np.linalg.norm(direction_next)

        # Compute perpendicular directions to left for both segments
        perp_prev = np.array([-direction_prev[1], direction_prev[0]])
        perp_next = np.array([-direction_next[1], direction_next[0]])

        if i == 0:
            verts_l[i] = points[i] + width[i] / 2 * perp_next
            verts_r[i] = points[i] - width[i] / 2 * perp_next
        elif i == N - 1:
            verts_l[i] = points[i] + width[i] / 2 * perp_prev
            verts_r[i] = points[i] - width[i] / 2 * perp_prev
        else:
            incoming_l = points[i] + width[i] / 2 * perp_prev
            incoming_r = points[i] - width[i] / 2 * perp_prev
            outgoing_l = points[i] + width[i] / 2 * perp_next
            outgoing_r = points[i] - width[i] / 2 * perp_next

            # Compute intersection point for right/left sides
            verts_l[i] = _compute_intersection(incoming_l, direction_prev, outgoing_l, direction_next)
            verts_r[i] = _compute_intersection(incoming_r, direction_prev, outgoing_r, direction_next)

    # Combine left and right vertices in counter-clockwise order
    vertices = np.vstack((verts_l, verts_r[::-1]))

    return vertices


def stripe_layer(config, size):
    layer = Layer(size)

    vertices = _compute_verticies(config.path, width=10)

    # vertices = np.array(config.vertices)
    radii = 0
    # radii = config.radii
    if radii is None:
        radii = 0
    if not isinstance(radii, list):
        radii = np.array([radii] * len(vertices))

    # if config.mirror_vertices:
    #     vertices, radii = _mirror_verts(vertices, radii, config.mirror_vertices)

    kwargs = {
        "facecolor": config.facecolor,
        "edgecolor": config.edgecolor,
        "facespec": config.facespec,
        "edgespec": config.edgespec,
        "edgewidth": config.edgewidth,
    }

    decal = _build_patch(size, vertices=vertices, radii=radii, **kwargs)
    layer = layer.flatten(decal)

    # if config.mirror_patch:
    #     reflect = [-1, 1]
    #     offset = [config.mirror_patch.offset, 0]
    #     if config.mirror_patch.axis == "x":
    #         reflect = reflect[::-1]
    #         offset = offset[::-1]

    #     vertices = (vertices - offset) * reflect + offset

    #     decal = _build_patch(size, vertices=vertices, radii=radii, **kwargs)
    #     layer = layer.flatten(decal)

    return layer
