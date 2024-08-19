import io

from PIL import Image
import matplotlib.pyplot as plt


def prep_ax(ax):
    # Hide grid lines
    ax.grid(False)

    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    plt.axis("off")

    # ax.set_aspect(1)
    ax.margins(0)

    plt.tight_layout(pad=0)


def get_fig(size):
    figsize = [s / 100 for s in size]
    fig, ax = plt.subplots(figsize=figsize)
    ax.patch.set_alpha(0)
    return fig, ax


def fig_to_img(fig, size):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    buf = io.BytesIO()

    # Set the figure size, written out at 100DPI
    # fig.set_figwidth(size[0] / 100)
    # fig.set_figheight(size[1] / 100)

    fig.savefig(buf, transparent=True)
    buf.seek(0)
    img = Image.open(buf)

    # Sometimes, we're off by a pixel in size
    if img.size != size:
        # Check that we're off by 1 pixel or less
        size_diff = [abs(x - y) for x, y in zip(img.size, size)]
        if max(size_diff) > 1:
            raise ValueError(f"Requested image size {size}, but got size {img.size}")
        img = img.resize(size)

    return img
