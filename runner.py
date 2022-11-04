# %%
from pathlib import Path
from e4e.align import xy_auto_align, t_align
from tqdm import tqdm
import yaml

# %%
deployment_root_path = Path('/home/ntlhui/google_drive/Test Data/2022-05 Reef Deployment/usa_florida')
target_path = Path('/home/ntlhui/fishsense/nas/data/2022-05 Reef Deployment outputs')
progress_path = Path('/home/ntlhui/fishsense/progress.yaml')

# %%
output_dirs = ['_'.join(bag_file.relative_to(deployment_root_path).with_suffix('').parts) for bag_file in deployment_root_path.glob('**/*.bag')]
label_dirs = ['_'.join(bag_file.relative_to(deployment_root_path).with_suffix('').parts) + '_label' for bag_file in deployment_root_path.glob('**/*.bag')]

# %%
for dir in tqdm(output_dirs):
    target_path.joinpath(dir).mkdir(parents=True, exist_ok=True)
for dir in tqdm(label_dirs):
    target_path.joinpath(dir).mkdir(parents=True, exist_ok=True)

# %%
progress_path.touch(exist_ok=True)
file_progress = {}
with open(progress_path, 'r') as f:
    recorded = yaml.safe_load(f)
    if recorded:
        file_progress.update(recorded)
for idx, bag_file in tqdm(enumerate(deployment_root_path.glob('**\\*.bag'))):
    if bag_file.as_posix() in file_progress:
        continue
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


