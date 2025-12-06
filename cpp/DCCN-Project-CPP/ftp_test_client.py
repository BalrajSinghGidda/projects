#!/usr/bin/env python3
# ftp_test_client.py
# Usage:
#   python3 ftp_test_client.py put <localfile> <remotename>
#   python3 ftp_test_client.py get <remotename> <localfile>
#   python3 ftp_test_client.py hello NAME

import socket
import sys
import os

HOST = "127.0.0.1"
PORT = 2121


def recvline(s):
    data = b""
    while True:
        c = s.recv(1)
        if not c:
            return None
        if c == b"\n":
            break
        if c == b"\r":
            continue
        data += c
    return data.decode()


def cmd_hello(name):
    s = socket.create_connection((HOST, PORT))
    s.sendall(f"HELLO {name}\n".encode())
    print(recvline(s))
    s.sendall(b"QUIT\n")
    s.close()


def cmd_put(local, remote):
    size = os.path.getsize(local)
    s = socket.create_connection((HOST, PORT))
    s.sendall(f"PUT {remote} {size}\n".encode())
    resp = recvline(s)
    print("SERVER:", resp)
    if not resp or not resp.startswith("150"):
        print("server refused to receive")
        s.close()
        return
    with open(local, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            s.sendall(data)
    # read final status lines until we get code-like line
    while True:
        line = recvline(s)
        if line is None:
            break
        print("SERVER:", line)
        if line.startswith("226") or line.startswith("426"):
            break
    s.sendall(b"QUIT\n")
    s.close()


def cmd_get(remote, local):
    s = socket.create_connection((HOST, PORT))
    s.sendall(f"GET {remote}\n".encode())
    line = recvline(s)
    print("SERVER:", line)
    if not line or not line.startswith("SIZE "):
        print("no SIZE header; aborting")
        s.close()
        return
    size = int(line.split()[1])
    remaining = size
    with open(local, "wb") as f:
        while remaining > 0:
            chunk = s.recv(min(4096, remaining))
            if not chunk:
                break
            f.write(chunk)
            remaining -= len(chunk)
    # read trailing status
    while True:
        line = recvline(s)
        if line is None:
            break
        print("SERVER:", line)
        if line.startswith("226") or line.startswith("550"):
            break
    s.sendall(b"QUIT\n")
    s.close()
    if remaining == 0:
        print("GET complete:", local)
    else:
        print("GET incomplete:", remaining, "bytes missing")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: put/get/hello ...")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "put" and len(sys.argv) == 4:
        cmd_put(sys.argv[2], sys.argv[3])
    elif cmd == "get" and len(sys.argv) == 4:
        cmd_get(sys.argv[2], sys.argv[3])
    elif cmd == "hello" and len(sys.argv) == 3:
        cmd_hello(sys.argv[2])
    else:
        print("bad args")
