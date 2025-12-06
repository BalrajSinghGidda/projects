#!/usr/bin/env python3
"""
Events server:
 - serves viewer.html at /
 - serves upload.html at /upload (POST to upload files)
 - SSE endpoint at /events (tails events.log)
 - /files listing (file size + mtime), /files/<name> for downloads
 - temporary /files/temp endpoints to create short links

Usage:
    python3 events-server.py
"""

from flask import (
    Flask,
    Response,
    stream_with_context,
    send_from_directory,
    jsonify,
    request,
    abort,
)
import os, time, json, threading, secrets, socket
from html import escape
from urllib.parse import quote
from datetime import datetime, timezone

# configuration
EVENTS_FILE = "events.log"
UPLOAD_DIR = "uploads"
STATE_FILE = "state.json"
TEMP_TOKENS = {}  # token -> (name, expires_ts)

app = Flask(__name__, static_folder=".")


# ---------- utilities ----------
def tail_file(path):
    while not os.path.exists(path):
        time.sleep(0.05)
    with open(path, "r") as f:
        for line in f:
            yield line
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(0.05)


def human_size(n):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024.0
    return f"{n:.1f} PB"


def fmt_mtime(ts):
    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return "-"


def safe_listdir(path):
    try:
        return sorted(os.listdir(path))
    except Exception:
        return []


def make_token(filename, ttl):
    token = secrets.token_urlsafe(18)
    expires = time.time() + int(ttl)
    TEMP_TOKENS[token] = (filename, expires)
    return token, expires


def validate_token(token):
    rec = TEMP_TOKENS.get(token)
    if not rec:
        return None
    name, expires = rec
    if time.time() > expires:
        del TEMP_TOKENS[token]
        return None
    return name


def token_cleanup_loop():
    while True:
        now = time.time()
        to_delete = [t for t, (_, exp) in list(TEMP_TOKENS.items()) if exp < now]
        for t in to_delete:
            try:
                del TEMP_TOKENS[t]
            except KeyError:
                pass
        time.sleep(5)


_cleanup_thread = threading.Thread(target=token_cleanup_loop, daemon=True)
_cleanup_thread.start()


# ---------- SSE endpoint ----------
@app.route("/events")
def sse():
    def gen():
        for line in tail_file(EVENTS_FILE):
            yield f"data: {line.strip()}\n\n"

    return Response(stream_with_context(gen()), mimetype="text/event-stream")


@app.route("/state")
def state():
    if not os.path.exists(STATE_FILE):
        return jsonify({"nodes": []})
    with open(STATE_FILE) as f:
        return Response(f.read(), mimetype="application/json")


# serve viewer.html (must exist next to this script)
@app.route("/")
def root():
    if os.path.exists("viewer.html"):
        return send_from_directory(".", "viewer.html")
    return ("viewer.html missing", 500)


# serve upload.html
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file = request.files.get("file")
        if not file:
            return "No file selected", 400
        safe_name = os.path.basename(file.filename)
        path = os.path.join(UPLOAD_DIR, safe_name)
        try:
            file.save(path)
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

        # try to get device id / client id from posted JSON header or fallback to request.remote_addr
        client_id = (
            request.form.get("client_id")
            or request.headers.get("X-Client-Id")
            or request.headers.get("X-Forwarded-For", request.remote_addr)
        )

        evt = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "type": "put_done",
            "detail": {
                "client": client_id,
                "file": safe_name,
                "size": os.path.getsize(path),
            },
        }
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(evt) + "\n")
        return jsonify({"ok": True, "file": safe_name})

    if os.path.exists("upload.html"):
        return send_from_directory(".", "upload.html")
    return ("Upload page missing", 500)


@app.route("/log_event", methods=["POST"])
def log_event():
    data = request.get_json(force=True)
    try:
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print("log_event write error:", e)
    return jsonify({"ok": True})


# ---------- Files listing + serving ----------
@app.route("/files")
def list_files():
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception:
        return (
            "<!doctype html><html><body><h1>Files error</h1><p>Could not ensure uploads directory.</p></body></html>",
            500,
        )

    entries = safe_listdir(UPLOAD_DIR)
    rows = []
    for name in sorted(entries, reverse=True):
        if name.startswith("."):
            continue
        full = os.path.join(UPLOAD_DIR, name)
        try:
            st = os.stat(full)
            size = human_size(st.st_size)
            mtime = fmt_mtime(st.st_mtime)
        except Exception:
            size = "?"
            mtime = "?"
        safe_label = escape(name)
        safe_href = quote(name, safe="")
        rows.append(
            "<tr>"
            f"<td style='padding:8px 12px;'><a href='/files/{safe_href}' style='color:var(--pine);text-decoration:none'>{safe_label}</a></td>"
            f"<td style='padding:8px 12px; text-align:right'>{size}</td>"
            f"<td style='padding:8px 12px; text-align:right'>{mtime}</td>"
            "</tr>"
        )

    table_body = (
        "\n".join(rows)
        if rows
        else "<tr><td colspan='3'><em>No uploaded files.</em></td></tr>"
    )

    html = (
        "<!doctype html>\n"
        "<html>\n"
        "<head>\n"
        "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>\n"
        "<title>Files — Network Node</title>\n"
        "<style>\n"
        ":root{ --base:#faf4ed; --text:#2b2430; --pine:#316a78; --rose:#e6b8c4; --muted:#6b646f; }\n"
        "html,body{ height:100vh; margin:0; overflow:hidden; scrollbar-gutter:stable; }\n"
        "body{ background:var(--base); color:var(--text); font-family:Inter,system-ui,sans-serif; padding-top:72px; }\n"
        ".topnav{ position:fixed; top:0; left:0; right:0; box-sizing:border-box; padding:12px 48px 12px 20px; display:flex; align-items:center; justify-content:space-between; background:#f3ebe7; z-index:9999; border-bottom:1px solid rgba(43,36,48,0.06); }\n"
        ".nav-links{ display:flex; gap:14px; margin-left:auto; }\n"
        ".topnav a{ text-decoration:none; color:var(--pine); font-weight:600; padding:6px 4px; }\n"
        "#wrap{ height:calc(100vh-72px); display:flex; align-items:flex-start; justify-content:center; padding:18px; box-sizing:border-box; overflow:auto; }\n"
        ".table-card{ max-width:1000px; width:90%; background:#fffaf6; border-radius:12px; box-shadow: 0 8px 24px rgba(18,16,20,0.04); overflow:auto; }\n"
        "table{ width:100%; border-collapse:collapse; }\n"
        "th{ text-align:left; padding:12px; border-bottom:1px solid rgba(43,36,48,0.04); background: rgba(0,0,0,0.02); position: sticky; top:0; z-index:2; }\n"
        "td{ border-bottom:1px solid rgba(43,36,48,0.03); }\n"
        ".row-meta{ color:var(--muted); font-size:13px; }\n"
        ".small{ font-size:12px; color:var(--muted); }\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "<nav class='topnav'><div style='color:var(--pine); font-weight:700;'>Network Topology Demo</div><div class='nav-links'><a href='/'>Visualization</a><a href='/upload'>Upload</a></div></nav>\n"
        "<div id='wrap'><div class='table-card'><table><thead><tr><th>File</th><th style='text-align:right'>Size</th><th style='text-align:right'>Modified</th></tr></thead><tbody>\n"
        + table_body
        + "\n</tbody></table></div></div>\n"
        "</body>\n"
        "</html>"
    )
    return html


@app.route("/files/<path:name>")
def serve_file(name):
    if ".." in name or name.startswith("/"):
        abort(404)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, name)
    if not os.path.isfile(path):
        abort(404)
    try:
        return send_from_directory(UPLOAD_DIR, name, as_attachment=True)
    except Exception as e:
        print("serve_file error:", e)
        return (
            "<!doctype html><html><body><h1>Unable to serve file</h1></body></html>",
            500,
        )


@app.route("/files/temp", methods=["POST"])
def create_temp_link():
    data = request.get_json(force=True)
    name = data.get("name")
    if not name:
        return jsonify({"ok": False, "error": "missing name"}), 400
    name = os.path.basename(name)
    full = os.path.join(UPLOAD_DIR, name)
    if not os.path.isfile(full):
        return jsonify({"ok": False, "error": "file not found"}), 404
    ttl = int(data.get("ttl", 60))
    token, expires = make_token(name, ttl)
    url = f"/files/temp/{token}"
    return jsonify({"ok": True, "url": url, "expires": int(expires)})


@app.route("/files/temp/<token>")
def serve_temp(token):
    name = validate_token(token)
    if not name:
        abort(404)
    try:
        return send_from_directory(UPLOAD_DIR, name, as_attachment=True)
    except Exception as e:
        print("serve_temp error:", e)
        abort(500)


if __name__ == "__main__":
    print("Events server running at http://0.0.0.0:5000/")
    app.run(host="0.0.0.0", port=5000, debug=False)
