cmake_minimum_required(VERSION 3.4...3.18)
project(fishsense_postcorrection_cpp)
add_subdirectory(extern/pybind11)

find_package( OpenCV REQUIRED )
include_directories( ${OpenCV_INCLUDE_DIRS} )

pybind11_add_module(fishsense_postcorrection_cpp
    src/align.cpp
    )

target_link_libraries(fishsense_postcorrection_cpp
    PUBLIC
        realsense2
        ${OpenCV_LIBS}
    )

