from pathlib import Path
from typing import List
from argparse import ArgumentParser
from e4e.detection_code.detect_function import detect

def find_fish(folder: Path) -> List[Path]:
    all_images = folder.glob('*.png')
    list =detect(all_images,0.3,0.45)
    file = open(FLAGS.output + image_name + ".txt", "+w")
    for i in list:
        file.write(i)
        file.write("\n")
    raise NotImplementedError

def fishfinder_main():
    parser = ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('output_file')
    
    args = parser.parse_args()
    input_path = Path(args.input_path)
    output_file = Path(args.output_file)
    if not input_path.exists():
        raise RuntimeError()
    if not input_path.is_dir():
        raise RuntimeError()
    
    fish_images = find_fish(folder=input_path)
    with open(output_file, 'w') as f:
        for img in fish_images:
            f.write(f'{img.relative_to(input_path).as_posix()}\n')

if __name__ == '__main__':
    fishfinder_main()