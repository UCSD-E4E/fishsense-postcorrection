'''Label Studio Mock Data
'''
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

@pytest.fixture(name='label_studio_export_json')
def create_test_export():
    """Creates a sample Label Studio JSON export

    Yields:
        Tuple[Path, Dict, Path]: Path to export file, corresponding data, data root path
    """
    data = [
        {
            "id": 109292,
            "annotations": [
                {
                    "id": 7151,
                    "completed_by": 9,
                    "result": [
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 62.65432098765432,
                                "y": 58.13528336380256,
                                "width": 0.205761316872428,
                                "keypointlabels": [
                                    "Nose"
                                ]
                            },
                            "id": "pWJeovDDir",
                            "from_name": "kp-1",
                            "to_name": "img-1",
                            "type": "keypointlabels",
                            "origin": "manual"
                        },
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 55.452674897119344,
                                "y": 63.25411334552103,
                                "width": 0.205761316872428,
                                "keypointlabels": [
                                    "Tail"
                                ]
                            },
                            "id": "IHNVlDZR6J",
                            "from_name": "kp-1",
                            "to_name": "img-1",
                            "type": "keypointlabels",
                            "origin": "manual"
                        },
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 54.11522633744856,
                                "y": 57.76965265082266,
                                "width": 9.876543209876543,
                                "height": 6.39853747714808,
                                "rotation": 0,
                                "rectanglelabels": [
                                    "Fish"
                                ]
                            },
                            "id": "SvaIR0S3yx",
                            "from_name": "labels",
                            "to_name": "img-1",
                            "type": "rectanglelabels",
                            "origin": "manual"
                        },
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 58.1275720164609,
                                "y": 49.177330895795244,
                                "width": 0.205761316872428,
                                "keypointlabels": [
                                    "Nose"
                                ]
                            },
                            "id": "ebVMh-DJFy",
                            "from_name": "kp-1",
                            "to_name": "img-1",
                            "type": "keypointlabels",
                            "origin": "manual"
                        },
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 52.674897119341566,
                                "y": 47.34917733089579,
                                "width": 0.205761316872428,
                                "keypointlabels": [
                                    "Tail"
                                ]
                            },
                            "id": "GmvxnGeOXn",
                            "from_name": "kp-1",
                            "to_name": "img-1",
                            "type": "keypointlabels",
                            "origin": "manual"
                        },
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 51.95473251028807,
                                "y": 45.703839122486286,
                                "width": 8.333333333333332,
                                "height": 5.301645338208409,
                                "rotation": 0,
                                "rectanglelabels": [
                                    "Fish"
                                ]
                            },
                            "id": "PT9Q0sb_zV",
                            "from_name": "labels",
                            "to_name": "img-1",
                            "type": "rectanglelabels",
                            "origin": "manual"
                        },
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 48.148148148148145,
                                "y": 61.06032906764168,
                                "width": 0.205761316872428,
                                "keypointlabels": [
                                    "Nose"
                                ]
                            },
                            "id": "yTobXnVp7V",
                            "from_name": "kp-1",
                            "to_name": "img-1",
                            "type": "keypointlabels",
                            "origin": "manual"
                        },
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 54.93827160493827,
                                "y": 56.672760511883,
                                "width": 0.205761316872428,
                                "keypointlabels": [
                                    "Tail"
                                ]
                            },
                            "id": "hQPPOrBTQx",
                            "from_name": "kp-1",
                            "to_name": "img-1",
                            "type": "keypointlabels",
                            "origin": "manual"
                        },
                        {
                            "original_width": 1280,
                            "original_height": 720,
                            "image_rotation": 0,
                            "value": {
                                "x": 47.325102880658434,
                                "y": 54.47897623400365,
                                "width": 8.127572016460908,
                                "height": 7.312614259597806,
                                "rotation": 0,
                                "rectanglelabels": [
                                    "Fish"
                                ]
                            },
                            "id": "m2UARLg4HP",
                            "from_name": "labels",
                            "to_name": "img-1",
                            "type": "rectanglelabels",
                            "origin": "manual"
                        }
                    ],
                    "was_cancelled": False,
                    "ground_truth": False,
                    "created_at": "2022-11-19T04:37:59.107220Z",
                    "updated_at": "2022-11-19T04:37:59.107258Z",
                    "lead_time": 26.681,
                    "prediction": {},
                    "result_count": 0,
                    "task": 109292,
                    "parent_prediction": None,
                    "parent_annotation": None
                }
            ],
            "drafts": [],
            "predictions": [],
            "data": {
                "img": r"\/data\/local-files\/?d=fishsense_nas\/data\/2022-05%20Reef%20Deployment%20outputs\/2022-06-29_Horseshoe%20Reef%20%28deep%29_fs002_530_label\/2022-06-29_Horseshoe%20Reef%20%28deep%29_fs002_530_Color_t1652423630.045211077.png" # pylint: disable=line-too-long
            },
            "meta": {},
            "created_at": "2022-11-08T23:55:54.261166Z",
            "updated_at": "2022-11-19T04:37:59.344524Z",
            "inner_id": 5897,
            "total_annotations": 1,
            "cancelled_annotations": 0,
            "total_predictions": 0,
            "comment_count": 0,
            "unresolved_comment_count": 0,
            "last_comment_updated_at": None,
            "project": 20,
            "updated_by": 9,
            "comment_authors": []
        },
        {
            "id": 108513,
            "annotations": [
                {
                    "id": 7140,
                    "completed_by": 9,
                    "result": [],
                    "was_cancelled": False,
                    "ground_truth": False,
                    "created_at": "2022-11-19T04:37:31.605152Z",
                    "updated_at": "2022-11-19T04:37:31.605184Z",
                    "lead_time": 1.725,
                    "prediction": {},
                    "result_count": 0,
                    "task": 108513,
                    "parent_prediction": None,
                    "parent_annotation": None
                }
            ],
            "drafts": [],
            "predictions": [],
            "data": {
                "img": r"\/data\/local-files\/?d=fishsense_nas\/data\/2022-05%20Reef%20Deployment%20outputs\/2022-06-29_Horseshoe%20Reef%20%28deep%29_fs002_530_label\/2022-06-29_Horseshoe%20Reef%20%28deep%29_fs002_530_Color_t1652423491.113808870.png" # pylint: disable=line-too-long
            },
            "meta": {},
            "created_at": "2022-11-08T23:55:08.163088Z",
            "updated_at": "2022-11-19T04:37:31.808326Z",
            "inner_id": 5118,
            "total_annotations": 1,
            "cancelled_annotations": 0,
            "total_predictions": 0,
            "comment_count": 0,
            "unresolved_comment_count": 0,
            "last_comment_updated_at": None,
            "project": 20,
            "updated_by": 9,
            "comment_authors": []
        },

    ]
    with TemporaryDirectory() as tmp_dir:
        export_path = Path(tmp_dir).joinpath('export.json')
        with open(export_path, 'w', encoding='ascii') as tmp_export:
            tmp_export.write(json.dumps(data, indent=None))
        yield export_path, data, Path(r"\/data\/local-files\/?d=fishsense_nas")
