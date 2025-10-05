import cv2
import mediapipe as mp
import math
import numpy as np
from collections import deque

# Configuration
smooth_window = 5
history_len = 200  # Number of frames to display in graph
jump_threshold = 40
x_threshold = 15

# Movement history
x_history = deque(maxlen=history_len)
y_history = deque(maxlen=history_len)

# Previous hip center
prev_center = None

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)

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

        delta_x = 0.0
        delta_y = 0.0

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

            left_x = int(left_hip.x * frame.shape[1])
            left_y = int(left_hip.y * frame.shape[0])
            right_x = int(right_hip.x * frame.shape[1])
            right_y = int(right_hip.y * frame.shape[0])

            center_x = (left_x + right_x) // 2
            center_y = (left_y + right_y) // 2

            # Calculate delta
            if prev_center:
                dx = center_x - prev_center[0]
                dy = prev_center[1] - center_y  # positive when jumping

                x_history.append(dx)
                y_history.append(dy)

                # Smooth using last few frames
                delta_x = sum(x_history)/len(x_history)
                delta_y = sum(y_history)/len(y_history)
            else:
                x_history.append(0)
                y_history.append(0)

            prev_center = (center_x, center_y)

            # Draw hip line
            cv2.line(frame, (left_x, left_y), (right_x, right_y), (0,255,0), 4)

        # Create a blank graph image
        graph = np.zeros((300, 600, 3), dtype=np.uint8)

        # Draw delta_x and delta_y history
        for i in range(1, len(x_history)):
            cv2.line(graph, (i-1, 150 - int(x_history[i-1]*5)),
                     (i, 150 - int(x_history[i]*5)), (0, 0, 255), 2)  # X in red
            cv2.line(graph, (i-1, 150 - int(y_history[i-1]*5)),
                     (i, 150 - int(y_history[i]*5)), (0, 255, 0), 2)  # Y in green

        # Add threshold lines
        cv2.line(graph, (0, 150 - jump_threshold), (history_len, 150 - jump_threshold), (255,0,0), 1)
        cv2.line(graph, (0, 150 + jump_threshold), (history_len, 150 + jump_threshold), (255,0,0), 1)

        # Add labels
        cv2.putText(graph, f"Delta X: {delta_x:.1f}", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255),1)
        cv2.putText(graph, f"Delta Y: {delta_y:.1f}", (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0),1)

        # Combine camera and graph horizontally
        graph_resized = cv2.resize(graph, (frame.shape[1], frame.shape[0]))
        combined = np.hstack((frame, graph_resized))

        cv2.imshow("Camera + Movement Graph", combined)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()