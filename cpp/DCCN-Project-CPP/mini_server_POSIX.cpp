// mini_server_posix.cpp
// Minimal single-threaded TCP server using POSIX sockets
// Compile: g++ -std=c++17 mini_server_posix.cpp -o mini_server_posix
// Run: ./mini_server_posix
// Test: nc 127.0.0.1 2121

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <cerrno>
#include <csignal>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>

volatile std::sig_atomic_t running = 1;
void handle_sigint(int) { running = 0; }

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

        // Read lines from client
        std::string buffer;
        while (true) {
            char c;
            ssize_t n = recv(client_fd, &c, 1, 0);
            if (n <= 0) break; // closed or error
            if (c == '\r') continue;
            if (c == '\n') {
                // handle command in buffer
                std::string cmd = buffer;
                buffer.clear();
                std::cout << "[REQ] " << cmd << "\n";

                std::string reply;
                if (cmd == "QUIT") {
                    reply = "221 Goodbye\r\n";
                    send(client_fd, reply.c_str(), reply.size(), 0);
                    break;
                } else if (cmd.rfind("HELLO", 0) == 0) {
                    std::string name = cmd.size() > 6 ? cmd.substr(6) : "guest";
                    reply = "200 WELCOME " + name + "\r\n";
                } else if (cmd == "LIST") {
                    reply = "150 Here comes the directory listing\r\nfile1.txt\r\nfile2.png\r\n226 Transfer complete\r\n";
                } else {
                    reply = "500 Unknown command\r\n";
                }
                send(client_fd, reply.c_str(), reply.size(), 0);
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

