from core.sparse_formats import DOK
from core.ds_utils import csr_to_dok, dok_to_csr, coo_to_csr, dok_to_coo

def rotate90(sparse_obj):
    """Rotates a sparse object 90 degrees clockwise."""
    
    # For simplicity, we convert to DOK for manipulation
    if sparse_obj.__class__.__name__ != 'DOK':
        dok = csr_to_dok(sparse_obj) # Assuming CSR for now
    else:
        dok = sparse_obj

    new_shape = (dok.shape[1], dok.shape[0])
    new_dok = DOK(new_shape, dok.dtype)
    
    for (r, c), value in dok.pixels.items():
        new_dok.set_pixel(c, dok.shape[0] - 1 - r, value)
        
    # Convert back to original format
    if sparse_obj.__class__.__name__ == 'CSR':
        return dok_to_csr(new_dok)
    elif sparse_obj.__class__.__name__ == 'COO':
        return dok_to_coo(new_dok)
    
    return new_dok
