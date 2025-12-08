import numpy as np
import json
from core.sparse_formats import DOK, COO, CSR
from core.ds_utils import dok_to_coo, coo_to_csr, csr_to_dok

def save_sparse(filepath, sparse_objs):
    """
    Saves one or more sparse objects to a compressed .npz file.
    """
    if not isinstance(sparse_objs, list):
        sparse_objs = [sparse_objs]

    first_obj = sparse_objs[0]
    metadata = {
        'format': first_obj.__class__.__name__,
        'shape': first_obj.shape,
        'dtype': np.dtype(first_obj.dtype).name,
        'channels': len(sparse_objs)
    }
    
    data_dict = {'_metadata': np.array([json.dumps(metadata)])}

    format_name = metadata['format']
    
    for i, sparse_obj in enumerate(sparse_objs):
        suffix = f'_{i}'
        if format_name == 'DOK':
            # Convert DOK to COO for efficient storage
            sparse_obj = dok_to_coo(sparse_obj)
        
        if isinstance(sparse_obj, (COO)):
            data_dict.update({f'row{suffix}': sparse_obj.row, f'col{suffix}': sparse_obj.col, f'data{suffix}': sparse_obj.data})
        elif isinstance(sparse_obj, (CSR)):
            data_dict.update({f'indptr{suffix}': sparse_obj.indptr, f'indices{suffix}': sparse_obj.indices, f'data{suffix}': sparse_obj.data})
        else:
            raise TypeError(f"Unsupported sparse format for saving: {type(sparse_obj)}")

    np.savez_compressed(filepath, **data_dict)

def load_sparse(filepath):
    """
    Loads one or more sparse objects from a .npz file.
    Returns a list of sparse objects.
    """
    with np.load(filepath, allow_pickle=True) as loaded:
        metadata = json.loads(loaded['_metadata'][0])
        
        format_name = metadata['format']
        shape = tuple(metadata['shape'])
        dtype = np.dtype(metadata['dtype'])
        # Use .get() to provide backward compatibility with old files
        channels = metadata.get('channels', 1)
        
        loaded_objs = []

        for i in range(channels):
            suffix = f'_{i}'
            
            # Reconstruct the native format that was saved (COO or CSR)
            if f'indptr{suffix}' in loaded: # It's a CSR
                csr = CSR(shape, dtype)
                csr.indptr = loaded[f'indptr{suffix}']
                csr.indices = loaded[f'indices{suffix}']
                csr.data = loaded[f'data{suffix}']
                csr.nnz = len(csr.data)
                native_obj = csr
            elif f'row{suffix}' in loaded: # It's a COO (or DOK saved as COO)
                coo = COO(shape, dtype)
                coo.row = loaded[f'row{suffix}']
                coo.col = loaded[f'col{suffix}']
                coo.data = loaded[f'data{suffix}']
                coo.nnz = len(coo.data)
                native_obj = coo
            else:
                raise ValueError(f"Could not find sparse data for channel {i} in file.")

            # If the original format was DOK, convert back
            # This part needs a robust coo_to_dok function.
            if format_name == 'DOK':
                if isinstance(native_obj, CSR):
                     loaded_objs.append(csr_to_dok(native_obj))
                else: # It's COO
                    dok = DOK(shape, dtype)
                    for r, c, v in zip(native_obj.row, native_obj.col, native_obj.data):
                        dok.set_pixel(r, c, v)
                    loaded_objs.append(dok)
            else:
                loaded_objs.append(native_obj)

        return loaded_objs
