#!/usr/bin/env python3
from flask import (
    Flask,
    Response,
    stream_with_context,
    send_from_directory,
    jsonify,
    request,
    redirect,
)
import time, os, json, socket

EVENTS_FILE = "events.log"
STATE_FILE = "state.json"
app = Flask(__name__, static_folder=".")


def tail_file(path):
    while not os.path.exists(path):
        time.sleep(0.1)
    with open(path, "r") as f:
        for line in f:
            yield line
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(0.1)


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


EVENTS_FILE = "events.log"
STATE_FILE = "state.json"
UPLOAD_DIR = "uploads"

app = Flask(__name__, static_folder=".")


def tail_file(path):
    while not os.path.exists(path):
        time.sleep(0.1)
    with open(path, "r") as f:
        for line in f:
            yield line
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(0.1)


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


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file = request.files.get("file")
        if not file:
            return "No file selected", 400
        path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(path)

        evt = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "type": "put_done",
            "detail": {
                "ip": socket.gethostbyname(socket.gethostname()),
                "file": file.filename,
                "size": os.path.getsize(path),
            },
        }
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(evt) + "\n")
        return jsonify({"ok": True, "file": file.filename})

    # GET -> return styled AJAX upload page
    return """
    <!doctype html>
    <html lang='en'>
    <head>
      <meta charset='utf-8'/>
      <title>Upload — Network Node</title>
      <style>
        :root {
          --base: #191724;
          --surface: #1f1d2e;
          --overlay: #26233a;
          --muted: #6e6a86;
          --subtle: #908caa;
          --text: #e0def4;
          --love: #eb6f92;
          --gold: #f6c177;
          --rose: #ebbcba;
          --pine: #31748f;
          --foam: #9ccfd8;
          --iris: #c4a7e7;
        }
        body {
          font-family: 'Inter', system-ui, sans-serif;
          background: var(--base);
          color: var(--text);
          text-align: center;
          padding-top: 80px;
          margin: 0;
        }
        h2 {
          color: var(--rose);
          font-weight: 600;
        }
        #uploadBox {
          background: var(--surface);
          display: inline-block;
          padding: 30px 40px;
          border-radius: 16px;
          box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        }
        input[type=file] {
          background: var(--overlay);
          border: 1px solid var(--muted);
          border-radius: 10px;
          color: var(--text);
          padding: 10px;
          width: 250px;
          margin-bottom: 20px;
        }
        button {
          background: var(--pine);
          border: none;
          color: var(--base);
          padding: 10px 24px;
          border-radius: 10px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease-in-out;
        }
        button:hover { background: var(--foam); }
        /* Progress bar responsive & rose-pine */
#progress {
  width: 100%;
  max-width: 520px;      /* responsive cap */
  height: 14px;
  border-radius: 12px;
  background: rgba(255,255,255,0.02);
  margin: 18px auto;
  overflow: hidden;
  box-shadow: inset 0 2px 6px rgba(0,0,0,0.4);
}
#bar {
  width: 0%;
  height: 100%;
  border-radius: 12px;
  background: linear-gradient(90deg, var(--iris), var(--rose));
  transition: width 120ms linear;
  transform-origin: left center;
}
#progress.wrap {
  padding: 4px; /* optional inner padding for style */
}
        #msg {
          margin-top: 15px;
          font-size: 14px;
          color: var(--subtle);
        }
        a {
          color: var(--foam);
          text-decoration: none;
          display:block;
          margin-top:20px;
        }
      </style>
    </head>
    <body>
  <nav style="
  position: fixed;
  top: 0; left: 0;
  width: 100%;
  background: var(--overlay);
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
  z-index: 50;
">
  <div style="color: var(--foam); font-weight: 600; font-size: 15px;">
    Network Topology Demo
  </div>
  <div style="display: flex; gap: 18px; font-size: 14px;">
    <a href="/" style="color: var(--rose); text-decoration: none;">Visualization</a>
    <a href="/upload" style="color: var(--foam); text-decoration: none;">Upload</a>
  </div>
</nav>
      <div id='uploadBox'>
        <h2>Upload a File to the Network Server</h2>
        <input type='file' id='fileInput'><br>
        <button onclick='uploadFile()'>Upload</button>
        <div id='progress'><div id='bar'></div></div>
        <div id='msg'></div>
        <a href='/'>← Back to Visualization</a>
      </div>
      <script>
  // helper to POST a JSON event to server (put_start/put_done)
  function emitEvent(event) {
    fetch('/log_event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    }).catch(()=>{/* ignore failures */});
  }

  // DOM refs
  const bar = document.getElementById('bar');
  const msg = document.getElementById('msg');

  // reset bar visually
  function resetBar(delay = 600) {
    setTimeout(() => {
      bar.style.width = '0%';
    }, delay);
  }

  // fake progress generator (used as fallback)
  function createFakeProgress() {
    let value = 0;
    let accel = 0.6;
    const id = setInterval(() => {
      value += Math.max(0.3, Math.random() * 3) * accel;
      value = Math.min(98, value);
      bar.style.width = value + '%';
      accel *= 0.99;
    }, 120);
    return () => { clearInterval(id); bar.style.width = '99%'; }; // returns stop function
  }

  function uploadFile() {
    const fileElem = document.getElementById('fileInput');
    const file = fileElem.files[0];
    if (!file) {
      msg.textContent = 'Please select a file.';
      return;
    }

    const client_ip = window.location.hostname; // okay for demo IP
    emitEvent({ ts: new Date().toISOString(), type: 'put_start', detail: { ip: client_ip, file: file.name, size: file.size } });

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);

    // fallback if progress never fires
    let fakeStop = null;
    let sawProgress = false;
    const fallbackTimer = setTimeout(() => {
      if (!sawProgress) {
        fakeStop = createFakeProgress();
      }
    }, 180); // 180ms — tweakable

    xhr.upload.onprogress = (e) => {
      sawProgress = true;
      if (fakeStop) { fakeStop(); fakeStop = null; }
      clearTimeout(fallbackTimer);
      if (e.lengthComputable) {
        const percent = (e.loaded / e.total) * 100;
        bar.style.width = Math.min(100, percent) + '%';
      }
    };

    xhr.onload = () => {
      clearTimeout(fallbackTimer);
      if (fakeStop) { fakeStop(); fakeStop = null; }
      if (xhr.status === 200) {
        bar.style.width = '100%';
        msg.textContent = 'Upload complete!';
        msg.style.color = 'var(--gold)';
        // emit done event for viewer (duplicate is fine)
        emitEvent({ ts: new Date().toISOString(), type: 'put_done', detail: { ip: client_ip, file: file.name, size: file.size }});
      } else {
        msg.textContent = 'Upload failed.';
        msg.style.color = 'var(--love)';
        emitEvent({ ts: new Date().toISOString(), type: 'error', detail: { ip: client_ip, what:'upload_failed', file: file.name }});
      }
      resetBar(900);
    };

    xhr.onerror = () => {
      clearTimeout(fallbackTimer);
      if (fakeStop) { fakeStop(); fakeStop = null; }
      msg.textContent = 'Network error during upload.';
      msg.style.color = 'var(--love)';
      resetBar(900);
    };

    // prepare and send
    const form = new FormData();
    form.append('file', file);
    msg.textContent = 'Uploading…';
    msg.style.color = 'var(--foam)';
    xhr.send(form);
  }
</script>
    </body>
    </html>
    """


@app.route("/log_event", methods=["POST"])
def log_event():
    data = request.get_json(force=True)
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
    return jsonify({"ok": True})


@app.route("/files")
def list_files():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    files = os.listdir(UPLOAD_DIR)
    items = "".join(
        f"<li><a href='/files/{f}' style='color:var(--foam);text-decoration:none;'>{f}</a></li>"
        for f in files
    )
    return f"""
    <!doctype html><html><head>
    <meta charset='utf-8'><title>Files — Network Node</title>
    <style>
      body{{background:#191724;color:#e0def4;font-family:Inter,system-ui,sans-serif;
            padding:80px 40px;}}
      a{{color:#9ccfd8;}}
      ul{{list-style:none;padding:0;}}
    </style></head><body>
    <nav style='position:fixed;top:0;left:0;width:100%;background:#26233a;padding:12px 24px;
                display:flex;justify-content:space-between;align-items:center;
                box-shadow:0 2px 8px rgba(0,0,0,0.4);z-index:50;'>
      <div style='color:#9ccfd8;font-weight:600;'>Network Topology Demo</div>
      <div><a href='/' style='color:#ebbcba;margin-right:18px;text-decoration:none;'>Visualization</a>
           <a href='/upload' style='color:#9ccfd8;text-decoration:none;'>Upload</a></div>
    </nav>
    <h2>Available Files</h2>
    <ul>{items}</ul>
    </body></html>
    """


@app.route("/files/<path:name>")
def serve_file(name):
    return send_from_directory(UPLOAD_DIR, name, as_attachment=True)


if __name__ == "__main__":
    print("Events server running at http://127.0.0.1:5000/")
    app.run(host="0.0.0.0", port=5000, debug=False)
