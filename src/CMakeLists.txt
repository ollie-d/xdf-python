cmake_minimum_required(VERSION 3.7)
project(pbxdf)
add_subdirectory(pybind11)
pybind11_add_module(pbxdf pbxdf.cpp)
