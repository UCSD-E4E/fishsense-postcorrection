from pathlib import Path
import pyrealsense2 as rs
import numpy as np
import cv2 as cv
from tqdm import tqdm

def xy_align(bag_file: Path, output_dir: Path, n_metadata: int = 15):
    pipeline = rs.pipeline()
    config = rs.config()
    
    rs.config.enable_device_from_file(config, bag_file.as_posix())
    config.enable_all_streams()

    profile = pipeline.start(config)
    
    device = profile.get_device()
    playback = device.as_playback()
    playback.set_real_time(False)

    duration = playback.get_duration().total_seconds()

    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    align_to = rs.stream.color
    align = rs.align(align_to)

    
    try:
        with tqdm(total=duration) as pbar:
            while True:
                posCurr = playback.get_position() / 1e9
                pbar.update(posCurr)
                frames = pipeline.wait_for_frames()
                aligned_frames = align.process(frames)

                aligned_depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()

                if aligned_depth_frame:
                    depth_image_counts = np.asanyarray(aligned_depth_frame.get_data())
                    depth_timestamp = aligned_depth_frame.get_timestamp()
                    depth_frame_number = aligned_depth_frame.get_frame_number()
                    depth_image_m = (depth_image_counts * depth_scale).astype(np.float32)
                    fname = output_dir.joinpath(f"{bag_file.stem}_Depth_{depth_timestamp:.9f}.tiff")
                    cv.imwrite(fname.as_posix(), depth_image_m)

                    with open(output_dir.joinpath(f'{bag_file.stem}_Depth_Metadata_{depth_timestamp:.9f}.txt'), 'w') as mtd_file:
                        mtd_file.write(f'Stream: {aligned_depth_frame.get_profile().stream_type().name}\n')

                        for i in range(n_metadata):
                            mtd_val = rs.frame_metadata_value(i)
                            if aligned_depth_frame.supports_frame_metadata(mtd_val):
                                mtd_file.write(f'{mtd_val.name}: {aligned_depth_frame.get_frame_metadata(mtd_val)}\n')
                        
                        mtd_file.write(f'Frame Number: {depth_frame_number}\n')
                
                if color_frame:
                    color_image = np.asanyarray(color_frame.get_data())
                    color_timestamp = color_frame.get_timestamp()
                    color_frame_number = color_frame.get_frame_number()
                    fname = output_dir.joinpath(f"{bag_file.stem}_Color_{color_timestamp:.9f}.png")
                    cv.imwrite(fname.as_posix(), color_image)
                    with open(output_dir.joinpath(f'{bag_file.stem}_Color_Metadata_{color_timestamp:.9f}.txt'), 'w') as mtd_file:
                        mtd_file.write(f'Stream: {aligned_depth_frame.get_profile().stream_type().name}\n')

                        for i in range(n_metadata):
                            mtd_val = rs.frame_metadata_value(i)
                            if aligned_depth_frame.supports_frame_metadata(mtd_val):
                                mtd_file.write(f'{mtd_val.name}: {aligned_depth_frame.get_frame_metadata(mtd_val)}\n')

                        mtd_file.write(f'Frame Number: {color_frame_number}\n')
                
                posNext = playback.get_position() / 1e9
                if posNext < posCurr:
                    break

    finally:
        pipeline.stop()