# src/tracking/scene.py
# -----------------------------------------
# Round 1 (Michelle): fake tracking so Valerie
# can already connect it to graphics.
#
# Later you can replace the internals of
# init_tracking() and get_body_state() with
# real webcam + MediaPipe logic, but keep
# the same function names / return keys.
# -----------------------------------------

import time
import math


class FakeTrackingContext:
    """
    Simple context that just stores a start time.
    We use this to generate smooth, fake motion
    values between 0 and 1.
    """
    def __init__(self):
        self.t0 = time.time()


def init_tracking():
    """
    Set up tracking and return a context object.
    For now this is just a FakeTrackingContext.
    Later, you will replace this with:
    - opening the webcam
    - creating a MediaPipe Pose object
    """
    return FakeTrackingContext()


def _clamp01(v: float) -> float:
    """Clamp a number to the range [0.0, 1.0]."""
    return max(0.0, min(1.0, v))


def get_body_state(ctx: FakeTrackingContext):
    """
    Return a dict describing the body position.

    Later, you will:
    - read a frame from the webcam
    - run pose estimation
    - fill these values from wrist/nose keypoints.
    """
    t = time.time() - ctx.t0

    # Fake "up and down" hands using sine waves
    right_hand_y = 0.5 + 0.4 * math.sin(t)
    left_hand_y = 0.5 + 0.4 * math.sin(t + 1.5)

    # Fake "left/right" body center, slower movement
    x_center = 0.5 + 0.4 * math.sin(t * 0.5)

    return {
        "right_hand_y": _clamp01(right_hand_y),
        "left_hand_y": _clamp01(left_hand_y),
        "x_center": _clamp01(x_center),
    }


if __name__ == "__main__":
    # Small test: run this file directly to see
    # the fake body_state values printed.
    ctx = init_tracking()
    while True:
        state = get_body_state(ctx)
        print(state)
        time.sleep(0.05)
