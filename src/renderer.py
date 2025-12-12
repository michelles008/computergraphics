# src/renderer.py
import cv2
import numpy as np
import mediapipe as mp
import random

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
        "trail_history": [],
        "smoothed_box": None,
        "break_trigger": False,
        "break_timer": 0,
        "break_particles": [],
        "grip_debug": None
    }


def apply_visual_state(scene, visual_state):
    if not visual_state:
        return

    scene["godzilla_active"] = visual_state.get("godzilla_active", False)
    scene["break_trigger"] = visual_state.get("break_trigger", False)
    scene["grip_debug"] = visual_state.get("grip_debug")
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
        debug = scene.get("grip_debug")
        if debug:
            msg = f"Grip L:{debug.get('left', 0):.2f} R:{debug.get('right', 0):.2f}"
            cv2.putText(img, msg, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow(scene["window_name"], img)
        if cv2.waitKey(1) & 0xFF == 27:
            raise KeyboardInterrupt
        return

    # -----------------------------
    # Compute tower geometry
    # -----------------------------
    base_y = h - 40

    raw_height = float(scene.get("tower_height", 0.3))
    if raw_height <= 1.0:
        height_norm = max(0.0, min(1.0, raw_height))
    else:
        height_norm = max(0.0, min(1.0, (raw_height - 1.0) / 3.0))

    min_height_px = 40
    max_height_px = base_y - 20
    tower_px = int(min_height_px + height_norm * (max_height_px - min_height_px))

    offset = float(scene.get("side_offset", 0.0))
    offset = max(-1.0, min(1.0, offset))

    raw_width = float(scene.get("tower_width", 0.25))
    min_width_px = 40
    max_width_px = int(w * 0.9)
    if raw_width <= 1.0:
        width_norm = max(0.0, min(1.0, raw_width))
        tower_w = int(min_width_px + width_norm * (max_width_px - min_width_px))
    else:
        tower_w = int(max(min_width_px, min(max_width_px, raw_width)))
        width_norm = max(0.0, min(1.0, (tower_w - min_width_px) / max(1, (max_width_px - min_width_px))))

    center_x = int(w / 2 + offset * (w / 3))
    x1 = center_x - tower_w // 2
    x2 = center_x + tower_w // 2
    y1 = base_y - tower_px
    y2 = base_y

    debug = scene.get("grip_debug")
    if debug:
        msg = f"Grip L:{debug.get('left', 0):.2f} R:{debug.get('right', 0):.2f}"
        cv2.putText(img, msg, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    new_box = (x1, y1, x2, y2)
    prev_box = scene.get("smoothed_box")
    if prev_box is None:
        smoothed = new_box
    else:
        alpha = 0.25
        smoothed = tuple(
            int(prev_box[i] * (1 - alpha) + new_box[i] * alpha)
            for i in range(4)
        )
    scene["smoothed_box"] = smoothed

    scene["trail_history"].append(smoothed)
    max_trail = 5
    if len(scene["trail_history"]) > max_trail:
        scene["trail_history"].pop(0)

    trigger_break = False
    if scene.get("break_trigger"):
        trigger_break = True
        scene["break_trigger"] = False

    if trigger_break and scene.get("break_timer", 0) == 0:
        particles = []
        for _ in range(30):
            px = random.uniform(x1, x2)
            py = random.uniform(y1, y2)
            vx = random.uniform(-5, 5)
            vy = random.uniform(-8, -2)
            particles.append({"x": px, "y": py, "vx": vx, "vy": vy})
        scene["break_particles"] = particles
        scene["break_timer"] = 14

    if scene.get("break_timer", 0) > 0:
        particles = scene.get("break_particles", [])
        new_particles = []
        for p in particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.8
            if 0 <= p["x"] < w and p["y"] < h:
                new_particles.append(p)
                cv2.circle(
                    img,
                    (int(p["x"]), int(p["y"])),
                    4,
                    (200, 220, 255),
                    -1,
                )
        scene["break_particles"] = new_particles
        scene["break_timer"] = max(0, scene["break_timer"] - 1)

        cv2.imshow(scene["window_name"], img)
        if cv2.waitKey(1) & 0xFF == 27:
            raise KeyboardInterrupt
        return


    # -----------------------------
    # AURA / SHIMMER TRAIL
    # -----------------------------
    if scene["trail_history"]:
        overlay = img.copy()
        total = len(scene["trail_history"])
        for i, (tx1, ty1, tx2, ty2) in enumerate(scene["trail_history"]):
            fade = (i + 1) / total
            color = (int(40 * fade), int(60 * fade), int(180 * fade))
            cv2.rectangle(overlay, (tx1, ty1), (tx2, ty2), color, -1)

        alpha = 0.2
        img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # -----------------------------
    # DYNAMIC SHADING (based on size)
    # -----------------------------
    height_factor = height_norm

    width_factor = width_norm

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
