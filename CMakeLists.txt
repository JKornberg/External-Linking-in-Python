cmake_minimum_required(VERSION 3.16)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project("_c_xorcipher")
set(SOURCE_FILES xorcipher.cpp)

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
