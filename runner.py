"""Extracts all data for labeling
"""
import os
from argparse import ArgumentParser
from pathlib import Path
from queue import Queue
from shutil import copy
from threading import Thread
from typing import Dict, List, Tuple

import yaml

from e4e.align import t_align, xy_auto_align


class Job:
    """Job Class - contains job definition and progress tracking
    """

    def __init__(self,
            bag_file: Path,
            data_root: Path,
            target_root: Path,
            cache_path: Path) -> None:
        self.__bag_file = bag_file.resolve()
        self.__data_root = data_root.resolve()
        self.__target_root = target_root.resolve()
        self.__cache_path = cache_path.resolve()

    @property
    def bag_path(self) -> Path:
        """Absolute bag file path

        Returns:
            Path: Absolute bag file path
        """
        return self.__bag_file

    @property
    def bag_file(self) -> Path:
        """Bag File Path relative to the deployment root

        Returns:
            Path: Relative path of bag file
        """
        return self.__bag_file.relative_to(self.__data_root)

    @property
    def output_folder(self) -> Path:
        """Directory in which paired RGB and depth frames will go

        Returns:
            Path: Paired frame folder
        """
        return self.__target_root.joinpath('_'.join(self.bag_file.with_suffix('').parts))

    @property
    def label_dir(self) -> Path:
        """Directory in which RGB stills for labeling will go

        Returns:
            Path: Label folder
        """
        return self.__target_root.joinpath('_'.join(self.bag_file.with_suffix('').parts) + '_label')

    @property
    def tmp_path(self) -> Path:
        """Cached path of bag file

        Returns:
            Path: cached bag file path
        """
        return self.__cache_path.joinpath(self.reference_name)

    @property
    def reference_name(self) -> str:
        """Returns the single part reference name for the job

        Returns:
            str: Reference string
        """
        return '_'.join(self.bag_file.parts)

def copy_thread_fn(jobs: List[Job], job_queue: "Queue[Job]"):
    """Copy Thread

    Args:
        bag_files (List[Path]): List of ROSBAG files
        tmp_paths (List[Path]): List of temporary paths to place the ROSBAGS
        tmp_path_queue (Queue[Path]): Queue to enqueue ready ROSBAGS
    """
    for job in jobs:
        if job.tmp_path.exists():
            if job.tmp_path.stat().st_size != job.bag_path.stat().st_size:
                copy(job.bag_path, job.tmp_path)
        else:
            copy(job.bag_path, job.tmp_path)
        job_queue.put(job)
        print(f'Copied {job.bag_path} to {job.tmp_path}')

def process_thread_fn(
        job_queue: "Queue[Job]",
        progress_path: Path,
        file_progress: Dict[str, Dict],
        num_jobs: int,
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
    for _ in enumerate(range(num_jobs)):
        job = job_queue.get()
        print(job.bag_file.as_posix())

        try:
            xy_auto_align(
                bag_file=job.tmp_path,
                output_dir=job.output_folder,
                ignore_errors=bypass_xy_align_errors
            )
            t_align(
                output_dir=job.output_folder,
                input_dir=job.output_folder,
                label_dir=job.label_dir
            )
            file_progress[job.reference_name] = {
                'status': True
            }
        except Exception as exc: # pylint: disable=broad-except
            file_progress[job.reference_name] = {
                'status': False,
                'error': str(exc)
            }
        finally:
            with open(progress_path, 'w', encoding='utf-8') as handle:
                yaml.safe_dump(file_progress, handle)
            os.remove(job.tmp_path)

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
    parser = ArgumentParser()
    parser.add_argument('--input_path')
    parser.add_argument('--output_path')
    parser.add_argument('--progress_db')
    parser.add_argument('--cache_path')
    parser.add_argument('--bypass_xy_align_errors', action='store_true')

    args = parser.parse_args()
    # deployment_root_path = Path(
    #     '/home/ntlhui/google_drive/Test Data/2022-05 Reef Deployment/usa_florida')
    # target_path = Path('/home/ntlhui/fishsense/nas/data/2022-05 Reef Deployment outputs')
    # progress_path = Path('/home/ntlhui/fishsense/progress.yaml')
    # fast_storage = Path('/home/ntlhui/fishsense/fast/fishsense')
    # bypass_xy_align_errors = True

    deployment_root_path = Path(args.input_path)
    progress_path = Path(args.progress_db)
    fast_storage = Path(args.cache_path)


    bag_files = sorted(list(deployment_root_path.glob('**/*.bag')), key=lambda x: x.stat().st_size)
    progress_path.touch(exist_ok=True)
    file_progress = {}
    with open(progress_path, 'r', encoding='utf-8') as handle:
        recorded = yaml.safe_load(handle)
        if recorded:
            file_progress.update(recorded)
    all_jobs: List[Job] = [Job(bag_file=bag_file,
        data_root=deployment_root_path,
        target_root=Path(args.output_path),
        cache_path=fast_storage) for bag_file in bag_files]

    jobs = [job for job in all_jobs if job.reference_name not in file_progress]
    fast_storage.mkdir(parents=True, exist_ok=True)

    job_queue: "Queue[Job]" = Queue(maxsize=4)

    copy_thread = Thread(target=copy_thread_fn,
        kwargs={
            'jobs': jobs,
            'job_queue': job_queue})
    process_thread = Thread(target=process_thread_fn,
        kwargs={
            'job_queue': job_queue,
            'progress_path': progress_path,
            'file_progress': file_progress,
            'num_jobs': len(jobs),
            'bypass_xy_align_errors': args.bypass_xy_align_errors})
    copy_thread.start()
    process_thread.start()

    process_thread.join()
    copy_thread.join()

if __name__ == '__main__':
    run()
