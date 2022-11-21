#include <chrono>

#include <pybind11/pybind11.h>
#include <librealsense2/rs.hpp>
#include <opencv2/opencv.hpp>

namespace py = pybind11;

void xy_auto_align(std::string bag_file, std::string output_dir, int n_metadata)
{
    uint64_t pos_prev_ns = 0, pos_curr_ns = 0;
    rs2::pipeline pipeline;
    rs2::config config;

    config.enable_device_from_file(bag_file);
    config.enable_all_streams();

    rs2::pipeline_profile profile = pipeline.start(config);

    rs2::device device = profile.get_device();
    rs2::playback playback = device.as<rs2::playback>();
    playback.set_real_time(false);

    std::chrono::nanoseconds duration = playback.get_duration();

    rs2::depth_sensor depth_sensor = device.first<rs2::depth_sensor>();
    float depth_scale = depth_sensor.get_depth_scale();

    rs2::align align = rs2::align(RS2_STREAM_COLOR);


    while (true)
    {
        rs2::frameset frames = pipeline.wait_for_frames();
        pos_curr_ns = playback.get_position();
        if(pos_curr_ns < pos_prev_ns)
        {
            break;
        }

        rs2::frameset aligned_frames = align.process(frames);

        rs2::depth_frame aligned_depth_frame = aligned_frames.get_depth_frame();
        rs2::video_frame color_frame = aligned_frames.get_color_frame();

        if(aligned_depth_frame)
        {
            const void* p_data = aligned_depth_frame.get_data();
        }
    }
    
}

PYBIND11_MODULE(fishsense_postcorrection_cpp, m)
{
    m.def("xy_auto_align", &xy_auto_align,
    R"(xy_auto_align(
    Extracts aligned RGB and Depth stills from the specified ROSBAG files

    Args:
        bag_file (str): ROSBAG path
        output_dir (str): Output directory for still frames and metadata
        n_metadata (int): Number of metadata items to write)",
    py::arg("bag_file"),
    py::arg("output_dir"),
    py::arg("n_metadata"));
}