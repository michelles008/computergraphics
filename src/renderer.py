# src/renderer.py
import cv2
import numpy as np
import mediapipe as mp

def init_scene():
    return {
        "window_name": "Interactive Tower Demo",
        "width": 640,
        "height": 480,
        "tower_height": 1.0,
        "side_offset": 0.0,
        "tower_width": 80,
        "active": False,
        "mode": "none",
        "pose_landmarks": None
    }

def apply_visual_state(scene, visual_state):
    if not visual_state:
        return

    scene["active"] = visual_state.get("active", False)

    if scene["active"]:
        scene["tower_height"] = visual_state.get("tower_height", scene["tower_height"])
        scene["side_offset"] = visual_state.get("side_offset", scene["side_offset"])
        scene["tower_width"] = visual_state.get("tower_width", scene["tower_width"])
        scene["mode"] = visual_state.get("mode", scene["mode"])
    else:
        scene["mode"] = "none"

def render_frame(scene, frame, landmarks=None):
    w = scene["width"]
    h = scene["height"]

    # Webcam feed as background
    img = cv2.resize(frame, (w, h))

    # Draw pose skeleton on webcam
    if landmarks is not None:
        mp.solutions.drawing_utils.draw_landmarks(
            img,
            landmarks,
            mp.solutions.pose.POSE_CONNECTIONS
        )

    # If no hands → just show webcam
    if not scene.get("active", False):
        cv2.imshow(scene["window_name"], img)
        if cv2.waitKey(1) & 0xFF == 27:
            raise KeyboardInterrupt
        return

    # Compute tower dimensions
    t = float(scene.get("tower_height", 1.0))
    t = max(1.0, min(4.0, t))  
    frac = (t - 1.0) / 3.0

    min_px = 60
    max_px = h - 80
    tower_px = int(min_px + frac * (max_px - min_px))

    offset = float(scene.get("side_offset", 0.0))
    offset = max(-1.0, min(1.0, offset))

    base_y = h - 40
    tower_w = int(scene.get("tower_width", 80))

    center_x = int(w / 2 + offset * (w / 3))
    x1 = center_x - tower_w // 2
    x2 = center_x + tower_w // 2
    y1 = base_y - tower_px
    y2 = base_y

    # Tower color based on mode
    mode = scene.get("mode", "none")
    if mode == "one_hand":
        color = (0, 255, 0)
    elif mode == "two_hands":
        color = (255, 150, 50)
    else:
        color = (0, 120, 255)

    # Draw tower ON TOP of webcam feed
    cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
    cv2.line(img, (0, base_y), (w, base_y), (255, 255, 255), 2)

    # Show final overlay
    cv2.imshow(scene["window_name"], img)
    if cv2.waitKey(1) & 0xFF == 27:
        raise KeyboardInterrupt
