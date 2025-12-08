import os
import sys
import time
import glob
import numpy as np

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_io import image_io, compressed_io
from core import ds_utils
from core.sparse_formats import DOK, COO, CSR

def get_obj_size(obj):
    """Recursively finds size of objects in bytes for a rough estimate."""
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(map(get_obj_size, obj.keys()))
        size += sum(map(get_obj_size, obj.values()))
    elif isinstance(obj, (list, tuple, set)):
        size += sum(map(get_obj_size, obj))
    elif isinstance(obj, np.ndarray):
        size += obj.nbytes
    return size

def run_benchmark_for_image(image_path):
    """Runs a full benchmark for a single image and returns results."""
    results = []
    
    try:
        dense_array = image_io.load_image(image_path)
    except Exception as e:
        print(f"Could not load image {image_path}: {e}")
        return []
        
    original_file_size = os.path.getsize(image_path)
    
    for format_name in ['DOK', 'COO', 'CSR']:
        start_time = time.perf_counter()
        
        # --- Compression & Memory ---
        dok = ds_utils.dense_to_dok(dense_array)
        if format_name == 'DOK':
            sparse_obj = dok
        elif format_name == 'COO':
            sparse_obj = ds_utils.dok_to_coo(dok)
        elif format_name == 'CSR':
            sparse_obj = ds_utils.dok_to_csr(dok)
        
        compress_time = time.perf_counter() - start_time
        mem_usage = get_obj_size(sparse_obj)

        # --- Save to File ---
        temp_path = "temp_bench.npz"
        compressed_io.save_sparse(temp_path, sparse_obj)
        compressed_file_size = os.path.getsize(temp_path)
        
        # --- Decompression ---
        start_time = time.perf_counter()
        loaded_obj = compressed_io.load_sparse(temp_path)
        loaded_obj.to_dense()
        decompress_time = time.perf_counter() - start_time
        
        os.remove(temp_path)
        
        results.append({
            'format': format_name,
            'compress_time_ms': compress_time * 1000,
            'decompress_time_ms': decompress_time * 1000,
            'memory_usage_kb': mem_usage / 1024,
            'compression_ratio': original_file_size / compressed_file_size if compressed_file_size > 0 else float('inf')
        })
        
    return results

def main():
    """Main function to run all benchmarks."""
    print("--- Running Sparse Image Compressor Benchmarks ---")
    
    image_paths = glob.glob('assets/*.png')
    if not image_paths:
        print("\nNo images found in 'assets' directory. Aborting.")
        return
        
    for image_path in image_paths:
        print(f"\n--- Benchmarking: {os.path.basename(image_path)} ---")
        
        results = run_benchmark_for_image(image_path)
        
        print("-" * 90)
        print(f"{'Format':<10} | {'Compress Time (ms)':<20} | {'Decompress Time (ms)':<22} | {'Memory (KB)':<15} | {'Ratio':<10}")
        print("-" * 90)
        
        for res in results:
            print(f"{res['format']:<10} | {res['compress_time_ms']:<20.2f} | {res['decompress_time_ms']:<22.2f} | {res['memory_usage_kb']:<15.2f} | {res['compression_ratio']:.2f}x")
        print("-" * 90)

if __name__ == '__main__':
    main()