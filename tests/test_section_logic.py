#!/usr/bin/env python3

from typing import Callable

import numpy as np
import pytest
from PIL import Image

from ilivery import TEMPLATE_DIR
from ilivery.utils import psd


def _run_test(expression: str, compare_ref_image: Callable):
    # Test basic select
    template_path = TEMPLATE_DIR / "test_template/segmented.psd"
    template, _, _ = psd.load_layers(template_path)

    mask, _ = psd.get_section_mask(expression, template, crop_mask=False)

    mask = (mask * 255).astype("uint8")
    mask = np.stack([mask] * 4, -1)

    mask = Image.fromarray(mask)

    compare_ref_image(mask)


class TestSectionLogic:
    @pytest.mark.parametrize(
        "expression",
        [
            "segments.left",
            "~segments.left",
            "segments.left & segments.top",
            "segments.left | segments.top",
            "~segments.left & ~segments.top",
            "~segments.left | ~segments.top",
        ],
    )
    def test_expressions(self, compare_ref_image, expression):
        _run_test(expression, compare_ref_image)
