#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    std::cout << "===================================" << std::endl;
    std::cout << "  C++ Demo Application" << std::endl;
    std::cout << "  Version: 1.0.0" << std::endl;
    std::cout << "===================================" << std::endl;
    std::cout << std::endl;
    
    if (argc > 1) {
        std::string arg = argv[1];
        if (arg == "--version" || arg == "-v") {
            std::cout << "Version: 1.0.0" << std::endl;
            return 0;
        }
        if (arg == "--help" || arg == "-h") {
            std::cout << "Usage: cpp_demo [options]" << std::endl;
            std::cout << "Options:" << std::endl;
            std::cout << "  -v, --version    Show version" << std::endl;
            std::cout << "  -h, --help       Show this help message" << std::endl;
            return 0;
        }
    }
    
    std::cout << "Hello from C++ Demo!" << std::endl;
    std::cout << "This is a simple C++ application for testing Release App." << std::endl;
    std::cout << std::endl;
    
    return 0;
}
