#!/usr/bin/env python3

from typing import List, Optional

from ilivery.config.base_model import BaseModel
from ilivery.config.layer_configs import LayerConfig


class SectionConfig(BaseModel):
    """
    Section config, composed of multiple layers limited to a section of the template.
    If no section is provided, applies to the entire area of the livery.

    layers: List of layers
    section: Section, which can contain boolean logic. Can be any section (aka layer) defined in the
        template PSD file.
        For example:
            segment.wing                - Only the wing
            segment.body | segment.rear - Logical OR of body and rear
            segment.body & segment.side - Logical AND of body and side
    """

    layers: List[LayerConfig]
    section: Optional[str] = None


class iRacingConfig(BaseModel):
    """
    iracing_paint_path: Path to iRacing paints. Typically /Users/<user>/Documents/iRacing/paint/<car>
    iracing_car_number: iRacing car number, used when saving directly to iRacing
    """

    paint_path: str
    car_number: int


class LiveryConfig(BaseModel):
    """
    Base livery config

    template: Template name, found in resources/templates/
    sections: List of sections to build
    final_mask: Final mask to apply
    iracing_output: iRacing output config, for saving directly to iracing paints
    """

    template: str
    sections: List[SectionConfig]
    final_mask: Optional[str] = None
    iracing_output: Optional[iRacingConfig] = None
