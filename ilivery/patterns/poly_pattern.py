#!/usr/bin/env python3
import matplotlib as mpl
from PIL import Image

from ilivery import utils


def _single_poly_pattern(
    size,
    poly_df,
    color=None,
    cmap=None,
    cfunc=None,
    edgecolor=None,
    edgewidth=None,
    c_min=0,
    c_max=1,
):
    poly_df = poly_df.copy()
    if cmap:
        # Compute cvalue
        poly_df["c_val"] = cfunc(poly_df["x"], poly_df["y"])

        # Adjust to cmin/cmax
        poly_df["c_val"] = poly_df["c_val"] * (c_max - c_min) + c_min

        # Apply
        poly_df["facecolor"] = poly_df["c_val"].apply(cmap)

    elif color:
        color = utils.color.standardize_colors(color)
        poly_df["facecolor"] = [color] * len(poly_df)
    else:
        poly_df["facecolor"] = [(0, 0, 0, 0)] * len(poly_df)

    if edgecolor:
        edgecolor = utils.color.standardize_colors(edgecolor)
        poly_df["edgecolor"] = [edgecolor] * len(poly_df)
    else:
        poly_df["edgecolor"] = [(0, 0, 0, 0)] * len(poly_df["facecolor"])

    poly_col = mpl.collections.PolyCollection(
        verts=poly_df["verts"],
        facecolors=poly_df["facecolor"],
        edgecolors=poly_df["edgecolor"],
        linewidths=edgewidth,
    )

    fig, ax = utils.mpl.get_fig(size)
    ax.add_collection(poly_col)
    ax.set_xlim(0, size[0])
    ax.set_ylim(0, size[1])

    utils.mpl.prep_ax(ax)
    paint = utils.mpl.fig_to_img(fig, size)
    return paint


def poly_pattern(
    size,
    poly_df,
    facecolor=None,
    face_cmap=None,
    face_cfunc=None,
    edgecolor=None,
    edgewidth=None,
    facespec=None,
    facespec_cmap=None,
    facespec_cfunc=None,
    edgespec=None,
    c_min=0,
    c_max=1,
):
    """
    Create a polygon pattern from a poly_verts df

    Parameters
    ----------
    size : tuple[int]
        Size tuple
    poly_df : pd.DataFrame
        Dataframe, one row per polygon, with following columns:
            x,y : float
                polygon center
            verts : list
                List of polygon verticies
    cmap : func
        Colormap function. Must take a value in range [0,1) and return a color
    cfunc : func
        Color function, must take an (x,y) pair and return a scalar value
    edgecolor : color
        Edgecolor
    edgewidth : float
        Edgewidth
    facespec : color
        Specmap for faces
    edgespec : color
        Specmap for edges

    Returns
    -------
    img : PIL.Image
        Poly image
    spec : PIL.Image
        Poly specmap, if facespec or edgespec are not None
    """
    kwargs = {
        "size": size,
        "poly_df": poly_df,
        "c_min": c_min,
        "c_max": c_max,
    }
    if (facecolor or face_cmap) or edgecolor:
        paint = _single_poly_pattern(
            color=facecolor,
            cmap=face_cmap,
            cfunc=face_cfunc,
            edgecolor=edgecolor,
            **kwargs,
        )
    else:
        paint = Image.new(size=size, mode="RGBA", color=(0, 0, 0, 0))

    if (facespec or facespec_cmap) or edgespec:
        spec = _single_poly_pattern(
            color=facespec,
            cmap=facespec_cmap,
            cfunc=facespec_cfunc,
            edgecolor=edgespec,
            **kwargs,
        )
    else:
        spec = Image.new(size=size, mode="RGBA", color=(0, 0, 0, 0))

    return (paint, spec)
