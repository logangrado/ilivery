from typing import List

import numpy as np


def _standardize_color(color, format="FLOAT"):
    # Standardize all to uint8 first
    if isinstance(color, str):
        if color.startswith("#"):
            color = color[1:]
        out = [int(color[2 * i : 2 * i + 2], 16) for i in range(3)]

    else:
        out = np.array(color)

        if out.dtype == "float":
            out = out * 255

    # Convert output
    if format.upper() == "FLOAT":
        out = tuple(np.array(out) / 255)
    elif format.upper() == "INT":
        out = tuple(np.array(out).astype("uint8"))
    elif format.upper() == "HEX":
        out = tuple(np.array(out).astype("uint8"))
        out = "#" + "".join([f"{item:02x}" for item in out])
        out = out.upper()

    return out


def _determine_color_format(color):
    """
    Determine format of a single color value
    """
    if isinstance(color, str):
        return "HEX"

    color = np.array(color)
    if color.dtype == int:
        return "INT"
    elif color.dtype == float:
        return "FLOAT"

    raise ValueError(f"Unknown color format: {color}")


def standardize_colors(colors, format="FLOAT"):
    """
    Standardize a list of colors

    Parameters
    ----------

    Returns
    -------
    """
    if isinstance(colors, (list, tuple)) and isinstance(colors[0], (tuple, list, str)):
        return [_standardize_color(c, format) for c in colors]
    else:
        return _standardize_color(colors, format)

    if colors is None:
        return None
    # Check all elements are same type/length

    # Standardize all to uint8 first
    if isinstance(colors[0], str):
        out = [[int(c_str[1 + i : 1 + i + 2], 16) for i in range(3)] for c_str in colors]

    else:
        out = np.array(colors)
        if np.max(colors) <= 1:
            out = out * 255

    # Convert output
    if format.upper() == "FLOAT":
        out = (np.array(out) / 255).tolist()
    elif format.upper() == "INT":
        out = np.array(out).astype("uint8").tolist()
    elif format.upper() == "HEX":
        raise NotImplementedError()

    return out


def color_spread(color: tuple, spread: float) -> List[tuple]:
    """Return a color spread around a given color, where the color spread is
    a list with two elements, the first being `color` darkened by `spread`, and
    the 2nd being lightened by `spread`
    """
    return [darken(color, spread), brighten(color, spread)]


def brighten(color, factor):
    factor = max(factor, 0)
    factor = min(factor, 1)

    fmt = _determine_color_format(color)

    color = _standardize_color(color, format="FLOAT")

    out = np.array(color) * (1 - factor) + np.ones_like(color) * factor

    return _standardize_color(out.tolist(), format=fmt)


def darken(color, factor):
    factor = max(factor, 0)
    factor = min(factor, 1)

    fmt = _determine_color_format(color)

    color = _standardize_color(color, format="FLOAT")

    out = np.array(color) * (1 - factor) + np.zeros_like(color) * factor

    return _standardize_color(out.tolist(), format=fmt)
