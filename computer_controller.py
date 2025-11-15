# Control computer given action
import pyautogui
from gestures import Gesture
    
class ComputerController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.left_down = False
        self.right_down = False
    
    def execute(self, gesture):
        if gesture == Gesture.FIST:
            if self.left_down:
                pyautogui.mouseUp(button='left')
                self.left_down = False
            if self.right_down:
                pyautogui.mouseUp(button='right')
                self.right_down = False
            
        elif gesture == Gesture.POINT:
            if not self.left_down:
                pyautogui.click(button='left')
                self.left_down = True

        elif gesture == Gesture.PEACE:
            if not self.right_down:
                pyautogui.click(button='right')
                self.right_down = True

        elif gesture == Gesture.THUMBS_UP:
            pyautogui.scroll(50)

        elif gesture == Gesture.THUMBS_DOWN:
            pyautogui.scroll(-50)