from core.sparse_formats import DOK
from core.ds_utils import csr_to_dok, dok_to_csr, coo_to_csr, dok_to_coo

def flip(sparse_obj, direction='vertical'):
    """Flips a sparse object vertically or horizontally."""
    
    if sparse_obj.__class__.__name__ != 'DOK':
        dok = csr_to_dok(sparse_obj)
    else:
        dok = sparse_obj
        
    new_dok = DOK(dok.shape, dok.dtype)
    
    if direction == 'vertical':
        for (r, c), value in dok.pixels.items():
            new_dok.set_pixel(dok.shape[0] - 1 - r, c, value)
    elif direction == 'horizontal':
        for (r, c), value in dok.pixels.items():
            new_dok.set_pixel(r, dok.shape[1] - 1 - c, value)
    else:
        raise ValueError("Direction must be 'vertical' or 'horizontal'")

    if sparse_obj.__class__.__name__ == 'CSR':
        return dok_to_csr(new_dok)
    elif sparse_obj.__class__.__name__ == 'COO':
        return dok_to_coo(new_dok)
        
    return new_dok
