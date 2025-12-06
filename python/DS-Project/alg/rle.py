# alg/rle.py
def rle_encode_rowmajor(arr):
    # arr: 2D numpy uint8
    flat = arr.flatten().tolist()
    out = []
    if not flat:
        return out
    prev = flat[0]
    cnt = 1
    for x in flat[1:]:
        if x == prev:
            cnt += 1
        else:
            out.append((prev, cnt))
            prev = x
            cnt = 1
    out.append((prev, cnt))
    return out


def rle_decode_rowmajor(rle, shape):
    import numpy as np

    flat = []
    for val, cnt in rle:
        flat.extend([val] * cnt)
    arr = np.array(flat, dtype="uint8").reshape(shape)
    return arr
