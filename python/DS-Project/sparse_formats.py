# sparse_formats.py
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Iterable
import json, struct, os
import numpy as np


# --- helpers for multi-channel pack/unpack ---
def pack_rgb_triplet(trip):
    """pack (r,g,b) 0-255 into 24-bit int"""
    r, g, b = trip
    return (int(r) << 16) | (int(g) << 8) | int(b)


def unpack_rgb_int(x):
    r = (x >> 16) & 0xFF
    g = (x >> 8) & 0xFF
    b = x & 0xFF
    return (r, g, b)


# --- COO representation (data stores v as int; channels recorded in shape if 3D) ---
@dataclass
class COO:
    shape: Tuple[int, int, int]  # (H,W,C) or (H,W,1) where C = 1 or 3
    data: List[Tuple[int, int, int]]  # list of (r,c,v) where v is int (packed for RGB)

    def to_json(self, path: str):
        payload = {"format": "COO", "shape": list(self.shape), "data": self.data}
        with open(path, "w") as f:
            json.dump(payload, f)

    @staticmethod
    def from_json(path: str):
        with open(path, "r") as f:
            o = json.load(f)
        return COO(tuple(o["shape"]), [tuple(x) for x in o["data"]])

    def to_dense(self, dtype=np.uint8):
        H, W, C = self.shape
        if C == 1:
            arr = np.zeros((H, W), dtype=dtype)
            for r, c, v in self.data:
                arr[r, c] = v
            return arr
        else:
            arr = np.zeros((H, W, 3), dtype=dtype)
            for r, c, v in self.data:
                arr[r, c, :] = unpack_rgb_int(v)
            return arr

    @staticmethod
    def from_dense(arr: np.ndarray, threshold: Optional[int] = None):
        """
        arr: 2D (H,W) grayscale or 3D (H,W,3) RGB uint8
        threshold: if provided, binarize on >threshold
        returns COO with shape (H,W,C) where C is 1 or 3
        """
        if not isinstance(arr, np.ndarray):
            arr = np.array(arr)
        if arr.ndim == 2:
            H, W = arr.shape
            C = 1
            if threshold is not None:
                mask = arr > threshold
                nz_idx = np.nonzero(mask)
                vals = arr[nz_idx].astype(int).tolist()
                rows = nz_idx[0].tolist()
                cols = nz_idx[1].tolist()
            else:
                nz_idx = np.nonzero(arr)
                rows = nz_idx[0].tolist()
                cols = nz_idx[1].tolist()
                vals = arr[nz_idx].astype(int).tolist()
            data = list(zip(rows, cols, vals))
            return COO((H, W, C), data)
        elif arr.ndim == 3 and arr.shape[2] == 3:
            H, W, _ = arr.shape
            C = 3
            if threshold is not None:
                # threshold per-channel: any channel > threshold counts as nonzero
                mask = (arr > threshold).any(axis=2)
                nz = np.nonzero(mask)
                rows = nz[0].tolist()
                cols = nz[1].tolist()
                vals = []
                for r, c in zip(rows, cols):
                    trip = tuple(int(x) for x in arr[r, c, :])
                    vals.append(pack_rgb_triplet(trip))
            else:
                nz = np.nonzero((arr != 0).any(axis=2))
                rows = nz[0].tolist()
                cols = nz[1].tolist()
                vals = []
                for r, c in zip(rows, cols):
                    trip = tuple(int(x) for x in arr[r, c, :])
                    vals.append(pack_rgb_triplet(trip))
            data = list(zip(rows, cols, vals))
            return COO((H, W, C), data)
        else:
            raise ValueError(
                "Unsupported array shape for from_dense: must be HxW or HxWx3"
            )

    # --- binary writer (streaming) ---
    def to_binary(self, path: str):
        """
        Binary header:
         4 bytes magic 'SPCO'
         H:uint32, W:uint32, C:uint8, reserved:uint8 (pad), N:uint32
        Each entry: r:uint32, c:uint32, v:uint32
        """
        with open(path, "wb") as f:
            f.write(b"SPCO")
            H, W, C = self.shape
            N = len(self.data)
            # pack header (pad one byte to align)
            f.write(struct.pack("<IIBB I", int(H), int(W), int(C), 0, int(N)))
            # write entries streaming
            for r, c, v in self.data:
                f.write(struct.pack("<III", int(r), int(c), int(v)))

    @staticmethod
    def from_binary(path: str):
        with open(path, "rb") as f:
            magic = f.read(4)
            if magic != b"SPCO":
                raise ValueError("Not SPCO format")
            hdr = f.read(4 + 4 + 1 + 1 + 4)  # H W C pad N
            H, W, C, pad, N = struct.unpack("<IIBBI", hdr)
            data = []
            for _ in range(N):
                r, c, v = struct.unpack("<III", f.read(12))
                data.append((int(r), int(c), int(v)))
        return COO((int(H), int(W), int(C)), data)


@dataclass
class CSR:
    shape: Tuple[int, int, int]
    row_ptr: List[int]
    col_idx: List[int]
    values: List[int]

    def to_coo(self):
        H, W, C = self.shape
        data = []
        for r in range(H):
            start = self.row_ptr[r]
            end = self.row_ptr[r + 1]
            for i in range(start, end):
                data.append((r, self.col_idx[i], self.values[i]))
        return COO(self.shape, data)

    @staticmethod
    def from_coo(coo: COO):
        H, W, C = coo.shape
        if not coo.data:
            return CSR(coo.shape, [0] * (H + 1), [], [])
        data_sorted = sorted(coo.data, key=lambda x: (x[0], x[1]))
        col_idx = []
        values = []
        row_ptr = [0] * (H + 1)
        cur_row = 0
        cnt = 0
        for r, c, v in data_sorted:
            while cur_row < r:
                row_ptr[cur_row + 1] = cnt
                cur_row += 1
            col_idx.append(c)
            values.append(v)
            cnt += 1
        while cur_row < H:
            row_ptr[cur_row + 1] = cnt
            cur_row += 1
        return CSR(coo.shape, row_ptr, col_idx, values)

    # streaming CSR binary writer (SPCS)
    def to_binary(self, path: str):
        # header: magic 'SPCS' | H:U32 | W:U32 | C:U8 | pad:U8 | rows:U32 | ncols:U32 | nvals:U32
        with open(path, "wb") as f:
            f.write(b"SPCS")
            H, W, C = self.shape
            rows = len(self.row_ptr)
            ncols = len(self.col_idx)
            nvals = len(self.values)
            f.write(
                struct.pack(
                    "<IIBBIII",
                    int(H),
                    int(W),
                    int(C),
                    0,
                    int(rows),
                    int(ncols),
                    int(nvals),
                )
            )
            # row_ptr
            f.write(struct.pack("<" + "I" * rows, *[int(x) for x in self.row_ptr]))
            # col_idx
            f.write(struct.pack("<" + "I" * ncols, *[int(x) for x in self.col_idx]))
            # values as uint32
            f.write(struct.pack("<" + "I" * nvals, *[int(x) for x in self.values]))

    @staticmethod
    def from_binary(path: str):
        with open(path, "rb") as f:
            magic = f.read(4)
            if magic != b"SPCS":
                raise ValueError("Not SPCS format")
            hdr = f.read(4 + 4 + 1 + 1 + 4 + 4 + 4)  # H W C pad rows ncols nvals
            H, W, C, pad, rows, ncols, nvals = struct.unpack("<IIBBIII", hdr)
            row_ptr = list(struct.unpack("<" + "I" * rows, f.read(4 * rows)))
            col_idx = list(struct.unpack("<" + "I" * ncols, f.read(4 * ncols)))
            values = list(struct.unpack("<" + "I" * nvals, f.read(4 * nvals)))
        return CSR((int(H), int(W), int(C)), row_ptr, col_idx, values)


class DOK:
    def __init__(self, shape: Tuple[int, int, int]):
        self.shape = shape
        self.map: Dict[Tuple[int, int], int] = {}

    @staticmethod
    def from_coo(coo: COO):
        dok = DOK(coo.shape)
        for r, c, v in coo.data:
            dok.map[(r, c)] = v
        return dok

    def to_coo(self):
        data = [(r, c, v) for (r, c), v in self.map.items()]
        return COO(self.shape, data)

    def set(self, r: int, c: int, v: int):
        if v == 0:
            self.map.pop((r, c), None)
        else:
            self.map[(r, c)] = int(v)

    def get(self, r: int, c: int):
        return self.map.get((r, c), 0)


# convenience reader for webapp
def read_coo_binary(path: str) -> COO:
    return COO.from_binary(path)


def file_size(p: str) -> int:
    return os.path.getsize(p)
