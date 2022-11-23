"""Extracts all data for labeling
"""
import os
from pathlib import Path
from queue import Queue
from shutil import copy
from threading import Thread
from typing import List, Dict, Tuple

import yaml
from tqdm import tqdm

from e4e.align import t_align, xy_auto_align

def copy_thread_fn(bag_files: List[Path], tmp_paths: List[Path], tmp_path_queue: "Queue[Path]"):
    """Copy Thread

    Args:
        bag_files (List[Path]): List of ROSBAG files
        tmp_paths (List[Path]): List of temporary paths to place the ROSBAGS
        tmp_path_queue (Queue[Path]): Queue to enqueue ready ROSBAGS
    """
    assert len(bag_files) == len(tmp_paths)
    for idx in range(len(bag_files)): # pylint: disable=consider-using-enumerate
        bag_file = bag_files[idx]
        tmp_path = tmp_paths[idx]
        if tmp_path.exists():
            if tmp_path.stat().st_size != bag_file.stat().st_size:
                copy(bag_file, tmp_path)
        else:
            copy(bag_file, tmp_path)
        tmp_path_queue.put(tmp_path)
        print(f"Copied {bag_file} to {tmp_path}")

def process_thread_fn(
        tmp_path_queue: "Queue[Path]",
        output_dirs: List[str],
        label_dirs: List[str],
        target_path: Path,
        progress_path: Path,
        file_progress: Dict[str, Dict],
        bypass_xy_align_errors: bool = False):
    """Processing thread function

    Args:
        tmp_path_queue (Queue[Path]): Queue of paths to process
        output_dirs (List[str]): List of output directories
        label_dirs (List[str]): List of label directories
        target_path (Path): Target paths
        progress_path (Path): Progress file path
        file_progress (Dict[str, Dict]): File progress object
        bypass_xy_align_errors (bool): xy_align error bypass
    """
    for idx, _ in enumerate(output_dirs):
        bag_file = tmp_path_queue.get()
        output_dir = target_path.joinpath(output_dirs[idx])
        label_dir = target_path.joinpath(label_dirs[idx])
        print(bag_file.as_posix())
        try:
            xy_auto_align(
                bag_file=bag_file,
                output_dir=output_dir,
                ignore_errors=bypass_xy_align_errors)
            t_align(output_dir=output_dir, input_dir=output_dir, label_dir=label_dir)
        except Exception as exp: # pylint: disable=broad-except
            file_progress[bag_file.name] = {
                'status': False,
                'error': str(exp)
            }
            with open(progress_path, 'w', encoding='utf-8') as handle:
                yaml.safe_dump(file_progress, handle)
            os.remove(bag_file)
            continue
        print("done")
        file_progress[bag_file.name] = {
            'status': True
        }
        with open(progress_path, 'w', encoding='utf-8') as handle:
            yaml.safe_dump(file_progress, handle)
        os.remove(bag_file)

def t_align_pipelined(input_queue: "Queue[Tuple[Path, Path]]", label_dirs: List[str]):
    """Pipelined version of temporal alignment

    Args:
        input_queue (Queue[Tuple[Path, Path]]): Queue of tuple of output and label directories
        label_dirs (List[str]): List of label directories
    """
    for _ in range(len(label_dirs)):
        output_dir, label_dir = input_queue.get()
        try:
            t_align(output_dir=output_dir, input_dir=output_dir, label_dir=label_dir)
        except Exception as exp: # pylint: disable=broad-except
            print(exp)

def run():
    """Main tool function
    """
    deployment_root_path = Path(
        '/home/ntlhui/google_drive/Test Data/2022-05 Reef Deployment/usa_florida')
    target_path = Path('/home/ntlhui/fishsense/nas/data/2022-05 Reef Deployment outputs')
    progress_path = Path('/home/ntlhui/fishsense/progress.yaml')
    fast_storage = Path('/home/ntlhui/fishsense/fast/fishsense')
    bypass_xy_align_errors = True

    bag_files = sorted(list(deployment_root_path.glob('**/*.bag')), key=lambda x: x.stat().st_size)
    progress_path.touch(exist_ok=True)
    file_progress = {}
    with open(progress_path, 'r', encoding='utf-8') as handle:
        recorded = yaml.safe_load(handle)
        if recorded:
            file_progress.update(recorded)

    bag_files = [f for f in bag_files
        if '_'.join(f.relative_to(deployment_root_path).parts) not in file_progress]

    output_dirs = ['_'.join(bag_file.relative_to(deployment_root_path).with_suffix('').parts)
        for bag_file in bag_files]
    label_dirs = ['_'.join(bag_file.relative_to(deployment_root_path).with_suffix('').parts) \
        + '_label'for bag_file in bag_files]
    tmp_paths = [fast_storage.joinpath('_'.join(bag_file.relative_to(deployment_root_path).parts))
        for bag_file in bag_files]

    for output_dir in tqdm(output_dirs):
        target_path.joinpath(output_dir).mkdir(parents=True, exist_ok=True)
    for label_dir in tqdm(label_dirs):
        target_path.joinpath(label_dir).mkdir(parents=True, exist_ok=True)
    fast_storage.mkdir(parents=True, exist_ok=True)

    tmp_path_queue: "Queue[Path]" = Queue(maxsize=4)

    copy_thread = Thread(target=copy_thread_fn, args=(bag_files, tmp_paths, tmp_path_queue))
    copy_thread.start()
    process_thread_args = {
        'tmp_path_queue': tmp_path_queue,
        'output_dirs': output_dirs,
        'label_dirs': label_dirs,
        'target_path': target_path,
        'progress_path': progress_path,
        'file_progress': file_progress,
        'bypass_xy_align_errors': bypass_xy_align_errors}
    process_thread = Thread(target=process_thread_fn, kwargs=process_thread_args)
    process_thread.start()
    process_thread.join()
    copy_thread.join()

if __name__ == '__main__':
    run()
