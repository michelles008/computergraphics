# src/tracking/scene.py
# Real webcam + MediaPipe Pose tracker (same API as before)

from __future__ import annotations
import math
import time
from dataclasses import dataclass
from typing import Dict, Optional

# --- deps ---
try:
    import cv2
    import mediapipe as mp
except Exception as e:
    cv2 = None
    mp = None

# -----------------------------
# Public API (same names/signatures)
# -----------------------------

@dataclass
class TrackingContext:
    cap: "cv2.VideoCapture"
    pose: "mp.solutions.pose.Pose"
    hands: "mp.solutions.hands.Hands"
    t0: float = time.time()
    preview: bool = False 


def init_tracking(preview: bool = False) -> TrackingContext:
    """
    Open webcam and create a MediaPipe Pose object.
    """
    if cv2 is None or mp is None:
        raise RuntimeError(
            "OpenCV/MediaPipe not available. Install with:\n"
            "  pip install opencv-python mediapipe"
        )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam (VideoCapture(0) failed).")

    pose = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )
    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=0,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )
    return TrackingContext(cap=cap, pose=pose, hands=hands, preview=preview)


def _clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def _dist2d(a, b) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx * dx + dy * dy)


def _dist3d(a, b) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _hand_grips_from_hands(hands_result) -> Dict[str, Optional[float]]:
    grips = {"left": None, "right": None}
    if hands_result is None:
        return grips

    if hands_result.multi_hand_landmarks is None:
        return grips

    handedness_list = getattr(hands_result, "multi_handedness", None)
    if handedness_list is None:
        return grips

    for hand_landmarks, handedness in zip(hands_result.multi_hand_landmarks, handedness_list):
        if not handedness.classification:
            continue
        label = handedness.classification[0].label.lower()
        wrist = hand_landmarks.landmark[0]
        tip_indices = (8, 12, 16, 20)
        dists = [_dist3d(wrist, hand_landmarks.landmark[i]) for i in tip_indices]
        openness = sum(dists) / len(dists)
        grips[label] = _clamp01(openness * 4.5)

    return grips


def _extract(body_landmarks, hands_result, w: int, h: int):
    if body_landmarks is None:
        return None

    lm = body_landmarks.landmark

    right_wrist = lm[16]
    left_wrist = lm[15]
    nose = lm[0]
    left_shoulder = lm[11]
    right_shoulder = lm[12]
    left_elbow = lm[13]
    right_elbow = lm[14]
    left_pinky = lm[17]
    left_index = lm[19]
    left_thumb = lm[21]
    right_pinky = lm[18]
    right_index = lm[20]
    right_thumb = lm[22]

    r_y = _clamp01(1.0 - right_wrist.y)
    l_y = _clamp01(1.0 - left_wrist.y)
    r_x = _clamp01(right_wrist.x)
    l_x = _clamp01(left_wrist.x)
    x_c = _clamp01(nose.x)

    shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2.0
    head_tilt = x_c - shoulder_mid_x

    left_span = (
        _dist3d(left_wrist, left_index)
        + _dist3d(left_wrist, left_pinky)
        + _dist3d(left_wrist, left_thumb)
    ) / 3.0
    right_span = (
        _dist3d(right_wrist, right_index)
        + _dist3d(right_wrist, right_pinky)
        + _dist3d(right_wrist, right_thumb)
    ) / 3.0

    left_forearm = max(_dist3d(left_elbow, left_wrist), 1e-4)
    right_forearm = max(_dist3d(right_elbow, right_wrist), 1e-4)

    pose_left_grip = _clamp01((left_span / left_forearm) * 3.0)
    pose_right_grip = _clamp01((right_span / right_forearm) * 3.0)

    hand_grips = _hand_grips_from_hands(hands_result)
    left_grip = hand_grips.get("left") if hand_grips.get("left") is not None else pose_left_grip
    right_grip = hand_grips.get("right") if hand_grips.get("right") is not None else pose_right_grip

    return {
        "right_hand_y": r_y,
        "left_hand_y": l_y,
        "right_hand_x": r_x,
        "left_hand_x": l_x,
        "x_center": x_c,
        "head_tilt": head_tilt,
        "left_grip": left_grip,
        "right_grip": right_grip,
    }


def get_body_state(ctx: TrackingContext) -> Optional[Dict[str, float]]:
    """
    Read a frame, run pose, and return the dict.
    Returns None if no person is detected this frame.
    """
    ok, frame = ctx.cap.read()
    if not ok:
        return None
    frame = cv2.flip(frame, 1)

    rgb = frame[:, :, ::-1]

    res = ctx.pose.process(rgb)
    hands_res = ctx.hands.process(rgb)
    state = _extract(res.pose_landmarks, hands_res, frame.shape[1], frame.shape[0])

    if ctx.preview:
        view = frame.copy()
        if mp is not None and res.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                view, res.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS
            )
        cv2.imshow("tracking preview (press q to quit)", view)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return None

    return state, frame, res.pose_landmarks


def _cleanup(ctx: TrackingContext) -> None:
    try:
        ctx.cap.release()
    except Exception:
        pass
    try:
        ctx.hands.close()
    except Exception:
        pass
    if cv2 is not None:
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass


# -----------------------------
# Local test (run this file directly)
# -----------------------------
if __name__ == "__main__":
    try:
        ctx = init_tracking(preview=True)
        while True:
            state = get_body_state(ctx)
            if state is None:
                continue
            print(state)
    except Exception as e:
        print(f"[tracking error] {e}")
    finally:
        try:
            _cleanup(ctx)  
        except Exception:
            pass
