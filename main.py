import cv2 as cv
from hand_tracking import HandTracker
from gestures import Gesture, GESTURE_MAP
from model.keypoint_classifier import KeyPointClassifier
from computer_controller import ComputerController

SHOW_LANDMARKS = True

NUM_GESTURES = len(GESTURE_MAP)

hand_tracker = HandTracker()
classifier = KeyPointClassifier(NUM_GESTURES)
computer = ComputerController()
    

def process_image(image):
    hands = hand_tracker.get_landmarks(image)
    if not hands:
        return image, None, None, None
    
    hand = hands[0]
    
    unprocessed_landmark_list = hand["landmarks"]
    draw_points = hand["draw_points"]
    palm_center = hand["palm_center"]

    if SHOW_LANDMARKS:
        hand_tracker.draw_landmarks(image, draw_points)
    
    processed_landmarks = hand_tracker.preprocess_landmarks(unprocessed_landmark_list)
    return image, processed_landmarks, palm_center, hand
    

def main():
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("Error:  open camera")
        return 
    
    while True:
        key = cv.waitKey(10)
        if key == 27: # ESC key
            break
        
        
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot capture frame")
            return
        
        image = cv.flip(frame, 1)

        image, landmark_list, palm_center, hand_info = process_image(image)

        if landmark_list:
            gesture_id = classifier(landmark_list)
            if not (0 <= gesture_id < NUM_GESTURES):
                cv.putText(image, "Unknown Gesture", (10, 30),
                           cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
            
                gesture = GESTURE_MAP[gesture_id]
                gesture_name = gesture.value

                cv.putText(image, gesture_name, (10, 30),
                           cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # computer.perform_action(gesture_name)
            
        cv.imshow("Hand Gesture Control", image)
  
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()