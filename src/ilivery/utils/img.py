import numpy as np
from PIL import Image, ImageEnhance


def mask(img: Image.Image, mask: np.ndarray, invert: bool = False) -> Image.Image:
    """
    Apply a boolean mask to an image, returning an RGBA Image.
    - img: PIL Image (any mode; will be converted to RGBA)
    - mask: 2D boolean array of shape (H, W)
    - invert: if True, use the logical NOT of `mask`

    """
    if mask.ndim != 2:
        raise ValueError(f"mask must be 2D (H, W); got shape {mask.shape}")
    if mask.dtype != np.bool_:
        # Accept 0/255 or 0/1 integer arrays, but use booleans internally.
        mask = mask.astype(bool, copy=False)

    # Ensure RGBA and shape match
    img_rgba = img.convert("RGBA")
    w, h = img_rgba.size
    if mask.shape != (h, w):
        raise ValueError(f"mask shape {mask.shape} does not match image size {(w, h)}")

    if invert:
        mask = ~mask

    # Array math (copy to avoid mutating the backing buffer)
    arr = np.asarray(img_rgba, dtype=np.uint8).copy()  # (H, W, 4)

    # Zero out all channels where mask is False (fast, in-place)
    arr[~mask] = 0

    return Image.fromarray(arr, mode="RGBA")


def enhance(img, brightness=1, contrast=1):
    if brightness != 1:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1:
        img = ImageEnhance.Contrast(img).enhance(contrast)

    return img
