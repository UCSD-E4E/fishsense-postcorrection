from argparse import ArgumentParser
from pathlib import Path
import cv2 as cv
def applyColorCorrection(src: cv.Mat, correction_parameters) -> cv.Mat:
    return src

def single_correction():
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

    output_img = applyColorCorrection(src=input_img, correction_parameters=params)
    
    cv.imwrite(output_path.as_posix(), output_img)
    