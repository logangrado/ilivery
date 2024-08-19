#!/usr/bin/env python3

import json
import hashlib
import logging
import shutil
from pathlib import Path

from ilivery.layer import Layer
from ilivery import TEMPLATE_DIR, LAYER_CACHE_DIR, utils
from ilivery import utils
from ilivery.layers import layer_from_config

logger = logging.getLogger(__name__)


def _get_cache_path(path, sha):
    return path / sha[:2] / sha[2:]


class Livery:
    def __init__(self, config, no_cache):
        self._config = config

        self._template_path = TEMPLATE_DIR / config.template / "segmented.psd"
        self._template, template_hash, template_size = utils.psd.load_layers(self._template_path)
        self._no_cache = no_cache

        self._layers = []

        self._size = template_size
        self._built = False
        # self._compute_cache(template_hash)

    def _compute_cache(self, template_hash):
        hashes = {"template": template_hash, "layers": []}
        last_hash = template_hash

        for layer_config in self._config.layers:
            config_str = json.dumps(layer_config.dict(), sort_keys=True)

            sha256 = hashlib.sha256()
            sha256.update(last_hash.encode())
            sha256.update(config_str.encode())
            last_hash = sha256.hexdigest()
            hashes["layers"].append(last_hash)

        # Compute cache paths
        self._layer_cache_paths = [_get_cache_path(LAYER_CACHE_DIR, sha) for sha in hashes["layers"]]

    def _load_latest_cached(self, no_cache):
        # Find the latest cached layer and load it
        livery = None
        if not self._no_cache:
            for i in range(len(self._layer_cache_paths))[::-1]:
                if (layer_cache := self._layer_cache_paths[i]).exists():
                    try:
                        next_layer = i + 1
                        livery = Layer.load(layer_cache)
                        break
                    except:
                        print("Invalid cache")
                        shutil.rmtree(layer_cache)

        if livery is None:
            livery = Layer(self._size)
            next_layer = 0

        return livery, next_layer

    def build(self):
        if not self._no_cache:
            raise NotImplementedError("Cache not implemented!")
        livery, next_layer = self._load_latest_cached(no_cache=self._no_cache)

        kwargs = {
            "template_path": self._template_path,
        }

        for i, section_config in enumerate(self._config.sections):
            logger.info(f"SECTION [{i+1}/{len(self._config.sections)}]")
            # Get the section, if required
            mask = None
            dest = (0, 0)
            size = self._size

            if section_config.section is not None:
                mask, bbox = utils.psd.get_section_mask(section_config.section, self._template)
                dest = (bbox[0], bbox[1])
                size = (bbox[2] - bbox[0], bbox[3] - bbox[1])

            layer_kwargs = {**kwargs, **{"size": size}}
            section = Layer(size)

            # Build all layers
            for j, layer_config in enumerate(section_config.layers):
                logger.info(f"  LAYER [{j+1}/{len(section_config.layers)}]")
                # Build layer
                layer = layer_from_config(layer_config, **layer_kwargs)

                # Flatten
                section = section.flatten(layer)

            # Mask the section, if required
            if mask:
                # Crop mask to bbox
                mask = mask.crop(bbox)
                # Mask section
                section = section.mask(mask)

            # Flatten section into livery
            livery = livery.flatten(section, dest)

        if self._config.final_mask:
            mask, bbox = utils.psd.get_section_mask(self._config.final_mask, self._template)
            livery = livery.mask(mask)

        self._livery = livery.brighten_by_spec()
        self._livery = livery
        self._built = True

    def show(self):
        self._livery.show()

    def save(self):
        if not self._built:
            self.build()

        if not self._config.iracing_output:
            raise ValueError("Must provide iracing output config to save paint")

        path = Path(self._config.iracing_output.paint_path)
        path.mkdir(exist_ok=True, parents=True)

        paint_path = path / f"car_{self._config.iracing_output.car_number}.tga"
        spec_path = path / f"car_spec_{self._config.iracing_output.car_number}.tga"

        print(f"Saving paint to path: {paint_path}")
        self._livery._paint.save(fp=paint_path, format="tga", compression="tga_rle")
        self._livery._spec.save(fp=spec_path, format="tga", compression="tga_rle")


def build_livery(config, no_cache):
    livery = Livery(config, no_cache)

    livery.build()

    return livery
