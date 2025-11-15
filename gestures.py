from enum import Enum, auto

class Gesture(Enum):
    FIST = "fist"
    POINT = "point"
    PEACE = "peace"
    # THUMBS_UP = "thumbs_up"
    # THUMBS_DOWN = "thumbs_down"

GESTURE_MAP = list(Gesture)

# GESTURE_INDEX = {
#     Gesture.FIST,
#     Gesture.POINT,
#     Gesture.PEACE,
#     Gesture.THUMBS_UP,
#     Gesture.THUMBS_DOWN,
# }