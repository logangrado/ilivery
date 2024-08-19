#!/usr/bin/env python3

import pytest

from ilivery.utils import color as color_utils


class TestStandardizeColors:
    @pytest.mark.parametrize(
        "color, expected",
        [
            ["000000", (0, 0, 0)],
            [(0, 0, 0), (0, 0, 0)],
            [(0.0, 0.0, 0.0), (0, 0, 0)],
            ["101010", (16, 16, 16)],
            [(16, 16, 16), (16, 16, 16)],
            [(0.063, 0.063, 0.063), (16, 16, 16)],
        ],
    )
    def test_single_element(self, color, expected):
        out = color_utils.standardize_colors(color, format="INT")

        assert out == expected

    @pytest.mark.parametrize(
        "color, expected",
        [
            [["000000", "101010"], [(0, 0, 0), (16, 16, 16)]],
            [[(0, 0, 0), (16, 16, 16)], [(0, 0, 0), (16, 16, 16)]],
            [[(0.0, 0.0, 0.0), (0.063, 0.063, 0.063)], [(0, 0, 0), (16, 16, 16)]],
        ],
    )
    def test_multi_element(self, color, expected):
        out = color_utils.standardize_colors(color, format="INT")

        assert out == expected


class TestBrighten:
    @pytest.mark.parametrize(
        "color, factor, expected",
        [
            [[0, 0.5, 1], 0.6, (0.6, 0.8, 1.0)],
            [[0, 128, 255], 0.6, (153, 204, 255)],
            ["#0040FF", 0.6, "#99B2FF"],
        ],
    )
    def test_basic(self, color, factor, expected):
        assert expected == color_utils.brighten(color, factor)


class TestDarken:
    @pytest.mark.parametrize(
        "color, factor, expected",
        [
            [[0, 0.5, 1], 0.6, (0.0, 0.2, 0.4)],
            [[0, 128, 255], 0.6, (0, 51, 102)],
            ["#0040FF", 0.6, "#001966"],
        ],
    )
    def test_basic(self, color, factor, expected):
        assert expected == color_utils.darken(color, factor)
