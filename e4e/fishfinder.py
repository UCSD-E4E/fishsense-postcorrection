"""Fish Finding utility
"""
from argparse import ArgumentParser
from getpass import getpass
from pathlib import Path
from typing import List

import tensorflow as tf
from smb_unzip.smb_unzip import smb_unzip

from e4e.detection_code.detect_function import detect


def find_fish(folder: Path) -> List[Path]:
    """Returns a list of images that most likely have fish in them

    Args:
        folder (Path): Directory to find fish in

    Returns:
        List[Path]: List of png files most likely containing fish
    """
    all_images = folder.glob('*.png')
    return detect(
        images=all_images,
        iou=0.3,
        score=0.45)

def fishfinder_main():
    """Top Level function for fishfinder

    Raises:
        RuntimeError: Input Path is not a directory/does not exist
    """
    parser = ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('output_file')

    args = parser.parse_args()
    input_path = Path(args.input_path)
    output_file = Path(args.output_file)
    if not input_path.is_dir():
        raise RuntimeError()

    fishfinder_loadweights()

    fish_images = find_fish(folder=input_path)

    with open(output_file, 'w', encoding='ascii') as f:
        for img in fish_images:
            f.write(f'{img.relative_to(input_path).as_posix()}\n')

def fishfinder_loadweights(
        model_path: Path = Path('yolov4-416'),
        network_path: str = 'smb://e4e-nas.ucsd.edu/fishsense/yolov4-416.zip'):
    """Loads the weights from the NAS into the specified path

    Args:
        path (Path, optional): model weights path. Defaults to Path('yolov4-416').
    """
    try:
        tf.saved_model.load(model_path.as_posix())
        return
    except OSError:
        username = input("E4E NAS Username: ")
        password = getpass()
        smb_unzip(
            network_path=network_path,
            output_path=model_path.parent,
            username=username,
            password=password
        )

if __name__ == '__main__':
    fishfinder_main()
