# src/tracking/scene.py
# Real webcam + MediaPipe Pose tracker (same API as before)

from __future__ import annotations
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
    return TrackingContext(cap=cap, pose=pose, preview=preview)


def _clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def _extract(body_landmarks, w: int, h: int):
    if body_landmarks is None:
        return None

    lm = body_landmarks.landmark

    right_wrist = lm[16]
    left_wrist  = lm[15]
    nose        = lm[0]
    left_shoulder = lm[11]
    right_shoulder = lm[12]

    shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2.0
    head_tilt = nose.x - shoulder_mid_x  

    return {
        "right_hand_y": 1.0 - right_wrist.y,
        "left_hand_y": 1.0 - left_wrist.y,
        "right_hand_x": right_wrist.x,
        "left_hand_x": left_wrist.x,
        "x_center": nose.x,
        "head_tilt": head_tilt
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
    state = _extract(res.pose_landmarks, frame.shape[1], frame.shape[0])

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