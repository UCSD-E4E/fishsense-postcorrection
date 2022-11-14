"""Provides color correction facilities
"""
from argparse import ArgumentParser
from pathlib import Path

import cv2 as cv

# pylint: disable=unused-argument
def apply_color_correction(src: cv.Mat, correction_parameters) -> cv.Mat:
    """Applies the specified color correction to the specified image

    Args:
        src (cv.Mat): Input image
        correction_parameters (_type_): Correction parameters

    Returns:
        cv.Mat: Corrected image
    """
    return src

def single_correction():
    """Applies color correction to a single image

    Raises:
        RuntimeError: _description_
        RuntimeError: _description_
    """
    parser = ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('parameter_file')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    parameter_path = Path(args.parameter_file)

    if not input_path.is_file():
        raise RuntimeError("Not a file")

    if not parameter_path.is_file():
        raise RuntimeError("Not a file")

    input_img = cv.imread(input_path.as_posix())
    params = None

    output_img = apply_color_correction(src=input_img, correction_parameters=params)

    cv.imwrite(output_path.as_posix(), output_img)
    