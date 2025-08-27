#!/usr/bin/env python3

import functools
import hashlib
import json
import logging
import shutil
import tqdm
import datetime

from pathlib import Path

from ilivery import LAYER_CACHE_DIR, TEMPLATE_DIR, utils
from ilivery.layer import Layer
from ilivery.layers import layer_from_config
from ilivery.utils.executor import make_executor

logger = logging.getLogger(__name__)


def _get_cache_path(path, sha):
    return path / sha[:2] / sha[2:]


def _build_layer(i, section_mask, section_dest, section_size, layer_config, template_path, template, base_size):
    if layer_config is None:
        return Layer(section_size)

    layer = layer_from_config(layer_config, size=section_size, template_path=template_path, template=template)

    if section_mask is not None:
        layer = layer.mask(section_mask)

    # Merge the result into base
    # print(f"{i}: {layer} {section_dest}")
    layer = Layer(base_size).flatten(layer, section_dest)
    # layer = base.flatten(layer, section_dest)
    return layer


def _merge(left, right):
    return left.flatten(right)


def _recursive_build(left, right, build_list, build_func, merge_func, pool, pbar):
    if right - left >= 2:
        center = left + (right - left) // 2

        left_f = pool.submit(_recursive_build, left, center, build_list, build_func, merge_func, pool, pbar)
        right_f = pool.submit(_recursive_build, center, right, build_list, build_func, merge_func, pool, pbar)

        return merge_func(left_f.result(), right_f.result())
    else:
        result = build_func(left, **build_list[left])
        if pbar is not None:
            # ensure thread-safe increments
            pbar.update(1)
        return result


class Livery:
    def __init__(self, config, no_cache):
        self._config = config

        self._template_path = TEMPLATE_DIR / config.template / "segmented.psd"
        logger.info("Loading template")
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
                    except Exception:
                        print("Invalid cache")
                        shutil.rmtree(layer_cache)

        if livery is None:
            livery = Layer(self._size)
            next_layer = 0

        return livery, next_layer

    def build(self, threads=16, progress=True):
        t0 = datetime.datetime.now()
        if not self._no_cache:
            raise NotImplementedError("Cache not implemented!")
        # livery, next_layer = self._load_latest_cached(no_cache=self._no_cache)
        # base = Layer(self._size)
        kwargs = {"template_path": self._template_path, "template": self._template, "base_size": self._size}

        logger.info("Building layer list")
        build_list = []
        for section_config in self._config.sections:
            section_size = self._size
            section_dest = (0, 0)
            section_mask = None
            if section_config.section is not None:
                print(f"BUILDING MASK: {section_config.section}")
                section_mask, bbox = utils.psd.get_section_mask(section_config.section, self._template)
                section_dest = (bbox[0], bbox[1])
                section_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])

            for layer_config in section_config.layers:
                build_list.append(
                    {
                        **kwargs,
                        **{
                            "section_mask": section_mask,
                            "section_dest": section_dest,
                            "section_size": section_size,
                            "layer_config": layer_config,
                        },
                    }
                )

        logger.info("Building layers")
        with make_executor(threads) as pool, tqdm.tqdm(
            total=len(build_list), desc="Layers", disable=not progress
        ) as pbar:
            livery = _recursive_build(0, len(build_list), build_list, _build_layer, _merge, pool, pbar)

        logger.info("Applying final mask")
        if self._config.final_mask:
            mask, bbox = utils.psd.get_section_mask(self._config.final_mask, self._template, crop_mask=False)
            livery = livery.mask(mask)

        logger.info("Brightening by spec")
        self._livery = livery.brighten_by_spec()
        self._livery = livery
        self._built = True

        dt = (datetime.datetime.now() - t0).total_seconds()
        logger.info(f"Livery built in {dt:0.2f}s")

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


def build_livery(config, no_cache, debug):
    livery = Livery(config, no_cache)

    threads = 16
    if debug:
        threads = 1
    livery.build(threads=threads)

    return livery
