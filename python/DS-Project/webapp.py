# webapp.py
import os, uuid, json, pathlib
from flask import Flask, request, render_template, send_file, abort
from types import SimpleNamespace
import cli
from io_utils import file_size

BASE = pathlib.Path(__file__).parent.resolve()
UPLOAD_DIR = BASE / "uploads"
OUT_DIR = BASE / "out"
for d in (UPLOAD_DIR, OUT_DIR):
    d.mkdir(exist_ok=True)


def ext_for_format(fmt: str):
    if fmt == "coo":
        return ".coo.json"
    if fmt == "rle":
        return ".rle.json"
    if fmt == "bin":
        return ".bin"
    return ".dat"


app = Flask(__name__, template_folder=str(BASE / "templates"))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    f = request.files.get("file")
    if not f:
        return "No file uploaded", 400
    fmt = request.form.get("format", "coo")
    thr_raw = request.form.get("threshold", "").strip()
    thr = int(thr_raw) if thr_raw != "" else None

    uid = uuid.uuid4().hex[:10]
    safe_name = f"{uid}_{f.filename}"
    in_path = UPLOAD_DIR / safe_name
    f.save(in_path)

    out_name = safe_name + ext_for_format(fmt)
    out_path = OUT_DIR / out_name

    # compress
    cargs = SimpleNamespace(
        input=str(in_path), output=str(out_path), format=fmt, threshold=thr
    )
    try:
        cli.compress(cargs)
    except Exception as e:
        return f"Compression failed: {e}", 500

    # decompress
    recon_name = safe_name + ".recon.png"
    recon_path = OUT_DIR / recon_name
    dargs = SimpleNamespace(input=str(out_path), output=str(recon_path))
    try:
        cli.decompress(dargs)
    except Exception as e:
        return f"Decompress failed: {e}", 500

    # visualize sparsity
    spars_name = safe_name + ".sparsity.png"
    spars_path = OUT_DIR / spars_name
    vargs = SimpleNamespace(input=str(out_path), output=str(spars_path))
    try:
        cli.visualize(vargs)
    except Exception as e:
        return f"Visualize failed: {e}", 500

    # stats
    try:
        orig_sz = file_size(str(in_path))
        comp_sz = file_size(str(out_path))
        recon_sz = file_size(str(recon_path))
    except Exception:
        orig_sz = comp_sz = recon_sz = 0

    # compute nonzeros/total if possible
    nonzeros = "?"
    total_pixels = "?"
    try:
        from sparse_formats import COO, read_coo_binary

        if fmt == "coo":
            coo = COO.from_json(str(out_path))
            nonzeros = len(coo.data)
            total_pixels = coo.shape[0] * coo.shape[1]
        elif fmt == "bin":
            coo = read_coo_binary(str(out_path))
            nonzeros = len(coo.data)
            total_pixels = coo.shape[0] * coo.shape[1]
    except Exception:
        pass

    ratio = f"{(orig_sz / comp_sz):.2f}" if comp_sz else "?"

    meta = {
        "original": str(in_path),
        "compressed": str(out_path),
        "reconstructed": str(recon_path),
        "sparsity": str(spars_path),
        "orig_size": orig_sz,
        "comp_size": comp_sz,
        "recon_size": recon_sz,
        "nonzeros": nonzeros,
        "total_pixels": total_pixels,
        "ratio": ratio,
    }
    meta_path = OUT_DIR / (safe_name + ".meta.json")
    with open(meta_path, "w") as mf:
        json.dump(meta, mf, indent=2)

    return render_template(
        "result.html",
        name=f.filename,
        orig=str(in_path.relative_to(BASE)),
        recon=str(recon_path.relative_to(BASE)),
        sparsity=str(spars_path.relative_to(BASE)),
        compfile=str(out_path.relative_to(BASE)),
        orig_name=f.filename,
        recon_name=recon_name,
        orig_size=orig_sz,
        recon_size=recon_sz,
        nonzeros=nonzeros,
        total_pixels=total_pixels,
        ratio=ratio,
    )


@app.route("/file/<path:relpath>")
def serve_file(relpath):
    p = BASE / relpath
    if not p.exists():
        abort(404)
    return send_file(str(p), conditional=True)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
