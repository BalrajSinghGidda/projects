// mini_server_events_mt.cpp
// Multi-threaded POSIX TCP server that logs NDJSON events to events.log
// and maintains a small state map written to state.json.
// Compile:
//   g++ -std=c++17 mini_server_events_mt.cpp -o mini_server_events_mt -pthread
// Run:
//   ./mini_server_events_mt

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <chrono>
#include <csignal>
#include <ctime>
#include <fcntl.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>
#include <unordered_map>

volatile std::sig_atomic_t running = 1;
void handle_sigint(int) { running = 0; }

// global synchronization for logs + state
std::mutex global_mtx;
std::unordered_map<std::string, std::string> state_map; // ip -> status

std::string iso_timestamp() {
    using namespace std::chrono;
    auto now = system_clock::now();
    std::time_t t = system_clock::to_time_t(now);
    auto ms = duration_cast<milliseconds>(now.time_since_epoch()) % 1000;
    std::ostringstream ss;
    std::tm tm;
    gmtime_r(&t, &tm);
    ss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%S");
    ss << '.' << std::setw(3) << std::setfill('0') << ms.count() << "Z";
    return ss.str();
}

void atomic_write_file(const std::string& path, const std::string& content) {
    std::string tmp = path + ".tmp";
    std::ofstream ofs(tmp, std::ios::trunc);
    if (!ofs.is_open()) return;
    ofs << content;
    ofs.flush();
    ofs.close();
    rename(tmp.c_str(), path.c_str());
}

void emit_event_locked(const std::string& type, const std::string& detail_json) {
    // caller must hold global_mtx
    std::ofstream ofs("events.log", std::ios::app);
    if (!ofs.is_open()) return;
    std::string ts = iso_timestamp();
    ofs << "{\"ts\":\"" << ts << "\",\"type\":\"" << type << "\",\"detail\":" << detail_json << "}\n";
    ofs.close();
}

void update_state_and_write(const std::string& ip, const std::string& status) {
    std::lock_guard<std::mutex> lk(global_mtx);
    state_map[ip] = status;
    // produce a simple state.json: { "nodes": [ {"ip":"x","state":"y"}, ... ] }
    std::ostringstream ss;
    ss << "{\"nodes\":[";
    bool first = true;
    for (auto &p : state_map) {
        if (!first) ss << ",";
        ss << "{\"ip\":\"" << p.first << "\",\"state\":\"" << p.second << "\"}";
        first = false;
    }
    ss << "]}\n";
    atomic_write_file("state.json", ss.str());
}

// thread-safe wrapper for emitting events
void emit_event(const std::string& type, const std::string& detail_json) {
    std::lock_guard<std::mutex> lk(global_mtx);
    emit_event_locked(type, detail_json);
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

void handle_client(int client_fd, std::string ip) {
    // emit connected
    emit_event("client_connected", "{\"ip\":\"" + ip + "\"}");
    update_state_and_write(ip, "connected");

    std::string buffer;
    char c;
    while (true) {
        ssize_t n = recv(client_fd, &c, 1, 0);
        if (n <= 0) break;
        if (c == '\r') continue;
        if (c == '\n') {
            std::string cmd = buffer;
            buffer.clear();
            // very similar handling as before:
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
            } else if (cmd.rfind("PUT ", 0) == 0) {
                std::istringstream iss(cmd);
                std::string tag, filename;
                size_t size = 0;
                iss >> tag >> filename >> size;
                if (filename.empty() || size == 0) {
                    std::string err = "500 PUT usage: PUT <filename> <size>\r\n";
                    send_all(client_fd, err.c_str(), err.size());
                    emit_event("error", "{\"ip\":\"" + ip + "\",\"what\":\"bad_put_cmd\"}");
                    update_state_and_write(ip, "error");
                } else {
                    emit_event("put_start", "{\"ip\":\"" + ip + "\",\"file\":\"" + filename + "\",\"size\":" + std::to_string(size) + "}");
                    update_state_and_write(ip, "transferring");
                    std::string ok = "150 Ready to receive\r\n"; send_all(client_fd, ok.c_str(), ok.size());

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
                        std::string done = "226 Transfer complete\r\n"; send_all(client_fd, done.c_str(), done.size());
                        emit_event("put_done", "{\"ip\":\"" + ip + "\",\"file\":\"" + filename + "\",\"size\":" + std::to_string(size) + "}");
                        update_state_and_write(ip, "connected");
                    } else {
                        std::string done = "426 Connection closed; transfer incomplete\r\n"; send_all(client_fd, done.c_str(), done.size());
                        emit_event("error", "{\"ip\":\"" + ip + "\",\"what\":\"put_incomplete\",\"file\":\"" + filename + "\"}");
                        update_state_and_write(ip, "error");
                    }
                }
            } else if (cmd.rfind("GET ", 0) == 0) {
                std::istringstream iss(cmd);
                std::string tag, filename;
                iss >> tag >> filename;
                std::ifstream ifs(filename, std::ios::binary | std::ios::ate);
                if (!ifs.is_open()) {
                    std::string err = "550 File not found\r\n";
                    send_all(client_fd, err.c_str(), err.size());
                    emit_event("error", "{\"ip\":\"" + ip + "\",\"what\":\"get_not_found\",\"file\":\"" + filename + "\"}");
                    update_state_and_write(ip, "error");
                } else {
                    std::streamsize fsize = ifs.tellg();
                    ifs.seekg(0, std::ios::beg);
                    emit_event("get_start", "{\"ip\":\"" + ip + "\",\"file\":\"" + filename + "\",\"size\":" + std::to_string((size_t)fsize) + "}");
                    update_state_and_write(ip, "transferring");

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
                    update_state_and_write(ip, "connected");
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

    // cleanup
    emit_event("client_disconnected", "{\"ip\":\"" + ip + "\"}");
    update_state_and_write(ip, "idle");
    close(client_fd);
    std::cerr << "Client handler exiting for " << ip << "\n";
}

int main() {
    std::signal(SIGINT, handle_sigint);
    const int port = 2121;
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) { std::cerr << "socket() failed\n"; return 1; }
    int opt = 1; setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    sockaddr_in addr{};
    addr.sin_family = AF_INET; addr.sin_addr.s_addr = INADDR_ANY; addr.sin_port = htons(port);
    if (bind(listen_fd, (sockaddr*)&addr, sizeof(addr)) < 0) { std::cerr << "bind() failed\n"; close(listen_fd); return 1; }
    if (listen(listen_fd, 16) < 0) { std::cerr << "listen() failed\n"; close(listen_fd); return 1; }

    std::cout << "Multi-threaded mini server listening on port " << port << "\n";

    // seed server state (the central server node)
    {
        std::lock_guard<std::mutex> lk(global_mtx);
        state_map["SERVER"] = "running";
        // write initial state
        std::ostringstream ss; ss << "{\"nodes\":[{\"ip\":\"SERVER\",\"state\":\"running\"}]}\n"; atomic_write_file("state.json", ss.str());
    }

    while (running) {
        sockaddr_in client_addr{}; socklen_t client_len = sizeof(client_addr);
        int client_fd = accept(listen_fd, (sockaddr*)&client_addr, &client_len);
        if (client_fd < 0) {
            if (errno == EINTR) break;
            std::cerr << "accept() failed\n"; continue;
        }
        char ipstr[INET_ADDRSTRLEN]; inet_ntop(AF_INET, &client_addr.sin_addr, ipstr, sizeof(ipstr));
        std::string ip = ipstr;
        std::cerr << "Accepted connection from " << ip << "\n";

        // set socket non-blocking optional — keep blocking for now
        std::thread t([client_fd, ip]() {
            handle_client(client_fd, ip);
        });
        t.detach();
    }

    close(listen_fd);
    std::cout << "Server exiting\n";
    return 0;
}

