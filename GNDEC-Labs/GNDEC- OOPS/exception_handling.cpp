#include <iostream>
#include <stdexcept>

int main() {
    try {
        int age = 15;
        if (age >= 18) {
            std::cout << "Access granted - you are old enough." << std::endl;
        } else {
            throw (age);
        }
    }
    catch (int myNum) {
        std::cout << "Access denied - You must be at least 18 years old." << std::endl;
        std::cout << "Age is: " << myNum << std::endl;
    }

    try {
        int x = 0;
        if (x == 0) {
            throw "Division by zero condition!";
        }
        int z = 10 / x;
    }
    catch (const char* msg) {
        std::cerr << "Error: " << msg << std::endl;
    }

    try {
        throw std::runtime_error("A runtime error occurred");
    }
    catch (const std::exception& e) {
        std::cerr << "Caught exception: " << e.what() << std::endl;
    }
    catch (...) {
        std::cerr << "Caught an unknown exception" << std::endl;
    }

    return 0;
}
