#!/usr/bin/env python3
"""
Auth + Signalling server (Socket.IO) for demo.

 - Provides /register, /login, /logout, /devices endpoints (simple SQLite)
 - Socket.IO signalling for WebRTC: offer/answer/candidate
 - Chat and multi-channel broadcast via socket.io rooms

Run:
    python3 auth-signaling.py
"""

from flask import Flask, request, jsonify, make_response, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room
import secrets, time, os
from functools import wraps

APP_SECRET = os.environ.get("APP_SECRET") or secrets.token_urlsafe(24)
DB_PATH = "sqlite:///auth_signaling.db"
SESSION_COOKIE = "ns_session"
DEVICE_COOKIE = "ns_device"
TOKEN_EXP = 60 * 60 * 24 * 7

app = Flask(__name__)
app.config["SECRET_KEY"] = APP_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash = db.Column(db.String(256), nullable=False)


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(128), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    label = db.Column(db.String(128), default="")
    last_seen = db.Column(db.Float, default=time.time)


def init_db():
    db.create_all()


SESSIONS = {}


def create_session_cookie(resp, username):
    token = secrets.token_urlsafe(32)
    resp.set_cookie(
        SESSION_COOKIE, token, httponly=True, max_age=TOKEN_EXP, samesite="Lax"
    )
    SESSIONS[token] = username


def get_current_user():
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    username = SESSIONS.get(token)
    if not username:
        return None
    u = User.query.filter_by(username=username).first()
    return u


def require_auth(fn):
    @wraps(fn)
    def inner(*a, **kw):
        u = get_current_user()
        if not u:
            return jsonify({"ok": False, "error": "auth required"}), 401
        g.user = u
        return fn(*a, **kw)

    return inner


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"ok": False, "error": "missing"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"ok": False, "error": "exists"}), 400
    pw_hash = generate_password_hash(password)
    u = User(username=username, pw_hash=pw_hash)
    db.session.add(u)
    db.session.commit()
    resp = jsonify({"ok": True})
    create_session_cookie(resp, username)
    return resp


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    u = User.query.filter_by(username=username).first()
    if not u or not check_password_hash(u.pw_hash, password):
        return jsonify({"ok": False, "error": "invalid"}), 401
    device_id = data.get("device_id") or secrets.token_urlsafe(8)
    label = data.get("label") or "browser"
    d = Device(device_id=device_id, user_id=u.id, label=label, last_seen=time.time())
    db.session.add(d)
    db.session.commit()
    resp = jsonify({"ok": True, "device_id": device_id})
    create_session_cookie(resp, username)
    resp.set_cookie(DEVICE_COOKIE, device_id, max_age=TOKEN_EXP, samesite="Lax")
    return resp


@app.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get(SESSION_COOKIE)
    if token and token in SESSIONS:
        del SESSIONS[token]
    resp = jsonify({"ok": True})
    resp.delete_cookie(SESSION_COOKIE)
    resp.delete_cookie(DEVICE_COOKIE)
    return resp


@app.route("/devices")
@require_auth
def devices():
    u = g.user
    devs = Device.query.filter_by(user_id=u.id).all()
    out = [
        {"device_id": d.device_id, "label": d.label, "last_seen": d.last_seen}
        for d in devs
    ]
    return jsonify({"ok": True, "devices": out})


clients = {}


@socketio.on("connect")
def on_connect():
    emit("hello", {"ok": True})


@socketio.on("identify")
def on_identify(payload):
    username = payload.get("username") or "anonymous"
    device_id = payload.get("device_id") or secrets.token_urlsafe(8)
    clients[request.sid] = {"username": username, "device_id": device_id}
    join_room(device_id)
    emit("identified", {"device_id": device_id})
    emit("presence", {"device_id": device_id, "when": time.time()}, broadcast=True)


@socketio.on("disconnect")
def on_disconnect():
    info = clients.pop(request.sid, None)
    if info:
        leave_room(info["device_id"])
        emit("presence", {"device_id": info["device_id"], "left": True}, broadcast=True)


@socketio.on("offer")
def on_offer(payload):
    to = payload.get("to_device")
    if to:
        emit("offer", payload, to=to)


@socketio.on("answer")
def on_answer(payload):
    to = payload.get("to_device")
    if to:
        emit("answer", payload, to=to)


@socketio.on("candidate")
def on_candidate(payload):
    to = payload.get("to_device")
    if to:
        emit("candidate", payload, to=to)


@socketio.on("chat")
def on_chat(payload):
    channel = payload.get("channel", "global")
    emit("chat", payload, room=channel)


@socketio.on("join")
def on_join(payload):
    channel = payload.get("channel")
    if channel:
        join_room(channel)
        emit("system", {"msg": f"joined {channel}"})


@socketio.on("leave")
def on_leave(payload):
    channel = payload.get("channel")
    if channel:
        leave_room(channel)
        emit("system", {"msg": f"left {channel}"})


@app.route("/_clients")
def _clients():
    return jsonify({"clients": clients})


if __name__ == "__main__":
    with app.app_context():
        init_db()
    print("Auth + signalling server running on :6000")
    socketio.run(app, host="0.0.0.0", port=6000)
