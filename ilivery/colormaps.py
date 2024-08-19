#!/usr/bin/env python3

import matplotlib as mpl

from ilivery import utils


class LinearSegmentedColormap:
    def __init__(self, config):
        self._config = config

        colors = [utils.color.standardize_colors(c) for c in config.colors]

        if self._config.segments:
            segments = [0] + self._config.segments + [1]

            colors = [(a, b) for a, b in zip(segments, colors)]

        self._cmap = mpl.colors.LinearSegmentedColormap.from_list("", colors, N=config.n_levels)

    def __call__(self, value):
        return self._cmap(value)


def colormap_from_config(config):
    if config is None:
        return None

    cmaps = {
        "LINEAR_SEGMENTED": LinearSegmentedColormap,
    }

    cmap = cmaps.get(config.type, None)
    if cmap is None:
        raise ValueError(f"Unknown cmap: {config.type}")

    return cmap(config)
