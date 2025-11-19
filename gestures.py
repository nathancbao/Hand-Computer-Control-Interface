from enum import Enum


# Allowed gestures (string values used everywhere)
class Gesture(Enum):
    FIST = "fist"
    POINT = "point"
    PEACE = "peace"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"


# IMPORTANT:
# The order in this list MUST MATCH the order used during training.
GESTURE_MAP = [
    Gesture.FIST,        # ID 0
    Gesture.POINT,       # ID 1
    Gesture.PEACE,       # ID 2
    # Gesture.THUMBS_UP,   # ID 3
    # Gesture.THUMBS_DOWN, # ID 4
]