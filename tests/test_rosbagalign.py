"""Test ROS Align
"""

import e4e.align as dut
from pathlib import Path

def test_xy_align():
    test_file = Path('/mnt/shared_data/270.bag')
    output_path = Path('/tmp/output')
    output_path.mkdir(parents=True, exist_ok=True)
    dut.xy_auto_align(bag_file=test_file, output_dir=output_path)