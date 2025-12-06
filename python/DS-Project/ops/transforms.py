# ops/transforms.py
from sparse_formats import COO


def rotate90_coo(coo: COO):
    H, W = coo.shape
    new_data = [(c, H - 1 - r, v) for (r, c, v) in coo.data]
    return COO((W, H), new_data)


def crop_coo(coo: COO, top, left, h, w):
    new = []
    H, W = coo.shape
    for r, c, v in coo.data:
        if top <= r < top + h and left <= c < left + w:
            new.append((r - top, c - left, v))
    return COO((h, w), new)
