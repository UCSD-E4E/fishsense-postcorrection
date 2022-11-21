from setuptools import setup, find_packages

setup(
    name='FishSensePostCorrection',
    version='0.0.0.1',
    author='UCSD Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
    entry_points={
        'console_scripts': [
            'fishsense_postcorrection = e4e.postcorrection:main',
            'fishsense_correctionAnalyze = e4e.analyze:main',
            'fishsense_extract = e4e.extract:main',
            'fishsense_visualalign = e4e.visualAlign:visualAlignRun',
            'fishsense_fishfinder = e4e.fishfinder:fishfinder_main',
        ]
    },
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'numpy',
        'scipy',
        'pyrealsense2',
        'opencv-python',
        'tqdm',
        'matplotlib',
        'pyyaml',
        'scikit-image',
        'lxml',
        'tensorflow',
        'absl-py',
        'easydict',
        'pillow',
        'pytesseract',
        'pysmb',
    ]
)