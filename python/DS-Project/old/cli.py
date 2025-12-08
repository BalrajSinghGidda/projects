# cli.py
import argparse, time, json, os
import numpy as np
from io_utils import load_image, save_png_from_array, file_size
from sparse_formats import COO, read_coo_binary
from alg.rle import rle_encode_rowmajor, rle_decode_rowmajor


def compress(args):
    # we auto-detect RGB if file is color
    # load as RGB first to see if it's colored; if grayscale desired, user can pass threshold (threshold on grayscale)
    arr_rgb = load_image(
        args.input,
        as_rgb=True,
        threshold=args.threshold if args.threshold is not None else None,
    )
    # decide if arr is really grayscale
    is_rgb = (
        arr_rgb.ndim == 3
        and not np.all(arr_rgb[:, :, 0] == arr_rgb[:, :, 1])
        and not np.all(arr_rgb[:, :, 1] == arr_rgb[:, :, 2])
    )
    if not is_rgb:
        # treat as grayscale (re-load as L without RGB packing)
        arr = load_image(
            args.input,
            as_rgb=False,
            threshold=args.threshold if args.threshold is not None else None,
        )
    else:
        arr = arr_rgb

    fmt = args.format.lower()
    start = time.perf_counter()
    coo = COO.from_dense(arr, threshold=args.threshold)
    if fmt == "coo":
        coo.to_json(args.output)
    elif fmt == "bin":
        coo.to_binary(args.output)
    elif fmt == "rle":
        # RLE works better on grayscale flattened arrays; do a grayscale flatten first (convert RGB to luminance)
        if arr.ndim == 3:
            # simple luminance
            gray = (
                0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]
            ).astype("uint8")
            rle = rle_encode_rowmajor(gray)
            payload = {"format": "RLE", "shape": list(gray.shape), "data": rle}
        else:
            rle = rle_encode_rowmajor(arr)
            payload = {"format": "RLE", "shape": list(arr.shape), "data": rle}
        with open(args.output, "w") as f:
            json.dump(payload, f)
    else:
        raise SystemExit("unknown format")
    elapsed = time.perf_counter() - start
    try:
        orig = file_size(args.input)
        comp = file_size(args.output)
        ratio = orig / comp if comp > 0 else float("inf")
    except Exception:
        orig = comp = ratio = 0
    print(
        f"[compress] {args.input} -> {args.output} fmt={fmt} time={elapsed:.3f}s nonzeros={len(coo.data)} orig={orig} comp={comp} ratio={ratio:.2f}"
    )


def decompress(args):
    inf = args.input
    outp = args.output
    # try JSON first
    if inf.endswith(".json") or inf.endswith(".coo.json") or inf.endswith(".rle.json"):
        with open(inf, "r") as f:
            o = json.load(f)
        if o.get("format") == "COO":
            coo = COO.from_json(inf)
            arr = coo.to_dense()
            save_png_from_array(arr, outp)
            print("[decompress] JSON COO ->", outp)
            return
        if o.get("format") == "RLE":
            shape = tuple(o["shape"])
            arr = rle_decode_rowmajor(o["data"], shape)
            save_png_from_array(arr, outp)
            print("[decompress] RLE ->", outp)
            return
    # try binary SPCO (COO) or SPCS (CSR)
    with open(inf, "rb") as f:
        magic = f.read(4)
    if magic == b"SPCO":
        coo = COO.from_binary(inf)
        arr = coo.to_dense()
        save_png_from_array(arr, outp)
        print("[decompress] BIN COO ->", outp)
        return
    elif magic == b"SPCS":
        from sparse_formats import CSR

        csr = CSR.from_binary(inf)
        coo = csr.to_coo()
        arr = coo.to_dense()
        save_png_from_array(arr, outp)
        print("[decompress] BIN CSR ->", outp)
        return
    else:
        raise SystemExit("Unknown input format for decompress")


def visualize(args):
    # visualize nonzero mask for any supported compressed format
    inf = args.input
    # load coo from JSON or binary
    coo = None
    if inf.endswith(".json") or inf.endswith(".coo.json"):
        coo = COO.from_json(inf)
    else:
        # try binary
        with open(inf, "rb") as f:
            magic = f.read(4)
        if magic == b"SPCO":
            coo = COO.from_binary(inf)
        elif magic == b"SPCS":
            from sparse_formats import CSR

            csr = CSR.from_binary(inf)
            coo = csr.to_coo()
        else:
            # try to parse RLE JSON
            try:
                with open(inf, "r") as f:
                    o = json.load(f)
                if o.get("format") == "RLE":
                    arr = np.array(
                        sum([[v] * cnt for v, cnt in o["data"]], []), dtype="uint8"
                    ).reshape(o["shape"])
                    mask = (arr > 0).astype("uint8")
                    import matplotlib.pyplot as plt

                    plt.figure(figsize=(6, 6))
                    plt.imshow(
                        mask, cmap="gray", vmin=0, vmax=1, interpolation="nearest"
                    )
                    plt.axis("off")
                    plt.savefig(args.output, bbox_inches="tight", pad_inches=0)
                    print("[visualize] RLE mask ->", args.output)
                    return
            except Exception:
                raise SystemExit("visualize: unknown format")
    arr = coo.to_dense()
    if arr.ndim == 3:
        mask = (arr.sum(axis=2) > 0).astype("uint8")
    else:
        mask = (arr > 0).astype("uint8")
    import matplotlib.pyplot as plt

    plt.figure(figsize=(6, 6))
    plt.imshow(mask, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    plt.axis("off")
    plt.savefig(args.output, bbox_inches="tight", pad_inches=0)
    print("[visualize] mask ->", args.output)


def bench(args):
    thresholds = args.thresholds
    results = []
    for t in thresholds:
        arr = load_image(args.input, as_rgb=False, threshold=t)
        coo = COO.from_dense(arr, threshold=t)
        import tempfile

        p = tempfile.NamedTemporaryFile(delete=False).name + ".json"
        coo.to_json(p)
        results.append((t, arr.size, len(coo.data), os.path.getsize(p)))
        os.remove(p)
    print("threshold,total_pixels,nonzeros,comp_bytes")
    for r in results:
        print(",".join(map(str, r)))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("compress")
    c.add_argument("--input", required=True)
    c.add_argument("--output", required=True)
    c.add_argument("--format", default="coo", choices=["coo", "bin", "rle"])
    c.add_argument("--threshold", type=int, default=None)
    d = sub.add_parser("decompress")
    d.add_argument("--input", required=True)
    d.add_argument("--output", required=True)
    v = sub.add_parser("visualize")
    v.add_argument("--input", required=True)
    v.add_argument("--output", required=True)
    b = sub.add_parser("bench")
    b.add_argument("--input", required=True)
    b.add_argument(
        "--thresholds", nargs="+", type=int, default=[None, 10, 30, 60, 100, 150, 200]
    )
    a = p.parse_args()
    if a.cmd == "compress":
        compress(a)
    elif a.cmd == "decompress":
        decompress(a)
    elif a.cmd == "visualize":
        visualize(a)
    elif a.cmd == "bench":
        bench(a)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
