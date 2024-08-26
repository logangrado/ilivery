import hashlib
import functools
import numpy as np
import re
import shutil

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


def _cache_psd_recursive(cache_dir, group, parent_groups=None):
    if not group.is_visible():
        group.visible = True

    if parent_groups is None:
        parent_groups = []
    if parent_groups is not None:
        parent_group_str = "/".join(parent_groups)

    for item in group:
        if item.is_group():
            group_cache_dir = cache_dir / item.name
            _cache_psd_recursive(group_cache_dir, item, parent_groups=parent_groups + [group.name])
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

            if item.offset != (0, 0):
                logger.warning(f"Layer {item.name} has nonzero offset: {item.offset}, skipping")

            else:
                layer = item.composite()
                # layer.save(fp=layer_cache_path, format="tga", compression="tga_rle")
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


def _crop_mask(mask):
    """
    Crop a section mask to the smallest rectangle containing the mask
    """
    if isinstance(mask, dict):
        mask = functools.reduce(lambda x, y: Image.alpha_composite(x, y), mask.values())

    mask_data = np.array(mask)[:, :, 3] == 255

    mask_indicies = np.where(mask_data)

    bbox = (
        min(mask_indicies[1]),
        min(mask_indicies[0]),
        max(mask_indicies[1]) + 1,
        max(mask_indicies[0]) + 1,
    )

    return mask, bbox


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


def get_section_mask(expression, template):
    tokens = re.findall(r"[a-zA-Z0-9_.]+|[&|~()]", expression)
    stack = []
    operators = []

    if template is None:
        raise ValueError("Attempted to get section mask, but no template provided")

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if re.match(r"[a-zA-Z0-9_]+", token):  # It's a word
            # If there's a pending NOT (~) operator, apply it immediately
            if operators and operators[-1] == "~":
                operators.pop()  # Remove the NOT operator
                stack.append(~_get_section_component(token, template))
            else:
                stack.append(_get_section_component(token, template))
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

    while operators:
        stack, operators = _apply_operator(stack, operators)

    section_mask = stack[0]

    if section_mask.sum() == 0:
        raise ValueError(f"Mask is empty!\nSection expression: {expression}")

    section_mask = (section_mask.reshape(-1, 1) * np.array([0, 0, 0, 255], dtype="uint8")).reshape(
        *section_mask.shape, 4
    )
    section_mask = Image.fromarray(section_mask)

    section_mask, bbox = _crop_mask(section_mask)
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

        _cache_psd_recursive(cache_paths["images"], psd)
        # Write checksum
        with open(cache_paths["checksum"], "w") as f:
            f.writelines(checksum)
    else:
        logger.info("Cache valid, loading")

    # Load in the data from cache.
    out, size = _load_cached_psd(cache_paths["images"], groups)

    return out, checksum, tuple(size)
