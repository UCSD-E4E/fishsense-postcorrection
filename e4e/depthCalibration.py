from pathlib import Path
from tkinter.filedialog import askdirectory
from typing import Dict, List, Tuple

import numpy as np
import yaml
from skimage import transform
from tqdm import tqdm


def computeAlignmentParameters(depth_points: List[np.ndarray], rgb_points: List[np.ndarray]):
    depth = np.array(depth_points)
    rgb = np.array(rgb_points)

    tf: transform.AffineTransform = transform.estimate_transform('affine', rgb, depth)
    return tf.params

def main():
    data_path = Path(askdirectory(title="Select run directory"))
    calibration_file_path = data_path.joinpath('calibration_data.yml')
    if not calibration_file_path.exists():
        raise RuntimeError("Calibration file not found")
    
    with open(calibration_file_path) as f:
        data: Dict[str, Dict[str, List[Tuple[float, float]]]] = yaml.safe_load(f)

    depth_points: List[np.ndarray] = []
    rgb_points: List[np.ndarray] = []

    for frame, frame_data in tqdm(data.items()):
        frame_depth_points = frame_data['depth']
        frame_rgb_points = frame_data['rgb']
        if len(frame_depth_points) != len(frame_rgb_points):
            continue
        depth_points.extend([np.array(l) for l in frame_depth_points])
        rgb_points.extend([np.array(l) for l in frame_rgb_points])

    print(computeAlignmentParameters(depth_points=depth_points, rgb_points=rgb_points))

if __name__ == '__main__':
    main()