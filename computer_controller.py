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
    
    def perform_action(self, gesture, palm_center, cam_w, cam_h):

        if palm_center:
            cx, cy, cz = palm_center

            # Normalize hand position
            rx = cx / cam_w
            ry = cy / cam_h

            # Map to screen coords
            screen_w, screen_h = pyautogui.size()
            mouse_x = int(rx * screen_w)
            mouse_y = int(ry * screen_h)

            SMOOTHING = 0.25    # lower = smoother, higher = faster
            DEADZONE = 2        # ignore tiny jitter
            PREDICT = 0.12      # add a little forward prediction

            if self.prev_x is not None:
                dx = mouse_x - self.prev_x
                dy = mouse_y - self.prev_y

                # Deadzone removes tiny tremors
                if abs(dx) < DEADZONE and abs(dy) < DEADZONE:
                    return

                # Smooth movement
                mouse_x = int(self.prev_x * (1-SMOOTHING) + mouse_x * SMOOTHING)
                mouse_y = int(self.prev_y * (1-SMOOTHING) + mouse_y * SMOOTHING)

                # Add predictive motion
                mouse_x += int(dx * PREDICT)
                mouse_y += int(dy * PREDICT)

            pyautogui.moveTo(mouse_x, mouse_y)

            self.prev_x = mouse_x
            self.prev_y = mouse_y

        # Hold Left Click (POINT)
        if gesture == "point":
            if not self.left_down:
                pyautogui.mouseDown(button='left')
                self.left_down = True

        # Hold Right Click (PEACE)
        if gesture == "peace":
            if not self.right_down:
                pyautogui.mouseDown(button='right')
                self.right_down = True

        # Neutral, Release Everything (FIST)
        if gesture == "fist":
            self.stop_all_actions()

        # Scroll (THUMBS_UP / THUMBS_DOWN)
        if gesture == "thumbs_up":
            pyautogui.scroll(40)
        elif gesture == "thumbs_down":
            pyautogui.scroll(-40)
    
    def stop_all_actions(self):
        self.prev_x = None  # reset smoothing

        if self.left_down:
            pyautogui.mouseUp(button='left')
            self.left_down = False

        if self.right_down:
            pyautogui.mouseUp(button='right')
            self.right_down = False