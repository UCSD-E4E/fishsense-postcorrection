from pathlib import Path
from random import shuffle
from tkinter.filedialog import askdirectory
from typing import Any, Dict, List, Tuple

import cv2 as cv
import matplotlib.pyplot as plt
import yaml
from matplotlib.backend_bases import PickEvent


class Aligner:
    def __init__(self, rgb: cv.Mat, depth: cv.Mat):
        self.__rgb = rgb
        self.__depth = depth
        self.__depth_points: List[Tuple[float, float]] = []
        self.__rgb_points: List[Tuple[float, float]] = []

    def __inner_picker(self, event: PickEvent):
        x = float(event.mouseevent.xdata)
        y = float(event.mouseevent.ydata)
        if event.artist is self.__rgb_artist:
            self.__rgb_points.append((x, y))
            self.__ax1.scatter(x, y)
        if event.artist is self.__depth_artist:
            self.__depth_points.append((x, y))
            self.__ax2.scatter(x, y)
        plt.draw()
        
        

    def run(self) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        fig = plt.figure()
        self.__ax1 = fig.add_subplot(121)
        self.__ax2 = fig.add_subplot(122)
        self.__rgb_artist = self.__ax1.imshow(self.__rgb, picker=True)
        self.__depth_artist = self.__ax2.imshow(self.__depth, picker=True)
        fig.canvas.mpl_connect('pick_event', self.__inner_picker)

        figManager = plt.get_current_fig_manager()
        figManager.window.state('zoomed')
        plt.ioff()
        plt.show()
        while len(self.__rgb_points) != len(self.__depth_points):
            plt.show()
        return self.__rgb_points, self.__depth_points


def visualAlignRun():
    rgb_points: List[Tuple[float, float]] = []
    depth_points: List[Tuple[float, float]] = []

    run_path = Path(askdirectory())
    frame_dirs = list(run_path.glob('frame_*'))

    frame_data_path = run_path.joinpath('calibration_data.yml')

    frame_data: Dict[str, Any] = {}
    if frame_data_path.exists():
        with open(frame_data_path, 'r') as f:
            previous = yaml.safe_load(f)
            if previous is not None:
                frame_data.update(previous)

    shuffle(frame_dirs)

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

        data = {
            'rgb': points[0],
            'depth': points[1]
        }
        frame_data[frame_dir.as_posix()] = data
        with open(frame_data_path, 'w') as f:
            yaml.safe_dump(frame_data, f)

if __name__ == '__main__':
    visualAlignRun(Aligner)
