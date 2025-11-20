#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
import copy
import argparse
import itertools
from collections import deque

import cv2 as cv
import numpy as np
from PIL import Image
import mediapipe as mp

from utils import CvFpsCalc
from keypoint_classifier import KeyPointClassifier

DESKTOP_MODE = True
DESKTOP_DIMENSIONS = (960, 540)
MOBILE_DIMENSIONS = (720, 1080)

OFFSET = 0  # Label offset for dataset expansion

# Load classification labels ###########################################################
keypoint_classifier_labels = []
with open('model/dataset/label.csv', encoding='utf-8-sig') as f:
    # keypoint_classifier_labels = csv.reader(f) PREVIOUS
    reader = csv.reader(f)

    # Added to comment out thumbs up/down (Our model only takes 3 gestures right now not 5 so we got to update that)
    for row in reader:
        # Skip empty lines
        if not row:
            continue

        label = row[0].strip()

        # Skip comments (# anything)
        if label.startswith("#"):
            continue

        keypoint_classifier_labels.append(label)
    # keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels] PREVIOUS
# keypoint_classifier_labels = ["placeholder"]

# Load model ###########################################################################
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
NUM_CLASSES = len(keypoint_classifier_labels)
keypoint_classifier = KeyPointClassifier(NUM_CLASSES)


# =============== PROCESS IMAGE ==========================================================
def process_image(image, training_mode=False, debug_mode=True, number=None, mode=None):
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands_detector.process(image)
    image.flags.writeable = True

    hand_sign_label = None
    handedness_label = None

    debug_image = copy.deepcopy(image)

    if results.multi_hand_landmarks is not None:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                              results.multi_handedness):

            brect = calc_bounding_rect(debug_image, hand_landmarks)
            handedness_label = handedness.classification[0].label
            landmark_list = calc_landmark_list(debug_image, hand_landmarks, handedness_label)


            # preprocess (normalize)
            pre_processed_landmark_list = pre_process_landmark(landmark_list)

            # write to CSV only when training_mode == True
            if training_mode:
                logging_csv(number, pre_processed_landmark_list)

            # hand label name
            hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
            hand_sign_label = keypoint_classifier_labels[hand_sign_id]

            handedness_label = handedness.classification[0].label

            # Drawing:
            if debug_mode:
                debug_image = draw_bounding_rect(True, debug_image, brect)
                debug_image = draw_landmarks(debug_image, landmark_list)
                debug_image = draw_info_text(debug_image, brect, handedness,
                                             hand_sign_label)
    return debug_image, hand_sign_label, handedness_label


# =============== COMMAND LINE ARGS =====================================================
def get_args():
    parser = argparse.ArgumentParser()

    if DESKTOP_MODE:
        width, height = DESKTOP_DIMENSIONS
    else:
        width, height = MOBILE_DIMENSIONS

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", type=int, default=width)
    parser.add_argument("--height", type=int, default=height)
    # parser.add_argument("--use_static_image_mode", action='store_true')
    # parser.add_argument("--min_detection_confidence", type=float, default=0.7)
    # parser.add_argument("--min_tracking_confidence", type=float, default=0.5)

    return parser.parse_args()


# =============== MAIN LOOP =============================================================
def main():
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    cvFpsCalc = CvFpsCalc(buffer_len=10)

    mode = 0  # only mode 1 matters

    while True:
        fps = cvFpsCalc.get()

        key = cv.waitKey(10)
        if key == 27:  # ESC
            break

        number, mode = select_mode(key, mode)

        ret, image = cap.read()
        if not ret:
            break

        image = cv.flip(image, 1)

        debug_image, _, _ = process_image(
            image,
            training_mode=True,
            number=number,
            mode=mode
        )

        debug_image = draw_info(debug_image, fps, mode, number)
        debug_image = cv.cvtColor(debug_image, cv.COLOR_RGB2BGR)

        cv.imshow('Hand Gesture Dataset Creator', debug_image)

    cap.release()
    cv.destroyAllWindows()


# =============== MODE SELECTION ========================================================
def select_mode(key, mode):
    number = -1

    if 48 <= key <= 57: # keys 0-9
        number = key - 48 + OFFSET

    if key == 110:  # n: none
        mode = 0

    if key == 107:  # k: keypoint logging
        mode = 1

    return number, mode


# =============== LANDMARK HELPERS ======================================================
def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)
    for lm in landmarks.landmark:
        x = min(int(lm.x * image_width), image_width - 1)
        y = min(int(lm.y * image_height), image_height - 1)
        landmark_array = np.append(landmark_array, [[x, y]], axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks, handedness):
    image_width, image_height = image.shape[1], image.shape[0]

    points = []
    for lm in landmarks.landmark:
        x = lm.x * image_width
        y = lm.y * image_height
        points.append([int(x), int(y)])

    # Mirror LEFT hand → matches HandTracker
    # if handedness == "Left":
    #     for lm in points:
    #         lm[0] = image_width - lm[0]

    return points


def pre_process_landmark(landmark_list):
    temp = copy.deepcopy(landmark_list)

    base_x, base_y = temp[0]

    for i, (x, y) in enumerate(temp):
        temp[i][0] = x - base_x
        temp[i][1] = y - base_y

    temp = list(itertools.chain.from_iterable(temp))
    max_value = max(map(abs, temp))

    if max_value == 0:
        max_value = 1

    temp = [v / max_value for v in temp]
    return temp


# =============== CSV LOGGING ===========================================================
def logging_csv(number, landmark_list):
    if number < 0:
        return
    
    csv_path = "./model/dataset/keypoint.csv"

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([number, *landmark_list])


# =============== DRAW FUNCTIONS ========================================================
def draw_landmarks(image, points):
    # MediaPipe hand connection index pairs
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),       # Thumb
        (0, 5), (5, 9), (5, 6), (6, 7), (7, 8),       # Index finger
        (9, 13), (9, 10), (10, 11), (11, 12),  # Middle finger
        (13, 17), (13, 14), (14, 15), (15, 16),# Ring finger
        (0, 17), (17, 18), (18, 19), (19, 20) # Pinky
    ]

    # Draw lines
    for start, end in connections:
        x1, y1 = points[start]
        x2, y2 = points[end]
        cv.line(image, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv.line(image, (x1, y1), (x2, y2), (0, 0, 0), 1)

    # Draw points
    for i, (x, y) in enumerate(points):
        radius = 8 if i in [4, 8, 12, 16, 20] else 5
        cv.circle(image, (x, y), radius, (255, 255, 255), -1)
        cv.circle(image, (x, y), radius, (0, 0, 0), 1)

    return image


def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        cv.rectangle(image, (brect[0], brect[1]),
                     (brect[2], brect[3]), (0, 0, 0), 1)
    return image


def draw_info_text(image, brect, handedness, hand_sign_text):
    cv.rectangle(image, (brect[0], brect[1]),
                 (brect[2], brect[1] - 22), (0, 0, 0), -1)

    text = handedness.classification[0].label
    if hand_sign_text:
        text += ':' + hand_sign_text

    cv.putText(image, text, (brect[0] + 5, brect[1] - 4),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
               cv.LINE_AA)
    return image


def draw_info(image, fps, mode, number):
    cv.putText(image, f"FPS:{fps}", (10, 30),
               cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    if mode == 0:
        cv.putText(image, "MODE: None", (10, 80),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    elif mode == 1:
        cv.putText(image, "MODE: Logging Keypoints", (10, 80),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        if number >= 0:
            cv.putText(image, f"NUM:{number}", (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return image


# =============== RUN ==================================================================
if __name__ == '__main__':
    main()
