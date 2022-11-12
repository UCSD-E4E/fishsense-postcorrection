import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float
    rotation: float

    def __contains__(self, other: Any):
        if isinstance(other, Point):
            point = np.array([other.x, other.y])
            point -= np.array([self.x, self.y])
            rotation = np.deg2rad(self.rotation)
            r_mat = np.array([[np.cos(rotation), np.sin(rotation)], [-np.sin(rotation), np.cos(rotation)]])
            point = np.matmul(r_mat, point)
            if np.abs(point[0]) <= self.width / 2. and np.abs(point[1]) <= self.height / 2.:
                return True
            else:
                return False
        else:
            raise NotImplementedError

@dataclass
class FishAnnotation:
    head: Point
    tail: Point
    image: Path

def extractFishAnnotations(export_path: Path, data_root: Path) -> List[FishAnnotation]:
    annotations: List[FishAnnotation] = []
    with open(export_path) as f:
        data: List[Dict] = json.load(f)
    for file_info in data:
        for annotation in file_info['annotations']:
            assert(isinstance(annotation, dict))
            if len(annotation['result']) == 0:
                continue
            else:
                rectangles: List[Dict] = []
                head_points: List[Dict] = []
                tail_points: List[Dict] = []
                # have data
                for entry in annotation['result']:
                    if entry['type'] == 'rectanglelabels':
                        rectangles.append(entry)
                    elif entry['type'] == 'keypointlabels':
                        if len(entry['value']['keypointlabels']) != 1:
                            raise NotImplementedError
                        if entry['value']['keypointlabels'][0] == 'Nose':
                            head_points.append(entry)
                        elif entry['value']['keypointlabels'][0] == 'Tail':
                            tail_points.append(entry)
                        else:
                            raise NotImplementedError
                    else:
                        raise NotImplementedError
                



if __name__ == '__main__':
    extractFishAnnotations(Path("project-20-at-2022-11-12-22-36-9505164f.json"), Path('data', 'local-files', '?d=fishsense_nas'))
