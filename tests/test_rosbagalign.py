"""Test ROS Align
"""

from pathlib import Path

# import e4e.align as dut
import fishsense_postcorrection_cpp as dut


def test_xy_align():
    """XY Alignment Test
    """
    test_file = Path('/mnt/shared_data/270.bag')
    output_path = Path('/tmp/output')
    output_path.mkdir(parents=True, exist_ok=True)
    # dut.xy_auto_align(
    #     bag_file=test_file,
    #     output_dir=output_path,
    #     n_metadata=5)
    dut.xy_auto_align(
        bag_file=test_file.as_posix(),
        output_dir=output_path.as_posix(),
        n_metadata=5)
