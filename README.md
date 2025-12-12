# computergraphics
# Michelle Soto and Valerie Pena

This project is an interactive computer graphics demo that uses real-time body tracking from a webcam to control a simple visual scene. The system detects a user’s pose using MediaPipe Pose + Hands, maps body motion (and hand gestures) to visual parameters, and renders a dynamic “tower” that responds instantly to the user’s movement.

---

## Overview

The pipeline consists of three main stages:

1. **Tracking** – Capture webcam input and extract body + hand features using MediaPipe Pose and Hands.
2. **Mapping** – Convert those features (hand heights, span, grip) into visual parameters (height, width, offset, break trigger).
3. **Rendering** – Draw a shaded tower scene using OpenCV with motion trails, lighting, and a shatter animation.

---

- **Body Tracking (`tracking/scene.py`)**
  - Opens the webcam and runs MediaPipe Pose + Hands simultaneously
  - Extracts right/left wrist positions, nose x-coordinate, and normalized hand “grip” (finger spread relative to forearm length)
  - Optional preview window draws pose/hand landmarks for debugging

- **Motion Mapping (`integration/motion_mapper.py`)**
  - Normalizes the body data, smooths grip values, and produces a `visual_state` dict:
    - `tower_height` → mapped from hand height (0 = arms down, 1 = overhead)
    - `side_offset` → mapped from nose x-position
    - `tower_width` → mapped from two-hand horizontal span (one-hand mode keeps a slim tower)
    - `break_trigger` → set when both hands are visible and fists are clenched
    - `grip_debug` → floats echoed on-screen so you can confirm the fist detection thresholds

- **Rendering (`renderer.py`)**
  - Applies the visual state, smooths tower bounds, and renders:
    - Live webcam feed with pose overlay
    - Shaded tower whose height/width follow your gestures
    - Cyan aura trail that follows tower motion
    - Particle burst + pause when `break_trigger` fires (close both fists to shatter the tower)

## Controls

- **Raise one hand** → tower height follows that wrist; tower stays slim.
- **Raise both hands apart** → average height drives tower height; hand span drives width so you can stretch it across the screen.
- **Shift your torso** → nose x-coordinate slides the tower left/right.
- **Clench both fists** (hands detected + grips drop below threshold) → tower breaks into particles, then rebuilds automatically.

Grip values print in the top-left corner of the window so you can see when the system thinks a fist is “closed”.

## Running the Project

### 1. Activate the virtual environment

```bash
source venv/bin/activate

pip install "numpy<2" opencv-python mediapipe matplotlib

python src/main.py
```
