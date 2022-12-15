'''Post Correction code
'''
import datetime as dt
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pyrealsense2 as rs
import yaml


def process_frame(*args):
    """Frame process placeholder
    """
    return args

def main():
    """Main function

    """
    parser = ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('--params', default='correction_params.yaml')

    args = parser.parse_args()
    input_file = Path(args.input)
    if not input_file.exists():
        raise RuntimeError("Input path not found")
    if not input_file.is_file():
        raise RuntimeError("Not a file")
    if args.output is None:
        output_file = input_file.with_name(input_file.stem + '_corrected' + input_file.suffix)
    else:
        output_file = Path(args.output)

    correction_parameter_file = Path(args.params)

    with open(correction_parameter_file, 'r', encoding='ascii') as handle:
        data = yaml.safe_load(handle)

    depth_matrix = np.array(data['depth_matrix'])

    frame_idx = 0
    pipeline = rs.pipeline()
    config = rs.config()
    rs.config.enable_device_from_file(config, input_file.as_posix())
    config.enable_all_streams()
    pipeline.start(config)

    __start_time = dt.datetime.now()
    try:
        while True:
            frame = pipeline.wait_for_frames()
            if frame_idx % 100 == 0:
                print(f'Got frame {frame_idx}')
            frame_idx += 1
            process_frame(frame, depth_matrix, output_file)
    except Exception:  # pylint: disable=broad-except
        pipeline.stop()
    __end_time = dt.datetime.now()
    total_time = (__end_time - __start_time).total_seconds()
    print(f"Processed {frame_idx} frames in {total_time:.2f} "
        f"seconds at {frame_idx / total_time} fps")

if __name__ == '__main__':
    main()
