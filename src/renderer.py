# src/renderer.py
import cv2
import numpy as np
import mediapipe as mp

godzilla_img = cv2.imread("src/reference_images/GZILL.jpg")
if godzilla_img is None:
    print("ERROR: Could not load Godzilla image!")


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
        "pose_landmarks": None,
        "godzilla_active": False,
        "godzilla_x": 450,
        "godzilla_y": 200,
        "trail_history": []
    }


def apply_visual_state(scene, visual_state):
    if not visual_state:
        return

    scene["godzilla_active"] = visual_state.get("godzilla_active", False)
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

    img = cv2.resize(frame, (w, h))

    if landmarks is not None:
        mp.solutions.drawing_utils.draw_landmarks(
            img,
            landmarks,
            mp.solutions.pose.POSE_CONNECTIONS
        )

    if not scene.get("active", False):
        cv2.imshow(scene["window_name"], img)
        if cv2.waitKey(1) & 0xFF == 27:
            raise KeyboardInterrupt
        return

    # -----------------------------
    # Compute tower geometry
    # -----------------------------
    t = float(scene.get("tower_height", 1.0))
    t = max(1.0, min(4.0, t))
    frac = (t - 1.0) / 3.0

    min_px = 60
    max_px = h - 80
    tower_px = int(min_px + frac * (max_px - min_px))

    offset = float(scene.get("side_offset", 0.0))
    offset = max(-1.0, min(1.0, offset))
    
    tower_w = int(scene.get("tower_width", 80))
    base_y = h - 40

    center_x = int(w / 2 + offset * (w / 3))
    x1 = center_x - tower_w // 2
    x2 = center_x + tower_w // 2
    y1 = base_y - tower_px
    y2 = base_y

    scene["trail_history"].append((x1, y1, x2, y2))
    if len(scene["trail_history"]) > 10:
        scene["trail_history"].pop(0)


    # -----------------------------
    # AURA / SHIMMER TRAIL
    # -----------------------------
    for i, (tx1, ty1, tx2, ty2) in enumerate(scene["trail_history"]):
        fade = (i + 1) / len(scene["trail_history"])  
        glow = int(200 * fade)                        

        cv2.rectangle(
            img,
            (tx1, ty1),
            (tx2, ty2),
            (0, glow, glow),   
            2
        )

    if len(scene["trail_history"]) > 10:
        scene["trail_history"].pop(0)

    # -----------------------------
    # DYNAMIC SHADING (based on size)
    # -----------------------------
    height_factor = (scene["tower_height"] - 1.0) / 3.0
    height_factor = max(0.0, min(1.0, height_factor))

    width_factor = min(1.0, tower_w / 280.0)

    light_factor = (height_factor * 0.7) + (width_factor * 0.3)

    for y in range(y1, y2):
        tpos = (y - y1) / max(1, (y2 - y1))

        base_light = int(60 + 150 * light_factor)
        shadow_strength = int(60 + 150 * light_factor)

        shade = base_light + int((1 - tpos) * shadow_strength)
        shade = max(0, min(255, shade))

        shaded_color = (shade, shade, int(shade * 0.7))

        cv2.line(img, (x1, y), (x2, y), shaded_color, 1)

    # -----------------------------
    # Specular Highlight (right side)
    # -----------------------------
    highlight_color = (255, 255, 255)
    cv2.rectangle(img, (x2 - 4, y1), (x2, y2), highlight_color, 1)

    # Ground line
    cv2.line(img, (0, base_y), (w, base_y), (255, 255, 255), 2)

    # -----------------------------
    # GODZILLA OVERLAY
    # -----------------------------
    if scene.get("godzilla_active", False) and godzilla_img is not None:

        gz = cv2.resize(godzilla_img, (160, 160))
        gx = scene.get("godzilla_x", 450)
        gy = scene.get("godzilla_y", 200)

        h_gz, w_gz, _ = gz.shape

        if gy + h_gz < img.shape[0] and gx + w_gz < img.shape[1]:
            img[gy:gy + h_gz, gx:gx + w_gz] = gz

    # Display
    cv2.imshow(scene["window_name"], img)
    if cv2.waitKey(1) & 0xFF == 27:
        raise KeyboardInterrupt
