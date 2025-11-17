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
    preview: bool = True  # set False to disable cv2.imshow


def init_tracking(preview: bool = True) -> TrackingContext:
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


def _extract(body_landmarks, w: int, h: int) -> Optional[Dict[str, float]]:
    """
    Pull out: right_hand_y, left_hand_y, x_center (nose.x).
    MediaPipe gives normalized coords already (0..1).
    Y increases downward; we invert so 'up' = 1.0.
    """
    if body_landmarks is None:
        return None

    lm = body_landmarks.landmark
    # Common landmark ids
    nose = lm[0]
    left_wrist = lm[15]
    right_wrist = lm[16]

    # Invert y so higher hand => larger number
    r_y = _clamp01(1.0 - right_wrist.y)
    l_y = _clamp01(1.0 - left_wrist.y)
    x_c = _clamp01(nose.x)

    return {
        "right_hand_y": r_y,
        "left_hand_y": l_y,
        "x_center": x_c,
    }


def get_body_state(ctx: TrackingContext) -> Optional[Dict[str, float]]:
    """
    Read a frame, run pose, and return the dict.
    Returns None if no person is detected this frame.
    """
    ok, frame = ctx.cap.read()
    if not ok:
        return None

    # BGR -> RGB for MediaPipe
    rgb = frame[:, :, ::-1]

    res = ctx.pose.process(rgb)
    state = _extract(res.pose_landmarks, frame.shape[1], frame.shape[0])

    # Optional tiny preview window (press 'q' to quit this test loop)
    if ctx.preview:
        view = frame.copy()
        if mp is not None and res.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                view, res.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS
            )
        cv2.imshow("tracking preview (press q to quit)", view)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Caller can catch None to stop its loop
            return None

    return state


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
            _cleanup(ctx)  # type: ignore[name-defined]
        except Exception:
            pass