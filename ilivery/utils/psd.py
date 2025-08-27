import hashlib
import functools
import numpy as np
import re
import shutil
from typing import Iterable

from ilivery import TEMPLATE_DIR
from psd_tools import PSDImage
from PIL import Image

import logging

logger = logging.getLogger(__name__)


def _compute_file_hash(path, buffsize=1024**2):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(buffsize)
            if not data:
                break
            sha256.update(data)

    return sha256.hexdigest()


def _get_cache_path_and_checksum(path):
    cache_path = TEMPLATE_DIR / "cache" / path.relative_to(TEMPLATE_DIR)
    checksum = _compute_file_hash(path)

    paths = {
        "cache": cache_path,
        "checksum": cache_path / "checksum.txt",
        "images": cache_path / "images",
    }

    return cache_path, paths, checksum


def _cache_psd_recursive(cache_dir, group, size, parent_groups=None):
    if not group.is_visible():
        group.visible = True

    if parent_groups is None:
        parent_groups = []
    if parent_groups is not None:
        parent_group_str = "/".join(parent_groups)

    for item in group:
        if item.is_group():
            group_cache_dir = cache_dir / item.name
            _cache_psd_recursive(group_cache_dir, item, size, parent_groups=parent_groups + [group.name])
        else:
            # Remove .tga from end if item names
            name = item.name
            if name.endswith(".tga"):
                name = name[:-4]
            logger.info(f"Caching layer: {parent_group_str}/{name}")
            name = name.replace(".", "/")
            layer_cache_path = (cache_dir / name).with_suffix(".png")
            layer_cache_path.parent.mkdir(exist_ok=True, parents=True)
            item.visible = True

            layer = Image.new(size=size, mode="RGBA")
            layer.alpha_composite(item.composite(), dest=item.offset)

            layer.save(fp=layer_cache_path, format="png", compression_level=0)


def _load_cached_psd(cache_dir, groups=None):
    out = {}
    size = [0, 0]
    for path in cache_dir.glob("*"):
        if path.is_dir():
            if groups is None or path.name in groups:
                out[path.name], group_size = _load_cached_psd(path)

                size[0] = max(size[0], group_size[0])
                size[1] = max(size[1], group_size[1])

        if path.is_file() and path.suffix == ".png":
            logger.debug(f"Loading layer: {path.stem}")
            layer = Image.open(path)

            out[path.stem] = layer
            size[0] = max(size[0], layer.size[0])
            size[1] = max(size[1], layer.size[1])

    return out, size


def _format_keys_recursive(x, indent=0):
    out = ""
    for key in sorted(x.keys()):
        out += "\n" + " " * indent + key
        value = x[key]
        if isinstance(value, dict):
            out += _format_keys_recursive(value, indent + 2)

    return out


def _iter_leaf_images(node) -> Iterable[Image.Image]:
    """Yield all PIL images under a node (recursive if dict)."""
    if isinstance(node, dict):
        for v in node.values():
            yield from _iter_leaf_images(v)
    else:
        yield node  # assume PIL.Image.Image


def _alpha_bool(img: Image.Image) -> np.ndarray:
    """Get a 2D boolean mask from the image's alpha (or luminance if no alpha)."""
    key = (id(img), img.size)

    if "A" in img.getbands():
        a = np.asarray(img.getchannel("A"), dtype=np.uint8)  # HxW
    else:
        # Fallback: luminance; Pillow convert('L') is fast and releases the GIL
        a = np.asarray(img.convert("L"), dtype=np.uint8)

    mask = a > 0  # True where 'on' (robust to antialiasing, not just ==255)
    return mask


def _get_section_component_bool(section, psd_layers) -> np.ndarray:
    img = template  # however you look it up; e.g., nested dict via dots
    for part in name.split("."):
        img = img[part]  # img is a PIL.Image.Image
    if img.mode == "RGBA":
        return np.asarray(img.getchannel("A")) > 0
    # fall back to luminance
    return np.asarray(img.convert("L"), dtype=np.uint8) > 0


def _get_section_component(section, psd_layers):
    sections = section.split(".")

    section_masks = functools.reduce(lambda x, y: x.get(y, {}), [psd_layers] + sections)
    # section_mask = self._psd_layers.get(section, None)
    if section_masks == {}:
        raise ValueError(f"Unknown section '{section}'.\nAvailabe sections:\n{_format_keys_recursive(psd_layers)}")

    if isinstance(section_masks, dict):
        section_masks = section_masks.values()
    else:
        section_masks = [section_masks]

    # Convert to binary masks
    section_masks = [np.array(x)[:, :, 3] == 255 for x in section_masks]

    # Union
    mask = functools.reduce(lambda x, y: np.logical_or(x, y), section_masks)

    return mask


def _lookup_path(psd_layers: dict, dotted: str):
    """Follow a dotted path like 'segments.rear_0' into nested dicts."""
    cur = psd_layers
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            # Reached a leaf too early
            raise ValueError(f"Path '{dotted}' is not valid at '{part}'")
        cur = cur.get(part, {})
    return cur  # dict (group) or PIL.Image.Image (leaf)


def _get_section_component_bool(
    section: str, psd_layers: dict, token_cache: dict[str, np.ndarray] | None = None
) -> np.ndarray:
    """
    Resolve a section token to a 2D boolean mask.
    - If token points to a dict, union all leaves beneath it.
    - If token points to a single image, just return its alpha>0 mask.
    Results are cached per token for the duration of a build.
    """
    if token_cache is not None and section in token_cache:
        return token_cache[section]

    node = _lookup_path(psd_layers, section)
    if node == {}:
        # Helpful error with available keys
        def _format_keys_recursive(d, prefix=""):
            lines = []
            for k, v in d.items():
                path = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    lines.append(path + "/")
                    lines.extend(_format_keys_recursive(v, path))
                else:
                    lines.append(path)
            return lines

        avail = "\n".join(_format_keys_recursive(psd_layers))
        raise ValueError(f"Unknown section '{section}'.\nAvailable sections:\n{avail}")

    if isinstance(node, dict):
        # Union all child leaves under this group
        masks = (_alpha_bool(img) for img in _iter_leaf_images(node))
        out = _fast_union_bool(masks)
    else:
        out = _alpha_bool(node)

    if token_cache is not None:
        token_cache[section] = out
    return out


def _crop_mask_fast(mask_bool: np.ndarray):
    """
    Given a 2D boolean mask (True = keep), return (cropped PIL mask, bbox).
    PIL mask is 1-channel ("L") with 0/255 values, cropped to bbox.
    """
    bbox = _bbox_from_bool(mask_bool)
    if bbox is None:
        raise ValueError("Mask is empty!")

    l, t, r, b = bbox
    cropped_bool = mask_bool[t:b, l:r]  # view, no copy
    # Build a small 1-channel image only once:
    cropped_u8 = cropped_bool.astype(np.uint8) * 255
    pil_mask = Image.fromarray(cropped_u8, mode="L")  # or .convert("1") if you prefer 1-bit
    return pil_mask, bbox


def _apply_operator(stack, operators):
    operator = operators.pop()
    if operator == "~":
        operand = stack.pop()
        stack.append(np.invert(operand))
    else:
        right = stack.pop()
        left = stack.pop()
        if operator == "&":
            stack.append(np.logical_and(left, right))
        elif operator == "|":
            stack.append(np.logical_or(left, right))
    return stack, operators


def _bbox_from_bool(mask_bool: np.ndarray):
    """Tight bbox (l, t, r, b) for True region; O(H+W)."""
    if not mask_bool.any():
        return None
    rows = mask_bool.any(axis=1)
    cols = mask_bool.any(axis=0)
    top = rows.argmax()
    bottom = mask_bool.shape[0] - rows[::-1].argmax()
    left = cols.argmax()
    right = mask_bool.shape[1] - cols[::-1].argmax()
    return (left, top, right, bottom)


def _crop_bool_mask(mask_bool: np.ndarray):
    """Return (cropped_bool, bbox) with tight bbox; raises if empty."""
    bbox = _bbox_from_bool(mask_bool)
    if bbox is None:
        raise ValueError("Mask is empty!")
    l, t, r, b = bbox
    return mask_bool[t:b, l:r].copy(), bbox  # small copy keeps it independent


def get_section_mask(expression, template, crop_mask=True):
    logger.info(f"Getting section: {expression}")
    tokens = re.findall(r"[a-zA-Z0-9_.]+|[&|~()]", expression)
    stack = []
    operators = []

    if template is None:
        raise ValueError("Attempted to get section mask, but no template provided")

    logger.info("Building operator stack")
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if re.match(r"[a-zA-Z0-9_]+", token):  # It's a word
            # If there's a pending NOT (~) operator, apply it immediately
            if operators and operators[-1] == "~":
                operators.pop()  # Remove the NOT operator
                stack.append(~_get_section_component_bool(token, template))
            else:
                stack.append(_get_section_component_bool(token, template))
        elif token in ("&", "|"):
            while operators and operators[-1] in ("&", "|") and operators[-1] != "(":
                stack, operators = _apply_operator(stack, operators)
            operators.append(token)
        elif token == "~":
            operators.append(token)  # Delay application until the operand is found
        elif token == "(":
            operators.append(token)
        elif token == ")":
            while operators and operators[-1] != "(":
                stack, operators = _apply_operator(stack, operators)
            operators.pop()  # Remove '('
        else:
            raise ValueError(f"Invalid token: {token}")
        i += 1

    logger.info("Applying operations")
    while operators:
        stack, operators = _apply_operator(stack, operators)

    mask_bool = stack[0]  # 2D boolean ndarray

    if not mask_bool.any():
        raise ValueError(f"Mask is empty!\nSection expression: {expression}")

    if crop_mask:
        logger.info("Cropping mask")
        section_mask, bbox = _crop_bool_mask(mask_bool)
    else:
        section_mask = mask_bool
        bbox = (0, 0) + section_mask.shape
    logger.info("Done")
    return section_mask, bbox


def load_layers(path, groups=None):
    logger.info(f"Loading PSD layers: {path}")

    cache_base_path, cache_paths, checksum = _get_cache_path_and_checksum(path)
    # Determine if cache is up to date
    cache_valid = False
    if cache_paths["checksum"].is_file():
        with open(cache_paths["checksum"], "r") as f:
            existing_checksum = f.readlines()[0]
        if existing_checksum == checksum:
            cache_valid = True

    if not cache_valid:
        logger.info("Cache invalid, re-caching PSD layers")
        if cache_base_path.exists():
            shutil.rmtree(cache_base_path)
        psd = PSDImage.open(path)

        size = psd.size
        _cache_psd_recursive(cache_paths["images"], psd, size)
        # Write checksum
        with open(cache_paths["checksum"], "w") as f:
            f.writelines(checksum)
    else:
        logger.info("Cache valid, loading")

    # Load in the data from cache.
    out, size = _load_cached_psd(cache_paths["images"], groups)

    return out, checksum, tuple(size)
