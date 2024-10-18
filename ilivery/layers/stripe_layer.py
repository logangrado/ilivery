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


def _compute_line_intersection(line1, line2):
    """
    Calculate the intersection point of two lines defined by two points each.

    Parameters:
    line1: ((x1, y1), (x2, y2)) - Points defining the first line.
    line2: ((x3, y3), (x4, y4)) - Points defining the second line.

    Returns:
    (x, y): The intersection point of the lines, or None if the lines are parallel.
    """
    # Unpack the points
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    # Calculate the differences
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denominator == 0:
        # The lines are parallel or coincident, no intersection
        return None

    # Calculate the intersection point using determinants
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator

    return (px, py)


def _compute_angle(a, b):
    a = a.reshape(-1)
    b = b.reshape(-1)
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


def _perp(x):
    return x @ np.array([[0, 1], [-1, 0]])


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
        width = np.full((N - 1, 2), width)

    else:
        if len(width) != len(points) - 1:
            raise ValueError(f"Width have one fewer elements than points. Expected {len(points)-1}, got {len(width)}")
        _widths = []
        for item in width:
            if isinstance(item, int):
                _widths.append([item] * 2)
            else:
                if len(width) != 2:
                    raise ValueError("")
                _widths.append(item)
        width = np.asarray(_widths)
    width = width.astype(float)

    if radii is None:
        radii = [0] * len(points)

    if len(radii) != len(points):
        raise ValueError("Require equal number of radii and points")

    # Ensure the widths array has the correct shape
    assert width.shape == (N - 1, 2), "Width must be a constant or have the same length as points."

    # Preallocate space for vertices
    verts_l = np.zeros((N, 2))
    verts_r = np.zeros((N, 2))

    radii_l = np.zeros(N)
    radii_r = np.zeros(N)

    # Compute directions for each segment
    directions = np.diff(points, axis=0)
    directions = directions / np.linalg.norm(directions, axis=1).reshape(-1, 1)

    # Compute verts at each point - resulting in an (N-1,2,2,2) list, where
    # Dim 1: Num segments (N-1)
    # Dim 2: start/end of the segment
    # Dim 3: left/right point
    # Dim 4: x/y coords
    x = []
    for i, (direction, width) in enumerate(zip(directions, width)):
        point0 = points[i]
        point1 = points[i + 1]

        x.append(
            [
                [
                    point0 + _perp(direction) * width[0],
                    point0 - _perp(direction) * width[0],
                ],
                [
                    point1 + _perp(direction) * width[1],
                    point1 - _perp(direction) * width[1],
                ],
            ]
        )
    x = np.array(x)

    # Finally, compute the actual path verticies
    verts_l = []
    verts_r = []
    radii_l = []
    radii_r = []
    for i in range(len(x)):
        if i == 0:
            verts_l.append(x[0, 0, 0])
            verts_r.append(x[0, 0, 1])
            radii_l.append(radii[i])
            radii_r.append(radii[i])

        else:
            left = _compute_line_intersection(
                (x[i - 1, 0, 0], x[i - 1, 1, 0]),
                (x[i, 0, 0], x[i, 1, 0]),
            )
            right = _compute_line_intersection(
                (x[i - 1, 0, 1], x[i - 1, 1, 1]),
                (x[i, 0, 1], x[i, 1, 1]),
            )

            verts_l.append(left)
            verts_r.append(right)

            if radii[i + 1] != 0:
                # Need to adjust radii according to the width at the turning point. Radii should be
                # Determine direction we are turning in. Positive is left, negative is right

                angle_l = _compute_angle(
                    np.diff(x[i - 1, :, 0], axis=0),
                    np.diff(x[i, :, 0], axis=0),
                )
                angle_r = _compute_angle(
                    np.diff(x[i - 1, :, 1], axis=0),
                    np.diff(x[i, :, 1], axis=0),
                )

                radii_l.append(np.max(radii[i] - np.sign(angle_l) * width[i] / 2, 0))
                radii_r.append(np.max(radii[i] + np.sign(angle_r) * width[i] / 2, 0))
            else:
                radii_l.append(0)
                radii_r.append(0)

        if i == len(x) - 1:
            verts_l.append(x[-1, 1, 0])
            verts_r.append(x[-1, 1, 1])
            radii_l.append(radii[i + 1])
            radii_r.append(radii[i + 1])

    vertices = np.vstack((verts_l, verts_r[::-1]))
    radii = np.concatenate([radii_l, radii_r[::-1]])

    # import matplotlib as mpl

    # mpl.use("qt5agg")
    # import matplotlib.pyplot as plt

    # print(x)
    # x = x.reshape(-1, 2)
    # fig, ax = plt.subplots()
    # ax.scatter(points[:, 0], points[:, 1], color="C0")
    # ax.scatter(x[:, 0], x[:, 1], color="C2")
    # ax.scatter(vertices[:, 0], vertices[:, 1], color="C1")
    # plt.show()
    # import ipdb

    # ipdb.set_trace()
    # pass
    return vertices, radii

    for i in range(N):
        # Compute directions for segments before and after the current point
        # This is the direction from the _center_, not accounting for varying widths
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
            verts_l[i] = points[i] + width[0][0] / 2 * perp_next
            verts_r[i] = points[i] - width[0][0] / 2 * perp_next
            radii_l[i] = radii[i]
            radii_r[i] = radii[i]

        elif i == N - 1:
            verts_l[i] = points[i] + width[-1][1] / 2 * perp_prev
            verts_r[i] = points[i] - width[-1][1] / 2 * perp_prev
            radii_l[i] = radii[i]
            radii_r[i] = radii[i]

        else:
            import ipdb

            ipdb.set_trace()
            pass
            incoming_l = points[i] + width[i] / 2 * perp_prev
            incoming_r = points[i] - width[i] / 2 * perp_prev
            outgoing_l = points[i] + width[i] / 2 * perp_next
            outgoing_r = points[i] - width[i] / 2 * perp_next

            # Compute intersection point for right/left sides
            verts_l[i] = _compute_intersection(incoming_l, direction_prev, outgoing_l, direction_next)
            verts_r[i] = _compute_intersection(incoming_r, direction_prev, outgoing_r, direction_next)

            if radii[i] != 0:
                # Need to adjust radii according to the width at the turning point. Radii should be
                # Determine direction we are turning in. Positive is left, negative is right
                angle = _compute_angle(direction_prev, direction_next)
                radii_l[i] = np.max(radii[i] - np.sign(angle) * width[i] / 2, 0)
                radii_r[i] = np.max(radii[i] + np.sign(angle) * width[i] / 2, 0)

    # Combine left and right vertices in counter-clockwise order
    vertices = np.vstack((verts_l, verts_r[::-1]))

    radii = np.concatenate([radii_l, radii_r[::-1]])

    return vertices, radii


def stripe_layer(config, size):
    layer = Layer(size)

    vertices, radii = _compute_verticies(config.path, config.radii, width=config.width)

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
