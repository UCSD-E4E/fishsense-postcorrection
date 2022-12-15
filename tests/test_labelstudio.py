"""Label Studio support test module
"""
from pathlib import Path
from typing import Dict, Tuple

from labelstudio_mock_data import create_test_export # pylint: disable=unused-import

from e4e.labelstudio import Point, Rectangle, extract_fish_annotations


def test_extract_annotations(label_studio_export_json: Tuple[Path, Dict, Path]):
    """Tests annotation extraction

    Args:
        label_studio_export_json (Tuple[Path, Dict, Path]): Sample export
    """
    export_path, _, data_root = label_studio_export_json
    output = extract_fish_annotations(
        export_path=export_path,
        data_root=data_root
    )
    assert len(output) == 3

def test_rectangle_contains():
    """Test for point in rotated angle
    """
    rect = Rectangle(0, 0, 1, 1, 0)
    point1 = Point(1, 1)
    assert point1 not in rect

    rect = Rectangle(0, 0, 1, 1, 45)
    point1 = Point(0, 0.707)
    assert point1 in rect

    rect = Rectangle(0, 0, 4, 2, 45)
    point1 = Point(1, 1)
    assert point1 in rect

    rect = Rectangle(2, 2, 4, 2, 45)
    point1 = Point(3, 3)
    assert point1 in rect
