#!/usr/bin/env python3

import functools

import numpy as np
import opensimplex as simplex


def _standardize(data, range):
    data = (data - data.min()) / (data.max() - data.min())

    data = (data - range[0]) * (range[1] - range[0])

    return data


class ColorFunction:
    def __call__(self, x, y):
        pass


class GradientCFunc:
    def __init__(self, config):
        self._config = config
        self._direction = np.array(self._config.direction).reshape(2, 1)
        self._direction = self._direction / np.linalg.norm(self._direction)

    def __call__(self, x, y, standardize=True):
        points = np.array([x, y]).T

        out = (points @ self._direction).reshape(x.shape)

        out = _standardize(out, self._config.range)

        return out


class RandomUniformCFunc:
    def __init__(self, config):
        self._config = config
        self._rnd_state = np.random.RandomState(self._config.seed)

    def __call__(self, x, y):
        out = self._rnd_state.uniform(size=x.shape)

        out = (out - self._config.range[0]) * (self._config.range[1] - self._config.range[0])

        return out


class SimplexNoiseCFunc:
    def __init__(self, config):
        self._config = config

    def __call__(self, x, y):
        simplex.seed(self._config.seed)

        if self._config.angle != 0:
            # Multiply by -1 so we rotate in correct direction (stupid PIL with y going down)
            theta = -1 * self._config.angle / 180 * np.pi
            rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

            xy = np.stack([x, y], axis=-1) @ rot_matrix

            x = xy[..., 0]
            y = xy[..., 1]

        x = x / self._config.length_scale[0]
        y = y / self._config.length_scale[1]

        out = np.vectorize(simplex.noise2)(x, y)

        out = _standardize(out, self._config.range)

        return out


class VoronoiNoiseCFunc:
    def __init__(self, config):
        self._config = config
        self._rnd_state = np.random.RandomState(self._config.seed)

    def __call__(self, x, y):
        x = np.array(x)
        y = np.array(y)

        levels = self._config.levels
        if isinstance(levels, int):
            levels = [1] * levels
        levels = np.array(levels)
        levels = levels / np.sum(levels)

        # Rotate the input points
        # =======================
        # Get anisotropy parameters
        # Multiply by -1 so we rotate in correct direction (stupid PIL with y going down)
        theta = -1 * self._config.angle / 180 * np.pi
        rot_matrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        scaling_matrix = np.array([[1, 0], [0, self._config.anisotropy]])
        transformation_matrix = np.dot(rot_matrix, scaling_matrix)

        # Transform input points
        xy = np.stack([x, y], axis=-1) @ transformation_matrix
        x = xy[..., 0]
        y = xy[..., 1]

        x_range = (x.min(), x.max())
        y_range = (y.min(), y.max())

        # Determine how many points to generate
        size = np.sqrt((np.diff(x_range) + 1) * (np.diff(y_range) + 1))
        n_points = int((size / self._config.spacing) ** 2)

        # Generate random seed points
        points = self._rnd_state.rand(n_points, 2) * [np.diff(x_range)[0], np.diff(y_range)[0]] + [
            np.min(x_range),
            np.min(y_range),
        ]

        point_color = self._rnd_state.choice(np.arange(len(levels)), size=n_points, p=levels)

        xy = np.stack([x.reshape(-1), y.reshape(-1)]).T

        distances = np.sqrt(np.sum((xy[:, np.newaxis, :] - points[np.newaxis, :, :]) ** 2, axis=-1))

        nearest_point = np.argmin(distances, axis=1)
        # nearest_point_dist = np.min(distances, axis=1)

        # Convert nearest point to it's actual color
        out = point_color[nearest_point]

        out = _standardize(out, (0, 1))
        out = out.reshape(x.shape)

        return out


class ComposedCFunc:
    def __init__(self, config):
        self._config = config
        self._color_funcs = [colorfunc_from_config(c) for c in config.color_functions]

    def __call__(self, x, y):
        results = [cfunc(x, y) for cfunc in self._color_funcs]

        result = functools.reduce(lambda x, y: x + y, results)

        result = _standardize(result, self._config.range)
        return result


def colorfunc_from_config(config) -> ColorFunction:
    if config is None:
        return None

    colorfuncs = {
        "GRADIENT": GradientCFunc,
        "RANDOM_UNIFORM": RandomUniformCFunc,
        "SIMPLEX_NOISE": SimplexNoiseCFunc,
        "COMPOSED": ComposedCFunc,
        "VORONOI": VoronoiNoiseCFunc,
    }

    cfunc = colorfuncs.get(config.type, None)
    if cfunc is None:
        raise ValueError(f"Unknown cfunc: {config.type}")

    return cfunc(config)
