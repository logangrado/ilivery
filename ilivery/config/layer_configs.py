#!/usr/bin/env python3

from enum import Enum
from typing import List, Union, Annotated, Optional
from typing_extensions import Literal
import re


import pydantic

from ilivery.config.base_model import BaseModel
from ilivery.config.color_configs import Color, Spec, ColorMap, ColorFunction


## LAYERS
## ==================================


class TextureLayer(BaseModel):
    """
    Named texture layer. Applies the given texture everywhere in the layer
    """

    type: Literal["TEXTURE"]
    texture: Literal["CARBON_FIBER"]
    section: Optional[str] = None


class SolidLayer(BaseModel):
    """
    Solid layer. Applies the given color for the entire layer, optionally, with specmap
    """

    type: Literal["SOLID"]
    color: Color
    spec: Optional[Spec] = None


class LogoDecal(BaseModel):
    """
    Logan Grado's custom logo decal
    """

    type: Literal["LOGO"]
    size: int
    facecolor: Color
    edgecolor: Color
    edgewidth: Optional[int] = None
    edgeratio: Optional[float] = None
    facespec: Optional[Spec] = None
    edgespec: Optional[Spec] = None


class NamedDecal(BaseModel):
    """
    Apply a named decal. See decals in resources/decals/ for options

    name: Decal name (in resources/decals/)
    color: Decal color. If none, use decal as is
    spec: Decal spec
    size: Decal size
    """

    type: Literal["NAMED"]
    name: str
    color: Optional[Color] = None
    spec: Optional[Spec] = None
    size: pydantic.conlist(Union[int, None], min_length=2, max_length=2)


class DecalLayer(BaseModel):
    """
    Decal layer. Applies the given decal onto the layer, with optional mirroring

    decal: Decal to apply
    pos: Decal position. (0,0) is the center of the image, with (1,1) being up and to the right
    rotate: If nonzero, rotate the decal
    mirror: Optionally, mirror the decal with the given parameters
    """

    class Mirror(BaseModel):
        """
        Mirror config

        axis: axis to mirror across
        rotate: If true, also rotate the decal when mirroring
        offset: Mirror axis offset
        """

        axis: Literal["x", "y"]
        rotate: bool = False
        offset: int = 0

    type: Literal["DECAL"]
    decal: Annotated[
        Union[
            NamedDecal,
            LogoDecal,
        ],
        pydantic.Discriminator("type"),
    ]
    pos: pydantic.conlist(int, min_length=2, max_length=2)
    rotate: float = 0
    mirror: Optional[Mirror] = None


class ClassDecalLayer(BaseModel):
    """
    Class decal

    class_name: Name of class decal, relative to template
    spec: Decal spec
    """

    type: Literal["CLASS_DECAL"]
    class_name: str
    spec: Spec


class PatchLayer(BaseModel):
    """
    Polygon Patch Layer

    Draw an arbitrary polygon, with given verticies

    verticies: List of verticies
    facecolor: Face color
    edgecolor: Edge color
    facespec: Face spec
    edgespec: Edge spec
    edgewidth: Edge width
    radii: Vertex radius
    mirror_patch: Optionally, mirror the entire patch
    mirror_vertices: Optionally, mirror verticies
    """

    class MirrorConfig(BaseModel):
        axis: Literal["x", "y"]
        offset: int = 0

    type: Literal["PATCH"]
    vertices: List[pydantic.conlist(int, min_length=2, max_length=2)]
    facecolor: Color
    edgecolor: Color
    facespec: Spec
    edgespec: Spec
    edgewidth: int
    radii: Optional[List[int] | int] = None
    mirror_patch: Optional[MirrorConfig] = None
    mirror_vertices: Optional[MirrorConfig] = None


class PatternLayer(BaseModel):
    """Pattern layer"""

    class TrianglePattern(BaseModel):
        """
        Triangle pattern

        triangle_size: Triangle size
        angle: Pattern angle
        facecolor: Triangle face color, mutually exclusive with face_cmap
        face_cmap: Triangle face colormap
        face_cfunc: Triangle face color function
        edgecolor: Triangle edge color
        facespec: Triangle facespec
        facespec: Triangle facespec, mutually exclusive with facespec_cmap
        facespec_cmap: Triangle facespec colormap
        facespec_cfunc: Triangle facespec function
        edgespec: Triangle edge spec
        edgewidth: Triangle edgewidth
        spacing: Spacing between triangles
        """

        type: Literal["TRIANGLES"]
        triangle_size: int
        angle: float = 0
        facecolor: Optional[Color] = None
        face_cmap: Optional[ColorMap] = None
        face_cfunc: Optional[ColorFunction] = None
        edgecolor: Optional[Color] = None
        facespec: Optional[Spec] = None
        facespec_cmap: Optional[ColorMap] = None
        facespec_cfunc: Optional[ColorFunction] = None
        edgespec: Optional[Spec] = None
        edgewidth: int = 0
        spacing: int = 0

    class HexagonPattern(BaseModel):
        type: Literal["HEXAGONS"]
        hexagon_size: int
        angle: float = 0
        facecolor: Optional[Color] = None
        face_cmap: Optional[ColorMap] = None
        face_cfunc: Optional[ColorFunction] = None
        edgecolor: Optional[Color] = None
        facespec: Optional[Spec] = None
        facespec_cmap: Optional[ColorMap] = None
        facespec_cfunc: Optional[ColorFunction] = None
        edgespec: Optional[Spec] = None
        edgewidth: int = 0
        spacing: int = 0

    type: Literal["PATTERN"]
    pattern: Annotated[
        Union[
            TrianglePattern,
            HexagonPattern,
        ],
        pydantic.Discriminator("type"),
    ]


## ==================================

LayerConfig = Annotated[
    Union[
        PatternLayer,
        SolidLayer,
        DecalLayer,
        TextureLayer,
        ClassDecalLayer,
        PatchLayer,
    ],
    pydantic.Discriminator("type"),
]
