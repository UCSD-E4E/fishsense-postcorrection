cmake_minimum_required(VERSION 3.4...3.18)
project(fishsense_postcorrection)
add_subdirectory(extern/pybind11)

pybind11_add_module(fishsense_postcorrection
    src/align.cpp
    )

target_link_libraries(fishsense_postcorrection
    PUBLIC
        realsense
    )

