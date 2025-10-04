import json
import pyautogui

with open("movement_data.json", "r") as f:
    data = json.load(f)

dx = data["delta_x"]
dy = data["delta_y"]

if dy > jump_threshold:
    pyautogui.press('space')

if dx > x_threshold:
    pyautogui.keyDown('d')
elif dx < -x_threshold:
    pyautogui.keyDown('a')
else:
    pyautogui.keyUp('a')
    pyautogui.keyUp('d')
