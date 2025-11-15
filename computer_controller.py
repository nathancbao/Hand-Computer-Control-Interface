# Control computer given action
import pyautogui
from gestures import Gesture
    
class ComputerController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.left_down = False
        self.right_down = False

        # For cursor smoothing
        self.prev_x = None
        self.prev_y = None
    
    def perform_action(self, gesture, palm_center):

        # Move Cursor (POINT)
        if gesture == "point" and palm_center:
            cx, cy, cz = palm_center
            screen_w, screen_h = pyautogui.size()

            # Clamp into screen bounds
            mouse_x = max(0, min(int(cx), screen_w - 1))
            mouse_y = max(0, min(int(cy), screen_h - 1))

            # Smoothing
            if self.prev_x is not None:
                mouse_x = int(self.prev_x * 0.7 + mouse_x * 0.3)
                mouse_y = int(self.prev_y * 0.7 + mouse_y * 0.3)

            pyautogui.moveTo(mouse_x, mouse_y)
            self.prev_x, self.prev_y = mouse_x, mouse_y

        # Left Click (PEACE)
        if gesture == "peace":
            if not self.left_down:
                pyautogui.mouseDown(button='left')
                self.left_down = True
        else:
            if self.left_down:
                pyautogui.mouseUp(button='left')
                self.left_down = False

        # Neutral (FIST)
        if gesture == "fist":
            self.prev_x = None  # reset smoothing

            if self.left_down:
                pyautogui.mouseUp(button='left')
                self.left_down = False

            if self.right_down:
                pyautogui.mouseUp(button='right')
                self.right_down = False

        # Scroll (THUMBS_UP / THUMBS_DOWN)
        if gesture == "thumbs_up":
            pyautogui.scroll(40)
        elif gesture == "thumbs_down":
            pyautogui.scroll(-40)