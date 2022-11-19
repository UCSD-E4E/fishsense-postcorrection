import math
import os
# comment out below line to enable tensorflow outputs
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
from absl import app, flags, logging
from absl.flags import FLAGS
import core.utils as utils
from core.yolov4 import filter_boxes
from core.functions import *
from tensorflow.python.saved_model import tag_constants
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

def detect(iou,score,images):
    list_fishes = []
    config = ConfigProto()
    config.gpu_options.allow_growth = True
    saved_model_loaded = tf.saved_model.load("./checkpoints/yolov4-416", tags=[tag_constants.SERVING])
    for file in images:
            original_image = cv2.imread(file)
            original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

            image_data = cv2.resize(original_image, (416, 416))
            image_data = image_data / 255.

            # get image name by using split method
            image_name = file.split('/')[-1]
            image_name = file.split('.')[0]

            images_data = []
            for i in range(1):
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

            # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, xmax, ymax
            original_h, original_w, _ = original_image.shape
            bboxes = utils.format_boxes(boxes.numpy()[0], original_h, original_w)

            ##############################################################################################

            ##############################################################################################

            # hold all detection data in one variable
            pred_bbox = [bboxes, scores.numpy()[0], classes.numpy()[0], valid_detections.numpy()[0]]

            # read in all class names from config
            class_names = utils.read_class_names(cfg.YOLO.CLASSES)

            # by default allow all classes in .names file
            allowed_classes = list(class_names.values())

            # custom allowed classes (uncomment line below to allow detections for only people)
            # allowed_classes = ['person']

            counted_things = (count_objects(pred_bbox, by_class=True, allowed_classes=['Fish']))
            classesfound = []
            for i in range(len(class_names)):
                classesfound.append(class_names[i])
            fishes = []
            if ('Fish' in counted_things):
                fishes_found = counted_things['Fish']

                for i in range(fishes_found):
                    fishes.append([bboxes[i][0], bboxes[i][1], bboxes[i][2], bboxes[i][3]])

            # if crop flag is enabled, crop each detection and save it as new image

            # if count flag is enabled, perform counting of objects
            image = utils.draw_bbox(original_image, pred_bbox, False, allowed_classes=allowed_classes,
                                        show_label=True, read_plate=False)

            image = Image.fromarray(image.astype(np.uint8))

            image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
            list_fishes.append(image_name)

    return list_fishes