'''FishFinder Multi Runner
'''
from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import IntEnum, auto
from pathlib import Path
from typing import Dict, List
import appdirs
import yaml

from e4e.fishfinder import find_fish, fishfinder_loadweights


class JobStatus(IntEnum):
    """Job Statuses
    """
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class Job:
    """Job Descriptor
    """
    path: Path
    output: Path
    status: JobStatus = JobStatus.PENDING

    @classmethod
    def from_dict(cls, obj) -> Job:
        """Loads from dictionary

        Args:
            obj (Any): Object to load from

        Raises:
            TypeError: Bad object

        Returns:
            Job: Job
        """
        if not isinstance(obj, dict):
            raise TypeError()
        path = Path(obj['path'])
        output = Path(obj['output'])
        status = JobStatus(obj['status'])
        return Job(
            path=path,
            output=output,
            status=status
        )

    def to_dict(self) -> Dict[str, str]:
        """Outputs to dictionary

        Returns:
            Dict[str, str]: Dictionary of data
        """
        return {
            'path': self.path.as_posix(),
            'output': self.output.as_posix(),
            'status': self.status.value,
        }

    def process(self) -> None:
        """Executes this job
        """
        fish_images = find_fish(folder=self.path)
        with open(self.output, 'w', encoding='ascii') as handle:
            for img in fish_images:
                handle.write(f'{img.relative_to(self.path).as_posix()}\n')

def main():
    """Multi Runner logic
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', type=Path)

    args = parser.parse_args()

    source_data_dir: Path = args.data_dir

    data_name = source_data_dir.name

    local_data_dir = Path(appdirs.user_data_dir('fishfinder_runner'))
    local_data_dir.mkdir(parents=True, exist_ok=True)
    db_name = local_data_dir.joinpath(data_name + '.yaml')

    jobs = load_jobs(db_name)

    label_dirs = source_data_dir.glob('*_label')
    for run in label_dirs:
        job = Job(
            path=run,
            output=run.joinpath('fishimages.txt')
        )
        if run not in jobs:
            jobs[run] = job

    write_jobs(db_name, jobs)

    fishfinder_loadweights()
    process_jobs(jobs, db_name)

def process_jobs(jobs: Dict[Path, Job], db_name: Path) -> None:
    """Processes all jobs

    Args:
        jobs (Dict[Path, Job]): Dictionary of jobs
        db_name (Path): Path to database to keep updated
    """
    for job in jobs.values():
        if job.status == JobStatus.COMPLETED:
            continue
        try:
            job.status = JobStatus.IN_PROGRESS
            job.process()
            job.status = JobStatus.COMPLETED
        except Exception: # pylint: disable=broad-except
            job.status = JobStatus.FAILED
        finally:
            write_jobs(db_name, jobs)

def load_jobs(db_name: Path) -> Dict[Path, Job]:
    """Loads all jobs from the database

    Args:
        db_name (Path): Path to database

    Returns:
        Dict[Path, Job]: Job map
    """
    if db_name.is_file():
        with open(db_name, 'r', encoding='ascii') as handle:
            job_objs: List[Dict[str, str]] = yaml.safe_load(handle)
        job_temp = [Job.from_dict(obj) for obj in job_objs]
        jobs = {job.path:job for job in job_temp}
    else:
        jobs = {}
    return jobs

def write_jobs(db_name: Path, jobs: Dict[Path, Job]):
    """Writes the job map to the database

    Args:
        db_name (Path): Path to database
        jobs (Dict[Path, Job]): Job map
    """
    with open(db_name, 'w', encoding='ascii') as handle:
        data_to_write = [job.to_dict() for job in jobs.values()]
        yaml.safe_dump(data_to_write, handle)

if __name__ == '__main__':
    main()
