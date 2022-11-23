""" Provides timerange support
"""
import datetime as dt
from pathlib import Path
from typing import List, Tuple

def read_timeranges(fname: Path) -> List[Tuple[dt.timedelta, dt.timedelta]]:
    """Reads a list of time ranges from file

    The file shall have timestamps as hh:mm:ss.sss to denote time ranges.  Two
    timestamps per range, denoting start and end, reference to t=0.  Timestamps
    shall be separated by `-`, one range per line.

    For example, the following denotes 2 time ranges.
    ```
    01:23:45.678-12:34:56.789
    23:45:67.890-34:56:78.901
    ```


    Args:
        fname (Path): File Path

    Returns:
        List[Tuple[timedelta, timedelta]]: List of time ranges
    """
    origin = dt.datetime(1900, 1, 1)
    time_ranges: List[Tuple[dt.timedelta, dt.timedelta]] = []
    with open(fname, 'r', encoding='utf-8') as handle:
        for line in handle:
            if line == '':
                continue
            parts = line.strip().split('-')
            if len(parts) != 2:
                raise RuntimeError("Missing parts")
            start = dt.datetime.strptime(parts[0] + '000', '%H:%M:%S.%f') - origin
            end = dt.datetime.strptime(parts[1] + '000', '%H:%M:%S.%f') - origin
            time_ranges.append((start, end))
    return time_ranges


def in_timeranges(timestamp: float, time_ranges: List[Tuple[dt.timedelta, dt.timedelta]]) -> bool:
    """Evaluates whether the specified time is in the specified range

    Args:
        t (float): time
        ranges (List[Tuple[dt.timedelta, dt.timedelta]]): timerange

    Returns:
        bool: True if time is in timerange, otherwise false
    """
    tranges = [(trange[0].total_seconds(), trange[1].total_seconds()) for trange in time_ranges]
    for time_range in tranges:
        if time_range[0] < timestamp < time_range[1]:
            return True
    return False
