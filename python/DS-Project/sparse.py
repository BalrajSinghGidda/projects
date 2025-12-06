# sparse.py
from dataclasses import dataclass, asdict
import json
from typing import List, Tuple, Dict


@dataclass
class COO:
    shape: Tuple[int, int]
    data: List[Tuple[int, int, int]]  # list of (r, c, val)

    def to_json(self, path):
        out = {"format": "COO", "shape": list(self.shape), "data": self.data}
        with open(path, "w") as f:
            json.dump(out, f)

    @staticmethod
    def from_dense(arr):
        H, W = arr.shape
        d = []
        for r in range(H):
            for c in range(W):
                v = int(arr[r, c])
                if v != 0:
                    d.append((r, c, v))
        return COO((H, W), d)

    @staticmethod
    def from_json(path):
        with open(path, "r") as f:
            o = json.load(f)
        return COO(tuple(o["shape"]), [tuple(x) for x in o["data"]])

    def to_dense(self, dtype=int):
        import numpy as np

        H, W = self.shape
        arr = np.zeros((H, W), dtype=dtype)
        for r, c, v in self.data:
            arr[r, c] = v
        return arr


class DOK:
    def __init__(self, shape):
        self.shape = shape
        self.map = {}  # (r,c) -> v

    def set(self, r, c, v):
        if v == 0:
            self.map.pop((r, c), None)
        else:
            self.map[(r, c)] = v

    def get(self, r, c):
        return self.map.get((r, c), 0)

    def to_coo(self):
        data = [(r, c, v) for (r, c), v in self.map.items()]
        return COO(self.shape, data)
