from argparse import ArgumentParser
from pathlib import Path
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

    subprocess.run(['rs-convert', '-c', '-d', '-i', input_path.as_posix(), '-p', output_path.as_posix()])

if __name__ == '__main__':
    main()