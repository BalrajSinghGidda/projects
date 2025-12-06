#!/usr/bin/env python3
# events_server.py
# Run: python3 events_server.py
# Streams events.log via SSE on /events, and serves a simple viewer at /.

from flask import Flask, Response, stream_with_context, send_from_directory
import time
import os

EVENTS_FILE = "events.log"
app = Flask(__name__, static_folder=".")


def tail_file(path):
    """Generator that yields existing lines then waits for new ones."""
    # wait until file exists
    while not os.path.exists(path):
        time.sleep(0.1)
    with open(path, "r") as f:
        # send existing content first
        for line in f:
            yield line
        # now tail for new lines
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(0.1)


@app.route("/events")
def sse_events():
    def generator():
        for line in tail_file(EVENTS_FILE):
            # SSE format: data: <payload>\n\n
            # We send the raw JSON line as data
            yield f"data: {line.strip()}\n\n"

    return Response(stream_with_context(generator()), mimetype="text/event-stream")


@app.route("/")
def viewer():
    return send_from_directory(".", "viewer.html")


if __name__ == "__main__":
    print("Starting events_server on http://127.0.0.1:5000/")
    app.run(host="127.0.0.1", port=5000, threaded=True)
