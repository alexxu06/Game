import cv2
import mediapipe as mp
import pandas as pd
from datetime import datetime
import math

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Open webcam
cap = cv2.VideoCapture(0)

# Variables for movement tracking
motion_list = [0, 0]
motion_times = []

prev_center = None
movement_threshold = 20  # Pixels, adjust sensitivity

df = pd.DataFrame(columns=["Start", "End"])

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

        motion = 0

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            # Use midpoint of left and right hip as body center
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

            center_x = int((left_hip.x + right_hip.x) / 2 * frame.shape[1])
            center_y = int((left_hip.y + right_hip.y) / 2 * frame.shape[0])

            if prev_center:
                dist = math.hypot(center_x - prev_center[0], center_y - prev_center[1])
                if dist > movement_threshold:
                    motion = 1

            prev_center = (center_x, center_y)

            # Draw skeleton
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2)
            )

        # Update motion list
        motion_list.append(motion)
        motion_list = motion_list[-2:]

        # Log start time
        if motion_list[-1] == 1 and motion_list[-2] == 0:
            motion_times.append(datetime.now())

        # Log end time
        if motion_list[-1] == 0 and motion_list[-2] == 1:
            motion_times.append(datetime.now())

        cv2.imshow("Body Movement Tracker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if motion == 1:
                motion_times.append(datetime.now())
            break

# Save movement times to CSV
for i in range(0, len(motion_times), 2):
    df = df.append({"Start": motion_times[i], "End": motion_times[i+1]}, ignore_index=True)

df.to_csv("Body_Movement_Times.csv", index=False)

cap.release()
cv2.destroyAllWindows()
