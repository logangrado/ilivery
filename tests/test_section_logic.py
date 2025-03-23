#!/usr/bin/env python3

import pytest

from ilivery.utils import psd
from ilivery import TEMPLATE_DIR


def _run_test(expression, compare_ref_image):
    # Test basic select
    template_path = TEMPLATE_DIR / "test_template/segmented.psd"
    template, _, _ = psd.load_layers(template_path)

    mask, _ = psd.get_section_mask(expression, template)

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
