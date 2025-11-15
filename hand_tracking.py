import itertools
import cv2 as cv
import mediapipe as mp

# For drawing landmarks
connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),         # Thumb
    (0, 5), (5, 9), (5, 6), (6, 7), (7, 8), # Index finger
    (9, 13), (9, 10), (10, 11), (11, 12),   # Middle finger
    (13, 17), (13, 14), (14, 15), (15, 16), # Ring finger
    (0, 17), (17, 18), (18, 19), (19, 20)   # Pinky
]

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    # Must take unprocessed hand landmarks
    def draw_landmarks(self, image, points):
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

    def get_landmarks(self, image):
        h, w, _ = image.shape
        rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        result = self.mp_hands.process(rgb)

        if not result.multi_hand_landmarks:
            return None
        
        hands_output = []
        
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            handedness_label = handedness.classification[0].label # Left or Right
            
            raw_list = []
            for lm in hand_landmarks.landmark:
                x = lm.x * w
                y = lm.y * h
                z = lm.z
                raw_list.append([x, y, z])

            proc_list = [lm.copy() for lm in raw_list]

            if handedness_label == "Left":
                for lm in proc_list:
                    lm[0] = w - lm[0]

            palm_ids = [0, 5, 9, 13, 17]
            palm_pts = [proc_list[i] for i in palm_ids]
            cx = sum(p[0] for p in palm_pts) / len(palm_pts)
            cy = sum(p[1] for p in palm_pts) / len(palm_pts)
            cz = sum(p[2] for p in palm_pts) / len(palm_pts)
            palm_center = (cx, cy, cz)

            
            hands_output.append({
                "landmarks": proc_list,                     # used by classifier
                "draw_points": [(int(x), int(y)) for x, y, _ in raw_list],  # REAL hand, NOT mirrored
                "palm_center": (cx, cy, cz),
                "handedness": handedness_label
            })
        
        return hands_output
    
    # Helper func to make landmarks relative to the wrist
    def preprocess_landmarks(self, landmark_list):
        temp = [[lm[0], lm[1]] for lm in landmark_list]

        # base point = wrist (index 0)
        base_x, base_y = temp[0]

        # convert to relative coords
        for lm in temp:
            lm[0] -= base_x
            lm[1] -= base_y

        # flatten
        flat = list(itertools.chain.from_iterable(temp))

        # normalize
        max_value = max(map(abs, flat)) or 1
        return [v / max_value for v in flat]
