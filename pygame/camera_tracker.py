import cv2
import mediapipe as mp
import math
from multiprocessing import Process, Value
import pyautogui
import time
from collections import deque

# Shared values for movement
delta_x = Value('d', 0.0)
delta_y = Value('d', 0.0)

# Thresholds
jump_threshold = 20
x_threshold = 8
jump_cooldown = 1.5  # seconds

def camera_process(delta_x, delta_y):
    print(delta_x, delta_y)
    mp_pose = mp.solutions.pose
    cap = cv2.VideoCapture(0)
    prev_center = None
    smooth_window = 5
    x_history = deque(maxlen=smooth_window)
    y_history = deque(maxlen=smooth_window)

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

                if prev_center:
                    dx = center_x - prev_center[0]
                    dy = prev_center[1] - center_y  # positive when jumping

                    x_history.append(dx)
                    y_history.append(dy)

                    delta_x.value = float(sum(x_history)/len(x_history))
                    delta_y.value = float(sum(y_history)/len(y_history))

                prev_center = (center_x, center_y)

                # Draw hip line
                cv2.line(frame, (left_x, left_y), (right_x, right_y), (0,255,0), 4)

            cv2.imshow("Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

def game_process(delta_x, delta_y):
    last_jump_time = 0  # For cooldown tracking

    while True:
        dx = delta_x.value
        dy = delta_y.value
        current_time = time.time()

        # Jump with cooldown
        if dy > jump_threshold and (current_time - last_jump_time) > jump_cooldown:
            pyautogui.press('space')
            print("Jump!")
            last_jump_time = current_time

        # Left/right movement
        if dx > x_threshold:
            pyautogui.keyDown('d')
            pyautogui.keyUp('a')
        elif dx < -x_threshold:
            pyautogui.keyDown('a')
            pyautogui.keyUp('d')
        else:
            pyautogui.keyUp('a')
            pyautogui.keyUp('d')

        time.sleep(0.01)

# if __name__ == "__main__":
#     p1 = Process(target=camera_process, args=(delta_x, delta_y))
#     p2 = Process(target=game_process, args=(delta_x, delta_y))
#     p1.start()
#     p2.start()
#     p1.join()
#     p2.join()