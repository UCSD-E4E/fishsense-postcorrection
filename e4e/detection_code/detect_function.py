import os
from pathlib import Path
from typing import List

import cv2
import numpy as np
import tensorflow as tf
from absl.flags import FLAGS
from PIL import Image
from tensorflow.compat.v1 import ConfigProto, InteractiveSession
from tensorflow.python.saved_model import tag_constants

import e4e.detection_code.core.utils as utils
from e4e.detection_code.core.functions import *
from e4e.detection_code.core.yolov4 import filter_boxes

def detect(iou: float, score: float, images: List[Path]) -> List[Path]:
    #taking in input from given weights and input folders
    list_fishes: List[Path] = []
    #saved_model_loaded = tf.saved_model.load("C:\\Users\\ragha\Desktop\\fishsense-postcorrection\\e4e\detection_code\\checkpoints\\yolov4-416\\", tags=[tag_constants.SERVING])
    saved_model_loaded = tf.saved_model.load("./yolov4-416", tags=[tag_constants.SERVING])
    for input_file in images:
        #The current weights are designed for 416 x 416 images, so preprocssing, recoloring and One-hot encoding
        original_image = cv2.imread(input_file.as_posix())
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        image_data = cv2.resize(original_image, (416, 416))
        image_data = image_data / 255.

        #image data is saved 
        images_data = []
        images_data.append(image_data)
        images_data = np.asarray(images_data).astype(np.float32)


        infer = saved_model_loaded.signatures['serving_default']
        batch_data = tf.constant(images_data)
        pred_bbox = infer(batch_data)
        for key, value in pred_bbox.items():
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

        class_names = utils.read_class_names(cfg.YOLO.CLASSES)
        input_classes = list(class_names.values())

        counted_things = (count_objects(pred_bbox, by_class=True, allowed_classes=input_classes))
        if('Fish' in counted_things and counted_things['Fish'] != 0):
            list_fishes.append(input_file)
            print("Finished evaluating: "+str(input_file)+ " which had "+str(counted_things['Fish'])+ " fishes")
        else:
            print("Finished evaluating: "+str(input_file)+ " which had 0 fishes")
    return list_fishes