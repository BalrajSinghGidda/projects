# io_utils.py
from PIL import Image
import numpy as np
import os, struct


def load_image(path: str, as_rgb: bool = False, threshold: int = None):
    img = Image.open(path)
    if as_rgb:
        img = img.convert("RGB")
        arr = np.array(img)
    else:
        img = img.convert("L")
        arr = np.array(img)
    if threshold is not None:
        if arr.ndim == 2:
            arr = (arr > threshold).astype("uint8") * 255
        else:
            # any-channel threshold
            mask = (arr > threshold).any(axis=2)
            # produce binary image with same shape as arr (RGB) -> keep colors where mask True, else 0
            new = np.zeros_like(arr)
            new[mask] = arr[mask]
            arr = new
    return arr


def save_png_from_array(arr, path: str):
    import numpy as np

    if isinstance(arr, np.ndarray):
        if arr.ndim == 2:
            img = Image.fromarray(arr.astype("uint8"), mode="L")
        elif arr.ndim == 3 and arr.shape[2] == 3:
            img = Image.fromarray(arr.astype("uint8"), mode="RGB")
        else:
            raise ValueError("save_png_from_array: unsupported array shape")
        img.save(path)
    else:
        raise ValueError("Expected numpy array")


def file_size(path: str) -> int:
    return os.path.getsize(path)


# binary reader used previously (kept for compatibility if needed)
def read_spco_binary(path: str):
    from sparse_formats import COO

    return COO.from_binary(path)
