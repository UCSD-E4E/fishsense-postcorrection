# %%
from pathlib import Path
from queue import Queue
from shutil import copy
from threading import Thread

import yaml
from tqdm import tqdm

from e4e.align import t_align, xy_auto_align

# %%
deployment_root_path = Path('/home/ntlhui/google_drive/Test Data/2022-05 Reef Deployment/usa_florida')
target_path = Path('/home/ntlhui/fishsense/nas/data/2022-05 Reef Deployment outputs')
progress_path = Path('/home/ntlhui/fishsense/progress.yaml')
fast_storage = Path('/home/ntlhui/fishsense/fast/fishsense')

# %%
bag_files = list(deployment_root_path.glob('**/*.bag'))
output_dirs = ['_'.join(bag_file.relative_to(deployment_root_path).with_suffix('').parts) for bag_file in bag_files]
label_dirs = ['_'.join(bag_file.relative_to(deployment_root_path).with_suffix('').parts) + '_label' for bag_file in bag_files]
tmp_paths = [fast_storage.joinpath('_'.join(bag_file.relative_to(deployment_root_path).parts)) for bag_file in bag_files]

# %%
for dir in tqdm(output_dirs):
    target_path.joinpath(dir).mkdir(parents=True, exist_ok=True)
for dir in tqdm(label_dirs):
    target_path.joinpath(dir).mkdir(parents=True, exist_ok=True)
fast_storage.mkdir(parents=True, exist_ok=True)
# %%
progress_path.touch(exist_ok=True)
file_progress = {}
with open(progress_path, 'r') as f:
    recorded = yaml.safe_load(f)
    if recorded:
        file_progress.update(recorded)

bag_files = [f for f in bag_files if f.as_posix() not in file_progress]

tmp_path_queue = Queue()
def copy_thread_fn(bag_files, tmp_paths, tmp_path_queue: Queue):
    assert(len(bag_files) == len(tmp_paths))
    for idx in range(len(bag_files)):
        bag_file = bag_files[idx]
        tmp_path = tmp_paths[idx]
        copy(bag_file, tmp_path)
        tmp_path_queue.put(tmp_path)
        print(f"Copied {bag_file} to {tmp_path}")

def process_thread_fn(tmp_path_queue: Queue, output_dirs, label_dirs):
    for idx in range(len(output_dirs)):
        bag_file = tmp_path_queue.get()
        output_dir = target_path.joinpath(output_dirs[idx])
        label_dir = target_path.joinpath(label_dirs[idx])
        print(bag_file.as_posix())
        try:
            xy_auto_align(bag_file=bag_file, output_dir=output_dir)
            t_align(output_dir=output_dir, input_dir=output_dir, label_dir=label_dir)
        except Exception as e:
            file_progress[bag_file.as_posix()] = {
                'status': False,
                'error': str(e)
            }
            with open(progress_path, 'w') as f:
                yaml.safe_dump(file_progress, f)
            continue
        print("done")
        file_progress[bag_file.as_posix()] = {
            'status': True
        }
        with open(progress_path, 'w') as f:
            yaml.safe_dump(file_progress, f)

copy_thread = Thread(target=copy_thread_fn, args=(bag_files, tmp_paths, tmp_path_queue))
copy_thread.start()
process_thread = Thread(target=process_thread_fn, args=(tmp_path_queue, output_dirs, label_dirs))
process_thread.start()
process_thread.join()
copy_thread.join()