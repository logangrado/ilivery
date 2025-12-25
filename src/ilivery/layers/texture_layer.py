#!/usr/bin/env python3


import numpy as np
from PIL import Image


from ilivery import TEXTURE_DIR
from ilivery.layer import Layer


def carbon_fiber(size=(2048, 2048)):
    texture_dir = TEXTURE_DIR / "carbon_fiber_2"

    texture = Image.open(texture_dir / "texture.jpg")
    spec_metallic = Image.open(texture_dir / "spec_metallic.jpg")
    spec_roughness = Image.open(texture_dir / "spec_roughness.jpg")

    spec_array = np.array(spec_metallic)
    spec_array[:, :, 1] = 0
    spec_array[:, :, 2] = 0

    spec_array[:, :, 1] = np.array(spec_roughness)[:, :, 1]

    spec = Image.fromarray(spec_array)

    spec.putalpha(255)
    texture.putalpha(255)

    # Adjust texture/spec size to match
    if texture.size < size:
        raise NotImplementedError

    if texture.size != size:
        texture = texture.crop((0, 0, size[0], size[1]))
        spec = spec.crop((0, 0, size[0], size[1]))

    return texture, spec


def texture_layer(config, size: tuple[int]) -> Layer:
    if config.texture == "CARBON_FIBER":
        paint, spec = carbon_fiber(size)

    else:
        raise ValueError("")

    layer = Layer.from_image(paint, spec)

    return layer
