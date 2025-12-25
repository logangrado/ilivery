#!/usr/bin/env python3

import re
from typing import List, Optional, Literal, Annotated, Union

import pydantic
from pydantic_core import core_schema

from ilivery.config.base_model import BaseModel


class Color:
    """
    Standardized color type. Accepts colors as any of:
    - Hex value (#000000 - #FFFFFF)
    - List of floats (0.0 - 1.0)
    - List of 8-bit int (0 - 255)

    All values are standardized to list of 8-bit ints
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, *args) -> core_schema.CoreSchema:
        # Handle None and custom validation
        return core_schema.union_schema(
            [
                core_schema.none_schema(),
                core_schema.with_info_plain_validator_function(cls.validate),
            ]
        )

    @classmethod
    def validate(cls, value, *args):
        if isinstance(value, str):
            if not re.match(r"^#[0-9A-Fa-f]{6}$", value):
                raise ValueError("Color string must be in the form #FFFFFF")
            # Convert hex string to a list of integers
            value = [int(value[i : i + 2], 16) for i in range(1, 7, 2)]
        elif isinstance(value, (tuple, list)):
            if all(isinstance(i, int) for i in value):
                if not all(0 <= i <= 255 for i in value):
                    raise ValueError("All integers in the list must be in the range 0-255")
            elif all(isinstance(i, float) for i in value):
                if not all(0 <= i <= 1 for i in value):
                    raise ValueError("All floats in the list must be in the range 0-1")
                # Convert floats to integers in the range 0-255
                value = [int(i * 255) for i in value]
            else:
                raise ValueError("List must contain either all integers or all floats")
        else:
            raise ValueError("Color must be a string, a list of integers, or a list of floats")
        return tuple(value)


class Spec(Color):
    """
    Standardized spec type. Accepts all the same types as Color, but additionall, accepts
    named specs, listed below.
    """

    NAMED_SPECS = {
        "FLAT": (0.0, 0.8, 0.0),
        "MATTE": (0.0, 0.5, 0.0),
        "SATIN": (0.0, 0.2, 0.0),
        "GLOSS": (0.0, 0.0, 0.0),
        "CHROME": (1.0, 0.0, 0.0),
        "METALLIC": (0.9, 0.4, 0.0),
        "CANDY": (0.5, 0.1, 0.0),
        "PEARL": (0.6, 0.2, 0.0),
        "VELVET": (0.8, 1.0, 0.0),
    }

    @classmethod
    def validate(cls, value, *args):
        if isinstance(value, str) and value in cls.NAMED_SPECS:
            value = cls.NAMED_SPECS[value]
        out = super().validate(value, *args)

        return out


class _Placeholder(BaseModel):
    """Placeholder config, needed for annotated union below. Delete when we have more than one colormap"""

    type: Literal["_PLACEHOLDER"]


class ColorSpreadConfig(BaseModel):
    """Color spread config. Takes a single color, and returns a tuple of two colors,
    dimmer and brighter than the given color, by `spread` amount.

    Color: color to spread around
    Spread: spread value. 0 spread returns the same value, 1 spread gives black/white.
    """

    color: Color
    spread: float

    @pydantic.model_validator(mode="after")
    def check_segments_length(self) -> "LinearSegmentedColorMap":
        from ilivery.utils.color import color_spread

        return color_spread(self.color, self.spread)


class LinearSegmentedColorMap(BaseModel):
    """
    Standard linearlly segmented colormap

    colors: List of colors, or ColorSpreadConfigs
    segments: List of segments. If provided, can break up the color-range non-uniformly.
    n_levels: Number of discrete color levels
    """

    type: Literal["LINEAR_SEGMENTED"]
    colors: List[Color | ColorSpreadConfig]
    segments: Optional[List[float]] = None
    n_levels: Optional[pydantic.conint(ge=2)] = 256

    @pydantic.model_validator(mode="after")
    def check_segments_length(self) -> "LinearSegmentedColorMap":
        colors = []
        for c in self.colors:
            if isinstance(c, list):
                colors += c
            else:
                colors.append(c)
        self.colors = colors
        if self.segments:
            assert len(self.segments) == len(self.colors) - 2
        return self


ColorMap = Annotated[
    Union[LinearSegmentedColorMap, _Placeholder],
    pydantic.Discriminator("type"),
]


class GradientCFunc(BaseModel):
    """Gradient color function

    direction: Color gradient vector
    range: Return value range, defaults to [0,1]
    """

    type: Literal["GRADIENT"]
    direction: pydantic.conlist(float, min_length=2, max_length=2)
    range: pydantic.conlist(float, min_length=2, max_length=2) = [0, 1]


class RandomUniformCFunc(BaseModel):
    """
    Random uniform color function

    Returns a value drawn from the random uniform distribution, scaled to the given range

    seed: Random seed
    range: Return value range, defaults to [0,1]
    """

    type: Literal["RANDOM_UNIFORM"]
    seed: int = 0
    range: pydantic.conlist(float, min_length=2, max_length=2) = [0, 1]


class SimplexNoiseCFunc(BaseModel):
    """
    Simplex noise clor function

    length_scale: Noise length scale in each direction (x,y)
    angle: Angle to rotate resulting noise
    seed: Random seed
    range: Return value range, defaults to [0,1]
    """

    type: Literal["SIMPLEX_NOISE"]
    length_scale: pydantic.conlist(float, min_length=2, max_length=2)
    angle: float = 0
    seed: int = 0
    range: pydantic.conlist(float, min_length=2, max_length=2) = [0, 1]


class VoronoiCFunc(BaseModel):
    type: Literal["VORONOI"]
    seed: int = 0
    spacing: int
    levels: Union[int, List[float]]
    anisotropy: float = 1
    angle: float = 0


class ComposedCFunc(BaseModel):
    """
    Composed color function. Allows combining multiple color functions into one, such as a gradient
    plus noise, etc.

    color_functions: List of color functions. The result is added together point-wise
    range: Return value range, defaults to [0,1]
    """

    type: Literal["COMPOSED"]
    color_functions: List["ColorFunction"]
    range: pydantic.conlist(float, min_length=2, max_length=2) = [0, 1]


ColorFunction = Annotated[
    Union[
        GradientCFunc,
        RandomUniformCFunc,
        SimplexNoiseCFunc,
        VoronoiCFunc,
        ComposedCFunc,
    ],
    pydantic.Discriminator("type"),
]
