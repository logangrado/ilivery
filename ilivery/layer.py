#!/usr/bin/env python3

from typing import Union
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageEnhance

from ilivery import utils


class Layer:
    def __init__(self, size):
        self._paint = Image.new(size=size, mode="RGBA")
        self._spec = Image.new(size=size, mode="RGBA")

    def __eq__(self, other):
        return (
            (self.size == other.size)
            & ((np.array(self._paint) == np.array(other._paint)).all())
            & ((np.array(self._spec) == np.array(other._spec)).all())
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} size={self.size[0]}x{self.size[1]} at {hex(id(self))}>"

    @property
    def size(self):
        return self._paint.size

    @classmethod
    def from_image(cls, image: Image.Image, spec: Union[str, Image.Image, None] = None) -> "Layer":
        layer = Layer(image.size)
        layer._paint = image

        if spec is None:
            pass
        elif isinstance(spec, tuple):
            layer = layer.set_spec(spec)
        elif isinstance(spec, Image.Image):
            if not spec.size == image.size:
                raise ValueError("Spec and paint must be same size")
            layer._spec = spec
        else:
            raise NotImplementedError("")

        return layer

    @classmethod
    def from_color(cls, size, color, spec=None):
        layer = Layer(size)

        layer._paint = Image.new(size=size, mode="RGBA", color=color)
        if spec:
            layer._spec = Image.new(size=size, mode="RGBA", color=spec)
        return layer

    def to_numpy(self):
        return {"paint": np.array(self._paint), "spec": np.array(self._spec)}

    def save(self, path, overwrite=False):
        path = Path(path)

        if overwrite:
            if path.exists():
                shutil.rmtree(path)

        path.mkdir(exist_ok=False, parents=True)

        # kwargs = {"format": "tga"}
        kwargs = {"format": "png", "compression_level": 0}

        self._paint.save(fp=path / "paint.png", **kwargs)
        self._spec.save(fp=path / "spec.png", **kwargs)

    @classmethod
    def load(cls, path) -> "Layer":
        layer = Layer((1, 1))

        path = Path(path)

        layer._paint = Image.open(path / "paint.png")
        layer._spec = Image.open(path / "spec.png")
        layer._size = layer._paint.size

        return layer

    def copy(self) -> "Layer":
        new_layer = Layer(self.size)
        new_layer._paint = self._paint.copy()
        new_layer._spec = self._spec.copy()
        return new_layer

    def rotate(self, angle, **kwargs):
        new_layer = self.copy()
        new_layer._paint = new_layer._paint.rotate(angle, **kwargs)
        new_layer._spec = new_layer._spec.rotate(angle, **kwargs)
        return new_layer

    def set_color(self, color) -> "Layer":
        new_layer = self.copy()

        data = np.array(new_layer._paint)
        data[:, :, :3] = color
        data[:, :, 3] = 255

        new_layer._paint = Image.fromarray(data)

        return new_layer

    def set_spec(self, spec) -> "Layer":
        """Set the spec for the layer, using alpha mask from paint"""
        new_layer = self.copy()

        data = np.array(new_layer._paint)
        data[:, :, :3] = spec

        new_layer._spec = Image.fromarray(data)

        return new_layer

    def mask(self, mask, invert=False) -> "Layer":
        new_layer = self.copy()
        new_layer._paint = utils.img.mask(new_layer._paint, mask, invert)
        new_layer._spec = utils.img.mask(new_layer._spec, mask, invert)

        return new_layer

    def flatten(self, other_layer, dest=(0, 0)) -> "Layer":
        new_layer = self.copy()

        new_layer._paint.alpha_composite(other_layer._paint, dest=dest)
        new_layer._spec.alpha_composite(other_layer._spec, dest=dest)

        return new_layer

    def show(self):
        self._paint.show()

    def show_spec(self):
        self._spec.show()

    def brighten_by_spec(self, a=1, b=0.5):
        self = self.copy()
        spec_data = np.array(self._spec)
        paint_data = np.array(self._paint)
        paint_out = Image.new(size=self._paint.size, mode=self._paint.mode)

        metallic_data = spec_data[:, :, 0]

        # Bin metallic data to levels
        n_bins = 16
        metallic_data = metallic_data // (256 / n_bins) * int(256 / n_bins)

        metallic_unique = np.unique(metallic_data)

        for metallic_level in metallic_unique:
            brightness_value = a + b * (metallic_level / 255)
            level_mask = np.expand_dims(metallic_data == metallic_level, -1)

            level_img = Image.fromarray(paint_data * level_mask)
            level_img = ImageEnhance.Brightness(level_img).enhance(brightness_value)

            paint_out = Image.alpha_composite(paint_out, level_img)

        self._paint = paint_out
        return self
