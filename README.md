# FishSense Post-Correction Utility
This utility provides the tools to apply affine corrections to a RealSense bag file

# Overall process
1. Identify temporal areas of interest.
2. Extract the component streams from the ROSBAG (RGB video, depth video, sensor transforms)
    1. Execute `C:\Program Files (x86)\Intel RealSense SDK 2.0\tools\rs-convert.exe -c -d -i ${rosbag} -p ${png_prefix}`
3. Apply color correction
4. Label the RGB video
5. Match the RGB video with depth data
6. Extract corrected labels

# Dependencies
| Name | Version | URL |
|---|---|---|
| Intel RealSense SDK | v2.51.1 | https://github.com/IntelRealSense/librealsense/releases/tag/v2.51.1 |
| Python 3 | 3.9.13 | https://www.python.org/downloads/release/python-3913/ |

# File formats
## Temporal Areas of Interest
This file will be a text file denoting temporal areas of interest, one per line.

Temporal areas of interest shall be defined by a start and end time, referenced to the start of the clip.

For instance, if we want to work on the clip 160.bag, the file shall be named 160.bag.times.txt

If we want to denote the ranges 13:11.012-15:11.016, 17:12.561-19:32.781, we would put the following in the file:

```
00:13:11.012-00:15:11.016
00:17:12.561-00:19:32.781
```

Formally, the timestamps shall be in hh:mm:ss.sss.  If possible, comply with ISO 8601 timestamp formats and include as much precision as possible.
## Color Correction
