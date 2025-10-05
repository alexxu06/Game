# 🦝 Racc-Moon — Camera-Controlled Platformer Game

**Racc-Moon** is a 2D platformer built with **Pygame**, where your **body movements control the player** using a webcam with **MediaPipe** pose estimation.

---

## Features

* **Camera-based controls**: Move your character by shifting left or right in front of the camera.
* **Jump physically**: Jump in real life to make your character jump in-game. The higher the jump, the higher the raccoon goes!
* **Dynamic platforms**: Endless recycling platforms keep the gameplay continuous.
* **Multiple player sprites**: Different sprites for idle, moving left/right, and jumping.

---

## Requirements

* Python 3.7 or higher, and below Python 3.13.0
* Pygame
* OpenCV (`cv2`)
* MediaPipe
* NumPy

---

## Installation

1. **Clone the repository** (or download the files).
2. **Install dependencies**:

```bash
pip install pygame opencv-python mediapipe numpy
```

---

## How to Run

Run the game from the terminal with:

```bash
python main.py
```

Make sure your webcam is connected and accessible.

---

## How to Play

* Move left/right by shifting your body left/right.
* Jump by jumping in front of the camera.
* Avoid falling off platforms (you'll end up at the bottom) and aim for as high as you can, to the moon!

---

## Notes

* Make sure your environment has good lighting for accurate camera detection.
* For best results, play in front of a plain background.
* Have fun!

## Made for StormHacks2025
## By Alex Xu, Anthony Yiu, Markus Chu, Xavier Sandilands
