from enum import Enum

"""
# Maps each hand gesture to an action

## Controls
Hand position on video capture: move cursor

Fist: neutral / no actions
Point (1 finger): left-click down
Peace (2 fingers): right-click down
Thumbs up: scroll up
Thumbs down: scroll down


spacebar
keyboard gestures


"""

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
    Gesture.THUMBS_UP,   # ID 3
    Gesture.THUMBS_DOWN, # ID 4
]