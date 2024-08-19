from PIL import Image, ImageEnhance
import numpy as np


def mask(img, mask, invert=False):
    if invert:
        mask_alpha = np.array(mask)[:, :, 3] != 255
    else:
        mask_alpha = np.array(mask)[:, :, 3] == 255
    mask_alpha = np.expand_dims(mask_alpha, -1)

    img = Image.fromarray(np.array(img) * mask_alpha, mode="RGBA")
    return img


def enhance(img, brightness=1, contrast=1):
    if brightness != 1:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1:
        img = ImageEnhance.Contrast(img).enhance(contrast)

    return img
