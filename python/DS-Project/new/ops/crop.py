from core.sparse_formats import DOK
from core.ds_utils import csr_to_dok, dok_to_csr, dok_to_coo

def crop(sparse_obj, box):
    """
    Crops a sparse object to a given bounding box.

    Args:
        sparse_obj: The sparse object to crop.
        box (tuple): A tuple of (x1, y1, x2, y2) defining the crop box.

    Returns:
        A new sparse object of the same type, cropped.
    """
    x1, y1, x2, y2 = box
    if not (0 <= x1 < x2 <= sparse_obj.shape[1] and 0 <= y1 < y2 <= sparse_obj.shape[0]):
        raise ValueError("Invalid crop box dimensions.")

    # Convert to DOK for easiest manipulation
    if sparse_obj.__class__.__name__ != 'DOK':
        dok = csr_to_dok(sparse_obj) # This assumes CSR or COO can be converted from CSR
    else:
        dok = sparse_obj

    new_width = x2 - x1
    new_height = y2 - y1
    new_dok = DOK(shape=(new_height, new_width), dtype=dok.dtype)

    for (r, c), value in dok.pixels.items():
        if x1 <= c < x2 and y1 <= r < y2:
            # Remap coordinates to the new cropped dimensions
            new_dok.set_pixel(r - y1, c - x1, value)

    # Convert back to the original format
    if sparse_obj.__class__.__name__ == 'CSR':
        return dok_to_csr(new_dok)
    elif sparse_obj.__class__.__name__ == 'COO':
        return dok_to_coo(new_dok)
        
    return new_dok
