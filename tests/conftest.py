import pytest
import numpy as np
from pathlib import Path

REF_BASE_PATH = Path(__file__).parent / "data" / "ref"


def pytest_addoption(parser):
    parser.addoption(
        "--update-ref-layers",
        action="store_true",
    )


def _add_grid(image, grid_spacing: int, center_line_thickness: int = 3, alpha: float = 0.8):
    """
    Adds a grid to the image with gridlines every `grid_spacing` pixels, and an extra thick line at the center.

    Args:
        image (Image.Image): The input image to add the grid to.
        grid_spacing (int): The spacing between the gridlines.
        center_line_thickness (int, optional): The thickness of the center lines. Defaults to 3.

    Returns:
        Image.Image: The image with the added grid.
    """
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    width, height = image.size

    grid_color = (0, 0, 0, int(255 * alpha))

    # Calculate the center of the image
    center_x = width // 2
    center_y = height // 2

    # Draw vertical lines starting from the center
    for x in range(center_x, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for x in range(center_x, 0, -grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)

    # Draw horizontal lines starting from the center
    for y in range(center_y, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
    for y in range(center_y, 0, -grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Draw the extra thick center lines
    draw.line([(center_x, 0), (center_x, height)], fill=grid_color, width=center_line_thickness)
    draw.line([(0, center_y), (width, center_y)], fill=grid_color, width=center_line_thickness)

    return image


@pytest.fixture
def test_id(request):
    unique_id = request.node.nodeid
    unique_id = "/".join(unique_id.split("::", 1))
    return unique_id


@pytest.fixture
def compare_ref_layer(request, test_id):
    def _compare_ref_layer(layer, grid=25):
        from ilivery.layer import Layer

        layer._paint = _add_grid(layer._paint, grid)
        layer._spec = _add_grid(layer._spec, grid)

        path = REF_BASE_PATH / test_id

        if request.config.getoption("update_ref_layers"):
            layer.save(path, overwrite=True)
        else:
            ref_layer = Layer.load(path)
            assert ref_layer == layer

    return _compare_ref_layer


@pytest.fixture
def compare_ref_image(request, test_id):
    def _compare_ref_layer(image, grid=25):
        from PIL import Image

        if grid:
            image = _add_grid(image, grid)

        path = (REF_BASE_PATH / test_id).with_suffix(".png")

        if request.config.getoption("update_ref_layers"):
            path.parent.mkdir(exist_ok=True, parents=True)
            image.save(fp=path, format="png", compression_level=0)
        else:
            ref_image = Image.open(path)
            assert (np.array(ref_image) == np.array(image)).all()

    return _compare_ref_layer
