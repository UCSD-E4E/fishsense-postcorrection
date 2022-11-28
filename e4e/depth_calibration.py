"""Provides facilities to compute the RGB to depth data alignment matrices
"""
from pathlib import Path
from tkinter.filedialog import askdirectory
from typing import Dict, List, Tuple

import numpy as np
import yaml
from skimage import transform
from tqdm import tqdm


def compute_alignment_parameters(
        depth_points: List[np.ndarray],
        rgb_points: List[np.ndarray]) -> np.ndarray:
    """Computes the RGB to depth alignment matrices

    Args:
        depth_points (List[np.ndarray]): List of depth points
        rgb_points (List[np.ndarray]): List of rgb points

    Returns:
        np.ndarray: Transformation matrix
    """
    depth = np.array(depth_points)
    rgb = np.array(rgb_points)

    computed_tf: transform.AffineTransform = transform.estimate_transform('affine', rgb, depth)
    return computed_tf.params

def main():
    """Main tool body

    Raises:
        RuntimeError: _description_
    """
    data_path = Path(askdirectory(title="Select run directory"))
    calibration_file_path = data_path.joinpath('calibration_data.yml')
    if not calibration_file_path.exists():
        raise RuntimeError("Calibration file not found")

    with open(calibration_file_path, encoding='utf-8') as handle:
        data: Dict[str, Dict[str, List[Tuple[float, float]]]] = yaml.safe_load(handle)

    depth_points: List[np.ndarray] = []
    rgb_points: List[np.ndarray] = []

    for _, frame_data in tqdm(data.items()):
        frame_depth_points = frame_data['depth']
        frame_rgb_points = frame_data['rgb']
        if len(frame_depth_points) != len(frame_rgb_points):
            continue
        depth_points.extend([np.array(l) for l in frame_depth_points])
        rgb_points.extend([np.array(l) for l in frame_rgb_points])

    print(compute_alignment_parameters(depth_points=depth_points, rgb_points=rgb_points))

if __name__ == '__main__':
    main()
