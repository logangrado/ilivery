#!/usr/bin/env python3

import numpy as np


def rotation_matrix(angle):
    theta = np.pi * angle / 180
    return np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])


def verts_from_path(vert_path):
    """Convert vert path to vertices"""
    verts = [vert_path[0]]
    direction = np.array([1, 0])
    for item in vert_path[1:]:
        if len(item) == 2:
            angle, distance = item
        else:
            angle, distance, abs_rel = item
            assert abs_rel.upper() == "ABS"
            direction = np.array([1, 0])

        rot_matrix = rotation_matrix(angle)

        direction = rot_matrix @ direction

        verts.append(verts[-1] + direction * distance)

    return np.array(verts)
