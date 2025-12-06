// mini_server_posix_fileio.cpp
// POSIX TCP server with minimal FTP-like PUT/GET support.
// Compile:
//   g++ -std=c++17 mini_server_posix_fileio.cpp -o mini_server_posix
// Run:
//   ./mini_server_posix
//
// Protocol (text commands ended by \n):
//   HELLO <name>        -> 200 WELCOME <name>
//   LIST                -> 150 ... 226
//   PUT <filename> <n>  -> server: 150 Ready to receive, then receive n raw bytes
//                         -> 226 Transfer complete (or 426 on incomplete)
//   GET <filename>      -> server: SIZE <n>\r\n then n raw bytes then 226 ...
//   QUIT                -> 221 Goodbye
//
// Test with the provided Python client below (recommended).

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <cerrno>
#include <csignal>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

volatile std::sig_atomic_t running = 1;
void handle_sigint(int) { running = 0; }

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
        std::cerr << "socket() failed: " << std::strerror(errno) << "\n";
        return 1;
    }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(listen_fd, (sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "bind() failed: " << std::strerror(errno) << "\n";
        close(listen_fd);
        return 1;
    }

    if (listen(listen_fd, 5) < 0) {
        std::cerr << "listen() failed: " << std::strerror(errno) << "\n";
        close(listen_fd);
        return 1;
    }

    std::cout << "Mini server (POSIX) listening on port " << port << " — Ctrl+C to stop\n";

    while (running) {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept(listen_fd, (sockaddr*)&client_addr, &client_len);
        if (client_fd < 0) {
            if (errno == EINTR) break;
            std::cerr << "accept() failed: " << std::strerror(errno) << "\n";
            continue;
        }

        char ipstr[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, ipstr, sizeof(ipstr));
        std::cout << "Client connected: " << ipstr << "\n";

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
                    std::string reply = "150 Here comes the directory listing\r\n";
                    // simple static listing; replace with dir read if you want
                    reply += "file1.txt\r\nfile2.png\r\n226 Transfer complete\r\n";
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
                    } else {
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
                        std::string done = (remaining==0) ? "226 Transfer complete\r\n" : "426 Connection closed; transfer incomplete\r\n";
                        send_all(client_fd, done.c_str(), done.size());
                        std::cerr << (remaining==0 ? "PUT done\n" : "PUT incomplete\n");
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
                    } else {
                        std::streamsize fsize = ifs.tellg();
                        ifs.seekg(0, std::ios::beg);
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
                        std::cerr << "GET done\n";
                    }
                } else {
                    std::string reply = "500 Unknown command\r\n";
                    send_all(client_fd, reply.c_str(), reply.size());
                }
            } else {
                buffer.push_back(c);
            }
        }

        std::cout << "Client disconnected\n";
        close(client_fd);
    }

    close(listen_fd);
    std::cout << "Server stopped\n";
    return 0;
}

