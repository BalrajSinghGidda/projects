#!/usr/bin/env python3
# events-server.py
# Full-featured Flask server for Network Topology visualization project
# - Cookie-based auth (SQLite)
# - Devices registration & listing
# - File uploads/downloads + temp links
# - SSE (/events) open to anonymous reporters
# - /log_event accepts anonymous events (for netcat/raw clients)
# - Web UI routes (/ , /upload, /files, /viewer.html) require login and redirect to /login

from flask import (
    Flask,
    request,
    Response,
    stream_with_context,
    send_from_directory,
    jsonify,
    session,
    g,
    abort,
    redirect,
    url_for,
)
import os, time, json, threading, secrets, sqlite3
from datetime import datetime, timezone
from html import escape
from urllib.parse import quote
from werkzeug.security import generate_password_hash, check_password_hash

# ---------- Config ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) or "."
EVENTS_FILE = os.path.join(BASE_DIR, "events.log")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATE_FILE = os.path.join(BASE_DIR, "state.json")
DB_PATH = os.path.join(BASE_DIR, "auth.db")
TEMP_TOKENS = {}  # token -> (name, expires_ts)

# Server settings
HOST = "0.0.0.0"
PORT = 5000
SESSION_SECRET = os.environ.get("FLASK_SECRET") or secrets.token_urlsafe(24)

app = Flask(__name__, static_folder=".")
app.secret_key = SESSION_SECRET
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 7  # 7 days

# ensure upload dir exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- Utilities ----------


def tail_file(path):
    # generator that yields appended lines (simple tail -f)
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
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024.0
    return f"{n:.1f} PB"


def fmt_mtime(ts):
    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return "-"


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
        try:
            del TEMP_TOKENS[token]
        except KeyError:
            pass
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

# ---------- Database helpers (SQLite) ----------


def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
        db = g._db = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(error):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      pw_hash TEXT NOT NULL,
      created_ts INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS devices (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      client_id TEXT NOT NULL,
      name TEXT,
      ua TEXT,
      last_seen INTEGER,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    db.commit()


# ---------- Auth helpers ----------


def login_required(f):
    # simple decorator
    from functools import wraps

    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            # redirect to login page
            return redirect("/login")
        return f(*args, **kwargs)

    return wrapped


# ---------- SSE (events) - open to anonymous reporters ----------
@app.route("/events")
def sse():
    def gen():
        for line in tail_file(EVENTS_FILE):
            yield f"data: {line.strip()}\n\n"

    return Response(stream_with_context(gen()), mimetype="text/event-stream")


# Provide a lightweight state endpoint (protected since it may reveal user info)
@app.route("/state")
@login_required
def state():
    if not os.path.exists(STATE_FILE):
        return jsonify({"nodes": []})
    with open(STATE_FILE) as f:
        return Response(f.read(), mimetype="application/json")


# ---------- Root and static pages (login/register/viewer) ----------
# Serve login/register pages (we created html earlier)
@app.route("/login")
def login_page():
    return send_from_directory(".", "login.html")


@app.route("/register")
def register_page():
    return send_from_directory(".", "register.html")


# viewer is gated: redirect to login if not authenticated
@app.route("/")
@login_required
def root():
    return send_from_directory(".", "viewer.html")


# ---------- Auth endpoints ----------
@app.route("/register", methods=["POST"])
def api_register():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    pw = data.get("password")
    if not username or not pw:
        return jsonify({"ok": False, "error": "missing"}), 400
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users (username, pw_hash, created_ts) VALUES (?, ?, ?)",
            (username, generate_password_hash(pw), int(time.time())),
        )
        db.commit()
        return jsonify({"ok": True})
    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "error": "user exists"}), 409


@app.route("/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    pw = data.get("password")
    if not username or not pw:
        return jsonify({"ok": False, "error": "missing"}), 400
    db = get_db()
    row = db.execute(
        "SELECT id, pw_hash FROM users WHERE username=?", (username,)
    ).fetchone()
    if not row or not check_password_hash(row["pw_hash"], pw):
        return jsonify({"ok": False, "error": "bad"}), 401
    session.clear()
    session["user_id"] = row["id"]
    session.permanent = True
    return jsonify({"ok": True, "user_id": row["id"], "username": username})


@app.route("/logout", methods=["POST", "GET"])
@login_required
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/me")
@login_required
def api_me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"ok": False}), 401
    db = get_db()
    row = db.execute("SELECT id, username FROM users WHERE id=?", (uid,)).fetchone()
    if not row:
        return jsonify({"ok": False}), 401
    return jsonify({"ok": True, "user_id": row["id"], "username": row["username"]})


# ---------- Devices endpoints (protected) ----------
@app.route("/devices/register", methods=["POST"])
@login_required
def devices_register():
    data = request.get_json(force=True)
    client_id = (data.get("client_id") or "").strip()
    name = (data.get("name") or "").strip()
    ua = request.headers.get("User-Agent", "")[:255]
    if not client_id:
        return jsonify({"ok": False, "error": "missing client_id"}), 400
    uid = session["user_id"]
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id FROM devices WHERE user_id=? AND client_id=?", (uid, client_id)
    )
    r = cur.fetchone()
    ts = int(time.time())
    if r:
        cur.execute(
            "UPDATE devices SET name=?, ua=?, last_seen=? WHERE id=?",
            (name, ua, ts, r["id"]),
        )
    else:
        cur.execute(
            "INSERT INTO devices (user_id, client_id, name, ua, last_seen) VALUES (?, ?, ?, ?, ?)",
            (uid, client_id, name, ua, ts),
        )
    db.commit()
    return jsonify({"ok": True})


@app.route("/devices/list")
@login_required
def devices_list():
    uid = session["user_id"]
    db = get_db()
    rows = db.execute(
        "SELECT client_id, name, last_seen FROM devices WHERE user_id=? ORDER BY last_seen DESC",
        (uid,),
    ).fetchall()
    devices = []
    for r in rows:
        devices.append(
            {
                "client_id": r["client_id"],
                "name": r["name"] or r["client_id"],
                "last_seen": r["last_seen"],
            }
        )
    return jsonify({"ok": True, "devices": devices})


# ---------- Event logging (open) ----------
@app.route("/log_event", methods=["POST"])
def log_event():
    # Accept anonymous events (from netcat/raw clients) and authenticated ones alike
    try:
        data = request.get_json(force=True)
    except Exception:
        # if not JSON, try form fields
        data = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "type": "raw",
            "detail": {"raw": request.get_data(as_text=True)[:4000]},
        }
    try:
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print("log_event write error:", e)
    return jsonify({"ok": True})


# ---------- Uploads & files (web protected) ----------
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file = request.files.get("file")
        if not file:
            return jsonify({"ok": False, "error": "no file"}), 400
        safe_name = os.path.basename(file.filename)
        path = os.path.join(UPLOAD_DIR, safe_name)
        try:
            file.save(path)
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

        # prefer client_id if submitted (from browser localStorage), else use remote addr
        client_id = (
            request.form.get("client_id")
            or request.headers.get("X-Forwarded-For")
            or request.remote_addr
            or session.get("user_id")
        )
        evt = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "type": "put_done",
            "detail": {
                "ip": client_id,
                "file": safe_name,
                "size": os.path.getsize(path),
            },
        }
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(evt) + "\n")
        return jsonify({"ok": True, "file": safe_name})

    # serve upload page if exists, else small fallback
    if os.path.exists(os.path.join(".", "upload.html")):
        return send_from_directory(".", "upload.html")
    return '<html><body><h1>Upload</h1><form method="post" enctype="multipart/form-data"><input type=file name=file><input type=submit></form></body></html>'

@app.route("/files")
@login_required
def list_files():
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception:
        return (
            "<!doctype html><html><body><h1>Files error</h1><p>Could not ensure uploads directory.</p></body></html>",
            500,
        )

    def safe_listdir(path):
        try:
            return sorted(os.listdir(path))
        except Exception:
            return []

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
# @app.route("/files")
# @login_required
# def list_files():
#     """Return a JSON list of files in the uploads directory.
#     Used by the JS-driven files.html page.
#     """
#     try:
#         os.makedirs(UPLOAD_DIR, exist_ok=True)
#     except Exception:
#         return jsonify({"ok": False, "error": "uploads dir error"}), 500
# 
#     entries = sorted(
#         [p for p in os.listdir(UPLOAD_DIR) if not p.startswith(".")], reverse=True
#     )
#     files = []
#     for name in entries:
#         full = os.path.join(UPLOAD_DIR, name)
#         try:
#             st = os.stat(full)
#             files.append(
#                 {
#                     "name": name,
#                     "size": st.st_size,
#                     "size_h": human_size(st.st_size),
#                     "mtime": int(st.st_mtime),
#                     "mtime_s": fmt_mtime(st.st_mtime),
#                 }
#             )
#         except Exception:
#             files.append(
#                 {
#                     "name": name,
#                     "size": None,
#                     "size_h": "?",
#                     "mtime": None,
#                     "mtime_s": "?",
#                 }
#             )
# 
#     return jsonify({"ok": True, "files": files})


@app.route("/files/<path:name>")
@login_required
def serve_file(name):
    if ".." in name or name.startswith("/"):
        abort(404)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, name)
    if not os.path.isfile(path):
        abort(404)
    return send_from_directory(UPLOAD_DIR, name, as_attachment=True)


@app.route("/files/temp", methods=["POST"])
@login_required
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
@login_required
def serve_temp(token):
    name = validate_token(token)
    if not name:
        abort(404)
    try:
        return send_from_directory(UPLOAD_DIR, name, as_attachment=True)
    except Exception as e:
        print("serve_temp error:", e)
        abort(500)


# ---------- Run server (init DB inside app context) ----------
if __name__ == "__main__":
    # create DB schema inside app context
    with app.app_context():
        init_db()
    print(f"Events server running at http://{HOST}:{PORT}/")
    # ensure events file exists
    open(EVENTS_FILE, "a").close()
    app.run(host=HOST, port=PORT, debug=False)
