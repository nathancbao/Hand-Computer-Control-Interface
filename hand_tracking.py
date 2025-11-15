import itertools
import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_landmarks(self, image):
        h, w, _ = image.shape
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = self.mp_hands.process(rgb)

        if not result.multi_hand_landmarks:
            return None
        
        hands_output = []
        
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            handedness_label = handedness.classification[0].label # Left or Right
            
            landmark_list = []
            for lm in hand_landmarks.landmark:
                x = min(int(lm.x * w), w - 1)
                y = min(int(lm.y * h), h - 1)
                landmark_list.append([x, y])
            
            processed = self._preprocess_landmarks(landmark_list)
            
            hands_output.append((processed, handedness_label))
        
        return hands_output
    
    # Helper func to make landmarks relative to the wrist
    def _preprocess_landmarks(self, landmark_list):
        temp = [p.copy() for p in landmark_list]

        # base point = wrist (index 0)
        base_x, base_y = temp[0]

        # convert to relative coords
        for i, (x, y) in enumerate(temp):
            temp[i][0] = x - base_x
            temp[i][1] = y - base_y

        # flatten
        flat = list(itertools.chain.from_iterable(temp))

        # normalize
        max_value = max(map(abs, flat)) or 1
        return [v / max_value for v in flat]
