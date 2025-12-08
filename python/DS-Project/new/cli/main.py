import argparse
import os
import sys

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project_io import image_io, compressed_io
from core import ds_utils
from core.sparse_formats import DOK, COO, CSR

def compress_image(args):
    """Handler for the 'compress' command."""
    print(f"Compressing '{args.input}' to '{args.output}' using {args.format} format.")
    
    # 1. Load image to dense array
    dense_array = image_io.load_image(args.input)
    print(f"Loaded image with shape: {dense_array.shape}")

    # 2. Convert dense array to DOK (the easiest to build)
    dok = ds_utils.dense_to_dok(dense_array)
    print(f"Initial DOK representation created with {dok.nnz} non-zero elements.")

    # 3. Convert to the target format
    target_format = args.format.upper()
    sparse_obj = None
    if target_format == 'DOK':
        sparse_obj = dok
    elif target_format == 'COO':
        sparse_obj = ds_utils.dok_to_coo(dok)
    elif target_format == 'CSR':
        sparse_obj = ds_utils.dok_to_csr(dok)
    else:
        print(f"Error: Unknown format '{args.format}'", file=sys.stderr)
        return

    print(f"Converted to {target_format} format.")

    # 4. Save the sparse object
    compressed_io.save_sparse(args.output, sparse_obj)
    print("Compression successful.")
    
    original_size = os.path.getsize(args.input)
    compressed_size = os.path.getsize(args.output)
    ratio = original_size / compressed_size if compressed_size > 0 else float('inf')
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression ratio: {ratio:.2f}x")


def decompress_image(args):
    """Handler for the 'decompress' command."""
    print(f"Decompressing '{args.input}' to '{args.output}'.")

    # 1. Load the sparse object
    sparse_obj = compressed_io.load_sparse(args.input)
    print(f"Loaded sparse object in {sparse_obj.__class__.__name__} format.")

    # 2. Convert to dense array
    dense_array = sparse_obj.to_dense()
    print("Converted to dense array.")

    # 3. Save the array as an image
    image_io.save_image(args.output, dense_array)
    print("Decompression successful.")


def main():
    parser = argparse.ArgumentParser(description="Sparse Image Compressor CLI.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # --- Compress command ---
    parser_compress = subparsers.add_parser('compress', help='Compress an image file.')
    parser_compress.add_argument('-i', '--input', type=str, required=True, help='Input image file path.')
    parser_compress.add_argument('-o', '--output', type=str, required=True, help='Output compressed file path (.npz).')
    parser_compress.add_argument('-f', '--format', type=str, default='CSR', choices=['dok', 'coo', 'csr'], help='Sparse format to use.')
    parser_compress.set_defaults(func=compress_image)

    # --- Decompress command ---
    parser_decompress = subparsers.add_parser('decompress', help='Decompress a file to an image.')
    parser_decompress.add_argument('-i', '--input', type=str, required=True, help='Input compressed file path (.npz).')
    parser_decompress.add_argument('-o', '--output', type=str, required=True, help='Output image file path.')
    parser_decompress.set_defaults(func=decompress_image)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
