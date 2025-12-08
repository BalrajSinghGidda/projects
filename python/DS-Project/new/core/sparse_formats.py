import numpy as np
from abc import ABC, abstractmethod

class SparseFormat(ABC):
    """
    Abstract base class for sparse matrix representations.
    """
    def __init__(self, shape, dtype=np.uint8):
        if not isinstance(shape, tuple) or len(shape) != 2:
            raise ValueError("Shape must be a tuple of two integers.")
        self.shape = shape
        self.width, self.height = shape
        self.dtype = dtype
        self.nnz = 0  # Number of non-zero elements

    @abstractmethod
    def get_pixel(self, row, col):
        pass

    @abstractmethod
    def set_pixel(self, row, col, value):
        pass

    @abstractmethod
    def to_dense(self):
        """Converts the sparse representation back to a dense 2D numpy array."""
        pass

    def __repr__(self):
        return (f"{self.__class__.__name__}(shape={self.shape}, "
                f"nnz={self.nnz}, dtype={np.dtype(self.dtype).name})")


class DOK(SparseFormat):
    """
    Dictionary of Keys (DOK) sparse format.
    Stores (row, col) -> value in a dictionary.
    Good for incremental construction of a sparse matrix.
    """
    def __init__(self, shape, dtype=np.uint8):
        super().__init__(shape, dtype)
        self.pixels = {}

    def get_pixel(self, row, col):
        return self.pixels.get((row, col), 0)

    def set_pixel(self, row, col, value):
        if value != 0:
            if (row, col) not in self.pixels:
                self.nnz += 1
            self.pixels[(row, col)] = value
        elif (row, col) in self.pixels:
            del self.pixels[(row, col)]
            self.nnz -= 1
            
    def to_dense(self):
        arr = np.zeros(self.shape, dtype=self.dtype)
        for (row, col), value in self.pixels.items():
            arr[row, col] = value
        return arr


class COO(SparseFormat):
    """
    Coordinate List (COO) sparse format.
    Stores lists of row indices, column indices, and values.
    Good for simple and fast construction.
    """
    def __init__(self, shape, dtype=np.uint8):
        super().__init__(shape, dtype)
        self.row = []
        self.col = []
        self.data = []

    def get_pixel(self, row, col):
        # Inefficient for COO, but provided for completeness.
        try:
            for i, (r, c) in enumerate(zip(self.row, self.col)):
                if r == row and c == col:
                    return self.data[i]
        except Exception:
            pass
        return 0

    def set_pixel(self, row, col, value):
        # Very inefficient for COO. Better to build from a list of coordinates.
        raise NotImplementedError("set_pixel is inefficient for COO. Construct from data instead.")

    def to_dense(self):
        arr = np.zeros(self.shape, dtype=self.dtype)
        arr[self.row, self.col] = self.data
        self.nnz = len(self.data)
        return arr


class CSR(SparseFormat):
    """
    Compressed Sparse Row (CSR) format.
    Efficient for row slicing and matrix-vector products.
    """
    def __init__(self, shape, dtype=np.uint8):
        super().__init__(shape, dtype)
        # indptr (row pointers): points to the start of each row in col_idx/data
        # Example: [0, 2, 3, 5] means row 0 is data[0:2], row 1 is data[2:3], row 2 is data[3:5]
        self.indptr = np.zeros(self.shape[0] + 1, dtype=np.int32)
        # indices (column indices): column index for each non-zero value
        self.indices = np.array([], dtype=np.int32)
        # data: non-zero values
        self.data = np.array([], dtype=self.dtype)

    def get_pixel(self, row, col):
        row_start = self.indptr[row]
        row_end = self.indptr[row + 1]
        for i in range(row_start, row_end):
            if self.indices[i] == col:
                return self.data[i]
        return 0

    def set_pixel(self, row, col, value):
        raise NotImplementedError("set_pixel is inefficient for CSR. Construct from another format.")

    def to_dense(self):
        arr = np.zeros(self.shape, dtype=self.dtype)
        for r in range(self.shape[0]):
            for i in range(self.indptr[r], self.indptr[r+1]):
                arr[r, self.indices[i]] = self.data[i]
        self.nnz = len(self.data)
        return arr
