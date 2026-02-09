cmake_minimum_required(VERSION 3.10)
project(CppDemo VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

add_executable(cpp_demo main.cpp)

install(TARGETS cpp_demo DESTINATION bin)
