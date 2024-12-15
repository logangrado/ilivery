#!/usr/bin/env python3
from ilivery.layer import Layer

def psd_layer(config, template):
    component = config.layer_name.split('.')
    result = template
    for key in component:
        result = result[key]

    layer = Layer.from_image(result, spec=config.spec)
    return layer
