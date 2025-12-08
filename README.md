# computergraphics
# Michelle Soto and Valerie Pena

This project is an interactive computer graphics demo that uses real-time body tracking from a webcam to control a simple visual scene. The system detects a user’s pose using MediaPipe, maps body motion to visual parameters, and renders a dynamic “tower” that responds to the user’s movement.

---

## Overview

The pipeline consists of three main stages:

1. **Tracking** – Capture webcam input and extract body features using MediaPipe Pose.
2. **Mapping** – Convert body features (e.g. hand height, body position) into visual parameters.
3. **Rendering** – Draw a simple graphical scene using OpenCV based on those parameters.

---

- **Body Tracking (`tracking/scene.py`)**
  - Opens the webcam
  - Runs MediaPipe Pose
  - Extracts:
    - Right hand height
    - Left hand height
    - Horizontal body position (nose x-coordinate)
  - Optionally displays the camera preview with pose landmarks

- **Motion Mapping (`integration/motion_mapper.py`)**
  - Maps body features into:
    - `tower_height` (based on hand height)
    - `side_offset` (based on body position)

- **Rendering (`renderer.py`)**
  - Draws a green rectangular “tower” using OpenCV
  - Tower height and horizontal position update in real time

## Running the Project

### 1. Activate the virtual environment

```bash
source venv/bin/activate

pip install "numpy<2" opencv-python mediapipe matplotlib


python src/main.py