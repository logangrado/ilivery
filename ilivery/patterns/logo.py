import numpy as np
from PIL import Image, ImageDraw


def _get_verts(a, b, c):
    b = a * b
    c = a * c

    main_verts = np.array(
        [
            [b, 0],
            [a - b, 0],
            [a - b / 2, np.sqrt(3) / 2 * b],
            [3 / 2 * b, np.sqrt(3) / 2 * b],
            [1 / 2 * (a + b), np.sqrt(3) / 2 * (a - b)],
            [1 / 2 * (a - b), np.sqrt(3) / 2 * (a - b)],
            [1 / 2 * b, np.sqrt(3) / 2 * b],
        ]
    )

    c = [-np.cos(60 / 180 * np.pi) * c, np.sin(60 / 180 * np.pi) * c]
    aux_verts = np.array(
        [
            (main_verts[1] + main_verts[5]) / 2 + [b, 0] + c,
            (main_verts[1] + main_verts[5]) / 2 + c,
            main_verts[2] - [b, 0] + c,
            main_verts[2] + c,
        ]
    )

    center = (int(a / 2), int(a / 2 / np.sqrt(3)))
    radius = np.sqrt(np.sum((main_verts[0] - center) ** 2)).astype(int)

    r_pad = 0.1
    radius = np.array(int(radius * (1 + r_pad)))

    center_factor = center - radius
    center -= center_factor
    main_verts -= center_factor
    aux_verts -= center_factor

    main_verts = tuple([tuple(x) for x in main_verts])
    aux_verts = tuple([tuple(x) for x in aux_verts])

    return main_verts, aux_verts, center, radius


def _crop_transparent(img):
    img_data = np.array(img)

    x = np.argwhere(img_data[:, :, 3] > 0)

    cropped_img_data = img_data[np.min(x[:, 0]) : np.max(x[:, 0]), np.min(x[:, 1]) : np.max(x[:, 1]), :]

    img_out = Image.fromarray(cropped_img_data)

    return img_out


def logo(size, facecolor, edgecolor, edgewidth=None, edgeratio=None, pad="TIGHT"):
    """ """
    pad = pad.upper()
    assert pad.upper() in ["TIGHT", "CIRCLE"]

    target_size = size

    if edgeratio:
        edgewidth = int(target_size * edgeratio)

    aa_factor = 4

    size = tuple([target_size * aa_factor for i in range(2)])

    b = 0.18
    c = b / 4
    main_verts, aux_verts, center, radius = _get_verts(size[0], b, c)

    img = Image.new(mode="RGBA", size=(2 * radius, 2 * radius))  # , color=(255, 255, 255, 255))

    draw = ImageDraw.Draw(img)
    draw.polygon(main_verts, fill=facecolor)
    draw.polygon(aux_verts, fill=facecolor)
    if edgewidth:
        edge_verts = main_verts + main_verts[:2]
        edge_aux_verts = aux_verts + aux_verts[:2]
        draw.line(edge_verts, fill=edgecolor, width=edgewidth, joint="curve")
        draw.line(edge_aux_verts, fill=edgecolor, width=edgewidth, joint="curve")

    img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    img = img.resize(
        (int(img.size[0] / aa_factor), int(img.size[1] / aa_factor)),
        resample=Image.Resampling.BICUBIC,
    )

    if pad == "TIGHT":
        img = _crop_transparent(img)

    return img


if __name__ == "__main__":
    f = (20, 20, 20, 255)
    e = (255, 38, 38, 255)
    e = (189, 22, 22, 255)

    logo_size = 512
    img = logo(size=(logo_size, logo_size), facecolor=f, edgecolor=e, edgewidth=20, pad="CIRCLE")
    img.show()
