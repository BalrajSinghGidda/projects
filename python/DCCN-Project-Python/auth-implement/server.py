#!/usr/bin/env python3
import asyncio, json, time, os

EVENT_LOG = "events.log"
STATE_FILE = "state.json"
PORT = 2121
STATE = {}  # ip -> status


def ts():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())


def emit_event(event_type, detail):
    evt = {"ts": ts(), "type": event_type, "detail": detail}
    with open(EVENT_LOG, "a") as f:
        f.write(json.dumps(evt) + "\n")
    update_state(detail.get("ip", ""), event_type)


def update_state(ip, status):
    if not ip:
        return
    STATE[ip] = status
    with open(STATE_FILE, "w") as f:
        json.dump({"nodes": [{"ip": k, "state": v} for k, v in STATE.items()]}, f)


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")[0]
    emit_event("client_connected", {"ip": addr})
    print(f"[+] {addr} connected")

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            cmd = data.decode().strip()
            print(f"{addr} -> {cmd}")
            if cmd == "QUIT":
                writer.write(b"221 Goodbye\r\n")
                await writer.drain()
                break

            elif cmd.startswith("HELLO"):
                writer.write(f"200 WELCOME {addr}\r\n".encode())
                await writer.drain()

            elif cmd == "LIST":
                reply = "150 Here comes the directory listing\r\nfile1.txt\r\nfile2.txt\r\n226 Done\r\n"
                writer.write(reply.encode())
                await writer.drain()

            elif cmd.startswith("PUT"):
                try:
                    _, filename, size = cmd.split()
                    size = int(size)
                except:
                    writer.write(b"500 PUT usage: PUT <filename> <size>\r\n")
                    await writer.drain()
                    continue

                emit_event("put_start", {"ip": addr, "file": filename, "size": size})
                writer.write(b"150 Ready to receive\r\n")
                await writer.drain()
                with open(filename, "wb") as f:
                    remaining = size
                    while remaining > 0:
                        chunk = await reader.read(min(4096, remaining))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)
                if remaining == 0:
                    emit_event("put_done", {"ip": addr, "file": filename, "size": size})
                    writer.write(b"226 Transfer complete\r\n")
                else:
                    emit_event(
                        "error",
                        {"ip": addr, "file": filename, "what": "PUT incomplete"},
                    )
                    writer.write(b"426 Transfer incomplete\r\n")
                await writer.drain()

            elif cmd.startswith("GET"):
                try:
                    _, filename = cmd.split()
                    size = os.path.getsize(filename)
                except:
                    writer.write(b"550 File not found\r\n")
                    await writer.drain()
                    continue

                emit_event("get_start", {"ip": addr, "file": filename, "size": size})
                writer.write(f"SIZE {size}\r\n".encode())
                await writer.drain()
                with open(filename, "rb") as f:
                    while chunk := f.read(4096):
                        writer.write(chunk)
                        await writer.drain()
                emit_event("get_done", {"ip": addr, "file": filename, "size": size})
                writer.write(b"226 Done\r\n")
                await writer.drain()

            else:
                emit_event("error", {"ip": addr, "what": "unknown", "cmd": cmd})
                writer.write(b"500 Unknown command\r\n")
                await writer.drain()

    except Exception as e:
        emit_event("error", {"ip": addr, "what": str(e)})

    emit_event("client_disconnected", {"ip": addr})
    writer.close()
    await writer.wait_closed()
    print(f"[-] {addr} disconnected")


async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", PORT)
    print(f"[FTP] Listening on {PORT}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
