# src/renderer.py
import cv2
import numpy as np

def init_scene():
    """Create a simple scene state for our tower."""
    scene = {
        "window_name": "Tower demo",
        "width": 640,
        "height": 480,
        "tower_height": 1.0,   # 1..4 from body_to_visual
        "side_offset": 0.0,    # -1..1 from body_to_visual
    }
    return scene


def apply_visual_state(scene, visual_state):
    """Update scene values from the visual_state dict."""
    if not visual_state:
        return

    scene["tower_height"] = visual_state.get(
        "tower_height", scene["tower_height"]
    )
    scene["side_offset"] = visual_state.get(
        "side_offset", scene["side_offset"]
    )


def render_frame(scene):
    """
    Draw a tower rectangle using OpenCV.

    - tower_height (1..4) -> pixel height
    - side_offset (-1..1) -> horizontal shift
    """
    w = scene["width"]
    h = scene["height"]

    # blank black image
    img = np.zeros((h, w, 3), dtype=np.uint8)

    # --- map tower_height to pixels ---
    t = float(scene.get("tower_height", 1.0))
    t = max(1.0, min(4.0, t))       # clamp 1..4
    frac = (t - 1.0) / 3.0          # 0..1

    min_px = 60                     # minimum height
    max_px = h - 80                 # max height
    tower_px = int(min_px + frac * (max_px - min_px))

    # --- map side_offset (-1..1) to x position ---
    offset = float(scene.get("side_offset", 0.0))
    offset = max(-1.0, min(1.0, offset))

    base_y = h - 40
    tower_w = 80

    center_x = int(w / 2 + offset * (w / 3))
    x1 = center_x - tower_w // 2
    x2 = center_x + tower_w // 2
    y1 = base_y - tower_px
    y2 = base_y

    # draw green tower
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), thickness=-1)

    # ground line
    cv2.line(img, (0, base_y), (w, base_y), (255, 255, 255), 2)

    # show window
    cv2.imshow(scene["window_name"], img)
    # ESC to quit window loop (optional)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        raise KeyboardInterrupt
