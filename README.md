# FishSense Post-Correction Utility
This utility provides the tools to apply affine corrections to a RealSense bag file

# Overall process
1. Extract the component streams from the ROSBAG (RGB video, depth video, sensor transforms)
    1. Execute `C:\Program Files (x86)\Intel RealSense SDK 2.0\tools\rs-convert.exe -c -d -i ${rosbag} -p ${png_prefix}`
2. Label the RGB video
3. Match the RGB video with depth data
4. Extract corrected labels

# Dependencies
| Name | Version | URL |
|---|---|---|
| Intel RealSense SDK | v2.51.1 | https://github.com/IntelRealSense/librealsense/releases/tag/v2.51.1 |
| Python 3 | 3.9.13 | https://www.python.org/downloads/release/python-3913/ |
