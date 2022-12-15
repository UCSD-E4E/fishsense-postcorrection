"""Visual alignment tool
"""
from pathlib import Path
from random import shuffle
from tkinter.filedialog import askdirectory
from typing import Any, Dict, List, Tuple

import cv2 as cv
import matplotlib.pyplot as plt
import yaml
from matplotlib.backend_bases import PickEvent
from tqdm import tqdm


class Aligner:
    """Alignment tool
    """
    # pylint: disable=too-many-instance-attributes,too-few-public-methods
    def __init__(self, rgb: cv.Mat, depth: cv.Mat):
        self.__rgb = rgb
        self.__depth = depth
        self.__depth_points: List[Tuple[float, float]] = []
        self.__rgb_points: List[Tuple[float, float]] = []
        self.__ax1 = None
        self.__ax2 = None
        self.__rgb_artist = None
        self.__depth_artist = None

    def __inner_picker(self, event: PickEvent):
        loc_x = float(event.mouseevent.xdata)
        loc_y = float(event.mouseevent.ydata)
        if event.artist is self.__rgb_artist:
            self.__rgb_points.append((loc_x, loc_y))
            self.__ax1.scatter(loc_x, loc_y)
        if event.artist is self.__depth_artist:
            self.__depth_points.append((loc_x, loc_y))
            self.__ax2.scatter(loc_x, loc_y)
        plt.draw()



    def run(self) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """Main body

        Returns:
            Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]: RGB and Depth points
        """
        fig = plt.figure()
        self.__ax1 = fig.add_subplot(121)
        self.__ax2 = fig.add_subplot(122)
        self.__rgb_artist = self.__ax1.imshow(self.__rgb, picker=True)
        self.__depth_artist = self.__ax2.imshow(self.__depth, picker=True)
        fig.canvas.mpl_connect('pick_event', self.__inner_picker)

        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.state('zoomed')
        plt.ioff()
        plt.show()
        while len(self.__rgb_points) != len(self.__depth_points):
            plt.show()
        return self.__rgb_points, self.__depth_points


def visual_align_run():
    """Main tool body
    """
    # pylint: disable=too-many-locals
    rgb_points: List[Tuple[float, float]] = []
    depth_points: List[Tuple[float, float]] = []

    run_path = Path(askdirectory())
    frame_dirs = list(run_path.glob('frame_*'))

    frame_data_path = run_path.joinpath('calibration_data.yml')

    frame_data: Dict[str, Any] = {}
    if frame_data_path.exists():
        with open(frame_data_path, 'r', encoding='utf-8') as handle:
            previous = yaml.safe_load(handle)
            if previous is not None:
                frame_data.update(previous)

    shuffle(frame_dirs)
    n_points = 0
    for data in frame_data.values():
        n_points += len(data['rgb'])

    with tqdm(total=100, initial=n_points) as pbar:
        for frame_dir in frame_dirs:
            if frame_dir.as_posix() in frame_data:
                continue
            rgb_paths = list(frame_dir.glob('*.png'))
            depth_paths = list(frame_dir.glob('*.tiff'))
            if len(rgb_paths) != 1:
                continue
            if len(depth_paths) != 1:
                continue

            rgb_img = cv.imread(rgb_paths[0].as_posix())
            depth_img = cv.imread(depth_paths[0].as_posix(), -1)

            points = Aligner(rgb_img, depth_img).run()
            rgb_points.extend(points[0])
            depth_points.extend(points[1])
            pbar.update(len(points[0]))

            data = {
                'rgb': points[0],
                'depth': points[1]
            }
            frame_data[frame_dir.as_posix()] = data
            with open(frame_data_path, 'w', encoding='utf-8') as handle:
                yaml.safe_dump(frame_data, handle)

if __name__ == '__main__':
    visual_align_run()
