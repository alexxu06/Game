import cv2
import mediapipe as mp
import pyautogui

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose

# Open webcam
cap = cv2.VideoCapture(0)

prev_center = None
jump_threshold = 40       # Pixels upward to detect jump
x_threshold = 30          # Pixels left/right to detect movement
cooldown_frames = 5       # Prevent multiple triggers for one movement
frame_counter = 0

with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        frame_counter += 1
        trigger_jump = trigger_left = trigger_right = False

        # Default values
        delta_x = 0
        delta_y = 0
        center_x = 0
        center_y = 0

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

            left_x = int(left_hip.x * frame.shape[1])
            left_y = int(left_hip.y * frame.shape[0])
            right_x = int(right_hip.x * frame.shape[1])
            right_y = int(right_hip.y * frame.shape[0])

            # Draw hip line only
            cv2.line(frame, (left_x, left_y), (right_x, right_y), (0,255,0), 4)

            # Center point
            center_x = (left_x + right_x) // 2
            center_y = (left_y + right_y) // 2

            if prev_center:
                delta_y = prev_center[1] - center_y  # positive if moving up
                delta_x = center_x - prev_center[0]  # positive if moving right

                # Only trigger actions if cooldown passed
                if frame_counter > cooldown_frames:
                    # Jump detection
                    if delta_y > jump_threshold:
                        pyautogui.press('space')
                        trigger_jump = True

                    # Left/Right movement detection
                    if delta_x > x_threshold:
                        pyautogui.keyDown('d')
                        trigger_right = True
                        pyautogui.keyUp('a')
                    elif delta_x < -x_threshold:
                        pyautogui.keyDown('a')
                        trigger_left = True
                        pyautogui.keyUp('d')
                    else:
                        pyautogui.keyUp('a')
                        pyautogui.keyUp('d')

                    frame_counter = 0  # reset cooldown

            prev_center = (center_x, center_y)

            # Display movement feedback
            if trigger_jump:
                cv2.putText(frame, "JUMP!", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            if trigger_left:
                cv2.putText(frame, "LEFT!", (10,90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            if trigger_right:
                cv2.putText(frame, "RIGHT!", (10,130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

        # Always show debug info
        cv2.putText(frame, f"Hip Center: ({center_x},{center_y})", (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
        cv2.putText(frame, f"Delta X: {delta_x}  Delta Y: {delta_y}", (10,160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        cv2.imshow("Game Controller", frame)

        # Quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pyautogui.keyUp('a')
            pyautogui.keyUp('d')
            break

cap.release()
cv2.destroyAllWindows()



# Get data
import json

data = {
    "center_x": center_x,
    "center_y": center_y,
    "delta_x": delta_x,
    "delta_y": delta_y
}

with open("movement_data.json", "w") as f:
    json.dump(data, f)