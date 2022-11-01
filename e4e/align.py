from datetime import timedelta
from pathlib import Path
from shutil import copy, move
from typing import Dict, List, Tuple
import cv2 as cv
import numpy as np
import pyrealsense2 as rs
from tqdm import tqdm

from e4e.timeranges import in_timeranges


def xy_align(bag_file: Path, output_dir: Path, n_metadata: int = 5):
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

    posPrev = 0
    
    try:
        with tqdm(total=duration) as pbar:
            while True:
                frames = pipeline.wait_for_frames()
                posCurr = playback.get_position() / 1e9
                if posCurr < posPrev:
                    break

                aligned_frames = align.process(frames)

                aligned_depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()

                if aligned_depth_frame:
                    depth_image_counts = np.asanyarray(aligned_depth_frame.get_data())
                    depth_timestamp_s = aligned_depth_frame.get_timestamp() / 1e3
                    depth_frame_number = aligned_depth_frame.get_frame_number()
                    depth_image_m = (depth_image_counts * depth_scale).astype(np.float32)
                    stream_name = aligned_depth_frame.get_profile().stream_type().name
                    fname = output_dir.joinpath(f"{bag_file.stem}_Depth_t{depth_timestamp_s:.9f}.tiff")
                    mtd_fname = output_dir.joinpath(f'{bag_file.stem}_Depth_Metadata_t{depth_timestamp_s:.9f}.txt')

                    metadata = {
                        "Stream": stream_name,
                        'frame_number': depth_frame_number,
                        'frame_timestamp': depth_timestamp_s
                    }

                    for i in range(n_metadata):
                        mtd_val = rs.frame_metadata_value(i)
                        if aligned_depth_frame.supports_frame_metadata(mtd_val):
                            metadata[mtd_val.name] = aligned_depth_frame.get_frame_metadata(mtd_val)
                    write_data(depth_image_m, fname, mtd_fname, metadata)
                
                if color_frame:
                    color_image = np.asanyarray(color_frame.get_data())
                    color_timestamp_s = color_frame.get_timestamp() / 1e3
                    color_frame_number = color_frame.get_frame_number()
                    stream_name = color_frame.get_profile().stream_type().name
                    fname = output_dir.joinpath(f"{bag_file.stem}_Color_t{color_timestamp_s:.9f}.png")
                    mtd_fname = output_dir.joinpath(f'{bag_file.stem}_Color_Metadata_t{color_timestamp_s:.9f}.txt')

                    metadata = {
                        "Stream": stream_name,
                        'frame_number': color_frame_number,
                        'frame_timestamp': color_timestamp_s
                    }

                    for i in range(n_metadata):
                        mtd_val = rs.frame_metadata_value(i)
                        if color_frame.supports_frame_metadata(mtd_val):
                            metadata[mtd_val.name] = color_frame.get_frame_metadata(mtd_val)
                    write_data(color_image, fname, mtd_fname, metadata)
                
                pbar.update(posCurr - posPrev)
                posPrev = posCurr

    finally:
        pipeline.stop()

def write_data(depth_image_m, img_fname, mtd_fname, metadata):
    cv.imwrite(img_fname.as_posix(), depth_image_m)

    with open(mtd_fname, 'w') as mtd_file:
        for k, v in metadata.items():
            mtd_file.write(f'{k}: {v}\n')

    
def t_align(input_dir: Path, output_dir: Path, label_dir: Path, max_permissible_difference_s: float = 0.1):
    color_frame_t: Dict[float, Path] = {}
    for color_frame in tqdm(input_dir.glob('*_Color_t[0-9.]*')):
        fname = color_frame.stem
        t = float(fname[fname.find('_t') + 2:])
        color_frame_t[t] = color_frame
    
    color_times = np.array(list(color_frame_t.keys()))

    depth_frame_t: Dict[float, Path] = {}
    for depth_frame in tqdm(input_dir.glob('*_Depth_t[0-9.]*')):
        fname = depth_frame.stem
        t = float(fname[fname.find('_t') + 2:])
        depth_frame_t[t] = depth_frame

    for idx, depth_time in tqdm(enumerate(depth_frame_t)):
        deltas = np.abs(color_times - depth_time)
        min_time_idx = np.argmin(deltas)
        if deltas[min_time_idx] >= max_permissible_difference_s:
            continue
        color_time = color_times[min_time_idx]


        depth_files = input_dir.glob(f"*Depth*_t{depth_time:.9f}*")
        color_files = input_dir.glob(f"*Color*_t{color_time:.9f}*")

        frame_folder = output_dir.joinpath(f'frame_{idx:06d}')
        frame_folder.mkdir(exist_ok=True, parents=True)

        for depth_file in depth_files:
            move(depth_file, frame_folder.joinpath(depth_file.name))
        for color_file in color_files:
            if color_file.suffix.endswith('png'):
                copy(color_file, label_dir.joinpath(color_file.name))
            move(color_file, frame_folder.joinpath(color_file.name))