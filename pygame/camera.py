import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

prev_hip = None
jumping = False
delta_x, delta_y = 0, 0
JUMP_THRESHOLD = 40  # pixels, adjust as needed
STRAIGHT_THRESHOLD = 5  # pixels for straight jump

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        # Get left and right hip coordinates
        left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        # Average hips for center
        hip_x = int((left_hip.x + right_hip.x) / 2 * frame.shape[1])
        hip_y = int((left_hip.y + right_hip.y) / 2 * frame.shape[0])

        if prev_hip is not None:
            dx = hip_x - prev_hip[0]
            dy = hip_y - prev_hip[1]

            # Detect jump (significant upward movement)
            if not jumping and dy < -JUMP_THRESHOLD:
                jumping = True
                delta_x, delta_y = dx, dy
                if abs(delta_x) <= STRAIGHT_THRESHOLD:
                    direction = "Jump Straight"
                elif delta_x > 0:
                    direction = "Jump Left"
                else:
                    direction = "Jump Right"
                print(f"Jump detected! delta_x: {delta_x}, delta_y: {delta_y}, {direction}")
            elif jumping and dy > 0:
                jumping = False  # Landed

        prev_hip = (hip_x, hip_y)

    cv2.imshow('Jump Tracker', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()