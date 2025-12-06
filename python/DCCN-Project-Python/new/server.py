#!/usr/bin/env python3
"""
Simple launcher to run both events-server and auth-signaling concurrently for local dev.

Usage:
    python3 server.py
"""

import subprocess
import sys
import time
import os
import signal

PROCS = []


def start(proc_cmd, env=None):
    print("Starting:", " ".join(proc_cmd))
    p = subprocess.Popen(
        proc_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, text=True
    )
    PROCS.append((proc_cmd, p))
    return p


def stream_output(p):
    # non-blocking-ish tail of subprocess output
    try:
        for line in p.stdout:
            print(line.rstrip())
    except Exception:
        pass


if __name__ == "__main__":
    root = os.path.dirname(__file__) or "."
    python = sys.executable

    # Launch events-server (port 5000)
    p1 = start([python, os.path.join(root, "events-server.py")])

    # Launch auth-signaling (port 6000)
    p2 = start([python, os.path.join(root, "auth-signaling.py")])

    try:
        # simple loop to pump output and check processes
        while True:
            for cmd, p in PROCS:
                if p.poll() is not None:
                    print(f"Process {' '.join(cmd)} exited with code {p.returncode}")
                else:
                    # flush a bit of its stdout (non-blocking stream)
                    try:
                        while True:
                            line = p.stdout.readline()
                            if not line:
                                break
                            print(line.rstrip())
                    except Exception:
                        pass
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Shutting down child processes...")
        for _, p in PROCS:
            try:
                p.send_signal(signal.SIGINT)
            except Exception:
                try:
                    p.terminate()
                except Exception:
                    pass
        time.sleep(0.5)
        print("Bye.")
