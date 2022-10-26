from argparse import ArgumentParser
from pathlib import Path
from platform import system
import subprocess


def main():
    parser = ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output_directory')
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_directory)

    if not input_path.is_file():
        raise RuntimeError("Not a file")
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    if not output_dir.is_dir():
        raise RuntimeError("Not a directory")
    
    output_path = output_dir.joinpath(input_path.stem)

    extract_rgb(input_path, output_path)
    extract_depth(input_path, output_path)

def extract_depth(input_path: Path, output_path: Path):
    if system() == 'Windows':
        rs_convert = Path("C:\\Program Files (x86)\Intel RealSense SDK 2.0\\tools\\rs-convert.exe")
    elif system() == 'Linux':
        rs_convert = Path('/usr/bin/rs-convert')
    else:
        raise NotImplementedError("Unknown rs-convert location")
    subprocess.run([rs_convert.as_posix(), '-d', '-i', input_path.as_posix(), '-r', output_path.as_posix()])

def extract_rgb(input_path: Path, output_path: Path):
    if system() == 'Windows':
        rs_convert = Path("C:\\Program Files (x86)\Intel RealSense SDK 2.0\\tools\\rs-convert.exe")
    elif system() == 'Linux':
        rs_convert = Path('/usr/bin/rs-convert')
    else:
        raise NotImplementedError("Unknown rs-convert location")

    subprocess.run([rs_convert.as_posix(), '-c', '-i', input_path.as_posix(), '-p', output_path.as_posix()])

if __name__ == '__main__':
    main()