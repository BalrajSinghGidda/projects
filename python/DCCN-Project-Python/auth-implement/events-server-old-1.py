#!/usr/bin/env python3
# events-server.py
# Extended Flask + uploads + file listing + simple auth + device registration
# Based on your original file. See also auth_signaling.py for signalling.

from flask import (
    Flask,
    Response,
    stream_with_context,
    send_from_directory,
    jsonify,
    request,
    abort,
    session,
    g,
)
import os, time, json, socket, threading, secrets, sqlite3
from html import escape
from urllib.parse import quote
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

# config
EVENTS_FILE = "events.log"
UPLOAD_DIR = "uploads"
STATE_FILE = "state.json"
DB_PATH = "auth.db"
TEMP_TOKENS = {}  # token -> (name, expires_ts)

app = Flask(__name__, static_folder=".")
# set a secret key for session cookies (change for production)
app.secret_key = os.environ.get("FLASK_SECRET") or secrets.token_urlsafe(24)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 7


# ---------------- utils ----------------
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
        to_delete = [t for t, (_, exp) in TEMP_TOKENS.items() if exp < now]
        for t in to_delete:
            try:
                del TEMP_TOKENS[t]
            except KeyError:
                pass
        time.sleep(5)


_cleanup_thread = threading.Thread(target=token_cleanup_loop, daemon=True)
_cleanup_thread.start()


# ---------------- events SSE ----------------
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


@app.route("/")
def root():
    return send_from_directory(".", "viewer.html")


# ---------------- simple DB helpers (SQLite) ----------------
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
    sql = """
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
    """
    db.executescript(sql)
    db.commit()


# init DB at startup
# init_db()


# ---------------- auth endpoints ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username")
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
def login():
    data = request.get_json(force=True)
    username = data.get("username")
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
    return jsonify({"ok": True, "user_id": row["id"]})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


# ---------------- device registration ----------------
@app.route("/devices/register", methods=["POST"])
def register_device():
    if "user_id" not in session:
        return jsonify({"ok": False, "error": "not logged in"}), 401
    data = request.get_json(force=True)
    client_id = data.get("client_id")
    name = data.get("name") or "browser"
    ua = request.headers.get("User-Agent", "")[:255]
    uid = session["user_id"]
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id FROM devices WHERE user_id=? AND client_id=?", (uid, client_id)
    )
    r = cur.fetchone()
    if r:
        cur.execute(
            "UPDATE devices SET name=?, ua=?, last_seen=? WHERE id=?",
            (name, ua, int(time.time()), r["id"]),
        )
    else:
        cur.execute(
            "INSERT INTO devices (user_id, client_id, name, ua, last_seen) VALUES (?, ?, ?, ?, ?)",
            (uid, client_id, name, ua, int(time.time())),
        )
    db.commit()
    return jsonify({"ok": True})


# ---------------- upload (POST) + embedded upload page (GET) ----------------
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

        # prefer real client identifier if provided in request JSON headers or form field
        # we previously had client_id sent by the browser as 'detail.ip' in events; here we try headers then remote_addr
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        evt = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "type": "put_done",
            "detail": {
                "ip": client_ip,
                "file": safe_name,
                "size": os.path.getsize(path),
            },
        }
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(evt) + "\n")
        return jsonify({"ok": True, "file": safe_name})

    # embedded upload page (rose-pine dawn look) with stable client_id logic
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Upload — Network Node</title>
<style>
:root{ --base:#faf4ed; --surface:#fffaf6; --overlay:#f3ebe7; --muted:#6b646f; --rose:#e6b8c4; --pine:#316a78; --iris:#8a6fd1; --gold:#c08a4b; --foam:#5fb6b1; --glass: rgba(43,36,48,0.04); }
html,body{ height:100vh; margin:0; overflow:hidden; scrollbar-gutter:stable; }
body{ background:var(--base); color:#2b2430; font-family:Inter,system-ui,sans-serif; padding-top:72px; }
.topnav{ position:fixed; top:0; left:0; right:0; padding:12px 48px 12px 20px; display:flex; align-items:center; justify-content:space-between; background:var(--overlay); z-index:9999; border-bottom:1px solid rgba(43,36,48,0.06);}
.nav-links{ display:flex; gap:14px; margin-left:auto; }
.topnav a{ text-decoration:none; color:var(--pine); font-weight:600; padding:6px 4px;}
.topnav a.active{ color:var(--rose); }
#wrap{ height:calc(100vh - 72px); display:flex; align-items:center; justify-content:center; }
#uploadBox{ width:min(760px,92%); background:var(--surface); padding:38px 36px; border-radius:14px; box-shadow:0 18px 40px rgba(18,16,20,0.06); border:1px solid rgba(43,36,48,0.03); text-align:center; }
h2{ margin:0 0 18px 0; color:var(--rose); font-size:20px; font-weight:700; }
input[type=file]{ width:320px; padding:10px; border-radius:10px; border:1px solid rgba(43,36,48,0.06); background:var(--overlay); }
button{ margin-top:8px; background:var(--pine); color:var(--base); border:none; padding:10px 22px; border-radius:10px; font-weight:700; cursor:pointer; box-shadow: 0 6px 18px rgba(49,106,120,0.08); }
#progress{ position:relative; width:80%; max-width:480px; height:16px; margin:20px auto; background:var(--glass); border-radius:8px; overflow:hidden; border:1px solid rgba(43,36,48,0.03); }
#bar{ position:absolute; left:0; top:0; height:100%; width:0%; background: linear-gradient(90deg,var(--iris),var(--rose)); border-radius:8px; transition: width 0.12s ease-out; box-shadow: inset 0 -4px 8px rgba(0,0,0,0.03); }
#msg{ margin-top:12px; color:#7f7482; }
@media (max-height:480px){ #wrap{ align-items:flex-start; overflow:auto; padding-top:12px; } #uploadBox{ margin:18px 0; } }
</style>
</head><body>
<nav class="topnav"><div style="color:var(--pine); font-weight:700;">Network Topology Demo</div><div class="nav-links"><a href="/">Visualization</a><a href="/upload" class="active">Upload</a><a href="/files">Files</a></div></nav>
<div id="wrap"><div id="uploadBox" role="region" aria-label="Upload panel">
<h2>Upload a File to the Network Server</h2>
<input id="fileInput" type="file" aria-label="Choose file"><br>
<button id="uploadBtn">Upload</button>
<div id="progress"><div id="bar"></div></div>
<div id="msg"></div>
<a href="/" style="display:inline-block; margin-top:12px; color:var(--pine); font-weight:600;">← Back to Visualization</a>
</div></div>
<script>
function generateClientId(){ const r=Math.random().toString(36).slice(2,8); const t=Date.now().toString(36).slice(-6); return r+'-'+t; }
function getClientId(){ try{ let id=localStorage.getItem('client_id'); if(!id){ id=generateClientId(); localStorage.setItem('client_id', id);} return id;}catch(e){return generateClientId();}}
const CLIENT_ID = getClientId();
function emitEvent(e){ if(!e.detail) e.detail={}; if(!e.detail.ip) e.detail.ip = CLIENT_ID; if(navigator.sendBeacon){ try{ navigator.sendBeacon('/log_event', JSON.stringify(e)); return; }catch(err){} } fetch('/log_event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(e)}).catch(()=>{}); }
function resetBar(delay=900){ setTimeout(()=>{ document.getElementById('bar').style.width='0%'; }, delay); }
document.getElementById('uploadBtn').addEventListener('click', () => {
  const file=document.getElementById('fileInput').files[0];
  const bar=document.getElementById('bar'); const msg=document.getElementById('msg');
  if(!file){ msg.textContent='Please select a file.'; msg.style.color='var(--rose)'; return; }
  const client_ip = CLIENT_ID;
  emitEvent({ ts:new Date().toISOString(), type:'put_start', detail:{ ip: client_ip, file: file.name, size: file.size } });
  const xhr=new XMLHttpRequest(); xhr.open('POST','/upload',true); bar.style.width='2%';
  xhr.upload.onprogress=(e)=>{ if(e.lengthComputable){ const pct=Math.floor((e.loaded/e.total)*100); bar.style.width=pct+'%'; } };
  xhr.onload=()=>{ if(xhr.status===200){ bar.style.width='100%'; msg.textContent='Upload complete!'; msg.style.color='var(--gold)'; emitEvent({ ts:new Date().toISOString(), type:'put_done', detail:{ ip: client_ip, file: file.name, size: file.size } }); } else { msg.textContent='Upload failed.'; msg.style.color='var(--rose)'; } resetBar(); };
  xhr.onerror=()=>{ msg.textContent='Network error.'; msg.style.color='var(--rose)'; resetBar(); };
  const form=new FormData(); form.append('file', file); msg.textContent='Uploading...'; msg.style.color='var(--foam)'; xhr.send(form);
});
</script></body></html>"""


# ---------------- event logging endpoint ----------------
@app.route("/log_event", methods=["POST"])
def log_event():
    data = request.get_json(force=True)
    try:
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print("log_event write error:", e)
    return jsonify({"ok": True})


# ---------------- files listing & download ----------------
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
            size, mtime = "?", "?"
        safe_label = escape(name)
        safe_href = quote(name, safe="")
        rows.append(
            "<tr>"
            + f"<td style='padding:8px 12px;'><a href='/files/{safe_href}' style='color:var(--pine);text-decoration:none'>{safe_label}</a></td>"
            + f"<td style='padding:8px 12px; text-align:right'>{size}</td>"
            + f"<td style='padding:8px 12px; text-align:right'>{mtime}</td>"
            + "</tr>"
        )

    table_body = (
        "\n".join(rows)
        if rows
        else "<tr><td colspan='3'><em>No uploaded files.</em></td></tr>"
    )

    html = (
        "<!doctype html>\n<html>\n<head>\n<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>\n<title>Files — Network Node</title>\n<style>\n:root{ --base:#faf4ed; --text:#2b2430; --pine:#316a78; --rose:#e6b8c4; --muted:#6b646f; }\nhtml,body{ height:100vh; margin:0; overflow:hidden; scrollbar-gutter:stable; }\nbody{ background:var(--base); color:var(--text); font-family:Inter,system-ui,sans-serif; padding-top:72px; }\n.topnav{ position:fixed; top:0; left:0; right:0; box-sizing:border-box; padding:12px 48px 12px 20px; display:flex; align-items:center; justify-content:space-between; background:#f3ebe7; z-index:9999; border-bottom:1px solid rgba(43,36,48,0.06); }\n.nav-links{ display:flex; gap:14px; margin-left:auto; }\n.topnav a{ text-decoration:none; color:var(--pine); font-weight:600; padding:6px 4px; }\n#wrap{ height:calc(100vh-72px); display:flex; align-items:flex-start; justify-content:center; padding:18px; box-sizing:border-box; overflow:auto; }\n.table-card{ max-width:1000px; width:90%; background:#fffaf6; border-radius:12px; box-shadow: 0 8px 24px rgba(18,16,20,0.04); overflow:auto; }\ntable{ width:100%; border-collapse:collapse; }\nth{ text-align:left; padding:12px; border-bottom:1px solid rgba(43,36,48,0.04); background: rgba(0,0,0,0.02); position: sticky; top:0; z-index:2; }\ntd{ border-bottom:1px solid rgba(43,36,48,0.03); }\n.row-meta{ color:var(--muted); font-size:13px; }\n.small{ font-size:12px; color:var(--muted); }\n</style>\n</head>\n<body>\n<nav class='topnav'><div style='color:var(--pine); font-weight:700;'>Network Topology Demo</div><div class='nav-links'><a href='/'>Visualization</a><a href='/upload'>Upload</a><a href='/files'>Files</a></div></nav>\n<div id='wrap'><div class='table-card'><table><thead><tr><th>File</th><th style='text-align:right'>Size</th><th style='text-align:right'>Modified</th></tr></thead><tbody>\n"
        + table_body
        + "\n</tbody></table></div></div>\n</body>\n</html>"
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
    # ensure DB schema is created inside an application context
    with app.app_context():
        init_db()

    print("Events server running at http://0.0.0.0:5000/")
    app.run(host="0.0.0.0", port=5000, debug=False)
