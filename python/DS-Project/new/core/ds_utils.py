import numpy as np
from .sparse_formats import DOK, COO, CSR

def dense_to_dok(arr, background_val=0):
    """Converts a dense numpy array to a DOK sparse matrix."""
    shape = arr.shape
    dok = DOK(shape, dtype=arr.dtype)
    for r in range(shape[0]):
        for c in range(shape[1]):
            val = arr[r, c]
            if val != background_val:
                dok.set_pixel(r, c, val)
    return dok

def dok_to_coo(dok: DOK):
    """Converts a DOK sparse matrix to a COO sparse matrix."""
    coo = COO(dok.shape, dtype=dok.dtype)
    if not dok.pixels:
        return coo

    # Sort pixels by row, then column for predictable order
    sorted_pixels = sorted(dok.pixels.items())
    
    rows, cols, datas = zip(*[(r, c, v) for (r, c), v in sorted_pixels])

    coo.row = list(rows)
    coo.col = list(cols)
    coo.data = list(datas)
    coo.nnz = len(coo.data)
    return coo

def coo_to_csr(coo: COO):
    """Converts a COO sparse matrix to a CSR sparse matrix."""
    csr = CSR(coo.shape, dtype=coo.dtype)
    if coo.nnz == 0:
        return csr

    # Combine row, col, data for sorting
    combined = sorted(zip(coo.row, coo.col, coo.data))
    sorted_row, sorted_col, sorted_data = zip(*combined)

    csr.indices = np.array(sorted_col, dtype=np.int32)
    csr.data = np.array(sorted_data, dtype=coo.dtype)
    csr.nnz = coo.nnz

    # Build the indptr array
    row_idx = 0
    for i, r in enumerate(sorted_row):
        while row_idx < r:
            csr.indptr[row_idx + 1] = i
            row_idx += 1
    
    # Fill in the rest of the indptr array
    for i in range(row_idx, csr.shape[0]):
         csr.indptr[i+1] = csr.nnz
            
    return csr

def dok_to_csr(dok: DOK):
    """Convenience function to convert DOK -> COO -> CSR."""
    coo = dok_to_coo(dok)
    return coo_to_csr(coo)

# You can also add reverse conversions if needed, e.g., csr_to_dok
def csr_to_dok(csr: CSR):
    """Converts a CSR sparse matrix to a DOK sparse matrix."""
    dok = DOK(csr.shape, dtype=csr.dtype)
    for r in range(csr.shape[0]):
        for i in range(csr.indptr[r], csr.indptr[r+1]):
            dok.set_pixel(r, csr.indices[i], csr.data[i])
    return dok
