import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from ilivery import utils


def _get_meshgrid(size, N=256):
    return np.meshgrid(
        np.linspace(0, size[0], N),
        np.linspace(0, size[1], N),
    )


def _img_from_data(size, cmap, data):
    # data = (data - np.min(data)) / (np.max(data) - np.min(data))

    # fig,ax = utils.mpl.get_fig(size)
    fig, ax = plt.subplots()
    ax.imshow(data, cmap=cmap, vmin=np.min(data), vmax=np.max(data), extent=(0, size[0], 0, size[1]))

    utils.mpl.prep_ax(ax)

    img = utils.mpl.fig_to_img(fig, size=size)

    return img


def _get_cmap(colors, cmap):
    if cmap is not None and colors is not None:
        raise ValueError("")

    elif cmap is not None:
        return cmap

    else:
        colors = utils.color.standardize_colors(colors, format="FLOAT")
        cmap = mpl.colors.LinearSegmentedColormap.from_list(name="", colors=colors)
        return cmap


def linear_gradient(size, cmap=None, colors=None, angle=0):
    # Negative angle for CC rotation
    angle = -1 * angle

    cmap = _get_cmap(colors, cmap)

    XX, YY = _get_meshgrid(size)

    data = np.cos(angle / 180 * np.pi) * XX + np.sin(angle / 180 * np.pi) * YY

    img = _img_from_data(size, cmap, data)

    return img


def radial_gradient(size, cmap=None, colors=None, xy=None):
    if xy is None:
        xy = (0, 0)

    cmap = _get_cmap(colors, cmap)

    XX, YY = _get_meshgrid(size)
    data = np.sqrt((XX - xy[0]) ** 2 + (YY - xy[1]) ** 2)

    img = _img_from_data(size, cmap, data)

    return img
