// mini_server_events.cpp
// POSIX TCP server with PUT/GET and JSON event logging (NDJSON to events.log)
// Compile: g++ -std=c++17 mini_server_events.cpp -o mini_server_events
// Run: ./mini_server_events
//
// Then run the Python SSE server (next section) to serve events to a browser.

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <chrono>
#include <csignal>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

volatile std::sig_atomic_t running = 1;
void handle_sigint(int) { running = 0; }

std::string iso_timestamp() {
    using namespace std::chrono;
    auto now = system_clock::now();
    std::time_t t = system_clock::to_time_t(now);
    auto ms = duration_cast<milliseconds>(now.time_since_epoch()) % 1000;
    std::ostringstream ss;
    std::tm tm;
    gmtime_r(&t, &tm); // UTC
    ss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%S");
    ss << '.' << std::setw(3) << std::setfill('0') << ms.count() << "Z";
    return ss.str();
}

// Append a JSON object line to events.log
void emit_event(const std::string& type, const std::string& detail_json) {
    std::ofstream ofs("events.log", std::ios::app);
    if (!ofs.is_open()) {
        std::cerr << "Failed to open events.log for writing\n";
        return;
    }
    std::string ts = iso_timestamp();
    // detail_json should already be a JSON object fragment like: {"ip":"1.2.3.4", "file":"x"}
    ofs << "{\"ts\":\"" << ts << "\",\"type\":\"" << type << "\"," << "\"detail\":" << detail_json << "}\n";
    ofs.close();
}

ssize_t send_all(int fd, const char* buf, size_t len) {
    size_t sent = 0;
    while (sent < len) {
        ssize_t n = send(fd, buf + sent, len - sent, 0);
        if (n <= 0) return n;
        sent += n;
    }
    return (ssize_t)sent;
}

int main() {
    std::signal(SIGINT, handle_sigint);

    const int port = 2121;
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        std::cerr << "socket() failed\n";
        return 1;
    }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(listen_fd, (sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "bind() failed\n";
        close(listen_fd);
        return 1;
    }

    if (listen(listen_fd, 5) < 0) {
        std::cerr << "listen() failed\n";
        close(listen_fd);
        return 1;
    }

    std::cout << "Mini server (events) listening on port " << port << " — Ctrl+C to stop\n";

    while (running) {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept(listen_fd, (sockaddr*)&client_addr, &client_len);
        if (client_fd < 0) {
            if (errno == EINTR) break;
            std::cerr << "accept() failed\n";
            continue;
        }

        char ipstr[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, ipstr, sizeof(ipstr));
        std::string ip = ipstr;
        std::cout << "Client connected: " << ip << "\n";

        // Emit connect event
        emit_event("client_connected", "{\"ip\":\"" + ip + "\"}");

        // read line-by-line commands
        std::string buffer;
        while (true) {
            char c;
            ssize_t n = recv(client_fd, &c, 1, 0);
            if (n <= 0) break; // closed or error
            if (c == '\r') continue;
            if (c == '\n') {
                std::string cmd = buffer;
                buffer.clear();
                std::cout << "[REQ] " << cmd << "\n";

                if (cmd == "QUIT") {
                    std::string reply = "221 Goodbye\r\n";
                    send_all(client_fd, reply.c_str(), reply.size());
                    break;
                } else if (cmd.rfind("HELLO", 0) == 0) {
                    std::string name = cmd.size() > 6 ? cmd.substr(6) : "guest";
                    std::string reply = "200 WELCOME " + name + "\r\n";
                    send_all(client_fd, reply.c_str(), reply.size());
                } else if (cmd == "LIST") {
                    std::string reply = "150 Here comes the directory listing\r\nfile1.txt\r\nfile2.png\r\n226 Transfer complete\r\n";
                    send_all(client_fd, reply.c_str(), reply.size());
                }
                // PUT <filename> <size>
                else if (cmd.rfind("PUT ", 0) == 0) {
                    std::istringstream iss(cmd);
                    std::string tag, filename;
                    size_t size = 0;
                    iss >> tag >> filename >> size;
                    if (filename.empty() || size == 0) {
                        std::string err = "500 PUT usage: PUT <filename> <size>\r\n";
                        send_all(client_fd, err.c_str(), err.size());
                        emit_event("error", "{\"ip\":\"" + ip + "\",\"what\":\"bad_put_cmd\"}");
                    } else {
                        emit_event("put_start", "{\"ip\":\"" + ip + "\",\"file\":\"" + filename + "\",\"size\":" + std::to_string(size) + "}");
                        std::string ok = "150 Ready to receive\r\n";
                        send_all(client_fd, ok.c_str(), ok.size());

                        std::ofstream ofs(filename, std::ios::binary);
                        size_t remaining = size;
                        char buf[4096];
                        while (remaining > 0) {
                            ssize_t r = recv(client_fd, buf, (remaining > sizeof(buf) ? sizeof(buf) : remaining), 0);
                            if (r <= 0) break;
                            ofs.write(buf, r);
                            remaining -= r;
                        }
                        ofs.close();
                        if (remaining == 0) {
                            std::string done = "226 Transfer complete\r\n";
                            send_all(client_fd, done.c_str(), done.size());
                            emit_event("put_done", "{\"ip\":\"" + ip + "\",\"file\":\"" + filename + "\",\"size\":" + std::to_string(size) + "}");
                            std::cerr << "PUT done\n";
                        } else {
                            std::string done = "426 Connection closed; transfer incomplete\r\n";
                            send_all(client_fd, done.c_str(), done.size());
                            emit_event("error", "{\"ip\":\"" + ip + "\",\"what\":\"put_incomplete\",\"file\":\"" + filename + "\"}");
                            std::cerr << "PUT incomplete\n";
                        }
                    }
                }
                // GET <filename>
                else if (cmd.rfind("GET ", 0) == 0) {
                    std::istringstream iss(cmd);
                    std::string tag, filename;
                    iss >> tag >> filename;
                    std::ifstream ifs(filename, std::ios::binary | std::ios::ate);
                    if (!ifs.is_open()) {
                        std::string err = "550 File not found\r\n";
                        send_all(client_fd, err.c_str(), err.size());
                        emit_event("error", "{\"ip\":\"" + ip + "\",\"what\":\"get_not_found\",\"file\":\"" + filename + "\"}");
                    } else {
                        std::streamsize fsize = ifs.tellg();
                        ifs.seekg(0, std::ios::beg);

                        emit_event("get_start", "{\"ip\":\"" + ip + "\",\"file\":\"" + filename + "\",\"size\":" + std::to_string((size_t)fsize) + "}");

                        std::string header = "SIZE " + std::to_string((size_t)fsize) + "\r\n";
                        send_all(client_fd, header.c_str(), header.size());

                        char buf[4096];
                        while (ifs.good()) {
                            ifs.read(buf, sizeof(buf));
                            std::streamsize r = ifs.gcount();
                            if (r > 0) {
                                if (send_all(client_fd, buf, (size_t)r) <= 0) break;
                            }
                        }
                        std::string done = "226 Transfer complete\r\n";
                        send_all(client_fd, done.c_str(), done.size());
                        emit_event("get_done", "{\"ip\":\"" + ip + "\",\"file\":\"" + filename + "\",\"size\":" + std::to_string((size_t)fsize) + "}");
                        std::cerr << "GET done\n";
                    }
                } else {
                    std::string reply = "500 Unknown command\r\n";
                    send_all(client_fd, reply.c_str(), reply.size());
                    emit_event("error", "{\"ip\":\"" + ip + "\",\"what\":\"unknown_cmd\",\"cmd\":\"" + cmd + "\"}");
                }
            } else {
                buffer.push_back(c);
            }
        }

        std::cout << "Client disconnected: " << ip << "\n";
        emit_event("client_disconnected", "{\"ip\":\"" + ip + "\"}");
        close(client_fd);
    }

    close(listen_fd);
    std::cout << "Server stopped\n";
    return 0;
}
