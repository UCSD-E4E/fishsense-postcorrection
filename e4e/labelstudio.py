"""Provides infrastructure to interact with Label Studio outputs
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


@dataclass
class Point:
    """Label Studio Point label
    """
    loc_x: float
    loc_y: float

@dataclass
class Rectangle:
    """Label Studio Rectangle label

    Raises:
        NotImplementedError: If compared against anything other Point

    Returns:
        _type_: _description_
    """
    loc_x: float
    loc_y: float
    width: float
    height: float
    rotation: float

    def __contains__(self, other: Any):
        if isinstance(other, Point):
            point = np.array([other.loc_x, other.loc_y])
            point -= np.array([self.loc_x, self.loc_y])
            rotation = np.deg2rad(self.rotation)
            r_mat = np.array([[np.cos(rotation), np.sin(rotation)],
                [-np.sin(rotation), np.cos(rotation)]])
            point = np.matmul(r_mat, point)
            if np.abs(point[0]) <= self.width / 2. and np.abs(point[1]) <= self.height / 2.:
                return True
            else:
                return False
        else:
            raise NotImplementedError

@dataclass
class FishAnnotation:
    """Label Studio Fish Complete Annotation
    """
    head: Point
    tail: Point
    image: Path

def extract_fish_annotations(export_path: Path, data_root: Path) -> List[FishAnnotation]:
    """Extracts a list of complete fish annotations

    Args:
        export_path (Path): Label Studio exported file
        data_root (Path): Data root directory

    Raises:
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_

    Returns:
        List[FishAnnotation]: List of completed fish
    """
    annotations: List[FishAnnotation] = []
    with open(export_path, 'r', encoding='utf8') as label_file:
        data: List[Dict] = json.load(label_file)
    for file_info in data:
        for annotation in file_info['annotations']:
            assert isinstance(annotation, dict)
            if len(annotation['result']) == 0:
                continue
            else:
                rectangles: List[Rectangle] = []
                head_points: List[Point] = []
                tail_points: List[Point] = []
                # have data
                for entry in annotation['result']:
                    if entry['type'] == 'rectanglelabels':
                        rectangles.append(Rectangle(
                            loc_x=entry['value']['x'],
                            loc_y=entry['value']['y'],
                            width=entry['value']['width'],
                            height=entry['value']['height'],
                            rotation=entry['value']['rotation']
                        ))
                    elif entry['type'] == 'keypointlabels':
                        if len(entry['value']['keypointlabels']) != 1:
                            raise NotImplementedError
                        if entry['value']['keypointlabels'][0] == 'Nose':
                            head_points.append(Point(
                                loc_x=entry['value']['x'],
                                loc_y=entry['value']['y']
                            ))
                        elif entry['value']['keypointlabels'][0] == 'Tail':
                            tail_points.append(Point(
                                loc_x=entry['value']['x'],
                                loc_y=entry['value']['y']
                            ))
                        else:
                            raise NotImplementedError
                    else:
                        raise NotImplementedError
                for fish_label in rectangles:
                    head_points_in_fish= [pt for pt in head_points if pt in fish_label]
                    tail_points_in_fish= [pt for pt in tail_points if pt in fish_label]
                    if len(head_points_in_fish) != 1 or len(tail_points_in_fish) != 1:
                        continue
                    annotations.append(FishAnnotation(
                        head=head_points_in_fish[0],
                        tail=tail_points_in_fish[0],
                        image=Path(file_info['data']['img']).relative_to(data_root)
                    ))
    return annotations


if __name__ == '__main__':
    output = extract_fish_annotations(
        Path("project-20-at-2022-11-12-22-36-9505164f.json"),
        Path('\\', 'data', 'local-files', '?d=fishsense_nas'))
    print(output)
