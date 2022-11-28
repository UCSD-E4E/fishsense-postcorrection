"""Provides spatial and temporal alignment routines for Intel RealSense ROSBAG files
"""
from pathlib import Path
from shutil import copy, move
from typing import Dict

import cv2 as cv
import numpy as np
import pyrealsense2 as rs
from tqdm import tqdm


def xy_auto_align(
        bag_file: Path,
        output_dir: Path,
        n_metadata: int = 5,
        ignore_errors: bool = False):
    """Extracts aligned RGB and Depth stills from the specified ROSBAG files

    Args:
        bag_file (Path): ROSBAG path
        output_dir (Path): Output directory for still frames and metadata
        n_metadata (int, optional): Number of metadata items to write. Defaults to 5.
    """
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

    pos_prev = 0

    try:
        with tqdm(total=duration) as pbar:
            while True:
                try:
                    frames = pipeline.wait_for_frames()
                    pos_curr = playback.get_position() / 1e9
                    if pos_curr < pos_prev:
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
                        depth_img_path = f"{bag_file.stem}_Depth_t{depth_timestamp_s:.9f}.tiff"
                        fname = output_dir.joinpath(depth_img_path)
                        depth_metadata_path = (f'{bag_file.stem}_'
                            f'Depth_Metadata_t{depth_timestamp_s:.9f}.txt')
                        mtd_fname = output_dir.joinpath(depth_metadata_path)

                        metadata = {
                            "Stream": stream_name,
                            'frame_number': depth_frame_number,
                            'frame_timestamp': depth_timestamp_s
                        }

                        for i in range(n_metadata):
                            mtd_val = rs.frame_metadata_value(i)
                            if aligned_depth_frame.supports_frame_metadata(mtd_val):
                                metadata[mtd_val.name] = \
                                    aligned_depth_frame.get_frame_metadata(mtd_val)
                        write_data(depth_image_m, fname, mtd_fname, metadata)

                    if color_frame:
                        color_image = np.asanyarray(color_frame.get_data())
                        color_timestamp_s = color_frame.get_timestamp() / 1e3
                        color_frame_number = color_frame.get_frame_number()
                        stream_name = color_frame.get_profile().stream_type().name
                        img_name = f"{bag_file.stem}_Color_t{color_timestamp_s:.9f}.png"
                        fname = output_dir.joinpath(img_name)
                        mtd_name = f'{bag_file.stem}_Color_Metadata_t{color_timestamp_s:.9f}.txt'
                        mtd_fname = output_dir.joinpath(mtd_name)

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

                    pbar.update(pos_curr - pos_prev)
                    pos_prev = pos_curr
                except Exception as exc: # pylint: disable=broad-except
                    if not ignore_errors:
                        raise exc

    finally:
        pipeline.stop()

def write_data(depth_image_m, img_fname, mtd_fname, metadata):
    """Writes the RealSense metadata to the specified filename

    Args:
        depth_image_m (_type_): _description_
        img_fname (_type_): _description_
        mtd_fname (_type_): _description_
        metadata (_type_): _description_
    """
    cv.imwrite(img_fname.as_posix(), depth_image_m)

    with open(mtd_fname, 'w', encoding='utf-8') as mtd_file:
        for key, value in metadata.items():
            mtd_file.write(f'{key}: {value}\n')


def t_align(
        input_dir: Path,
        output_dir: Path,
        label_dir: Path,
        max_permissible_difference_s: float = 0.1):
    """Generates temporally aligned RGB and depth frames

    Args:
        input_dir (Path): Directory containing all RGB and Depth frames
        output_dir (Path): Directory in which to place aligned RGB and depth frames
        label_dir (Path): Directory in which to place a copy of RGB frames for labeling
        max_permissible_difference_s (float, optional): Maximum temporal misalignment.
            Defaults to 0.1.
    """
    bag_file_name = ''
    color_frame_t: Dict[float, Path] = {}
    for color_frame in tqdm(input_dir.glob('*_Color_t[0-9.]*')):
        fname = color_frame.stem
        timestamp = float(fname[fname.find('_t') + 2:])
        color_frame_t[timestamp] = color_frame
        bag_file_name = color_frame.name[:color_frame.name.find('_Color_t')]

    color_times = list(color_frame_t.keys())

    depth_frame_t: Dict[float, Path] = {}
    for depth_frame in tqdm(input_dir.glob('*_Depth_t[0-9.]*')):
        fname = depth_frame.stem
        timestamp = float(fname[fname.find('_t') + 2:])
        depth_frame_t[timestamp] = depth_frame

    depth_times = list(depth_frame_t.keys())

    rgb_idx = 0
    depth_idx = 0
    frame_idx = 0
    with tqdm(total=len(depth_times)) as pbar:
        while rgb_idx < len(color_times) and depth_idx < len(depth_times):
            initial_difference_s = color_times[rgb_idx] - depth_times[depth_idx]
            if initial_difference_s < -1 * max_permissible_difference_s:
                rgb_idx += 1
            elif initial_difference_s > max_permissible_difference_s:
                depth_idx += 1
                pbar.update(1)
            else:
                depth_time = depth_times[depth_idx]
                color_time = color_times[rgb_idx]

                depth_files = [
                    input_dir.joinpath(f'{bag_file_name}_Depth_t{depth_time:.9f}.tiff'),
                    input_dir.joinpath(f'{bag_file_name}_Depth_Metadata_t{depth_time:.9f}.txt'),
                ]
                color_files = [
                    input_dir.joinpath(f'{bag_file_name}_Color_t{color_time:.9f}.png'),
                    input_dir.joinpath(f'{bag_file_name}_Color_Metadata_t{color_time:.9f}.txt'),
                ]

                frame_folder = output_dir.joinpath(f'frame_{frame_idx:06d}')
                frame_folder.mkdir(exist_ok=True, parents=True)
                for depth_file in depth_files:
                    move(depth_file, frame_folder.joinpath(depth_file.name))
                for color_file in color_files:
                    if color_file.suffix.endswith('png'):
                        copy(color_file, label_dir.joinpath(color_file.name))
                    move(color_file, frame_folder.joinpath(color_file.name))
                rgb_idx += 1
                depth_idx += 1
                frame_idx += 1
                pbar.update(1)
