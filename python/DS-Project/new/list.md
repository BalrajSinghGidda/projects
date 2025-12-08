# Project Status: Sparse Image Compressor

This file tracks the progress of the project, outlining the initial vision, completed tasks, current work, and future plans.

## Initial Project Vision

The goal is to create a comprehensive tool for sparse image compression. This includes:
- Implementing various sparse matrix formats (DOK, COO, CSR).
- Providing tools for lossless and lossy compression.
- Visualizing the compressed data.
- Performing transformations directly on compressed formats.
- Offering both a Command-Line Interface (CLI) and a Web UI for demos.
- Benchmarking the performance of different formats and algorithms.

---

## Completed Work

- **Core Data Structures (`core/`)**:
    - [x] Implemented DOK, COO, and CSR sparse formats.
    - [x] Created utilities for converting between formats (`ds_utils.py`).

- **File I/O (`project_io/`)**:
    - [x] Loading and saving standard image files.
    - [x] Saving and loading custom `.npz` compressed sparse objects.

- **Command-Line Interface (`cli/`)**:
    - [x] Functional CLI with `compress` and `decompress` commands.

- **Web UI (`ui/`)**:
    - [x] Flask application with three main pages.
    - [x] **Compress Page**: Upload an image, choose a sparse format, view results.
    - [x] **Decompress Page**: Upload a `.npz` file, view reconstructed/heatmap, see metadata and stats.
    - [x] **Transform Page**: Upload a `.npz` file, apply rotate/flip/interactive crop, view before/after.
    - [x] **Visualizations**: Displays original, reconstructed, and sparsity heatmap images.
    - [x] **File Downloads**: Allows downloading of compressed `.npz` files and result images.
    - [x] **UX Improvements**: Human-readable file sizes (KB/MB), improved page styling, dark mode toggle, heatmap style toggle.

- **Lossy Compression Algorithms (`alg/`)**:
    - [x] **Thresholding**: Implemented and integrated into the UI.
    - [x] **Quantization**: Implemented and integrated into the UI.

- **Advanced Transformations (`ops/`)**:
    - [x] Implemented `rotate` and `flip` functionality.
    - [x] Implemented `crop` functionality with interactive UI.

- **Benchmarking Suite (`bench/`)**:
    - [x] Created a script in `bench/benchmarks.py` to compare format performance.
    - [x] The script measures and reports on compression ratio, speed, and memory usage.

---

## Current Task

- [x] Update `list.md` to reflect latest completed features.
- [ ] Commit and push `list.md` changes.

---

## Future Work (Optional)

- **Advanced Compression (Optional)**:
    - [ ] Implement Run-Length Encoding (RLE) on top of the sparse data.
    - [ ] Implement Huffman coding for entropy encoding of pixel values.
- **Documentation**:
    - [ ] Flesh out the `docs/README.md` with detailed instructions and analysis.
    - [ ] Add more comments and docstrings throughout the code.
- **Unit Tests**:
    - [ ] Add comprehensive unit tests in the `tests/` directory to ensure correctness of all operations.
