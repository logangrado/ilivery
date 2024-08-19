#!/usr/bin/env python3
import pytest

from ilivery.config.livery_config import LiveryConfig
from ilivery.build_livery import build_livery


class TestBuildLivery:
    def test_basic(self, compare_ref_layer):
        config = {
            "template": "test_template",
            "sections": [
                {
                    "layers": [
                        {
                            "type": "SOLID",
                            "color": [255, 0, 0],
                            "spec": [0, 255, 0],
                        }
                    ],
                }
            ],
        }

        config = LiveryConfig.model_validate(config)

        livery = build_livery(config, no_cache=True)

        compare_ref_layer(livery._livery)

    def test_basic_decal(self, compare_ref_layer):
        config = {
            "template": "test_template",
            "sections": [
                {
                    "layers": [
                        {
                            "type": "SOLID",
                            "color": [255, 0, 0],
                            "spec": [0, 255, 0],
                        },
                        {
                            "type": "DECAL",
                            "decal": {
                                "type": "NAMED",
                                "name": "MAASR",
                                "color": [0, 255, 0],
                                "spec": [0, 0, 255],
                                "size": [100, None],
                            },
                            "pos": [0, 0],
                            "mirror": None,
                            "rotate": 0,
                        },
                    ],
                }
            ],
        }

        config = LiveryConfig.model_validate(config)

        livery = build_livery(config, no_cache=True)

        compare_ref_layer(livery._livery)

    def test_decal_sectioned(self, compare_ref_layer):
        config = {
            "template": "test_template",
            "sections": [
                {
                    "section": "segments.left",
                    "layers": [
                        {
                            "type": "SOLID",
                            "color": [255, 0, 0],
                            "spec": [0, 255, 0],
                        },
                        {
                            "type": "DECAL",
                            "decal": {
                                "type": "NAMED",
                                "name": "MAASR",
                                "color": [0, 255, 0],
                                "spec": [0, 0, 255],
                                "size": [50, None],
                            },
                            "pos": [0, 50],
                            "mirror": {"axis": "y"},
                            "rotate": 0,
                        },
                    ],
                }
            ],
        }

        config = LiveryConfig.model_validate(config)

        livery = build_livery(config, no_cache=True)

        compare_ref_layer(livery._livery)

    def test_basic_section_masking(self, compare_ref_layer):
        config = {
            "template": "test_template",
            "sections": [
                {
                    "section": "segments.left",
                    "layers": [
                        {
                            "type": "SOLID",
                            "color": [255, 0, 0],
                            "spec": [0, 255, 0],
                        },
                    ],
                },
            ],
        }

        config = LiveryConfig.model_validate(config)

        livery = build_livery(config, no_cache=True)

        compare_ref_layer(livery._livery)

    def test_basic_section_logic(self, compare_ref_layer):
        config = {
            "template": "test_template",
            "sections": [
                {
                    "section": "segments.left & segments.top",
                    "layers": [
                        {
                            "type": "SOLID",
                            "color": [255, 0, 0],
                            "spec": [0, 255, 0],
                        },
                    ],
                },
            ],
        }

        config = LiveryConfig.model_validate(config)

        livery = build_livery(config, no_cache=True)

        compare_ref_layer(livery._livery)

    def test_final_mask(self, compare_ref_layer):
        config = {
            "template": "test_template",
            "sections": [
                {
                    "layers": [
                        {
                            "type": "SOLID",
                            "color": [255, 0, 0],
                            "spec": [0, 255, 0],
                        }
                    ],
                }
            ],
            "final_mask": "~segments.mask",
        }

        config = LiveryConfig.model_validate(config)

        livery = build_livery(config, no_cache=True)

        compare_ref_layer(livery._livery)


class TestBuildLiveryCaching:
    pass
