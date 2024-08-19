#!/usr/bin/env python3

#!/usr/bin/env python

import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon
from matplotlib.transforms import Bbox, BboxTransformTo
import matplotlib.pyplot as plt

from ilivery import utils


def side(a, b, c):
    "On which side of line a-b is point c? Returns -1, 0, or 1."
    return np.sign(np.linalg.det(np.c_[[a, b, c], [1, 1, 1]]))


def find_center(seg, radius):
    "Find center of arc approximating corner at curr."
    if radius == 0:
        return seg[1]

    prev, curr, next = seg
    p0, p1 = prev
    c0, c1 = curr
    n0, n1 = next
    dp = radius * np.hypot(c1 - p1, c0 - p0)
    dn = radius * np.hypot(c1 - n1, c0 - n0)
    p = p1 * c0 - p0 * c1
    n = n1 * c0 - n0 * c1
    try:
        results = np.linalg.solve(
            [[p1 - c1, c0 - p0], [n1 - c1, c0 - n0]],
            [[p - dp, p - dp, p + dp, p + dp], [n - dn, n + dn, n - dn, n + dn]],
        )
    except np.linalg.LinAlgError:
        raise ValueError(f"Unable to find center, points are likely on a line:\n{np.array(seg)}")
    side_n = side(prev, curr, next)
    side_p = side(next, curr, prev)
    for r in results.T:
        if (side(prev, curr, r), side(next, curr, r)) == (side_n, side_p):
            return r
    raise ValueError("Cannot find solution")


def proj(seg, center):
    "Project center onto lines prev-curr and next-curr."
    prev, curr, next = seg
    p0, p1 = prev = np.asarray(prev)
    c0, c1 = curr = np.asarray(curr)
    n0, n1 = next = np.asarray(next)
    pc = curr - prev
    nc = curr - next
    pc2 = np.dot(pc, pc)
    nc2 = np.dot(nc, nc)
    return (prev + np.dot(center - prev, pc) / pc2 * pc, next + np.dot(center - next, nc) / nc2 * nc)


def rad2deg(angle):
    return angle * 180.0 / np.pi


def angle(center, point):
    x, y = np.asarray(point) - np.asarray(center)
    return np.arctan2(y, x)


def arc_path(center, start, end):
    "Return a Path for an arc from start to end around center."
    # matplotlib arcs always go ccw so we may need to mirror
    mirror = side(center, start, end) < 0
    if mirror:
        start *= [1, -1]
        center *= [1, -1]
        end *= [1, -1]
    return Path.arc(rad2deg(angle(center, start)), rad2deg(angle(center, end))), mirror


def _points_are_collinear(p1, p2, p3):
    """
    Determine if three 2D points are collinear.

    :param p1: A tuple representing the first point (x1, y1)
    :param p2: A tuple representing the second point (x2, y2)
    :param p3: A tuple representing the third point (x3, y3)
    :return: True if the points are collinear, False otherwise
    """
    # Calculate the area of the triangle formed by the three points
    # Area formula: 0.5 * |x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)|
    area = p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])

    # If the area is zero, the points are collinear
    return area == 0


def compute_path(vertices, radii):
    "Return a Path for a closed rounded polygon."

    vertices, radii = _remove_duplicate_points(vertices, radii)

    if np.isscalar(radii):
        radii = np.repeat(radii, len(vertices))
    else:
        radii = np.asarray(radii)
    path_vertices = []
    path_codes = []
    first = True
    for i in range(len(vertices)):
        if i == 0:
            seg = (vertices[-1], vertices[0], vertices[1])
        elif i == len(vertices) - 1:
            seg = (vertices[-2], vertices[-1], vertices[0])
        else:
            seg = vertices[i - 1 : i + 2]

        radius = radii[i]
        if radius == 0:
            radius = 1e-10

        # Determine if the segment is on a line
        if not _points_are_collinear(*seg):
            center = find_center(seg, radius)
            a, b = proj(seg, center)
            arc, mirror = arc_path(center, a, b)
            m = [1, 1] if not mirror else [1, -1]
            bb = Bbox([center, center + (radius, radius)])
            iter = arc.iter_segments(BboxTransformTo(bb))

            for vertex, code in iter:
                if code == Path.CURVE4:
                    path_vertices.extend([m * vertex[0:2], m * vertex[2:4], m * vertex[4:6]])
                    path_codes.extend([code, code, code])
                elif code == Path.MOVETO:
                    path_vertices.append(m * vertex)
                    if first:
                        path_codes.append(Path.MOVETO)
                        first = False
                    else:
                        path_codes.append(Path.LINETO)

    path_vertices.append([0, 0])
    path_codes.append(Path.CLOSEPOLY)

    return Path(path_vertices, path_codes)


def _compute_intersection(a0, a1, b0, b1):
    A = np.array([a0, a0 + a1])
    B = np.array([b0, b0 + b1])
    t, s = np.linalg.solve(np.array([A[1] - A[0], B[0] - B[1]]).T, B[0] - A[0])
    intersection = (1 - t) * A[0] + t * A[1]
    return intersection


def _unpack_or_repeat(x, n):
    if not isinstance(x, (list, tuple, np.ndarray)):
        x = [x] * n
    else:
        if len(x) != n:
            raise ValueError(f"Expected length {n}, got {len(x)}")
    return tuple(x)


def _rot_matrix(theta, scale=False):
    theta = theta / 180 * np.pi
    out = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    if scale:
        out = out / np.cos(theta)
    return out


def patch_path_verts(verts, widths, radii, angle_start=None, angle_end=None):
    verts = np.array(verts)
    if np.isscalar(widths):
        widths = np.repeat(widths, len(verts) - 1)

    if np.isscalar(radii):
        radii = np.repeat(radii, len(verts))
    else:
        radii = np.asarray(radii)

    path_left, path_right = [], []
    last_vec_left = None
    last_vec_right = None
    for i in range(len(verts)):
        if i + 1 < len(verts):
            a, b = verts[i], verts[i + 1]
            w0, w1 = _unpack_or_repeat(widths[i], 2)
        else:
            a, b = verts[-2], verts[-1]
            w0, w1 = _unpack_or_repeat(widths[-1], 2)[::-1]

        vec = (b - a) / np.linalg.norm(b - a)
        ortho_vec = np.array([[0, 1], [-1, 0]]) @ (vec)
        if i == 0 and angle_start:
            ortho_vec = ortho_vec @ _rot_matrix(angle_start, scale=True)
        if i == len(verts) - 1 and angle_end:
            ortho_vec = ortho_vec @ _rot_matrix(angle_end, scale=True)

        left_point = verts[i] - ortho_vec * w0 / 2
        right_point = verts[i] + ortho_vec * w0 / 2

        if w0 != w1:
            vec_left = (b - ortho_vec * w1 / 2) - left_point
            vec_right = (b + ortho_vec * w1 / 2) - right_point
            vec_left /= np.linalg.norm(vec_left)
            vec_right /= np.linalg.norm(vec_right)
        else:
            vec_left, vec_right = vec, vec

        if i == 0 or i + 1 == len(verts):
            path_left.append(left_point)
            path_right.append(right_point)

        else:
            path_left.append(_compute_intersection(path_left[-1], last_vec_left, left_point, vec_left))
            path_right.append(_compute_intersection(path_right[-1], last_vec_right, right_point, vec_right))

        last_vec_left = vec_left
        last_vec_right = vec_right

    path = np.array(path_right + path_left[::-1])
    radii = np.array(radii.tolist() + radii.tolist()[::-1])

    path, radii = _remove_duplicate_points(path, radii)

    return path, radii


def _remove_duplicate_points(vertices, radii):
    if np.isscalar(radii):
        radii = np.repeat(radii, len(vertices))
    else:
        radii = np.asarray(radii)

    _, inds = np.unique(vertices, axis=0, return_index=True)
    inds = sorted(inds)

    vertices = vertices[inds]
    radii = radii[inds]

    return vertices, radii


def poly_patch(vertices, radii, facecolor, edgecolor=None, linewidth=None, size=None):
    if size is None:
        size = np.ceil(np.array(vertices).max(axis=0) - np.array(vertices).min(axis=0)).astype(int).tolist()

    fig, ax = utils.mpl.get_fig(size)

    vertices = np.array(vertices)
    assert len(vertices.shape) == 2
    assert vertices.shape[1] == 2

    # face/edge color must be converted to floats
    facecolor = np.array(facecolor) / 255
    edgecolor = np.array(edgecolor) / 255

    if edgecolor is None:
        edgecolor = facecolor

    path = compute_path(vertices, radii)
    patch = PathPatch(path, edgecolor=edgecolor, facecolor=facecolor, linewidth=linewidth)
    ax.add_patch(patch)

    utils.mpl.prep_ax(ax)

    ax.set_xlim(0, size[0])
    ax.set_ylim(0, size[1])

    img = utils.mpl.fig_to_img(fig, size)

    return img


if __name__ == "__main__":
    vertices = [
        (0, 0),
        (0, 50),
        (50, 50),
        (50, 0),
    ]

    radii = [0, 50, 0, 0]
    size = (100, 100)

    facecolor = (0.5, 0, 0, 1)
    edgecolor = None
    linewidth = None
    # edgecolor=(0,0.5,0,1)
    # linewidth=4

    poly_patch(size, vertices, radii, facecolor, edgecolor, linewidth)
