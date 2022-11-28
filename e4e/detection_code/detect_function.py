from pathlib import Path
from typing import List, Dict

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.python.saved_model import tag_constants
from tqdm import tqdm

import e4e.detection_code.core.utils as utils
from e4e.detection_code.core.config import cfg
from e4e.detection_code.core.functions import count_objects


def detect(iou: float, score: float, images: List[Path]) -> List[Path]:
    """Detects the fish images

    Args:
        iou (float): IoU threshold
        score (float): Score threshold
        images (List[Path]): List of images to process

    Returns:
        List[Path]: List of images that have fish
    """
    #taking in input from given weights and input folders
    list_fishes: List[Path] = []
    saved_model_loaded = tf.saved_model.load("./yolov4-416", tags=[tag_constants.SERVING])
    infer = saved_model_loaded.signatures['serving_default']
    class_names = utils.read_class_names(cfg.YOLO.CLASSES)
    input_classes = list(class_names.values())
    for input_file in tqdm(images):
        # The current weights are designed for 416 x 416 images, so preprocssing, recoloring and
        # One-hot encoding
        original_image = cv2.imread(input_file.as_posix())
        rgb_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        image_data = np.asarray([cv2.resize(rgb_img, (416, 416)) / 255.], dtype=np.float32)

        batch_data = tf.constant(image_data)
        pred_bbox: Dict[str, tf.Tensor] = infer(batch_data)
        for value in pred_bbox.values():
            boxes = value[:, :, 0:4]
            pred_conf = value[:, :, 4:]

        # run non max suppression on detections
        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=iou,
            score_threshold=score
        )

        original_h, original_w, _ = original_image.shape
        bboxes = utils.format_boxes(boxes.numpy()[0], original_h, original_w)
        pred_bbox = [bboxes, scores.numpy()[0], classes.numpy()[0], valid_detections.numpy()[0]]

        counted_things = count_objects(pred_bbox, by_class=True, allowed_classes=input_classes)
        if 'Fish' in counted_things and counted_things['Fish'] != 0:
            list_fishes.append(input_file)

    return list_fishes
