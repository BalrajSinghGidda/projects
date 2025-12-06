// mini_server.cpp
// Simple TCP server using Boost.Asio
// Compile: g++ -std=c++17 mini_server.cpp -o mini_server -lboost_system -lpthread

#include <boost/asio.hpp>
#include <iostream>
#include <string>

using boost::asio::ip::tcp;

int main() {
    try {
        boost::asio::io_context io_context;

        const unsigned short port = 2121; // demo ftp-like port (not real FTP)
        tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), port));

        std::cout << "Mini server listening on port " << port << "...\n";

        while (true) {
            tcp::socket socket(io_context);
            acceptor.accept(socket);
            std::cout << "Client connected: " << socket.remote_endpoint().address().to_string() << "\n";

            boost::asio::streambuf buf;
            boost::system::error_code ec;

            // Simple loop: read lines and respond
            while (boost::asio::read_until(socket, buf, '\n', ec)) {
                std::istream is(&buf);
                std::string line;
                std::getline(is, line);
                if (!line.empty() && line.back() == '\r') line.pop_back();

                std::cout << "[REQ] " << line << "\n";

                // Very small command handler
                if (line == "QUIT") {
                    std::string reply = "221 Goodbye\r\n";
                    boost::asio::write(socket, boost::asio::buffer(reply), ec);
                    break;
                } else if (line.rfind("HELLO", 0) == 0) {
                    // HELLO name
                    std::string name = line.size() > 6 ? line.substr(6) : "guest";
                    std::string reply = "200 WELCOME " + name + "\r\n";
                    boost::asio::write(socket, boost::asio::buffer(reply), ec);
                } else if (line == "LIST") {
                    // Simple fake listing
                    std::string reply = "150 Here comes the directory listing\r\nfile1.txt\r\nfile2.png\r\n226 Transfer complete\r\n";
                    boost::asio::write(socket, boost::asio::buffer(reply), ec);
                } else {
                    std::string reply = "500 Unknown command\r\n";
                    boost::asio::write(socket, boost::asio::buffer(reply), ec);
                }

                if (ec) {
                    std::cerr << "Write error: " << ec.message() << "\n";
                    break;
                }
            }

            if (ec && ec != boost::asio::error::eof) {
                std::cerr << "Connection error: " << ec.message() << "\n";
            }
            std::cout << "Client disconnected\n\n";
        }
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
    }

    return 0;
}

