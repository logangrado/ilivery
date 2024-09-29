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


def _compute_angle(a, b):
    # Compute dot product
    dot_product = np.dot(a, b)
    # Compute magnitudes (norms)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    # Compute cosine of the angle
    cos_theta = dot_product / (norm_a * norm_b)
    # Compute angle in radians
    angle_radians = np.arccos(np.clip(cos_theta, -1.0, 1.0))

    # Compute cross product (only valid for 2D vectors)
    cross_product = np.cross(a, b)

    # Determine the sign of the angle based on the cross product
    if cross_product < 0:
        angle_radians = -angle_radians  # Clockwise (right turn)

    # Convert angle to degrees
    angle_degrees = np.degrees(angle_radians)

    return angle_degrees


def _compute_verticies(points, radii, width):
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

    if radii is None:
        radii = [0] * len(points)

    if len(radii) != len(points):
        raise ValueError("Require equal number of radii and points")

    # Ensure the widths array has the correct shape
    assert width.shape[0] == N, "Width must be a constant or have the same length as points."

    # Preallocate space for vertices
    verts_l = np.zeros((N, 2))
    verts_r = np.zeros((N, 2))

    radii_l = np.zeros(N)
    radii_r = np.zeros(N)

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
            radii_l[i] = radii[i]
            radii_r[i] = radii[i]

        elif i == N - 1:
            verts_l[i] = points[i] + width[i] / 2 * perp_prev
            verts_r[i] = points[i] - width[i] / 2 * perp_prev
            radii_l[i] = radii[i]
            radii_r[i] = radii[i]

        else:
            incoming_l = points[i] + width[i] / 2 * perp_prev
            incoming_r = points[i] - width[i] / 2 * perp_prev
            outgoing_l = points[i] + width[i] / 2 * perp_next
            outgoing_r = points[i] - width[i] / 2 * perp_next

            # Compute intersection point for right/left sides
            verts_l[i] = _compute_intersection(incoming_l, direction_prev, outgoing_l, direction_next)
            verts_r[i] = _compute_intersection(incoming_r, direction_prev, outgoing_r, direction_next)

            # Need to adjust radii according to the width at the turning point. Radii should be
            # Determine direction we are turning in. Positive is left, negative is right
            angle = _compute_angle(direction_prev, direction_next)
            radii_l[i] = np.min(radii[i] - np.sign(angle) * width[i] / 2, 0)
            radii_r[i] = np.min(radii[i] + np.sign(angle) * width[i] / 2, 0)

    # Combine left and right vertices in counter-clockwise order
    vertices = np.vstack((verts_l, verts_r[::-1]))

    radii = np.concatenate([radii_l, radii_r[::-1]])

    return vertices, radii


def stripe_layer(config, size):
    layer = Layer(size)

    vertices, radii = _compute_verticies(config.path, config.radii, width=10)

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
