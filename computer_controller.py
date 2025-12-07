# Control computer given action
import pydirectinput
import win32api
import win32con
from gestures import Gesture
    
class ComputerController:
    def __init__(self):
        pydirectinput.FAILSAFE = False
        self.left_down = False
        self.right_down = False

        # For cursor smoothing
        self.prev_x = None
        self.prev_y = None
        
        # Movement mode (True = relative for games, False = absolute for desktop)
        self.relative_mode = False
    
    def perform_action(self, gesture, palm_center, cam_w, cam_h):

        if palm_center:
            cx, cy, cz = palm_center

            # Normalize hand position (0 to 1)
            rx = cx / cam_w
            ry = cy / cam_h

            if self.relative_mode:
                # RELATIVE MODE (for games like Minecraft)
                # Convert to centered coordinates (-0.5 to 0.5)
                centered_x = rx - 0.5
                centered_y = ry - 0.5

                SENSITIVITY = 200    # Adjust for game sensitivity
                DEADZONE = 0.05     # Ignore small movements (0-1 range)
                SMOOTHING = 0.3     # Smooth the movement

                # Apply deadzone
                if abs(centered_x) < DEADZONE:
                    centered_x = 0
                if abs(centered_y) < DEADZONE:
                    centered_y = 0

                if self.prev_x is not None:
                    # Smooth the centered positions
                    centered_x = self.prev_x * (1 - SMOOTHING) + centered_x * SMOOTHING
                    centered_y = self.prev_y * (1 - SMOOTHING) + centered_y * SMOOTHING

                # Calculate relative movement for this frame
                dx = int(centered_x * SENSITIVITY)
                dy = int(centered_y * SENSITIVITY)

                # Use relative mouse movement for in-game camera control
                if dx != 0 or dy != 0:
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

                self.prev_x = centered_x
                self.prev_y = centered_y
            
            else:
                # ABSOLUTE MODE (for desktop use)
                # Map to screen coords with expanded range
                screen_w = win32api.GetSystemMetrics(0)
                screen_h = win32api.GetSystemMetrics(1)
                
                # Remap from camera range to larger virtual range, then clamp
                # Adjust EXPANSION_FACTOR: higher = less hand movement needed
                EXPANSION_FACTOR = 1.5
                
                # Center and expand the mapping
                centered_rx = (rx - 0.5) * EXPANSION_FACTOR + 0.5
                centered_ry = (ry - 0.5) * EXPANSION_FACTOR + 0.5
                
                # Clamp to screen bounds
                centered_rx = max(0, min(1, centered_rx))
                centered_ry = max(0, min(1, centered_ry))
                
                mouse_x = int(centered_rx * screen_w)
                mouse_y = int(centered_ry * screen_h)

                SMOOTHING = 0.25    # lower = smoother, higher = faster
                DEADZONE = 2        # ignore tiny jitter

                if self.prev_x is not None:
                    dx = mouse_x - self.prev_x
                    dy = mouse_y - self.prev_y

                    # Deadzone removes tiny tremors
                    if abs(dx) < DEADZONE and abs(dy) < DEADZONE:
                        return

                    # Smooth movement
                    mouse_x = int(self.prev_x * (1-SMOOTHING) + mouse_x * SMOOTHING)
                    mouse_y = int(self.prev_y * (1-SMOOTHING) + mouse_y * SMOOTHING)

                # Use absolute positioning
                win32api.SetCursorPos((mouse_x, mouse_y))

                self.prev_x = mouse_x
                self.prev_y = mouse_y

        # Hold Left Click (POINT)
        if gesture == "point":
            if not self.left_down:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                self.left_down = True

        # Hold Right Click (PEACE)
        if gesture == "peace":
            if not self.right_down:
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
                self.right_down = True

        # Neutral, Release Everything (FIST)
        if gesture == "fist":
            self.stop_all_actions()

        # Scroll (THUMBS_UP / THUMBS_DOWN)
        if gesture == "thumbs_up":
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120)
        elif gesture == "thumbs_down":
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120)

        #double left click
        if gesture =="five":
            if self.left_down:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                self.left_down = False
            if self.right_down:
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
                self.right_down = False

            # perform a double left click
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    
    def toggle_mode(self):
        """Toggle between relative (game) and absolute (desktop) mouse mode"""
        self.relative_mode = not self.relative_mode
        self.prev_x = None  # reset smoothing when switching modes
        self.prev_y = None
        mode_name = "RELATIVE (Game)" if self.relative_mode else "ABSOLUTE (Desktop)"
        print(f"Switched to {mode_name} mode")
        return mode_name
    
    def stop_all_actions(self):
        self.prev_x = None  # reset smoothing

        if self.left_down:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            self.left_down = False

        if self.right_down:
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
            self.right_down = False